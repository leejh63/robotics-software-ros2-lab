# 03. Behavior Tree Nav2 practical

이 문서는 Nav2의 Behavior Tree를 “XML 커스터마이징” 수준이 아니라, 주행 흐름을 이해하고 디버깅하는 데 필요한 수준으로 정리한다.

핵심은 다음이다.

```text
bt_navigator는 NavigateToPose action goal을 받고,
Behavior Tree를 따라 planner_server, controller_server, recovery behavior를 호출한다.
```

---

## 1. Behavior Tree가 필요한 이유

로봇 주행은 단순히 아래처럼 끝나지 않는다.

```text
목표 받음 -> 경로 생성 -> 이동 -> 도착
```

실제 주행에서는 계속 판단이 필요하다.

```text
목표가 유효한가?
현재 위치를 알고 있는가?
경로를 만들 수 있는가?
경로가 막혔는가?
로봇이 이동 중인가?
장애물이 생겼는가?
목표 근처에 도착했는가?
실패했으면 costmap을 지울까?
다시 계획할까?
복구 행동을 할까?
```

이 순서를 관리하는 구조가 Behavior Tree다.

---

## 2. Nav2에서 BT Navigator의 위치

전체 흐름:

```text
/robot_ns/navigate_to_pose action goal
  -> /robot_ns/bt_navigator
  -> Behavior Tree 실행
      -> ComputePathToPose
          -> /robot_ns/planner_server
      -> FollowPath
          -> /robot_ns/controller_server
      -> Recovery behaviors
          -> clear costmap / spin / backup 등
  -> action feedback/result
```

즉, `bt_navigator`가 직접 path를 만들거나 velocity를 계산하는 것이 아니다.

```text
path 생성은 planner_server
velocity 생성은 controller_server
전체 절차 관리는 bt_navigator
```

---

## 3. 단순화한 Behavior Tree 흐름

아주 단순화하면 다음과 같다.

```text
NavigateToPose
├── 목표 pose 수신
├── 현재 pose 확인
├── ComputePathToPose
│   └── planner_server 호출
├── FollowPath
│   └── controller_server 호출
├── 목표 도착 확인
└── 실패 시 Recovery
    ├── ClearCostmap
    ├── Spin
    ├── BackUp
    └── Retry
```

실제 Nav2 BT XML은 더 복잡하지만, 학습 단계에서는 이 정도 흐름을 먼저 잡는 것이 중요하다.

---

## 4. BT가 실패를 처리하는 방식

예를 들어 planner가 경로를 못 만들면:

```text
ComputePathToPose 실패
  -> recovery subtree 진입
  -> costmap clear 또는 다른 recovery 실행
  -> 다시 ComputePathToPose 시도
```

controller가 path를 따라가지 못하면:

```text
FollowPath 실패
  -> recovery subtree 진입
  -> local/global costmap clear
  -> 다시 plan 또는 follow 시도
```

그래서 Nav2가 실패했을 때는 “어느 서버가 죽었나”만 볼 게 아니라, BT가 어느 단계에서 실패했는지 생각해야 한다.

---

## 5. 증상별 BT 관점 해석

### 증상 A. action goal 자체가 들어가지 않음

의심:

```text
/robot_ns/navigate_to_pose action 이름 불일치
namespace 문제
bt_navigator가 active 상태가 아님
RViz Goal 설정 문제
```

확인:

```bash
ros2 action list | grep navigate
ros2 action info /robot_ns/navigate_to_pose
ros2 lifecycle get /robot_ns/bt_navigator
```

---

### 증상 B. action goal은 받는데 path가 안 생김

의심:

```text
planner_server 문제
map/costmap 문제
goal이 map 밖에 있음
current pose를 못 찾음
map_robot_ns -> base_footprint TF 문제
```

확인:

```bash
ros2 lifecycle get /robot_ns/planner_server
ros2 topic echo /robot_ns/plan --once
ros2 run tf2_ros tf2_echo map_robot_ns base_footprint
ros2 topic echo /robot_ns/map --once
```

---

### 증상 C. path는 있는데 로봇이 안 움직임

의심:

```text
controller_server 문제
DWB 문제
local costmap 문제
odom_robot_ns -> base_footprint TF 문제
/robot_ns/cmd_vel 미발행
```

확인:

```bash
ros2 lifecycle get /robot_ns/controller_server
ros2 topic echo /robot_ns/cmd_vel
ros2 run tf2_ros tf2_echo odom_robot_ns base_footprint
```

---

### 증상 D. 실패 후 로봇이 제자리에서 돌거나 복구 행동을 함

의심:

```text
BT recovery 동작 중일 수 있음
controller가 path follow에 실패했을 수 있음
costmap이 막혔다고 판단했을 수 있음
목표 도달 조건을 만족하지 못했을 수 있음
```

확인:

```bash
ros2 topic echo /robot_ns/cmd_vel
ros2 topic list | grep costmap
ros2 action info /robot_ns/navigate_to_pose
```

---

## 6. RViz Goal과 CLI action goal 차이

RViz의 `2D Goal Pose` 또는 Nav2 Goal 버튼이 실패해도, CLI action goal이 성공할 수 있다.

이 경우 Nav2 서버가 완전히 죽었다고 보면 안 된다.

가능한 원인:

```text
RViz의 fixed frame 설정 문제
RViz의 namespace/action 설정 문제
goal topic/action plugin 설정 문제
RViz가 보내는 goal frame이 Nav2가 기대하는 frame과 다름
```

반대로 CLI로 아래가 성공하면:

```bash
ros2 action send_goal /robot_ns/navigate_to_pose nav2_msgs/action/NavigateToPose "..."
```

강하게 볼 수 있는 것:

```text
/robot_ns/bt_navigator는 action goal을 받을 수 있다.
planner/controller/lifecycle 일부는 동작하고 있을 가능성이 있다.
문제는 RViz 설정 또는 goal frame/namespace 쪽일 가능성이 커진다.
```

---

## 7. BT와 lifecycle 관계

Nav2 노드들은 lifecycle node로 관리된다.

BT가 planner/controller를 호출하려면 해당 서버들이 active 상태여야 한다.

확인:

```bash
ros2 lifecycle get /robot_ns/bt_navigator
ros2 lifecycle get /robot_ns/planner_server
ros2 lifecycle get /robot_ns/controller_server
ros2 lifecycle get /robot_ns/behavior_server
```

정상적으로 goal을 처리하려면 보통 다음이 필요하다.

```text
bt_navigator: active
planner_server: active
controller_server: active
behavior_server: active
amcl: active
map_server: active
```

---

## 8. 핵심 결론

Behavior Tree를 한 문장으로 정리하면 다음과 같다.

```text
Behavior Tree는 NavigateToPose goal을 처리할 때 planner, controller, recovery를 어떤 순서로 실행하고 실패 시 어떻게 재시도할지 관리하는 Nav2의 의사결정 흐름이다.
```

디버깅 관점에서는 아래처럼 나누면 된다.

```text
goal이 안 들어간다
  -> action 이름, namespace, bt_navigator, RViz 설정 확인

path가 안 생긴다
  -> planner_server, map, global costmap, map_robot_ns TF 확인

path는 있는데 cmd_vel이 없다
  -> controller_server, DWB, local costmap, odom_robot_ns TF 확인

cmd_vel은 있는데 이상하게 움직인다
  -> DWB critic, local costmap, footprint, obstacle/inflation 확인

실패 후 복구 행동이 나온다
  -> BT recovery 흐름으로 보고 planner/controller 실패 원인을 나눠 확인
```
