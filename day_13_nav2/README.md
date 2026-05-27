# Day 13 - Nav2 학습 정리

Day 13의 목표는 “Nav2를 실행했다”가 아니다.  
핵심은 **저장된 지도, AMCL 위치 추정, costmap, planner, controller, action goal, `/cmd_vel`이 어떻게 연결되는지** 이해하는 것이다.

```text
Day 10 Gazebo/URDF
  -> 로봇 모델, 센서, odom, cmd_vel 준비

Day 11 SLAM
  -> 지도 생성: slam_map.yaml, slam_map.pgm

Day 12 AMCL
  -> 저장 지도 위에서 현재 위치 추정

Day 13 Nav2
  -> 목표 지점까지 경로 생성 후 속도 명령 발행
```

---

## 1. Day 13에서 보는 핵심 파일

```text
$ROS2_WS/lee_robot_description/
├── launch/nav2.launch.py
├── launch/localization.launch.py
├── launch/nav2_navigation.launch.py
├── config/nav2_params.yaml
├── config/amcl_param.yaml
├── rviz/amcl.rviz
├── worlds/slam.world
└── urdf/turtlebot.xacro
```

문서 기준 source map은 아래 파일에 따로 정리했다.

```text
day_13_nav2/00_source_overview.md
```

---

## 2. 현재 실습 구조

현재 구조는 두 가지 실행 방식으로 구분한다.

```text
통합 실행:
  ros2 launch lee_robot_description nav2.launch.py

분리 실행 1단계:
  ros2 launch lee_robot_description localization.launch.py

분리 실행 2단계:
  ros2 launch lee_robot_description nav2_navigation.launch.py
```

`nav2.launch.py`는 `localization.launch.py`와 `nav2_navigation.launch.py`를 함께 include하는 통합 wrapper다.
따라서 `nav2.launch.py`를 실행한 뒤 같은 세션에서 `nav2_navigation.launch.py`를 다시 실행하면 Nav2 stack이 중복 실행될 수 있다.

이렇게 나누는 이유는 문제를 분리하기 위해서다.

```text
Gazebo, map_server, AMCL 문제가 있는가?
Nav2 planner/controller/bt_navigator 문제가 있는가?
```

둘을 나눠두면 어디서 막혔는지 확인하기 쉽다.

---

## 3. Day 13 문서 읽는 순서

```text
00_source_overview.md
  실제 파일과 역할 확인

01_overview_flow.md
  Day 10~13 전체 연결 흐름

02_nav2_stack_lifecycle_bt.md
  Nav2 stack, lifecycle, BT Navigator

03_costmap_topic_frame_flow.md
  global/local costmap, topic, frame 관계

04_planner_controller_dwb.md
  planner, controller, DWB, critic 개념

05_execution_split_and_goal_send.md
  실제 실행 순서와 action goal 전송

06_rviz_nav2_validation_and_debug.md
  RViz와 CLI 검증 차이

07_execution_notes.md
  실습 환경 실행 메모

08_runtime_notes.md
  실행 중 헷갈리기 쉬운 관찰 사항과 확인 기준

09_day13_review_questions.md
  복습 질문
```

배경지식은 `background/`에, 명령어는 `commands/`에, 문제 해결은 `troubleshooting/`에 정리했다.

---

## 4. Day 13 핵심 요약

Nav2의 goal 흐름은 아래처럼 이해하면 된다.

아래 topic/frame은 namespace 개념 설명용 예시다. 현재 `projects/ros2_navigation_lab` 실행 예시는 `/lee`, `map_lee`, `odom_lee`를 사용한다.

```text
사용자 goal
  -> /robot_ns/navigate_to_pose action
  -> bt_navigator
  -> planner_server
  -> /robot_ns/plan
  -> controller_server
  -> velocity_smoother
  -> /robot_ns/cmd_vel
  -> Gazebo diff_drive plugin
  -> /robot_ns/odom, /robot_ns/tf 갱신
  -> AMCL 위치 보정
```

즉, Nav2는 단일 노드가 목표를 받아 곧바로 바퀴를 제어하는 구조가 아니다. 여러 서버가 lifecycle 상태로 올라오고, 각 서버가 costmap과 TF를 보면서 action을 처리한다.

---

## 5. Day 13에서 특히 헷갈리는 부분

```text
1. node가 떠 있다고 active 상태인 것은 아니다.
2. action server가 있어도 TF/costmap이 깨지면 주행은 실패한다.
3. RViz Goal 버튼 실패와 CLI action goal 실패는 같은 문제가 아닐 수 있다.
4. topic 이름 remap과 frame_id 설정은 별개다.
5. global costmap과 local costmap은 목적과 기준 frame이 다르다.
6. controller는 경로를 직접 만드는 게 아니라 경로를 따라갈 속도 후보를 고른다.
7. /lee/cmd_vel에 여러 publisher가 붙으면 teleop과 Nav2가 충돌할 수 있다.
```

---

## 6. 현재 프로젝트 기준 최소 실행 흐름

현재 `projects/ros2_navigation_lab` 기준 복사 실행 예시는 `/lee`, `map_lee`, `odom_lee`를 사용한다.

```bash
cd projects/ros2_navigation_lab
source /opt/ros/humble/setup.bash
colcon build --symlink-install --packages-select lee_robot_description
source install/setup.bash
```

통합 실행:

```bash
ros2 launch lee_robot_description nav2.launch.py use_rviz:=false
```

분리 실행을 할 때는 터미널 1에서 localization을 먼저 실행한다.

```bash
ros2 launch lee_robot_description localization.launch.py world:=slam.world
```

터미널 2에서 Nav2 navigation stack만 실행한다.

```bash
cd projects/ros2_navigation_lab
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch lee_robot_description nav2_navigation.launch.py
```

초기 위치:

```bash
ros2 topic pub --once /initialpose geometry_msgs/msg/PoseWithCovarianceStamped \
"{header: {frame_id: 'map_lee'}, pose: {pose: {position: {x: 0.0, y: 0.0, z: 0.0}, orientation: {w: 1.0}}, covariance: [0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0685]}}"
```

Goal 전송:

```bash
ros2 action send_goal /lee/navigate_to_pose nav2_msgs/action/NavigateToPose \
"{pose: {header: {frame_id: 'map_lee'}, pose: {position: {x: 1.0, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}}"
```

자세한 실행법은 아래 문서를 본다.

```text
day_13_nav2/07_execution_notes.md
day_13_nav2/commands/nav2_local_cheatsheet.md
```
