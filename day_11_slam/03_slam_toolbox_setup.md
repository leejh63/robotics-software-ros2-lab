# 03. SLAM Toolbox 설정 구조

## 1. `slam.launch.py`가 하는 일

현재 `slam.launch.py`는 Day 11에서 가장 중요한 launch 파일이다.

역할:

```text
1. Gazebo 실행
2. robot_state_publisher 실행
3. Gazebo에 turtlebot_lee spawn
4. SLAM Toolbox 실행
5. RViz2 실행
```

실행 명령:

```bash
cd $ROS2_WS
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 launch lee_robot_description slam.launch.py world:=slam.world
```

---

## 2. launch argument

`slam.launch.py`의 주요 argument는 다음이다.

| Argument | 기본값 | 의미 |
|---|---:|---|
| `use_sim_time` | `true` | Gazebo 또는 bag의 `/clock` 사용 |
| `world` | `lee_world.world` | `worlds/` 아래 world 파일명 |
| `use_rviz` | `true` | RViz2 실행 여부 |
| `use_slam` | `true` | SLAM Toolbox 실행 여부 |
| `spawn_z` | `0.1` | Gazebo spawn 높이 |

인자 확인:

```bash
ros2 launch lee_robot_description slam.launch.py --show-args
```

예시:

```bash
ros2 launch lee_robot_description slam.launch.py world:=slam.world
ros2 launch lee_robot_description slam.launch.py world:=simple_maze.world
ros2 launch lee_robot_description slam.launch.py world:=slam.world use_rviz:=false
ros2 launch lee_robot_description slam.launch.py world:=slam.world use_slam:=false
```

---

## 3. launch 내부 remap 구조

현재 launch에는 `isolated_remappings`가 있다.

```python
isolated_remappings = [
    ('/robot_description', '/robot_ns/robot_description'),
    ('/tf', '/robot_ns/tf'),
    ('/tf_static', '/robot_ns/tf_static'),
]
```

의미:

```text
기본 /robot_description 대신 /robot_ns/robot_description 사용
기본 /tf 대신 /robot_ns/tf 사용
기본 /tf_static 대신 /robot_ns/tf_static 사용
```

이 구조는 여러 실습자가 같은 ROS_DOMAIN_ID 또는 같은 네트워크에서 작업할 때 기본 topic이 섞이는 것을 줄이는 데 도움이 된다.

다만 주의할 점도 있다.

```text
RViz2, tf2_echo, bag play, SLAM Toolbox도 같은 remap 기준을 맞춰야 한다.
```

---

## 4. SLAM Toolbox node 설정

`slam.launch.py`에서 SLAM Toolbox는 다음 노드로 실행된다.

```text
package: slam_toolbox
executable: async_slam_toolbox_node
name: slam_toolbox
params: config/slam_param.yaml + use_sim_time
remap: /scan -> /robot_ns/scan
       /map -> /robot_ns/map
       /map_updates -> /robot_ns/map_updates
       /tf -> /robot_ns/tf
       /tf_static -> /robot_ns/tf_static
```

중요한 점:

```text
slam_param.yaml 안에도 scan_topic: /robot_ns/scan 이 들어 있다.
launch remap에도 /scan -> /robot_ns/scan 이 있다.
```

둘 중 하나만 맞아도 되는 경우가 있지만, 현재 문서 기준에서는 `/robot_ns/scan`을 기준으로 정리한다.  
SLAM이 scan을 못 받는다면 `ros2 node info /slam_toolbox`에서 실제 subscriber topic을 확인해야 한다.

---

## 5. `slam_param.yaml` 핵심값

현재 설정의 핵심값:

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

각 값의 의미:

| 값 | 의미 |
|---|---|
| `use_sim_time` | `/clock` 기준으로 시간 사용 |
| `odom_frame` | 오도메트리 기준 frame |
| `map_frame` | SLAM이 만드는 지도 기준 frame |
| `base_frame` | 로봇 기준 frame |
| `scan_topic` | LiDAR scan topic |
| `mode` | mapping 또는 localization |
| `resolution` | 지도 격자 해상도 |
| `max_laser_range` | SLAM에 사용할 LiDAR 최대 거리 |
| `minimum_time_interval` | scan 처리 최소 시간 간격 |
| `minimum_travel_distance` | 새 pose 처리 최소 이동 거리 |
| `minimum_travel_heading` | 새 pose 처리 최소 회전량 |
| `use_scan_matching` | scan matching 사용 여부 |
| `do_loop_closing` | loop closure 사용 여부 |

---

## 6. 현재 TF 기준

SLAM 전:

```text
odom_robot_ns
  -> base_footprint
    -> base_link
      -> base_scan
```

SLAM 후:

```text
map_robot_ns
  -> odom_robot_ns
    -> base_footprint
      -> base_link
        -> base_scan
```

확인 명령:

```bash
ros2 run tf2_ros tf2_echo map_robot_ns base_footprint \
  --ros-args \
  -r /tf:=/robot_ns/tf \
  -r /tf_static:=/robot_ns/tf_static
```

`map_robot_ns -> base_footprint`가 나오면 `map_robot_ns -> odom_robot_ns -> base_footprint`가 이어진 것이다.

---

## 7. 설치 경로와 source 경로 주의

`CMakeLists.txt`에는 다음 설치 규칙이 있다.

```cmake
install(
  DIRECTORY urdf launch rviz config worlds
  DESTINATION share/${PROJECT_NAME}
)
```

따라서 아래 파일을 수정하거나 추가하면 다시 빌드해야 한다.

```text
urdf/
launch/
rviz/
config/
worlds/
```

빌드:

```bash
cd $ROS2_WS
colcon build --packages-select lee_robot_description
source install/setup.bash
```

확인:

```bash
ros2 pkg prefix lee_robot_description
ls $(ros2 pkg prefix lee_robot_description)/share/lee_robot_description
```

---

## 8. 내가 직접 작성한 부분과 외부 패키지가 해주는 부분

### 내가 구성한 부분

```text
lee_robot_description package
URDF/Xacro 구조
Gazebo plugin 설정
slam.launch.py
slam_param.yaml
RViz 설정
world 파일
```

### 외부 패키지가 해주는 부분

```text
Gazebo
  물리 시뮬레이션, 센서 시뮬레이션

robot_state_publisher
  URDF의 link/joint를 TF로 변환

gazebo_ros plugins
  /robot_ns/scan, /robot_ns/odom, /robot_ns/cmd_vel 연결

slam_toolbox
  scan matching, loop closure, pose graph, map 생성

nav2_map_server
  map 저장/로딩

RViz2
  topic과 TF 시각화
```

이 구분이 중요하다.  
Day 11은 SLAM 알고리즘을 직접 구현한 것이 아니라, **SLAM Toolbox가 요구하는 입력 데이터와 frame/topic 구조를 맞춰서 지도 생성을 실습한 것**이다.
