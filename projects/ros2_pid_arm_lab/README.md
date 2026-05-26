# ROS2 PID Arm Lab

Gazebo Classic과 `ros2_control`을 사용해 1-DOF arm의 PID 제어 흐름을 확인하는 ROS2 workspace입니다.

`day_14_control_and_path_planning/`은 개념 정리 문서이고, 이 폴더는 해당 내용을 실행 가능한 파일 구조로 분리한 공간입니다.

```text
projects/ros2_pid_arm_lab/
└── src/
    └── pid_arm_lab/
```

---

## 범위

이 실습은 아래 흐름을 확인하는 데 초점을 둡니다.

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

```bash
ros2 launch pid_arm_lab full.launch.py
```

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

---

## 검증 상태

런타임 검증 결과는 아래 문서에 기록합니다.

- [`docs/RUNTIME_VALIDATION.md`](docs/RUNTIME_VALIDATION.md)

Gazebo 실행, controller loading, PID node 실행, joint motion을 모두 확인하기 전에는 검증 완료로 표시하지 않습니다.

---

## 관련 문서

- Day 14 PID notes: [`../../day_14_control_and_path_planning/pid_control/`](../../day_14_control_and_path_planning/pid_control/)
- Runtime validation checklist: [`docs/RUNTIME_VALIDATION.md`](docs/RUNTIME_VALIDATION.md)
