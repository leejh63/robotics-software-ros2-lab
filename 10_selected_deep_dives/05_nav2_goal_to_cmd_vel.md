# 05. Nav2 Goal이 /cmd_vel로 바뀌는 흐름

Nav2를 처음 보면 “RViz에서 goal을 찍었는데 왜 로봇이 움직이거나 안 움직이는지”가 잘 안 보인다.

이 문서는 내 환경 기준으로 `NavigateToPose action goal`이 어떻게 `planner`, `controller`, `costmap`을 거쳐 최종적으로 `/robot_ns/cmd_vel`이 되는지 정리한다.

---

## 1. 한 줄 결론

```text
goal은 바로 /cmd_vel이 되지 않는다.
```

Nav2에서는 대략 아래 단계를 거친다.

```text
RViz 또는 CLI goal
  -> /robot_ns/navigate_to_pose action
  -> bt_navigator
  -> planner_server
  -> global path 생성
  -> controller_server
  -> local costmap + DWB controller
  -> velocity_smoother
  -> /robot_ns/cmd_vel
  -> Gazebo diff_drive plugin
  -> robot movement
```

---

## 2. 내 환경 기준 Nav2 구성

주요 파일:

```text
lee_robot_description/launch/nav2.launch.py
lee_robot_description/launch/nav2_navigation.launch.py
lee_robot_description/config/nav2_params.yaml
```

구분:

```text
nav2.launch.py
  -> Gazebo, robot_state_publisher, map_server, AMCL, localization lifecycle, RViz

nav2_navigation.launch.py
  -> nav2_bringup의 navigation_launch.py include
  -> planner/controller/bt_navigator 등 navigation stack 실행
```

즉, 주행하려면 localization과 navigation이 모두 필요하다.

---

## 3. Goal은 action으로 들어간다

Nav2의 목표 이동은 보통 `NavigateToPose` action으로 들어간다.

내 환경 기준 action 이름:

```text
/robot_ns/navigate_to_pose
```

확인:

```bash
ros2 action list | grep navigate
ros2 action info /robot_ns/navigate_to_pose
```

CLI goal 예시:

```bash
ros2 action send_goal /robot_ns/navigate_to_pose nav2_msgs/action/NavigateToPose \
"{pose: {header: {frame_id: 'map_robot_ns'}, pose: {position: {x: 1.0, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}}"
```

여기서 중요한 점:

```text
frame_id: map_robot_ns
```

goal pose는 map 기준 목표 지점이어야 한다.

---

## 4. bt_navigator는 전체 흐름을 지휘한다

`bt_navigator`는 Behavior Tree를 이용해 navigation 절차를 관리한다.

단순화하면 이런 역할이다.

```text
goal을 받는다.
path를 계산하라고 planner에게 요청한다.
path를 따라가라고 controller에게 요청한다.
중간에 실패하면 recovery behavior를 실행할 수 있다.
goal 도착 여부를 판단한다.
```

즉, `bt_navigator`가 직접 속도 명령을 계산하는 것은 아니다.

---

## 5. planner_server는 global path를 만든다

`planner_server`는 현재 위치에서 goal까지 가는 전역 경로를 만든다.

입력:

```text
current pose
  -> AMCL/TF를 통해 map_robot_ns 기준으로 알 수 있음

goal pose
  -> NavigateToPose action goal

global costmap
  -> static map + obstacle + inflation
```

출력:

```text
global path
```

내 `nav2_params.yaml` 기준 planner:

```yaml
planner_plugins:
  - GridBased

GridBased:
  plugin: nav2_navfn_planner/NavfnPlanner
  tolerance: 0.5
  use_astar: false
  allow_unknown: true
```

직관:

```text
map_robot_ns 기준 지도 위에서 현재 위치부터 목표 위치까지 큰 길을 찾는다.
```

---

## 6. global costmap과 local costmap

Nav2는 costmap을 사용해 어디가 지나갈 수 있는 곳인지 판단한다.

