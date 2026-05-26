# Nav2 Action Goal 직접 전송

이 문서는 AMCL 확인 이후 Nav2 goal을 CLI로 직접 전송해 localization과 navigation 연결 상태를 확인하는 방법을 정리한다.

---

## 1. 사용 기준

```text
Nav2 action server와 localization 연결을 CLI에서 직접 확인한다.
RViz Nav2 Goal 버튼은 robot_ns namespace 기준 추가 설정이 필요할 수 있다.
이 경우 `ros2 action send_goal` 명령으로 목표를 직접 보낸다.
```

확인할 연결:

```text
/robot_ns/navigate_to_pose
bt_navigator
planner_server
controller_server
global/local costmap
/robot_ns/cmd_vel
Gazebo diff_drive
```

---

## 2. 실행 순서

터미널 1:

```bash
cd $ROS2_WS
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 launch lee_robot_description nav2.launch.py
```

터미널 2:

```bash
cd $ROS2_WS
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 launch lee_robot_description nav2_navigation.launch.py
```

---

## 3. goal 직접 전송

```bash
ros2 action send_goal /robot_ns/navigate_to_pose nav2_msgs/action/NavigateToPose \
"{pose: {header: {frame_id: 'map_robot_ns'}, pose: {position: {x: 0.0, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}}"
```

성공 판단:

```text
action feedback이 나온다.
planner/controller가 동작한다.
/robot_ns/cmd_vel이 발행된다.
Gazebo 로봇이 움직인다.
```

---

## 4. RViz에서 좌표 얻기

RViz의 `Publish Point`를 사용한다.

```bash
ros2 topic echo /clicked_point
```

출력의 `point.x`, `point.y`를 action goal의 `x`, `y`에 넣는다.

---

## 5. 다음 단계로 넘길 문제

이 문서는 RViz 버튼 대신 action goal을 직접 보내는 검증 절차를 정리한다.

남은 문제:

```text
RViz Nav2 Goal 버튼과 robot_ns namespace 연결
behavior tree / planner / controller 설정 정리
costmap frame/topic 설정 정리
AMCL localization과 Nav2 navigation launch 분리 기준 정리
```
