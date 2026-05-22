# Nav2 Local Cheatsheet

현재 내 환경 기준 Nav2 실행/검증 명령어 모음이다.

명령어를 복사하기 전에 `lee_robot_description`은 package name이고, `robot_ns`는 namespace 예시라는 점을 구분한다. 자세한 기준은 `appendix/command_execution_conventions.md`를 참고한다.

---

## 1. 공통 준비

```bash
cd $ROS2_WS
source /opt/ros/humble/setup.bash
source install/setup.bash
```

---

## 2. Gazebo + Map + AMCL 실행

```bash
ros2 launch lee_robot_description nav2.launch.py
```

명시적으로 world/map 지정:

```bash
ros2 launch lee_robot_description nav2.launch.py \
  world:=slam.world \
  map_yaml:=$ROS2_WS/slam_map.yaml
```

다른 world/map 조합:

```bash
ros2 launch lee_robot_description nav2.launch.py \
  world:=lee_world.world \
  map_yaml:=$ROS2_WS/room_map.yaml
```

---

## 3. 초기 상태 확인

먼저 실제 topic 이름을 확인한다.

```bash
ros2 topic list | sort | grep -E 'map|scan|odom|amcl|particle|initialpose'
```

기본 확인:

```bash
ros2 topic echo /robot_ns/map --once
ros2 topic hz /robot_ns/scan
ros2 topic echo /robot_ns/odom --once
```

AMCL 출력 topic은 launch namespace 설정에 따라 `/amcl_pose` 또는 `/robot_ns/amcl_pose`처럼 달라질 수 있다.

```bash
ros2 topic echo /amcl_pose --once
ros2 topic echo /particle_cloud --once
# namespace가 붙어 있다면:
ros2 topic echo /robot_ns/amcl_pose --once
ros2 topic echo /robot_ns/particle_cloud --once
```

TF:

```bash
ros2 run tf2_ros tf2_echo map_robot_ns odom_robot_ns
ros2 run tf2_ros tf2_echo odom_robot_ns base_footprint
ros2 run tf2_ros tf2_echo base_footprint base_scan
```

RViz에서 `2D Pose Estimate`를 찍는다.

---

## 4. Navigation 서버 실행

터미널 2:

```bash
cd $ROS2_WS
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 launch lee_robot_description nav2_navigation.launch.py
```

---

## 5. Lifecycle 확인

```bash
ros2 lifecycle get /robot_ns/planner_server
ros2 lifecycle get /robot_ns/controller_server
ros2 lifecycle get /robot_ns/bt_navigator
ros2 lifecycle get /robot_ns/behavior_server
ros2 lifecycle get /robot_ns/smoother_server
ros2 lifecycle get /robot_ns/waypoint_follower
ros2 lifecycle get /robot_ns/velocity_smoother
```

정상:

```text
active [3]
```

---

## 6. Action 확인

```bash
ros2 action list | grep navigate
ros2 action info /robot_ns/navigate_to_pose
```

정상 후보:

```text
/robot_ns/navigate_to_pose
/robot_ns/navigate_through_poses
```

---

## 7. 목표 전송

기본 goal:

```bash
ros2 action send_goal /robot_ns/navigate_to_pose nav2_msgs/action/NavigateToPose \
"{pose: {header: {frame_id: 'map_robot_ns'}, pose: {position: {x: 0.0, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}}"
```

좌표 지정 goal:

```bash
ros2 action send_goal /robot_ns/navigate_to_pose nav2_msgs/action/NavigateToPose \
"{pose: {header: {frame_id: 'map_robot_ns'}, pose: {position: {x: 1.2, y: -0.8, z: 0.0}, orientation: {w: 1.0}}}}"
```

---

## 8. RViz 클릭 좌표 확인

```bash
ros2 topic echo /clicked_point
```

RViz에서 `Publish Point`로 지도 위 자유 공간을 찍고 `point.x`, `point.y`를 goal에 넣는다.

---

## 9. 주행 중 확인

```bash
ros2 topic echo /robot_ns/plan --once
ros2 topic echo /robot_ns/cmd_vel
ros2 topic echo /robot_ns/global_costmap/costmap --once
ros2 topic echo /robot_ns/local_costmap/costmap --once
```

---

## 10. teleop 충돌 확인

```bash
ros2 topic info /robot_ns/cmd_vel -v
```

자율주행 중에는 teleop, wall follower, 직접 만든 `/robot_ns/cmd_vel` publisher를 꺼둔다.

---

## 11. Parameter 빠른 확인

```bash
ros2 param get /robot_ns/planner_server planner_plugins
ros2 param get /robot_ns/controller_server controller_plugins
ros2 param get /robot_ns/controller_server FollowPath.critics
ros2 param get /robot_ns/controller_server odom_topic
ros2 param get /robot_ns/bt_navigator global_frame
ros2 param get /robot_ns/bt_navigator robot_base_frame
```

Costmap frame:

```bash
ros2 param get /robot_ns/global_costmap/global_costmap global_frame
ros2 param get /robot_ns/local_costmap/local_costmap global_frame
```

환경에 따라 costmap node 이름이 다르게 보이면 먼저 확인한다.

```bash
ros2 node list | grep costmap
```

