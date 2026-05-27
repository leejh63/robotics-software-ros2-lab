# Gazebo → SLAM → AMCL → Nav2 검증 순서

이 문서는 전체 navigation pipeline을 확인할 때의 순서를 정리한다.

```text
뒤 단계가 안 되면 앞 단계를 먼저 확인한다.
Nav2가 안 된다고 바로 Nav2만 보지 않는다.
```

현재 `projects/ros2_navigation_lab` 기본 실행값:

```text
namespace  : /lee
map frame  : map_lee
odom frame : odom_lee
base frame : base_footprint
scan frame : base_scan
```

---

## 1. 전체 검증 순서

```text
1. workspace 빌드/환경 확인
2. Gazebo robot spawn 확인
3. sensor topic 확인
4. TF chain 확인
5. SLAM map 생성 확인
6. map save/load 확인
7. AMCL localization 확인
8. Nav2 lifecycle 확인
9. goal 전송 확인
10. /lee/cmd_vel과 robot motion 확인
```

---

## 2. workspace 환경 확인

```bash
cd $ROS2_WS
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 pkg list | grep lee_robot_description
```

패키지가 보이지 않으면 다시 빌드하고 환경을 source한다.

```bash
colcon build
source install/setup.bash
```

---

## 3. Gazebo robot 확인

```bash
ros2 launch lee_robot_description gazebo.launch.py
```

확인:

```bash
ros2 node list | sort
ros2 topic list | grep /lee
```

기대 topic:

```text
/lee/scan
/lee/odom
/lee/cmd_vel
/lee/tf
/lee/tf_static
```

---

## 4. sensor topic 확인

```bash
ros2 topic echo /lee/scan --once
ros2 topic echo /lee/odom --once
```

확인할 것:

```text
/lee/scan header.frame_id가 base_scan 계열인지
/lee/odom child_frame_id가 base_footprint/base_link 계열인지
ranges 값이 비어 있지 않은지
```

---

## 5. TF chain 확인

```bash
ros2 run tf2_ros tf2_echo odom_lee base_footprint \
  --ros-args -r /tf:=/lee/tf -r /tf_static:=/lee/tf_static

ros2 run tf2_ros tf2_echo base_footprint base_scan \
  --ros-args -r /tf:=/lee/tf -r /tf_static:=/lee/tf_static
```

SLAM/AMCL/Nav2에서는 최종적으로 아래 관계가 필요하다.

```text
map_lee -> odom_lee -> base_footprint -> base_scan
```

Gazebo만 실행한 상태에서는 `map_lee -> odom_lee`가 없을 수 있다. 이 관계는 보통 SLAM 또는 AMCL이 만든다.

---

## 6. SLAM 확인

```bash
ros2 launch lee_robot_description slam.launch.py
```

확인:

```bash
ros2 topic echo /lee/map --once
ros2 run tf2_ros tf2_echo map_lee odom_lee \
  --ros-args -r /tf:=/lee/tf -r /tf_static:=/lee/tf_static
```

기대 결과:

```text
/lee/map이 발행된다.
map_lee -> odom_lee TF가 생긴다.
RViz에서 map이 누적된다.
```

---

## 7. map 저장/로딩 확인

저장:

```bash
ros2 run nav2_map_server map_saver_cli -f slam_map --ros-args -r map:=/lee/map
```

확인:

```bash
ls -lh slam_map.yaml slam_map.pgm
cat slam_map.yaml
```

저장한 map은 AMCL/Nav2에서 사용하는 world와 맞아야 한다.

---

## 8. AMCL localization 확인

AMCL만 먼저 확인하려면 localization launch를 사용한다.

```bash
ros2 launch lee_robot_description localization.launch.py world:=slam.world
```

확인:

```bash
ros2 topic echo /lee/map --once
ros2 topic list | sort | grep -E 'initialpose|amcl_pose|particle_cloud'
ros2 run tf2_ros tf2_echo map_lee odom_lee \
  --ros-args -r /tf:=/lee/tf -r /tf_static:=/lee/tf_static
```

