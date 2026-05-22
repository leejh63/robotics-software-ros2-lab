# 02. DWB local controller practical

이 문서는 Nav2의 DWB local controller를 “튜닝 전문가 수준”이 아니라, 디버깅에 필요한 수준으로 정리한다.

핵심은 다음이다.

```text
planner_server는 목표까지의 전체 경로를 만든다.
controller_server는 그 경로를 따라가기 위해 지금 당장 낼 속도 명령을 만든다.
DWB는 controller_server 안에서 여러 속도 후보를 평가해서 /robot_ns/cmd_vel을 고르는 local planner/controller다.
```

---

## 1. Nav2 안에서 DWB의 위치

전체 흐름은 다음과 같다.

```text
NavigateToPose action goal
  -> bt_navigator
  -> planner_server
  -> /robot_ns/plan 생성
  -> controller_server
  -> DWBLocalPlanner
  -> /robot_ns/cmd_vel 생성
  -> Gazebo diff drive plugin
  -> robot 이동
```

DWB가 담당하는 부분:

```text
현재 pose, global path, local costmap, odom을 보고
지금 순간의 선속도/각속도 후보 중 하나를 선택한다.
```

---

## 2. 왜 global path만으로는 로봇이 못 움직이나?

global path는 “어디로 가야 하는지”를 알려준다.

하지만 실제 로봇은 매 순간 속도 명령이 필요하다.

```text
linear.x = 얼마로 전진할 것인가?
angular.z = 얼마로 회전할 것인가?
장애물 앞에서 멈출 것인가?
path를 따라가기 위해 왼쪽으로 돌 것인가?
목표 근처에서는 어떻게 감속할 것인가?
```

이 결정을 controller가 한다.

즉:

```text
planner_server = 경로를 만든다.
controller_server = 속도를 만든다.
DWB = 속도 후보를 평가해서 하나를 고른다.
```

---

## 3. DWB가 속도를 고르는 방식

DWB는 단순히 “path 방향으로 전진”하지 않는다.

대략적인 흐름은 다음과 같다.

```text
1. 가능한 velocity 후보를 여러 개 만든다.
2. 각 velocity 후보로 짧은 시간 동안 움직인다고 가정한다.
3. 예상 trajectory를 만든다.
4. 각 trajectory를 여러 critic으로 평가한다.
5. 가장 점수가 좋은 trajectory의 velocity를 /cmd_vel로 낸다.
```

예를 들어 후보는 이런 식이다.

```text
후보 A: linear.x = 0.05, angular.z = 0.0
후보 B: linear.x = 0.10, angular.z = 0.2
후보 C: linear.x = 0.10, angular.z = -0.2
후보 D: linear.x = 0.00, angular.z = 0.5
```

DWB는 각 후보가 만든 짧은 trajectory를 평가한다.

---

## 4. critic이란 무엇인가?

critic은 후보 trajectory를 평가하는 기준이다.

현재 기록 기준으로 자주 보는 critic은 다음과 같다.

```yaml
FollowPath:
  plugin: dwb_core::DWBLocalPlanner
  critics:
    - RotateToGoal
    - Oscillation
    - BaseObstacle
    - GoalAlign
    - PathAlign
    - PathDist
    - GoalDist
```

각 critic의 의미를 아주 단순화하면 다음과 같다.

| critic | 보는 것 | 직관 |
|---|---|---|
| `BaseObstacle` | 장애물과 충돌하거나 너무 가까운가 | 벽에 박으면 안 됨 |
| `PathAlign` | global path 방향과 잘 맞는가 | 경로 방향으로 가야 함 |
| `GoalAlign` | 목표 방향과 잘 맞는가 | 목표 쪽을 향해야 함 |
| `PathDist` | path에서 얼마나 떨어졌는가 | 경로에서 너무 벗어나면 안 됨 |
| `GoalDist` | 목표와 얼마나 가까워지는가 | 목표에 가까워져야 함 |
| `RotateToGoal` | 목표 근처에서 방향 정렬이 필요한가 | 도착 후 자세를 맞춤 |
| `Oscillation` | 앞뒤/좌우로 흔들리는가 | 제자리 진동 방지 |

DWB는 이 critic 점수들을 합쳐서 가장 나은 속도 후보를 고른다.

---

## 5. DWB가 실패할 때 증상별 의심 지점

### 증상 A. path는 있는데 `/robot_ns/cmd_vel`이 안 나옴

