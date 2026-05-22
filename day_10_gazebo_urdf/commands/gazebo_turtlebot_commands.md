# Gazebo / TurtleBot Day 10 Commands

## 1. 기본 빌드와 source

```bash
cd $ROS2_WS
source /opt/ros/humble/setup.bash
colcon build --packages-select lee_robot_description
source install/setup.bash
```

패키지 확인:

```bash
ros2 pkg prefix lee_robot_description
ros2 pkg executables lee_robot_description
```

---

## 2. Xacro 변환 확인

```bash
xacro ./lee_robot_description/urdf/turtlebot.xacro \
  -o ./lee_robot_description/urdf/turtle_from_xacro.urdf
```

변환 결과 확인:

```bash
head -40 ./lee_robot_description/urdf/turtle_from_xacro.urdf
```

---

## 3. RViz2에서 모델만 확인

```bash
ros2 launch lee_robot_description display.launch.py
```

joint_state GUI 없이 실행:

```bash
ros2 launch lee_robot_description display.launch.py use_joint_state_gui:=false
```

---

## 4. Gazebo 통합 실행

기본 실행:

```bash
ros2 launch lee_robot_description gaze.launch.py
```

회피 노드 없이 실행:

```bash
ros2 launch lee_robot_description gaze.launch.py use_avoidance:=false
```

RViz 없이 실행:

```bash
ros2 launch lee_robot_description gaze.launch.py use_rviz:=false
```

spawn 높이 변경:

```bash
ros2 launch lee_robot_description gaze.launch.py spawn_z:=0.2
```

launch argument 확인:

```bash
ros2 launch lee_robot_description gaze.launch.py --show-args
```

---

## 5. Topic 확인

```bash
ros2 topic list | grep /robot_ns
```

센서 확인:

```bash
ros2 topic echo /robot_ns/scan --qos-reliability best_effort --once
ros2 topic echo /robot_ns/imu --once
ros2 topic echo /robot_ns/image_raw --once
ros2 topic echo /robot_ns/camera_info --once
```

주기 확인:

```bash
ros2 topic hz /robot_ns/scan --qos-reliability best_effort
ros2 topic hz /robot_ns/odom
ros2 topic hz /robot_ns/joint_states
```

타입 확인:

```bash
ros2 topic type /robot_ns/scan
ros2 topic type /robot_ns/odom
ros2 topic type /robot_ns/cmd_vel
```

---

## 6. TF 확인

현재 구조는 `/tf`, `/tf_static`이 `/robot_ns/tf`, `/robot_ns/tf_static`으로 remap되어 있을 수 있다.

```bash
ros2 topic echo /robot_ns/tf --once
ros2 topic echo /robot_ns/tf_static --once
```

TF tree 생성:

```bash
ros2 run tf2_tools view_frames --ros-args \
  -r /tf:=/robot_ns/tf \
  -r /tf_static:=/robot_ns/tf_static
```

특정 transform 확인:

```bash
ros2 run tf2_ros tf2_echo odom_robot_ns base_footprint --ros-args \
  -r /tf:=/robot_ns/tf \
  -r /tf_static:=/robot_ns/tf_static
```

```bash
ros2 run tf2_ros tf2_echo base_link base_scan --ros-args \
  -r /tf:=/robot_ns/tf \
  -r /tf_static:=/robot_ns/tf_static
```

---

## 7. Teleop 조작

회피 노드를 끈 상태에서 실행하는 것을 권장한다.

```bash
ros2 launch lee_robot_description gaze.launch.py use_avoidance:=false
```

다른 터미널:

```bash
source /opt/ros/humble/setup.bash
source $ROS2_WS/install/setup.bash

ros2 run teleop_twist_keyboard teleop_twist_keyboard \
  --ros-args \
  -r __node:=lee_teleop \
  -r cmd_vel:=/robot_ns/cmd_vel
```

`/robot_ns/cmd_vel` 발행자 확인:

```bash
ros2 topic info /robot_ns/cmd_vel -v
```

---

## 8. LiDAR 회피 노드만 실행

launch에서 같이 실행:

```bash
ros2 launch lee_robot_description gaze.launch.py use_avoidance:=true
```

노드만 별도 실행:

```bash
ros2 run lee_robot_description lidar_wall_follower.py \
  --ros-args \
  -p scan_topic:=/robot_ns/scan \
  -p cmd_vel_topic:=/robot_ns/cmd_vel \
  -p obstacle_distance:=0.55 \
  -p front_angle_deg:=25.0 \
  -p turn_direction:=right
```

---

## 9. Entity 삭제와 Gazebo 정리

Gazebo entity 삭제:

```bash
ros2 run gazebo_ros delete_entity.py -entity turtlebot_lee
```

Gazebo 프로세스 정리:

```bash
pkill -f gzserver
pkill -f gzclient
pkill -f gazebo
```

RViz까지 정리:

```bash
pkill -f rviz2
```

---

## 10. /clock 확인

```bash
ros2 topic echo /clock --once
ros2 topic info /clock -v
```

`/clock` publisher가 여러 개면 Gazebo/rosbag이 여러 개 떠 있는지 확인한다.
