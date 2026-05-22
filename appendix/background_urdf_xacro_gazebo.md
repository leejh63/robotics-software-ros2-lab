# 추가 배경지식 - URDF, XACRO, Gazebo, RViz2 관계

이 문서는 Day 10을 이해하기 위해 필요한 배경지식을 따로 정리한 것이다.

## 1. RViz2와 Gazebo는 다르다

초보자 입장에서 가장 먼저 구분해야 할 것은 RViz2와 Gazebo다.

| 도구 | 핵심 역할 |
|---|---|
| RViz2 | ROS2 topic, TF, sensor data를 시각화 |
| Gazebo | 물리 시뮬레이션, 센서 시뮬레이션, 로봇 움직임 계산 |

RViz2는 실제 물리 계산을 하지 않는다.  
RViz2에서 로봇이 보인다는 것은 topic/TF/robot_description이 맞다는 뜻이다.

Gazebo에서 로봇이 움직인다는 것은 물리 속성, collision, joint, plugin, cmd_vel 연결까지 맞다는 뜻이다.

## 2. URDF는 로봇 설명서다

URDF는 로봇의 link와 joint 구조를 설명한다.

```text
base_link
  ├── left_wheel
  ├── right_wheel
  ├── base_scan
  └── camera_link
```

이런 식으로 로봇이 어떤 부품으로 구성되어 있고, 각 부품이 어떻게 연결되는지를 표현한다.

## 3. XACRO는 URDF를 편하게 쓰기 위한 문법이다

URDF는 XML이라 반복이 많다.  
XACRO는 property, macro, include를 사용해 URDF를 더 관리하기 쉽게 만든다.

예:

```text
wheel_radius 값을 한 번 정의
왼쪽 바퀴와 오른쪽 바퀴에서 같은 값을 재사용
```

또는:

```text
turtlebot.xacro
  로봇 구조 정의

include turtlebot_gaze.xacro
  Gazebo plugin 정의
```

## 4. robot_state_publisher는 TF를 만든다

`robot_state_publisher`는 URDF 구조를 읽고 link 사이의 TF를 발행한다.

```text
URDF robot_description
+ joint_states
        ↓
robot_state_publisher
        ↓
/tf, /tf_static
```

움직이지 않는 고정 관계는 `/tf_static`, 움직이는 관계는 `/tf`로 나간다.

## 5. Gazebo plugin은 ROS2와 Gazebo를 연결한다

Gazebo 내부에서는 물리 엔진이 로봇을 움직이고 센서값을 계산한다.  
하지만 ROS2 노드가 그 값을 쓰려면 ROS2 topic으로 나와야 한다.

그 연결을 하는 것이 Gazebo ROS plugin이다.

```text
Gazebo 내부 센서값
        ↓
Gazebo ROS plugin
        ↓
ROS2 topic
```

예:

```text
Gazebo ray sensor
        ↓
libgazebo_ros_ray_sensor.so
        ↓
/robot_ns/scan
```

## 6. spawn_entity.py는 Gazebo에 로봇을 넣는다

`spawn_entity.py`는 topic에 올라온 URDF를 읽어서 Gazebo world 안에 entity로 생성한다.

```text
/robot_ns/robot_description
        ↓
spawn_entity.py
        ↓
Gazebo world 안의 turtlebot entity
```

따라서 `/robot_ns/robot_description`이 비어 있거나 remap이 맞지 않으면 spawn이 실패한다.

## 7. Day 10에서 제일 중요한 관점

Day 10은 파일 하나를 외우는 것이 아니라 관계를 이해하는 것이 중요하다.

```text
turtlebot.xacro
  로봇 구조 작성

robot_state_publisher
  구조를 TF로 발행

Gazebo world
  로봇이 놓일 시뮬레이션 환경

spawn_entity.py
  robot_description을 읽어 Gazebo에 로봇 생성

Gazebo plugin
  센서/구동 데이터를 ROS2 topic으로 연결

RViz2
  topic과 TF를 시각화
```
