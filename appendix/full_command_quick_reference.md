# 전체 명령어 빠른 참조

이 문서는 Day 01~13 전체 실습에서 자주 쓰는 명령어를 한 곳에 모은 것이다.

기준 환경:

```bash
cd $ROS2_WS
source /opt/ros/humble/setup.bash
source install/setup.bash
```

명령어를 그대로 복사하기 전에 [command_execution_conventions.md](command_execution_conventions.md)를 먼저 확인한다.

핵심 구분:

```text
lee_robot_description  = package name 예시
robot_ns               = namespace 예시
map_robot_ns           = frame name 예시
```

`ros2 launch`에는 namespace가 아니라 package name이 들어간다. 반대로 `/robot_ns/scan`처럼 `/`로 시작하는 값은 topic 이름이다.

## 명령어 블록 구분

이 문서의 명령어는 다음 기준으로 읽는다.

| 구분 | 예시 | 의미 |
|---|---|---|
| 실제 실행 명령 | `ros2 node list` | 실행 중인 환경에서 바로 확인 가능 |
| placeholder 포함 명령 | `ros2 bag play <bag_dir> --clock` | `<bag_dir>`를 실제 값으로 바꿔야 함 |
| namespace 예시 | `/robot_ns/scan` | 실제 topic 이름은 `ros2 topic list`로 확인 |
| frame 예시 | `map_robot_ns` | message 내부 `header.frame_id` 또는 TF frame 이름 |

실행이 안 되면 명령어 자체를 수정하기 전에 `ros2 topic list`, `ros2 node list`, `ros2 action list`로 실제 이름을 먼저 확인한다.

---


## 1. 빌드와 환경 설정

```bash
cd $ROS2_WS
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

node 정보:

```bash
ros2 node info /노드이름
```

topic 정보:

```bash
ros2 topic info /robot_ns/scan
ros2 topic echo /robot_ns/scan --once
ros2 topic hz /robot_ns/scan
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

두 frame 관계 확인:

```bash
ros2 run tf2_ros tf2_echo odom_robot_ns base_footprint
ros2 run tf2_ros tf2_echo map_robot_ns odom_robot_ns
ros2 run tf2_ros tf2_echo base_footprint base_scan
```

TF topic 확인:

```bash
ros2 topic echo /robot_ns/tf --once
ros2 topic echo /robot_ns/tf_static --once
```

---

## 4. Gazebo / URDF 실행

Gazebo 로봇 실행:

```bash
ros2 launch lee_robot_description gaze.launch.py
```

URDF/RViz 표시:

```bash
ros2 launch lee_robot_description display.launch.py
```

센서 topic 확인:

```bash
ros2 topic list | grep /robot_ns
ros2 topic echo /robot_ns/scan --once
ros2 topic echo /robot_ns/odom --once
ros2 topic echo /robot_ns/imu --once
```

cmd_vel 테스트:

```bash
ros2 topic pub /robot_ns/cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.1}, angular: {z: 0.0}}" --once
```

---

## 5. rosbag 기록과 재생

기록:

```bash
ros2 bag record /robot_ns/scan /robot_ns/odom /robot_ns/tf /robot_ns/tf_static /clock
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

namespace 없는 bag을 `/robot_ns` 구조로 재생할 때 예시:

```bash
ros2 bag play "$BAG_DIR" --loop -r 0.1 --clock \
  --remap /scan:=/robot_ns/scan \
  --remap /odom:=/robot_ns/odom \
  --remap /tf:=/robot_ns/tf \
  --remap /tf_static:=/robot_ns/tf_static
```

주의:

```text
remap은 topic 이름만 바꾼다.
message 안의 frame_id는 자동으로 바뀌지 않는다.
```

---

## 6. SLAM 실행과 map 저장

SLAM 실행:

```bash
ros2 launch lee_robot_description slam.launch.py
```

map topic 확인:

```bash
ros2 topic echo /robot_ns/map --once
ros2 topic info /robot_ns/map
```

map 저장:

```bash
ros2 run nav2_map_server map_saver_cli -f slam_map --ros-args -r map:=/robot_ns/map
```

저장 결과 확인:

```bash
ls -lh slam_map.yaml slam_map.pgm
cat slam_map.yaml
```

---

## 7. AMCL 실행과 initialpose

localization 실행:

```bash
ros2 launch lee_robot_description nav2.launch.py
```

AMCL 관련 topic 확인:

```bash
ros2 topic list | grep -E 'amcl|particle|initialpose|map'
```

AMCL topic은 launch namespace 설정에 따라 `/amcl_pose` 또는 `/robot_ns/amcl_pose`처럼 달라질 수 있다. 먼저 실제 topic 이름을 확인한 뒤 그 이름으로 echo한다.

```bash
ros2 topic echo /amcl_pose --once
ros2 topic echo /particle_cloud --once
# namespace가 붙어 있다면:
ros2 topic echo /robot_ns/amcl_pose --once
ros2 topic echo /robot_ns/particle_cloud --once
```

initialpose CLI 예시:

```bash
ros2 topic pub /initialpose geometry_msgs/msg/PoseWithCovarianceStamped \
"{header: {frame_id: 'map_robot_ns'}, pose: {pose: {position: {x: 0.0, y: 0.0, z: 0.0}, orientation: {z: 0.0, w: 1.0}}, covariance: [0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0685]}}" \
--once
```

TF 확인:

```bash
ros2 run tf2_ros tf2_echo map_robot_ns odom_robot_ns
```

---

## 8. Nav2 실행과 goal 전송

localization terminal:

```bash
ros2 launch lee_robot_description nav2.launch.py
```

navigation terminal:

```bash
ros2 launch lee_robot_description nav2_navigation.launch.py
```

Nav2 action 확인:

```bash
ros2 action list | grep navigate
ros2 action info /robot_ns/navigate_to_pose
```

CLI goal 예시:

```bash
ros2 action send_goal /robot_ns/navigate_to_pose nav2_msgs/action/NavigateToPose \
"{pose: {header: {frame_id: 'map_robot_ns'}, pose: {position: {x: 1.0, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}}"
```

cmd_vel 확인:

```bash
ros2 topic echo /robot_ns/cmd_vel
```

plan 확인:

```bash
ros2 topic echo /robot_ns/plan --once
```

---

## 9. Lifecycle 확인

lifecycle node 목록:

```bash
ros2 lifecycle nodes
```

상태 확인:

```bash
ros2 lifecycle get /robot_ns/map_server
ros2 lifecycle get /robot_ns/amcl
ros2 lifecycle get /robot_ns/planner_server
ros2 lifecycle get /robot_ns/controller_server
ros2 lifecycle get /robot_ns/bt_navigator
```

수동 전환 예시:

```bash
ros2 lifecycle set /robot_ns/map_server configure
ros2 lifecycle set /robot_ns/map_server activate
```

---

## 10. Parameter 확인

```bash
ros2 param list /robot_ns/controller_server
ros2 param get /robot_ns/controller_server controller_plugins
ros2 param get /robot_ns/controller_server goal_checker_plugins
ros2 param get /robot_ns/controller_server progress_checker_plugin
```

AMCL parameter 확인:

```bash
ros2 param list /robot_ns/amcl
ros2 param get /robot_ns/amcl base_frame_id
ros2 param get /robot_ns/amcl global_frame_id
ros2 param get /robot_ns/amcl odom_frame_id
```

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
