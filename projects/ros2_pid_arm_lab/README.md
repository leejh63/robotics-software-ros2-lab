# ROS2 PID Arm Lab

This directory is an executable ROS2 workspace for a 1-DOF arm PID control practice.

It is separated from `day_14_control_and_path_planning/` so the study notes and executable source code stay independent.

```text
projects/ros2_pid_arm_lab/
└── src/
    └── pid_arm_lab/
```

## Scope

This lab focuses on:

- Gazebo Classic simulation
- `ros2_control` controller loading
- `joint_state_broadcaster`
- effort controller command publishing
- a simple custom PID node for one revolute joint

This is a practice package, not a production robot controller.

## Build

```bash
cd projects/ros2_pid_arm_lab
source /opt/ros/humble/setup.bash
rosdep install --from-paths src -y --ignore-src
colcon build --symlink-install
source install/setup.bash
```

## Run

```bash
ros2 launch pid_arm_lab full.launch.py
```

## Check

```bash
ros2 control list_controllers
ros2 topic echo /joint_states --once
ros2 topic echo /effort_controller/commands --once
```

## Tuning example

```bash
ros2 param set /pid_arm_controller kp 10.0
ros2 param set /pid_arm_controller ki 0.0
ros2 param set /pid_arm_controller kd 0.5
ros2 param set /pid_arm_controller setpoint 0.5
```

## Related notes

- Day 14 PID notes: [`../../day_14_control_and_path_planning/pid_control/`](../../day_14_control_and_path_planning/pid_control/)
- Runtime validation checklist: [`docs/RUNTIME_VALIDATION.md`](docs/RUNTIME_VALIDATION.md)
