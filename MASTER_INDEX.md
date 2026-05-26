# ROS2 Navigation 학습 문서 전체 색인

이 문서는 저장소 전체의 읽는 순서를 정리한다. 파일 목록을 전부 나열하기보다, 목적에 따라 어느 문서를 먼저 보면 되는지 안내한다.

---

## 1. 전체 학습 지도

```text
Python / NumPy / OpenCV
  ↓
Camera calibration / YOLO / Kalman filter
  ↓
ROS2 workspace / package / node
  ↓
Topic / Service / Action / Custom interface
  ↓
Launch / Parameter / Debug command
  ↓
TF2 / Sensor topic / Rosbag replay
  ↓
Gazebo / URDF / Xacro / Plugin / RViz
  ↓
SLAM Toolbox: scan + odom + TF → map
  ↓
AMCL: map + scan + odom + TF → estimated pose
  ↓
Nav2: goal + pose + costmap → path → cmd_vel
  ↓
Control / Path planning: PID / Dijkstra / A* / RRT / RRT*
  ↓
Navigation debugging: rosbag-frame / DWB / Behavior Tree
```

---

## 2. 처음 볼 문서

| 목적 | 문서 |
|---|---|
| 저장소 목적과 구조 확인 | [README.md](README.md) |
| 빠른 실행/읽기 순서 확인 | [QUICK_START.md](QUICK_START.md) |
| 전체 흐름 1페이지 요약 | [appendix/learning_flow_one_page.md](appendix/learning_flow_one_page.md) |
| Gazebo → SLAM → AMCL → Nav2 연결 | [appendix/full_pipeline_reference.md](appendix/full_pipeline_reference.md) |
| 명령어 실행 기준 | [appendix/command_execution_conventions.md](appendix/command_execution_conventions.md) |
| 문제 발생 시 빠른 진단 | [appendix/troubleshooting_quick_diagnosis.md](appendix/troubleshooting_quick_diagnosis.md) |

---

## 3. 핵심 질문 체크리스트

```text
1. 이 기능은 내가 작성한 코드인가, 외부 ROS2/Nav2 패키지가 제공한 기능인가?
2. 어떤 node가 실행되고 있는가?
3. 각 node는 어떤 topic을 publish/subscribe 하는가?
4. topic 이름과 message 내부 header.frame_id를 구분하고 있는가?
5. frame 이름과 TF topic을 구분하고 있는가?
6. launch 파일은 어떤 node와 parameter를 동시에 올리는가?
7. YAML parameter 하나가 실제 동작의 어느 부분을 바꾸는가?
8. package name, namespace, topic name, frame name을 서로 섞고 있지 않은가?
9. rosbag remap은 topic 이름만 바꾸는가, frame_id까지 바꾸는가?
10. SLAM과 AMCL 중 누가 map -> odom TF를 발행해야 하는 상황인가?
11. Nav2 goal이 /cmd_vel로 바뀌기까지 어떤 서버들이 개입하는가?
12. path는 있는데 /cmd_vel이 없을 때 DWB/controller 쪽을 의심할 수 있는가?
13. 실패 지점을 Behavior Tree 단계로 나눠 볼 수 있는가?
```

---

## 4. 날짜별 문서

| 순서 | 문서 | 주제 |
|---:|---|---|
| 1 | [day_01_05_python_opencv_foundation/README.md](day_01_05_python_opencv_foundation/README.md) | Python, OpenCV, camera, YOLO, Kalman |
| 2 | [day_06_09_ros2_foundation/README.md](day_06_09_ros2_foundation/README.md) | ROS2 node/topic/service/action/launch/TF/rosbag |
| 3 | [day_10_gazebo_urdf/README.md](day_10_gazebo_urdf/README.md) | Gazebo, URDF/Xacro, plugin, RViz |
| 4 | [day_11_slam/README.md](day_11_slam/README.md) | SLAM Toolbox, map 생성, rosbag offline SLAM |
| 5 | [day_12_amcl_mcl/README.md](day_12_amcl_mcl/README.md) | AMCL, MCL, particle filter, localization |
| 6 | [day_13_nav2/README.md](day_13_nav2/README.md) | Nav2 lifecycle, planner, controller, goal, cmd_vel |
| 7 | [day_14_control_and_path_planning/README.md](day_14_control_and_path_planning/README.md) | PID 제어, ros2_control, Dijkstra/A*/RRT/RRT* |

---

## 5. 선별 심화 문서

