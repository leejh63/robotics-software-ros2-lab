# Background - URDF / SDF / Xacro / Gazebo 최소 배경지식

## 1. URDF

URDF는 ROS 쪽에서 로봇 구조를 표현하기 위한 XML 형식이다.

```text
로봇은 어떤 link로 이루어졌는가?
각 link는 어떤 joint로 연결되는가?
각 link의 외형, 충돌 형상, 질량은 무엇인가?
```

RViz2의 RobotModel과 robot_state_publisher는 URDF를 중요하게 사용한다.

---

## 2. Xacro

Xacro는 URDF를 편하게 쓰기 위한 전처리/매크로 문법이다.

```text
반복 구조를 macro로 줄인다.
수치를 property로 관리한다.
파일을 include로 나눈다.
```

최종적으로는 Xacro도 URDF XML로 변환되어 사용된다.

---

## 3. SDF

SDF는 Gazebo에서 world와 simulation model을 표현하는 데 많이 쓰는 형식이다.

```text
world
physics
light
model
collision
visual
```

이번 실습에서 `.world` 파일은 SDF 형식을 사용한다.

---

## 4. Gazebo

Gazebo는 물리 시뮬레이터다.

```text
중력
충돌
마찰
센서 시뮬레이션
바퀴 구동
카메라/라이다/IMU 생성
```

ROS2와 연결하려면 `gazebo_ros` 계열 plugin이 필요하다.

---

## 5. 한 줄 구분

```text
URDF  = 로봇 구조 설명
Xacro = URDF를 편하게 작성하는 매크로
SDF   = Gazebo world/model 표현에 강한 형식
Gazebo = 물리/센서 시뮬레이터
RViz2 = ROS2 데이터 시각화 도구
```
