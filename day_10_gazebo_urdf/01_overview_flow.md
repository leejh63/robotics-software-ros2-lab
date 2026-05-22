# 01. Day 10 전체 흐름

## 1. Day 10의 위치

Day 10은 ROS2 기본 통신을 배운 뒤, SLAM/AMCL/Nav2로 넘어가기 전에 **로봇과 센서를 시뮬레이션으로 만드는 단계**이다.

```text
Day 06~09 ROS2 기본기
  node / topic / service / action / launch / parameter / TF / rosbag
        ↓
Day 10 Gazebo / URDF / Xacro
  robot model / Gazebo world / sensor plugin / /scan / /odom / /tf
        ↓
Day 11 SLAM
  LaserScan + TF + odom 기반 지도 생성
        ↓
Day 12 AMCL
  저장된 지도 위에서 현재 위치 추정
        ↓
Day 13 Nav2
  위치 추정 + costmap + planner/controller로 목표 지점 이동
```

Day 10이 부실하면 Day 11부터 문제가 연쇄적으로 발생한다. 특히 `/scan`, `/odom`, `/tf`, `/tf_static`, `frame_id`, `use_sim_time`이 맞지 않으면 SLAM/AMCL/Nav2가 정상적으로 동작하기 어렵다.

---

## 2. 이번 실습에서 실제로 한 일

Day 10의 실습은 크게 다섯 묶음이다.

```text
1. rosbag2/RViz2로 저장된 센서 데이터 확인
2. URDF/Xacro로 로봇의 link/joint 구조 이해
3. robot_state_publisher로 robot_description과 TF 흐름 확인
4. Gazebo world + plugin으로 가상 센서와 구동 topic 생성
5. namespace/remap/use_sim_time/QoS 문제를 확인하며 SLAM 입력 준비
```

---

## 3. 전체 실행 흐름

`gaze.launch.py` 기준 흐름은 다음과 같다.

```text
ros2 launch lee_robot_description gaze.launch.py

1. get_package_share_directory('lee_robot_description')로 패키지 설치 경로를 찾음
2. urdf/turtlebot.xacro 경로를 만듦
3. worlds/robot_ns_world.world 경로를 만듦
4. xacro 명령으로 turtlebot.xacro를 URDF XML 문자열로 변환
5. robot_state_publisher가 robot_description 파라미터를 받고 실행됨
6. Gazebo가 lee_world.world와 함께 실행됨
7. Gazebo에 libgazebo_ros_init.so, libgazebo_ros_factory.so가 로드됨
8. spawn_entity.py가 /robot_ns/robot_description을 읽어 Gazebo에 turtlebot_lee entity 생성
9. turtlebot_gaze.xacro에 정의된 Gazebo plugin들이 동작 시작
10. plugin들이 /robot_ns/cmd_vel, /robot_ns/odom, /robot_ns/scan, /robot_ns/imu, /robot_ns/image_raw 등을 연결
11. RViz2가 robot_description, TF, scan, odom 등을 시각화
12. 옵션에 따라 lidar_wall_follower.py가 /robot_ns/scan을 읽고 /robot_ns/cmd_vel 발행
```

---

## 4. 가장 중요한 데이터 흐름

### 4.1 로봇 모델/TF 흐름

```text
turtlebot.xacro
        ↓ xacro 변환
robot_description
        ↓
robot_state_publisher
        ↓
/robot_ns/tf, /robot_ns/tf_static
        ↓
RViz2 RobotModel / TF display
```

### 4.2 Gazebo spawn 흐름

```text
robot_state_publisher가 제공하는 /robot_ns/robot_description
        ↓
spawn_entity.py -topic /robot_ns/robot_description
        ↓
Gazebo 안에 turtlebot_lee entity 생성
        ↓
Gazebo plugin 동작 시작
```

### 4.3 구동 흐름

```text
teleop 또는 lidar_wall_follower.py
        ↓ publish
/robot_ns/cmd_vel
        ↓ subscribe
Gazebo diff_drive plugin
        ↓
wheel_left_joint / wheel_right_joint 구동
        ↓ publish
/robot_ns/odom, /robot_ns/joint_states
```

### 4.4 센서 흐름

```text
Gazebo ray sensor on base_scan
        ↓
/robot_ns/scan  sensor_msgs/msg/LaserScan

Gazebo imu sensor on imu_link
        ↓
/robot_ns/imu   sensor_msgs/msg/Imu

Gazebo camera sensor on camera_link
        ↓
/robot_ns/image_raw, /robot_ns/camera_info
```

---

## 5. Day 10에서 Day 11로 넘어가는 기준

Day 11 SLAM으로 넘어가기 전에 Day 10에서 최소한 아래가 확인되어야 한다.

```text
1. /robot_ns/scan이 발행된다.
2. /robot_ns/odom이 발행된다.
3. /robot_ns/tf와 /robot_ns/tf_static이 발행된다.
4. LaserScan의 frame_id가 TF tree 안에 존재한다.
5. odom frame과 base frame이 TF로 연결된다.
6. Gazebo/RViz/SLAM 노드가 모두 simulation time을 쓰는지 확인한다.
```

확인 명령 예시:

```bash
ros2 topic list | grep /robot_ns
ros2 topic echo /robot_ns/scan --qos-reliability best_effort --once
ros2 topic echo /robot_ns/odom --once
ros2 run tf2_tools view_frames --ros-args -r /tf:=/robot_ns/tf -r /tf_static:=/robot_ns/tf_static
```

---

## 6. Day 10의 결론

Day 10은 화면에 로봇을 띄우는 날이 아니라, 아래 사실을 확인하는 날이다.

```text
Gazebo plugin은 시뮬레이션 세계의 물리/센서 결과를 ROS2 topic으로 바꿔준다.
robot_state_publisher는 URDF의 link/joint 구조를 TF로 바꿔준다.
RViz2는 그 topic과 TF를 시각화할 뿐이다.
SLAM/AMCL/Nav2는 결국 이 topic과 TF를 입력으로 사용한다.
```