| 문서 | 주제 |
|---|---|
| [10_selected_deep_dives/README.md](10_selected_deep_dives/README.md) | 선별 심화 개요 |
| [10_selected_deep_dives/01_tf_topic_namespace_frame_id.md](10_selected_deep_dives/01_tf_topic_namespace_frame_id.md) | TF/topic/namespace/frame_id 구분 |
| [10_selected_deep_dives/02_laserscan_odom_tf_to_slam.md](10_selected_deep_dives/02_laserscan_odom_tf_to_slam.md) | LaserScan/Odom/TF에서 SLAM까지 |
| [10_selected_deep_dives/03_slam_vs_amcl.md](10_selected_deep_dives/03_slam_vs_amcl.md) | SLAM과 AMCL 차이 |
| [10_selected_deep_dives/04_amcl_parameters_practical_meaning.md](10_selected_deep_dives/04_amcl_parameters_practical_meaning.md) | AMCL parameter 실전 의미 |
| [10_selected_deep_dives/05_nav2_goal_to_cmd_vel.md](10_selected_deep_dives/05_nav2_goal_to_cmd_vel.md) | Nav2 goal에서 `/cmd_vel`까지 |
| [10_selected_deep_dives/06_selected_deep_dive_review_questions.md](10_selected_deep_dives/06_selected_deep_dive_review_questions.md) | 심화 복습 질문 |

---

## 6. Navigation 디버깅 심화 문서

| 문서 | 주제 |
|---|---|
| [11_navigation_debug_deep_dives/README.md](11_navigation_debug_deep_dives/README.md) | Navigation 디버깅 심화 개요 |
| [11_navigation_debug_deep_dives/01_rosbag_topic_remap_vs_frame_id.md](11_navigation_debug_deep_dives/01_rosbag_topic_remap_vs_frame_id.md) | rosbag topic remap vs frame_id |
| [11_navigation_debug_deep_dives/02_dwb_local_controller_practical.md](11_navigation_debug_deep_dives/02_dwb_local_controller_practical.md) | DWB local controller |
| [11_navigation_debug_deep_dives/03_behavior_tree_nav2_practical.md](11_navigation_debug_deep_dives/03_behavior_tree_nav2_practical.md) | Nav2 Behavior Tree |
| [11_navigation_debug_deep_dives/04_navigation_failure_diagnosis_map.md](11_navigation_debug_deep_dives/04_navigation_failure_diagnosis_map.md) | Navigation failure diagnosis map |
| [11_navigation_debug_deep_dives/05_navigation_debug_review_questions.md](11_navigation_debug_deep_dives/05_navigation_debug_review_questions.md) | 디버깅 복습 질문 |

---

## 7. 실행 코드 프로젝트

| 위치 | 역할 |
|---|---|
| [projects/ros2_navigation_lab/README.md](projects/ros2_navigation_lab/README.md) | Gazebo → SLAM → AMCL → Nav2 실행 검증 workspace |
| [projects/ros2_pid_arm_lab/README.md](projects/ros2_pid_arm_lab/README.md) | Gazebo + ros2_control 기반 1-DOF arm PID 제어 workspace |
| [projects/path_planning_algorithms_lab/README.md](projects/path_planning_algorithms_lab/README.md) | Dijkstra, A*, RRT, RRT* notebook 실습 |

---

## 8. Appendix 읽는 법

Appendix는 전부 순서대로 읽는 폴더가 아니다. 필요한 상황에 맞춰 골라 본다.

| 상황 | 먼저 볼 문서 |
|---|---|
| 전체 흐름 확인 | [appendix/learning_flow_one_page.md](appendix/learning_flow_one_page.md), [appendix/full_pipeline_reference.md](appendix/full_pipeline_reference.md) |
| 명령어 실행 | [appendix/command_execution_conventions.md](appendix/command_execution_conventions.md), [appendix/full_command_quick_reference.md](appendix/full_command_quick_reference.md) |
| topic/frame/action 확인 | [appendix/table_reference_guide.md](appendix/table_reference_guide.md) |
| 기준표 확인 | [appendix/topic_frame_message_action_master_table.md](appendix/topic_frame_message_action_master_table.md) |
| 문제 진단 | [appendix/troubleshooting_quick_diagnosis.md](appendix/troubleshooting_quick_diagnosis.md), [appendix/troubleshooting_index.md](appendix/troubleshooting_index.md) |
| 용어 확인 | [appendix/glossary_ros2_navigation_pipeline.md](appendix/glossary_ros2_navigation_pipeline.md) |
| 직접 작성/설정한 범위 확인 | [appendix/external_package_boundary.md](appendix/external_package_boundary.md) |
