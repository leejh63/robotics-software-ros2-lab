# Architecture

This repository connects standard ROS2 navigation packages into one simulation workflow. The package is configured around the `/lee` namespace and these frames:

```text
map_lee -> odom_lee -> base_footprint
```

## Runtime Data Flow

```text
Gazebo
  -> publishes /lee/scan from the LiDAR plugin
  -> publishes /lee/odom from the differential drive plugin
  -> consumes /lee/cmd_vel for velocity commands

robot_state_publisher
  -> reads robot_description from the xacro-generated URDF
  -> publishes robot link transforms on /lee/tf and /lee/tf_static

slam_toolbox
  -> consumes /lee/scan and TF
  -> publishes /lee/map and map-related updates during mapping
  -> provides the map_lee -> odom_lee correction during SLAM

nav2_map_server
  -> loads a saved map yaml/pgm pair
  -> publishes the map on /lee/map

nav2_amcl
  -> consumes /lee/scan, /lee/map, and TF
  -> publishes /amcl_pose and /particle_cloud
  -> provides the map_lee -> odom_lee correction during localization

Nav2
  -> consumes the map, costmaps, TF, odometry, and goals
  -> plans and controls navigation behavior
  -> publishes velocity commands to /lee/cmd_vel
```

## Launch File Roles

| Launch file | Role |
| --- | --- |
| `display.launch.py` | URDF/Xacro visualization only |
| `gazebo.launch.py` | Gazebo simulation, robot spawn, optional RViz, optional wall follower |
| `slam.launch.py` | Gazebo plus `slam_toolbox` mapping flow |
| `gazebo_slam.launch.py` | Public SLAM entrypoint that includes `slam.launch.py` |
| `localization.launch.py` | Gazebo plus map server, AMCL, lifecycle manager, and RViz |
| `nav2_navigation.launch.py` | Nav2 navigation stack only, intended after localization is running |
| `nav2.launch.py` | Full localization plus Nav2 stack |

## Namespace Boundary

`/lee` is the robot topic and node namespace used by the simulation and Nav2 workflow. It is not a fully parameterized multi-robot namespace template.

The following values are currently hardcoded or coupled across launch, URDF, RViz, and parameter files:

```text
/lee
map_lee
odom_lee
base_footprint
/lee/scan
/lee/odom
/lee/cmd_vel
```

Changing only `namespace:=...` is not enough to make the package generic. URDF plugin namespaces, Nav2 parameters, RViz displays, remappings, and TF assumptions must be updated together.
