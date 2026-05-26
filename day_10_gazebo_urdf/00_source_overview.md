# 00. 소스 구성 요약 - `lee_robot_description` 기준

이 문서는 Day 10 Gazebo/URDF 실습에서 사용하는 주요 파일과 역할을 빠르게 찾기 위한 참조 문서다.

기준 경로:

```text
projects/ros2_navigation_lab/src/lee_robot_description/
```

---

## 1. 패키지 메타데이터

| 파일 | 역할 | 학습 포인트 |
|---|---|---|
| `package.xml` | ROS2 패키지 이름, 의존성, build type 선언 | 어떤 외부 패키지에 의존하는지 확인 |
| `CMakeLists.txt` | `ament_cmake` 빌드 설정, 리소스 설치 설정 | launch/urdf/rviz/config/worlds가 install/share로 복사되는 구조 확인 |

### `package.xml`에서 보이는 핵심 의존성

```text
urdf, xacro
robot_state_publisher
joint_state_publisher, joint_state_publisher_gui
gazebo_ros, gazebo_plugins
rviz2
sensor_msgs, geometry_msgs
slam_toolbox
nav2_map_server, nav2_amcl, nav2_lifecycle_manager
teleop_twist_keyboard
```

Day 10에서는 Gazebo/URDF/RViz 관련 의존성이 핵심이고, Day 11~13으로 이어지면서 `slam_toolbox`, `nav2_*` 의존성이 함께 사용된다.

### `CMakeLists.txt`에서 중요한 부분

```cmake
install(
  DIRECTORY urdf launch rviz config worlds
  DESTINATION share/${PROJECT_NAME}
)

install(
  PROGRAMS scripts/lidar_wall_follower.py
  DESTINATION lib/${PROJECT_NAME}
)
```

이 설정 때문에 빌드 후 launch 파일이 다음 위치에서 리소스를 찾을 수 있다.

```text
install/lee_robot_description/share/lee_robot_description/urdf
install/lee_robot_description/share/lee_robot_description/launch
install/lee_robot_description/share/lee_robot_description/worlds
install/lee_robot_description/share/lee_robot_description/rviz
install/lee_robot_description/share/lee_robot_description/config
```

그리고 `lidar_wall_follower.py`는 실행 파일로 설치되어 아래처럼 실행될 수 있다.

```bash
ros2 run lee_robot_description lidar_wall_follower.py
```

---

## 2. URDF/Xacro 파일

| 파일 | 역할 |
|---|---|
| `urdf/turtlebot.xacro` | 로봇 본체 구조 정의. link, joint, visual, collision, inertial, 센서 부착 위치 포함 |
| `urdf/turtlebot_gaze.xacro` | Gazebo용 물리 속성 및 plugin 정의 |

현재 폴더에는 xacro 변환 결과물인 `.urdf` 산출물을 저장해 두지 않는다. 사람이 확인해야 할 때만 `xacro` 명령으로 별도 생성한다.

### `turtlebot.xacro`에서 만들어지는 주요 frame/link

```text
base_footprint
base_link
wheel_left_link
wheel_right_link
caster_back_link
imu_link
base_scan
camera_link
```

### `turtlebot.xacro`에서 중요한 joint

```text
base_joint           base_footprint -> base_link, fixed
wheel_left_joint     base_link -> wheel_left_link, continuous
wheel_right_joint    base_link -> wheel_right_link, continuous
caster_back_joint    base_link -> caster_back_link, fixed
imu_joint            base_link -> imu_link, fixed
scan_joint           base_link -> base_scan, fixed
camera_joint         base_link -> camera_link, fixed
```

### `turtlebot_gaze.xacro`에서 붙는 주요 plugin

