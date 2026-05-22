# Troubleshooting Index

이 문서는 각 Day 폴더에 흩어진 troubleshooting 문서를 빠르게 찾기 위한 색인이다.

가장 먼저 볼 문서는 `appendix/troubleshooting_quick_diagnosis.md`다. 이 문서에서 증상별로 첫 확인 명령을 고른 뒤, Day별 troubleshooting 문서로 들어간다.

---

## 1. 전체 원칙

문제가 생기면 아래 순서로 본다.

```text
1. 실행한 명령어가 맞는가?
2. source install/setup.bash를 했는가?
3. node가 떠 있는가?
4. topic/action/service 이름이 맞는가?
5. message가 실제로 흐르는가?
6. frame_id와 TF chain이 맞는가?
7. lifecycle 상태가 active인가?
8. parameter가 YAML 기준으로 적용되었는가?
9. RViz 표시 문제인지 ROS graph 문제인지 분리했는가?
```

---

## 2. 빠른 진단 문서

| 문서 | 역할 |
|---|---|
| `appendix/troubleshooting_quick_diagnosis.md` | SLAM/AMCL/Nav2 증상별 첫 확인 명령과 이동 경로 |
| `appendix/ros2_navigation_debug_order.md` | ROS graph -> topic -> message -> frame -> lifecycle -> parameter 순서의 공통 점검 |

---

## 3. Day별 troubleshooting 문서

| 영역 | 문서 | 주로 다루는 문제 |
|---|---|---|
| Python/OpenCV/YOLO | `day_01_05_python_opencv_foundation/troubleshooting/python_opencv_yolo_troubleshooting.md` | camera index, OpenCV display, YOLO model path, NIS log |
| ROS2 foundation | `day_06_09_ros2_foundation/troubleshooting/ros2_foundation_troubleshooting.md` | package build, topic/service/action, custom interface, launch/parameter |
| Gazebo/URDF | `day_10_gazebo_urdf/troubleshooting/gazebo_day10_troubleshooting.md` | robot spawn, plugin topic, /clock, RViz, LaserScan QoS |
| SLAM | `day_11_slam/troubleshooting/slam_day11_troubleshooting.md` | /scan, TF, map 생성, map 저장, rosbag remap |
| AMCL | `day_12_amcl_mcl/troubleshooting/amcl_day12_troubleshooting.md` | initialpose, particle 수렴, map->odom TF, map/world 불일치 |
| Nav2 | `day_13_nav2/troubleshooting/nav2_day13_troubleshooting.md` | lifecycle, goal 실패, costmap, planner/controller, cmd_vel |

---

## 4. 증상별 빠른 이동

### 빌드/패키지 인식 문제

볼 문서:

```text
day_06_09_ros2_foundation/troubleshooting/ros2_foundation_troubleshooting.md
appendix/full_command_quick_reference.md
```

확인 명령:

```bash
colcon build
source install/setup.bash
ros2 pkg list | grep 패키지명
```

---

### topic은 있는데 데이터가 안 나옴

볼 문서:

```text
appendix/ros2_navigation_debug_order.md
```

확인 명령:

```bash
ros2 topic info /topic_name
ros2 topic echo /topic_name --once
ros2 topic hz /topic_name
```

---

### RViz에 안 보임

볼 문서:

```text
day_10_gazebo_urdf/06_rosbag_rviz_remap.md
appendix/ros2_navigation_debug_order.md
```

확인 포인트:

```text
- Fixed Frame
- display topic 이름
- QoS
- TF chain
- namespace
```

---

### SLAM map이 안 생김

볼 문서:

```text
day_11_slam/08_runtime_observations_without_code_changes.md
day_11_slam/troubleshooting/slam_day11_troubleshooting.md
appendix/validation_sequence_gazebo_slam_amcl_nav2.md
```

확인 명령:

```bash
ros2 topic echo /robot_ns/scan --once
ros2 run tf2_ros tf2_echo odom_robot_ns base_footprint
ros2 topic echo /robot_ns/map --once
```

---

### AMCL particle이 수렴하지 않음

볼 문서:

```text
day_12_amcl_mcl/background/initial_pose_covariance_and_convergence.md
day_12_amcl_mcl/troubleshooting/amcl_day12_troubleshooting.md
```

확인 포인트:

```text
- initialpose를 줬는가?
- map과 world가 맞는가?
- /robot_ns/scan frame_id와 TF가 맞는가?
- map_robot_ns -> odom_robot_ns TF가 생기는가?
```

---

### Nav2 goal이 실패함

볼 문서:

```text
day_13_nav2/08_runtime_observations_without_code_changes.md
day_13_nav2/troubleshooting/nav2_day13_troubleshooting.md
appendix/ros2_navigation_debug_order.md
```

확인 명령:

```bash
ros2 action info /robot_ns/navigate_to_pose
ros2 lifecycle get /robot_ns/planner_server
ros2 lifecycle get /robot_ns/controller_server
ros2 topic echo /robot_ns/plan --once
ros2 topic echo /robot_ns/cmd_vel
```

---

## 5. 자주 나오는 근본 원인

| 증상 | 흔한 원인 |
|---|---|
| package가 안 보임 | `source install/setup.bash` 누락, build 실패 |
| topic 이름이 다름 | namespace/remap 차이 |
| RViz에 map이 안 보임 | Fixed Frame 불일치, `/robot_ns/map` 미발행 |
| scan은 있는데 SLAM이 안 됨 | scan frame과 TF chain 불일치 |
| rosbag remap 후에도 안 됨 | frame_id는 remap으로 바뀌지 않음 |
| AMCL이 안 잡힘 | initialpose 누락, map/world 불일치 |
| Nav2 action이 없음 | navigation launch 미실행, namespace 다름 |
| cmd_vel은 나오는데 로봇이 안 움직임 | diff_drive plugin subscribe topic 불일치 |
