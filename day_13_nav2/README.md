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
day_67/ws/lee_robot_description/
├── launch/nav2.launch.py
├── launch/nav2_navigation.launch.py
├── config/nav2_params.yaml
├── config/amcl_param.yaml
├── rviz/amcl.rviz
├── worlds/slam.world
└── urdf/turtlebot.xacro
```

문서 기준 source map은 아래 파일에 따로 정리했다.

```text
day_13_nav2/00_source_file_map.md
```

---

## 2. 현재 실습 구조

현재 구조는 Nav2 전체를 한 번에 합친 단일 launch가 아니라 두 단계로 나뉜다.

```text
1단계: localization/simulation 쪽
  ros2 launch lee_robot_description nav2.launch.py

2단계: navigation stack 쪽
  ros2 launch lee_robot_description nav2_navigation.launch.py
```

이렇게 나누는 이유는 문제를 분리하기 위해서다.

```text
Gazebo, map_server, AMCL 문제가 있는가?
Nav2 planner/controller/bt_navigator 문제가 있는가?
```

둘을 나눠두면 어디서 막혔는지 확인하기 쉽다.

---

## 3. Day 13 문서 읽는 순서

```text
00_source_file_map.md
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

07_my_environment_execution_notes.md
  내 환경 기준 실행 메모

08_runtime_observations_without_code_changes.md
  코드 수정 없이 기록한 실행상 주의점

09_day13_review_questions.md
  복습 질문
```

배경지식은 `background/`에, 명령어는 `commands/`에, 문제 해결은 `troubleshooting/`에 정리했다.

---

## 4. Day 13 핵심 요약

Nav2의 goal 흐름은 아래처럼 이해하면 된다.

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

즉, Nav2는 “목표 하나 넣으면 바로 바퀴가 도는 마법 상자”가 아니다.  
여러 서버가 lifecycle 상태로 올라오고, 각 서버가 costmap과 TF를 보면서 action을 처리한다.

---

## 5. Day 13에서 특히 헷갈리는 부분

```text
1. node가 떠 있다고 active 상태인 것은 아니다.
2. action server가 있어도 TF/costmap이 깨지면 주행은 실패한다.
3. RViz Goal 버튼 실패와 CLI action goal 실패는 같은 문제가 아닐 수 있다.
4. topic 이름 remap과 frame_id 설정은 별개다.
5. global costmap과 local costmap은 목적과 기준 frame이 다르다.
6. controller는 경로를 직접 만드는 게 아니라 경로를 따라갈 속도 후보를 고른다.
7. /robot_ns/cmd_vel에 여러 publisher가 붙으면 teleop과 Nav2가 충돌할 수 있다.
```

---

## 6. 내 환경 기준 최소 실행 흐름

```bash
cd $ROS2_WS
source /opt/ros/humble/setup.bash
source install/setup.bash
```

터미널 1:

```bash
ros2 launch lee_robot_description nav2.launch.py
```

터미널 2:

```bash
ros2 launch lee_robot_description nav2_navigation.launch.py
```

터미널 3:

```bash
ros2 action send_goal /robot_ns/navigate_to_pose nav2_msgs/action/NavigateToPose \
"{pose: {header: {frame_id: 'map_robot_ns'}, pose: {position: {x: 1.0, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}}"
```

자세한 실행법은 아래 문서를 본다.

```text
day_13_nav2/07_my_environment_execution_notes.md
day_13_nav2/commands/nav2_local_cheatsheet.md
```

---

## 7. 코드 수정 여부

이 문서 정리에서는 코드 수정이나 launch/config 변경을 하지 않았다.

```text
코드 수정 없음
패키지 구조 변경 없음
문서 정리 + 배경지식 보강 + 실행 기준 정리만 진행
```

