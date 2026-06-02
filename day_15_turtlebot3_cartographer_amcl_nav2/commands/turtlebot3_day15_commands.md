# TurtleBot3 Day 15 명령어 모음

설명 없이 실제 실행 명령어만 모은 문서이다.


## 경로 표기 기준

문서에서는 개인 경로를 직접 쓰지 않고 아래 변수로 워크스페이스를 표현한다.

```bash
# 예시: 사용자의 실제 TurtleBot3 워크스페이스 경로로 지정한다.
export TB3_WS=~/turtlebot3_ws
cd "$TB3_WS"
source ~/envs/tb3_humble.bash
```

## 1. 공통 환경 적용

```bash
cd "$TB3_WS"
source ~/envs/tb3_humble.bash
```

## 빠른 흐름: Cartographer -> map_saver_cli -> Navigation2

### 터미널 1 — Gazebo

```bash
cd "$TB3_WS"
source ~/envs/tb3_humble.bash
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

### 터미널 2 — Cartographer

```bash
cd "$TB3_WS"
source ~/envs/tb3_humble.bash
ros2 launch turtlebot3_cartographer cartographer.launch.py use_sim_time:=True
```

### 터미널 3 — Teleop

```bash
cd "$TB3_WS"
source ~/envs/tb3_humble.bash
ros2 run turtlebot3_teleop teleop_keyboard
```

### 터미널 4 — map_saver_cli

```bash
cd "$TB3_WS"
source ~/envs/tb3_humble.bash
mkdir -p "$TB3_WS/maps"
ros2 run nav2_map_server map_saver_cli -f "$TB3_WS/maps/tb3_map"
```

### 터미널 2 종료 후 — Navigation2

```bash
pkill -f cartographer
pkill -f teleop_keyboard

cd "$TB3_WS"
source ~/envs/tb3_humble.bash
ros2 launch turtlebot3_navigation2 navigation2.launch.py \
use_sim_time:=True \
map:="$TB3_WS/maps/tb3_map.yaml"
```

### RViz

```text
Fixed Frame = map
2D Pose Estimate
Navigation2 Goal
```

## 2. SLAM 지도 만들기

### 터미널 1 — Gazebo

```bash
cd "$TB3_WS"
source ~/envs/tb3_humble.bash
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

### 터미널 2 — Cartographer

```bash
cd "$TB3_WS"
source ~/envs/tb3_humble.bash
ros2 launch turtlebot3_cartographer cartographer.launch.py use_sim_time:=True
```

### 터미널 3 — Teleop

```bash
cd "$TB3_WS"
source ~/envs/tb3_humble.bash
ros2 run turtlebot3_teleop teleop_keyboard
```

### 터미널 4 — 지도 저장

```bash
cd "$TB3_WS"
source ~/envs/tb3_humble.bash
mkdir -p "$TB3_WS/maps"

ros2 service call /write_state cartographer_ros_msgs/srv/WriteState \
"{filename: '$TB3_WS/maps/tb3_map.pbstream'}"

ros2 run cartographer_ros cartographer_pbstream_to_ros_map \
-pbstream_filename $TB3_WS/maps/tb3_map.pbstream \
-map_filestem $TB3_WS/maps/tb3_map \
-resolution 0.05
```

## 3. map_server 단독 확인

### 터미널 1 — map_server

```bash
cd "$TB3_WS"
source ~/envs/tb3_humble.bash

ros2 run nav2_map_server map_server \
--ros-args -p yaml_filename:=$TB3_WS/maps/tb3_map.yaml -p use_sim_time:=True
```

### 터미널 2 — lifecycle_manager

```bash
cd "$TB3_WS"
source ~/envs/tb3_humble.bash

ros2 run nav2_lifecycle_manager lifecycle_manager \
--ros-args -p node_names:='["map_server"]' -p autostart:=True -p use_sim_time:=True
```

### 확인

```bash
ros2 lifecycle get /map_server

ros2 topic echo /map nav_msgs/msg/OccupancyGrid --once \
--qos-durability transient_local \
--qos-reliability reliable
```

## 4. AMCL 실행

### 기존 노드 정리

```bash
pkill -f rviz2
pkill -f map_server
pkill -f lifecycle_manager
pkill -f amcl
pkill -f static_transform_publisher
```

### 터미널 1 — Gazebo

```bash
cd "$TB3_WS"
source ~/envs/tb3_humble.bash
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

### 터미널 2 — map_server

```bash
cd "$TB3_WS"
source ~/envs/tb3_humble.bash

ros2 run nav2_map_server map_server \
--ros-args \
-p yaml_filename:=$TB3_WS/maps/tb3_map.yaml \
-p use_sim_time:=true
```

### 터미널 3 — AMCL

```bash
cd "$TB3_WS"
source ~/envs/tb3_humble.bash

