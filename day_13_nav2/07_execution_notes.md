# 07. 실습 환경 Nav2 실행 메모

이 문서는 예시 실습 환경에서 Nav2를 다시 실행할 때 필요한 경로, 명령, 토픽 확인 순서를 정리한다.

---

## 1. 기준 환경

```text
OS/ROS: Ubuntu 22.04 + ROS2 Humble 기준
workspace: $ROS2_WS
package: lee_robot_description
simulation: Gazebo classic
robot model: turtlebot.xacro
localization launch: lee_robot_description/launch/localization.launch.py
navigation launch: lee_robot_description/launch/nav2_navigation.launch.py
integrated launch: lee_robot_description/launch/nav2.launch.py
nav2 params: lee_robot_description/config/nav2_params.yaml
amcl params: lee_robot_description/config/amcl_param.yaml
```

현재 `projects/ros2_navigation_lab` 실행 기준:

```text
namespace: lee
map topic: /lee/map
scan topic: /lee/scan
odom topic: /lee/odom
cmd_vel topic: /lee/cmd_vel
tf topic: /lee/tf, /lee/tf_static
navigate action: /lee/navigate_to_pose
map frame: map_lee
odom frame: odom_lee
base frame: base_footprint
scan frame: base_scan
```

---

## 2. world-map 짝 맞추기

현재 기록 기준으로는 아래처럼 맞춰서 보는 것이 안전하다.

```text
slam.world       <-> slam_map.yaml
lee_world.world  <-> room_map.yaml
```

틀린 조합을 쓰면 AMCL이 지도를 기준으로 위치를 맞출 수 없다.

예:

```text
Gazebo는 lee_world.world인데 map은 slam_map.yaml
  -> LiDAR가 보는 벽과 저장 지도가 다름
  -> /particle_cloud가 수렴하지 않거나 /amcl_pose가 이상함
  -> Nav2 goal을 보내도 path/costmap이 이상해질 수 있음
```

---

## 3. 기본 실행 순서

통합 실행은 아래 한 명령만 사용한다.

```bash
cd $ROS2_WS
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 launch lee_robot_description nav2.launch.py
```

분리 실행은 터미널 1에서 localization을 먼저 실행한다.

```bash
cd $ROS2_WS
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 launch lee_robot_description localization.launch.py
```

터미널 2에서 navigation stack만 실행한다.

```bash
cd $ROS2_WS
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 launch lee_robot_description nav2_navigation.launch.py
```

터미널 3:

```bash
cd $ROS2_WS
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 action send_goal /lee/navigate_to_pose nav2_msgs/action/NavigateToPose \
"{pose: {header: {frame_id: 'map_lee'}, pose: {position: {x: 1.0, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}}"
```

---

## 4. 명시적으로 map/world 지정

`slam.world`와 `slam_map.yaml`:

```bash
ros2 launch lee_robot_description localization.launch.py \
  world:=slam.world \
  map_yaml:=$ROS2_WS/slam_map.yaml
```

`lee_world.world`와 `room_map.yaml`:

```bash
ros2 launch lee_robot_description localization.launch.py \
  world:=lee_world.world \
  map_yaml:=$ROS2_WS/room_map.yaml
```

---

## 5. localization 확인

```bash
ros2 topic echo /lee/map --once
ros2 topic hz /lee/scan
ros2 topic echo /lee/odom --once
ros2 topic echo /amcl_pose --once
ros2 topic echo /particle_cloud --once
```

TF:

```bash
ros2 run tf2_ros tf2_echo map_lee odom_lee --ros-args -r /tf:=/lee/tf -r /tf_static:=/lee/tf_static
ros2 run tf2_ros tf2_echo odom_lee base_footprint --ros-args -r /tf:=/lee/tf -r /tf_static:=/lee/tf_static
ros2 run tf2_ros tf2_echo base_footprint base_scan --ros-args -r /tf:=/lee/tf -r /tf_static:=/lee/tf_static
```

RViz에서 `2D Pose Estimate`를 찍고, `/particle_cloud`가 로봇 주변으로 수렴하는지 본다.

---

## 6. navigation 확인

노드:

```bash
ros2 node list | grep -E 'lee|map_server|amcl|planner|controller|bt_navigator|costmap' | sort
```

lifecycle:

```bash
ros2 lifecycle get /lee/planner_server
ros2 lifecycle get /lee/controller_server
ros2 lifecycle get /lee/bt_navigator
ros2 lifecycle get /lee/behavior_server
```

action:

```bash
ros2 action list | grep navigate
ros2 action info /lee/navigate_to_pose
```

costmap:

```bash
ros2 topic echo /lee/global_costmap/costmap --once
ros2 topic echo /lee/local_costmap/costmap --once
```

path/cmd_vel:

```bash
ros2 topic echo /lee/plan --once
ros2 topic echo /lee/cmd_vel
```

---

## 7. RViz Goal이 안 될 때 우회 방법

현재 기록 기준으로 RViz Nav2 Goal 버튼은 namespace/action 연결 문제로 안 맞을 수 있다.
그럴 때는 CLI action goal을 기준으로 검증한다.

좌표를 RViz에서 얻고 싶으면:

```bash
ros2 topic echo /clicked_point
```

RViz의 `Publish Point`로 자유 공간을 찍고 나온 x/y를 goal에 넣는다.

---

## 8. 예시 환경에서 우선 의심할 것

문제가 생기면 아래를 우선 의심한다.

```text
1. map/world 조합이 맞는가?
2. RViz Fixed Frame이 map_lee인가?
3. /lee/scan, /lee/odom, /lee/tf가 살아 있는가?
4. AMCL 초기 위치를 찍었는가?
5. /lee/planner_server, /lee/controller_server가 active인가?
6. action 이름을 /navigate_to_pose가 아니라 /lee/navigate_to_pose로 보냈는가?
7. /lee/cmd_vel에 teleop이나 wall follower가 같이 붙어 있지 않은가?
```
