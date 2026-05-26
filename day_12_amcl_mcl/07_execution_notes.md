# 07. 실습 환경 AMCL 실행 메모

이 문서는 예시 실습 환경에서 AMCL을 다시 실행할 때 필요한 경로, 명령, 토픽 확인 순서를 정리한다.

---

## 1. 기본 환경

```text
OS/ROS 기준        Ubuntu 22.04 + ROS2 Humble 기준
workspace          $ROS2_WS
package            lee_robot_description
map                $ROS2_WS/slam_map.yaml
world              lee_robot_description/worlds/slam.world
AMCL params        lee_robot_description/config/amcl_param.yaml
RViz config        lee_robot_description/rviz/amcl.rviz
```

모든 터미널 공통:

```bash
cd $ROS2_WS
source /opt/ros/humble/setup.bash
source install/setup.bash
```

---

## 2. 통합 실행으로 빠르게 확인

```bash
ros2 launch lee_robot_description amcl_full.launch.py
```

실행 후 RViz에서 확인:

```text
Fixed Frame: map_robot_ns
Map: /robot_ns/map
LaserScan: /robot_ns/scan
RobotModel: /robot_ns/robot_description
ParticleCloud: /particle_cloud
```

그 다음:

```text
RViz 2D Pose Estimate로 초기 위치와 방향 입력
teleop 또는 wall follower로 천천히 이동
particle_cloud가 수렴하는지 확인
```

---

## 3. 작은 방 world/map으로 실행

```bash
ros2 launch lee_robot_description amcl_full.launch.py \
  world:=lee_world.world \
  map_yaml:=$ROS2_WS/room_map.yaml
```

주의:

```text
lee_world.world에 slam_map.yaml을 쓰면 안 된다.
slam.world에 room_map.yaml을 쓰면 안 된다.
```

---

## 4. 분리 실행으로 구조 확인

### 터미널 1: Gazebo + RViz

```bash
cd $ROS2_WS
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 launch lee_robot_description amcl.launch.py world:=slam.world
```

### 터미널 2: map_server

```bash
cd $ROS2_WS
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 run nav2_map_server map_server \
  --ros-args \
  -p yaml_filename:=$ROS2_WS/slam_map.yaml \
  -p use_sim_time:=true \
  -p frame_id:=map_robot_ns \
  -r /map:=/robot_ns/map
```

### 터미널 3: AMCL

```bash
cd $ROS2_WS
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 run nav2_amcl amcl \
  --ros-args \
  --params-file $ROS2_WS/lee_robot_description/config/amcl_param.yaml \
  -p use_sim_time:=true \
  -r /map:=/robot_ns/map \
  -r /tf:=/robot_ns/tf \
  -r /tf_static:=/robot_ns/tf_static
```

### 터미널 4: lifecycle manager

```bash
cd $ROS2_WS
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 run nav2_lifecycle_manager lifecycle_manager \
  --ros-args \
  -p node_names:="['map_server', 'amcl']" \
  -p autostart:=true \
  -p use_sim_time:=true
```

---

## 5. 정상 확인 명령

Lifecycle:

```bash
ros2 lifecycle get /map_server
ros2 lifecycle get /amcl
```

정상:

```text
active [3]
active [3]
```

Map:

```bash
ros2 topic echo /robot_ns/map --once
```

확인 포인트:

```text
header.frame_id: map_robot_ns
width와 height가 0이 아님
data가 비어 있지 않음
```

Scan:

```bash
ros2 topic echo /robot_ns/scan --once
```

확인 포인트:

```text
header.frame_id: base_scan
ranges 배열이 있음
```

TF:

```bash
ros2 run tf2_ros tf2_echo odom_robot_ns base_footprint \
  --ros-args \
  -r /tf:=/robot_ns/tf \
  -r /tf_static:=/robot_ns/tf_static
```

initialpose 후:

```bash
ros2 run tf2_ros tf2_echo map_robot_ns odom_robot_ns \
  --ros-args \
  -r /tf:=/robot_ns/tf \
  -r /tf_static:=/robot_ns/tf_static
```

AMCL pose:

```bash
ros2 topic echo /amcl_pose --once
```

Particle:

```bash
ros2 topic echo /particle_cloud --once
```

---

## 6. 움직임 확인

teleop을 쓰는 경우:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard \
  --ros-args \
  -r /cmd_vel:=/robot_ns/cmd_vel
```

주의:

```text
AMCL 수렴 확인 중에는 너무 빠르게 움직이지 않는다.
처음에는 직진/회전을 조금씩만 준다.
```

---

## 7. 예시 환경에서 자주 헷갈릴 수 있는 것

```text
1. /map이 아니라 /robot_ns/map이다.
2. /scan이 아니라 /robot_ns/scan이다.
3. /cmd_vel이 아니라 /robot_ns/cmd_vel이다.
4. TF topic은 /robot_ns/tf, /robot_ns/tf_static으로 remap되어 있다.
5. frame은 map_robot_ns, odom_robot_ns, base_footprint, base_scan을 쓴다.
6. RViz Fixed Frame은 map_robot_ns다.
7. map_server와 amcl은 active 상태여야 한다.
8. initialpose를 줘야 AMCL이 제대로 수렴한다.
9. SLAM Toolbox와 AMCL을 동시에 map->odom 발행 주체로 두면 안 된다.
```
