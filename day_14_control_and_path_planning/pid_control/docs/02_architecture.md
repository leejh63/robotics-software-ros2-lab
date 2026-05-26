# 01. 구조

## 패키지 구조

```text
src/pid_arm_lab/
├── package.xml
├── setup.py
├── setup.cfg
├── resource/pid_arm_lab
├── pid_arm_lab/
│   ├── __init__.py
│   └── pid_arm_controller.py
├── launch/
│   ├── sim.launch.py
│   ├── pid.launch.py
│   └── full.launch.py
├── urdf/
│   └── one_dof_arm.xacro
├── config/
│   ├── ros2_controllers.yaml
│   └── pid_params.yaml
└── worlds/
    └── empty.world
```

## 주요 파일 역할

```text
one_dof_arm.xacro
  링크, 조인트, 관성, ros2_control interface를 정의한다.

ros2_controllers.yaml
  controller_manager, joint_state_broadcaster, effort_controller를 정의한다.

pid_arm_controller.py
  /joint_states를 구독하고 /effort_controller/commands로 effort를 발행한다.

sim.launch.py
  Gazebo, robot_state_publisher, spawn_entity.py, controller spawner를 실행한다.

pid.launch.py
  PID 노드만 실행한다.

full.launch.py
  시뮬레이션과 PID 노드를 한 번에 실행한다.
```

## 변경 가능한 값

아래 값은 launch argument 또는 ROS parameter로 변경할 수 있습니다.

```text
robot_name
entity_name
payload_mass
start_z
kp / ki / kd
setpoint
max_effort
gravity_gain
joint_name
joint_states_topic
command_topic
```

ROS2 패키지명 `pid_arm_lab`은 `ros2 launch`, `ros2 run`, ament resource index에서 사용되므로 기본값으로 유지하는 편이 안전합니다.
