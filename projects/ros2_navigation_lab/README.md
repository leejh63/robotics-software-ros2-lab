# ROS2 Navigation Lab

This repository documents a ROS2 Humble navigation practice workflow using Gazebo Classic, URDF/Xacro, `slam_toolbox`, `nav2_amcl`, `nav2_map_server`, and `nav2_bringup`.

The focus is package integration, configuration, runtime verification, and documentation. This project does not implement custom SLAM, AMCL, planner, or controller algorithms.

## Environment

- Ubuntu 22.04
- ROS2 Humble
- Gazebo Classic with `gazebo_ros`
- Nav2 Humble packages
- `slam_toolbox`
- RViz2

## Repository Structure

```text
.
├── README.md
├── docs/
│   ├── ARCHITECTURE.md
│   ├── COMMANDS_ONLY.md
│   ├── REFERENCES.md
│   ├── RUNTIME_WORKFLOW.md
│   └── TROUBLESHOOTING.md
└── src/
    └── lee_robot_description/
        ├── launch/
        ├── config/
        ├── maps/
        ├── rviz/
        ├── scripts/
        ├── urdf/
        └── worlds/
```

## Main Workflow

1. Start Gazebo with the TurtleBot-style robot model.
2. Use `slam_toolbox` to build or inspect a map from `/lee/scan` and TF.
3. Load a saved map with `nav2_map_server`.
4. Use `nav2_amcl` to localize the robot on the map.
5. Start the Nav2 navigation stack and send goals from RViz or the action CLI.

The default workflow uses `slam.world` with `maps/slam_map.yaml`.
`lee_world.world` and `maps/room_map.yaml` are kept as an optional smaller room test pair.

## Build

```bash
source /opt/ros/humble/setup.bash
colcon build --symlink-install --packages-select lee_robot_description
source install/setup.bash
```

## Run

Gazebo only:

```bash
ros2 launch lee_robot_description gazebo.launch.py world:=slam.world use_avoidance:=false
```

SLAM:

```bash
ros2 launch lee_robot_description gazebo_slam.launch.py world:=slam.world
```

Localization:

```bash
ros2 launch lee_robot_description localization.launch.py world:=slam.world
```

Full localization and Nav2:

```bash
ros2 launch lee_robot_description nav2.launch.py use_rviz:=false
```

After starting `nav2.launch.py`, publish the initial pose before sending a Nav2 goal. AMCL needs the initial pose to stabilize the `map_lee -> odom_lee` transform.

Navigation stack only, after localization is already running:

```bash
ros2 launch lee_robot_description nav2_navigation.launch.py
```

## Verification Commands

```bash
ros2 topic echo /lee/scan --once
ros2 topic echo /lee/odom --once
ros2 topic echo /lee/map --once --qos-durability transient_local
ros2 topic echo /amcl_pose --once
ros2 topic echo /particle_cloud --once
ros2 lifecycle get /map_server
ros2 lifecycle get /amcl
ros2 run tf2_ros tf2_echo map_lee odom_lee --ros-args -r /tf:=/lee/tf -r /tf_static:=/lee/tf_static
ros2 run tf2_ros tf2_echo odom_lee base_footprint --ros-args -r /tf:=/lee/tf -r /tf_static:=/lee/tf_static
ros2 action send_goal /lee/navigate_to_pose nav2_msgs/action/NavigateToPose "{pose: {header: {frame_id: map_lee}, pose: {position: {x: 0.5, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}}"
```

TF is published on `/lee/tf` and `/lee/tf_static`. `tf2_echo` reads `/tf` and `/tf_static` by default, so use the remaps shown above.

Nav2 namespace checks:

```bash
ros2 node list | sort | grep controller_server
ros2 node list | sort | grep planner_server
ros2 node list | sort | grep bt_navigator
```

Expected Nav2 node names are under `/lee`, for example `/lee/controller_server`.

## Launch Files

| Launch file | Starts Gazebo | Starts SLAM | Starts AMCL | Starts Nav2 | Main use |
| --- | --- | --- | --- | --- | --- |
| `display.launch.py` | No | No | No | No | URDF/RViz model check |
| `gazebo.launch.py` | Yes | No | No | No | Simulation only |
| `gazebo_slam.launch.py` | Yes | Yes | No | No | Mapping workflow |
| `localization.launch.py` | Yes | No | Yes | No | AMCL localization test |
| `nav2_navigation.launch.py` | No | No | No | Yes | Nav2 stack only after localization |
| `nav2.launch.py` | Yes | No | Yes | Yes | Full localization + navigation |

## Key Frames and Topics

| Item | Value |
| --- | --- |
| Robot namespace | `/lee` |
| Map frame | `map_lee` |
| Odometry frame | `odom_lee` |
| Base frame | `base_footprint` |
| LiDAR topic | `/lee/scan` |
| Odometry topic | `/lee/odom` |
| Velocity command topic | `/lee/cmd_vel` |
| Map topic | `/lee/map` |
| AMCL pose topic | `/amcl_pose` |
| AMCL particle cloud topic | `/particle_cloud` |

## What I Configured

- ROS2 package metadata, install rules, and launch entrypoints
- Gazebo robot spawning and ROS topic wiring
- URDF/Xacro model usage for simulation
- `slam_toolbox` mapping parameters for the custom frame names
- `nav2_map_server` and `nav2_amcl` localization flow
- Nav2 costmap, planner, controller, behavior, and navigator parameters
- RViz configurations and runtime verification commands

## Provided By ROS2/Nav2

- SLAM implementation: `slam_toolbox`
- Localization implementation: `nav2_amcl`
- Map server: `nav2_map_server`
- Navigation stack: `nav2_bringup` and Nav2 servers
- Visualization: RViz2
- Simulation integration: Gazebo Classic and `gazebo_ros`

## Limitations

This package is currently configured for a fixed `/lee` namespace. Changing `namespace:=...` is not fully supported yet because URDF plugins, Nav2 parameters, RViz config, and topic remappings are written for `/lee`.

This is a simulation practice repository. It does not include multi-robot support, physical robot deployment, custom SLAM algorithms, custom AMCL algorithms, or custom Nav2 planner/controller plugins.

## Documentation

- [Runtime workflow](docs/RUNTIME_WORKFLOW.md)
- [Copy-paste commands](docs/COMMANDS_ONLY.md)
- [Architecture overview](docs/ARCHITECTURE.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [References](docs/REFERENCES.md)
