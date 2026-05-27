# Day 11 - SLAM 학습 정리

Day 11은 `Gazebo에서 만든 로봇/센서 출력`을 이용해서 **지도를 생성하는 단계**이다. 이 문서는 SLAM 실습을 다시 볼 때 아래 질문에 답할 수 있도록 정리한 학습 노트이다.

```text
1. SLAM Toolbox는 어떤 데이터를 받아서 지도를 만드는가?
2. /scan, /odom, /tf는 각각 왜 필요한가?
3. map frame, odom frame, base frame은 왜 분리되는가?
4. OccupancyGrid, .pgm, .yaml, .posegraph는 각각 무엇인가?
5. Gazebo live SLAM과 rosbag offline SLAM은 무엇이 다른가?
6. 현재 projects/ros2_navigation_lab에서는 어떤 토픽과 frame 이름을 기준으로 실행해야 하는가?
```

---

## 1. Day 11의 핵심 위치

전체 흐름에서 Day 11은 아래 위치에 있다.

```text
Day 10 Gazebo / URDF / Xacro
  -> 로봇 모델, LiDAR, odometry, TF 생성

Day 11 SLAM
  -> /lee/scan + /lee/odom + /lee/tf를 이용해 /lee/map 생성

Day 12 AMCL
  -> 저장된 지도 위에서 현재 위치 추정

Day 13 Nav2
  -> 위치 추정 결과와 costmap을 이용해 목표점까지 이동
```

즉, Day 11은 “자율주행” 전체가 아니라 **자율주행에 쓸 지도 파일을 만드는 단계**이다.

---

## 2. 현재 실습 기준

현재 `projects/ros2_navigation_lab`의 실제 기본 실행 기준은 다음이다.

```text
워크스페이스      $ROS2_WS
패키지            lee_robot_description
주요 launch        lee_robot_description/launch/slam.launch.py
SLAM 설정          lee_robot_description/config/slam_param.yaml
RViz 설정          lee_robot_description/rviz/slam.rviz
기본 world 후보    lee_world.world, simple_maze.world, slam.world
현재 지도 토픽     /lee/map
현재 scan 토픽     /lee/scan
현재 odom 토픽     /lee/odom
현재 TF 토픽       /lee/tf, /lee/tf_static
지도 frame         map_lee
odom frame         odom_lee
base frame         base_footprint
LiDAR frame        base_scan
```

문서 전반에서 `/robot_ns`, `map_robot_ns`, `odom_robot_ns`가 나오면 일반 설명용 placeholder로 본다. 실제 현재 프로젝트 명령어를 복사할 때는 `/lee`, `map_lee`, `odom_lee` 기준으로 확인한다.

---

## 3. 추천 읽기 순서

```text
00_source_overview.md
  -> 실제 어떤 파일을 기준으로 보는지 확인

01_overview_flow.md
  -> Day 10에서 Day 11로 이어지는 전체 흐름 이해

02_slam_concepts_and_data_model.md
  -> SLAM, OccupancyGrid, scan matching, loop closure 개념 이해

03_slam_toolbox_setup.md
  -> slam.launch.py와 slam_param.yaml 구조 이해

04_mapping_and_map_save.md
  -> 실시간 Gazebo SLAM과 지도 저장 흐름 이해

05_map_loading_lifecycle.md
  -> 저장한 map을 map_server로 다시 띄우는 흐름 이해

06_rosbag_offline_slam.md
  -> rosbag으로 SLAM 재현하는 방법 이해

07_execution_notes.md
  -> 예시 환경 기준 실행/점검 방법 확인

08_runtime_notes.md
  -> 실행 중 헷갈리기 쉬운 관찰 사항과 확인 기준

09_day11_review_questions.md
  -> 복습 질문으로 이해 점검
```

---

## 4. Day 11에서 얻어야 하는 결론

Day 11의 핵심은 명령어가 아니라 이 구조다.

```text
Gazebo LiDAR plugin
  -> /lee/scan

Gazebo diff_drive plugin
  -> /lee/odom
  -> odom_lee -> base_footprint TF

robot_state_publisher
  -> base_footprint -> base_link -> base_scan TF

SLAM Toolbox
  <- /lee/scan
  <- /lee/tf, /lee/tf_static
  -> /lee/map
  -> map_lee -> odom_lee TF

map_saver_cli
  <- /lee/map
  -> slam_map.pgm + slam_map.yaml
```

SLAM은 `/lee/scan` 하나만 보고 지도를 만드는 것이 아니다. `이 scan이 어느 좌표계에서 나왔는지`, `로봇이 시간에 따라 어떻게 움직였는지`, `오도메트리 오차를 어떻게 보정할지`까지 같이 본다.

---

## 5. 자주 헷갈리는 구분

| 구분 | 현재 실행 기준 | 의미 |
|---|---|---|
| topic namespace | `/lee` | topic/action 이름 앞에 붙는 구분자 |
| map frame | `map_lee` | SLAM이 만드는 지도 좌표계 |
| odom frame | `odom_lee` | Gazebo odometry 기준 좌표계 |
| base frame | `base_footprint` | 로봇 바닥 중심 좌표계 |
| scan frame | `base_scan` | LiDAR 센서 좌표계 |

중요한 점:

```text
/lee/map은 topic 이름이다.
map_lee는 TF frame 이름이다.
둘은 비슷해 보여도 완전히 다른 개념이다.
```

---

## 6. 최소 실행 흐름

```bash
cd $ROS2_WS
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch lee_robot_description slam.launch.py
```

확인:

```bash
ros2 topic echo /lee/scan --once
ros2 topic echo /lee/map --once
ros2 run tf2_ros tf2_echo map_lee odom_lee \
  --ros-args -r /tf:=/lee/tf -r /tf_static:=/lee/tf_static
```

지도 저장:

```bash
ros2 run nav2_map_server map_saver_cli -f slam_map --ros-args -r map:=/lee/map
```

---

## 7. 다음 단계와 연결

Day 11에서 저장한 지도는 Day 12 AMCL과 Day 13 Nav2의 입력이 된다.

```text
Day 11 결과:
  slam_map.yaml
  slam_map.pgm

Day 12 사용:
  map_server가 /lee/map으로 지도 발행
  AMCL이 /lee/scan과 map을 비교해 위치 추정
  AMCL이 map_lee -> odom_lee TF 발행

Day 13 사용:
  Nav2 global costmap이 /lee/map 사용
  local costmap이 /lee/scan 사용
  planner/controller가 /lee/plan, /lee/cmd_vel 흐름 생성
```
