# 03. AMCL 위치 추정

## 1. 목표

저장된 지도 `tb3_map.yaml` 위에서 AMCL을 실행하여 로봇의 현재 위치를 추정한다.

이 단계에서는 임시 `static_transform_publisher map odom`을 사용하지 않는다.

```text
map -> odom
```

이 변환은 AMCL이 초기 위치를 받은 뒤 추정해서 발행한다.

## 2. 기존 노드 정리

실습이 꼬였을 때는 먼저 정리한다.

```bash
pkill -f rviz2
pkill -f map_server
pkill -f lifecycle_manager
pkill -f amcl
pkill -f static_transform_publisher
```

확인:

```bash
ros2 node list
```

## 3. 터미널 1 — Gazebo 실행

```bash
cd "$TB3_WS"
source ~/envs/tb3_humble.bash

ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

확인:

```bash
ros2 topic echo /clock --once
```

## 4. 터미널 2 — map_server 실행

```bash
cd "$TB3_WS"
source ~/envs/tb3_humble.bash

ros2 run nav2_map_server map_server \
--ros-args \
-p yaml_filename:=$TB3_WS/maps/tb3_map.yaml \
-p use_sim_time:=true
```

## 5. 터미널 3 — AMCL 실행

```bash
cd "$TB3_WS"
source ~/envs/tb3_humble.bash

ros2 run nav2_amcl amcl \
--ros-args \
-p use_sim_time:=true \
-p base_frame_id:=base_footprint \
-p odom_frame_id:=odom \
-p global_frame_id:=map \
-p robot_model_type:=nav2_amcl::DifferentialMotionModel
```

## 6. 터미널 4 — lifecycle_manager 실행

`map_server`와 `amcl`은 lifecycle node이므로 둘 다 active 상태가 되어야 한다.

```bash
cd "$TB3_WS"
source ~/envs/tb3_humble.bash

ros2 run nav2_lifecycle_manager lifecycle_manager \
--ros-args \
-p node_names:='["map_server", "amcl"]' \
-p autostart:=true \
-p use_sim_time:=true
```

확인:

```bash
ros2 lifecycle get /map_server
ros2 lifecycle get /amcl
```

정상:

```text
active [3]
active [3]
```

## 7. 터미널 5 — RViz 실행

```bash
cd "$TB3_WS"
source ~/envs/tb3_humble.bash

rviz2 --ros-args -p use_sim_time:=true
```

RViz 설정:

```text
Global Options
  Fixed Frame: map
```

Display 추가:

```text
Map        → /map
TF         → 활성화
LaserScan  → /scan
PoseArray  → /particlecloud
```

Map Display 설정:

```text
Reliability Policy: Reliable
Durability Policy: Transient Local
```

## 8. 초기 위치 설정

AMCL은 처음에 로봇이 지도 어디에 있는지 모른다.  
따라서 초기 위치를 넣어야 `map -> odom`을 발행할 수 있다.

### 방법 A. RViz에서 설정

RViz 상단의 `2D Pose Estimate`를 클릭한다.

그 다음 지도 위에서 로봇의 실제 위치를 클릭하고, 마우스를 드래그해서 방향을 지정한다.

단, RViz의 `Fixed Frame`이 반드시 `map`이어야 한다.

### 방법 B. 짧은 명령어로 설정

긴 covariance 배열 없이 테스트용으로 짧게 넣을 수 있다.

```bash
ros2 topic pub --once /initialpose geometry_msgs/msg/PoseWithCovarianceStamped \
"{header: {frame_id: 'map'}, pose: {pose: {position: {x: 0.0, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}}"
```

핵심은 `frame_id`가 `map`이어야 한다는 점이다.

```yaml
header:
  frame_id: map
```

`odom`으로 들어가면 AMCL이 무시한다.

## 9. 정상 확인

AMCL pose 확인:

```bash
ros2 topic echo /amcl_pose --once
```

particlecloud 확인:

```bash
ros2 topic echo /particlecloud --once
```

AMCL이 `map -> odom`을 발행하는지 확인:

```bash
ros2 run tf2_ros tf2_echo map odom
```

정상이라면 transform이 계속 출력된다.

## 10. 자주 보인 경고

```text
AMCL cannot publish a pose or update the transform. Please set the initial pose...
```

초기 위치가 아직 들어가지 않았다는 뜻이다.

```text
Ignoring initial pose in frame "odom"; initial poses must be in the global frame, "map"
```

초기 위치 메시지가 `odom` 프레임으로 들어갔다는 뜻이다.  
RViz의 `Fixed Frame`을 `map`으로 바꾸거나, 명령어에서 `frame_id: 'map'`으로 발행한다.
