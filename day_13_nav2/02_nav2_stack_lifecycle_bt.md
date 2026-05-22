# 02. Nav2 Stack, Lifecycle, Behavior Tree

Nav2는 하나의 거대한 노드가 아니다.  
여러 서버 노드가 각각 자기 역할을 맡고, `bt_navigator`가 전체 흐름을 조율한다.

---

## 1. Nav2 Stack 구성

현재 Day 13에서 봐야 할 서버는 크게 세 그룹이다.

### Localization 쪽

```text
map_server
  저장 지도 yaml/pgm을 읽어서 /robot_ns/map 발행

amcl
  /robot_ns/map과 /robot_ns/scan을 비교해서 현재 위치 추정
  map_robot_ns -> odom_robot_ns TF 생성

lifecycle_manager_localization
  map_server와 amcl을 configure/activate
```

이 부분은 Day 12에서 이미 정리한 영역이다.

### Navigation 쪽

```text
bt_navigator
  NavigateToPose action을 받고 전체 주행 절차를 관리

planner_server
  현재 위치에서 목표까지 global path 생성

controller_server
  global path를 따라가도록 속도 명령 계산

behavior_server
  stuck, 장애물, 실패 상황에서 spin/back up/wait 같은 recovery 동작 수행

smoother_server
  경로를 더 부드럽게 다듬는 역할

waypoint_follower
  여러 waypoint를 순차적으로 따라가는 기능

velocity_smoother
  /cmd_vel을 더 부드러운 속도 명령으로 보정

lifecycle_manager_navigation
  navigation 서버들을 active 상태로 전환
```

### Costmap 쪽

```text
global_costmap
  전체 지도 기준으로 큰 경로를 계획할 때 사용

local_costmap
  로봇 주변의 실시간 장애물 회피에 사용
```

Costmap은 별도 서버처럼 보이지만, 실제로는 planner/controller/behavior가 경로 계획과 제어 판단에 사용하는 환경 표현이다.

---

## 2. Lifecycle Node가 헷갈리는 이유

Nav2 서버들은 일반 노드처럼 실행만 됐다고 바로 동작하지 않는다.  
대부분 lifecycle node이기 때문에 상태가 있다.

```text
unconfigured -> inactive -> active
```

실행 중이지만 `active`가 아니면 기능을 제대로 수행하지 않는다.

그래서 아래 두 상태는 다르다.

```text
노드가 node list에 보인다
  프로세스가 떠 있다는 뜻

lifecycle 상태가 active다
  실제 기능 수행 준비가 끝났다는 뜻
```

확인 명령:

```bash
ros2 lifecycle get /robot_ns/planner_server
ros2 lifecycle get /robot_ns/controller_server
ros2 lifecycle get /robot_ns/bt_navigator
ros2 lifecycle get /robot_ns/behavior_server
```

정상 예:

```text
active [3]
```

---

## 3. lifecycle_manager의 역할

`lifecycle_manager_navigation`은 여러 Nav2 서버를 순서대로 활성화한다.

```text
planner_server configure/activate
controller_server configure/activate
bt_navigator configure/activate
behavior_server configure/activate
smoother_server configure/activate
waypoint_follower configure/activate
velocity_smoother configure/activate
```

`autostart:=true`이면 launch 시 자동으로 active까지 진행한다.

`autostart:=false`이면 서버는 뜨지만 자동 활성화하지 않는다. 이 상태는 파라미터 확인이나 단계별 디버깅에는 좋지만, 실제 주행하려면 lifecycle 전환을 따로 해줘야 한다.

```text
autostart:=true
  바로 주행 테스트할 때 적합

autostart:=false
  lifecycle, parameter, server 상태를 수동 확인할 때 적합
```

---

## 4. Behavior Tree의 역할

`bt_navigator`는 goal을 받으면 내부 Behavior Tree를 실행한다.

대표 흐름은 다음과 같다.

```text
NavigateToPose
  ├─ ComputePathToPose
  │    planner_server에 global path 요청
  │
  ├─ FollowPath
  │    controller_server에 path 추종 요청
  │
  ├─ 조건 확인
  │    goal 도달 여부, path 유효성, 장애물 상황 확인
  │
  └─ Recovery
       실패 시 spin, backup, wait 같은 복구 동작
```

즉, Behavior Tree는 “어떤 순서로 planner와 controller와 recovery를 호출할지”를 관리한다.

---

## 5. 왜 Behavior Tree가 필요한가

단순히 한 번 path 만들고 따라가면 끝나는 구조라면 BT가 필요 없어 보일 수 있다.  
하지만 실제 주행에서는 아래 상황이 생긴다.

```text
목표로 가는 길이 갑자기 막힘
로봇이 좁은 곳에서 회전하다가 stuck
local costmap에 장애물 등장
목표 근처에서 방향이 맞지 않음
controller가 path를 따라가지 못함
```

이때 BT는 다음 행동을 결정한다.

```text
다시 경로 계산할 것인가?
기다릴 것인가?
회전할 것인가?
뒤로 물러날 것인가?
goal을 실패 처리할 것인가?
```

---

## 6. 현재 실습에서 꼭 봐야 할 것

Day 13에서는 모든 BT XML을 깊게 분석하는 것보다 아래를 먼저 확인하는 게 중요하다.

```text
1. bt_navigator가 active인지
2. /robot_ns/navigate_to_pose action이 있는지
3. goal을 보내면 planner_server가 /robot_ns/plan을 만드는지
4. controller_server가 /robot_ns/cmd_vel을 만드는지
5. 실패 시 로그가 planner 문제인지 controller 문제인지 구분되는지
```

명령어:

```bash
ros2 action info /robot_ns/navigate_to_pose
ros2 lifecycle get /robot_ns/bt_navigator
ros2 topic echo /robot_ns/plan --once
ros2 topic echo /robot_ns/cmd_vel
```

