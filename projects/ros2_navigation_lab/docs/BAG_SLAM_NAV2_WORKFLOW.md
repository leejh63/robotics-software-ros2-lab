# Rosbag 기반 SLAM → Map 저장 → Map 로드 → AMCL/Nav2 Costmap 확인

> rosbag 원본 데이터는 이 저장소에 포함하지 않습니다. 실행할 때는 사용자가 직접 준비한 bag 디렉토리를 `BAG_DIR=/path/to/rosbag_directory`로 지정합니다.


이 문서는 기록된 rosbag 데이터를 사용해서 다음 흐름을 분리해서 확인하는 문서입니다.

```text
1. rosbag replay로 /scan, /odom, /tf, /tf_static을 공급한다.
2. slam_toolbox가 LaserScan과 TF를 사용해서 OccupancyGrid map을 만든다.
3. map_saver_cli로 map을 .yaml + .pgm 파일로 저장한다.
4. 저장한 map을 nav2_map_server로 다시 불러온다.
5. 같은 rosbag을 다시 replay해서 AMCL이 map 위 위치를 추정하게 한다.
6. Nav2를 실행해서 static map + LaserScan 기반 global/local costmap을 확인한다.
```

중요한 제한도 있습니다.

```text
rosbag은 과거에 기록된 sensor/odom/TF를 다시 재생할 뿐입니다.
Nav2가 새로 /cmd_vel을 내도 rosbag 안의 로봇 위치와 scan은 바뀌지 않습니다.
따라서 이 흐름은 map 생성, localization, costmap, planner/controller node 연결 확인용입니다.
실제 목표점까지 움직이는 closed-loop 주행 검증은 Gazebo 또는 실제 TurtleBot이 필요합니다.
```

---

## 0. rosbag frame/topic 전제

사용자가 준비한 rosbag에서 확인해야 할 핵심 토픽은 다음과 같습니다.

```text
/scan
/odom
/tf
/tf_static
```

기록된 frame 이름은 다음 흐름입니다.

```text
odom -> base_footprint -> base_link -> base_scan
```

주의할 점은 이것입니다.

```text
ros2 bag play의 topic remap은 topic 이름만 바꿉니다.
message 내부의 header.frame_id, child_frame_id 문자열은 바꾸지 않습니다.
```

따라서 bag workflow에서는 기존 Gazebo용 `odom_lee`가 아니라 rosbag 내부 frame인 `odom`을 사용합니다.

```text
map_lee -> odom -> base_footprint -> base_link -> base_scan
```

---

## 1. 빌드

workspace root, 즉 `ros2_navigation_lab`에서 실행합니다.

```bash
source /opt/ros/humble/setup.bash
colcon build --symlink-install --packages-select lee_robot_description
source install/setup.bash
```

rosbag 경로는 개인 PC 경로나 특정 파일명을 문서에 직접 박지 않고 환경변수로 둡니다. 아래 값만 실제 rosbag 디렉토리 경로로 바꿔서 사용합니다.

```bash
export BAG_DIR=/path/to/rosbag_directory
```

예를 들어 `ros2 bag info "$BAG_DIR"`가 정상 출력되면 이후 명령에서 같은 `$BAG_DIR`를 그대로 사용합니다. 단, 환경변수는 터미널마다 따로 적용되므로 rosbag을 재생하는 터미널에서도 한 번 더 `export BAG_DIR=/path/to/rosbag_directory`를 실행해야 합니다.

---

## 2. rosbag replay 방식 선택

두 가지 방식이 있습니다.

### 방식 A. 추천: rosbag topic을 `/lee/*`로 remap해서 replay

이 방식은 기존 RViz 설정, Nav2 params, 문서 흐름과 가장 잘 맞습니다.

rosbag 원본:

```text
/scan
/odom
/tf
/tf_static
```

replay 후:

```text
/lee/scan
/lee/odom
/lee/tf
/lee/tf_static
```

명령어:

```bash
ros2 bag play "$BAG_DIR" \
  --clock \
  --topics /scan /odom /tf /tf_static \
  --remap /scan:=/lee/scan \
          /odom:=/lee/odom \
          /tf:=/lee/tf \
          /tf_static:=/lee/tf_static
```

만약 현재 ROS2 환경에서 `--remap` 옵션이 동작하지 않으면 아래 방식으로 시도합니다.

