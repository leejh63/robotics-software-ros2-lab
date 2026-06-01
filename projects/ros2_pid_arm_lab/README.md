# ROS2 PID Arm Lab

Gazebo Classic과 `ros2_control`을 사용해 1-DOF arm의 PID effort 제어 흐름을 실행해보는 ROS2 workspace입니다.

`day_14_control_and_path_planning/`은 개념 정리 문서이고, 이 폴더는 해당 내용을 실행 가능한 파일 구조로 분리한 공간입니다.

```text
projects/ros2_pid_arm_lab/
└── src/
    └── pid_arm_lab/
```

---

## 범위

이 실습은 아래 흐름을 다룹니다.

- Gazebo Classic simulation
- `ros2_control` controller loading
- `joint_state_broadcaster`
- effort controller command publishing
- one revolute joint를 대상으로 한 custom PID node

생산 환경용 로봇 제어기가 아니라, Gazebo에서 PID 제어 구조를 이해하기 위한 실습 패키지입니다.

---

## Build

```bash
cd projects/ros2_pid_arm_lab
source /opt/ros/humble/setup.bash
rosdep install --from-paths src -y --ignore-src
colcon build --symlink-install
source install/setup.bash
```

---

## Run

기본 실행:

```bash
ros2 launch pid_arm_lab full.launch.py
```

`full.launch.py`는 Gazebo에서 1-DOF arm을 spawn하고, `gazebo_ros2_control`을 통해 `joint_state_broadcaster`, `effort_controller`, PID controller node를 함께 실행합니다.

기본 PID gain은 안전하게 `0.0`으로 시작합니다. 팔의 응답을 바로 확인하려면 launch argument로 gain과 setpoint를 지정합니다.

```bash
ros2 launch pid_arm_lab full.launch.py \
  kp:=10.0 \
  ki:=0.0 \
  kd:=0.5 \
  setpoint:=0.5
```

값을 크게 올리면 Gazebo 상에서 진동하거나 effort가 포화될 수 있으므로, `kp`, `kd`, `setpoint`를 작은 값부터 조정합니다.

---

## Check

```bash
ros2 control list_controllers
ros2 topic echo /joint_states --once
ros2 topic echo /effort_controller/commands --once
```

---

## PID parameter tuning example

```bash
ros2 param set /pid_arm_controller kp 10.0
ros2 param set /pid_arm_controller ki 0.0
ros2 param set /pid_arm_controller kd 0.5
ros2 param set /pid_arm_controller setpoint 0.5
```


## Parameter notes

`gravity_gain`은 실제 로봇 동역학 모델을 완전히 보상하는 항이 아니라, 이 실습 arm에서 중력 방향 effort bias를 관찰하기 위한 feed-forward 실습 항입니다. 기본값은 `0.0`이며, 값을 키울 때는 작은 값부터 조정합니다.

`use_actual_dt`가 `true`이면 timer 주기 대신 실제 callback 간격을 사용해 derivative/integral 계산을 합니다. 재현성을 우선할 때는 launch argument로 `use_actual_dt:=false`를 넘겨 고정 `dt`를 사용할 수 있습니다.

`reset_integral_on_setpoint_change`는 목표각을 바꿀 때 누적 오차를 초기화해 이전 목표의 integral 영향이 다음 목표에 남지 않게 합니다.

---

## 관련 문서

- Runtime validation checklist: [`docs/RUNTIME_VALIDATION_CHECKLIST.md`](docs/RUNTIME_VALIDATION_CHECKLIST.md)
- Runtime session guide: [`docs/RUNTIME_SESSION_GUIDE.md`](docs/RUNTIME_SESSION_GUIDE.md)
- Day 14 PID notes: [`../../day_14_control_and_path_planning/pid_control/`](../../day_14_control_and_path_planning/pid_control/)
