# Navigation Runtime Validation Checklist

이 문서는 `projects/ros2_navigation_lab`에서 실제 ROS2 Humble + Gazebo Classic + Nav2 환경으로 확인해야 할 항목을 분리한 체크리스트입니다. 정적 검사는 launch/config/문서 구조를 확인하지만, lifecycle active, TF 연결, costmap 갱신, goal 처리 여부는 실제 런타임에서만 확정할 수 있습니다. Terminal별 실행 순서는 [`RUNTIME_SESSION_GUIDE.md`](RUNTIME_SESSION_GUIDE.md)를 따르고, 결과는 루트의 [`RUNTIME_VALIDATION_RESULT_TEMPLATE.md`](../../../RUNTIME_VALIDATION_RESULT_TEMPLATE.md)에 기록합니다.

## 1. Build

```bash
cd projects/ros2_navigation_lab
source /opt/ros/humble/setup.bash
rosdep install --from-paths src -y --ignore-src
colcon build --symlink-install
source install/setup.bash
```

통과 기준:

```text
colcon build가 실패하지 않는다.
lee_robot_description package가 install space에서 조회된다.
```

## 2. Gazebo sensor / TF

```bash
ros2 launch lee_robot_description gazebo.launch.py world:=slam.world use_avoidance:=false
```

다른 터미널에서 확인합니다.

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 topic echo /lee/scan --once
ros2 topic echo /lee/odom --once
ros2 run tf2_ros tf2_echo odom_lee base_footprint --ros-args -r /tf:=/lee/tf -r /tf_static:=/lee/tf_static
```

통과 기준:

```text
/lee/scan이 LaserScan을 publish한다.
/lee/odom이 Odometry를 publish한다.
odom_lee -> base_footprint TF가 조회된다.
```

## 3. SLAM

```bash
ros2 launch lee_robot_description gazebo_slam.launch.py world:=slam.world
```

확인 명령:

```bash
ros2 topic echo /lee/map --once --qos-durability transient_local
ros2 run tf2_ros tf2_echo map_lee odom_lee --ros-args -r /tf:=/lee/tf -r /tf_static:=/lee/tf_static
```

통과 기준:

```text
/lee/map이 OccupancyGrid를 publish한다.
map_lee -> odom_lee TF가 조회된다.
```

## 4. Localization / AMCL

```bash
ros2 launch lee_robot_description localization.launch.py world:=slam.world
```

초기 위치를 RViz `2D Pose Estimate`로 지정하거나 `docs/RUNTIME_WORKFLOW.md`의 CLI 예시를 사용합니다.

확인 명령:

```bash
ros2 lifecycle get /map_server
ros2 lifecycle get /amcl
ros2 topic echo /amcl_pose --once
ros2 topic echo /particle_cloud --once
ros2 run tf2_ros tf2_echo map_lee odom_lee --ros-args -r /tf:=/lee/tf -r /tf_static:=/lee/tf_static
```

통과 기준:

```text
map_server와 amcl이 active 상태다.
/amcl_pose와 /particle_cloud가 publish된다.
map_lee -> odom_lee TF가 안정적으로 조회된다.
```

## 5. Nav2 node namespace / lifecycle

```bash
ros2 launch lee_robot_description nav2.launch.py use_rviz:=false
```

확인 명령:

```bash
ros2 node list | sort | grep controller_server
ros2 node list | sort | grep planner_server
ros2 node list | sort | grep bt_navigator
ros2 lifecycle get /lee/controller_server
ros2 lifecycle get /lee/planner_server
ros2 lifecycle get /lee/bt_navigator
```

통과 기준:

```text
Nav2 node가 /lee/controller_server처럼 /lee namespace 아래에 뜬다.
/lee/lee/controller_server처럼 namespace가 중복되지 않는다.
/controller_server처럼 root namespace에 뜨지 않는다.
controller/planner/bt_navigator lifecycle이 active 상태다.
```

## 6. Costmap / goal command

```bash
ros2 topic echo /lee/global_costmap/costmap --once --qos-durability transient_local
ros2 topic echo /lee/local_costmap/costmap --once --qos-durability transient_local
ros2 action list | grep navigate_to_pose
ros2 action send_goal /lee/navigate_to_pose nav2_msgs/action/NavigateToPose "{pose: {header: {frame_id: 'map_lee'}, pose: {position: {x: 0.5, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}}"
ros2 topic echo /lee/cmd_vel --once
```

통과 기준:

```text
global/local costmap이 publish된다.
/lee/navigate_to_pose action server가 보인다.
goal 전송 후 /lee/cmd_vel이 publish된다.
```

## 7. Rosbag workflow 별도 기준

rosbag workflow는 closed-loop 주행 검증이 아니라 replay 기반 map/localization/costmap 확인입니다. rosbag replay는 과거 sensor/odom/TF를 다시 공급하므로 Nav2가 새 `/lee/cmd_vel`을 내도 rosbag 내부 로봇 위치는 바뀌지 않습니다.

확인 명령은 `docs/BAG_SLAM_NAV2_WORKFLOW.md`와 `docs/BAG_COMMANDS_ONLY.md`를 따릅니다.

통과 기준:

```text
bag_slam_map.yaml과 bag_slam_map.pgm을 직접 생성한다.
bag workflow에서는 local costmap frame이 odom_lee가 아니라 rosbag 내부 frame인 odom 기준임을 유지한다.
closed-loop goal 도착 성공으로 표현하지 않는다.
```
