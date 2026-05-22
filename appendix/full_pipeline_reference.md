# Full Pipeline Reference

이 문서는 Day 01~13 전체 학습 흐름을 한 번에 보기 위한 참조 문서다.

---

## 1. 전체 흐름

```text
Python / NumPy / OpenCV
  -> 이미지와 배열 데이터를 다루는 기초

Camera Calibration / YOLO / Kalman
  -> 카메라, 객체 인식, 추적/필터링 기초

ROS2 Foundation
  -> package, node, topic, service, action, launch, parameter, interface

TF2 / Sensor / Rosbag
  -> 좌표계, 센서 데이터, 재현 실험

Gazebo / URDF / Xacro
  -> 가상 로봇, 센서, actuator, ROS topic 연결

SLAM
  -> /scan + /tf + /odom으로 지도 생성

AMCL
  -> 저장 지도 + LiDAR로 현재 위치 추정

Nav2
  -> 현재 위치 + goal + costmap으로 경로와 속도 명령 생성
```

---

## 2. 핵심 데이터 흐름

```text
Gazebo diff_drive / sensor plugins
  -> /robot_ns/odom
  -> /robot_ns/scan
  -> /robot_ns/tf
        ↓
SLAM Toolbox
  -> /robot_ns/map
  -> slam_map.yaml / slam_map.pgm
        ↓
map_server
  -> /robot_ns/map
        ↓
AMCL
  -> /amcl_pose 또는 /robot_ns/amcl_pose
  -> /particle_cloud 또는 /robot_ns/particle_cloud
  -> map_robot_ns -> odom_robot_ns TF
        ↓
Nav2 planner_server
  -> /robot_ns/plan
        ↓
Nav2 controller_server / velocity_smoother
  -> /robot_ns/cmd_vel
        ↓
Gazebo diff_drive plugin
  -> robot motion
```

---

## 3. 내가 직접 작성/설정한 부분과 외부 패키지 역할

| 구분 | 내가 다룬 부분 | 외부 패키지가 제공한 부분 |
|---|---|---|
| ROS2 기본 | node, topic, service, action 예제 코드 | rclpy, rclcpp, ros2cli |
| Interface | msg/srv/action 정의 | rosidl code generation |
| Camera/YOLO | image node, detection msg publish | OpenCV, Ultralytics, cv_bridge |
| TF | broadcaster/listener 실습 | tf2_ros |
| Gazebo | URDF/Xacro, plugin 설정 | gazebo_ros plugins, physics/sensor simulation |
| SLAM | launch/parameter/topic 연결, map 저장 | SLAM Toolbox |
| AMCL | parameter, initialpose, particle 결과 해석 | nav2_amcl |
| Nav2 | launch/parameter/goal/diagnostics | Nav2 planner/controller/BT/costmap |

더 자세한 경계는 아래 문서를 본다.

```text
appendix/external_package_boundary.md
```

---

## 4. 전체 pipeline을 이해하는 질문

### Gazebo 단계

```text
- 로봇 모델은 어디에서 정의되는가?
- 어떤 plugin이 /robot_ns/scan, /robot_ns/odom, /robot_ns/cmd_vel을 만드는가?
- robot_state_publisher는 어떤 TF를 만드는가?
```

### SLAM 단계

```text
- SLAM Toolbox는 어떤 scan과 TF를 입력으로 받는가?
- /robot_ns/map은 어떤 frame 기준인가?
- map_saver_cli는 어떤 topic을 저장하는가?
```

### AMCL 단계

```text
- map_server가 어떤 map을 publish하는가?
- AMCL은 initialpose를 받은 뒤 particle을 어떻게 수렴시키는가?
- AMCL이 map_robot_ns -> odom_robot_ns TF를 발행하는 이유는 무엇인가?
```

### Nav2 단계

```text
- NavigateToPose action goal은 어떤 frame 기준인가?
- planner_server는 어떤 map/costmap을 보고 /robot_ns/plan을 만드는가?
- controller_server는 왜 /robot_ns/cmd_vel을 발행하는가?
- /robot_ns/cmd_vel은 최종적으로 누가 받는가?
```

---

## 5. 왜 map_robot_ns / odom_robot_ns처럼 쓰는가

일반 예제에서는 `map`, `odom`이라는 frame 이름을 많이 쓴다. 이 학습 노트에서는 같은 역할을 아래 이름으로 기록한다.

```text
map      -> map_robot_ns
odom     -> odom_robot_ns
base     -> base_footprint
```

이 이름은 topic namespace와 frame 이름을 구분하기 위한 학습용 표기다.

```text
/robot_ns/map  = topic 이름
map_robot_ns   = frame 이름

/robot_ns/odom = topic 이름
odom_robot_ns  = frame 이름
```

`/robot_ns/scan`처럼 topic을 namespace 아래로 remap해도 `LaserScan.header.frame_id`나 TF 내부 frame 이름이 자동으로 바뀌지는 않는다. 그래서 AMCL/Nav2 parameter의 `global_frame_id`, `odom_frame_id`, `base_frame_id`는 실제 TF tree에 존재하는 frame 이름과 직접 맞춰야 한다.

자세한 설명은 [`../day_12_amcl_mcl/background/map_odom_namespace_frames.md`](../day_12_amcl_mcl/background/map_odom_namespace_frames.md)를 본다.

---

## 6. Message와 frame_id의 관계

ROS2 sensor/navigation 메시지는 대개 header를 가진다.

```text
header.stamp     메시지가 생성된 시간
header.frame_id  이 데이터가 어떤 좌표계 기준인지
```

예시:

```text
/robot_ns/scan topic의 LaserScan.header.frame_id = base_scan
/robot_ns/map topic의 OccupancyGrid.header.frame_id = map_robot_ns
NavigateToPose goal의 header.frame_id = map_robot_ns
```

즉, topic 이름과 frame_id는 같은 것이 아니다.

---

## 7. 단계별 최소 정상 조건

| 단계 | 최소 정상 조건 |
|---|---|
| Gazebo | `/robot_ns/scan`, `/robot_ns/odom`, `/robot_ns/tf`, `/robot_ns/cmd_vel` subscriber 확인 |
| SLAM | `/robot_ns/scan` 수신, TF chain 연결, `/robot_ns/map` 발행 |
| Map Save | `/robot_ns/map` 존재, map_saver remap/저장 경로 정상 |
| AMCL | `/robot_ns/map`, `/robot_ns/scan`, initialpose, `map_robot_ns->odom_robot_ns` 발행 |
| Nav2 | lifecycle active, costmap 발행, `/robot_ns/navigate_to_pose` action server, `/robot_ns/cmd_vel` 발행 |

상세 검증 순서는 아래 문서를 본다.

```text
appendix/validation_sequence_gazebo_slam_amcl_nav2.md
```

---

## 8. 한 줄 요약

```text
Gazebo가 센서/구동 데이터를 만들고,
SLAM이 지도를 만들고,
AMCL이 지도 위 현재 위치를 추정하고,
Nav2가 목표까지 갈 속도 명령을 만들고,
Gazebo가 그 속도 명령으로 로봇을 움직인다.
```
