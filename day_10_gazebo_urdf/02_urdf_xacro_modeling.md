# 02. URDF / Xacro 로봇 모델링 정리

## 1. URDF가 표현하는 것

URDF는 로봇의 구조를 XML로 표현하는 형식이다. ROS2에서 URDF는 로봇의 부품 관계와 좌표계 관계를 설명하는 데 사용된다.

URDF에서 가장 중요한 단어는 `link`와 `joint`다.

```text
link
  로봇의 부품 또는 좌표계 단위
  예: base_link, wheel_left_link, base_scan, camera_link

joint
  link와 link를 연결하는 관계
  예: base_link와 camera_link를 고정 연결
```

로봇 모델은 결국 link와 joint의 트리 구조다.

```text
base_footprint
  └── base_link
      ├── wheel_left_link
      ├── wheel_right_link
      ├── caster_back_link
      ├── imu_link
      ├── base_scan
      └── camera_link
```

---

## 2. link 안의 visual / collision / inertial

`link` 안에는 보통 세 종류의 정보가 들어간다.

| 요소 | 의미 | 어디에 중요함 |
|---|---|---|
| `visual` | 사람이 보는 외형 | RViz2, Gazebo 화면 |
| `collision` | 물리 엔진이 충돌 계산에 쓰는 형상 | Gazebo 충돌/접촉 계산 |
| `inertial` | 질량과 관성 | Gazebo 물리 계산 |

초보자 입장에서 중요한 구분은 이것이다.

```text
visual이 있어도 collision이 없으면 보기에는 있는데 물리적으로 이상할 수 있다.
inertial이 없거나 이상하면 Gazebo에서 로봇이 튀거나 움직임이 비정상일 수 있다.
```

즉 RViz2에서 잘 보이는 것과 Gazebo에서 잘 움직이는 것은 별개다.

---

## 3. joint type

Day 10의 `turtlebot.xacro`에서는 크게 두 종류의 joint가 중요하다.

| joint type | 의미 | 예시 |
|---|---|---|
| `fixed` | 두 link가 고정되어 상대적으로 움직이지 않음 | `base_joint`, `scan_joint`, `camera_joint`, `imu_joint` |
| `continuous` | 제한 없이 회전 가능한 joint | `wheel_left_joint`, `wheel_right_joint` |

바퀴는 Gazebo diff drive plugin이 실제로 회전시켜야 하므로 `continuous` joint로 표현된다.

---

## 4. Xacro가 필요한 이유

URDF를 순수 XML로 작성하면 반복이 많고 관리가 어렵다. Xacro는 URDF를 편하게 작성하기 위한 매크로 시스템이다.

Xacro에서 자주 쓰는 기능:

```text
property
  반복해서 쓰는 값을 변수처럼 관리

macro
  반복되는 link/joint 구조를 함수처럼 재사용

include
  파일을 나누어 구조와 Gazebo 설정을 분리
```

현재 실습에서는 `turtlebot.xacro` 마지막에 아래처럼 Gazebo 설정 파일이 포함된다.

```xml
<xacro:include filename="turtlebot_gaze.xacro"/>
```

따라서 실제 URDF 변환 결과는 아래 두 파일이 합쳐진 결과다.

```text
turtlebot.xacro
  + turtlebot_gaze.xacro
        ↓
URDF XML 문자열
```

---

## 5. 현재 `turtlebot.xacro`의 구조

`urdf/turtlebot.xacro`에서 핵심은 다음이다.

### 5.1 base

```text
base_footprint
  지면 기준 로봇 중심 좌표계 성격

base_link
  로봇 본체 좌표계
```

`base_footprint`와 `base_link`는 `base_joint`로 고정 연결된다.

### 5.2 wheel macro

왼쪽/오른쪽 바퀴는 같은 구조를 반복하므로 `xacro:macro`로 정의되어 있다.

```text
wheel_left_link  + wheel_left_joint
wheel_right_link + wheel_right_joint
```

Gazebo diff drive plugin은 이 joint 이름을 사용한다.

```xml
<left_joint>wheel_left_joint</left_joint>
<right_joint>wheel_right_joint</right_joint>
```

즉 URDF/Xacro의 joint 이름과 Gazebo plugin 설정이 반드시 맞아야 한다.

### 5.3 sensor links

```text
imu_link
  IMU plugin이 붙을 위치

base_scan
  LiDAR ray sensor plugin이 붙을 위치

camera_link
  camera plugin이 붙을 위치
```

여기서 주의할 점은 `base_scan`이나 `camera_link` 자체가 센서 데이터를 발행하는 것이 아니라는 점이다. 이 link는 “센서가 붙는 좌표계/위치”이고, 실제 ROS2 topic 발행은 Gazebo plugin이 한다.

---

## 6. URDF와 SDF의 관계

Gazebo는 원래 SDF 형식을 많이 사용한다. ROS에서는 URDF/Xacro로 로봇 모델을 작성하고, Gazebo가 이를 받아 내부적으로 시뮬레이션 가능한 모델로 사용한다.

구분하면 다음과 같다.

```text
URDF/Xacro
  ROS 쪽 로봇 구조 표현에 익숙한 형식
  robot_state_publisher, RViz2와 연결하기 좋음

SDF/world
  Gazebo world와 환경 모델 표현에 익숙한 형식
  벽, 바닥, 조명, 물리 설정, 장애물 배치 등에 사용
```

이번 실습에서는 다음처럼 나뉜다.

```text
로봇 자체       -> turtlebot.xacro, turtlebot_gaze.xacro
로봇이 있는 환경 -> lee_world.world, simple_maze.world, slam.world
```

---

## 7. 기억할 핵심

```text
URDF/Xacro는 로봇의 몸체와 좌표계 구조를 만든다.
robot_state_publisher는 이 구조를 TF로 바꿔 ROS2에 알린다.
Gazebo plugin은 이 구조에 물리 구동과 센서 데이터를 붙인다.
```
