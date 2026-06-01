# ROS2 Navigation Study Notes

ROS2 Navigation 실습 내용을 `topic`, `frame`, `message`, `action`, `parameter` 기준으로 재정리한 학습 노트입니다.

이 저장소의 목표는 RViz에서 보이는 결과를 ROS graph의 데이터 흐름으로 설명하는 것입니다. Gazebo, SLAM, AMCL, Nav2가 각각 어떤 데이터를 사용하고 어떤 결과를 내는지 단계별로 확인합니다.

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

## Rosbag 데이터 포함 여부

이 저장소에는 rosbag 원본 데이터는 포함하지 않았습니다. rosbag은 용량이 크고 실행 환경마다 다르므로 Git에는 올리지 않고, 실행할 때 사용자가 직접 준비한 bag 디렉토리를 지정합니다.

```bash
export BAG_DIR=/path/to/rosbag_directory
ros2 bag info "$BAG_DIR"
```

rosbag 기반 SLAM/Nav2 실행 흐름은 [`projects/ros2_navigation_lab/docs/BAG_SLAM_NAV2_WORKFLOW.md`](projects/ros2_navigation_lab/docs/BAG_SLAM_NAV2_WORKFLOW.md)와 [`projects/ros2_navigation_lab/docs/BAG_COMMANDS_ONLY.md`](projects/ros2_navigation_lab/docs/BAG_COMMANDS_ONLY.md)를 기준으로 봅니다.

---

핵심 관점은 다음과 같습니다.

```text
1. SLAM, AMCL, Nav2가 각각 해결하는 문제를 구분한다.
2. topic 이름과 message 내부 header.frame_id를 분리해서 본다.
3. package name, namespace, topic name, frame name을 섞지 않는다.
4. rosbag replay, TF, DWB, Behavior Tree 문제를 순서대로 디버깅한다.
5. 직접 작성한 설정과 ROS2/Nav2 패키지가 제공하는 기능을 구분한다.
```

---

## 먼저 볼 문서

| 목적 | 문서 |
|---|---|
| 빠른 시작 | [QUICK_START.md](QUICK_START.md) |
| 전체 색인 | [MASTER_INDEX.md](MASTER_INDEX.md) |
| Gazebo → SLAM → AMCL → Nav2 흐름 | [appendix/full_pipeline_reference.md](appendix/full_pipeline_reference.md) |
| rosbag 기반 SLAM/Nav2 실행 | [projects/ros2_navigation_lab/docs/BAG_SLAM_NAV2_WORKFLOW.md](projects/ros2_navigation_lab/docs/BAG_SLAM_NAV2_WORKFLOW.md), [projects/ros2_navigation_lab/docs/BAG_COMMANDS_ONLY.md](projects/ros2_navigation_lab/docs/BAG_COMMANDS_ONLY.md) |
| topic / frame / message / action 기준 | [appendix/table_reference_guide.md](appendix/table_reference_guide.md), [appendix/topic_frame_message_action_master_table.md](appendix/topic_frame_message_action_master_table.md) |
| 명령어 실행 규칙 | [appendix/command_execution_conventions.md](appendix/command_execution_conventions.md) |
| 문제 발생 시 빠른 진단 | [appendix/troubleshooting_quick_diagnosis.md](appendix/troubleshooting_quick_diagnosis.md) |
| Runtime 결과 기록 양식 | [RUNTIME_VALIDATION_RESULT_TEMPLATE.md](RUNTIME_VALIDATION_RESULT_TEMPLATE.md) |
| Notebook/asset 정리 결과 | [projects/python_opencv_foundation_lab/ASSET_NOTEBOOK_INVENTORY_STAGE06.md](projects/python_opencv_foundation_lab/ASSET_NOTEBOOK_INVENTORY_STAGE06.md) |

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
| [day_15_turtlebot3_cartographer_amcl_nav2/](day_15_turtlebot3_cartographer_amcl_nav2/) | TurtleBot3 Burger 기반 Gazebo, Cartographer SLAM, AMCL, Navigation2, Explore Lite 자동 탐색 재현 문서 |
| [10_selected_deep_dives/](10_selected_deep_dives/) | 핵심 개념 선별 심화 |
| [11_navigation_debug_deep_dives/](11_navigation_debug_deep_dives/) | rosbag-frame, DWB, Behavior Tree, navigation failure 디버깅 심화 |
| [appendix/](appendix/) | 빠른 참조, 용어집, 명령어, topic/frame/action 표, troubleshooting |

