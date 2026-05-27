# Nav2 Topic / Action / TF 진단 명령어

Nav2 문제가 발생하면 이 문서의 순서대로 node, lifecycle, action, topic, TF를 확인한다.

먼저 실제 node/topic/action 이름에 namespace가 붙어 있는지 확인한다. 문서에서는 `/lee/...` 형태를 많이 쓰지만, 환경에 따라 `/amcl_pose`처럼 namespace가 없는 topic도 있을 수 있다.

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
/lee/planner_server
/lee/controller_server
/lee/bt_navigator
/lee/behavior_server
/lee/smoother_server
/lee/waypoint_follower
/lee/velocity_smoother
/lee/lifecycle_manager_navigation
```

---

## 2. Lifecycle 상태

```bash
ros2 lifecycle get /lee/planner_server
ros2 lifecycle get /lee/controller_server
ros2 lifecycle get /lee/bt_navigator
ros2 lifecycle get /lee/behavior_server
ros2 lifecycle get /lee/smoother_server
ros2 lifecycle get /lee/waypoint_follower
ros2 lifecycle get /lee/velocity_smoother
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

환경에 따라 `/lee/map_server`, `/lee/amcl`일 수도 있으므로 노드 목록을 먼저 확인한다.

---

## 3. Action 확인

```bash
ros2 action list | sort
ros2 action list | grep navigate
```

정상 후보:

```text
/lee/navigate_to_pose
/lee/navigate_through_poses
```

Action 정보:

```bash
ros2 action info /lee/navigate_to_pose
```

---

## 4. Topic 확인

주요 topic:

```bash
ros2 topic list | grep -E 'lee|map|scan|odom|cmd_vel|amcl|particle|initialpose'
```

지도:

```bash
ros2 topic echo /lee/map --once
ros2 topic info /lee/map -v
```

LiDAR:

```bash
ros2 topic hz /lee/scan
ros2 topic info /lee/scan -v
```

Odom:

```bash
ros2 topic echo /lee/odom --once
ros2 topic info /lee/odom -v
```

Costmap:

```bash
ros2 topic echo /lee/global_costmap/costmap --once
ros2 topic echo /lee/local_costmap/costmap --once
ros2 topic info /lee/global_costmap/costmap -v
ros2 topic info /lee/local_costmap/costmap -v
```

Path:

```bash
ros2 topic echo /lee/plan --once
ros2 topic info /lee/plan -v
```

속도 명령:

```bash
ros2 topic echo /lee/cmd_vel
ros2 topic info /lee/cmd_vel -v
```

---

## 5. TF 확인

```bash
ros2 run tf2_ros tf2_echo map_lee odom_lee --ros-args -r /tf:=/lee/tf -r /tf_static:=/lee/tf_static
ros2 run tf2_ros tf2_echo odom_lee base_footprint --ros-args -r /tf:=/lee/tf -r /tf_static:=/lee/tf_static
ros2 run tf2_ros tf2_echo base_footprint base_scan --ros-args -r /tf:=/lee/tf -r /tf_static:=/lee/tf_static
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
ros2 topic echo /lee/amcl_pose --once
ros2 topic echo /lee/particle_cloud --once
ros2 topic info /lee/initialpose -v
```

---

## 7. Parameter 확인

Planner:

```bash
ros2 param get /lee/planner_server planner_plugins
ros2 param get /lee/planner_server GridBased.plugin
```

Controller:

```bash
ros2 param get /lee/controller_server controller_plugins
ros2 param get /lee/controller_server FollowPath.plugin
ros2 param get /lee/controller_server FollowPath.critics
ros2 param get /lee/controller_server odom_topic
```

BT Navigator:

```bash
ros2 param get /lee/bt_navigator global_frame
ros2 param get /lee/bt_navigator robot_base_frame
ros2 param get /lee/bt_navigator odom_topic
```

Costmap node 이름 확인:

```bash
ros2 node list | grep costmap
```

---

## 8. Goal 전송 테스트

```bash
ros2 action send_goal /lee/navigate_to_pose nav2_msgs/action/NavigateToPose \
"{pose: {header: {frame_id: 'map_lee'}, pose: {position: {x: 1.0, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}}"
```

Goal 전송 직후:

```bash
ros2 topic echo /lee/plan --once
ros2 topic echo /lee/cmd_vel
```

