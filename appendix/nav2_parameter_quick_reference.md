# Nav2 파라미터 빠른 참조

Day 13 기준으로 자주 보는 Nav2 parameter를 빠르게 정리한다.

---

## 1. Frame / Topic 핵심

```text
global frame: map_robot_ns
local frame: odom_robot_ns
robot base frame: base_footprint
scan topic: /robot_ns/scan
odom topic: /robot_ns/odom
map topic: /robot_ns/map
cmd_vel topic: /robot_ns/cmd_vel
```

---

## 2. Planner

```yaml
planner_server:
  ros__parameters:
    planner_plugins:
      - GridBased
    GridBased:
      plugin: nav2_navfn_planner/NavfnPlanner
      tolerance: 0.5
      use_astar: false
      allow_unknown: true
```

확인:

```bash
ros2 param get /robot_ns/planner_server planner_plugins
ros2 param get /robot_ns/planner_server GridBased.plugin
```

---

## 3. Controller / DWB

```yaml
controller_server:
  ros__parameters:
    odom_topic: /robot_ns/odom
    controller_plugins:
      - FollowPath

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

확인:

```bash
ros2 param get /robot_ns/controller_server controller_plugins
ros2 param get /robot_ns/controller_server FollowPath.plugin
ros2 param get /robot_ns/controller_server FollowPath.critics
```

---

## 4. Global Costmap

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

핵심:

```text
저장 지도 + 실시간 scan + inflation을 사용해 planner가 볼 비용 지도를 만든다.
```

---

## 5. Local Costmap

```yaml
local_costmap:
  local_costmap:
    ros__parameters:
      global_frame: odom_robot_ns
      robot_base_frame: base_footprint
      rolling_window: true
      plugins:
        - obstacle_layer
        - inflation_layer
```

핵심:

```text
로봇 주변 rolling window에서 controller가 볼 비용 지도를 만든다.
```

---

## 6. BT Navigator

```yaml
bt_navigator:
  ros__parameters:
    global_frame: map_robot_ns
    robot_base_frame: base_footprint
    odom_topic: /robot_ns/odom
```

핵심:

```text
NavigateToPose action을 받고 planner/controller/recovery 절차를 관리한다.
```

---

## 7. 문제별 의심 parameter

| 증상 | 우선 확인 |
|---|---|
| `No critics defined for FollowPath` | `FollowPath.critics`, namespace, params_file |
| 경로 없음 | planner plugin, global costmap, map, goal 위치 |
| path는 있는데 속도 없음 | controller plugin, local costmap, odom, DWB |
| 목표 근처에서 실패 | goal checker tolerance |
| 장애물 너무 가까이 감 | inflation radius, robot radius |
| 로봇이 너무 느림 | max_vel_x, max_vel_theta, acc_lim |

