# ROS2 PID Arm Lab Runtime Validation

This document is a checklist for validating `projects/ros2_pid_arm_lab` in a ROS2 Humble + Gazebo Classic environment.

## Status

```text
Build: TODO
Gazebo: TODO
ros2_control controllers: TODO
PID node: TODO
Joint motion: TODO
```

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

## Required checks

```bash
ros2 control list_controllers
ros2 topic echo /joint_states --once
ros2 topic echo /effort_controller/commands --once
ros2 node list | grep pid_arm_controller
```

Expected checks:

```text
joint_state_broadcaster: active
effort_controller: active
/joint_states is publishing
/effort_controller/commands is publishing
/pid_arm_controller is running
```

## PID parameter check

```bash
ros2 param get /pid_arm_controller kp
ros2 param get /pid_arm_controller ki
ros2 param get /pid_arm_controller kd
ros2 param get /pid_arm_controller setpoint
```

## Runtime tuning example

```bash
ros2 param set /pid_arm_controller kp 10.0
ros2 param set /pid_arm_controller kd 0.5
ros2 param set /pid_arm_controller setpoint 0.5
```

## Notes

Do not mark this lab as fully verified until Gazebo, controller loading, PID node execution, and joint motion are all observed in the target environment.