---

## 실행 코드 프로젝트

학습 노트와 실행 코드는 분리했습니다. `day_*` 폴더는 개념과 흐름 정리이고, `projects/` 아래는 실습 코드를 모아둔 workspace입니다.

| 위치 | 역할 |
|---|---|
| [projects/python_opencv_foundation_lab/](projects/python_opencv_foundation_lab/) | Python, NumPy, OpenCV, Camera Calibration, YOLO, Kalman foundation 실습 |
| [projects/ros2_foundation_lab/](projects/ros2_foundation_lab/) | ROS2 topic, service, action, custom interface, launch, camera, TF 기초 실습 |
| [projects/ros2_navigation_lab/](projects/ros2_navigation_lab/) | Gazebo, SLAM, AMCL, Nav2 실행 흐름 정리 |
| [projects/ros2_pid_arm_lab/](projects/ros2_pid_arm_lab/) | Gazebo + ros2_control 기반 1-DOF arm PID 제어 실습 |
| [projects/path_planning_algorithms_lab/](projects/path_planning_algorithms_lab/) | Dijkstra, A*, RRT, RRT* notebook 실습 |

---

## 공개 전 정적 검증

수정본을 공유하거나 commit하기 전에는 아래 정적 검증을 먼저 실행합니다.

```bash
python3 tools/static_repo_check.py
```

이 검사는 Python/XML/YAML/notebook JSON/notebook output/Markdown link/민감 경로 잔존 여부만 확인합니다. ROS2, Gazebo, Nav2, camera, controller runtime 성공은 각 프로젝트의 runtime checklist와 session guide에서 별도로 확인해야 합니다. 결과를 공개 문서에 반영하기 전에는 [RUNTIME_VALIDATION_RESULT_TEMPLATE.md](RUNTIME_VALIDATION_RESULT_TEMPLATE.md)에 실제 관찰 결과를 남깁니다. 원본 archive와 현재 수정본의 차이는 [REVISION_SUMMARY.md](REVISION_SUMMARY.md)와 [docs/revision_history/](docs/revision_history/)에서 확인합니다.

---

## 실행 예시의 표기 규칙

문서의 명령어는 로컬 환경값을 그대로 노출하지 않도록 placeholder를 사용합니다.

단, `projects/ros2_navigation_lab`의 복사 실행 예시는 현재 정리한 실습 환경에 맞춰 `/lee`, `map_lee`, `odom_lee`를 우선 사용합니다. `/robot_ns`, `map_robot_ns`, `odom_robot_ns`는 일반 설명용 placeholder입니다.

| Placeholder | 의미 |
|---|---|
| `$ROS2_WS` | ROS2 workspace 경로 |
| `$BAG_DIR` | 사용자가 직접 준비한 rosbag 디렉토리 경로 |
| `$ROS2_WORK_DIR` | ROS2 실습 상위 작업 디렉터리 |
| `robot_ns` | 로봇별 ROS namespace 예시 |
| `ROBOT_IP` | 로봇 또는 개발 보드의 로컬 IP 예시 |
| `ROBOT_HOST.local` | 로봇 또는 개발 보드의 mDNS hostname 예시 |
| `$SOURCE_ARCHIVE` | 정리 기준이 된 개인 실습 자료 묶음 |
| `$SOURCE_NOTES` | 정리 기준이 된 개인 실습 노트 경로 |

일반화된 placeholder 예시:

```bash
cd $ROS2_WS
source install/setup.bash
export BAG_DIR=/path/to/rosbag_directory
ros2 bag play "$BAG_DIR" --clock --remap /scan:=/robot_ns/scan
```

위 예시는 일반화된 표기입니다. 현재 `projects/ros2_navigation_lab`를 그대로 실행할 때는 `/robot_ns`가 아니라 `/lee` 기준 명령어를 먼저 봅니다. 실행할 때는 placeholder를 본인 환경에 맞게 바꿔야 합니다.

