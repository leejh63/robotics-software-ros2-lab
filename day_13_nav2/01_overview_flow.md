# 01. Day 13 Nav2 전체 흐름

Day 13의 목표는 단순히 로봇을 움직이는 것이 아니다.  
Day 10~12에서 만든 요소들을 연결해서, 사용자가 목적지만 찍으면 로봇이 스스로 경로를 만들고 이동하는 구조를 확인하는 것이다.

---

## 1. Day 10~13 연결 구조

아래 topic/frame은 현재 `projects/ros2_navigation_lab` 실행 예시 기준이다.

```text
Day 10 Gazebo/URDF
  로봇 모델, LiDAR, odom, cmd_vel, Gazebo plugin 준비
        ↓
Day 11 SLAM
  /lee/scan + /lee/odom + TF로 slam_map.yaml, slam_map.pgm 생성
        ↓
Day 12 AMCL
  저장 지도 + 실시간 LiDAR를 비교해서 현재 위치 추정
        ↓
Day 13 Nav2
  현재 위치에서 목표 지점까지 경로를 만들고 /lee/cmd_vel 발행
```

Day 13은 앞 단계를 모두 소비한다.  
그래서 Nav2 문제가 생겼을 때 바로 `nav2_params.yaml`만 보면 안 된다. 아래 순서로 끊어서 확인해야 한다.

```text
1. Gazebo 로봇이 떠 있는가?
2. /lee/scan, /lee/odom, /lee/tf가 있는가?
3. /lee/map이 발행되는가?
4. AMCL이 /amcl_pose와 map_lee -> odom_lee TF를 만드는가?
5. Nav2 lifecycle 서버들이 active인가?
6. /lee/navigate_to_pose action이 떠 있는가?
7. goal 전송 후 /lee/plan이 생기는가?
8. /lee/cmd_vel이 발행되는가?
9. Gazebo 로봇이 실제로 움직이는가?
```

---

## 2. 현재 실행 구조와 launch 역할

현재 실행 구조는 통합 실행과 분리 실행을 모두 지원한다.

```text
통합 실행: nav2.launch.py
  localization.launch.py + nav2_navigation.launch.py를 함께 include

분리 실행 1단계: localization.launch.py
  Gazebo
  robot_state_publisher
  spawn_entity.py
  map_server
  AMCL
  lifecycle_manager_localization
  RViz

분리 실행 2단계: nav2_navigation.launch.py
  planner_server
  controller_server
  bt_navigator
  behavior_server
  smoother_server
  waypoint_follower
  velocity_smoother
  lifecycle_manager_navigation
  global_costmap
  local_costmap
```

`nav2.launch.py`를 이미 실행했다면 `nav2_navigation.launch.py`를 추가로 실행하지 않는다.
분리 실행으로 디버깅할 때만 `localization.launch.py` 다음에 `nav2_navigation.launch.py`를 실행한다.

이렇게 나눈 이유는 명확하다.

```text
Gazebo/AMCL 문제가 있는지, Nav2 navigation 문제가 있는지 분리해서 보기 위해서다.
```

처음부터 통합 런치를 만들면 편하긴 하지만, 문제가 생겼을 때 원인 범위가 너무 넓어진다.

---

## 3. Nav2 goal이 처리되는 순서

사용자가 목표를 보내면 다음 순서로 흐른다.

```text
1. 사용자가 goal Pose를 보냄
   /lee/navigate_to_pose

2. bt_navigator가 goal을 받음
   Behavior Tree 흐름 시작

3. planner_server가 global path 생성
   현재 위치 + 지도 + costmap -> /lee/plan

4. controller_server가 path를 추종
   /lee/plan + local_costmap + 현재 odom -> 속도 계산

5. velocity_smoother가 속도 명령을 다듬음
   급격한 속도 변화 완화

6. /lee/cmd_vel 발행
   Gazebo diff_drive plugin이 구독

7. 로봇이 움직임
   /lee/odom, /lee/tf, /lee/scan이 다시 갱신

8. AMCL이 위치를 다시 보정
   map_lee -> odom_lee TF 갱신

9. 목표 도달 또는 실패 판정
   success, canceled, aborted 등 action result 출력
```

중요한 점은 이 흐름이 한 번만 실행되는 것이 아니라 주행 중 계속 반복된다는 것이다.

```text
로봇 이동 -> 센서 갱신 -> 위치 추정 갱신 -> costmap 갱신 -> 경로/속도 재계산
```

---

## 4. 최소 성공 조건

Nav2가 정상적으로 주행하려면 최소한 아래 조건이 맞아야 한다.

| 조건 | 확인 방법 | 실패 시 증상 |
|---|---|---|
| 지도 발행 | `ros2 topic echo /lee/map --once` | RViz 지도 없음, global costmap 이상 |
| 초기 위치 추정 | `/amcl_pose`, `map_lee -> odom_lee` | goal은 보내도 로봇 위치를 모름 |
| navigation lifecycle active | `ros2 lifecycle get /lee/planner_server` 등 | action server는 있어도 반응 불안정 |
| action 존재 | `ros2 action list | grep navigate` | goal 전송 실패 |
| global costmap 정상 | `/lee/global_costmap/costmap` | No Path Found |
| local costmap 정상 | `/lee/local_costmap/costmap` | path는 있는데 주행 실패 |
| cmd_vel 연결 | `ros2 topic info /lee/cmd_vel -v` | 속도 명령은 없거나 Gazebo가 못 받음 |

---

## 5. 현재 확인한 결론

현재 기록 기준 결론은 다음과 같다.

```text
Nav2 서버 자체는 동작한다.
/lee/navigate_to_pose action goal로는 로봇 주행을 확인했다.
RViz Nav2 Goal 버튼은 /lee namespace/action 기준 추가 설정이 필요할 수 있다.
```

따라서 다음과 같이 판단해야 한다.

```text
RViz 버튼 실패
  RViz 설정/namespace/action 연결 문제일 가능성이 높음

action goal 실패
  Nav2 서버, lifecycle, costmap, TF 문제일 가능성이 높음

cmd_vel 없음
  controller/local_costmap/DWB 문제일 가능성이 높음
```

---

## 6. 학습 관점에서 봐야 할 것

Day 13에서는 “결과적으로 로봇이 움직였다”만 보면 안 된다.  
아래 연결을 설명할 수 있어야 한다.

```text
/map이 왜 필요한가?
/amcl_pose는 어디에 쓰이는가?
map_lee -> odom_lee TF는 왜 필요한가?
planner_server는 무엇을 만들고 controller_server는 무엇을 만드는가?
왜 /lee/plan이 있어도 /lee/cmd_vel이 없을 수 있는가?
왜 RViz Goal 버튼이 안 되는데 action CLI는 될 수 있는가?
```

이 질문에 답할 수 있으면 Day 13은 단순 실행이 아니라 구조 이해 단계로 올라간 것이다.
