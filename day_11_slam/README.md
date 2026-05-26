# Day 11 - SLAM 학습 정리

Day 11은 `Gazebo에서 만든 로봇/센서 출력`을 이용해서 **지도를 생성하는 단계**이다. 이 문서는 SLAM 실습을 다시 볼 때 아래 질문에 답할 수 있도록 정리한 학습 노트이다.

```text
1. SLAM Toolbox는 어떤 데이터를 받아서 지도를 만드는가?
2. /scan, /odom, /tf는 각각 왜 필요한가?
3. map_robot_ns, odom_robot_ns, base_footprint는 왜 분리되는가?
4. OccupancyGrid, .pgm, .yaml, .posegraph는 각각 무엇인가?
5. Gazebo live SLAM과 rosbag offline SLAM은 무엇이 다른가?
6. 예시 환경에서는 어떤 경로와 토픽 이름을 기준으로 실행해야 하는가?
```

---

## 1. Day 11의 핵심 위치

전체 흐름에서 Day 11은 아래 위치에 있다.

```text
Day 10 Gazebo / URDF / Xacro
  -> 로봇 모델, LiDAR, odometry, TF 생성

Day 11 SLAM
  -> /robot_ns/scan + /robot_ns/odom + /robot_ns/tf를 이용해 /robot_ns/map 생성

Day 12 AMCL
  -> 저장된 지도 위에서 현재 위치 추정

Day 13 Nav2
  -> 위치 추정 결과와 costmap을 이용해 목표점까지 이동
```

즉, Day 11은 “자율주행” 전체가 아니라 **자율주행에 쓸 지도 파일을 만드는 단계**이다.

---

## 2. 현재 실습 기준

현재 문서의 기준 환경은 다음이다.

```text
워크스페이스      $ROS2_WS
패키지            lee_robot_description
주요 launch        lee_robot_description/launch/slam.launch.py
SLAM 설정          lee_robot_description/config/slam_param.yaml
RViz 설정          lee_robot_description/rviz/slam.rviz
기본 world 후보    lee_world.world, simple_maze.world, slam.world
현재 지도 토픽     /robot_ns/map
현재 scan 토픽     /robot_ns/scan
현재 odom 토픽     /robot_ns/odom
현재 TF 토픽       /robot_ns/tf, /robot_ns/tf_static
지도 frame         map_robot_ns
odom frame         odom_robot_ns
base frame         base_footprint
LiDAR frame        base_scan
```

중요한 점은 현재 실습이 기본 `/map`, `/scan`, `/tf`가 아니라 `/robot_ns/map`, `/robot_ns/scan`, `/robot_ns/tf`처럼 **namespace가 붙은 토픽 구조**를 쓴다는 점이다.

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
  -> /robot_ns/scan

Gazebo diff_drive plugin
  -> /robot_ns/odom
  -> odom_robot_ns -> base_footprint TF

robot_state_publisher
  -> base_footprint -> base_link -> base_scan TF

SLAM Toolbox
  <- /robot_ns/scan
  <- /robot_ns/tf, /robot_ns/tf_static
  -> /robot_ns/map
  -> map_robot_ns -> odom_robot_ns TF

map_saver_cli
  <- /robot_ns/map
  -> slam_map.pgm + slam_map.yaml
```

SLAM은 `/robot_ns/scan` 하나만 보고 지도를 만드는 것이 아니다.  
`이 scan이 어느 좌표계에서 나왔는지`, `로봇이 시간에 따라 어떻게 움직였는지`, `오도메트리 오차를 어떻게 보정할지`까지 같이 본다.
