# Troubleshooting

## No `/lee/scan`

Check that Gazebo started with the robot spawned:

```bash
ros2 launch lee_robot_description gazebo.launch.py use_avoidance:=false
ros2 topic list | sort
```

If `/lee/scan` is missing, inspect `urdf/turtlebot_gaze.xacro` and the Gazebo sensor plugin namespace.

## No `odom_lee -> base_footprint` TF

Check the odometry topic and TF output:

```bash
ros2 topic echo /lee/odom --once
ros2 run tf2_ros tf2_echo odom_lee base_footprint --ros-args -r /tf:=/lee/tf -r /tf_static:=/lee/tf_static
```

This package publishes TF on `/lee/tf` and `/lee/tf_static`. Plain `tf2_echo` without remaps listens to `/tf` and can look broken even when TF is being published correctly.

If odometry exists but TF is missing, inspect the differential drive plugin frame settings in the URDF/Xacro files.

## AMCL Does Not Publish Pose

AMCL needs a map, scan data, TF, and an initial pose.

```bash
ros2 lifecycle get /map_server
ros2 lifecycle get /amcl
ros2 topic echo /lee/map --once --qos-durability transient_local
ros2 topic echo /lee/scan --once
ros2 topic echo /amcl_pose --once
ros2 topic echo /particle_cloud --once
```

Publish `/initialpose` in RViz or with the command in `docs/RUNTIME_WORKFLOW.md`, then move the robot slightly with teleop.

## Nav2 Nodes Are Not Under `/lee`

Check node names:

```bash
ros2 node list | sort | grep controller_server
ros2 node list | sort | grep planner_server
ros2 node list | sort | grep bt_navigator
```

Expected:

```text
/lee/controller_server
/lee/planner_server
/lee/bt_navigator
```

Problem cases:

```text
/controller_server
/lee/lee/controller_server
```

Do not change both `PushRosNamespace` and the `nav2_bringup` namespace argument at the same time without rechecking runtime node names.

## Nav2 Reports Missing DWB Critics

Verify the `FollowPath.critics` parameters:

```bash
ros2 param get /lee/controller_server controller_plugins
ros2 param get /lee/controller_server goal_checker_plugins
ros2 param get /lee/controller_server progress_checker_plugin
```

Also inspect:

```text
src/lee_robot_description/config/nav2_params.yaml
```

`FollowPath.critics` must be nested under the `FollowPath` controller plugin configuration.

## Robot Moves Without Nav2 Or Teleop

The optional wall follower publishes directly to `/lee/cmd_vel`. Keep it disabled during Nav2 and teleop tests:

```bash
ros2 launch lee_robot_description gazebo.launch.py use_avoidance:=false
```

Only enable it explicitly:

```bash
ros2 launch lee_robot_description gazebo.launch.py use_avoidance:=true
```
