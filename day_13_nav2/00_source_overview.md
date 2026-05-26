# 00. Day 13 소스 구성 요약

이 문서는 Day 13 Nav2 실습에서 기준이 되는 launch, parameter, map, RViz 설정 파일을 정리한다.

---

## 1. 기준 workspace

```text
projects/ros2_navigation_lab
```

Day 13의 핵심 패키지는 `lee_robot_description`이다.

주의할 점:

```text
lee_robot_description은 `projects/ros2_navigation_lab/src/lee_robot_description`
경로를 기준으로 설명한다.
```

명령어를 실행할 때는 실제 workspace 경로에 맞게 `$ROS2_WS`를 설정한다.

---

## 2. 핵심 파일 목록

```text
projects/ros2_navigation_lab/src/lee_robot_description/
├── launch/
│   ├── localization.launch.py
│   ├── nav2.launch.py
│   └── nav2_navigation.launch.py
├── config/
│   ├── nav2_params.yaml
│   ├── amcl_param.yaml
│   └── slam_param.yaml
├── urdf/
│   ├── turtlebot.xacro
│   └── turtlebot_gaze.xacro
├── worlds/
│   ├── slam.world
│   ├── lee_world.world
│   └── simple_maze.world
├── rviz/
│   ├── amcl.rviz
│   ├── slam.rviz
│   └── turtlebot.rviz
└── CMakeLists.txt
```

---

## 3. launch 파일 역할

| 파일 | 역할 | 포함되는 주요 요소 |
|---|---|---|
| `localization.launch.py` | simulation + localization 실행 | Gazebo, robot_state_publisher, spawn_entity, map_server, AMCL, localization lifecycle manager, RViz |
| `nav2_navigation.launch.py` | Nav2 navigation stack 실행 | nav2_bringup의 `navigation_launch.py`, `/lee` namespace, `nav2_params.yaml` |
| `nav2.launch.py` | 통합 실행 wrapper | `localization.launch.py`와 `nav2_navigation.launch.py` include |

이 실습 구성은 의도적으로 두 단계로 나뉜다.

```text
localization.launch.py
  로봇과 위치추정이 정상인지 확인하는 단계

nav2_navigation.launch.py
  goal을 받아 경로와 속도 명령을 생성하는 단계

nav2.launch.py
  위 두 단계를 한 번에 실행하는 통합 단계
```

---

## 4. `localization.launch.py`가 하는 일

실제 파일 기준 핵심 흐름은 다음과 같다.

```text
1. package share directory 확인
2. 기본 map_yaml 경로를 package share의 maps/slam_map.yaml로 설정
3. Gazebo 실행
4. xacro -> robot_description 생성
5. robot_state_publisher 실행
6. spawn_entity.py로 Gazebo에 robot spawn
7. nav2_map_server 실행
8. nav2_amcl 실행
9. lifecycle_manager_localization 실행
10. RViz 실행
```

주요 remap:

```text
/robot_description -> /lee/robot_description
/tf                -> /lee/tf
/tf_static         -> /lee/tf_static
/joint_states      -> /lee/joint_states
/map               -> /lee/map
```

중요한 점:

```text
map_server와 amcl 노드 이름은 /map_server, /amcl일 수 있다.
하지만 topic은 /lee/map, /lee/scan, /lee/tf 구조로 연결된다.
```

노드 이름과 topic 이름을 혼동하면 디버깅이 어려워진다.

---

## 5. `nav2_navigation.launch.py`가 하는 일

이 파일은 직접 planner/controller를 하나하나 띄우는 것이 아니라, `nav2_bringup`의 `navigation_launch.py`를 include한다.

```text
nav2_navigation.launch.py
  -> PushRosNamespace(namespace='lee')
  -> Include nav2_bringup/launch/navigation_launch.py
  -> params_file = lee_robot_description/config/nav2_params.yaml
```

이 구조를 둔 이유는 `nav2_bringup navigation_launch.py`를 직접 실행했을 때 Nav2 서버 노드가 기대한 namespace 아래에 생성되지 않아, namespace와 parameter 구조가 어긋날 수 있기 때문이다. 이 경우 `controller_server`가 `FollowPath`의 DWB critic 설정을 읽지 못해 `No critics defined for FollowPath` 같은 오류가 발생할 수 있다.

기본 namespace:

```text
lee
```

그래서 정상적으로 올라오면 navigation 노드는 보통 아래처럼 보인다.

```text
/lee/planner_server
/lee/controller_server
/lee/bt_navigator
/lee/behavior_server
/lee/smoother_server
/lee/waypoint_follower
/lee/velocity_smoother
/lee/lifecycle_manager_navigation
```

---

## 6. `nav2_params.yaml` 역할

`nav2_params.yaml`은 Nav2 navigation stack의 동작을 결정한다.

주요 섹션:

```text
global_costmap
local_costmap
planner_server
controller_server
smoother_server
behavior_server
bt_navigator
waypoint_follower
velocity_smoother
lifecycle_manager_navigation
```

예시 실습 환경 기준으로 중요한 설정:

```text
map frame       : map_lee
odom frame      : odom_lee
base frame      : base_footprint
scan topic      : /lee/scan
odom topic      : /lee/odom
map topic       : /lee/map
cmd_vel topic   : /lee/cmd_vel
```

---

## 7. URDF/Xacro와 Nav2의 관계

Nav2는 URDF를 직접 읽어서 주행하는 것이 아니다.  
하지만 URDF/Xacro에서 만들어진 frame과 Gazebo plugin topic이 Nav2 입력이 된다.

```text
turtlebot.xacro
  -> robot_state_publisher
  -> base_footprint, base_link, base_scan, camera_link TF

Gazebo plugin
  -> /lee/scan
  -> /lee/odom
  -> /lee/cmd_vel 구독
```

Nav2가 기대하는 frame/topic과 URDF/Gazebo가 실제 제공하는 frame/topic이 맞아야 한다.

---

## 8. map 파일과 world 파일 관계

예시 실습 구성의 world-map 조합은 아래처럼 본다.

| world | map |
|---|---|
| `slam.world` | `slam_map.yaml`, `slam_map.pgm` |
| `lee_world.world` | `room_map.yaml`, `room_map.pgm` |

주의:

```text
world와 map이 서로 다른 환경이면 AMCL과 Nav2가 이상하게 동작한다.
```

예를 들어 `lee_world.world`를 띄웠는데 `slam_map.yaml`을 쓰면, LiDAR가 보는 벽과 지도 벽이 맞지 않는다.  
그러면 AMCL 위치추정부터 틀어지고, Nav2 경로 계획도 흔들린다.
