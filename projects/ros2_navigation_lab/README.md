# ROS2 Navigation Lab

Gazebo Classic, URDF/Xacro, `slam_toolbox`, `nav2_amcl`, `nav2_map_server`, `nav2_bringup`을 연결해 ROS2 Humble Navigation 흐름을 확인하는 실습 workspace입니다.

이 패키지는 SLAM, AMCL, planner, controller 알고리즘을 직접 구현하는 프로젝트가 아닙니다. 표준 ROS2/Nav2 패키지를 어떤 launch, parameter, topic, frame 구조로 연결했는지 확인하는 데 초점을 둡니다.

---

## 패키지 역할

`src/lee_robot_description`은 이름상 description 패키지처럼 보이지만, 이 실습에서는 URDF/Xacro만 담는 순수 description 패키지가 아닙니다. Gazebo 실행, SLAM, AMCL, Nav2, rosbag workflow에 필요한 launch, config, map, RViz 설정까지 함께 관리하는 실습용 bringup 패키지 역할을 합니다.

따라서 이 workspace를 볼 때는 `lee_robot_description`을 아래 범위를 묶은 실습 패키지로 이해합니다.

```text
URDF/Xacro model
+ Gazebo world/spawn launch
+ SLAM Toolbox parameter
+ AMCL / map_server parameter
+ Nav2 bringup 연결
+ rosbag replay 기반 확인 workflow
```

---

## 환경

| 항목 | 기준 |
|---|---|
| OS | Ubuntu 22.04 |
| ROS2 | Humble |
| Simulator | Gazebo Classic + `gazebo_ros` |
| Navigation | Nav2 Humble packages |
| SLAM | `slam_toolbox` |
| Visualization | RViz2 |

---

## 구조

```text
.
├── README.md
├── docs/
│   ├── ARCHITECTURE.md
│   ├── COMMANDS_ONLY.md
│   ├── BAG_COMMANDS_ONLY.md
│   ├── BAG_SLAM_NAV2_WORKFLOW.md
│   ├── REFERENCES.md
│   ├── RUNTIME_WORKFLOW.md
│   └── TROUBLESHOOTING.md
└── src/
    └── lee_robot_description/
        ├── launch/
        ├── config/
        ├── maps/
        ├── rviz/
        ├── scripts/
        ├── urdf/
        └── worlds/
```

---

## Rosbag 데이터 포함 여부

이 workspace는 rosbag 기반 SLAM/Nav2 workflow를 지원하지만, rosbag 원본 데이터는 저장소에 포함하지 않습니다. rosbag은 용량이 크고 실행 환경마다 다르므로 Git에는 올리지 않고, 실행 시 직접 준비한 bag 디렉토리를 `$BAG_DIR`로 지정합니다.

```bash
export BAG_DIR=/path/to/rosbag_directory
ros2 bag info "$BAG_DIR"
```

기준 workflow는 다음 문서에 분리했습니다.

```text
docs/BAG_SLAM_NAV2_WORKFLOW.md   단계별 설명
docs/BAG_COMMANDS_ONLY.md        명령어만 빠르게 복사
```

---

## 주요 실행 흐름

```text
1. Gazebo에서 로봇 모델을 실행한다.
2. slam_toolbox로 /lee/scan과 TF를 사용해 map을 생성하거나 확인한다.
3. 저장된 map을 nav2_map_server로 불러온다.
4. nav2_amcl로 map 위에서 현재 위치를 추정한다.
5. Nav2 stack을 실행하고 RViz 또는 action CLI로 goal을 보낸다.
```

기본 workflow는 `slam.world`와 `maps/slam_map.yaml`을 사용합니다. `lee_world.world`와 `maps/room_map.yaml`은 작은 방 환경 테스트용으로 유지합니다.

---

## 빌드

```bash
source /opt/ros/humble/setup.bash
colcon build --symlink-install --packages-select lee_robot_description
source install/setup.bash
```

---

## 실행

Gazebo만 실행:

```bash
ros2 launch lee_robot_description gazebo.launch.py world:=slam.world use_avoidance:=false
```

SLAM 실행:

```bash
ros2 launch lee_robot_description gazebo_slam.launch.py world:=slam.world
```

Localization 실행:

```bash
ros2 launch lee_robot_description localization.launch.py world:=slam.world
```

Localization + Nav2 통합 실행:

