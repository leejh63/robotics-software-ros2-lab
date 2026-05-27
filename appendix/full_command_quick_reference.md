# 전체 명령어 빠른 참조

이 문서는 Day 01~13 전체 실습에서 자주 쓰는 명령어를 한 곳에 모은 것이다.

명령어를 그대로 복사하기 전에 [command_execution_conventions.md](command_execution_conventions.md)를 먼저 확인한다.

현재 `projects/ros2_navigation_lab` 실제 기본값:

```text
package name : lee_robot_description
namespace    : /lee
map frame    : map_lee
odom frame   : odom_lee
base frame   : base_footprint
scan frame   : base_scan
```

`/robot_ns`, `map_robot_ns`, `odom_robot_ns`는 일반 설명용 placeholder다. 이 문서의 복사 실행 명령은 `/lee`, `map_lee`, `odom_lee`를 우선 사용한다.

---

## 1. 빌드와 환경 설정

```bash
cd $ROS2_WS
source /opt/ros/humble/setup.bash
colcon build
source install/setup.bash
```

특정 패키지만 빌드:

```bash
colcon build --packages-select lee_robot_description
colcon build --packages-select camera_pkg my_if
```

빌드 결과 초기화가 필요할 때:

```bash
rm -rf build install log
colcon build
source install/setup.bash
```

---

## 2. ROS graph 기본 확인

```bash
ros2 node list | sort
ros2 topic list | sort
ros2 service list | sort
ros2 action list | sort
```

현재 프로젝트 주요 topic 확인:

```bash
ros2 topic list | sort | grep -E 'lee|scan|odom|tf|map|cmd_vel|amcl|particle|initialpose|costmap|plan'
```

node 정보:

```bash
ros2 node info /노드이름
```

topic 정보:

```bash
ros2 topic info /lee/scan
ros2 topic echo /lee/scan --once
ros2 topic hz /lee/scan
```

message type 확인:

```bash
ros2 interface show sensor_msgs/msg/LaserScan
ros2 interface show nav_msgs/msg/Odometry
ros2 interface show nav_msgs/msg/OccupancyGrid
ros2 interface show nav2_msgs/action/NavigateToPose
```

---

## 3. TF 확인

TF tree 파일 생성:

```bash
ros2 run tf2_tools view_frames
```

현재 `/lee/tf`, `/lee/tf_static`를 쓰는 경우에는 `tf2_echo`에도 remap을 명시한다.

```bash
ros2 run tf2_ros tf2_echo odom_lee base_footprint \
  --ros-args -r /tf:=/lee/tf -r /tf_static:=/lee/tf_static

ros2 run tf2_ros tf2_echo map_lee odom_lee \
  --ros-args -r /tf:=/lee/tf -r /tf_static:=/lee/tf_static

ros2 run tf2_ros tf2_echo base_footprint base_scan \
  --ros-args -r /tf:=/lee/tf -r /tf_static:=/lee/tf_static
```

TF topic 확인:

```bash
ros2 topic echo /lee/tf --once
ros2 topic echo /lee/tf_static --once
```

---

## 4. Gazebo / URDF 실행

Gazebo 로봇 실행:

```bash
ros2 launch lee_robot_description gazebo.launch.py
```

URDF/RViz 표시:

```bash
ros2 launch lee_robot_description display.launch.py
```

센서 topic 확인:

```bash
ros2 topic list | grep /lee
ros2 topic echo /lee/scan --once
ros2 topic echo /lee/odom --once
ros2 topic echo /lee/imu --once
```

cmd_vel 테스트:

```bash
ros2 topic pub /lee/cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.1}, angular: {z: 0.0}}" --once
```

---

## 5. rosbag 기록과 재생

기록:

```bash
ros2 bag record /lee/scan /lee/odom /lee/tf /lee/tf_static /clock
```

재생:

```bash
ros2 bag play <bag_dir> --clock
```

반복 재생:

```bash
ros2 bag play <bag_dir> --loop --clock
```

느리게 재생:

```bash
ros2 bag play <bag_dir> --clock -r 0.1
```

namespace 없는 bag을 현재 `/lee` 구조로 재생할 때 예시:

```bash
ros2 bag play "$BAG_DIR" --loop -r 0.1 --clock \
  --remap /scan:=/lee/scan \
  --remap /odom:=/lee/odom \
  --remap /tf:=/lee/tf \
  --remap /tf_static:=/lee/tf_static
```

주의:

```text
remap은 topic 이름만 바꾼다.
message 안의 header.frame_id는 자동으로 바뀌지 않는다.
rosbag 원본 데이터는 현재 저장소에 올리지 않는다.
```

---

## 6. SLAM 실행과 map 저장

SLAM 실행:

```bash
ros2 launch lee_robot_description slam.launch.py
```

