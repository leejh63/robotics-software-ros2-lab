# Day 01~14 정리 진행 현황

확인일: 2026-05-27  
확인 경로: `/home/jaeholee/Downloads/test`

이 문서는 현재 저장소에서 Day 01부터 Day 14까지 어떤 범위가 정리되어 있고, 어떤 부분이 아직 보강 대상인지 확인하기 위한 진행 현황 문서다.

---

## 1. 전체 결론

Day 01~14 전체 범위는 저장소 안에 모두 정리되어 있다. 다만 정리 방식은 날짜별 14개 폴더가 아니라 아래처럼 묶여 있다.

```text
Day 01~05 -> day_01_05_python_opencv_foundation/
Day 06~09 -> day_06_09_ros2_foundation/
Day 10    -> day_10_gazebo_urdf/
Day 11    -> day_11_slam/
Day 12    -> day_12_amcl_mcl/
Day 13    -> day_13_nav2/
Day 14    -> day_14_control_and_path_planning/
```

현재 상태를 한 줄로 정리하면 다음과 같다.

```text
내용 정리 관점: Day 01~14 전체 정리됨
실행 재현성 관점: Day 10~14는 실행 프로젝트와 직접 연결됨
보강 필요 관점: Day 01~09는 원본 코드/노트북이 저장소 안에 완전히 들어온 구조는 아님
```

---

## 2. 폴더별 정리량

| 위치 | 파일 수 | Markdown | 역할 |
|---|---:|---:|---|
| `day_01_05_python_opencv_foundation/` | 16 | 16 | Python, OpenCV, YOLO, Kalman, Raspberry Pi 기초 정리 |
| `day_06_09_ros2_foundation/` | 18 | 18 | ROS2 package, node, topic, service, action, launch, TF, rosbag 정리 |
| `day_10_gazebo_urdf/` | 16 | 16 | Gazebo, URDF, Xacro, sensor plugin 정리 |
| `day_11_slam/` | 17 | 17 | SLAM Toolbox, map 생성, rosbag offline SLAM 정리 |
| `day_12_amcl_mcl/` | 21 | 21 | AMCL, MCL, particle filter, localization 정리 |
| `day_13_nav2/` | 19 | 19 | Nav2 lifecycle, costmap, planner, controller 정리 |
| `day_14_control_and_path_planning/` | 23 | 23 | PID 제어와 경로 탐색 정리 |
| `appendix/` | 35 | 35 | 전체 빠른 참조, 표, troubleshooting, 연결 문서 |
| `10_selected_deep_dives/` | 7 | 7 | 핵심 개념 심화 |
| `11_navigation_debug_deep_dives/` | 6 | 6 | Navigation 디버깅 심화 |

실행 코드는 `projects/` 아래에 분리되어 있다.

| 위치 | 역할 | 현재 상태 |
|---|---|---|
| `projects/ros2_navigation_lab/` | Day 10~13 Gazebo, SLAM, AMCL, Nav2 실행 workspace | `colcon build` 확인됨 |
| `projects/ros2_pid_arm_lab/` | Day 14 PID arm 실행 workspace | `colcon build` 확인됨 |
| `projects/path_planning_algorithms_lab/` | Day 14 Dijkstra, A*, RRT, RRT* notebook | notebook 4개 존재 |

---

## 3. Day별 진행 상태

| Day | 주제 | 현재 정리 위치 | 상태 | 메모 |
|---:|---|---|---|---|
| 01 | Python, NumPy, Matplotlib | `day_01_05_python_opencv_foundation/` | 정리 완료 | 문법, ndarray, 시각화가 ROS2 node/callback 이해로 연결되도록 정리됨 |
| 02 | OOP, 파일, JSON, thread/process | `day_01_05_python_opencv_foundation/` | 정리 완료 | runtime notes에 race condition, 파일 생성 순서, queue 폭주 같은 주의점까지 정리됨 |
| 03 | OpenCV basic, edge, color tracking | `day_01_05_python_opencv_foundation/` | 정리 완료 | ROS2 camera topic 처리와 연결되는 관점으로 정리됨 |
| 04 | Camera calibration, YOLO, Kalman | `day_01_05_python_opencv_foundation/` | 정리 완료 | bbox, confidence, Kalman predict/update, ROS2 custom msg 연결까지 정리됨 |
| 05 | Raspberry Pi / TurtleBot 환경 메모 | `day_01_05_python_opencv_foundation/` | 부분 정리 | 설치 기록 성격이 강함. 재현 가능한 설치 runbook으로 보강하면 좋음 |
| 06 | ROS2 workspace, package, node, topic | `day_06_09_ros2_foundation/` | 정리 완료 | package/file/executable/node/topic 이름 구분이 잘 정리됨 |
| 07 | pub/sub, service, action, custom interface | `day_06_09_ros2_foundation/` | 정리 완료 | Nav2 action과 lifecycle service를 이해하기 위한 기반으로 연결됨 |
| 08 | launch, parameter, custom msg, debug | `day_06_09_ros2_foundation/` | 정리 완료 | launch와 YAML parameter가 Day 10~13으로 이어지는 구조가 정리됨 |
| 09 | TF2, sensor topic, rosbag, camera-YOLO-TF | `day_06_09_ros2_foundation/` | 정리 완료 | TF frame/topic 구분, rosbag replay, camera detection TF 흐름이 정리됨 |
| 10 | Gazebo / URDF / Xacro | `day_10_gazebo_urdf/`, `projects/ros2_navigation_lab/` | 정리 완료 | 실행 코드, launch, world, URDF, RViz, simple LiDAR avoidance까지 연결됨 |
| 11 | SLAM | `day_11_slam/`, `projects/ros2_navigation_lab/` | 정리 완료 | SLAM Toolbox, map save/load, map yaml/pgm, offline SLAM 개념 정리됨 |
| 12 | AMCL / MCL | `day_12_amcl_mcl/`, `projects/ros2_navigation_lab/` | 정리 완료 | particle filter, AMCL parameter, initial pose, map->odom TF까지 정리됨 |
| 13 | Nav2 | `day_13_nav2/`, `projects/ros2_navigation_lab/` | 정리 완료, 일부 문서 보정 필요 | Nav2 stack 흐름은 정리됨. 단, 실행 분리 설명 일부는 `nav2.launch.py` 중복 실행으로 읽힐 수 있어 보정 필요 |
| 14 | PID control, path planning | `day_14_control_and_path_planning/`, `projects/ros2_pid_arm_lab/`, `projects/path_planning_algorithms_lab/` | 정리 완료 | PID arm ROS2 workspace와 path planning notebook이 분리되어 있음 |

