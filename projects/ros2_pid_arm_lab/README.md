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

```bash
ros2 launch pid_arm_lab full.launch.py
```

`full.launch.py`는 Gazebo에서 1-DOF arm을 spawn하고, `gazebo_ros2_control`을 통해 `joint_state_broadcaster`, `effort_controller`, PID controller node를 함께 실행합니다.

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

## 관련 문서

- Day 14 PID notes: [`../../day_14_control_and_path_planning/pid_control/`](../../day_14_control_and_path_planning/pid_control/)
