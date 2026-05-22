# 06. RViz, Nav2 검증, Debug

Day 13에서 중요한 점은 RViz가 실패했다고 해서 Nav2 전체가 실패했다고 단정하면 안 된다는 것이다.

```text
RViz는 시각화/입력 도구다.
Nav2의 실제 동작은 topic, action, lifecycle, TF, costmap으로 확인해야 한다.
```

---

## 1. RViz에서 확인할 것

RViz에서 최소한 아래 항목을 확인한다.

```text
Fixed Frame: map_robot_ns
Map: /robot_ns/map
RobotModel: /robot_ns/robot_description 또는 robot_description 설정 확인
TF: map_robot_ns -> odom_robot_ns -> base_footprint -> base_scan
LaserScan: /robot_ns/scan
AMCL Pose: /amcl_pose
ParticleCloud: /particle_cloud
Global Costmap: /robot_ns/global_costmap/costmap
Local Costmap: /robot_ns/local_costmap/costmap
Plan: /robot_ns/plan
```

Fixed Frame이 `map`으로 되어 있으면 현재 환경의 `map_robot_ns`와 맞지 않는다.  
이 경우 RViz에서 데이터가 안 보이거나 frame transform 에러가 뜰 수 있다.

---

## 2. RViz Goal 버튼과 CLI action goal 차이

현재 기록 기준으로는 `/robot_ns/navigate_to_pose` action goal을 CLI로 보내면 주행이 확인되었다.

하지만 RViz Nav2 Goal 버튼은 namespace 연결 문제로 실패할 수 있다.

이 말은 아래처럼 해석해야 한다.

```text
CLI action goal 성공
  Nav2 서버, planner/controller, costmap, TF는 대체로 동작할 가능성이 높음

RViz Goal 버튼 실패
  RViz Navigation2 panel 설정, namespace, action 이름 연결 문제일 가능성이 높음
```

즉, RViz 버튼 실패만 보고 Nav2 전체를 고치려고 하면 안 된다.

---

## 3. CLI 기준 검증 순서

Nav2가 진짜 동작하는지 확인하려면 아래 순서가 더 확실하다.

```bash
ros2 action list | grep navigate
ros2 action info /robot_ns/navigate_to_pose
ros2 lifecycle get /robot_ns/bt_navigator
ros2 lifecycle get /robot_ns/planner_server
ros2 lifecycle get /robot_ns/controller_server
```

그 다음 goal 전송:

```bash
ros2 action send_goal /robot_ns/navigate_to_pose nav2_msgs/action/NavigateToPose \
"{pose: {header: {frame_id: 'map_robot_ns'}, pose: {position: {x: 1.0, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}}"
```

그리고 결과 확인:

```bash
ros2 topic echo /robot_ns/plan --once
ros2 topic echo /robot_ns/cmd_vel
```

---

## 4. RViz에서 goal 좌표만 얻는 방법

RViz의 Nav2 Goal 버튼이 안 맞을 때도, `Publish Point`는 좌표 확인용으로 쓸 수 있다.

```bash
ros2 topic echo /clicked_point
```

RViz에서 자유 공간을 클릭하면 아래처럼 좌표가 나온다.

```text
point:
  x: 1.23
  y: -0.45
  z: 0.0
```

이 값을 CLI action goal에 넣는다.

---

## 5. Fixed Frame 문제

현재 환경 기준 frame은 아래다.

```text
map_robot_ns
odom_robot_ns
base_footprint
base_scan
```

따라서 RViz Fixed Frame은 보통 `map_robot_ns`가 되어야 한다.

확인:

```bash
ros2 run tf2_ros tf2_echo map_robot_ns odom_robot_ns
ros2 run tf2_ros tf2_echo odom_robot_ns base_footprint
```

TF가 없으면 RViz display를 아무리 추가해도 제대로 보이지 않는다.

---

## 6. RViz에 costmap이 안 보일 때

먼저 topic이 실제로 있는지 확인한다.

```bash
ros2 topic list | grep costmap
```

확인:

```bash
ros2 topic echo /robot_ns/global_costmap/costmap --once
ros2 topic echo /robot_ns/local_costmap/costmap --once
```

topic은 있는데 RViz에 안 보이면 RViz display 설정 문제일 수 있다.  
topic 자체가 없으면 Nav2 서버/lifecycle/parameter 문제를 봐야 한다.

---

## 7. Debug를 나누는 기준

```text
RViz에 안 보임
  RViz Fixed Frame, display topic, QoS, TF 확인

action server 없음
  bt_navigator, namespace, lifecycle 확인

goal accepted 후 plan 없음
  planner_server, global costmap, goal 위치 확인

plan은 있는데 cmd_vel 없음
  controller_server, local costmap, DWB 설정 확인

cmd_vel은 있는데 로봇 안 움직임
  Gazebo plugin, cmd_vel remap, teleop 충돌, Gazebo pause 확인
```

이렇게 단계별로 잘라야 시간을 덜 낭비한다.

