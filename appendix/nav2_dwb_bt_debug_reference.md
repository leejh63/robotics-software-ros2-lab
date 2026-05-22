# Nav2 DWB / Behavior Tree Debug Reference

Nav2 goal 처리 중 어디서 막혔는지 빠르게 나누기 위한 참조 문서다.

## 전체 흐름

```text
/robot_ns/navigate_to_pose
  -> /robot_ns/bt_navigator
  -> /robot_ns/planner_server
  -> /robot_ns/plan
  -> /robot_ns/controller_server
  -> DWBLocalPlanner
  -> /robot_ns/cmd_vel
```

## path가 안 생길 때

```bash
ros2 lifecycle get /robot_ns/bt_navigator
ros2 lifecycle get /robot_ns/planner_server
ros2 topic echo /robot_ns/plan --once
ros2 run tf2_ros tf2_echo map_robot_ns base_footprint
```

## cmd_vel이 안 나올 때

```bash
ros2 lifecycle get /robot_ns/controller_server
ros2 param get /robot_ns/controller_server controller_plugins
ros2 param get /robot_ns/controller_server FollowPath.plugin
ros2 param get /robot_ns/controller_server FollowPath.critics
ros2 run tf2_ros tf2_echo odom_robot_ns base_footprint
ros2 topic echo /robot_ns/cmd_vel
```

## cmd_vel은 나오는데 로봇이 안 움직일 때

```bash
ros2 topic info /robot_ns/cmd_vel -v
ros2 topic echo /robot_ns/cmd_vel
ros2 topic list | grep cmd_vel
```
