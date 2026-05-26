# 05. AMCL 실행 방식: 분리 실행과 통합 런치

Day 12에는 실행 방식이 두 가지 있다.

```text
1. 분리 실행
2. 통합 실행
```

처음 학습할 때는 분리 실행이 더 낫다. 문제가 생겼을 때 어느 노드가 원인인지 찾기 쉽기 때문이다. 구조를 이해한 뒤에는 `localization.launch.py`로 반복 실행하면 된다.

---

## 1. 분리 실행 구조

분리 실행은 기존 실습 흐름에 가깝다.

```text
터미널 1  Gazebo + robot_state_publisher + spawn_entity + RViz2
터미널 2  map_server
터미널 3  amcl
터미널 4  lifecycle_manager
터미널 5  initialpose 또는 RViz 2D Pose Estimate
터미널 6  teleop_twist_keyboard 또는 lidar_wall_follower.py
```

이때 `gazebo.launch.py`는 모든 것을 켜는 파일이 아니다.

```text
gazebo.launch.py가 실행하는 것:
  Gazebo
  robot_state_publisher
  spawn_entity.py
  RViz2

gazebo.launch.py가 직접 실행하지 않는 것:
  map_server
  amcl
  lifecycle_manager
  teleop
```

---

## 2. 분리 실행의 장점

```text
/map_server가 active인지 따로 확인 가능
/amcl이 /lee/map, /lee/scan을 구독하는지 확인 가능
initialpose 전후 차이를 보기 쉬움
map_lee -> odom_lee TF가 언제 생기는지 보기 쉬움
RViz 문제인지 AMCL 문제인지 분리해서 판단 가능
```

초보자에게는 분리 실행이 더 번거롭지만, 디버깅에는 훨씬 좋다.

---

## 3. 통합 실행 구조

`localization.launch.py`는 반복 실습을 편하게 하기 위한 파일이다.

실행:

```bash
ros2 launch lee_robot_description localization.launch.py
```

통합 런치가 실행하는 것:

```text
Gazebo
robot_state_publisher
spawn_entity.py
map_server
amcl
lifecycle_manager_localization
RViz2
```

launch 내부 핵심:

```text
map_server
  yaml_filename: map_yaml
  frame_id: map_lee
  /map -> /lee/map remap

amcl
  params-file: config/amcl_param.yaml
  /map -> /lee/map remap
  /tf -> /lee/tf remap
  /tf_static -> /lee/tf_static remap

lifecycle_manager_localization
  node_names: ['map_server', 'amcl']
  autostart: True
```

---

## 4. map_yaml 인자

`localization.launch.py`는 기본적으로 package share의 `maps/slam_map.yaml`을 찾는다.

```text
기본 map:
share/lee_robot_description/maps/slam_map.yaml
```

다른 map을 쓰려면 명시한다.

```bash
ros2 launch lee_robot_description localization.launch.py \
  world:=lee_world.world \
  map_yaml:=$(ros2 pkg prefix lee_robot_description)/share/lee_robot_description/maps/room_map.yaml
```

주의:

```text
world와 map은 반드시 같은 환경에서 만든 한 쌍이어야 한다.
```

예:

```text
slam.world       <-> slam_map.yaml
lee_world.world  <-> room_map.yaml
```

---

## 5. 분리 실행과 통합 실행 중 무엇을 쓸까?

| 상황 | 추천 |
|---|---|
| 처음 구조를 이해하는 중 | 분리 실행 |
| map_server lifecycle 문제 확인 | 분리 실행 |
| AMCL topic/TF 문제 추적 | 분리 실행 |
| 정상 동작을 반복 재현 | 통합 실행 |
| RViz와 initialpose만 확인 | 통합 실행 가능 |
| Nav2까지 이어 붙일 준비 | 통합 실행 후 navigation 별도 실행 |

현재 학습 목적에서는 둘 다 문서화해두는 것이 좋다.

```text
분리 실행: 원리를 이해하기 좋음
통합 실행: 반복 확인하기 좋음
```

---

## 6. 실행 전 정리 명령

Gazebo/RViz/Nav2 계열은 이전 프로세스가 남아 있으면 topic이나 entity가 꼬일 수 있다.

```bash
pkill -f gzserver
pkill -f gzclient
pkill -f gazebo
pkill -f rviz2
pkill -f nav2_map_server
pkill -f nav2_amcl
pkill -f nav2_lifecycle_manager
pkill -f teleop_twist_keyboard
```

필요하면 현재 노드 목록도 확인한다.

```bash
ros2 node list
```

---

## 7. 빌드가 필요한 경우

문서만 보는 경우는 빌드가 필요 없다. 하지만 launch/config/package를 수정했다면 다시 빌드한다.

```bash
cd $ROS2_WS
source /opt/ros/humble/setup.bash
colcon build --packages-select lee_robot_description
source install/setup.bash
```

문서만 확인하는 경우에는 빌드가 필요하지 않지만, launch/config/urdf 파일을 수정한 뒤에는 다시 빌드해야 한다.
