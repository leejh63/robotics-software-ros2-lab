# 04. Navigation2 실행

## 1. 목표

저장된 지도 `tb3_map.yaml`을 사용해서 TurtleBot3 Navigation2를 실행한다.

지도 경로:

```bash
$TB3_WS/maps/tb3_map.yaml
```

## 2. 기존 노드 정리

Nav2를 실행하기 전에 이전에 띄운 개별 `map_server`, `amcl`, `lifecycle_manager`, `rviz2`가 남아 있으면 정리한다.

```bash
pkill -f rviz2
pkill -f map_server
pkill -f lifecycle_manager
pkill -f amcl
pkill -f static_transform_publisher
```

## 3. 터미널 1 — Gazebo 실행

```bash
cd "$TB3_WS"
source ~/envs/tb3_humble.bash

ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

## 4. 터미널 2 — Navigation2 실행

실제 참고 명령어:

```bash
ros2 launch turtlebot3_navigation2 navigation2.launch.py \
use_sim_time:=True \
map:=$TB3_WS/maps/tb3_map.yaml
```

이 명령은 TurtleBot3에서 제공하는 Navigation2 통합 런치 파일을 실행한다.

일반적으로 내부에서 다음 계층을 함께 실행한다.

```text
map_server
amcl
planner_server
controller_server
behavior_server / recoveries
bt_navigator
lifecycle_manager
```

따라서 Nav2 통합 런치 파일을 사용할 때는 별도로 `map_server`와 `amcl`을 중복 실행하지 않는 것이 좋다.

## 5. 터미널 3 — RViz 실행

Nav2 전용 RViz 설정을 사용할 수 있다.

```bash
rviz2 -d /opt/ros/humble/share/nav2_bringup/rviz/nav2_default_view.rviz \
--ros-args -p use_sim_time:=true
```

또는 기본 RViz:

```bash
rviz2 --ros-args -p use_sim_time:=true
```

RViz에서 확인:

```text
Fixed Frame: map
Map: /map
LaserScan: /scan
TF: enabled
PoseArray: /particlecloud
```

## 6. 초기 위치 설정

Nav2도 AMCL 기반이므로 초기 위치 설정이 필요하다.

RViz 상단:

```text
2D Pose Estimate
```

지도 위에서 로봇 위치와 방향을 지정한다.

또는 짧은 명령어:

```bash
ros2 topic pub --once /initialpose geometry_msgs/msg/PoseWithCovarianceStamped \
"{header: {frame_id: 'map'}, pose: {pose: {position: {x: 0.0, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}}"
```

## 7. 목표 위치 지정

RViz 상단:

```text
Navigation2 Goal
```

지도 위에서 목표 위치를 클릭하고, 도착 방향으로 드래그한다.

정상 동작 흐름:

```text
planner_server가 global path 생성
controller_server가 local control 수행
로봇이 목표 위치로 이동
```

## 8. 정상 확인

노드 확인:

```bash
ros2 node list | grep -E "map_server|amcl|planner|controller|bt_navigator"
```

AMCL pose 확인:

```bash
ros2 topic echo /amcl_pose --once
```

Nav2 action 확인:

```bash
ros2 action list | grep navigate
```

TF 확인:

```bash
ros2 run tf2_ros tf2_echo map odom
```

## 9. 주의

`navigation2.launch.py`를 사용할 때는 개별 `map_server`, `amcl`, `lifecycle_manager`를 따로 실행한 상태에서 겹치게 띄우지 않는다.

중복 실행하면 같은 노드 이름, 같은 lifecycle 관리, 같은 `/map`, `/amcl_pose` 등이 충돌하거나 헷갈릴 수 있다.
