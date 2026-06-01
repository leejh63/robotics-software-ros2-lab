# Navigation Runtime Session Guide

이 문서는 `projects/ros2_navigation_lab`을 실제 ROS2 Humble + Gazebo Classic + Nav2 환경에서 검증할 때 쓰는 터미널별 실행 순서입니다. `RUNTIME_VALIDATION_CHECKLIST.md`가 통과 기준이라면, 이 문서는 그 기준을 확인하기 위한 실행 세션 절차입니다.

정적 검증을 통과해도 아래 항목은 runtime에서만 확정합니다.

```text
Gazebo spawn 안정성
LaserScan / Odometry publish 여부
TF tree 연결 여부
SLAM map publish 여부
AMCL lifecycle / pose publish 여부
Nav2 namespace / lifecycle / costmap / action server 상태
Nav2 goal 이후 /lee/cmd_vel publish 여부
```

결과를 README에 성공으로 적기 전에는 루트의 [`RUNTIME_VALIDATION_RESULT_TEMPLATE.md`](../../../RUNTIME_VALIDATION_RESULT_TEMPLATE.md)에 실제 명령, 날짜, 환경, 관찰 결과를 남깁니다.

---

## 0. 공통 준비

모든 터미널은 workspace root인 `projects/ros2_navigation_lab`에서 시작한다고 가정합니다.

```bash
cd projects/ros2_navigation_lab
source /opt/ros/humble/setup.bash
```

처음 한 번 build합니다.

```bash
rosdep install --from-paths src -y --ignore-src
colcon build --symlink-install
source install/setup.bash
ros2 pkg prefix lee_robot_description
```

권장 로그 디렉토리입니다. 이 디렉토리는 runtime 산출물이므로 commit하지 않습니다.

```bash
mkdir -p runtime_logs/navigation_$(date +%Y%m%d_%H%M%S)
```

---

## 1. Gazebo sensor smoke test

### Terminal A: Gazebo 실행

```bash
cd projects/ros2_navigation_lab
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch lee_robot_description gazebo.launch.py world:=slam.world use_avoidance:=false
```

### Terminal B: topic / TF 확인

```bash
cd projects/ros2_navigation_lab
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 topic echo /lee/scan --once
ros2 topic echo /lee/odom --once
ros2 run tf2_ros tf2_echo odom_lee base_footprint --ros-args -r /tf:=/lee/tf -r /tf_static:=/lee/tf_static
```

기록할 것:

```text
/lee/scan publish 여부:
/lee/odom publish 여부:
odom_lee -> base_footprint TF 조회 여부:
Gazebo console error:
```

---

## 2. SLAM workflow

### Terminal A: SLAM 포함 Gazebo 실행

```bash
cd projects/ros2_navigation_lab
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch lee_robot_description gazebo_slam.launch.py world:=slam.world
```

### Terminal B: SLAM 결과 확인

```bash
cd projects/ros2_navigation_lab
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 topic echo /lee/map --once --qos-durability transient_local
ros2 run tf2_ros tf2_echo map_lee odom_lee --ros-args -r /tf:=/lee/tf -r /tf_static:=/lee/tf_static
ros2 run tf2_ros tf2_echo odom_lee base_footprint --ros-args -r /tf:=/lee/tf -r /tf_static:=/lee/tf_static
```

기록할 것:

```text
/lee/map OccupancyGrid publish 여부:
map_lee -> odom_lee TF 조회 여부:
map 저장 필요 여부:
```

---

## 3. Localization / AMCL workflow

### Terminal A: localization 실행

```bash
cd projects/ros2_navigation_lab
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch lee_robot_description localization.launch.py world:=slam.world
```

### Terminal B: initial pose 지정

RViz에서 `2D Pose Estimate`를 사용하는 것이 가장 안전합니다. CLI로 최소 확인만 할 때는 다음 예시를 사용합니다.

```bash
cd projects/ros2_navigation_lab
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 topic pub --once /initialpose geometry_msgs/msg/PoseWithCovarianceStamped "
header:
  frame_id: 'map_lee'
pose:
  pose:
    position:
      x: 0.0
      y: 0.0
      z: 0.0
    orientation:
      x: 0.0
      y: 0.0
      z: 0.0
      w: 1.0
  covariance:
  - 0.25
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.25
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0685
"
```

### Terminal C: lifecycle / pose 확인

