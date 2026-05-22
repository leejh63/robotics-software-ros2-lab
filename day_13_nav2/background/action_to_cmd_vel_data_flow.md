# NavigateToPose Action에서 /cmd_vel까지

이 문서는 Nav2 goal이 실제 속도 명령이 되는 흐름을 하나로 정리한다.

---

## 1. 시작점: NavigateToPose action

사용자가 goal을 보낸다.

```bash
ros2 action send_goal /robot_ns/navigate_to_pose nav2_msgs/action/NavigateToPose \
"{pose: {header: {frame_id: 'map_robot_ns'}, pose: {position: {x: 1.0, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}}"
```

이 goal은 `map_robot_ns` 기준 좌표다.

---

## 2. bt_navigator

`bt_navigator`는 action server 역할을 한다.

```text
/robot_ns/navigate_to_pose goal 수신
  -> Behavior Tree 실행
```

bt_navigator가 직접 바퀴를 제어하지는 않는다.

---

## 3. planner_server

BT의 `ComputePathToPose` 단계에서 planner_server가 호출된다.

입력:

```text
현재 위치
목표 위치
global costmap
```

출력:

```text
/robot_ns/plan
```

---

## 4. controller_server

BT의 `FollowPath` 단계에서 controller_server가 호출된다.

입력:

```text
/robot_ns/plan
/robot_ns/odom
local costmap
TF
```

출력:

```text
속도 명령
```

현재 구조에서는 최종적으로 `/robot_ns/cmd_vel` 흐름을 봐야 한다.

---

## 5. Gazebo diff_drive plugin

Gazebo의 diff_drive plugin은 `/robot_ns/cmd_vel`을 구독해서 로봇 모델을 움직인다.

로봇이 움직이면 다시 아래 데이터가 갱신된다.

```text
/robot_ns/odom
/robot_ns/tf
/robot_ns/scan
```

이 데이터는 다시 AMCL, costmap, controller로 들어간다.

---

## 6. 폐루프 구조

Nav2 주행은 일회성 명령이 아니다.

```text
goal
  -> path
  -> cmd_vel
  -> robot moves
  -> odom/scan/tf update
  -> AMCL/costmap update
  -> controller updates cmd_vel
```

이 폐루프가 계속 돌기 때문에 로봇이 경로를 따라갈 수 있다.

---

## 7. 어디서 끊겼는지 보는 법

```text
action goal 자체가 안 감
  /robot_ns/navigate_to_pose, bt_navigator 확인

/robot_ns/plan이 없음
  planner_server, global costmap, map, goal 위치 확인

/robot_ns/plan은 있는데 /robot_ns/cmd_vel이 없음
  controller_server, local costmap, odom, DWB 확인

/robot_ns/cmd_vel은 있는데 로봇 안 움직임
  Gazebo plugin, topic remap, teleop 충돌 확인
```

