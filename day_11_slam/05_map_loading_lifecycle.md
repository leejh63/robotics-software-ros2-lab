# 05. 저장 지도 로딩과 Lifecycle

## 1. 왜 저장 지도를 다시 로딩하는가?

SLAM으로 지도를 만들었다면 다음 단계는 그 지도를 다시 사용하는 것이다.

```text
Day 11
  SLAM으로 slam_map.yaml + slam_map.pgm 저장

Day 12
  map_server가 저장 지도를 /lee/map으로 발행
  AMCL이 그 지도 위에서 현재 위치 추정

Day 13
  Nav2가 그 지도와 costmap을 이용해 경로 계획/주행
```

즉, 지도 저장만 하고 끝나면 안 되고, 저장한 지도가 다시 ROS2 topic으로 발행되는지 확인해야 한다.

---

## 2. map_server의 역할

`nav2_map_server`의 `map_server`는 `.yaml + .pgm`을 읽어서 `/map` 또는 remap된 topic으로 `nav_msgs/msg/OccupancyGrid`를 발행한다.

현재 환경에서는 `/map`이 아니라 `/lee/map`으로 쓰는 것이 자연스럽다.

```text
slam_map.yaml + slam_map.pgm
  -> map_server
  -> /lee/map
```

---

## 3. Lifecycle이 필요한 이유

Nav2 계열 노드 중 일부는 lifecycle node이다.
일반 노드처럼 실행만 하면 바로 완전히 동작하는 것이 아니라 상태 전이가 필요하다.

대표 상태:

```text
unconfigured
  설정 전

inactive
  설정은 됐지만 실제 동작 전

active
  실제 topic/service/action 동작 중

finalized
  종료 상태
```

`map_server`도 active 상태가 되어야 map을 제대로 발행한다.
그래서 `lifecycle_manager`를 같이 쓰면 편하다.

---

## 4. 저장 지도만 로딩하는 기본 흐름

### 터미널 1. Gazebo + 로봇만 실행

SLAM은 끄고 실행한다.

```bash
cd $ROS2_WS
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 launch lee_robot_description slam.launch.py \
  world:=slam.world \
  use_slam:=false
```

이렇게 하면 Gazebo, robot_state_publisher, spawn_entity, RViz2는 뜨지만 SLAM Toolbox는 꺼진다.

---

### 터미널 2. 확인용 map_lee -> odom_lee TF 연결

지도만 보려면 `map_lee`와 `odom_lee`가 이어져야 RViz2에서 로봇/지도 관계를 볼 수 있다.
AMCL을 켜기 전 확인용으로 static transform을 사용할 수 있다.

```bash
cd $ROS2_WS
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 run tf2_ros static_transform_publisher 0 0 0 0 0 0 map_lee odom_lee \
  --ros-args \
  -r /tf:=/lee/tf \
  -r /tf_static:=/lee/tf_static
```

주의:

```text
이 static transform은 확인용이다.
AMCL을 실행할 때는 AMCL이 map_lee -> odom_lee를 발행해야 한다.
SLAM/AMCL/static_transform_publisher가 동시에 같은 map_lee -> odom_lee를 발행하면 안 된다.
```

---

### 터미널 3. map_server 실행

workspace root의 `slam_map.yaml`을 기준으로 실행:

```bash
cd $ROS2_WS
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 run nav2_map_server map_server \
  --ros-args \
  -r /map:=/lee/map \
  -p yaml_filename:=$PWD/slam_map.yaml \
  -p frame_id:=map_lee
```

`maps/` 폴더에 저장한 경우:

```bash
ros2 run nav2_map_server map_server \
  --ros-args \
  -r /map:=/lee/map \
  -p yaml_filename:=$PWD/maps/slam_map.yaml \
  -p frame_id:=map_lee
```

---

### 터미널 4. lifecycle_manager 실행

```bash
cd $ROS2_WS
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 run nav2_lifecycle_manager lifecycle_manager \
  --ros-args \
  -p node_names:='["map_server"]' \
  -p autostart:=True
```

확인:

```bash
ros2 topic echo /lee/map --once
ros2 lifecycle get /map_server
```

---

## 5. map 로딩 시 자주 헷갈리는 점

### 5.1 yaml 파일과 pgm 파일은 같이 있어야 한다

`slam_map.yaml` 안에는 보통 다음처럼 이미지 파일명이 상대 경로로 적혀 있다.

```yaml
image: slam_map.pgm
```

따라서 yaml과 pgm이 같은 폴더에 있어야 한다.

```text
정상:
  maps/slam_map.yaml
  maps/slam_map.pgm

문제 가능:
  maps/slam_map.yaml
  다른폴더/slam_map.pgm
```

---

### 5.2 frame_id가 map_lee인지 확인해야 한다

현재 RViz2와 SLAM/AMCL 흐름은 `map_lee`를 기준으로 정리되어 있다.
map_server가 기본 `map` frame으로 발행하면 다른 설정과 맞지 않을 수 있다.

현재 권장:

```bash
-p frame_id:=map_lee
```

---

### 5.3 map_server의 topic remap 확인

현재 지도 topic은 `/lee/map`이다.

```bash
-r /map:=/lee/map
```

이 remap을 빼면 `/map`으로 발행될 수 있고, RViz2가 `/lee/map`을 보고 있다면 지도 표시가 안 될 수 있다.

---

## 6. Day 12 AMCL과의 연결

Day 11에서 지도 로딩을 이해하면 Day 12 AMCL 흐름이 쉬워진다.

```text
map_server
  -> /lee/map 발행

AMCL
  <- /lee/map
  <- /lee/scan
  <- odom_lee -> base_footprint TF
  -> /amcl_pose
  -> /particle_cloud
  -> map_lee -> odom_lee TF
```

Day 11에서 SLAM이 발행하던 `map_lee -> odom_lee`는 Day 12에서 AMCL이 담당한다.

---

## 7. 결론

```text
map_saver_cli는 /lee/map을 파일로 저장한다.
map_server는 저장된 파일을 다시 /lee/map topic으로 발행한다.
map_server는 lifecycle active 상태가 되어야 제대로 동작한다.
확인용 static map_lee -> odom_lee TF는 확인용일 뿐, AMCL 단계에서는 AMCL이 그 역할을 해야 한다.
```
