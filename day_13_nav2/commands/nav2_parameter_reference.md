# Nav2 Parameter Reference

이 문서는 Day 13 실습에서 자주 확인하는 Nav2 파라미터를 빠르게 보기 위한 문서다.

---

## 1. Planner Server

대표 구조:

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

| 파라미터 | 의미 | 확인 포인트 |
|---|---|---|
| `planner_plugins` | 사용할 planner plugin 이름 목록 | `GridBased` 같은 이름이 하위 설정과 일치해야 함 |
| `GridBased.plugin` | 실제 planner 구현 | NavFn, Smac 등 |
| `tolerance` | 목표점 허용 반경 | 너무 작으면 목표 근처 실패 가능 |
| `use_astar` | A* 사용 여부 | false면 Dijkstra 계열로 이해 |
| `allow_unknown` | unknown 영역 통과 허용 | unknown을 막으면 경로 실패 가능 |

---

## 2. Controller Server

대표 구조:

```yaml
controller_server:
  ros__parameters:
    use_sim_time: true
    controller_frequency: 20.0
    odom_topic: /robot_ns/odom
    progress_checker_plugin: progress_checker
    goal_checker_plugins:
      - general_goal_checker
    controller_plugins:
      - FollowPath
```

| 파라미터 | 의미 | 확인 포인트 |
|---|---|---|
| `controller_frequency` | 속도 명령 계산 주기 | 낮으면 반응 느림, 높으면 CPU 부하 증가 |
| `odom_topic` | controller가 참고할 odom topic | 현재는 `/robot_ns/odom` |
| `controller_plugins` | 로컬 controller plugin 이름 목록 | `FollowPath` 하위 설정이 반드시 있어야 함 |
| `goal_checker_plugins` | 목표 도달 판정 plugin | tolerance 문제와 연결 |
| `progress_checker_plugin` | 로봇이 실제로 진행 중인지 검사 | stuck 판정과 연결 |

---

## 3. DWB FollowPath

대표 구조:

```yaml
FollowPath:
  plugin: dwb_core::DWBLocalPlanner
  min_vel_x: 0.0
  max_vel_x: 0.26
  max_vel_theta: 1.0
  acc_lim_x: 2.5
  acc_lim_theta: 3.2
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

| 파라미터 | 의미 | 문제 시 증상 |
|---|---|---|
| `max_vel_x` | 최대 전진 속도 | 너무 높으면 불안정, 너무 낮으면 느림 |
| `max_vel_theta` | 최대 회전 속도 | 너무 낮으면 회전 답답함 |
| `acc_lim_x` | 전진 가속도 제한 | 너무 높으면 급가속 |
| `vx_samples` | 선속도 후보 개수 | 많을수록 정밀하지만 계산량 증가 |
| `vtheta_samples` | 각속도 후보 개수 | 회전 후보 탐색 정밀도 |
| `sim_time` | 몇 초 미래까지 궤적 평가 | 너무 길면 반응 느림, 너무 짧으면 근시안적 |
| `critics` | 궤적 평가 기준 목록 | 비어 있으면 `No critics defined` 오류 |

---

## 4. Goal Checker

```yaml
general_goal_checker:
  plugin: nav2_controller::SimpleGoalChecker
  xy_goal_tolerance: 0.25
  yaw_goal_tolerance: 0.25
  stateful: true
```

| 파라미터 | 의미 |
|---|---|
| `xy_goal_tolerance` | 목표 위치 허용 오차 |
| `yaw_goal_tolerance` | 목표 방향 허용 오차 |
| `stateful` | 도달 상태 유지 여부 |

목표 근처에서 계속 회전하거나 실패하면 tolerance가 너무 빡빡한지 본다.

---

## 5. Global Costmap

대표 구조:

```yaml
global_costmap:
  global_costmap:
    ros__parameters:
      global_frame: map_robot_ns
      robot_base_frame: base_footprint
      plugins:
        - static_layer
        - obstacle_layer
        - inflation_layer
```

| 파라미터 | 의미 |
|---|---|
| `global_frame` | 전체 지도 기준 frame. 현재는 `map_robot_ns` |
| `robot_base_frame` | 로봇 기준 frame. 현재는 `base_footprint` |
| `static_layer` | 저장 지도 기반 벽 정보 |
| `obstacle_layer` | 실시간 센서 장애물 |
| `inflation_layer` | 장애물 주변 안전 버퍼 |
| `map_topic` | 현재 설정은 `/robot_ns/map` |
| `observation_sources` | 현재 설정은 `scan` |
| `scan.topic` | 현재 설정은 `/robot_ns/scan` |

---

## 6. Local Costmap

대표 구조:

```yaml
local_costmap:
  local_costmap:
    ros__parameters:
      global_frame: odom_robot_ns
      robot_base_frame: base_footprint
      rolling_window: true
      width: 3
      height: 3
      resolution: 0.05
      plugins:
        - obstacle_layer
        - inflation_layer
```

| 파라미터 | 의미 |
|---|---|
| `global_frame` | 로컬 기준 frame. 보통 `odom_robot_ns` |
| `rolling_window` | 로봇 중심으로 움직이는 창 사용 |
| `width`, `height` | local costmap 크기 |
| `resolution` | costmap 격자 해상도 |
| `obstacle_layer` | 실시간 scan 기반 장애물 |
| `inflation_layer` | 장애물 주변 안전 버퍼 |

---

## 7. BT Navigator

```yaml
bt_navigator:
  ros__parameters:
    use_sim_time: true
    global_frame: map_robot_ns
    robot_base_frame: base_footprint
    odom_topic: /robot_ns/odom
    navigators:
      - navigate_to_pose
      - navigate_through_poses
```

| 파라미터 | 의미 |
|---|---|
| `global_frame` | goal과 전역 경로 기준 frame |
| `robot_base_frame` | 로봇 기준 frame |
| `odom_topic` | odometry topic |
| `navigators` | 사용할 navigator plugin 목록 |

---

## 8. Velocity Smoother

```yaml
velocity_smoother:
  ros__parameters:
    smoothing_frequency: 20.0
    feedback: OPEN_LOOP
    max_velocity: [0.26, 0.0, 1.0]
    min_velocity: [-0.26, 0.0, -1.0]
    odom_topic: /robot_ns/odom
```

| 파라미터 | 의미 |
|---|---|
| `smoothing_frequency` | 속도 smoothing 주기 |
| `feedback` | open loop/closed loop 방식 |
| `max_velocity` | x, y, theta 최대 속도 |
| `min_velocity` | x, y, theta 최소 속도 |
| `odom_topic` | 속도 피드백에 사용할 odom topic |