| plugin | 연결 대상 | ROS2 입출력 |
|---|---|---|
| `libgazebo_ros_diff_drive.so` | `wheel_left_joint`, `wheel_right_joint` | subscribe `/lee/cmd_vel`, publish `/lee/odom`, TF |
| `libgazebo_ros_joint_state_publisher.so` | wheel joints | publish `/lee/joint_states` |
| `libgazebo_ros_ray_sensor.so` | `base_scan` | publish `/lee/scan` |
| `libgazebo_ros_imu_sensor.so` | `imu_link` | publish `/lee/imu` |
| `libgazebo_ros_camera.so` | `camera_link` | publish `/lee/image_raw`, `/lee/camera_info` |

---

## 3. Launch 파일

| 파일 | 역할 |
|---|---|
| `launch/display.launch.py` | Gazebo 없이 RViz2에서 로봇 모델/TF 확인 |
| `launch/gazebo.launch.py` | Gazebo world, robot_state_publisher, spawn_entity, RViz2, LiDAR 회피 노드 통합 실행 |
| `launch/gazebo_slam.launch.py` | `slam.launch.py`를 include하는 SLAM 실행용 wrapper |
| `launch/slam.launch.py` | Day 11 SLAM Toolbox 실행과 연결 |
| `launch/localization.launch.py` | Gazebo + map_server + AMCL + lifecycle 구성을 함께 실행 |
| `launch/nav2.launch.py` | `localization.launch.py`와 `nav2_navigation.launch.py`를 함께 include하는 상위 launch |
| `launch/nav2_navigation.launch.py` | `nav2_bringup/navigation_launch.py`를 포함하여 navigation stack 실행 |

Day 10에서 직접 중요한 파일은 `display.launch.py`와 `gazebo.launch.py`이다. 나머지는 Day 11~13에서 다시 자세히 다룬다.

---

## 4. World 파일

| 파일 | 역할 |
|---|---|
| `worlds/lee_world.world` | 작은 방 형태의 기본 실습 world |
| `worlds/simple_maze.world` | 미로/장애물 형태의 world |
| `worlds/slam.world` | SLAM 실습에 쓰기 좋은 구조화된 world |

World 파일은 로봇 모델이 아니라 로봇이 주행할 시뮬레이션 환경을 정의한다.

```text
world
├── physics
├── ground_plane
├── sun/light
├── wall/box/cylinder obstacle
└── 기타 static model
```

---

## 5. RViz 설정 파일

| 파일 | 역할 |
|---|---|
| `rviz/turtlebot.rviz` | Day 10 로봇 모델/센서 확인용 RViz 설정 |
| `rviz/slam.rviz` | Day 11 SLAM 확인용 RViz 설정 |
| `rviz/amcl.rviz` | Day 12 AMCL 확인용 RViz 설정 |

RViz 설정 파일은 코드가 아니라 시각화 설정이다. Fixed Frame, display type, topic 이름, QoS 설정 등이 저장된다.

---

## 6. 스크립트

| 파일 | 역할 |
|---|---|
| `scripts/lidar_wall_follower.py` | `/lee/scan`을 읽고 `/lee/cmd_vel`을 발행하는 간단한 정면 장애물 회피 노드 |

`lidar_wall_follower.py`의 동작은 엄밀한 wall following보다 단순 장애물 회피에 가깝다.

```text
정면이 막히면 회전
정면이 비어 있으면 전진
```

따라서 학습 문서에서는 “단순 LiDAR 회피 노드”로 설명한다.

---

## 7. Day 10 기준 최소 실행 단위

### RViz 모델 확인

```bash
ros2 launch lee_robot_description display.launch.py
```

### Gazebo 통합 실행

```bash
ros2 launch lee_robot_description gazebo.launch.py
```

### 회피 노드 포함 실행

```bash
ros2 launch lee_robot_description gazebo.launch.py use_avoidance:=true
```

### 토픽 확인

```bash
ros2 topic list | grep /lee
ros2 topic echo /lee/scan --qos-reliability best_effort --once
ros2 topic echo /lee/odom --once
ros2 topic echo /lee/joint_states --once
```
