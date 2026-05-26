# 직접 구성한 범위와 외부 패키지 경계

이 문서는 학습 정리에서 중요한 경계를 정리한다.

```text
직접 작성한 것인가?
외부 패키지를 설정한 것인가?
외부 ROS2 패키지가 내부 기능을 제공한 것인가?
```

이 구분은 과장을 피하고, 실제로 이해하고 조정한 범위를 정확히 설명하기 위해 필요하다.

---

## 1. 큰 구분

| 영역 | 직접 작성/설정한 부분 | 외부 패키지가 제공한 부분 |
|---|---|---|
| ROS2 기본 | 예제 node 작성, topic/service/action 사용 | rclpy, rclcpp, ros2cli 통신 기반 |
| Custom Interface | `.msg`, `.srv`, `.action` 정의 | rosidl code generation |
| Camera/OpenCV | image publish/subscribe, 변환, YOLO 결과 처리 | OpenCV, cv_bridge, sensor_msgs |
| YOLO | model 실행 결과를 ROS2 메시지로 연결 | Ultralytics YOLO 추론 엔진 |
| TF | broadcaster/listener 예제, frame 이름 설정 | tf2_ros transform 관리 |
| URDF/Xacro | robot link/joint/sensor 모델 작성/수정 | robot_state_publisher가 TF 발행 |
| Gazebo | plugin 설정, world/launch 구성 | Gazebo physics, gazebo_ros plugin |
| SLAM | slam_toolbox 실행/설정/입력 topic 연결 | SLAM Toolbox mapping 알고리즘 |
| Map Server | map 저장/로드 명령 사용 | nav2_map_server lifecycle/map publish |
| AMCL | parameter 설정, initialpose, 결과 해석 | nav2_amcl particle filter localization |
| Nav2 | launch/parameter/goal/action 확인 | Nav2 stack planner/controller/BT/costmap |

---

## 2. 작성과 설정의 차이

### 작성한 것

```text
Python/C++/XML/YAML 파일을 만들어 특정 동작을 정의한 것
```

예:

```text
- ROS2 publisher/subscriber 예제 node
- service/action server/client 예제
- custom msg/srv/action interface
- URDF/Xacro 일부
- launch 파일
- parameter YAML
```

### 설정한 것

```text
이미 존재하는 외부 패키지의 동작을 parameter, launch, topic remap으로 조정한 것
```

예:

```text
- slam_toolbox parameter 설정
- AMCL parameter 설정
- Nav2 planner/controller/costmap parameter 설정
- Gazebo plugin topic/frame 설정
```

### 외부 패키지가 제공한 것

```text
알고리즘과 시스템 내부 구현은 외부 패키지가 담당한 것
```

예:

```text
- SLAM Toolbox의 scan matching/pose graph
- AMCL의 particle filter implementation
- Nav2의 behavior tree execution
- DWB controller의 trajectory scoring
- Gazebo의 physics/sensor simulation
```

---

## 3. 정확한 표현 예시

좋은 표현:

```text
SLAM 알고리즘을 직접 구현한 것은 아니고,
SLAM Toolbox를 사용해 Gazebo LiDAR/TF 데이터를 기반으로 지도를 생성하는 흐름을 실습했다.
```

```text
AMCL을 직접 구현한 것은 아니고,
Particle Filter 개념을 노트북으로 학습한 뒤 Nav2 AMCL의 input/output과 parameter를 분석했다.
```

```text
Nav2 controller를 직접 구현한 것은 아니고,
Nav2 stack의 planner/controller/costmap/lifecycle 구조와 NavigateToPose action이 /cmd_vel로 이어지는 흐름을 실습했다.
```

피해야 할 표현:

```text
SLAM 구현 완료
AMCL 구현 완료
자율주행 시스템 구현 완료
```

이 표현은 현재 학습 정리 범위를 넘어선다.

---

## 4. 이 저장소의 초점

```text
- 외부 패키지가 무엇을 해주는지 이해한다.
- 어떤 topic/frame/parameter를 맞춰야 하는지 이해한다.
- 실행 결과를 어떻게 검증하는지 정리한다.
- 문제가 생겼을 때 어디부터 확인해야 하는지 정리한다.
```

---

## 5. 별도 프로젝트로 확장하기 좋은 부분

```text
- 커스텀 sensor processing node
- obstacle filtering node
- navigation 상태 모니터링 node
- object detection 결과를 costmap/behavior에 연결하는 bridge
- map/world 자동 검증 script
- rosbag 기반 regression test
- launch 통합/parameter profile 관리
```

이런 부분을 추가하면 학습 정리에서 독립 프로젝트로 자연스럽게 확장할 수 있다.