```bash
ros2 bag play "$BAG_DIR" \
  --clock \
  --topics /scan /odom /tf /tf_static \
  --ros-args \
  -r /scan:=/lee/scan \
  -r /odom:=/lee/odom \
  -r /tf:=/lee/tf \
  -r /tf_static:=/lee/tf_static
```

초기 위치를 맞추거나 RViz에서 scan/map 정합을 볼 때는 느리게 반복 재생하는 편이 좋습니다.

```bash
ros2 bag play "$BAG_DIR" \
  --clock \
  --loop \
  -r 0.2 \
  --topics /scan /odom /tf /tf_static \
  --remap /scan:=/lee/scan \
          /odom:=/lee/odom \
          /tf:=/lee/tf \
          /tf_static:=/lee/tf_static
```

옵션 의미는 다음과 같습니다.

```text
--clock : bag timestamp 기준 /clock 발행
--loop  : bag이 끝나면 다시 처음부터 반복 재생
-r 0.2  : 원래 속도의 20%로 느리게 재생
```

`/cmd_vel`은 replay하지 않는 것을 추천합니다. Nav2가 새로 내는 `/lee/cmd_vel`과 과거에 기록된 `/cmd_vel`을 섞으면 해석이 꼬일 수 있습니다.

---

### 방식 B. 원본 topic 그대로 replay

이 방식은 rosbag 원본을 최대한 건드리지 않고 확인할 때 사용합니다.

```bash
ros2 bag play "$BAG_DIR" \
  --clock \
  --topics /scan /odom /tf /tf_static
```

이 경우 launch 쪽도 root topic을 보게 해야 합니다.

예를 들어 SLAM은 다음처럼 실행합니다.

```bash
ros2 launch lee_robot_description bag_slam.launch.py \
  use_rviz:=false \
  scan_topic:=/scan \
  map_topic:=/map \
  map_updates_topic:=/map_updates \
  tf_topic:=/tf \
  tf_static_topic:=/tf_static
```

`use_rviz:=false`를 넣은 이유는 기본 RViz 설정이 `/lee/map`, `/lee/scan` 기준이기 때문입니다. raw topic 방식에서 RViz를 쓰려면 RViz display topic도 `/map`, `/scan`으로 직접 바꿔야 합니다.

단, 이 저장소의 Nav2 costmap 확인 흐름은 기본적으로 방식 A, 즉 `/lee/*` remap 방식을 기준으로 정리했습니다.

---

## 3. rosbag으로 SLAM map 생성

터미널 1에서 SLAM을 먼저 실행합니다.

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 launch lee_robot_description bag_slam.launch.py
```

터미널 2에서 rosbag을 replay합니다.

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 bag play "$BAG_DIR" \
  --clock \
  --topics /scan /odom /tf /tf_static \
  --remap /scan:=/lee/scan \
          /odom:=/lee/odom \
          /tf:=/lee/tf \
          /tf_static:=/lee/tf_static
```

확인 명령:

```bash
ros2 topic echo /lee/scan --once
ros2 topic echo /lee/odom --once
ros2 topic echo /lee/map --once --qos-durability transient_local
ros2 run tf2_ros tf2_echo map_lee odom --ros-args -r /tf:=/lee/tf -r /tf_static:=/lee/tf_static
ros2 run tf2_ros tf2_echo odom base_footprint --ros-args -r /tf:=/lee/tf -r /tf_static:=/lee/tf_static
```

정상이라면 SLAM 단계의 TF 흐름은 다음처럼 됩니다.

```text
slam_toolbox: map_lee -> odom 발행
rosbag:       odom -> base_footprint 발행
rosbag:       base_footprint -> base_link -> base_scan 발행
```

---

## 4. 생성한 map 저장

SLAM으로 `/lee/map`이 보이면 map을 저장합니다.

workspace root에서 실행합니다.

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 run nav2_map_server map_saver_cli \
  -f src/lee_robot_description/maps/bag_slam_map \
  --ros-args -r /map:=/lee/map
