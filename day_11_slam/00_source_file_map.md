# 00. Day 11 Source File Map

이 문서는 Day 11 SLAM 문서를 읽을 때 기준이 되는 실제 파일 위치를 정리한다.

---

## 1. SLAM 관련 핵심 패키지

현재 Day 11 SLAM의 중심 패키지는 다음이다.

```text
$ROS2_WS/lee_robot_description/
```

주의할 점:

```text
lee_robot_description은 현재 ws/src 아래가 아니라 ws 루트에 있다.
```

일반적인 ROS2 workspace에서는 패키지가 `src/` 아래에 있는 경우가 많지만, 현재 실습 폴더에서는 `day_67/ws/lee_robot_description`에 있다.  
그래도 `colcon build` 대상이 되며, install 경로로 복사되면 `ros2 launch lee_robot_description ...` 형태로 실행할 수 있다.

---

## 2. 주요 파일 목록

```text
lee_robot_description/
├── CMakeLists.txt
├── package.xml
├── launch/
│   ├── slam.launch.py
│   ├── nav2.launch.py
│   ├── amcl.launch.py
│   ├── amcl_full.launch.py
│   └── nav2_navigation.launch.py
├── config/
│   ├── slam_param.yaml
│   ├── amcl_param.yaml
│   └── nav2_params.yaml
├── urdf/
│   ├── turtlebot.xacro
│   └── turtlebot_gaze.xacro
├── rviz/
│   └── slam.rviz
├── worlds/
│   ├── lee_world.world
│   ├── simple_maze.world
│   └── slam.world
└── scripts/
    └── lidar_wall_follower.py
```

---

## 3. 파일별 역할

| 파일 | Day 11에서의 역할 |
|---|---|
| `launch/slam.launch.py` | Gazebo, robot_state_publisher, spawn_entity, SLAM Toolbox, RViz2를 한 번에 실행 |
| `config/slam_param.yaml` | SLAM Toolbox의 frame, scan topic, map 해상도, scan matching, loop closure 설정 |
| `urdf/turtlebot.xacro` | 로봇의 link/joint 구조와 `base_scan` 같은 frame 구조 정의 |
| `urdf/turtlebot_gaze.xacro` | Gazebo plugin 설정. `/robot_ns/scan`, `/robot_ns/odom`, `/robot_ns/cmd_vel` 생성에 관여 |
| `rviz/slam.rviz` | SLAM 확인용 RViz2 설정 |
| `worlds/slam.world` | SLAM용 Gazebo world |
| `CMakeLists.txt` | `urdf launch rviz config worlds`를 install/share로 복사 |

---

## 4. 현재 SLAM parameter 핵심값

`config/slam_param.yaml` 기준 핵심값은 다음이다.

```yaml
slam_toolbox:
  ros__parameters:
    use_sim_time: true
    odom_frame: odom_robot_ns
    map_frame: map_robot_ns
    base_frame: base_footprint
    scan_topic: /robot_ns/scan
    mode: mapping
    transform_publish_period: 0.02
    map_update_interval: 1.0
    resolution: 0.05
    max_laser_range: 3.5
    minimum_time_interval: 0.2
    minimum_travel_distance: 0.05
    minimum_travel_heading: 0.05
    use_scan_matching: true
    do_loop_closing: true
```

초보자 기준으로 가장 먼저 확인해야 할 값은 이것이다.

```text
scan_topic = /robot_ns/scan
map_frame  = map_robot_ns
odom_frame = odom_robot_ns
base_frame = base_footprint
```

이 네 개가 실제 토픽/frame과 맞지 않으면 SLAM이 거의 바로 막힌다.

---

## 5. 현재 bag 파일

현재 확인된 rosbag은 크게 두 종류다.

### 5.1 현재 SLAM용 bag

```text
$ROS2_WS/bags/slam_raw_01
```

metadata 기준:

```text
Duration       약 90.3초
Messages       11700개
Topics         /robot_ns/tf_static, /robot_ns/scan, /robot_ns/tf, /robot_ns/odom
```

이 bag은 현재 `/robot_ns` namespace 구조와 잘 맞는다.

### 5.2 이전 Day 9 계열 bag

```text
$ROS2_WS/rosbag2_2026_05_13-16_27_44
$ROS2_WORK_DIR/day_9/rosbag2_2026_05_13-16_27_44
```

metadata 기준:

```text
Duration       약 52.0초
Messages       5323개
Topics         /scan, /odom, /tf, /tf_static, /imu, /cmd_vel, /image_raw/compressed
```

이 bag은 namespace가 없다. 현재 `/robot_ns/scan`, `/robot_ns/tf` 기준 설정과 바로 맞지 않으므로 재생할 때 remap을 고려해야 한다.

---

## 6. 지도/posegraph 산출물

현재 workspace root에 다음 산출물이 있다.

```text
slam_map.yaml
slam_map.pgm
room_map.yaml
room_map.pgm
slam_map_serial.data
slam_map_serial.posegraph
slam_map_serial1.data
slam_map_serial1.posegraph
slam_map_serial2.data
slam_map_serial2.posegraph
```

의미:

| 파일 | 의미 |
|---|---|
| `.yaml` | 지도 이미지 파일명, 해상도, 원점, threshold 같은 메타데이터 |
| `.pgm` | 실제 occupancy grid를 이미지로 저장한 파일 |
| `.posegraph` / `.data` | SLAM Toolbox pose graph 저장 파일. 지도 이미지보다 SLAM 내부 상태에 가까움 |

---

## 7. 문서 작성 기준

이 문서에서는 코드를 수정하지 않는다.

```text
코드 변경 X
패키지 구조 변경 X
문서 재정리 O
배경지식 보강 O
실행상 주의점 기록 O
내 환경 기준 실행법 추가 O
```
