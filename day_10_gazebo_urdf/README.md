# Day 10 - Gazebo / URDF / Xacro 학습 정리

## 1. 이 폴더의 목적

Day 10은 ROS2 Navigation 실습에서 **가상 로봇과 센서 데이터를 준비하는 단계**이다.

여기서 목표는 “Gazebo를 띄웠다”가 아니다. 정확한 목표는 아래 흐름을 이해하는 것이다.

```text
Xacro/URDF로 로봇 구조 작성
-> robot_state_publisher가 link/joint 구조를 TF로 변환
-> Gazebo가 world를 실행
-> spawn_entity.py가 URDF를 읽어 Gazebo 안에 로봇 생성
-> Gazebo plugin이 /robot_ns/scan, /robot_ns/odom, /robot_ns/imu, /robot_ns/image_raw 같은 ROS2 topic 생성
-> RViz2, teleop, 간단한 LiDAR 회피 노드로 동작 확인
-> Day 11 SLAM 입력인 LaserScan/Odometry/TF 준비
```

즉 Day 10은 이후 SLAM/AMCL/Nav2를 위한 **시뮬레이션 로봇 + 센서 topic 공급층**이다.

---

## 2. 실제 기준 코드 위치

이 문서의 기준은 아래 패키지다.

```text
day_67/ws/lee_robot_description/
```

주의할 점은 이 패키지가 일반적인 `ws/src/` 아래가 아니라, 현재 압축본에서는 `ws/lee_robot_description/` 위치에 있다는 것이다. 문서에서는 실제 파일 위치를 기준으로 설명한다.

```text
lee_robot_description/
├── package.xml
├── CMakeLists.txt
├── urdf/
│   ├── turtlebot.xacro
│   ├── turtlebot_gaze.xacro
│   └── turtle_from_xacro.urdf
├── launch/
│   ├── display.launch.py
│   ├── gaze.launch.py
│   ├── slam.launch.py
│   ├── amcl.launch.py
│   ├── amcl_full.launch.py
│   ├── nav2.launch.py
│   └── nav2_navigation.launch.py
├── config/
│   ├── slam_param.yaml
│   ├── amcl_param.yaml
│   └── nav2_params.yaml
├── worlds/
│   ├── lee_world.world
│   ├── simple_maze.world
│   └── slam.world
├── rviz/
│   ├── turtlebot.rviz
│   ├── gaze,rviz.rviz
│   ├── slam.rviz
│   └── amcl.rviz
└── scripts/
    └── lidar_wall_follower.py
```

---

## 3. 문서 구성

| 문서 | 역할 |
|---|---|
| `00_source_file_map.md` | 실제 `lee_robot_description` 파일 역할 지도 |
| `01_overview_flow.md` | Day 10 전체 실행 흐름과 Day 11 연결 |
| `02_urdf_xacro_modeling.md` | URDF/Xacro, link/joint/visual/collision/inertial 설명 |
| `03_robot_state_publisher_tf_flow.md` | `robot_state_publisher`, `robot_description`, `/tf`, `/tf_static` 흐름 |
| `04_gazebo_plugin_topic_flow.md` | Gazebo plugin이 ROS2 topic을 만드는 구조 |
| `05_world_launch_namespace.md` | world, launch, namespace, remap, spawn 흐름 |
| `06_rosbag_rviz_remap.md` | rosbag2/RViz2/remap/use_sim_time 정리 |
| `07_lidar_avoidance_and_laserscan.md` | `lidar_wall_follower.py`, LaserScan angle/ranges 해설 |
| `08_runtime_observations_without_code_changes.md` | 코드 수정 없이 기록한 실행상 주의점 |
| `09_day10_review_questions.md` | 복습 질문 |
| `background/` | Day 10 이해에 필요한 배경지식 |
| `commands/` | 실행/확인 명령어 |
| `troubleshooting/` | 문제 상황별 확인 순서 |

---

## 4. Day 10에서 반드시 잡아야 하는 핵심

### 4.1 RViz2와 Gazebo는 역할이 다르다

```text
RViz2
  ROS2 topic, TF, robot_description을 시각화하는 도구
  물리 시뮬레이터가 아님

Gazebo
  물리 계산, 센서 시뮬레이션, 로봇 동작을 수행하는 시뮬레이터
  plugin을 통해 ROS2 topic과 연결됨
```

RViz2에서 로봇이 보인다는 것은 모델/TF 시각화가 된다는 뜻이다. Gazebo에서 로봇이 움직인다는 것은 plugin, joint, collision, inertial, `/cmd_vel` 연결까지 맞아야 한다는 뜻이다.

### 4.2 `turtlebot.xacro`와 `turtlebot_gaze.xacro`는 역할이 다르다

```text
turtlebot.xacro
  로봇의 구조 정의
  base_link, base_footprint, wheel, base_scan, imu_link, camera_link 등 생성

turtlebot_gaze.xacro
  Gazebo 전용 설정 정의
  diff drive, joint state, LiDAR, IMU, camera plugin 연결
```

이름은 `gaze`지만 역할상 “Gazebo 설정 xacro”에 가깝다. 문서에서는 실제 파일명을 유지하되 역할을 명확히 구분한다.

### 4.3 topic 이름과 frame 이름은 다르다

```text
/robot_ns/scan     = LaserScan 메시지가 흐르는 topic
base_scan     = LaserScan이 어느 좌표계 기준인지 나타내는 frame_id

/robot_ns/odom     = Odometry 메시지가 흐르는 topic
odom_robot_ns      = odometry 기준 좌표계 frame

/robot_ns/tf       = TF 메시지가 흐르는 topic
base_link     = 로봇 몸체 좌표계 frame
```

`namespace`는 topic 이름을 나누기 위한 장치이고, `frame_id`는 좌표계를 표현하는 이름이다. 이 둘을 섞어 이해하면 SLAM/AMCL/Nav2에서 계속 헷갈린다.

---

## 5. Day 11로 이어지는 핵심 연결

Day 10 출력은 Day 11 SLAM의 입력이 된다.

```text
Gazebo diff_drive plugin
  -> /robot_ns/odom
  -> odom_robot_ns -> base_footprint 계열 TF

Gazebo LiDAR plugin
  -> /robot_ns/scan
  -> frame_id: base_scan

robot_state_publisher
  -> /robot_ns/tf
  -> /robot_ns/tf_static

이 세 가지가 맞물려야 SLAM Toolbox가 scan을 지도 좌표계로 누적할 수 있다.
```

따라서 Day 10의 목표는 “로봇이 화면에 보임”에서 끝나면 안 된다. 최소한 아래를 확인해야 한다.

```bash
ros2 topic list | grep /robot_ns
ros2 topic echo /robot_ns/scan --qos-reliability best_effort --once
ros2 topic echo /robot_ns/odom --once
ros2 topic echo /robot_ns/joint_states --once
ros2 run tf2_tools view_frames --ros-args -r /tf:=/robot_ns/tf -r /tf_static:=/robot_ns/tf_static
```

---

## 6. 현재 문서에서 하지 않은 것

이번 단계에서도 **코드는 수정하지 않았다.**

한 일은 다음뿐이다.

```text
- 기존 Day 10 문서 재정렬
- 실제 lee_robot_description 코드 기준 파일 역할 설명
- URDF/Xacro/Gazebo/TF/rosbag 배경지식 보강
- 실행 중 문제가 될 수 있는 부분을 observation 문서로 분리
- Day 11 SLAM으로 이어지는 입력 데이터 흐름 명확화
```
