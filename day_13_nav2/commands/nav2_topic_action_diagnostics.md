# Nav2 Topic / Action / TF 진단 명령어

문제가 생겼을 때 이 문서 순서대로 확인한다.

먼저 실제 node/topic/action 이름에 namespace가 붙어 있는지 확인한다. 문서에서는 `/robot_ns/...` 형태를 많이 쓰지만, 환경에 따라 `/amcl_pose`처럼 namespace가 없는 topic도 있을 수 있다.

---

## 1. 노드 목록

```bash
ros2 node list | sort
```

Navigation 서버만 보기:

```bash
ros2 node list | grep -E "planner|controller|bt_navigator|behavior|smoother|waypoint|velocity|lifecycle"
```

정상 후보:

```text
/robot_ns/planner_server
/robot_ns/controller_server
/robot_ns/bt_navigator
/robot_ns/behavior_server
/robot_ns/smoother_server
/robot_ns/waypoint_follower
/robot_ns/velocity_smoother
/robot_ns/lifecycle_manager_navigation
```

---

## 2. Lifecycle 상태

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

Localization 쪽:

```bash
ros2 lifecycle get /map_server
ros2 lifecycle get /amcl
```

환경에 따라 `/robot_ns/map_server`, `/robot_ns/amcl`일 수도 있으므로 노드 목록을 먼저 확인한다.

---

## 3. Action 확인

```bash
ros2 action list | sort
ros2 action list | grep navigate
```

정상 후보:

```text
/robot_ns/navigate_to_pose
/robot_ns/navigate_through_poses
```

Action 정보:

```bash
ros2 action info /robot_ns/navigate_to_pose
```

---

## 4. Topic 확인

주요 topic:

```bash
ros2 topic list | grep -E 'robot_ns|map|scan|odom|cmd_vel|amcl|particle|initialpose'
```

지도:

```bash
ros2 topic echo /robot_ns/map --once
ros2 topic info /robot_ns/map -v
```

LiDAR:

```bash
ros2 topic hz /robot_ns/scan
ros2 topic info /robot_ns/scan -v
```

Odom:

```bash
ros2 topic echo /robot_ns/odom --once
ros2 topic info /robot_ns/odom -v
```

Costmap:

```bash
ros2 topic echo /robot_ns/global_costmap/costmap --once
ros2 topic echo /robot_ns/local_costmap/costmap --once
ros2 topic info /robot_ns/global_costmap/costmap -v
ros2 topic info /robot_ns/local_costmap/costmap -v
```

Path:

```bash
ros2 topic echo /robot_ns/plan --once
ros2 topic info /robot_ns/plan -v
```

속도 명령:

```bash
ros2 topic echo /robot_ns/cmd_vel
ros2 topic info /robot_ns/cmd_vel -v
```

---

## 5. TF 확인

```bash
ros2 run tf2_ros tf2_echo map_robot_ns odom_robot_ns
ros2 run tf2_ros tf2_echo odom_robot_ns base_footprint
ros2 run tf2_ros tf2_echo base_footprint base_scan
```

TF 전체 PDF 생성:

```bash
ros2 run tf2_tools view_frames
```

---

## 6. AMCL 확인

AMCL topic은 namespace 설정에 따라 이름이 달라질 수 있다. 먼저 후보를 찾는다.

```bash
ros2 topic list | grep -E 'amcl_pose|particle_cloud|initialpose'
```

namespace가 없는 경우:

```bash
ros2 topic echo /amcl_pose --once
ros2 topic echo /particle_cloud --once
ros2 topic info /initialpose -v
```

namespace가 붙은 경우:

```bash
ros2 topic echo /robot_ns/amcl_pose --once
ros2 topic echo /robot_ns/particle_cloud --once
ros2 topic info /robot_ns/initialpose -v
```

---

## 7. Parameter 확인

Planner:

```bash
ros2 param get /robot_ns/planner_server planner_plugins
ros2 param get /robot_ns/planner_server GridBased.plugin
```

Controller:

```bash
ros2 param get /robot_ns/controller_server controller_plugins
ros2 param get /robot_ns/controller_server FollowPath.plugin
ros2 param get /robot_ns/controller_server FollowPath.critics
ros2 param get /robot_ns/controller_server odom_topic
```

BT Navigator:

```bash
ros2 param get /robot_ns/bt_navigator global_frame
ros2 param get /robot_ns/bt_navigator robot_base_frame
ros2 param get /robot_ns/bt_navigator odom_topic
```

Costmap node 이름 확인:

```bash
ros2 node list | grep costmap
```

---

## 8. Goal 전송 테스트

```bash
ros2 action send_goal /robot_ns/navigate_to_pose nav2_msgs/action/NavigateToPose \
"{pose: {header: {frame_id: 'map_robot_ns'}, pose: {position: {x: 1.0, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}}"
```

Goal 전송 직후:

```bash
ros2 topic echo /robot_ns/plan --once
ros2 topic echo /robot_ns/cmd_vel
```