### global costmap

내 설정:

```yaml
global_frame: map_robot_ns
robot_base_frame: base_footprint
plugins:
  - static_layer
  - obstacle_layer
  - inflation_layer
```

역할:

```text
전체 지도 기준으로 큰 경로를 계획하는 데 사용
```

static_layer:

```text
/robot_ns/map에서 온 저장 지도 기반 장애물
```

obstacle_layer:

```text
/robot_ns/scan에서 현재 감지한 장애물
```

inflation_layer:

```text
장애물 주변에 안전 여유 공간을 부여
```

### local costmap

내 설정:

```yaml
global_frame: odom_robot_ns
robot_base_frame: base_footprint
rolling_window: true
plugins:
  - obstacle_layer
  - inflation_layer
```

역할:

```text
로봇 주변의 짧은 범위에서 실제 주행 속도를 계산하는 데 사용
```

local costmap은 `odom_robot_ns` 기준 rolling window다. 즉, 로봇 주변을 따라다니는 작은 지도라고 보면 된다.

---

## 7. controller_server와 DWB

`controller_server`는 planner가 만든 path를 따라가기 위한 속도를 계산한다.

내 설정:

```yaml
controller_plugins:
  - FollowPath

FollowPath:
  plugin: dwb_core::DWBLocalPlanner
```

DWB의 직관:

```text
가능한 속도 후보들을 여러 개 샘플링한다.
각 속도 후보로 조금 미래를 시뮬레이션한다.
경로를 잘 따라가는지, 장애물과 가까운지, 목표 방향에 맞는지 점수를 매긴다.
가장 좋은 속도 후보를 선택한다.
```

내 설정에서 중요한 값:

```yaml
max_vel_x: 0.26
max_vel_theta: 1.0
vx_samples: 20
vtheta_samples: 20
sim_time: 1.7
critics:
  - RotateToGoal
  - Oscillation
  - BaseObstacle
  - GoalAlign
  - PathAlign
  - PathDist
  - GoalDist
```

의미:

```text
max_vel_x
  -> 전진 속도 최대값

max_vel_theta
  -> 회전 속도 최대값

vx_samples / vtheta_samples
  -> 평가할 속도 후보 수

sim_time
  -> 각 속도 후보를 얼마 동안 미래 시뮬레이션할지

critics
  -> 후보 경로를 평가하는 기준들
```

---

## 8. velocity_smoother와 /robot_ns/cmd_vel

controller가 속도 명령을 만들면 최종적으로 `/robot_ns/cmd_vel`로 나간다.

중간에 `velocity_smoother`가 속도를 부드럽게 만들 수 있다.

내 설정:

```yaml
velocity_smoother:
  smoothing_frequency: 20.0
  feedback: OPEN_LOOP
  max_velocity: [0.26, 0.0, 1.0]
  min_velocity: [-0.26, 0.0, -1.0]
```

최종적으로 Gazebo diff_drive plugin은 `/robot_ns/cmd_vel`을 받아 로봇을 움직인다.

```text
/robot_ns/cmd_vel
  -> Gazebo diff_drive plugin
  -> robot movement
  -> /robot_ns/odom update
  -> TF update
  -> AMCL/Nav2 feedback loop
```

---

## 9. goal을 줬는데 로봇이 안 움직일 때 확인 순서

### 1단계: action server 존재 확인

```bash
ros2 action list | grep navigate
ros2 action info /robot_ns/navigate_to_pose
```

없다면 navigation launch가 제대로 안 뜬 것이다.

### 2단계: lifecycle active 확인

```bash
ros2 lifecycle nodes
ros2 lifecycle get /robot_ns/controller_server
ros2 lifecycle get /robot_ns/planner_server
ros2 lifecycle get /robot_ns/bt_navigator
```

active가 아니면 goal을 받아도 정상 동작하지 않을 수 있다.

### 3단계: map/scan/odom/TF 확인