```

생성 결과:

```text
src/lee_robot_description/maps/bag_slam_map.yaml
src/lee_robot_description/maps/bag_slam_map.pgm
```

`--symlink-install`로 빌드했다면 보통 바로 launch에서 접근할 수 있습니다. 그래도 map 파일을 못 찾는다면 다시 빌드하거나 `map_yaml:=`에 절대경로를 넘깁니다.

```bash
colcon build --symlink-install --packages-select lee_robot_description
source install/setup.bash
```

---

## 5. 저장한 map 불러오기 + AMCL 위치 추정

이 단계에서는 SLAM을 끄고, 저장된 map을 `map_server`가 다시 불러오게 합니다.

터미널 1:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 launch lee_robot_description bag_localization.launch.py
```

터미널 2:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 bag play "$BAG_DIR" \
  --clock \
  --topics /scan /odom /tf /tf_static \
  --remap /scan:=/lee/scan \
          /odom:=/lee/odom \
          /tf:=/lee/tf \
          /tf_static:=/lee/tf_static
```

초기 위치는 먼저 RViz의 `2D Pose Estimate`로 지정하는 것을 추천합니다.

```text
1. RViz Fixed Frame을 map_lee로 둔다.
2. Map은 /lee/map, LaserScan은 /lee/scan, ParticleCloud는 /particle_cloud를 본다.
3. 상단의 2D Pose Estimate를 누른다.
4. map 위에서 로봇이 있을 위치를 클릭한다.
5. 마우스를 드래그해서 로봇이 바라보는 방향을 지정한 뒤 놓는다.
```

이 동작은 `/initialpose`를 자동으로 publish합니다. SLAM으로 만든 map에서는 `x=0.0, y=0.0, yaw=0.0`이 실제 시작 위치라고 보장되지 않으므로, 처음부터 고정 좌표를 명령어로 넣기보다 RViz에서 map과 scan이 겹치는 위치를 직접 찍는 편이 안전합니다.

명령어로 직접 넣고 싶다면 먼저 RViz의 `Publish Point`로 좌표를 확인합니다.

```bash
ros2 topic echo /clicked_point
```

그 뒤 아래 템플릿의 `<x>`, `<y>`, `<qz>`, `<qw>`를 실제 값으로 바꿉니다.

```bash
ros2 topic pub --once /initialpose geometry_msgs/msg/PoseWithCovarianceStamped "
header:
  frame_id: 'map_lee'
pose:
  pose:
    position:
      x: <x>
      y: <y>
      z: 0.0
    orientation:
      x: 0.0
      y: 0.0
      z: <qz>
      w: <qw>
  covariance:
  - 0.25
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.25
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0685
"
```

2D yaw를 quaternion으로 바꾸는 기준은 다음과 같습니다.

```text
yaw = 0도   -> z = 0.0,     w = 1.0
yaw = 90도  -> z = 0.7071,  w = 0.7071
yaw = -90도 -> z = -0.7071, w = 0.7071
yaw = 180도 -> z = 1.0,     w = 0.0
```

확인 명령:

```bash
ros2 lifecycle get /map_server
ros2 lifecycle get /amcl
ros2 topic echo /lee/map --once --qos-durability transient_local
ros2 topic echo /amcl_pose --once
ros2 topic echo /particle_cloud --once
ros2 run tf2_ros tf2_echo map_lee odom --ros-args -r /tf:=/lee/tf -r /tf_static:=/lee/tf_static
```

---

## 6. 저장한 map + rosbag scan으로 Nav2 costmap 확인

여기서 costmap은 SLAM이 직접 띄우는 것이 아니라 Nav2 costmap server가 만듭니다. SLAM 단계에서 만든 것은 정적 map이고, Nav2는 그 map과 현재 LaserScan을 합쳐 global/local costmap을 구성합니다.

이 단계에서는 다음 두 costmap을 확인합니다.

```text
global_costmap:
  저장한 static map + scan obstacle layer + inflation layer

local_costmap:
  odom 기준 rolling window + scan obstacle layer + inflation layer
```

터미널 1:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 launch lee_robot_description bag_nav2.launch.py
```

터미널 2:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 bag play "$BAG_DIR" \
  --clock \
  --topics /scan /odom /tf /tf_static \
  --remap /scan:=/lee/scan \
          /odom:=/lee/odom \
          /tf:=/lee/tf \
          /tf_static:=/lee/tf_static
