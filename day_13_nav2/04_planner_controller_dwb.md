# 04. Planner Server, Controller Server, DWB

Nav2에서 로봇이 목표까지 움직이는 핵심은 두 단계다.

```text
planner_server
  어디로 갈지 큰 경로를 만든다.

controller_server
  그 경로를 실제 속도 명령으로 바꾼다.
```

---

## 1. Global Planner의 역할

Global planner는 현재 위치에서 목표 위치까지의 전체 경로를 만든다.

```text
현재 위치 + 목표 위치 + global costmap -> /robot_ns/plan
```

스마트폰 내비게이션으로 치면 전체 경로를 계산하는 부분이다.

Global planner가 직접 바퀴를 제어하지는 않는다.  
`/robot_ns/plan`이라는 경로를 만들고, 그 경로를 controller가 따라가게 한다.

---

## 2. NavFn Planner

현재 기본 실습에서는 `NavFn` 계열 설정을 기준으로 보면 된다.

대표 설정 형태:

```yaml
planner_server:
  ros__parameters:
    use_sim_time: true
    expected_planner_frequency: 20.0
    planner_plugins:
      - GridBased
    GridBased:
      plugin: nav2_navfn_planner/NavfnPlanner
      tolerance: 0.5
      use_astar: false
      allow_unknown: true
```

의미:

```text
plugin
  어떤 planner 알고리즘을 사용할지 지정한다.

tolerance
  목표 지점에 정확히 못 가도 허용할 반경이다.

use_astar
  false이면 Dijkstra 기반, true이면 A* 기반으로 볼 수 있다.

allow_unknown
  unknown 영역을 경로 후보로 허용할지 결정한다.
```

NavFn은 단순하고 안정적이다. TurtleBot처럼 제자리 회전이 가능한 차동 구동 로봇에서는 실습용으로 충분하다.

---

## 3. Controller Server의 역할

Controller는 global path를 보고 실제 속도 명령을 만든다.

```text
/robot_ns/plan + local costmap + 현재 odom -> /robot_ns/cmd_vel
```

여기서 중요한 점은 controller가 “경로를 만드는 것”이 아니라는 점이다.

```text
planner
  지도 전체를 보고 길을 만든다.

controller
  지금 당장 어떤 속도로 움직일지 고른다.
```

---

## 4. DWB Controller 개념

현재 설정은 `dwb_core::DWBLocalPlanner`를 사용한다.

DWB는 여러 속도 후보를 만들어 보고, 각 후보가 가까운 미래에 어떤 궤적을 만들지 시뮬레이션한다.  
그 다음 critic 점수를 계산해서 가장 괜찮은 속도를 고른다.

```text
속도 후보 생성
  v_x, v_y, v_theta 후보 샘플링
        ↓
짧은 미래 궤적 예측
        ↓
critic 점수 계산
        ↓
가장 낮은 비용의 속도 선택
        ↓
/robot_ns/cmd_vel 발행
```

차동 구동 로봇에서는 보통 `v_y = 0`이다.  
옆으로 미끄러지듯 이동하지 못하기 때문이다.

---

## 5. Critic이 하는 일

Critic은 각 속도 후보를 평가하는 기준이다.

현재 설정에는 아래 critic들이 있다.

```text
RotateToGoal
Oscillation
BaseObstacle
GoalAlign
PathAlign
PathDist
GoalDist
```

대략 의미:

| critic | 의미 |
|---|---|
| `BaseObstacle` | 장애물과 너무 가까운 궤적을 나쁘게 평가 |
| `PathAlign` | global path 방향과 잘 맞는지 평가 |
| `PathDist` | global path에서 얼마나 벗어나는지 평가 |
| `GoalAlign` | 목표 방향으로 정렬되는지 평가 |
| `GoalDist` | 목표에 가까워지는지 평가 |
| `RotateToGoal` | 목표 근처에서 방향을 맞추는 동작 평가 |
| `Oscillation` | 앞뒤로 떨리거나 반복되는 움직임 억제 |

`No critics defined for FollowPath` 에러는 이 critic 목록을 controller가 읽지 못했다는 뜻이다.

---

## 6. 현재 설정에서 중요한 DWB 파라미터

```yaml
FollowPath:
  plugin: dwb_core::DWBLocalPlanner
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
  최대 전진 속도

max_vel_theta
  최대 회전 속도

vx_samples, vtheta_samples
  속도 후보를 몇 개 샘플링할지

sim_time
  각 속도 후보를 몇 초 뒤까지 예측해볼지

critics
  후보 궤적 평가 기준 목록
```

---

## 7. /robot_ns/plan은 있는데 /robot_ns/cmd_vel이 없을 수 있는 이유

이 경우 planner는 성공했지만 controller가 실패한 것이다.

가능한 원인:

```text
local costmap이 비정상
odom topic이 안 들어옴
TF가 끊김
DWB critic 설정 문제
goal이 너무 벽 가까이 있음
robot footprint/radius가 costmap과 맞지 않음
controller_server가 active가 아님
```

확인:

```bash
ros2 topic echo /robot_ns/plan --once
ros2 topic echo /robot_ns/local_costmap/costmap --once
ros2 topic echo /robot_ns/odom --once
ros2 lifecycle get /robot_ns/controller_server
ros2 param get /robot_ns/controller_server controller_plugins
ros2 param get /robot_ns/controller_server FollowPath.critics
```

---

## 8. 학습 관점 결론

Nav2의 주행은 아래처럼 나누어 이해해야 한다.

```text
경로를 못 만든다
  planner_server / global_costmap / map / goal 위치 문제

경로는 있는데 움직이지 않는다
  controller_server / local_costmap / odom / DWB / cmd_vel 문제

cmd_vel은 나오는데 로봇이 안 움직인다
  Gazebo diff_drive plugin / topic remap / 다른 publisher 충돌 문제
```

