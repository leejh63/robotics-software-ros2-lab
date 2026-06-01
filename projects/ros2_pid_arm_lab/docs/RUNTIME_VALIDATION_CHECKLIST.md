# PID Arm Runtime Validation Checklist

이 문서는 `projects/ros2_pid_arm_lab`에서 실제 ROS2 Humble + Gazebo Classic 환경으로 확인해야 할 항목을 분리한 체크리스트입니다. 이 저장소의 정적 검사는 launch 문법과 파일 구조를 확인하지만, Gazebo controller loading과 effort 응답은 실제 런타임에서만 확정할 수 있습니다. Terminal별 실행 순서는 [`RUNTIME_SESSION_GUIDE.md`](RUNTIME_SESSION_GUIDE.md)를 따르고, 결과는 루트의 [`RUNTIME_VALIDATION_RESULT_TEMPLATE.md`](../../../RUNTIME_VALIDATION_RESULT_TEMPLATE.md)에 기록합니다.

## 1. Build

```bash
cd projects/ros2_pid_arm_lab
source /opt/ros/humble/setup.bash
rosdep install --from-paths src -y --ignore-src
colcon build --symlink-install
source install/setup.bash
```

통과 기준:

```text
colcon build가 실패하지 않는다.
pid_arm_lab package가 install space에서 조회된다.
```

## 2. Gazebo + controller loading

```bash
ros2 launch pid_arm_lab full.launch.py
```

다른 터미널에서 확인합니다.

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 control list_controllers
ros2 topic echo /joint_states --once
```

통과 기준:

```text
joint_state_broadcaster가 active 상태다.
effort_controller가 active 상태다.
/joint_states에 arm_joint position이 포함된다.
```

## 3. PID node parameter 확인

```bash
ros2 param get /pid_arm_controller kp
ros2 param get /pid_arm_controller ki
ros2 param get /pid_arm_controller kd
ros2 param get /pid_arm_controller setpoint
ros2 param get /pid_arm_controller use_actual_dt
ros2 param get /pid_arm_controller reset_integral_on_setpoint_change
ros2 param get /pid_arm_controller gravity_gain
```

통과 기준:

```text
launch argument 또는 config yaml 값이 node parameter로 반영된다.
```

## 4. Effort command 확인

작은 gain부터 시작합니다.

```bash
ros2 param set /pid_arm_controller kp 10.0
ros2 param set /pid_arm_controller ki 0.0
ros2 param set /pid_arm_controller kd 0.5
ros2 param set /pid_arm_controller setpoint 0.5
ros2 topic echo /effort_controller/commands --once
```

통과 기준:

```text
/effort_controller/commands에 Float64MultiArray가 publish된다.
명령값이 max_effort 범위 안에 있다.
setpoint를 바꾸면 effort 방향이 바뀐다.
```

## 5. 종료 안전성

Ctrl+C로 종료한 뒤 확인합니다.

```bash
ros2 topic echo /effort_controller/commands --once
```

통과 기준:

```text
PID node 종료 시 zero effort publish를 시도한다.
동일 launch를 재실행했을 때 controller 이름 충돌 없이 다시 시작된다.
```

## 보류 항목

아래 항목은 실제 Gazebo 동작을 확인한 뒤에만 문서에 성공으로 적습니다.

```text
fixed-base arm spawn 안정성
large gain에서 진동/포화 여부
gravity_gain feed-forward 체감 효과
continuous joint angle wrap 필요 여부
```