```bash
ros2 launch lee_robot_description nav2.launch.py use_rviz:=false
```

Rosbag 기반 SLAM map 생성:

```bash
ros2 launch lee_robot_description bag_slam.launch.py
```

Rosbag으로 만든 map을 불러와 AMCL 확인:

```bash
ros2 launch lee_robot_description bag_localization.launch.py
```

Rosbag으로 만든 map + rosbag scan으로 Nav2 costmap 확인:

```bash
ros2 launch lee_robot_description bag_nav2.launch.py
```

`nav2.launch.py`를 실행한 뒤에는 Nav2 goal을 보내기 전에 initial pose를 먼저 지정해야 합니다. AMCL은 initial pose를 기준으로 `map_lee -> odom_lee` transform을 안정화합니다.

Localization이 이미 실행 중일 때 Nav2 stack만 따로 실행:

```bash
ros2 launch lee_robot_description nav2_navigation.launch.py
```

`nav2.launch.py`와 `nav2_navigation.launch.py`를 같은 세션에서 중복 실행하지 않도록 주의합니다.

---

## Rosbag 기반 workflow 요약

rosbag 기반 흐름은 기존 Gazebo launch와 분리되어 있습니다.

```text
1. bag_slam.launch.py로 rosbag replay 기반 SLAM map 생성
2. map_saver_cli로 bag_slam_map.yaml / bag_slam_map.pgm 저장
3. bag_localization.launch.py로 저장 map 로드 + AMCL 확인
4. bag_nav2.launch.py로 저장 map + rosbag scan 기반 Nav2 costmap 확인
```

추천 rosbag replay 명령은 다음과 같습니다.

```bash
export BAG_DIR=/path/to/rosbag_directory
ros2 bag play "$BAG_DIR" \
  --clock \
  --loop \
  -r 0.2 \
  --topics /scan /odom /tf /tf_static \
  --remap /scan:=/lee/scan \
          /odom:=/lee/odom \
          /tf:=/lee/tf \
          /tf_static:=/lee/tf_static
```

초기 위치는 고정 좌표를 넣기보다 RViz의 `2D Pose Estimate`로 map 위에서 직접 지정합니다. SLAM으로 만든 map에서 `x=0.0`, `y=0.0`, `yaw=0.0`이 실제 시작 위치라고 보장되지 않기 때문입니다.

---

## 주요 확인 명령

```bash
ros2 topic echo /lee/scan --once
ros2 topic echo /lee/odom --once
ros2 topic echo /lee/map --once --qos-durability transient_local
ros2 topic echo /amcl_pose --once
ros2 topic echo /particle_cloud --once
ros2 lifecycle get /map_server
ros2 lifecycle get /amcl
ros2 run tf2_ros tf2_echo map_lee odom_lee --ros-args -r /tf:=/lee/tf -r /tf_static:=/lee/tf_static
ros2 run tf2_ros tf2_echo odom_lee base_footprint --ros-args -r /tf:=/lee/tf -r /tf_static:=/lee/tf_static
ros2 action send_goal /lee/navigate_to_pose nav2_msgs/action/NavigateToPose "{pose: {header: {frame_id: 'map_lee'}, pose: {position: {x: 0.5, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}}"
```

TF는 `/lee/tf`, `/lee/tf_static`으로 publish됩니다. `tf2_echo`는 기본적으로 `/tf`, `/tf_static`을 보기 때문에 위처럼 remap해서 확인합니다.

Nav2 node namespace 확인:

```bash
ros2 node list | sort | grep controller_server
ros2 node list | sort | grep planner_server
ros2 node list | sort | grep bt_navigator
```

정상적인 경우 `/lee/controller_server`처럼 `/lee` namespace 아래에 node가 떠야 합니다.

---

## Launch 파일 역할

| Launch file | Gazebo | SLAM | AMCL | Nav2 | 용도 |
|---|---:|---:|---:|---:|---|
| `display.launch.py` | No | No | No | No | URDF/RViz 모델 확인 |
| `gazebo.launch.py` | Yes | No | No | No | 시뮬레이션 단독 실행 |
| `gazebo_slam.launch.py` | Yes | Yes | No | No | Mapping workflow |
| `localization.launch.py` | Yes | No | Yes | No | AMCL localization 확인 |
| `nav2_navigation.launch.py` | No | No | No | Yes | Localization 이후 Nav2 stack만 실행 |
| `nav2.launch.py` | Yes | No | Yes | Yes | Localization + Nav2 통합 실행 |
| `bag_slam.launch.py` | No | Yes | No | No | Rosbag replay 기반 mapping |
| `bag_localization.launch.py` | No | No | Yes | No | 저장된 rosbag map 로드 + AMCL |
| `bag_nav2_navigation.launch.py` | No | No | No | Yes | Rosbag workflow용 Nav2 stack만 실행 |
| `bag_nav2.launch.py` | No | No | Yes | Yes | 저장된 rosbag map + Nav2 costmap 확인 |

