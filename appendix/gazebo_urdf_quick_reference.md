# Gazebo / URDF / Xacro Quick Reference

## 1. 핵심 구분

| 개념 | 한 줄 설명 |
|---|---|
| URDF | 로봇 link/joint 구조를 표현하는 XML 형식 |
| Xacro | URDF를 편하게 쓰기 위한 매크로 시스템 |
| SDF/World | Gazebo 환경, 물리, 장애물, 조명 등을 정의하는 형식 |
| RViz2 | ROS2 topic/TF 시각화 도구 |
| Gazebo | 물리/센서 시뮬레이터 |
| robot_state_publisher | URDF + joint_states를 TF로 변환하는 노드 |
| spawn_entity.py | Gazebo에 URDF/SDF model을 생성하는 도구 |

## 2. Day 10 핵심 topic

| topic | type | 주체 | 의미 |
|---|---|---|---|
| `/robot_ns/cmd_vel` | `geometry_msgs/msg/Twist` | teleop/회피/Nav2 -> Gazebo | 속도 명령 |
| `/robot_ns/odom` | `nav_msgs/msg/Odometry` | Gazebo diff_drive | 오도메트리 |
| `/robot_ns/scan` | `sensor_msgs/msg/LaserScan` | Gazebo ray sensor | LiDAR 거리 배열 |
| `/robot_ns/imu` | `sensor_msgs/msg/Imu` | Gazebo IMU | IMU 센서값 |
| `/robot_ns/image_raw` | `sensor_msgs/msg/Image` | Gazebo camera | 카메라 이미지 |
| `/robot_ns/joint_states` | `sensor_msgs/msg/JointState` | Gazebo joint state plugin | 바퀴 joint 상태 |
| `/robot_ns/tf` | `tf2_msgs/msg/TFMessage` | robot_state_publisher / Gazebo | 동적 TF |
| `/robot_ns/tf_static` | `tf2_msgs/msg/TFMessage` | robot_state_publisher | 정적 TF |

## 3. 핵심 frame

| frame | 의미 |
|---|---|
| `odom_robot_ns` | odometry 기준 좌표계 |
| `base_footprint` | 지면 기준 로봇 footprint |
| `base_link` | 로봇 본체 좌표계 |
| `base_scan` | LiDAR 좌표계 |
| `camera_link` | 카메라 좌표계 |
| `imu_link` | IMU 좌표계 |

## 4. 기억할 문장

```text
Topic은 메시지가 흐르는 이름이고, frame은 좌표계 이름이다.
Namespace는 topic 이름을 묶지만 frame 이름을 자동으로 바꾸지는 않는다.
```
