# SLAM 명령어 정리

Day 11 SLAM 실습에서 사용하는 명령어를 목적별로 정리한다. 복사하기 전에 실제 topic, namespace, map 저장 경로를 확인한다.

`lee_robot_description`은 ROS2 package name이고, `robot_ns`는 namespace 예시다. `ros2 launch`와 `ros2 pkg prefix`에는 package name이 들어가야 한다.

---

## 0. 공통 준비

```bash
cd $ROS2_WS
source /opt/ros/humble/setup.bash
source install/setup.bash
```

수정 후 빌드:

```bash
colcon build --packages-select lee_robot_description
source install/setup.bash
```

---

## 1. live SLAM 실행

```bash
ros2 launch lee_robot_description slam.launch.py world:=slam.world
```

다른 world:

```bash
ros2 launch lee_robot_description slam.launch.py world:=lee_world.world
ros2 launch lee_robot_description slam.launch.py world:=simple_maze.world
```

옵션:

```bash
ros2 launch lee_robot_description slam.launch.py world:=slam.world use_rviz:=false
ros2 launch lee_robot_description slam.launch.py world:=slam.world use_slam:=false
ros2 launch lee_robot_description slam.launch.py --show-args
```

---

## 2. teleop

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard \
  --ros-args \
  -r __node:=lee_teleop \
  -r cmd_vel:=/lee/cmd_vel
```

---

## 3. topic 확인

```bash
ros2 topic list | sort
ros2 topic echo /lee/scan --once
ros2 topic echo /lee/odom --once
ros2 topic echo /lee/map --once
ros2 topic hz /lee/scan
ros2 topic info /lee/map -v
```

---

## 4. node 확인

```bash
ros2 node list
ros2 node info /slam_toolbox
```

---

## 5. TF 확인

```bash
ros2 run tf2_ros tf2_echo map_lee base_footprint \
  --ros-args \
  -r /tf:=/lee/tf \
  -r /tf_static:=/lee/tf_static
```

```bash
ros2 run tf2_ros tf2_echo odom_lee base_footprint \
  --ros-args \
  -r /tf:=/lee/tf \
  -r /tf_static:=/lee/tf_static
```

```bash
ros2 run tf2_ros tf2_echo base_link base_scan \
  --ros-args \
  -r /tf:=/lee/tf \
  -r /tf_static:=/lee/tf_static
```

---

## 6. 지도 저장

workspace root:

```bash
ros2 run nav2_map_server map_saver_cli \
  -t /lee/map \
  -f ./slam_map
```

maps 폴더:

```bash
mkdir -p maps
ros2 run nav2_map_server map_saver_cli \
  -t /lee/map \
  -f ./maps/slam_map
```

---

## 7. 저장 지도 로딩

map_server:

```bash
ros2 run nav2_map_server map_server \
  --ros-args \
  -r /map:=/lee/map \
  -p yaml_filename:=$PWD/slam_map.yaml \
  -p frame_id:=map_lee
```

lifecycle manager:

```bash
ros2 run nav2_lifecycle_manager lifecycle_manager \
  --ros-args \
  -p node_names:='["map_server"]' \
  -p autostart:=True
```

확인:

```bash
ros2 topic echo /lee/map --once
ros2 lifecycle get /map_server
```

---

## 8. offline SLAM - 현재 `/lee` bag

SLAM Toolbox:

```bash
ros2 run slam_toolbox async_slam_toolbox_node \
  --ros-args \
  -r __node:=slam_toolbox \
  --params-file $PWD/lee_robot_description/config/slam_param.yaml \
  -p use_sim_time:=true \
  -r /map:=/lee/map \
  -r /map_updates:=/lee/map_updates \
  -r /tf:=/lee/tf \
  -r /tf_static:=/lee/tf_static
```

RViz2:

```bash
rviz2 -d $(ros2 pkg prefix lee_robot_description)/share/lee_robot_description/rviz/slam.rviz \
  --ros-args \
  -p use_sim_time:=true \
  -r /tf:=/lee/tf \
  -r /tf_static:=/lee/tf_static
```

bag play:

```bash
ros2 bag play "$BAG_DIR" --clock --rate 0.5
```

---

## 9. offline SLAM - namespace 없는 bag remap

```bash
ros2 bag play "$BAG_DIR" --clock --rate 0.5 \
  --remap /scan:=/lee/scan \
  --remap /odom:=/lee/odom \
  --remap /tf:=/lee/tf \
  --remap /tf_static:=/lee/tf_static
```

주의:

```text
이 명령은 topic 이름만 바꾼다.
frame_id는 자동 변경되지 않는다.
```

---

## 10. posegraph 저장/복원

저장:

```bash
ros2 service call /slam_toolbox/serialize_map \
  slam_toolbox/srv/SerializePoseGraph \
  "{filename: './slam_map_serial'}"
```

복원:

```bash
ros2 service call /slam_toolbox/deserialize_map \
  slam_toolbox/srv/DeserializePoseGraph \
  "{filename: './slam_map_serial', match_type: 1}"
```

주의:

```text
filename에는 .data 또는 .posegraph 확장자를 붙이지 않는다.
```