ros2 run nav2_amcl amcl \
--ros-args \
-p use_sim_time:=true \
-p base_frame_id:=base_footprint \
-p odom_frame_id:=odom \
-p global_frame_id:=map \
-p robot_model_type:=nav2_amcl::DifferentialMotionModel
```

### 터미널 4 — lifecycle_manager

```bash
cd "$TB3_WS"
source ~/envs/tb3_humble.bash

ros2 run nav2_lifecycle_manager lifecycle_manager \
--ros-args \
-p node_names:='["map_server", "amcl"]' \
-p autostart:=true \
-p use_sim_time:=true
```

### 터미널 5 — RViz

```bash
cd "$TB3_WS"
source ~/envs/tb3_humble.bash
rviz2 --ros-args -p use_sim_time:=true
```

### 초기 위치 짧은 명령

```bash
ros2 topic pub --once /initialpose geometry_msgs/msg/PoseWithCovarianceStamped \
"{header: {frame_id: 'map'}, pose: {pose: {position: {x: 0.0, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}}"
```

### 확인

```bash
ros2 topic echo /amcl_pose --once
ros2 run tf2_ros tf2_echo map odom
```

## 5. Navigation2 실행

### 기존 노드 정리

```bash
pkill -f rviz2
pkill -f map_server
pkill -f lifecycle_manager
pkill -f amcl
pkill -f static_transform_publisher
```

### 터미널 1 — Gazebo

```bash
cd "$TB3_WS"
source ~/envs/tb3_humble.bash
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

### 터미널 2 — Navigation2

```bash
cd "$TB3_WS"
source ~/envs/tb3_humble.bash

ros2 launch turtlebot3_navigation2 navigation2.launch.py \
use_sim_time:=True \
map:=$TB3_WS/maps/tb3_map.yaml
```

### 터미널 3 — RViz

```bash
rviz2 -d /opt/ros/humble/share/nav2_bringup/rviz/nav2_default_view.rviz \
--ros-args -p use_sim_time:=true
```

### 초기 위치

```bash
ros2 topic pub --once /initialpose geometry_msgs/msg/PoseWithCovarianceStamped \
"{header: {frame_id: 'map'}, pose: {pose: {position: {x: 0.0, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}}"
```


## 6. Explore Lite 자동 탐색

### 패키지 추가

```bash
cd "$TB3_WS/src"
git clone https://github.com/robo-friends/m-explore-ros2
cd m-explore-ros2
# 최종 실행 검증 후에는 테스트한 commit으로 고정한다.
# git checkout <tested_commit_hash>

cd "$TB3_WS"
rosdep install --from-paths src -y --ignore-src
colcon build --symlink-install
source ~/envs/tb3_humble.bash
```

### 기존 노드 정리

```bash
pkill -f rviz2
pkill -f map_server
pkill -f lifecycle_manager
pkill -f amcl
pkill -f static_transform_publisher
pkill -f slam_toolbox
pkill -f explore
```

### 터미널 1 — Gazebo

```bash
cd "$TB3_WS"
source ~/envs/tb3_humble.bash
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

### 터미널 2 — slam_toolbox

```bash
cd "$TB3_WS"
source ~/envs/tb3_humble.bash
ros2 launch slam_toolbox online_async_launch.py use_sim_time:=True
```

### 터미널 3 — Nav2 navigation stack

```bash
cd "$TB3_WS"
source ~/envs/tb3_humble.bash
ros2 launch nav2_bringup navigation_launch.py use_sim_time:=True
```

### 터미널 4 — explore_lite

```bash
cd "$TB3_WS"
source ~/envs/tb3_humble.bash
ros2 launch explore_lite explore.launch.py use_sim_time:=True
```

### 터미널 5 — RViz

```bash
cd "$TB3_WS"
source ~/envs/tb3_humble.bash
rviz2 --ros-args -p use_sim_time:=true
```

### 확인

```bash
ros2 action list | grep navigate
ros2 topic list | grep explore
ros2 topic echo /map nav_msgs/msg/OccupancyGrid --once --qos-durability transient_local --qos-reliability reliable
ros2 run tf2_ros tf2_echo map odom
```

### 탐색 중지/재개

```bash
ros2 topic pub --once /explore/resume std_msgs/msg/Bool "{data: false}"
ros2 topic pub --once /explore/resume std_msgs/msg/Bool "{data: true}"
```

### 탐색 지도 저장

```bash
mkdir -p "$TB3_WS/maps"
ros2 run nav2_map_server map_saver_cli -f "$TB3_WS/maps/explore_map"
```
