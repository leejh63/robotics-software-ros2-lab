# Runtime Workflow

이 문서는 `projects/ros2_navigation_lab`을 실행할 때 사용하는 기본 workflow를 정리합니다.

명령어는 workspace root에서 실행하는 것을 기준으로 합니다. ROS2 Humble 환경을 먼저 source해야 합니다.

기본 workflow는 `slam.world`와 `maps/slam_map.yaml`을 사용합니다. `lee_world.world`와 `maps/room_map.yaml`은 작은 방 환경 테스트용으로 유지합니다.

---

## 1. Build

```bash
source /opt/ros/humble/setup.bash
colcon build --symlink-install --packages-select lee_robot_description
source install/setup.bash
```

---

## 2. Gazebo

로봇을 Gazebo에 spawn합니다.

```bash
ros2 launch lee_robot_description gazebo.launch.py world:=slam.world use_avoidance:=false
```

sensor topic과 odometry topic을 확인합니다.

```bash
ros2 node list | sort
ros2 topic list | sort
ros2 topic echo /lee/scan --once
ros2 topic echo /lee/odom --once
ros2 run tf2_ros tf2_echo odom_lee base_footprint --ros-args -r /tf:=/lee/tf -r /tf_static:=/lee/tf_static
```

TF는 `/lee/tf`, `/lee/tf_static`으로 publish됩니다. 따라서 `tf2_echo`에는 remap을 붙여 확인합니다.

`use_avoidance:=false`가 기본입니다. `lidar_wall_follower.py`는 `/lee/cmd_vel`에 직접 publish하므로, Nav2나 teleop을 테스트할 때는 끄는 편이 안전합니다.

---

## 3. SLAM

Gazebo와 `slam_toolbox`를 함께 실행합니다.

```bash
ros2 launch lee_robot_description gazebo_slam.launch.py world:=slam.world
```

SLAM topic과 TF를 확인합니다.

```bash
ros2 topic echo /lee/scan --once
ros2 topic echo /lee/map --once --qos-durability transient_local
ros2 run tf2_ros tf2_echo map_lee odom_lee --ros-args -r /tf:=/lee/tf -r /tf_static:=/lee/tf_static
ros2 run tf2_ros tf2_echo odom_lee base_footprint --ros-args -r /tf:=/lee/tf -r /tf_static:=/lee/tf_static
```

---

## 4. Localization

Gazebo, map server, AMCL, lifecycle manager, RViz를 실행합니다.

```bash
ros2 launch lee_robot_description localization.launch.py world:=slam.world
```

AMCL 초기 위치를 지정합니다.

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

필요하면 로봇을 조금 움직여 AMCL update를 유도합니다.

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r /cmd_vel:=/lee/cmd_vel
```

Localization 상태를 확인합니다.

```bash
ros2 lifecycle get /map_server
ros2 lifecycle get /amcl
ros2 topic echo /amcl_pose --once
ros2 topic echo /particle_cloud --once
ros2 run tf2_ros tf2_echo map_lee odom_lee --ros-args -r /tf:=/lee/tf -r /tf_static:=/lee/tf_static
ros2 run tf2_ros tf2_echo odom_lee base_footprint --ros-args -r /tf:=/lee/tf -r /tf_static:=/lee/tf_static
```

현재 `localization.launch.py`에서 `map_server`와 `amcl` node는 root node namespace로 실행됩니다. 대신 map, scan, TF topic은 `/lee` workflow에 맞게 remap됩니다.

---

## 5. Nav2

### A. 통합 실행

Localization과 Nav2를 함께 실행합니다.

```bash
ros2 launch lee_robot_description nav2.launch.py use_rviz:=false
```

실행 후 initial pose를 먼저 지정하고, 그 다음 Nav2 goal을 보냅니다.

### B. 분리 실행

Localization을 이미 실행 중인 상태에서 Nav2 stack만 따로 실행합니다.

```bash
ros2 launch lee_robot_description nav2_navigation.launch.py
```

`nav2.launch.py`는 localization과 Nav2를 함께 실행합니다. 같은 세션에서 `nav2.launch.py`를 실행한 뒤 `nav2_navigation.launch.py`를 다시 실행하면 Nav2 node가 중복될 수 있습니다.

Nav2 node namespace를 확인합니다.

```bash
ros2 node list | sort | grep controller_server
ros2 node list | sort | grep planner_server
ros2 node list | sort | grep bt_navigator
```

정상적인 node 이름은 `/lee/controller_server`처럼 `/lee` 아래에 있어야 합니다. `/controller_server`는 namespace가 적용되지 않은 경우이고, `/lee/lee/controller_server`는 namespace가 중복 적용된 경우일 수 있습니다.

controller parameter를 확인합니다.

```bash
ros2 param get /lee/controller_server controller_plugins
ros2 param get /lee/controller_server goal_checker_plugins
ros2 param get /lee/controller_server progress_checker_plugin
```

CLI로 goal을 보냅니다.

```bash
ros2 action send_goal /lee/navigate_to_pose nav2_msgs/action/NavigateToPose "{pose: {header: {frame_id: map_lee}, pose: {position: {x: 0.5, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}}"
```

`/lee/cmd_vel` 출력을 확인합니다.

```bash
ros2 topic info /lee/cmd_vel -v
ros2 topic echo /lee/cmd_vel --once
```
