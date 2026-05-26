# 00. 개요

이 실습 코드는 ROS2 Humble과 Gazebo Classic에서 1자유도 팔을 PID effort 제어로 움직이는 실습 코드입니다.

## 핵심 목표

```text
1. Gazebo에 1자유도 arm 모델을 띄운다.
2. ros2_control effort controller로 arm_joint에 effort 명령을 넣는다.
3. Python PID 노드가 /joint_states를 읽는다.
4. PID 노드가 /effort_controller/commands로 토크 명령을 발행한다.
5. kp, ki, kd, setpoint를 바꾸며 응답을 확인한다.
```

## 전체 실행 흐름

```text
full.launch.py
├── sim.launch.py
│   ├── Gazebo Classic 실행
│   ├── robot_state_publisher 실행
│   ├── one_dof_arm.xacro 처리
│   ├── spawn_entity.py로 Gazebo에 모델 생성
│   ├── joint_state_broadcaster 로드
│   └── effort_controller 로드
└── pid.launch.py
    └── pid_arm_controller 실행
```

## 주요 토픽

```text
/joint_states
  joint_state_broadcaster가 발행한다.
  PID 노드는 여기서 arm_joint의 현재 position을 읽는다.

/effort_controller/commands
  PID 노드가 Float64MultiArray로 effort 명령을 발행한다.
  effort_controller가 이 값을 arm_joint에 적용한다.
```

## 현재 범위

```text
포함:
  - 1자유도 arm Gazebo 모델
  - ros2_control effort interface
  - Python PID 제어 노드
  - 런타임 PID 파라미터 변경
  - 실행/튜닝/트러블슈팅 문서

제외:
  - 실제 하드웨어 드라이버
  - SLAM / AMCL / Nav2
  - 복잡한 manipulator 제어
  - 산업용 제어 성능 검증
```