```

초기 위치는 RViz의 `2D Pose Estimate`로 지정합니다. 이 단계에서도 `x=0.0, y=0.0`을 고정으로 넣기보다 map 위에서 실제 위치와 방향을 찍어야 합니다.

```text
RViz 상단 2D Pose Estimate 선택
→ map 위에서 로봇 위치 클릭
→ 로봇이 바라보는 방향으로 드래그
→ scan 점들이 map 벽과 겹치는지 확인
```

rosbag replay는 시간이 계속 진행되므로, 위치를 맞출 때는 아래처럼 느리게 반복 재생하는 것을 추천합니다.

```bash
ros2 bag play "$BAG_DIR" \
  --clock \
  --loop \
  -r 0.2 \
  --topics /scan /odom /tf /tf_static \
  --remap /scan:=/lee/scan \
          /odom:=/lee/odom \
          /tf:=/lee/tf \
          /tf_static:=/lee/tf_static
```

costmap topic 확인:

```bash
ros2 node list | sort | grep -E 'controller_server|planner_server|bt_navigator|costmap'
ros2 topic list | sort | grep costmap
ros2 topic echo /lee/global_costmap/costmap --once
ros2 topic echo /lee/local_costmap/costmap --once
```

RViz에서 확인할 항목:

```text
Map:            /lee/map
LaserScan:      /lee/scan
ParticleCloud:  /particle_cloud
GlobalCostmap:  /lee/global_costmap/costmap
LocalCostmap:   /lee/local_costmap/costmap
```

---

## 7. Nav2 goal은 어떻게 봐야 하는가

goal을 보내면 path나 `/lee/cmd_vel`이 나올 수 있습니다.

```bash
ros2 action send_goal /lee/navigate_to_pose nav2_msgs/action/NavigateToPose "{pose: {header: {frame_id: map_lee}, pose: {position: {x: 0.5, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}}"

ros2 topic echo /lee/cmd_vel --once
```

하지만 이것은 closed-loop 주행 성공을 의미하지 않습니다.

```text
Nav2가 /lee/cmd_vel을 발행해도 rosbag replay 데이터는 그 명령을 따라 변하지 않습니다.
```

즉, 이 단계의 목표는 아래입니다.

```text
- 저장한 map이 map_server로 정상 로드되는지
- AMCL이 map_lee -> odom을 잡는지
- Nav2 global/local costmap이 생성되는지
- planner/controller server가 정상 lifecycle active가 되는지
- goal 입력 시 path/cmd_vel이 나오는지
```

실제 목표점까지 이동하는 검증은 다음 단계에서 진행합니다.

```text
1. 같은 공간에서 실제 TurtleBot으로 Nav2 실행
2. 또는 rosbag으로 만든 map과 일치하는 Gazebo world 구성 후 Nav2 실행
```

---

## 8. 자주 막히는 지점

### `/lee/map`이 안 보임

```bash
ros2 topic echo /lee/map --once --qos-durability transient_local
```

SLAM이 scan을 못 받는지 확인합니다.

```bash
ros2 topic hz /lee/scan
ros2 topic echo /lee/scan --once
```

---

### TF가 안 이어짐

```bash
ros2 run tf2_ros tf2_echo odom base_footprint --ros-args -r /tf:=/lee/tf -r /tf_static:=/lee/tf_static
ros2 run tf2_ros tf2_echo map_lee odom --ros-args -r /tf:=/lee/tf -r /tf_static:=/lee/tf_static
```

`map_lee -> odom`은 SLAM 또는 AMCL이 만듭니다. rosbag 자체에는 보통 없습니다.

---

### `odom_lee`를 찾는 에러가 남

bag workflow에서는 `odom_lee`를 쓰면 안 됩니다. rosbag 내부 frame은 `odom`입니다.

확인할 파일:

```text
config/bag_slam_param.yaml
config/bag_amcl_param.yaml
config/bag_nav2_params.yaml
```

---

### Nav2 costmap이 scan을 못 받음

```bash
ros2 topic info /lee/scan -v
ros2 topic info /lee/global_costmap/costmap -v
ros2 topic info /lee/local_costmap/costmap -v
```

rosbag replay에서 `/scan`을 `/lee/scan`으로 remap했는지 확인합니다.

---

### map 파일을 못 찾음

`bag_slam_map.yaml`을 만든 뒤 다시 빌드하거나, 절대경로를 넘깁니다.

```bash
ros2 launch lee_robot_description bag_nav2.launch.py \
  map_yaml:=$(realpath src/lee_robot_description/maps/bag_slam_map.yaml)
```