map topic 확인:

```bash
ros2 topic echo /lee/map --once
ros2 topic info /lee/map
```

TF 확인:

```bash
ros2 run tf2_ros tf2_echo map_lee odom_lee \
  --ros-args -r /tf:=/lee/tf -r /tf_static:=/lee/tf_static
```

map 저장:

```bash
ros2 run nav2_map_server map_saver_cli -f slam_map --ros-args -r map:=/lee/map
```

저장 결과 확인:

```bash
ls -lh slam_map.yaml slam_map.pgm
cat slam_map.yaml
```

---

## 7. AMCL 실행과 initialpose

localization만 실행:

```bash
ros2 launch lee_robot_description localization.launch.py
```

또는 localization과 Nav2 navigation stack을 한 번에 실행:

```bash
ros2 launch lee_robot_description nav2.launch.py
```

AMCL 관련 topic 확인:

```bash
ros2 topic list | grep -E 'amcl|particle|initialpose|map'
```

현재 launch 구조에서는 `map_server`와 `amcl` node 이름이 root namespace에 있을 수 있다. 먼저 실제 topic 이름을 확인한 뒤 echo한다.

```bash
ros2 topic echo /amcl_pose --once
ros2 topic echo /particle_cloud --once
# namespace가 붙어 있다면:
ros2 topic echo /lee/amcl_pose --once
ros2 topic echo /lee/particle_cloud --once
```

initialpose CLI 예시:

```bash
ros2 topic pub --once /initialpose geometry_msgs/msg/PoseWithCovarianceStamped "
header:
  frame_id: 'map_lee'
pose:
  pose:
    position:
      x: 0.0
      y: 0.0
      z: 0.0
    orientation:
      x: 0.0
      y: 0.0
      z: 0.0
      w: 1.0
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

TF 확인:

```bash
ros2 run tf2_ros tf2_echo map_lee odom_lee \
  --ros-args -r /tf:=/lee/tf -r /tf_static:=/lee/tf_static
```

---

## 8. Nav2 실행과 goal 전송

Nav2는 아래 두 방식 중 하나만 선택한다. 같은 세션에서 중복 실행하지 않는다.

### 방식 A: localization + Nav2 통합 실행

```bash
ros2 launch lee_robot_description nav2.launch.py
```

### 방식 B: localization과 Nav2 stack 분리 실행

Terminal 1:

```bash
ros2 launch lee_robot_description localization.launch.py
```

Terminal 2:

```bash
ros2 launch lee_robot_description nav2_navigation.launch.py
```

Nav2 action 확인:

```bash
ros2 action list | grep navigate
ros2 action info /lee/navigate_to_pose
```

CLI goal 예시:

```bash
ros2 action send_goal /lee/navigate_to_pose nav2_msgs/action/NavigateToPose \
"{pose: {header: {frame_id: 'map_lee'}, pose: {position: {x: 1.0, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}}"
```

plan / cmd_vel 확인:

```bash
ros2 topic echo /lee/plan --once
ros2 topic echo /lee/cmd_vel
```

---

## 9. Lifecycle 확인

lifecycle node 목록:

```bash
ros2 lifecycle nodes
```

Localization 쪽은 root namespace로 보일 수 있다.

```bash
ros2 lifecycle get /map_server
ros2 lifecycle get /amcl
```

Nav2 navigation stack은 기본적으로 `/lee` namespace 기준으로 확인한다.

```bash
ros2 lifecycle get /lee/planner_server
ros2 lifecycle get /lee/controller_server
ros2 lifecycle get /lee/bt_navigator
ros2 lifecycle get /lee/behavior_server
```

수동 전환 예시:

```bash
ros2 lifecycle set /map_server configure
ros2 lifecycle set /map_server activate
```

---

## 10. Parameter 확인

```bash
ros2 param list /lee/controller_server
ros2 param get /lee/controller_server controller_plugins
ros2 param get /lee/controller_server goal_checker_plugins
ros2 param get /lee/controller_server progress_checker_plugin
```

AMCL parameter 확인:

```bash
ros2 param list /amcl
ros2 param get /amcl base_frame_id
ros2 param get /amcl global_frame_id
ros2 param get /amcl odom_frame_id
```

AMCL node가 `/lee/amcl`로 보이면 그 이름으로 바꿔 확인한다.

---

## 11. Python/OpenCV/YOLO 쪽 빠른 확인

카메라 장치 확인:

```bash
ls /dev/video*
```

OpenCV camera index 테스트는 각 day 문서의 Python script 기준으로 확인한다.

YOLO model 경로 문제 확인:

```bash
find $ROS2_WS -name 'yolov8n.pt'
```

주의:

```text
YOLO model_path가 상대경로이면 실행 위치에 따라 파일을 못 찾을 수 있다.
```
