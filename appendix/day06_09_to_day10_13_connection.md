# Day 06~09 -> Day 10~13 연결표

이 문서는 ROS2 기본기와 Gazebo/SLAM/AMCL/Nav2 문서를 연결하기 위한 빠른 참조표이다.

## 개념 연결

| Day 06~09 개념 | 뒤쪽에서 나타나는 위치 | 연결 의미 |
|---|---|---|
| workspace/package | 모든 실습 | `colcon build`, `source install/setup.bash`, package 실행 |
| executable | Day 07 camera, Day 10 launch | `ros2 run <package> <executable>`의 두 번째 이름 |
| node name | Day 08 parameter, Day 13 Nav2 | YAML 최상위 key, `ros2 param get /node` 대상 |
| topic | Day 10~13 전체 | `/scan`, `/odom`, `/map`, `/cmd_vel`, `/tf` |
| message type | Day 09 sensor, Day 11~13 | `LaserScan`, `Odometry`, `OccupancyGrid`, `Twist` |
| service | Day 11~12 lifecycle/map | map server lifecycle, clear costmap, snapshot |
| action | Day 13 Nav2 | `/robot_ns/navigate_to_pose` |
| launch | Day 10~13 전체 | 여러 node/parameter/remap/namespace 통합 실행 |
| parameter | Day 11~13 전체 | SLAM/AMCL/Nav2 설정 |
| custom msg | Day 09 YOLO TF | detection 데이터를 구조화해서 TF broadcaster 입력으로 사용 |
| TF2 | Day 10~13 전체 | map/odom/base/sensor 좌표계 연결 |
| rosbag | Day 10~11, Day 09 | sensor/TF/topic 기록과 재현 |
| rqt/RViz | Day 08~13 | topic, image, TF, map, particle, goal 시각화 |

## topic 연결

| Topic | 처음 배우는 기반 | 실제 사용 위치 |
|---|---|---|
| `/image_raw0` | Day 07 camera topic | Day 08/09 camera/YOLO pipeline |
| `/img_yolo1` | Day 08 custom msg | Day 09 YOLO TF broadcaster 입력 |
| `/tf`, `/tf_static` | Day 09 TF2 | Day 10~13 전체 |
| `/robot_ns/scan` | Day 09 LaserScan | Day 11 SLAM, Day 12 AMCL, Day 13 costmap |
| `/robot_ns/odom` | Day 09 Odometry | Day 11~13 pose/TF 기반 |
| `/robot_ns/map` | Day 11 SLAM/map_server | Day 12 AMCL, Day 13 global costmap |
| `/robot_ns/cmd_vel` | Day 06/07 Twist topic | Day 13 controller output |

## frame 연결

| Frame | 의미 | 관련 문서 |
|---|---|---|
| `map_robot_ns` | 지도 기준 전역 frame | Day 11~13 |
| `odom_robot_ns` | odometry 기준 frame | Day 10~13 |
| `base_footprint` | 2D navigation 로봇 기준 | Day 12~13 |
| `base_link_robot_ns` | 로봇 본체 기준 | Day 10 |
| `camera_frame`, `camera_link_lee` | 카메라 기준 | Day 09 |
| `object_person_0` | YOLO detection object frame | Day 09 |

## 디버깅 연결

| 증상 | 먼저 볼 기본기 |
|---|---|
| `Package not found` | Day 06 source/workspace/package |
| `No executable found` | Day 06 executable 등록 |
| topic은 있는데 데이터가 안 옴 | Day 07 pub/sub topic/type/QoS |
| service call 타입 오류 | Day 07 service/interface 확인 |
| action goal이 안 먹음 | Day 07 action, Day 13 namespace |
| parameter가 적용 안 됨 | Day 08 YAML node name, launch parameters |
| RViz No transform | Day 09 TF2 frame tree |
| SLAM/AMCL이 scan을 못 씀 | Day 09 LaserScan header.frame_id + TF |
| rosbag replay가 재현 안 됨 | Day 09 rosbag + `/clock` + `/tf` 기록 |
| Nav2 plugin 설정이 비어 있음 | Day 08 launch/parameter namespace 구조 |
