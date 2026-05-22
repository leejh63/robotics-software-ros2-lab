# Topic / Frame / Message / Action Master Table

이 문서는 Day 06~13에서 등장하는 주요 topic, frame, message, action을 한 곳에 모은 표다.

주의:

```text
topic 이름과 frame 이름은 다르다.
action 이름과 topic 이름도 다르다.
```

---

## 0. 이 표의 역할

이 문서는 이 저장소의 topic/frame/message/action **기준표**다.

다른 표 문서는 Day별 빠른 참조표다. 표현이 다르게 보이면 이 문서를 우선한다.

관련 표의 역할은 [`table_reference_guide.md`](table_reference_guide.md)를 본다.

---

## 1. 주요 topic 통합표

| Topic | Message Type | 주 발행자 | 주 사용처 | 비고 |
|---|---|---|---|---|
| `/robot_ns/scan` | `sensor_msgs/msg/LaserScan` | Gazebo LiDAR plugin | SLAM, AMCL, costmap, RViz | `header.frame_id`는 보통 `base_scan` |
| `/robot_ns/odom` | `nav_msgs/msg/Odometry` | Gazebo diff_drive plugin | SLAM, AMCL, Nav2, RViz | odometry estimate |
| `/robot_ns/cmd_vel` | `geometry_msgs/msg/Twist` | teleop, Nav2 controller, avoidance node | Gazebo diff_drive plugin | 최종 속도 명령 |
| `/robot_ns/map` | `nav_msgs/msg/OccupancyGrid` | SLAM Toolbox 또는 map_server | RViz, AMCL, Nav2 costmap | `header.frame_id`는 `map_robot_ns` |
| `/robot_ns/tf` | `tf2_msgs/msg/TFMessage` | robot_state_publisher, SLAM/AMCL, plugins | 전체 navigation stack | dynamic transform |
| `/robot_ns/tf_static` | `tf2_msgs/msg/TFMessage` | robot_state_publisher | 전체 navigation stack | static transform |
| `/robot_ns/imu` | `sensor_msgs/msg/Imu` | Gazebo IMU plugin | RViz, 확장 실습 | 현재 Nav2 핵심 입력은 아님 |
| `/robot_ns/image_raw` | `sensor_msgs/msg/Image` | Gazebo camera plugin | RViz, vision pipeline | Day 10 이후 camera 연결 |
| `/robot_ns/joint_states` | `sensor_msgs/msg/JointState` | Gazebo joint state plugin | robot_state_publisher | joint 기반 TF |
| `/amcl_pose` 또는 `/robot_ns/amcl_pose` | `geometry_msgs/msg/PoseWithCovarianceStamped` | AMCL | RViz, localization 확인 | AMCL node namespace에 따라 달라질 수 있음 |
| `/particle_cloud` 또는 `/robot_ns/particle_cloud` | `nav2_msgs/msg/ParticleCloud` 또는 유사 타입 | AMCL | RViz | particle 분포 시각화 |
| `/initialpose` 또는 `/robot_ns/initialpose` | `geometry_msgs/msg/PoseWithCovarianceStamped` | RViz 또는 CLI | AMCL | AMCL이 실제로 subscribe하는 topic에 맞춰야 함 |
| `/robot_ns/plan` | `nav_msgs/msg/Path` | planner_server | RViz, controller | global path |
| `/clock` | `rosgraph_msgs/msg/Clock` | Gazebo 또는 rosbag | use_sim_time node | simulation time |

---

### AMCL topic namespace 주의

AMCL 관련 topic은 root namespace에 있을 수도 있고 robot namespace 아래에 있을 수도 있다. 따라서 `/amcl_pose`만 고정해서 외우지 말고 아래 순서로 확인한다.

```bash
ros2 node list | sort | grep amcl
ros2 topic list | sort | grep -E 'initialpose|amcl_pose|particle_cloud'
```

```text
/amcl
  -> /initialpose, /amcl_pose, /particle_cloud 가능성이 높음

/robot_ns/amcl
  -> /robot_ns/initialpose, /robot_ns/amcl_pose, /robot_ns/particle_cloud 가능성이 높음
```

상세 기준은 [`amcl_namespace_cases.md`](amcl_namespace_cases.md)를 본다.

---

