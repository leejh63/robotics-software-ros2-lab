# 06. Explore Lite 자동 탐색

## 1. 목적

이 문서는 TurtleBot3 Burger 시뮬레이션에서 `m-explore-ros2`의 `explore_lite`를 사용해 자동 탐색을 수행하는 흐름을 정리한다.

기존 문서의 흐름은 다음과 같았다.

```text
Cartographer SLAM
→ 지도 저장
→ AMCL 위치 추정
→ 저장된 지도 기반 Navigation2
```

이 문서는 별도 확장 흐름으로 다음을 다룬다.

```text
Gazebo
→ slam_toolbox online SLAM
→ Nav2 navigation stack
→ explore_lite frontier exploration
```

즉, 저장된 지도를 먼저 만들고 AMCL로 localization하는 방식이 아니라, **SLAM으로 지도를 만드는 동시에 탐색 노드가 frontier를 찾아 Nav2 목표를 보내는 방식**이다.

---

## 2. m-explore-ros2 역할

`m-explore-ros2`는 ROS2용 `explore_lite` 포트이다.

이 실습에서 핵심적으로 사용하는 것은 `explore_lite`이다.

역할은 다음과 같다.

```text
/map에서 미탐색 영역과 탐색 완료 영역 경계(frontier)를 찾음
→ 탐색할 후보 지점을 선택
→ Nav2에 목표 위치를 전달
→ 로봇이 이동하면서 SLAM 지도 확장
→ 더 이상 유효한 frontier가 없으면 탐색 종료
```

구조적으로는 다음 흐름이다.

```text
slam_toolbox
  └── /map 생성
        ↓
explore_lite
  └── frontier 탐색
        ↓
Nav2
  └── 이동 목표 수행
        ↓
TurtleBot3
  └── 주행하며 새로운 scan 제공
        ↓
slam_toolbox
  └── 지도 갱신
```

---

## 3. 주의할 점

이 흐름은 기존 AMCL/Nav2 흐름과 다르다.

### 기존 저장 지도 기반 Nav2

```text
map_server
AMCL
Navigation2
```

이 방식에서는 이미 만들어진 `tb3_map.yaml`을 사용하고, AMCL이 `map -> odom`을 추정한다.

### Explore Lite 자동 탐색

```text
slam_toolbox
Navigation2
explore_lite
```

이 방식에서는 아직 완성된 지도가 없으므로 AMCL을 사용하지 않는다.  
`slam_toolbox`가 SLAM을 수행하면서 `/map`과 `map -> odom` 관계를 제공한다.

따라서 이 흐름에서는 다음을 동시에 실행하지 않는 것이 좋다.

```text
AMCL
static_transform_publisher map odom
저장 지도용 map_server
```

---

## 4. 패키지 추가

워크스페이스의 `src`로 이동한다.

```bash
cd "$TB3_WS/src"
```

`m-explore-ros2`를 clone한다.

```bash
git clone https://github.com/robo-friends/m-explore-ros2
```

워크스페이스 루트로 돌아간다.

```bash
cd "$TB3_WS"
```

의존성 설치가 필요하면 실행한다.

```bash
rosdep install --from-paths src -y --ignore-src
```

빌드한다.

```bash
colcon build --symlink-install
```

환경을 다시 적용한다.

```bash
source install/setup.bash
```

또는 기존 환경 파일을 다시 source한다.

```bash
source ~/envs/tb3_humble.bash
```

---

## 5. 실행 전 기존 노드 정리

이 흐름은 기존 AMCL/Nav2 개별 실행과 섞이면 안 된다.

먼저 관련 노드를 정리한다.

```bash
pkill -f rviz2
pkill -f map_server
pkill -f lifecycle_manager
pkill -f amcl
pkill -f static_transform_publisher
pkill -f slam_toolbox
pkill -f explore
```

확인:

```bash
ros2 node list
```

---

## 6. 터미널 1 — Gazebo 실행

```bash
cd "$TB3_WS"
source ~/envs/tb3_humble.bash

ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

확인:

```bash
ros2 topic echo /clock --once
```

---

## 7. 터미널 2 — slam_toolbox online SLAM 실행

```bash
cd "$TB3_WS"
source ~/envs/tb3_humble.bash

