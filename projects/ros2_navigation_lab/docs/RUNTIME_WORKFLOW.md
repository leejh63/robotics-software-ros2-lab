# Runtime Workflow

> This document assumes that `clean_ws` has been promoted to the repository root.
> For the current cleanup workspace, use the root-level runtime validation documents first.

Run commands from the repository root after sourcing ROS2 Humble.

The default workflow uses `slam.world` with `maps/slam_map.yaml`.
`lee_world.world` and `maps/room_map.yaml` are kept as an optional smaller room test pair.

## Build

```bash
source /opt/ros/humble/setup.bash
colcon build --symlink-install --packages-select lee_robot_description
source install/setup.bash
```

## Gazebo

Start the robot in Gazebo:

```bash
ros2 launch lee_robot_description gazebo.launch.py world:=slam.world use_avoidance:=false
```

Verify the simulated sensor and odometry topics:

```bash
ros2 node list | sort
ros2 topic list | sort
ros2 topic echo /lee/scan --once
ros2 topic echo /lee/odom --once
ros2 run tf2_ros tf2_echo odom_lee base_footprint --ros-args -r /tf:=/lee/tf -r /tf_static:=/lee/tf_static
```

TF is published on `/lee/tf` and `/lee/tf_static`, so `tf2_echo` must be remapped as shown.

`use_avoidance:=false` is the default because `lidar_wall_follower.py` publishes directly to `/lee/cmd_vel`. Enable it only when testing that example node.

## SLAM

Start Gazebo with `slam_toolbox`:

```bash
ros2 launch lee_robot_description gazebo_slam.launch.py world:=slam.world
```

Verify SLAM topics and TF:

```bash
ros2 topic echo /lee/scan --once
ros2 topic echo /lee/map --once --qos-durability transient_local
ros2 run tf2_ros tf2_echo map_lee odom_lee --ros-args -r /tf:=/lee/tf -r /tf_static:=/lee/tf_static
ros2 run tf2_ros tf2_echo odom_lee base_footprint --ros-args -r /tf:=/lee/tf -r /tf_static:=/lee/tf_static
```

## Localization

Start Gazebo, map server, AMCL, lifecycle manager, and optional RViz:

```bash
ros2 launch lee_robot_description localization.launch.py world:=slam.world
```

Publish an initial pose:

```bash
ros2 topic pub --once /initialpose geometry_msgs/msg/PoseWithCovarianceStamped "
header:
  frame_id: 'map_lee'
pose:
  pose:
    position:
      x: 0.0
      y: 0.0
      z: 0.0
    orientation:
      x: 0.0
      y: 0.0
      z: 0.0
      w: 1.0
  covariance:
  - 0.25
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.25
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0685
"
```

Move the robot slightly so AMCL can update:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r /cmd_vel:=/lee/cmd_vel
```

Verify localization:

```bash
ros2 lifecycle get /map_server
ros2 lifecycle get /amcl
ros2 topic echo /amcl_pose --once
ros2 topic echo /particle_cloud --once
ros2 run tf2_ros tf2_echo map_lee odom_lee --ros-args -r /tf:=/lee/tf -r /tf_static:=/lee/tf_static
ros2 run tf2_ros tf2_echo odom_lee base_footprint --ros-args -r /tf:=/lee/tf -r /tf_static:=/lee/tf_static
```

With the current `localization.launch.py`, `map_server` and `amcl` run at the root node namespace. Their input map, scan, and TF topics are remapped to the `/lee` workflow.

## Nav2

For the full workflow, start localization and Nav2 together:

```bash
ros2 launch lee_robot_description nav2.launch.py use_rviz:=false
```

After starting `nav2.launch.py`, publish the initial pose before sending a Nav2 goal. AMCL needs the initial pose to stabilize the `map_lee -> odom_lee` transform.

To start only the Nav2 navigation stack after localization is already running:

```bash
ros2 launch lee_robot_description nav2_navigation.launch.py
```

Verify Nav2 nodes:

```bash
ros2 node list | sort | grep controller_server
ros2 node list | sort | grep planner_server
ros2 node list | sort | grep bt_navigator
```

Expected names are under `/lee`, such as `/lee/controller_server`. `/controller_server` means namespace was not applied, and `/lee/lee/controller_server` means namespace was likely applied twice.

Check controller parameters:

```bash
ros2 param get /lee/controller_server controller_plugins
ros2 param get /lee/controller_server goal_checker_plugins
ros2 param get /lee/controller_server progress_checker_plugin
```

Send a headless test goal:

```bash
ros2 action send_goal /lee/navigate_to_pose nav2_msgs/action/NavigateToPose "{pose: {header: {frame_id: map_lee}, pose: {position: {x: 0.5, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}}"
```

Verify command output:

```bash
ros2 topic info /lee/cmd_vel -v
ros2 topic echo /lee/cmd_vel --once
```
