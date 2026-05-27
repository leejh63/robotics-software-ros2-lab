# 05. 실행 분리와 Goal 전송

Day 13에서는 실행을 두 단계로 나눠서 보는 것이 좋다.

```text
1단계: simulation + localization
2단계: navigation
```

이렇게 해야 문제가 생겼을 때 어디서 막혔는지 분리할 수 있다.

---

## 1. 공통 준비

```bash
cd $ROS2_WS
source /opt/ros/humble/setup.bash
colcon build --symlink-install --packages-select lee_robot_description
source install/setup.bash
```

현재 프로젝트 기준 실제 실행 예시는 `/lee`, `map_lee`, `odom_lee`를 사용한다.
`/robot_ns`, `map_robot_ns`, `odom_robot_ns`는 일반 namespace/frame 설명용 placeholder로만 사용한다.

---

## 2. 터미널 1 - Gazebo + Map + AMCL

```bash
ros2 launch lee_robot_description localization.launch.py
```

이 launch는 다음을 실행한다.

```text
Gazebo
robot_state_publisher
spawn_entity.py
map_server
amcl
lifecycle_manager_localization
RViz
```

전체를 한 번에 실행하려면 아래 통합 wrapper를 단독으로 사용한다.

```bash
ros2 launch lee_robot_description nav2.launch.py
```

`nav2.launch.py`는 `localization.launch.py`와 `nav2_navigation.launch.py`를 함께 include하므로, 통합 실행 뒤에 `nav2_navigation.launch.py`를 다시 실행하지 않는다.

명시적으로 world와 map을 지정하고 싶으면:

```bash
ros2 launch lee_robot_description localization.launch.py \
  world:=slam.world \
  map_yaml:=$ROS2_WS/slam_map.yaml
```

`lee_world.world`를 쓰는 경우에는 map도 맞춰야 한다.

```bash
ros2 launch lee_robot_description localization.launch.py \
  world:=lee_world.world \
  map_yaml:=$ROS2_WS/room_map.yaml
```

---

## 3. 터미널 1 실행 후 확인

새 터미널에서:

```bash
cd $ROS2_WS
source /opt/ros/humble/setup.bash
source install/setup.bash
```

확인:

```bash
ros2 topic echo /lee/map --once
ros2 topic hz /lee/scan
ros2 topic echo /lee/odom --once
ros2 topic echo /amcl_pose --once
ros2 run tf2_ros tf2_echo map_lee odom_lee --ros-args -r /tf:=/lee/tf -r /tf_static:=/lee/tf_static
ros2 run tf2_ros tf2_echo odom_lee base_footprint --ros-args -r /tf:=/lee/tf -r /tf_static:=/lee/tf_static
```

RViz에서 `2D Pose Estimate`를 찍어서 초기 위치를 맞춘다.  
초기 위치가 틀리면 Nav2가 아무리 정상이어도 주행이 이상해질 수 있다.

---

## 4. 터미널 2 - Navigation Stack

```bash
cd $ROS2_WS
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 launch lee_robot_description nav2_navigation.launch.py
```

이 launch는 `nav2_bringup`의 navigation stack을 `/lee` namespace로 올린다.

> 이 파일은 공식 `nav2_bringup/launch/navigation_launch.py`를 바로 실행하지 않고, 먼저 `PushRosNamespace(lee)`를 적용한 뒤 include하는 구조를 기준으로 한다. 이렇게 해야 `controller_server`, `planner_server`, `bt_navigator` 같은 Nav2 서버 노드가 `/lee` 아래에 생성되고, `nav2_params.yaml`의 namespace 구조와 실제 node namespace가 맞는다. 관련 오류 사례는 [`troubleshooting/nav2_day13_troubleshooting.md`](troubleshooting/nav2_day13_troubleshooting.md)의 `No critics defined for FollowPath` 항목을 참고한다.

---

## 5. Navigation 실행 후 확인

노드:

```bash
ros2 node list | grep -E "planner|controller|bt_navigator|behavior|smoother|waypoint|velocity|lifecycle"
```

lifecycle:

```bash
ros2 lifecycle get /lee/planner_server
ros2 lifecycle get /lee/controller_server
ros2 lifecycle get /lee/bt_navigator
ros2 lifecycle get /lee/behavior_server
```

정상:

```text
active [3]
```

Action:

```bash
ros2 action list | grep navigate
ros2 action info /lee/navigate_to_pose
```

정상 후보:

```text
/lee/navigate_to_pose
/lee/navigate_through_poses
```

---

## 6. CLI로 goal 보내기

기본 goal:

```bash
ros2 action send_goal /lee/navigate_to_pose nav2_msgs/action/NavigateToPose \
"{pose: {header: {frame_id: 'map_lee'}, pose: {position: {x: 0.0, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}}"
```

좌표 지정 goal:

```bash
ros2 action send_goal /lee/navigate_to_pose nav2_msgs/action/NavigateToPose \
"{pose: {header: {frame_id: 'map_lee'}, pose: {position: {x: 1.2, y: -0.8, z: 0.0}, orientation: {w: 1.0}}}}"
```

방향까지 지정하려면 quaternion을 넣어야 한다.  
단순 실습에서는 우선 `orientation: {w: 1.0}`으로 시작해도 된다.

---

## 7. goal 전송 후 봐야 할 topic

```bash
ros2 topic echo /lee/plan --once
ros2 topic echo /lee/cmd_vel
ros2 topic echo /lee/global_costmap/costmap --once
ros2 topic echo /lee/local_costmap/costmap --once
```

판단:

```text
/lee/plan이 생김
  planner_server는 일단 동작

/lee/cmd_vel이 생김
  controller_server가 속도 명령 생성

/lee/cmd_vel이 있는데 로봇이 안 움직임
  Gazebo plugin, topic 충돌, pause 상태 확인
```

---

## 8. RViz 좌표를 CLI goal로 쓰는 방법

RViz에서 `Publish Point` 도구를 사용할 수 있다.

```bash
ros2 topic echo /clicked_point
```

RViz 지도에서 자유 공간을 클릭하고 나온 `point.x`, `point.y`를 action goal의 position에 넣는다.

이 방식은 RViz Nav2 Goal 버튼이 namespace 문제로 잘 안 될 때도 좌표를 얻는 데 유용하다.

---

## 9. teleop과 Nav2 충돌 확인

자율주행 중에는 teleop을 꺼두는 게 좋다.

```bash
ros2 topic info /lee/cmd_vel -v
```

`/lee/cmd_vel`에 여러 publisher가 붙어 있으면 누가 속도 명령을 내는지 확인해야 한다.

```text
Nav2 controller/velocity_smoother
teleop
wall follower
직접 만든 test publisher
```

이런 노드들이 동시에 속도를 내면 로봇이 이상하게 움직일 수 있다.