ros2 launch slam_toolbox online_async_launch.py use_sim_time:=True
```

확인:

```bash
ros2 topic list | grep map
```

기대 토픽:

```text
/map
```

지도 메시지 확인:

```bash
ros2 topic echo /map nav_msgs/msg/OccupancyGrid --once \
--qos-durability transient_local \
--qos-reliability reliable
```

---

## 8. 터미널 3 — Nav2 navigation stack 실행

```bash
cd "$TB3_WS"
source ~/envs/tb3_humble.bash

ros2 launch nav2_bringup navigation_launch.py use_sim_time:=True
```

이 명령은 Nav2의 navigation server 계층을 실행한다.

일반적으로 다음 계층이 포함된다.

```text
planner_server
controller_server
behavior_server
bt_navigator
waypoint_follower
velocity_smoother
lifecycle_manager_navigation
```

이 흐름에서는 `slam_toolbox`가 localization 역할을 수행하므로 별도 AMCL을 실행하지 않는다.

---

## 9. 터미널 4 — explore_lite 실행

```bash
cd "$TB3_WS"
source ~/envs/tb3_humble.bash

ros2 launch explore_lite explore.launch.py use_sim_time:=True
```

정상 실행되면 `explore_lite`가 `/map`을 기준으로 frontier를 찾고 Nav2로 목표를 보낸다.

---

## 10. 터미널 5 — RViz 확인

```bash
cd "$TB3_WS"
source ~/envs/tb3_humble.bash

rviz2 --ros-args -p use_sim_time:=true
```

RViz 권장 설정:

```text
Global Options
  Fixed Frame: map
```

추가할 Display:

```text
Map        → /map
TF         → enabled
LaserScan  → /scan
RobotModel → optional
Marker     → /explore/frontiers
```

`explore_lite`의 frontier 시각화 토픽은 일반적으로 다음이다.

```text
/explore/frontiers
```

RViz에서 Marker 또는 MarkerArray 타입으로 추가해서 확인한다.

---

## 11. 정상 동작 확인

Nav2 action 확인:

```bash
ros2 action list | grep navigate
```

예상:

```text
/navigate_to_pose
```

SLAM map 확인:

```bash
ros2 topic echo /map nav_msgs/msg/OccupancyGrid --once \
--qos-durability transient_local \
--qos-reliability reliable
```

TF 확인:

```bash
ros2 run tf2_ros tf2_echo map odom
```

explore 관련 토픽 확인:

```bash
ros2 topic list | grep explore
```

예상:

```text
/explore/frontiers
/explore/resume
```

---

## 12. 탐색 중지와 재개

`explore_lite`는 `/explore/resume` 토픽을 통해 탐색을 멈추거나 재개할 수 있다.

탐색 정지:

```bash
ros2 topic pub --once /explore/resume std_msgs/msg/Bool "{data: false}"
```

탐색 재개:

```bash
ros2 topic pub --once /explore/resume std_msgs/msg/Bool "{data: true}"
```

---

## 13. 탐색 후 지도 저장

탐색이 끝나면 현재 SLAM 지도를 저장할 수 있다.

```bash
mkdir -p "$TB3_WS/maps"
```

```bash
ros2 run nav2_map_server map_saver_cli -f "$TB3_WS/maps/explore_map"
```

결과:

```text
maps/explore_map.pgm
maps/explore_map.yaml
```

slam_toolbox 자체 저장 기능을 사용할 수도 있지만, 이 문서에서는 Nav2 map saver를 통한 `.pgm + .yaml` 저장을 우선 기준으로 둔다.

---

## 14. 실행 순서 요약

```text
0. m-explore-ros2 clone 및 colcon build
1. Gazebo 실행
2. slam_toolbox online_async 실행
3. nav2_bringup navigation_launch.py 실행
4. explore_lite 실행
5. RViz에서 /map, /scan, /explore/frontiers 확인
6. 탐색 완료 후 map_saver_cli로 지도 저장
```

---

## 15. 이 문서의 위치

이 문서는 기존 Day 15 흐름의 확장 문서이다.

기존 흐름:

```text
02_cartographer_slam_map_save.md
03_amcl_localization.md
04_navigation2_run.md
```

자동 탐색 확장 흐름:

```text
06_auto_exploration_explore_lite.md
```

두 흐름은 목적이 다르므로 명령어를 섞어서 실행하지 않는다.
