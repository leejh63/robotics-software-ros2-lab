# SLAM 빠른 실행 명령

예시 실습 환경에서 자주 사용하는 최소 명령 모음이다.

---

## 1. 공통

```bash
cd $ROS2_WS
source /opt/ros/humble/setup.bash
source install/setup.bash
```

---

## 2. live SLAM

터미널 1:

```bash
ros2 launch lee_robot_description slam.launch.py world:=slam.world
```

터미널 2:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard \
  --ros-args \
  -r __node:=lee_teleop \
  -r cmd_vel:=/robot_ns/cmd_vel
```

---

## 3. 확인

```bash
ros2 topic echo /robot_ns/scan --once
ros2 topic echo /robot_ns/odom --once
ros2 topic echo /robot_ns/map --once
```

```bash
ros2 run tf2_ros tf2_echo map_robot_ns base_footprint \
  --ros-args \
  -r /tf:=/robot_ns/tf \
  -r /tf_static:=/robot_ns/tf_static
```

---

## 4. 지도 저장

```bash
ros2 run nav2_map_server map_saver_cli \
  -t /robot_ns/map \
  -f ./slam_map
```

---

## 5. offline SLAM

터미널 1:

```bash
ros2 run slam_toolbox async_slam_toolbox_node \
  --ros-args \
  -r __node:=slam_toolbox \
  --params-file $PWD/lee_robot_description/config/slam_param.yaml \
  -p use_sim_time:=true \
  -r /map:=/robot_ns/map \
  -r /map_updates:=/robot_ns/map_updates \
  -r /tf:=/robot_ns/tf \
  -r /tf_static:=/robot_ns/tf_static
```

터미널 2:

```bash
rviz2 -d $(ros2 pkg prefix lee_robot_description)/share/lee_robot_description/rviz/slam.rviz \
  --ros-args \
  -p use_sim_time:=true \
  -r /tf:=/robot_ns/tf \
  -r /tf_static:=/robot_ns/tf_static
```

터미널 3:

```bash
ros2 bag play "$BAG_DIR" --clock --rate 0.5
```

---

## 6. 자주 까먹는 것

```text
map topic      /robot_ns/map
scan topic     /robot_ns/scan
tf topic       /robot_ns/tf, /robot_ns/tf_static
Fixed Frame    map_robot_ns
cmd_vel        /robot_ns/cmd_vel
map_saver      -t /robot_ns/map 필요
bag play       use_sim_time=true이면 --clock 필요
```
