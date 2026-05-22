# 00. Day 13 Source File Map

이 문서는 Day 13 Nav2 실습에서 실제로 기준이 되는 파일을 정리한다.  
목적은 “어떤 파일이 어떤 역할을 하는지”를 먼저 잡는 것이다.

---

## 1. 기준 workspace

```text
$ROS2_WS
```

현재 Day 13의 핵심 패키지는 `lee_robot_description`이다.

주의할 점:

```text
lee_robot_description은 일반적인 ws/src 아래 패키지 구조가 아니라,
현재 기록 기준으로 ws 루트에 놓인 패키지처럼 다뤄지고 있다.
```

문서에서는 실제 네가 사용한 경로를 우선 기준으로 둔다.

---

## 2. 핵심 파일 목록

```text
$ROS2_WS/lee_robot_description/
├── launch/
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
| `nav2.launch.py` | simulation + localization 실행 | Gazebo, robot_state_publisher, spawn_entity, map_server, AMCL, localization lifecycle manager, RViz |
| `nav2_navigation.launch.py` | Nav2 navigation stack 실행 | nav2_bringup의 `navigation_launch.py`, `/robot_ns` namespace, `nav2_params.yaml` |

현재 구조는 의도적으로 두 단계로 나뉜다.

```text
nav2.launch.py
  로봇과 위치추정이 정상인지 확인하는 단계

nav2_navigation.launch.py
  goal을 받아 경로와 속도 명령을 생성하는 단계
```

---

## 4. `nav2.launch.py`가 하는 일

실제 파일 기준 핵심 흐름은 다음과 같다.

```text
1. package share directory 확인
2. 기본 map_yaml 경로를 workspace root의 slam_map.yaml로 추정
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
/robot_description -> /robot_ns/robot_description
/tf                -> /robot_ns/tf
/tf_static         -> /robot_ns/tf_static
/joint_states      -> /robot_ns/joint_states
/map               -> /robot_ns/map
```

중요한 점:

```text
map_server와 amcl 노드 이름은 /map_server, /amcl일 수 있다.
하지만 topic은 /robot_ns/map, /robot_ns/scan, /robot_ns/tf 구조로 연결된다.
```

노드 이름과 topic 이름을 혼동하면 디버깅이 어려워진다.

---

## 5. `nav2_navigation.launch.py`가 하는 일

이 파일은 직접 planner/controller를 하나하나 띄우는 것이 아니라, `nav2_bringup`의 `navigation_launch.py`를 include한다.

```text
nav2_navigation.launch.py
  -> PushRosNamespace(namespace='robot_ns')
  -> Include nav2_bringup/launch/navigation_launch.py
  -> params_file = lee_robot_description/config/nav2_params.yaml
```

이 구조를 둔 이유는 `nav2_bringup navigation_launch.py`를 직접 실행했을 때 Nav2 서버 노드가 기대한 namespace 아래에 생성되지 않아, `nav2_params.yaml`의 `robot_ns:` parameter 구조와 실제 node namespace가 어긋날 수 있기 때문이다. 이 경우 `controller_server`가 `FollowPath`의 DWB critic 설정을 읽지 못해 `No critics defined for FollowPath` 같은 오류가 발생할 수 있다.

기본 namespace:

```text
robot_ns
```

그래서 정상적으로 올라오면 navigation 노드는 보통 아래처럼 보인다.

```text
/robot_ns/planner_server
/robot_ns/controller_server
/robot_ns/bt_navigator
/robot_ns/behavior_server
/robot_ns/smoother_server
/robot_ns/waypoint_follower
/robot_ns/velocity_smoother
/robot_ns/lifecycle_manager_navigation
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

현재 환경 기준으로 중요한 설정:

```text
map frame       : map_robot_ns
odom frame      : odom_robot_ns
base frame      : base_footprint
scan topic      : /robot_ns/scan
odom topic      : /robot_ns/odom
map topic       : /robot_ns/map
cmd_vel topic   : /robot_ns/cmd_vel
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
  -> /robot_ns/scan
  -> /robot_ns/odom
  -> /robot_ns/cmd_vel 구독
```

Nav2가 기대하는 frame/topic과 URDF/Gazebo가 실제 제공하는 frame/topic이 맞아야 한다.

---

## 8. map 파일과 world 파일 관계

현재 기록 기준 world-map 짝은 아래처럼 본다.

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

---

## 9. 이 문서에서 코드 수정은 하지 않음

이 source map은 현재 코드 구조를 이해하기 위한 문서다.

```text
코드 변경 없음
launch 변경 없음
parameter 변경 없음
```

