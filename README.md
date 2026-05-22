# ROS2 Navigation Study Notes

ROS2 Navigation 학습 과정을 정리한 개인 학습 노트 저장소입니다.

이 저장소는 완성된 자율주행 프로젝트나 공식 튜토리얼이 아닙니다. ROS2 기초부터 Gazebo, SLAM, AMCL, Nav2까지 이어지는 실습 내용을 다시 설명할 수 있도록 정리한 학습 기록입니다. GitHub 업로드와 비공개 학습 데이터 사용을 고려해 로컬 사용자명, 절대경로, IP, hostname 등은 placeholder로 일반화했습니다.

---

## 바로 보기

| 목적 | 먼저 볼 문서 |
|---|---|
| 전체 구조를 빠르게 파악 | [QUICK_START.md](QUICK_START.md) |
| 전체 학습 색인 확인 | [MASTER_INDEX.md](MASTER_INDEX.md) |
| Gazebo → SLAM → AMCL → Nav2 흐름 확인 | [appendix/full_pipeline_reference.md](appendix/full_pipeline_reference.md) |
| topic / frame / message / action 통합 표 확인 | [appendix/topic_frame_message_action_master_table.md](appendix/topic_frame_message_action_master_table.md) |
| 명령어 실행 전 규칙 확인 | [appendix/command_execution_conventions.md](appendix/command_execution_conventions.md) |
| 문제 발생 시 빠른 진단 | [appendix/troubleshooting_quick_diagnosis.md](appendix/troubleshooting_quick_diagnosis.md) |
| 업로드 전 검수 기준 확인 | [FINAL_UPLOAD_AUDIT.md](FINAL_UPLOAD_AUDIT.md) |

---

## 학습 범위

```text
Python / NumPy / OpenCV
→ ROS2 node / topic / service / action / launch / parameter
→ TF2 / sensor topic / rosbag
→ Gazebo / URDF / Xacro / plugin
→ SLAM Toolbox
→ AMCL / MCL / particle filter
→ Nav2 lifecycle / costmap / planner / controller / Behavior Tree
→ rosbag-frame / DWB / Navigation failure debugging
```

핵심 목표는 `보이는 결과`를 ROS graph의 데이터 흐름으로 설명하는 것입니다.

```text
1. SLAM, AMCL, Nav2가 각각 어떤 문제를 해결하는지 구분한다.
2. topic 이름과 message 내부 header.frame_id를 분리해서 본다.
3. package name, namespace, topic name, frame name을 섞지 않는다.
4. rosbag replay, TF, DWB, Behavior Tree 문제를 순서대로 디버깅한다.
5. 학습 기록을 나중에 포트폴리오 README나 발표 자료로 확장할 수 있게 정리한다.
```

---

## 추천 학습 경로

### 1. 전체 흐름 복습

```text
QUICK_START.md
→ MASTER_INDEX.md
→ appendix/learning_flow_one_page.md
→ appendix/full_pipeline_reference.md
→ day_01_05_python_opencv_foundation/README.md
→ day_06_09_ros2_foundation/README.md
→ day_10_gazebo_urdf/README.md
→ day_11_slam/README.md
→ day_12_amcl_mcl/README.md
→ day_13_nav2/README.md
```

### 2. ROS2 Navigation 핵심만 빠르게 보기

```text
appendix/full_pipeline_reference.md
→ appendix/topic_frame_message_action_master_table.md
→ 10_selected_deep_dives/01_tf_topic_namespace_frame_id.md
→ 10_selected_deep_dives/02_laserscan_odom_tf_to_slam.md
→ 10_selected_deep_dives/03_slam_vs_amcl.md
→ 10_selected_deep_dives/05_nav2_goal_to_cmd_vel.md
```

### 3. 디버깅 중심으로 보기

```text
appendix/ros2_navigation_debug_order.md
→ appendix/troubleshooting_quick_diagnosis.md
→ appendix/troubleshooting_index.md
→ 11_navigation_debug_deep_dives/01_rosbag_topic_remap_vs_frame_id.md
→ 11_navigation_debug_deep_dives/02_dwb_local_controller_practical.md
→ 11_navigation_debug_deep_dives/03_behavior_tree_nav2_practical.md
→ 11_navigation_debug_deep_dives/04_navigation_failure_diagnosis_map.md
```

---

## 폴더 구조

| 위치 | 역할 |
|---|---|
| [day_01_05_python_opencv_foundation/](day_01_05_python_opencv_foundation/) | Python, NumPy, OpenCV, camera calibration, YOLO, Kalman 기반 |
| [day_06_09_ros2_foundation/](day_06_09_ros2_foundation/) | ROS2 workspace, package, node, topic, service, action, launch, parameter, TF, rosbag |
| [day_10_gazebo_urdf/](day_10_gazebo_urdf/) | URDF/Xacro, Gazebo plugin, sensor topic, RViz 연결 |
| [day_11_slam/](day_11_slam/) | SLAM Toolbox, map 생성, map 저장, rosbag offline SLAM |
| [day_12_amcl_mcl/](day_12_amcl_mcl/) | AMCL, MCL, particle filter, initial pose, localization |
| [day_13_nav2/](day_13_nav2/) | Nav2 stack, lifecycle, costmap, planner, controller, action goal, `/cmd_vel` |
| [10_selected_deep_dives/](10_selected_deep_dives/) | 계속 헷갈리는 핵심 개념 선별 심화 |
| [11_navigation_debug_deep_dives/](11_navigation_debug_deep_dives/) | rosbag-frame, DWB, Behavior Tree, navigation failure 디버깅 심화 |
| [appendix/](appendix/) | 빠른 참조, 용어집, 명령어, topic/frame/action 표, troubleshooting |

---

## 명령어 실행 전 주의

명령어를 그대로 복사하기 전에 [appendix/command_execution_conventions.md](appendix/command_execution_conventions.md)를 먼저 확인합니다.

```text
lee_robot_description  = ROS2 package name 예시
robot_ns               = ROS namespace 예시
/robot_ns/scan          = topic name 예시
map_robot_ns            = TF frame name 예시
```

`ros2 bag play --remap`은 topic 이름만 바꾸고 message 내부 `header.frame_id`는 바꾸지 않습니다. rosbag, SLAM, AMCL, Nav2 문제를 디버깅할 때는 topic 이름과 frame 이름을 반드시 분리해서 봅니다.

---

## Placeholder 규칙

| Placeholder | 의미 |
|---|---|
| `$ROS2_WS` | ROS2 workspace 경로 |
| `$ROS2_WORK_DIR` | ROS2 실습 상위 작업 디렉터리 |
| `USER` | 로컬 사용자명 예시 |
| `HOST` | 로컬 PC hostname 예시 |
| `ROBOT_IP` | 로봇 또는 개발 보드의 로컬 IP 예시 |
| `ROBOT_HOST.local` | 로봇 또는 개발 보드의 mDNS hostname 예시 |
| `user_ns` | 사용자별 ROS namespace 예시 |
| `robot_ns` | 로봇별 ROS namespace 예시 |

예시:

```bash
cd $ROS2_WS
source install/setup.bash

ros2 bag play <bag_dir> --clock \
  --remap /scan:=/robot_ns/scan
```

실제로 실행할 때는 placeholder를 본인 환경에 맞게 바꿔야 합니다.

---
