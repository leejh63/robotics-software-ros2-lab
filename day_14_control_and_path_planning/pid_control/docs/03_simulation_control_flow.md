# 02. 시뮬레이션 제어 흐름

## 전체 데이터 흐름

```text
Gazebo physics
   ↓
gazebo_ros2_control
   ↓
controller_manager
   ↓
joint_state_broadcaster
   ↓
/joint_states
   ↓
pid_arm_controller
   ↓
/effort_controller/commands
   ↓
effort_controller
   ↓
arm_joint torque
   ↓
Gazebo physics
```

이 흐름이 닫힌 루프입니다. PID 노드는 팔의 현재 각도를 읽고, 목표각과의 오차를 계산한 뒤, effort 명령을 다시 Gazebo로 보냅니다.

## URDF/Xacro 쪽 핵심

`one_dof_arm.xacro`에서 가장 중요한 부분은 `arm_joint`입니다.

```xml
<joint name="arm_joint" type="continuous">
  <parent link="base_link"/>
  <child link="arm_link"/>
  <axis xyz="0 1 0"/>
</joint>
```

그리고 `ros2_control`에서 이 조인트를 effort command interface로 등록합니다.

```xml
<joint name="arm_joint">
  <command_interface name="effort"/>
  <state_interface name="position"/>
  <state_interface name="velocity"/>
</joint>
```

즉 이 모델은 position controller가 아니라 effort controller로 움직입니다.

## controller 쪽 핵심

`ros2_controllers.yaml`의 핵심은 아래입니다.

```yaml
effort_controller:
  ros__parameters:
    joints:
      - arm_joint
    command_interfaces:
      - effort
    state_interfaces:
      - position
      - velocity
```

PID 노드는 `/effort_controller/commands`로 `Float64MultiArray`를 발행합니다.

```text
msg.data = [effort]
```

컨트롤러는 이 effort 값을 `arm_joint`에 토크로 넣습니다.

## PID 계산 흐름

```text
error = setpoint - current_position
P = kp * error
I = ki * integral(error)
D = kd * derivative(error)
G = gravity compensation
output = P + I + D + G
```

이 구현에서는 `max_effort`로 출력 포화 제한을 걸고, 포화가 발생하면 integral windup을 줄이기 위해 해당 step의 적분 증가분을 되돌립니다.

## 이 구조가 중요한 이유

여기서 PID 노드는 Gazebo를 직접 제어하지 않습니다. PID 노드는 단지 ROS 토픽으로 effort 명령을 발행합니다. 실제로 Gazebo physics에 토크를 넣는 쪽은 `effort_controller`와 `gazebo_ros2_control`입니다.

```text
PID 노드
  계산 담당

ros2_control controller
  명령을 실제 joint interface에 연결하는 역할

Gazebo
  물리 시뮬레이션 담당
```

이 분리를 이해해야 나중에 문제가 났을 때 어느 구간이 끊겼는지 확인할 수 있습니다.
