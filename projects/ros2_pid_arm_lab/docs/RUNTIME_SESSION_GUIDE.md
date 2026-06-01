# PID Arm Runtime Session Guide

이 문서는 `projects/ros2_pid_arm_lab`을 실제 ROS2 Humble + Gazebo Classic 환경에서 검증할 때 쓰는 터미널별 실행 순서입니다. `RUNTIME_VALIDATION_CHECKLIST.md`가 통과 기준이라면, 이 문서는 그 기준을 확인하기 위한 실행 세션 절차입니다.

정적 검증을 통과해도 아래 항목은 runtime에서만 확정합니다.

```text
Gazebo spawn 안정성
ros2_control controller loading
/joint_states publish 여부
effort_controller command 수신 여부
PID node parameter 반영 여부
setpoint/gain 변경에 따른 effort command 변화
종료 시 zero effort publish 시도 여부
```

결과를 README에 성공으로 적기 전에는 루트의 [`RUNTIME_VALIDATION_RESULT_TEMPLATE.md`](../../../RUNTIME_VALIDATION_RESULT_TEMPLATE.md)에 실제 명령, 날짜, 환경, 관찰 결과를 남깁니다.

---

## 0. 공통 준비

모든 터미널은 workspace root인 `projects/ros2_pid_arm_lab`에서 시작한다고 가정합니다.

```bash
cd projects/ros2_pid_arm_lab
source /opt/ros/humble/setup.bash
```

처음 한 번 build합니다.

```bash
rosdep install --from-paths src -y --ignore-src
colcon build --symlink-install
source install/setup.bash
ros2 pkg prefix pid_arm_lab
```

권장 로그 디렉토리입니다. 이 디렉토리는 runtime 산출물이므로 commit하지 않습니다.

```bash
mkdir -p runtime_logs/pid_arm_$(date +%Y%m%d_%H%M%S)
```

---

## 1. 기본 launch smoke test

### Terminal A: Gazebo + controller + PID node 실행

```bash
cd projects/ros2_pid_arm_lab
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch pid_arm_lab full.launch.py
```

### Terminal B: controller와 joint state 확인

```bash
cd projects/ros2_pid_arm_lab
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 control list_controllers
ros2 topic echo /joint_states --once
ros2 topic echo /effort_controller/commands --once
```

기록할 것:

```text
joint_state_broadcaster active 여부:
effort_controller active 여부:
/joint_states에 arm_joint가 있는지:
/effort_controller/commands publish 여부:
Gazebo console error:
```

---

## 2. Parameter 확인

```bash
cd projects/ros2_pid_arm_lab
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 param get /pid_arm_controller kp
ros2 param get /pid_arm_controller ki
ros2 param get /pid_arm_controller kd
ros2 param get /pid_arm_controller setpoint
ros2 param get /pid_arm_controller dt
ros2 param get /pid_arm_controller use_actual_dt
ros2 param get /pid_arm_controller reset_integral_on_setpoint_change
ros2 param get /pid_arm_controller max_effort
ros2 param get /pid_arm_controller gravity_gain
```

기록할 것:

```text
launch argument 값이 parameter로 반영되는지:
yaml 기본값과 다르게 보이는 값이 있는지:
```

---

## 3. 작은 gain으로 effort 변화 확인

기본 gain은 안전하게 0에서 시작합니다. 움직임을 확인할 때는 작은 값부터 적용합니다.

```bash
cd projects/ros2_pid_arm_lab
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 param set /pid_arm_controller kp 10.0
ros2 param set /pid_arm_controller ki 0.0
ros2 param set /pid_arm_controller kd 0.5
ros2 param set /pid_arm_controller setpoint 0.5
ros2 topic echo /effort_controller/commands --once
```

반대 방향 setpoint도 확인합니다.

```bash
ros2 param set /pid_arm_controller setpoint -0.5
ros2 topic echo /effort_controller/commands --once
```

기록할 것:

```text
setpoint 0.5에서 effort 방향/크기:
setpoint -0.5에서 effort 방향/크기:
max_effort 포화 여부:
관찰된 진동 여부:
```

---

## 4. launch argument 반영 확인

새 터미널에서 다음처럼 시작해 parameter가 바로 반영되는지 확인합니다.

```bash
cd projects/ros2_pid_arm_lab
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch pid_arm_lab full.launch.py \
  kp:=10.0 \
  ki:=0.0 \
  kd:=0.5 \
  setpoint:=0.5 \
  use_actual_dt:=false \
  reset_integral_on_setpoint_change:=true
```

다른 터미널에서 확인합니다.

```bash
ros2 param get /pid_arm_controller kp
ros2 param get /pid_arm_controller kd
ros2 param get /pid_arm_controller setpoint
ros2 param get /pid_arm_controller use_actual_dt
ros2 param get /pid_arm_controller reset_integral_on_setpoint_change
```

기록할 것:

```text
launch argument 반영 여부:
use_actual_dt false 반영 여부:
reset_integral_on_setpoint_change true 반영 여부:
```

---

## 5. 종료 확인

`full.launch.py` 터미널에서 Ctrl+C로 종료합니다. 종료 직후 console에 exception이 반복되는지 확인합니다.

기록할 것:

```text
Ctrl+C 종료 시 traceback 여부:
zero effort publish 시도 log 여부:
동일 launch 재실행 가능 여부:
controller 이름 충돌 여부:
```

---

## 6. 보류 항목 판단 기준

아래 항목은 관찰값 없이 README에 성공으로 쓰지 않습니다.

```text
fixed-base arm spawn이 모든 환경에서 안정적이다.
gravity_gain이 실제 동역학 보상으로 충분하다.
large gain에서도 안정적이다.
continuous joint wrap이 필요 없다.
```

관찰 후에도 표현은 보수적으로 씁니다.

```text
적절한 표현:
- Gazebo Classic 환경에서 1-DOF effort controller와 custom PID node의 연결을 확인했다.
- 작은 gain/setpoint에서 effort command publish를 확인했다.

피해야 할 표현:
- 산업용 로봇 팔 제어기를 구현했다.
- 실제 하드웨어 제어 안정성을 검증했다.
- gravity compensation을 완성했다.
```
