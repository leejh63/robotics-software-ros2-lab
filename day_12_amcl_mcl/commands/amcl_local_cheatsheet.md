# AMCL Local Cheatsheet

현재 환경 기준 AMCL 실행 명령 모음이다.

`lee_robot_description`은 package name 예시이고, `robot_ns`는 namespace 예시다. AMCL topic/node는 launch 방식에 따라 namespace가 붙거나 붙지 않을 수 있으므로 먼저 실제 이름을 확인한다.

---

## 0. 모든 터미널 공통

```bash
cd $ROS2_WS
source /opt/ros/humble/setup.bash
source install/setup.bash
```

---

## 1. 기존 프로세스 정리

```bash
pkill -f gzserver
pkill -f gzclient
pkill -f gazebo
pkill -f rviz2
pkill -f nav2_map_server
pkill -f nav2_amcl
pkill -f nav2_lifecycle_manager
pkill -f teleop_twist_keyboard
```

---

## 2. 통합 실행

```bash
ros2 launch lee_robot_description amcl_full.launch.py
```

작은 방 world/map:

```bash
ros2 launch lee_robot_description amcl_full.launch.py \
  world:=lee_world.world \
  map_yaml:=$ROS2_WS/room_map.yaml
```

RViz에서:

```text
2D Pose Estimate로 초기 위치 입력
ParticleCloud 확인
LaserScan과 Map 정합 확인
```

---

## 3. 분리 실행

### 터미널 1: Gazebo + RViz

```bash
ros2 launch lee_robot_description amcl.launch.py world:=slam.world
```

### 터미널 2: map_server

```bash
ros2 run nav2_map_server map_server \
  --ros-args \
  -p yaml_filename:=$ROS2_WS/slam_map.yaml \
  -p use_sim_time:=true \
  -p frame_id:=map_robot_ns \
  -r /map:=/robot_ns/map
```

### 터미널 3: AMCL

```bash
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
ros2 run nav2_lifecycle_manager lifecycle_manager \
  --ros-args \
  -p node_names:="['map_server', 'amcl']" \
  -p autostart:=true \
  -p use_sim_time:=true
```

---

## 4. 확인 명령

먼저 실제 node/topic 이름을 확인한다.

```bash
ros2 node list | sort | grep -E 'map_server|amcl|lifecycle'
ros2 topic list | sort | grep -E 'map|scan|amcl_pose|particle_cloud|initialpose'
```

기본 확인:

```bash
ros2 lifecycle get /map_server
ros2 lifecycle get /amcl
ros2 topic echo /robot_ns/map --once
ros2 topic echo /robot_ns/scan --once
```

AMCL 출력 topic은 namespace 설정에 따라 둘 중 하나일 수 있다.

```bash
ros2 topic echo /amcl_pose --once
ros2 topic echo /particle_cloud --once
# namespace가 붙어 있다면:
ros2 topic echo /robot_ns/amcl_pose --once
ros2 topic echo /robot_ns/particle_cloud --once
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

---

## 5. teleop

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard \
  --ros-args \
  -r /cmd_vel:=/robot_ns/cmd_vel
```

---

## 6. RViz 체크

```text
Fixed Frame: map_robot_ns
Map: /robot_ns/map
LaserScan: /robot_ns/scan
RobotModel: /robot_ns/robot_description
ParticleCloud: /particle_cloud 또는 /robot_ns/particle_cloud
```

Map display:

```text
Reliability: Reliable
Durability: Transient Local
```

LaserScan:

```text
Reliability: Best Effort
```