---

## 기본 frame과 topic

| 항목 | 값 |
|---|---|
| Robot namespace | `/lee` |
| Map frame | `map_lee` |
| Odometry frame | `odom_lee` |
| Base frame | `base_footprint` |
| LiDAR topic | `/lee/scan` |
| Odometry topic | `/lee/odom` |
| Velocity command topic | `/lee/cmd_vel` |
| Map topic | `/lee/map` |
| AMCL pose topic | `/amcl_pose` |
| AMCL particle cloud topic | `/particle_cloud` |

---

## Rosbag workflow frame과 topic

rosbag workflow는 Gazebo workflow와 frame 전제가 다릅니다. rosbag replay는 topic 이름은 remap할 수 있지만 message 내부의 `header.frame_id`, `child_frame_id`는 바꾸지 않으므로, bag 전용 parameter에서는 `odom_lee`가 아니라 `odom`을 사용합니다.

| 항목 | Gazebo workflow | Rosbag workflow |
|---|---|---|
| Map frame | `map_lee` | `map_lee` |
| Odometry frame | `odom_lee` | `odom` |
| Base frame | `base_footprint` | `base_footprint` |
| LiDAR topic | `/lee/scan` | `/lee/scan`으로 remap 권장 |
| Odometry topic | `/lee/odom` | `/lee/odom`으로 remap 권장 |
| TF topic | `/lee/tf`, `/lee/tf_static` | `/lee/tf`, `/lee/tf_static`으로 remap 권장 |

---

## 직접 구성한 부분

- ROS2 package metadata, install rule, launch entrypoint
- Gazebo robot spawn과 ROS topic 연결
- URDF/Xacro 기반 simulation model 구성
- 사용자 frame 이름에 맞춘 `slam_toolbox` mapping parameter
- `nav2_map_server`, `nav2_amcl` localization 흐름
- Nav2 costmap, planner, controller, behavior, navigator parameter
- RViz 설정과 runtime verification 명령

---

## ROS2/Nav2가 제공하는 부분

- SLAM 구현: `slam_toolbox`
- Localization 구현: `nav2_amcl`
- Map server: `nav2_map_server`
- Navigation stack: `nav2_bringup`과 Nav2 server들
- Visualization: RViz2
- Simulation integration: Gazebo Classic과 `gazebo_ros`

---

## Namespace / Frame 인자

Gazebo, SLAM, localization launch는 기본값으로 `/lee`, `map_lee`, `odom_lee`를 사용하지만 아래 인자로 바꿀 수 있습니다.

```bash
ros2 launch lee_robot_description gazebo.launch.py namespace:=robot1 odom_frame:=odom_robot1 entity_name:=turtlebot
ros2 launch lee_robot_description gazebo_slam.launch.py namespace:=robot1 map_frame:=map_robot1 odom_frame:=odom_robot1
ros2 launch lee_robot_description localization.launch.py namespace:=robot1 map_frame:=map_robot1 odom_frame:=odom_robot1
```

Nav2 navigation parameter와 RViz 설정은 아직 기본 `/lee`, `map_lee`, `odom_lee` 기준입니다. `namespace:=...`만 바꿔서 완전한 multi-robot template처럼 사용할 수 있는 상태는 아니며, Nav2 params/RViz display topic도 함께 맞춰야 합니다.

---

## 관련 문서

- [Runtime workflow](docs/RUNTIME_WORKFLOW.md)
- [Copy-paste commands](docs/COMMANDS_ONLY.md)
- [Rosbag SLAM/Nav2 workflow](docs/BAG_SLAM_NAV2_WORKFLOW.md)
- [Rosbag commands only](docs/BAG_COMMANDS_ONLY.md)
- [Architecture overview](docs/ARCHITECTURE.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [References](docs/REFERENCES.md)