의심:

```text
controller_server가 active 상태가 아님
FollowPath plugin 설정 오류
local costmap이 robot pose를 못 찾음
odom topic이 안 들어옴
base frame / odom frame TF가 안 맞음
DWB critic 설정 문제
```

확인:

```bash
ros2 lifecycle get /robot_ns/controller_server
ros2 param get /robot_ns/controller_server controller_plugins
ros2 param get /robot_ns/controller_server FollowPath.plugin
ros2 param get /robot_ns/controller_server FollowPath.critics
ros2 topic echo /robot_ns/cmd_vel --once
ros2 topic echo /robot_ns/odom --once
ros2 run tf2_ros tf2_echo odom_robot_ns base_footprint
```

---

### 증상 B. `/robot_ns/cmd_vel`은 나오는데 로봇이 안 움직임

의심:

```text
Gazebo diff drive plugin이 /robot_ns/cmd_vel을 구독하지 않음
cmd_vel topic 이름 불일치
속도 값이 너무 작음
simulation time 문제
robot spawn/plugin 문제
```

확인:

```bash
ros2 topic echo /robot_ns/cmd_vel
ros2 topic info /robot_ns/cmd_vel -v
ros2 topic list | grep cmd_vel
```

---

### 증상 C. 로봇이 벽 근처에서 이상하게 돈다

의심:

```text
local costmap obstacle/inflation 설정
BaseObstacle critic 영향
robot footprint/radius 설정
scan topic/frame 문제
DWB 속도 후보 범위 문제
```

확인:

```bash
ros2 topic list | grep costmap
ros2 topic echo /robot_ns/scan --once --field header.frame_id
ros2 run tf2_ros tf2_echo base_footprint base_scan
ros2 param get /robot_ns/controller_server FollowPath.critics
```

---

### 증상 D. 목표 근처에서 도착 판정이 안 남

의심:

```text
goal checker tolerance
RotateToGoal critic
robot yaw 목표 자세 정렬 문제
localization pose가 흔들림
```

확인:

```bash
ros2 param get /robot_ns/controller_server goal_checker_plugins
ros2 param get /robot_ns/controller_server general_goal_checker.xy_goal_tolerance
ros2 param get /robot_ns/controller_server general_goal_checker.yaw_goal_tolerance
```

---

## 6. DWB와 costmap의 관계

DWB는 장애물을 직접 “센서 원본”만 보고 피하는 것이 아니다.

대부분의 경우 다음 흐름이다.

```text
/robot_ns/scan
  -> local_costmap obstacle_layer
  -> inflation_layer
  -> local costmap
  -> DWB critic들이 trajectory 평가에 사용
```

따라서 DWB 문제가 의심될 때도 scan과 TF를 먼저 확인해야 한다.

```text
scan이 local costmap에 못 들어가면
DWB는 장애물 정보를 제대로 평가할 수 없다.
```

---

## 7. 내 환경 기준 확인 명령어

```bash
# controller server 상태
ros2 lifecycle get /robot_ns/controller_server

# controller plugin 확인
ros2 param get /robot_ns/controller_server controller_plugins
ros2 param get /robot_ns/controller_server FollowPath.plugin
ros2 param get /robot_ns/controller_server FollowPath.critics

# odom / TF 확인
ros2 topic echo /robot_ns/odom --once
ros2 run tf2_ros tf2_echo odom_robot_ns base_footprint

# cmd_vel 확인
ros2 topic echo /robot_ns/cmd_vel
ros2 topic info /robot_ns/cmd_vel -v
```

---

## 8. 핵심 결론

DWB를 한 문장으로 정리하면 다음과 같다.

```text
DWB는 Nav2 controller_server 안에서 여러 velocity 후보를 짧게 시뮬레이션하고, costmap/path/goal/obstacle 기준으로 평가해서 가장 나은 후보를 /robot_ns/cmd_vel로 내는 local controller다.
```

디버깅 관점에서는 아래 순서로 본다.

```text
1. NavigateToPose goal이 들어갔는가?
2. /robot_ns/plan이 생성됐는가?
3. controller_server가 active인가?
4. odom_robot_ns -> base_footprint TF가 되는가?
5. local costmap이 robot pose와 scan을 받는가?
6. FollowPath plugin과 critics가 정상인가?
7. /robot_ns/cmd_vel이 나오는가?
8. Gazebo plugin이 /robot_ns/cmd_vel을 구독하는가?
```
