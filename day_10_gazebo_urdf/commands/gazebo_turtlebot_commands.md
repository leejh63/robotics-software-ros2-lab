# Gazebo/TurtleBot 명령어 정리

## 1. 기본 빌드와 환경 적용

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
  -o ./lee_robot_description/urdf/turtlebot.urdf
```

변환 결과 확인:

```bash
head -40 ./lee_robot_description/urdf/turtlebot.urdf
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
ros2 launch lee_robot_description gazebo.launch.py
```

회피 노드 없이 실행:

```bash
ros2 launch lee_robot_description gazebo.launch.py use_avoidance:=false
```

RViz 없이 실행:

```bash
ros2 launch lee_robot_description gazebo.launch.py use_rviz:=false
```

spawn 높이 변경:

```bash
ros2 launch lee_robot_description gazebo.launch.py spawn_z:=0.2
```

launch argument 확인:

```bash
ros2 launch lee_robot_description gazebo.launch.py --show-args
```

---

## 5. Topic 확인

```bash
ros2 topic list | grep /lee
```

센서 확인:

```bash
ros2 topic echo /lee/scan --qos-reliability best_effort --once
ros2 topic echo /lee/imu --once
ros2 topic echo /lee/image_raw --once
ros2 topic echo /lee/camera_info --once
```

주기 확인:

```bash
ros2 topic hz /lee/scan --qos-reliability best_effort
ros2 topic hz /lee/odom
ros2 topic hz /lee/joint_states
```

타입 확인:

```bash
ros2 topic type /lee/scan
ros2 topic type /lee/odom
ros2 topic type /lee/cmd_vel
```

---

## 6. TF 확인

이 실습 구성에서는 `/tf`, `/tf_static`이 `/lee/tf`, `/lee/tf_static`으로 remap되어 있을 수 있다.

```bash
ros2 topic echo /lee/tf --once
ros2 topic echo /lee/tf_static --once
```

TF tree 생성:

```bash
ros2 run tf2_tools view_frames --ros-args \
  -r /tf:=/lee/tf \
  -r /tf_static:=/lee/tf_static
```

특정 transform 확인:

```bash
ros2 run tf2_ros tf2_echo odom_lee base_footprint --ros-args \
  -r /tf:=/lee/tf \
  -r /tf_static:=/lee/tf_static
```

```bash
ros2 run tf2_ros tf2_echo base_link base_scan --ros-args \
  -r /tf:=/lee/tf \
  -r /tf_static:=/lee/tf_static
```

---

## 7. Teleop 조작

수동 조작을 확인할 때는 회피 노드를 끈 상태에서 실행한다.

```bash
ros2 launch lee_robot_description gazebo.launch.py use_avoidance:=false
```

다른 터미널:

```bash
source /opt/ros/humble/setup.bash
source $ROS2_WS/install/setup.bash

ros2 run teleop_twist_keyboard teleop_twist_keyboard \
  --ros-args \
  -r __node:=lee_teleop \
  -r cmd_vel:=/lee/cmd_vel
```

`/lee/cmd_vel` 발행자 확인:

```bash
ros2 topic info /lee/cmd_vel -v
```

---

## 8. LiDAR 회피 노드만 실행

launch에서 같이 실행:

```bash
ros2 launch lee_robot_description gazebo.launch.py use_avoidance:=true
```

노드만 별도 실행:

```bash
ros2 run lee_robot_description lidar_wall_follower.py \
  --ros-args \
  -p scan_topic:=/lee/scan \
  -p cmd_vel_topic:=/lee/cmd_vel \
  -p obstacle_distance:=0.55 \
  -p front_angle_deg:=25.0 \
  -p turn_direction:=right
```

---

## 9. Entity 삭제와 Gazebo 정리

Gazebo entity 삭제:

```bash
ros2 run gazebo_ros delete_entity.py -entity turtlebot
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