---

## 4. 현재 강점

1. Day 10~13 흐름이 한 프로젝트로 이어진다.

```text
Gazebo/URDF -> SLAM -> AMCL -> Nav2
```

이 흐름이 `projects/ros2_navigation_lab/`에 실제 launch, config, map, rviz, world 파일로 연결되어 있다.

2. topic, frame, message, action 기준으로 정리되어 있다.

문서 전체가 단순 개념 요약이 아니라 다음 질문에 답하도록 구성되어 있다.

```text
어떤 node가 어떤 topic을 publish/subscribe 하는가?
topic 이름과 frame_id는 어떻게 다른가?
map -> odom -> base -> sensor TF chain은 누가 만드는가?
Nav2 goal이 어떻게 /cmd_vel까지 이어지는가?
```

3. Appendix와 deep dive가 잘 분리되어 있다.

빠른 참조, topic/frame/action 표, troubleshooting, SLAM/AMCL/Nav2 연결 문서가 `appendix/`에 모여 있어 복습과 디버깅에 유리하다.

---

## 5. 보강 필요 항목

### 5.1 Day 01~09 원본 실행 코드 정리

Day 01~09 문서는 원본 자료를 `$SOURCE_ARCHIVE`, `$SOURCE_NOTES`, `$ROS2_WS` 같은 placeholder로 참조한다. 현재 저장소에는 해당 원본 코드와 노트북이 완전히 들어와 있지 않다.

보강 방향:

```text
1. Day 01~05 최소 실행 예제를 projects/python_opencv_foundation_lab/로 분리
2. Day 06~09 ROS2 기본 패키지를 projects/ros2_foundation_lab/로 분리
3. 문서의 $SOURCE_* 참조를 실제 저장소 상대경로로 바꾸기
```

### 5.2 Day 05 환경 구축 문서 보강

Day 05는 Raspberry Pi / TurtleBot 환경 메모로 정리되어 있지만, 현재는 완성된 설치 매뉴얼보다는 기록 성격이 강하다.

보강 방향:

```text
사전 조건
설치 명령
네트워크 설정
SSH 확인
ROS2 통신 확인
카메라/센서 확인
실패 시 체크리스트
```

### 5.3 Day 13 실행 문서 보정

`projects/ros2_navigation_lab/docs/COMMANDS_ONLY.md` 기준으로는 아래 구분이 정확하다.

```text
통합 실행:
  ros2 launch lee_robot_description nav2.launch.py

분리 실행:
  ros2 launch lee_robot_description localization.launch.py
  ros2 launch lee_robot_description nav2_navigation.launch.py
```

반면 `day_13_nav2/05_execution_split_and_goal_send.md`는 simulation + localization 단계에서 `nav2.launch.py`를 쓰는 것처럼 설명한다. 현재 launch 구조상 `nav2.launch.py`는 localization과 Nav2 navigation을 함께 include하므로, 이후 `nav2_navigation.launch.py`를 또 실행하면 중복 실행될 수 있다.

보강 방향:

```text
day_13_nav2/05_execution_split_and_goal_send.md의 터미널 1 명령을
localization.launch.py 기준으로 수정
```

### 5.4 검증 자동화

빌드 확인은 되었지만 자동 테스트는 아직 약하다.

현재 확인된 상태:

```text
lee_robot_description: colcon build 성공
pid_arm_lab: colcon build 성공
Markdown local link: 깨진 링크 없음
Python syntax: 오류 없음
```

추가로 필요한 것:

```text
ROS launch --show-args smoke check
YAML parameter key validation
notebook 실행 검증
Nav2 command 문서와 launch 구조 일치 검사
flake8 line length 정리
```

---

## 6. 다음 작업 우선순위

1. `day_13_nav2/05_execution_split_and_goal_send.md`의 실행 명령 보정
2. Day 01~09에 대해 day별 체크리스트 추가
3. Day 05를 재현 가능한 설치 runbook으로 승격
4. Day 01~09 원본 코드 중 핵심만 `projects/` 아래 실행 가능한 형태로 이관
5. `lee_robot_description` flake8 line length 정리
6. notebook과 ROS launch smoke test 추가

---

## 7. 현재 판정

```text
Day 01~14 학습 내용 정리: 완료
Day 10~14 실행 프로젝트 연결: 완료
Day 01~09 실행 코드 재현성: 부분 완료
문서 내부 링크 상태: 양호
다음 보강의 핵심: Day 13 실행 설명 보정, Day 01~09 실행 예제 이관
```
