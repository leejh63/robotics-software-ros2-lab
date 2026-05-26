# Gazebo Day 10 트러블슈팅

## 1. RViz2에서 로봇 모델이 보이지 않음

확인 순서:

```bash
ros2 topic list | grep robot_description
ros2 topic list | grep tf
ros2 topic echo /lee/tf_static --once
ros2 topic echo /lee/joint_states --once
```

확인할 것:

```text
1. robot_state_publisher가 실행 중인가?
2. robot_description remap이 RViz2와 맞는가?
3. RViz2 Fixed Frame이 실제 TF tree 안에 있는 frame인가?
4. /tf를 /lee/tf로 remap했다면 RViz2도 같은 remap을 받았는가?
```

---

## 2. Gazebo에 로봇이 spawn되지 않음

확인:

```bash
ros2 topic echo /lee/robot_description --once
ros2 service list | grep spawn
```

가능한 원인:

```text
1. Gazebo에 libgazebo_ros_factory.so가 로드되지 않음
2. /lee/robot_description topic이 비어 있음
3. xacro 변환 실패
4. 이미 같은 entity 이름이 존재함
```

entity 중복이면 삭제:

```bash
ros2 run gazebo_ros delete_entity.py -entity turtlebot
```

---

## 3. `/lee/scan`이 안 보임

확인:

```bash
ros2 topic list | grep scan
ros2 topic info /lee/scan -v
ros2 topic echo /lee/scan --qos-reliability best_effort --once
```

가능한 원인:

```text
1. Gazebo LiDAR plugin이 로드되지 않음
2. base_scan link/reference 문제
3. QoS mismatch
4. Gazebo가 pause 상태
5. RViz2 LaserScan Reliability Policy가 맞지 않음
```

---

## 4. `/lee/cmd_vel`을 보내도 로봇이 안 움직임

확인:

```bash
ros2 topic echo /lee/cmd_vel --once
ros2 topic info /lee/cmd_vel -v
ros2 topic echo /lee/odom --once
ros2 topic echo /lee/joint_states --once
```

가능한 원인:

```text
1. diff_drive plugin이 로드되지 않음
2. command_topic/namespace가 예상과 다름
3. wheel joint 이름이 plugin 설정과 맞지 않음
4. Gazebo physics가 pause 상태
5. teleop과 회피 노드가 동시에 cmd_vel을 발행함
```

회피 노드 끄기:

```bash
ros2 launch lee_robot_description gazebo.launch.py use_avoidance:=false
```

---

## 5. 움직임이 이상하게 튐

확인:

```bash
ros2 topic info /lee/cmd_vel -v
```

Publisher가 여러 개면 `/lee/cmd_vel` 충돌 가능성이 있다.

가능한 충돌:

```text
teleop_twist_keyboard
lidar_wall_follower.py
Nav2 controller_server
직접 만든 cmd_vel publisher
```

학습 중에는 하나만 켜는 것이 좋다.

---

## 6. TF가 없다고 나옴

이 실습 구성에서는 `/tf`가 `/lee/tf`로 remap되어 있을 수 있다.

기본 명령이 안 되면 remap을 붙인다.

```bash
ros2 run tf2_tools view_frames --ros-args \
  -r /tf:=/lee/tf \
  -r /tf_static:=/lee/tf_static
```

SLAM/AMCL/Nav2도 같은 문제가 날 수 있다. 해당 launch 파일에서 TF remap이 맞는지 확인해야 한다.

---

## 7. Message Filter dropping message

가능한 원인:

```text
1. LaserScan frame_id가 TF tree에 없음
2. sensor timestamp와 TF timestamp가 맞지 않음
3. use_sim_time 설정이 노드마다 다름
4. /clock publisher가 여러 개
```

확인:

```bash
ros2 topic echo /clock --once
ros2 topic info /clock -v
ros2 param get /robot_state_publisher use_sim_time
ros2 topic echo /lee/scan --qos-reliability best_effort --once
```

---

## 8. xacro 변환 실패

수동 변환:

```bash
xacro ./lee_robot_description/urdf/turtlebot.xacro \
  -o /tmp/turtlebot.urdf
```

확인할 것:

```text
1. XML 태그가 닫혔는가?
2. include 파일명이 맞는가? turtlebot_gaze.xacro
3. macro parameter 이름이 맞는가?
4. joint가 존재하지 않는 link를 참조하지 않는가?
```

---

## 9. `/clock` 관련 경고

증상:

```text
Detected jump back in time
Moved backwards in time
```

확인:

```bash
ros2 topic info /clock -v
```

정리:

```bash
pkill -f gzserver
pkill -f gzclient
pkill -f gazebo
pkill -f ros2
```

`pkill -f ros2`는 다른 ROS2 노드까지 죽일 수 있으므로 필요한 경우에만 사용한다.
