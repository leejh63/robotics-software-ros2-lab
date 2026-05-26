# 00. Day 11 소스 구성 요약

이 문서는 Day 11 SLAM 실습에서 참고해야 할 실제 파일과 설정 위치를 정리한다.

---

## 1. SLAM 관련 핵심 패키지

Day 11 SLAM 실습의 중심 패키지는 다음이다.

```text
projects/ros2_navigation_lab/src/lee_robot_description/
```

주의할 점:

```text
lee_robot_description은 projects/ros2_navigation_lab/src 아래에 있다.
```

이 프로젝트는 `projects/ros2_navigation_lab`를 ROS2 workspace처럼 사용하고, 패키지는 `src/lee_robot_description` 아래에 둔다.  
`colcon build` 대상이 되며, install 경로로 복사되면 `ros2 launch lee_robot_description ...` 형태로 실행할 수 있다.

---

## 2. 주요 파일 목록

```text
lee_robot_description/
├── CMakeLists.txt
├── package.xml
├── launch/
│   ├── display.launch.py
│   ├── gazebo.launch.py
│   ├── slam.launch.py
│   ├── gazebo_slam.launch.py
│   ├── localization.launch.py
│   ├── nav2.launch.py
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
| `urdf/turtlebot_gaze.xacro` | Gazebo plugin 설정. `/lee/scan`, `/lee/odom`, `/lee/cmd_vel` 생성에 관여 |
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
    odom_frame: odom_lee
    map_frame: map_lee
    base_frame: base_footprint
    scan_topic: /lee/scan
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
scan_topic = /lee/scan
map_frame  = map_lee
odom_frame = odom_lee
base_frame = base_footprint
```

이 네 개가 실제 토픽/frame과 맞지 않으면 SLAM이 거의 바로 막힌다.

---

## 5. 현재 bag 파일

현재 저장소에는 rosbag 원본을 포함하지 않는다.

SLAM bag을 새로 기록한다면 현재 기본 namespace 기준으로 아래 토픽을 확인한다.

```text
/lee/tf_static
/lee/scan
/lee/tf
/lee/odom
```

namespace가 없는 예전 bag을 재생할 때는 topic remap만으로 충분하지 않을 수 있다. bag 안의 `frame_id`, `child_frame_id`, TF frame 이름도 `map_lee`, `odom_lee`, `base_footprint` 흐름과 맞는지 확인해야 한다.

---

## 6. 지도/posegraph 산출물

현재 package의 `maps/` 폴더에 다음 지도 파일이 있다.

```text
maps/slam_map.yaml
maps/slam_map.pgm
maps/room_map.yaml
maps/room_map.pgm
```

의미:

| 파일 | 의미 |
|---|---|
| `.yaml` | 지도 이미지 파일명, 해상도, 원점, threshold 같은 메타데이터 |
| `.pgm` | 실제 occupancy grid를 이미지로 저장한 파일 |
| `.posegraph` / `.data` | SLAM Toolbox pose graph 저장 파일. 현재 저장소에는 포함하지 않음 |

---

## 7. 문서 작성 기준

이 문서는 소스 구조를 바꾸기보다 SLAM 실습에서 각 파일이 맡는 역할을 정리한다.

```text
문서 재정리
배경지식 보강
실행상 주의점 정리
예시 환경 기준 실행법 추가
```