```bash
ros2 topic echo /robot_ns/map --once
ros2 topic echo /robot_ns/scan --once
ros2 topic echo /robot_ns/odom --once
ros2 run tf2_ros tf2_echo map_robot_ns base_footprint
```

Nav2는 현재 위치를 알아야 path를 만들 수 있다.

### 4단계: plan 생성 확인

```bash
ros2 topic list | grep plan
ros2 topic echo /robot_ns/plan --once
```

plan이 안 나오면 planner/costmap/current pose 쪽 문제일 가능성이 크다.

### 5단계: cmd_vel 확인

```bash
ros2 topic echo /robot_ns/cmd_vel
ros2 topic hz /robot_ns/cmd_vel
```

`/robot_ns/cmd_vel`이 나오는데 로봇이 안 움직이면 Gazebo plugin이나 topic 연결 문제다.

`/robot_ns/cmd_vel`이 안 나오면 controller/costmap/BT/action 문제다.

---

## 10. RViz Goal 버튼과 CLI action goal의 차이

RViz Goal 버튼이 실패한다고 해서 Nav2가 반드시 죽은 것은 아니다.

RViz는 설정에 따라 다른 action 이름이나 frame을 사용할 수 있다.

예를 들어 RViz가 `/navigate_to_pose`로 goal을 보내는데 실제 action은 `/robot_ns/navigate_to_pose`라면 실패한다.

반대로 CLI에서:

```bash
ros2 action send_goal /robot_ns/navigate_to_pose ...
```

가 성공하면 Nav2 action server 자체는 살아 있다는 강한 근거다.

정리:

```text
RViz Goal 실패
  -> RViz 설정, namespace, action name, fixed frame 문제 가능성

CLI action goal 성공
  -> Nav2 서버 자체는 동작한다는 근거
```

---

## 11. 내 환경에서 최소 실행 흐름

터미널 1:

```bash
cd $ROS2_WS
source install/setup.bash
ros2 launch lee_robot_description nav2.launch.py
```

터미널 2:

```bash
cd $ROS2_WS
source install/setup.bash
ros2 launch lee_robot_description nav2_navigation.launch.py
```

터미널 3:

```bash
ros2 action list | grep navigate
ros2 topic list | grep -E '/robot_ns/(map|scan|odom|cmd_vel|tf)'
ros2 run tf2_ros tf2_echo map_robot_ns base_footprint
```

초기 위치를 줬는지 확인:

```text
RViz 2D Pose Estimate
또는 /initialpose publish
```

goal 전송:

```bash
ros2 action send_goal /robot_ns/navigate_to_pose nav2_msgs/action/NavigateToPose \
"{pose: {header: {frame_id: 'map_robot_ns'}, pose: {position: {x: 1.0, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}}"
```

---

## 12. 핵심 요약

```text
Goal은 바로 /cmd_vel이 되지 않는다.
NavigateToPose action이 bt_navigator로 들어간다.
planner_server는 global costmap을 이용해 path를 만든다.
controller_server는 local costmap과 DWB를 이용해 속도 후보를 평가한다.
velocity_smoother를 거쳐 /robot_ns/cmd_vel이 나온다.
/robot_ns/cmd_vel은 Gazebo diff_drive plugin이 받아 로봇을 움직인다.
/cmd_vel이 안 나오면 action/lifecycle/planner/controller/costmap/TF를 순서대로 확인해야 한다.
/cmd_vel은 나오는데 로봇이 안 움직이면 Gazebo plugin/topic 연결을 확인해야 한다.
```

---

## 13. 이 문서와 연결되는 기존 문서

```text
day_13_nav2/02_nav2_stack_lifecycle_bt.md
day_13_nav2/03_costmap_topic_frame_flow.md
day_13_nav2/04_planner_controller_dwb.md
day_13_nav2/background/action_to_cmd_vel_data_flow.md
day_13_nav2/background/costmap_layers_and_dwb_minimum.md
appendix/nav2_topic_frame_action_table.md
appendix/ros2_navigation_debug_order.md
```