initial pose를 준 뒤 기대할 것:

```text
map_server가 /lee/map을 발행한다.
AMCL particle이 pose 주변으로 수렴한다.
AMCL이 map_lee -> odom_lee TF를 발행한다.
```

현재 launch 구조에서는 `map_server`와 `amcl` node 이름은 root namespace에 있을 수 있다. 실제 이름은 아래 명령으로 확인한다.

```bash
ros2 node list | sort | grep -E 'map_server|amcl'
ros2 topic list | sort | grep -E 'initialpose|amcl_pose|particle_cloud'
```

---

## 9. Nav2 실행 방식 선택

Nav2는 두 가지 방식 중 하나만 선택해서 실행한다. 같은 세션에서 중복 실행하지 않는다.

### 방식 A: localization + Nav2 통합 실행

```bash
ros2 launch lee_robot_description nav2.launch.py use_rviz:=false
```

### 방식 B: localization을 먼저 실행한 뒤 Nav2 stack만 실행

Terminal 1:

```bash
ros2 launch lee_robot_description localization.launch.py world:=slam.world
```

Terminal 2:

```bash
ros2 launch lee_robot_description nav2_navigation.launch.py
```

---

## 10. Nav2 lifecycle 확인

```bash
ros2 lifecycle nodes
ros2 lifecycle get /lee/planner_server
ros2 lifecycle get /lee/controller_server
ros2 lifecycle get /lee/bt_navigator
```

Localization 쪽은 다음처럼 확인한다.

```bash
ros2 lifecycle get /map_server
ros2 lifecycle get /amcl
```

기대 결과:

```text
map_server, amcl, planner_server, controller_server, bt_navigator 등이 active 상태여야 한다.
```

---

## 11. goal 전송 확인

```bash
ros2 action info /lee/navigate_to_pose
```

CLI goal 예시:

```bash
ros2 action send_goal /lee/navigate_to_pose nav2_msgs/action/NavigateToPose \
"{pose: {header: {frame_id: 'map_lee'}, pose: {position: {x: 1.0, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}}"
```

확인:

```bash
ros2 topic echo /lee/plan --once
ros2 topic echo /lee/cmd_vel
```

---

## 12. robot motion 확인

Gazebo에서 로봇이 움직이지 않으면 아래를 확인한다.

```bash
ros2 topic info /lee/cmd_vel
ros2 topic echo /lee/cmd_vel
ros2 node info /lee/controller_server
```

가능한 원인:

```text
- controller_server가 cmd_vel을 발행하지 않음
- diff_drive plugin이 /lee/cmd_vel을 subscribe하지 않음
- obstacle/costmap 때문에 controller가 속도 후보를 모두 거부함
- TF chain이 끊김
- robot이 이미 goal tolerance 안에 있다고 판단함
```

---

## 13. 실패 위치별 해석

| 실패 위치 | 의미 |
|---|---|
| `/lee/scan` 없음 | Gazebo sensor plugin 또는 launch 문제 |
| `/lee/odom` 없음 | diff_drive plugin 또는 robot spawn 문제 |
| `odom_lee -> base_footprint` 없음 | odom TF 또는 robot_state_publisher 문제 |
| `/lee/map` 없음 | SLAM/map_server lifecycle 문제 |
| `map_lee -> odom_lee` 없음 | SLAM 또는 AMCL localization 문제 |
| `/lee/navigate_to_pose` 없음 | Nav2 launch/namespace/lifecycle 문제 |
| `/lee/plan` 없음 | planner/costmap/map/TF 문제 |
| `/lee/cmd_vel` 없음 | controller/costmap/goal/TF 문제 |
| `/lee/cmd_vel` 있는데 robot 안 움직임 | Gazebo diff_drive plugin topic 연결 문제 |
