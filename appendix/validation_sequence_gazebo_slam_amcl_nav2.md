# Validation Sequence - Gazebo -> SLAM -> AMCL -> Nav2

이 문서는 전체 navigation pipeline을 확인할 때의 순서를 정리한 것이다.

핵심 원칙:

```text
뒤 단계가 안 되면 앞 단계를 먼저 확인한다.
Nav2가 안 된다고 바로 Nav2만 보지 않는다.
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
10. /robot_ns/cmd_vel과 robot motion 확인
```

---

## 2. 1단계 - workspace 환경 확인

```bash
cd $ROS2_WS
source install/setup.bash
ros2 pkg list | grep lee_robot_description
```

정상 기대:

```text
lee_robot_description 패키지가 보여야 한다.
```

안 보이면:

```bash
colcon build
source install/setup.bash
```

---

## 3. 2단계 - Gazebo robot 확인

```bash
ros2 launch lee_robot_description gaze.launch.py
```

확인:

```bash
ros2 node list | sort
ros2 topic list | grep /robot_ns
```

정상 기대:

```text
/robot_ns/scan
/robot_ns/odom
/robot_ns/cmd_vel
/robot_ns/tf
/robot_ns/tf_static
```

---

## 4. 3단계 - sensor topic 확인

```bash
ros2 topic echo /robot_ns/scan --once
ros2 topic echo /robot_ns/odom --once
```

확인할 것:

```text
/robot_ns/scan header.frame_id가 base_scan 계열인지
/robot_ns/odom child_frame_id가 base_footprint/base_link 계열인지
거리값 ranges가 비어 있지 않은지
```

---

## 5. 4단계 - TF chain 확인

```bash
ros2 run tf2_ros tf2_echo odom_robot_ns base_footprint
ros2 run tf2_ros tf2_echo base_footprint base_scan
```

SLAM/AMCL/Nav2에서는 최종적으로 아래 관계가 필요하다.

```text
map_robot_ns -> odom_robot_ns -> base_footprint -> base_scan
```

초기 Gazebo만 실행한 상태에서는 `map_robot_ns -> odom_robot_ns`가 없을 수 있다.  
이 관계는 SLAM 또는 AMCL이 담당하는 경우가 많다.

---

## 6. 5단계 - SLAM 확인

```bash
ros2 launch lee_robot_description slam.launch.py
```

확인:

```bash
ros2 topic echo /robot_ns/map --once
ros2 run tf2_ros tf2_echo map_robot_ns odom_robot_ns
```

정상 기대:

```text
/robot_ns/map이 발행된다.
map_robot_ns -> odom_robot_ns TF가 생긴다.
RViz에서 map이 누적된다.
```

---

## 7. 6단계 - map 저장/로딩 확인

저장:

```bash
ros2 run nav2_map_server map_saver_cli -f slam_map --ros-args -r map:=/robot_ns/map
```

확인:

```bash
ls -lh slam_map.yaml slam_map.pgm
cat slam_map.yaml
```

저장된 map은 AMCL/Nav2에서 사용하는 world와 맞아야 한다.

---

## 8. 7단계 - AMCL 확인

```bash
ros2 launch lee_robot_description nav2.launch.py
```

확인:

```bash
ros2 topic echo /robot_ns/map --once
ros2 topic echo /amcl_pose --once
ros2 topic echo /particle_cloud --once
ros2 run tf2_ros tf2_echo map_robot_ns odom_robot_ns
```

정상 기대:

```text
map_server가 map을 발행한다.
initialpose 이후 particle이 수렴한다.
AMCL이 map_robot_ns -> odom_robot_ns TF를 발행한다.
```

---

## 9. 8단계 - Nav2 lifecycle 확인

```bash
ros2 launch lee_robot_description nav2_navigation.launch.py
```

확인:

```bash
ros2 lifecycle nodes
ros2 lifecycle get /robot_ns/planner_server
ros2 lifecycle get /robot_ns/controller_server
ros2 lifecycle get /robot_ns/bt_navigator
```

정상 기대:

```text
planner_server, controller_server, bt_navigator 등이 active 상태여야 한다.
```

---

## 10. 9단계 - goal 전송 확인

```bash
ros2 action info /robot_ns/navigate_to_pose
```

CLI goal:

```bash
ros2 action send_goal /robot_ns/navigate_to_pose nav2_msgs/action/NavigateToPose \
"{pose: {header: {frame_id: 'map_robot_ns'}, pose: {position: {x: 1.0, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}}"
```

확인:

```bash
ros2 topic echo /robot_ns/plan --once
ros2 topic echo /robot_ns/cmd_vel
```

---

## 11. 10단계 - robot motion 확인

Gazebo에서 로봇이 움직이지 않으면 아래를 확인한다.

```bash
ros2 topic info /robot_ns/cmd_vel
ros2 topic echo /robot_ns/cmd_vel
ros2 node info /robot_ns/controller_server
```

가능한 원인:

```text
- controller_server가 cmd_vel을 발행하지 않음
- diff_drive plugin이 /robot_ns/cmd_vel을 subscribe하지 않음
- obstacle/costmap 때문에 controller가 속도 후보를 모두 거부함
- TF chain이 끊김
- robot이 이미 goal tolerance 안에 있다고 판단함
```

---

## 12. 실패 위치별 해석

| 실패 위치 | 의미 |
|---|---|
| `/robot_ns/scan` 없음 | Gazebo sensor plugin 또는 launch 문제 |
| `/robot_ns/odom` 없음 | diff_drive plugin 또는 robot spawn 문제 |
| `odom_robot_ns -> base_footprint` 없음 | odom TF 또는 robot_state_publisher 문제 |
| `/robot_ns/map` 없음 | SLAM/map_server lifecycle 문제 |
| `map_robot_ns -> odom_robot_ns` 없음 | SLAM 또는 AMCL localization 문제 |
| `/robot_ns/navigate_to_pose` 없음 | Nav2 launch/namespace/lifecycle 문제 |
| `/robot_ns/plan` 없음 | planner/costmap/map/TF 문제 |
| `/robot_ns/cmd_vel` 없음 | controller/costmap/goal/TF 문제 |
| `/robot_ns/cmd_vel` 있는데 robot 안 움직임 | Gazebo diff_drive plugin topic 연결 문제 |