```bash
cd projects/ros2_navigation_lab
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 lifecycle get /map_server
ros2 lifecycle get /amcl
ros2 topic echo /amcl_pose --once
ros2 topic echo /particle_cloud --once
ros2 run tf2_ros tf2_echo map_lee odom_lee --ros-args -r /tf:=/lee/tf -r /tf_static:=/lee/tf_static
```

기록할 것:

```text
map_server lifecycle:
amcl lifecycle:
/amcl_pose publish 여부:
/particle_cloud publish 여부:
map_lee -> odom_lee TF 안정성:
```

---

## 4. Nav2 integrated workflow

`nav2.launch.py`는 localization과 Nav2 stack을 함께 실행합니다. 이미 `localization.launch.py`를 켜 둔 상태에서 중복 실행하지 않습니다.

### Terminal A: Nav2 통합 실행

```bash
cd projects/ros2_navigation_lab
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch lee_robot_description nav2.launch.py use_rviz:=false
```

### Terminal B: initial pose 지정

RViz의 `2D Pose Estimate`를 우선 사용합니다. headless 확인에서는 3장의 CLI initial pose 예시를 사용합니다.

### Terminal C: Nav2 node / lifecycle / costmap 확인

```bash
cd projects/ros2_navigation_lab
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 node list | sort | grep controller_server
ros2 node list | sort | grep planner_server
ros2 node list | sort | grep bt_navigator
ros2 lifecycle get /lee/controller_server
ros2 lifecycle get /lee/planner_server
ros2 lifecycle get /lee/bt_navigator
ros2 topic echo /lee/global_costmap/costmap --once --qos-durability transient_local
ros2 topic echo /lee/local_costmap/costmap --once --qos-durability transient_local
ros2 action list | grep navigate_to_pose
```

### Terminal D: goal과 cmd_vel 확인

```bash
cd projects/ros2_navigation_lab
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 action send_goal /lee/navigate_to_pose nav2_msgs/action/NavigateToPose "{pose: {header: {frame_id: 'map_lee'}, pose: {position: {x: 0.5, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}}"
ros2 topic echo /lee/cmd_vel --once
```

기록할 것:

```text
Nav2 node namespace가 /lee 아래인지:
/lee/lee 중복 namespace가 없는지:
controller/planner/bt_navigator lifecycle:
global/local costmap publish 여부:
/lee/navigate_to_pose action server 여부:
goal 전송 결과:
/lee/cmd_vel publish 여부:
```

---

## 5. Nav2 분리 workflow

이미 localization이 실행 중이고 initial pose가 지정된 상태에서 Nav2 stack만 확인할 때 사용합니다.

### Terminal A: localization 유지

```bash
ros2 launch lee_robot_description localization.launch.py world:=slam.world
```

### Terminal B: Nav2 stack만 실행

```bash
cd projects/ros2_navigation_lab
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch lee_robot_description nav2_navigation.launch.py
```

이 모드에서도 4장의 namespace/lifecycle/costmap/goal 확인을 그대로 수행합니다.

---

## 6. Rosbag workflow 확인

rosbag은 closed-loop 주행 성공 검증이 아니라 replay 기반 SLAM/localization/costmap 확인입니다. replay 중 Nav2가 `/lee/cmd_vel`을 publish하더라도 rosbag 내부 로봇 pose가 새 명령으로 바뀌지는 않습니다.

```bash
export BAG_DIR=/path/to/rosbag_directory
ros2 bag info "$BAG_DIR"
```

상세 명령은 다음 문서를 사용합니다.

```text
docs/BAG_SLAM_NAV2_WORKFLOW.md
docs/BAG_COMMANDS_ONLY.md
```

기록할 것:

```text
bag metadata 확인 여부:
사용한 replay mode: /lee remap mode / raw topic mode
bag_slam_map.yaml 생성 여부:
rosbag 내부 frame: odom / 기타
closed-loop 성공으로 표현하지 않았는지:
```

---

## 7. 실패 시 중단 기준

아래 상태에서는 다음 단계로 넘어가지 않습니다.

```text
/lee/scan이 나오지 않음 → SLAM/AMCL/Nav2 확인 중단
odom_lee -> base_footprint TF가 안 나옴 → AMCL/Nav2 확인 중단
map_lee -> odom_lee TF가 안 나옴 → Nav2 goal 확인 중단
Nav2 lifecycle이 active가 아님 → goal 성공 claim 금지
costmap이 publish되지 않음 → planner/controller 성공 claim 금지
/lee/cmd_vel이 안 나옴 → navigation 성공 claim 금지
```
