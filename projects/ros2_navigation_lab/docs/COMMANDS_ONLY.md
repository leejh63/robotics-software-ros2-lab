```bash
source /opt/ros/humble/setup.bash
colcon build --symlink-install --packages-select lee_robot_description
source install/setup.bash
```

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch lee_robot_description gazebo.launch.py world:=slam.world use_avoidance:=false
```

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 node list | sort
ros2 topic list | sort
ros2 topic echo /lee/scan --once
ros2 topic echo /lee/odom --once
ros2 run tf2_ros tf2_echo odom_lee base_footprint --ros-args -r /tf:=/lee/tf -r /tf_static:=/lee/tf_static
```

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch lee_robot_description gazebo_slam.launch.py world:=slam.world
```

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 topic echo /lee/scan --once
ros2 topic echo /lee/map --once --qos-durability transient_local
ros2 run tf2_ros tf2_echo map_lee odom_lee --ros-args -r /tf:=/lee/tf -r /tf_static:=/lee/tf_static
ros2 run tf2_ros tf2_echo odom_lee base_footprint --ros-args -r /tf:=/lee/tf -r /tf_static:=/lee/tf_static
```

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch lee_robot_description localization.launch.py world:=slam.world
```

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
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

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r /cmd_vel:=/lee/cmd_vel
```

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 lifecycle get /map_server
ros2 lifecycle get /amcl
ros2 topic echo /amcl_pose --once
ros2 topic echo /particle_cloud --once
ros2 run tf2_ros tf2_echo map_lee odom_lee --ros-args -r /tf:=/lee/tf -r /tf_static:=/lee/tf_static
ros2 run tf2_ros tf2_echo odom_lee base_footprint --ros-args -r /tf:=/lee/tf -r /tf_static:=/lee/tf_static
```

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch lee_robot_description nav2.launch.py use_rviz:=false
```

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
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

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch lee_robot_description nav2_navigation.launch.py
```

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 node list | sort | grep controller_server
ros2 node list | sort | grep planner_server
ros2 node list | sort | grep bt_navigator
ros2 param get /lee/controller_server controller_plugins
ros2 param get /lee/controller_server goal_checker_plugins
ros2 param get /lee/controller_server progress_checker_plugin
ros2 topic info /lee/cmd_vel -v
ros2 action send_goal /lee/navigate_to_pose nav2_msgs/action/NavigateToPose "{pose: {header: {frame_id: map_lee}, pose: {position: {x: 0.5, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}}"
ros2 topic echo /lee/cmd_vel --once
```
