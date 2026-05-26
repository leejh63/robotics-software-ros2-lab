# Topic / Frame 정리표 - Day 10 기준

## 0. 이 표의 역할

이 문서는 Day 10 Gazebo/URDF 이후에 처음 정리한 topic-frame 빠른 참조표다.

최신 통합 기준은 [`topic_frame_message_action_master_table.md`](topic_frame_message_action_master_table.md)를 우선한다. 다른 표들의 역할은 [`table_reference_guide.md`](table_reference_guide.md)를 본다.

ROS2에서 topic 이름과 frame 이름은 다르다.  
Day 10 이후 SLAM/AMCL/Nav2에서 계속 헷갈릴 수 있으므로 이 표를 기준으로 정리한다.

## 1. 주요 Topic

| Topic | 메시지 성격 | 발행 주체 | 사용처 |
|---|---|---|---|
| `/robot_ns/cmd_vel` | 속도 명령 | teleop, 회피 노드, 이후 Nav2 controller | Gazebo diff_drive plugin |
| `/robot_ns/odom` | Odometry | Gazebo diff_drive plugin | RViz2, SLAM, AMCL/Nav2 |
| `/robot_ns/scan` | LaserScan | Gazebo LiDAR plugin | RViz2, 회피 노드, SLAM, AMCL |
| `/robot_ns/imu` | IMU | Gazebo IMU plugin | RViz2, 센서 확인 |
| `/robot_ns/image_raw` | Camera image | Gazebo camera plugin 또는 republish | RViz2, vision pipeline |
| `/robot_ns/joint_states` | Joint state | Gazebo joint state plugin | robot_state_publisher |
| `/robot_ns/robot_description` | URDF XML | robot_state_publisher 쪽 설정/launch | spawn_entity.py, RViz RobotModel |
| `/robot_ns/tf` | Dynamic TF | robot_state_publisher 등 | RViz2, SLAM/AMCL/Nav2 |
| `/robot_ns/tf_static` | Static TF | robot_state_publisher 등 | RViz2, SLAM/AMCL/Nav2 |
| `/clock` | Simulation time | Gazebo 또는 rosbag play --clock | use_sim_time 사용하는 노드 |

## 2. 주요 Frame

실제 frame 이름은 xacro와 launch 설정에 따라 달라질 수 있다.  
아래는 이 저장소에서 반복적으로 사용하는 frame 기준이다.

| Frame | 역할 |
|---|---|
| `base_footprint` | 로봇 바닥 기준 좌표계 |
| `base_link` | 로봇 본체 기준 좌표계 |
| `base_scan` | LiDAR 센서가 붙은 좌표계 |
| `camera_link` 또는 카메라 계열 frame | 카메라 기준 좌표계 |
| `odom_robot_ns` | odometry 기준 좌표계 |
| `map_robot_ns` | 지도 기준 좌표계. Day 11/12에서 중요 |

## 3. Topic과 Frame 구분 예시

```text
/robot_ns/scan
  ROS2 topic 이름이다.
  LaserScan 메시지가 흐른다.

base_scan
  LaserScan 메시지 안의 frame_id로 쓰일 수 있는 좌표계 이름이다.
  센서가 로봇 어디에 붙어 있는지 나타낸다.
```

```text
/robot_ns/odom
  Odometry 메시지가 흐르는 topic이다.

odom_robot_ns
  odometry 기준 frame 이름이다.
```

## 4. Day 11 이후 연결

Day 10에서 확인한 topic/frame은 이후 이렇게 쓰인다.

| Day | 필요한 입력 | 설명 |
|---|---|---|
| Day 11 SLAM | `/robot_ns/scan`, `/robot_ns/odom`, TF | 지도 생성 |
| Day 12 AMCL | map, `/robot_ns/scan`, `/robot_ns/odom`, TF | 지도 위 위치 추정 |
| Day 13 Nav2 | map, AMCL pose, costmap sensor, TF | 목표 지점 주행 |

## 5. 확인 명령어

```bash
ros2 topic list | grep /robot_ns
ros2 topic echo /robot_ns/scan --once
ros2 topic echo /robot_ns/odom --once
ros2 topic echo /robot_ns/tf_static --once
ros2 topic echo /robot_ns/tf --once
```

TF 관계를 더 명확히 보고 싶으면 다음 도구를 사용한다.

```bash
ros2 run tf2_tools view_frames
ros2 run tf2_ros tf2_echo odom_robot_ns base_footprint
```

단, frame 이름은 실제 xacro/launch 설정과 일치해야 한다.
