# ROS2 Navigation Study Notes

`study/ros2-navigation-notes` 브랜치에 정리한 ROS2 Navigation 학습 노트입니다.  
완성형 자율주행 프로젝트나 공식 튜토리얼 대체 문서가 아니라, 실습 내용을 `topic`, `frame`, `message`, `action`, `parameter` 기준으로 다시 설명하기 위한 기록입니다.

---

## 핵심 범위

```text
Python / NumPy / OpenCV
→ ROS2 node / topic / service / action / launch / parameter
→ TF2 / sensor topic / rosbag
→ Gazebo / URDF / Xacro / plugin
→ SLAM Toolbox
→ AMCL / MCL / particle filter
→ Nav2 lifecycle / costmap / planner / controller / Behavior Tree
→ PID control / path planning algorithms
→ rosbag-frame / DWB / Navigation failure debugging
```

핵심 목표는 RViz에서 보이는 결과를 ROS graph의 데이터 흐름으로 설명하는 것입니다.

```text
1. SLAM, AMCL, Nav2가 각각 해결하는 문제를 구분한다.
2. topic 이름과 message 내부 header.frame_id를 분리해서 본다.
3. package name, namespace, topic name, frame name을 섞지 않는다.
4. rosbag replay, TF, DWB, Behavior Tree 문제를 순서대로 디버깅한다.
```

---

## 먼저 볼 문서

| 목적 | 문서 |
|---|---|
| 빠른 시작 | [QUICK_START.md](QUICK_START.md) |
| 전체 색인 | [MASTER_INDEX.md](MASTER_INDEX.md) |
| Gazebo → SLAM → AMCL → Nav2 흐름 | [appendix/full_pipeline_reference.md](appendix/full_pipeline_reference.md) |
| topic / frame / message / action 기준 | [appendix/table_reference_guide.md](appendix/table_reference_guide.md), [appendix/topic_frame_message_action_master_table.md](appendix/topic_frame_message_action_master_table.md) |
| 명령어 실행 규칙 | [appendix/command_execution_conventions.md](appendix/command_execution_conventions.md) |
| 문제 발생 시 빠른 진단 | [appendix/troubleshooting_quick_diagnosis.md](appendix/troubleshooting_quick_diagnosis.md) |

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
| [day_14_control_and_path_planning/](day_14_control_and_path_planning/) | PID 제어, ros2_control, Dijkstra/A*/RRT/RRT* 경로 탐색 |
| [10_selected_deep_dives/](10_selected_deep_dives/) | 핵심 개념 선별 심화 |
| [11_navigation_debug_deep_dives/](11_navigation_debug_deep_dives/) | rosbag-frame, DWB, Behavior Tree, navigation failure 디버깅 심화 |
| [appendix/](appendix/) | 빠른 참조, 용어집, 명령어, topic/frame/action 표, troubleshooting |


---

## 실행 코드 프로젝트

학습 노트와 실제 실행 코드는 분리했습니다. `day_*` 폴더는 개념과 흐름 정리이고, `projects/` 아래는 실행 가능한 코드입니다.

| 위치 | 역할 |
|---|---|
| [projects/ros2_navigation_lab/](projects/ros2_navigation_lab/) | Gazebo, SLAM, AMCL, Nav2 실행 검증 workspace |
| [projects/ros2_pid_arm_lab/](projects/ros2_pid_arm_lab/) | Gazebo + ros2_control 기반 1-DOF arm PID 제어 workspace |
| [projects/path_planning_algorithms_lab/](projects/path_planning_algorithms_lab/) | Dijkstra, A*, RRT, RRT* notebook 실습 |

---

## 실행 예시의 표기 규칙

문서의 명령어는 로컬 환경값을 그대로 노출하지 않도록 placeholder를 사용합니다.

| Placeholder | 의미 |
|---|---|
| `$ROS2_WS` | ROS2 workspace 경로 |
| `$ROS2_WORK_DIR` | ROS2 실습 상위 작업 디렉터리 |
| `robot_ns` | 로봇별 ROS namespace 예시 |
| `ROBOT_IP` | 로봇 또는 개발 보드의 로컬 IP 예시 |
| `ROBOT_HOST.local` | 로봇 또는 개발 보드의 mDNS hostname 예시 |
| `$SOURCE_ARCHIVE` | 정리 기준이 된 개인 실습 자료 묶음 |
| `$SOURCE_NOTES` | 정리 기준이 된 개인 실습 노트 경로 |

예시:

```bash
cd $ROS2_WS
source install/setup.bash
ros2 bag play <bag_dir> --clock --remap /scan:=/robot_ns/scan
```

실제로 실행할 때는 placeholder를 본인 환경에 맞게 바꿔야 합니다.

---