## 2. 주요 frame 통합표

일반 예제의 `map`, `odom`은 이 문서에서 각각 `map_robot_ns`, `odom_robot_ns`로 기록한다. 역할이 바뀐 것이 아니라, robot namespace가 섞이는 상황에서 frame 충돌을 줄이기 위한 표기다. 자세한 배경은 [`../day_12_amcl_mcl/background/map_odom_namespace_frames.md`](../day_12_amcl_mcl/background/map_odom_namespace_frames.md)를 본다.

| Frame | 일반 예제 대응 | 의미 | 연결 관계 |
|---|---|---|---|
| `map_robot_ns` | `map` | 지도 기준 전역 frame | SLAM 또는 AMCL이 `map_robot_ns -> odom_robot_ns` 관계를 만든다 |
| `odom_robot_ns` | `odom` | odometry 기준 지역 frame | `odom_robot_ns -> base_footprint`로 이어진다 |
| `base_footprint` | `base_link` 또는 `base_footprint` | 로봇 바닥 중심 frame | navigation에서 base frame으로 자주 사용 |
| `base_link` | `base_link` | 로봇 본체 frame | URDF link 구조에 따라 사용 |
| `base_scan` | `laser` 또는 `base_scan` | LiDAR frame | LaserScan의 `header.frame_id`와 연결 |
| `camera_link` | `camera_link` | camera frame | camera image/TF 실습과 연결 |
| `object_person_0` 등 | 사용자 정의 object frame | YOLO object TF 실습 frame | bbox 기반 시각화용 frame |

핵심 chain:

```text
map_robot_ns -> odom_robot_ns -> base_footprint -> base_link -> base_scan
```

---

## 3. 주요 action

| Action | Type | 주 서버 | 의미 |
|---|---|---|---|
| `/robot_ns/navigate_to_pose` | `nav2_msgs/action/NavigateToPose` | bt_navigator | 목표 pose까지 이동 |
| 사용자 정의 action 예제 | `my_if/action/...` | my_robot_action 예제 | action 구조 학습용 |

Nav2 goal 예시의 핵심:

```text
goal pose의 header.frame_id는 map_robot_ns 기준이어야 한다.
```

---

## 4. 주요 service

| Service | Type | 의미 |
|---|---|---|
| custom AddTwoNum 계열 | `my_if/srv/...` | service request/response 학습 |
| `/map_server/load_map` 계열 | Nav2 map server service | map load 관련 |
| lifecycle 관련 service | `lifecycle_msgs/srv/...` | configure/activate 상태 전환 |

실제 service 이름은 namespace와 launch에 따라 달라질 수 있으므로 항상 아래로 확인한다.

```bash
ros2 service list | sort
```

---

## 5. topic과 frame을 함께 봐야 하는 예시

### LaserScan

```text
Topic: /robot_ns/scan
Type: sensor_msgs/msg/LaserScan
Message header.frame_id: base_scan
```

의미:

```text
/robot_ns/scan이라는 통로로 LaserScan이 흐르고,
그 거리값들은 base_scan 좌표계를 기준으로 측정된 값이다.
```

### Map

```text
Topic: /robot_ns/map
Type: nav_msgs/msg/OccupancyGrid
Message header.frame_id: map_robot_ns
```

의미:

```text
/robot_ns/map이라는 통로로 grid map이 흐르고,
그 map은 map_robot_ns 좌표계를 기준으로 한다.
```

### Navigation Goal

```text
Action: /robot_ns/navigate_to_pose
Type: nav2_msgs/action/NavigateToPose
Goal pose header.frame_id: map_robot_ns
```

의미:

```text
목표 지점은 map_robot_ns 좌표계 기준 좌표로 해석된다.
```

---

## 6. remap 주의사항

```bash
--remap /scan:=/robot_ns/scan
```

이 명령은 topic 이름만 바꾼다.

바뀌는 것:

```text
/scan topic name -> /robot_ns/scan topic name
```

자동으로 바뀌지 않는 것:

```text
LaserScan.header.frame_id
Odometry.header.frame_id
Odometry.child_frame_id
TF message 내부 frame_id / child_frame_id
```

그래서 bag을 재생할 때는 topic 이름과 frame 이름을 둘 다 확인해야 한다.
