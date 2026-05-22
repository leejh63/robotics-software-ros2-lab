# 04. Navigation failure diagnosis map

이 문서는 rosbag-frame, DWB, Behavior Tree 주제를 실제 디버깅 관점으로 연결한다.

```text
rosbag-frame 문제
DWB 문제
Behavior Tree 문제
```

Nav2/SLAM/AMCL이 실패할 때는 증상을 먼저 나누는 것이 중요하다.

---

## 1. 큰 진단 순서

문제가 생기면 아래 순서로 본다.

```text
1. topic이 존재하는가?
2. message가 실제로 흐르는가?
3. message 내부 frame_id가 맞는가?
4. TF tree에서 transform이 가능한가?
5. lifecycle node가 active인가?
6. planner가 path를 만들었는가?
7. controller가 /cmd_vel을 만들었는가?
8. Gazebo/robot이 /cmd_vel을 실제로 받는가?
```

---

## 2. 증상별 의심 지점

| 증상 | 우선 의심 | 관련 문서 |
|---|---|---|
| `/robot_ns/scan`은 보이는데 SLAM이 map을 못 만듦 | scan `header.frame_id`, `/robot_ns/tf`, `/clock` | `01_rosbag_topic_remap_vs_frame_id.md` |
| rosbag을 remap했는데 frame 에러가 남 | topic remap과 frame_id 혼동 | `01_rosbag_topic_remap_vs_frame_id.md` |
| AMCL particle이 엉뚱한 곳에 퍼짐 | initialpose, scan frame, map/world mismatch | AMCL 문서 + `01_rosbag_topic_remap_vs_frame_id.md` |
| goal을 줬는데 path가 안 생김 | planner_server, global costmap, map frame | `03_behavior_tree_nav2_practical.md` |
| path는 있는데 `/robot_ns/cmd_vel`이 안 나옴 | controller_server, DWB, local costmap, odom TF | `02_dwb_local_controller_practical.md` |
| `/robot_ns/cmd_vel`은 있는데 로봇이 안 움직임 | diff drive plugin, cmd_vel topic mismatch | Gazebo/plugin 문서 + `02_dwb_local_controller_practical.md` |
| 로봇이 벽 앞에서 이상하게 돌거나 멈춤 | local costmap, DWB critic, inflation/footprint | `02_dwb_local_controller_practical.md` |
| RViz Goal 실패, CLI goal 성공 | RViz namespace/action/fixed frame 문제 | `03_behavior_tree_nav2_practical.md` |
| 실패 후 recovery처럼 제자리 회전 | BT recovery 동작 가능성 | `03_behavior_tree_nav2_practical.md` |

---

## 3. 상황별 최소 확인 명령어

### SLAM/rosbag frame 문제 의심

```bash
ros2 bag info rosbag2_xxx
ros2 topic echo /robot_ns/scan --once --field header.frame_id
ros2 topic echo /robot_ns/odom --once --field header.frame_id
ros2 topic echo /robot_ns/odom --once --field child_frame_id
ros2 run tf2_tools view_frames
ros2 run tf2_ros tf2_echo odom_robot_ns base_scan
```

---

### AMCL 위치추정 문제 의심

```bash
ros2 topic echo /robot_ns/amcl_pose --once
ros2 topic echo /robot_ns/particle_cloud --once
ros2 run tf2_ros tf2_echo map_robot_ns odom_robot_ns
ros2 topic echo /robot_ns/scan --once --field header.frame_id
```

---

### Nav2 path 생성 문제 의심

```bash
ros2 lifecycle get /robot_ns/bt_navigator
ros2 lifecycle get /robot_ns/planner_server
ros2 topic echo /robot_ns/plan --once
ros2 run tf2_ros tf2_echo map_robot_ns base_footprint
```

---

### Nav2 controller/DWB 문제 의심

```bash
ros2 lifecycle get /robot_ns/controller_server
ros2 param get /robot_ns/controller_server controller_plugins
ros2 param get /robot_ns/controller_server FollowPath.plugin
ros2 param get /robot_ns/controller_server FollowPath.critics
ros2 topic echo /robot_ns/cmd_vel
ros2 run tf2_ros tf2_echo odom_robot_ns base_footprint
```

---

### Gazebo가 속도를 안 받는 문제 의심

```bash
ros2 topic info /robot_ns/cmd_vel -v
ros2 topic echo /robot_ns/cmd_vel
ros2 topic list | grep cmd_vel
```

---

## 4. 디버깅 판단 기준

### `/robot_ns/scan`이 보인다

성공으로 판단하지 않는다.

추가로 확인:

```text
header.frame_id가 무엇인가?
그 frame이 TF tree에 있는가?
SLAM/AMCL/Nav2가 기대하는 scan frame과 맞는가?
```

---

### `/robot_ns/map`이 보인다

Nav2 성공으로 판단하지 않는다.

추가로 확인:

```text
map_robot_ns -> odom_robot_ns -> base_footprint TF가 되는가?
AMCL이 localization을 하고 있는가?
global costmap이 map을 받는가?
```

---

### `/robot_ns/plan`이 보인다

planner는 어느 정도 동작한 것이다.

다음 의심은 controller 쪽이다.

```text
controller_server active?
DWB plugin 정상?
local costmap 정상?
odom TF 정상?
/robot_ns/cmd_vel 발행?
```

---

### `/robot_ns/cmd_vel`이 보인다

Nav2 controller는 어느 정도 동작한 것이다.

다음 의심은 로봇/Gazebo 쪽이다.

```text
Gazebo plugin이 /robot_ns/cmd_vel을 구독하는가?
robot entity가 정상 spawn 되었는가?
cmd_vel 값이 너무 작지 않은가?
```

---

## 5. 핵심 결론

문제를 크게 나누면 다음과 같다.

```text
데이터가 안 들어온다
  -> topic/remap 문제

데이터는 들어오는데 해석이 안 된다
  -> frame_id/TF 문제

현재 위치를 못 잡는다
  -> AMCL/initialpose/map-frame 문제

path를 못 만든다
  -> planner/global costmap 문제

path는 있는데 못 따라간다
  -> controller/DWB/local costmap 문제

속도는 나오는데 안 움직인다
  -> robot/Gazebo plugin/cmd_vel 구독 문제
```

이 폴더의 세 심화 주제는 이 중에서 특히 아래 구간을 설명하기 위해 추가했다.

```text
rosbag-frame 문제
  -> 데이터는 있는데 해석이 안 되는 문제

DWB
  -> path는 있는데 속도 명령을 못 만들거나 이상하게 만드는 문제

Behavior Tree
  -> goal 처리 절차 중 어디서 실패했는지 나누는 문제
```
