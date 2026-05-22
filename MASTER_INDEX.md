# MASTER_INDEX - ROS2 Navigation Study Notes

이 문서는 저장소 전체의 학습 색인입니다. 단순 파일 목록이 아니라, ROS2 Navigation을 어떤 순서와 관점으로 이해해야 하는지 정리합니다.

---

## 0. GitHub에서 처음 볼 때

| 목적 | 문서 |
|---|---|
| 저장소 구조를 빠르게 파악 | [QUICK_START.md](QUICK_START.md) |
| 전체 학습 흐름을 한 페이지로 확인 | [appendix/learning_flow_one_page.md](appendix/learning_flow_one_page.md) |
| Gazebo → SLAM → AMCL → Nav2 연결 확인 | [appendix/full_pipeline_reference.md](appendix/full_pipeline_reference.md) |
| 명령어 실행 전 규칙 확인 | [appendix/command_execution_conventions.md](appendix/command_execution_conventions.md) |
| 문제 발생 시 빠른 진단 | [appendix/troubleshooting_quick_diagnosis.md](appendix/troubleshooting_quick_diagnosis.md) |

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
Navigation debugging: rosbag-frame / DWB / Behavior Tree
```

핵심은 `보이는 결과`가 아니라 `데이터 흐름`입니다. RViz에서 로봇이 움직이거나 지도가 보이는 현상을 topic, frame, message, action, parameter 단위로 설명할 수 있어야 합니다.

---

## 2. 핵심 질문 체크리스트

학습 문서를 읽을 때 아래 질문을 계속 기준으로 삼습니다.

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
14. 같은 개념이 여러 문서에 있을 때 기준 문서를 확인했는가?
```

---

## 3. 목적별 빠른 시작

### 전체를 처음부터 복습

| 순서 | 문서 |
|---:|---|
| 1 | [README.md](README.md) |
| 2 | [appendix/learning_flow_one_page.md](appendix/learning_flow_one_page.md) |
| 3 | [appendix/full_pipeline_reference.md](appendix/full_pipeline_reference.md) |
| 4 | [day_01_05_python_opencv_foundation/README.md](day_01_05_python_opencv_foundation/README.md) |
| 5 | [day_06_09_ros2_foundation/README.md](day_06_09_ros2_foundation/README.md) |
| 6 | [day_10_gazebo_urdf/README.md](day_10_gazebo_urdf/README.md) |
| 7 | [day_11_slam/README.md](day_11_slam/README.md) |
| 8 | [day_12_amcl_mcl/README.md](day_12_amcl_mcl/README.md) |
| 9 | [day_13_nav2/README.md](day_13_nav2/README.md) |

### 명령어를 직접 실행하기 전

| 문서 | 확인할 것 |
|---|---|
| [appendix/command_execution_conventions.md](appendix/command_execution_conventions.md) | package name, namespace, topic, frame, placeholder 구분 |
| [appendix/full_command_quick_reference.md](appendix/full_command_quick_reference.md) | 전체 실습 명령어 빠른 참조 |
| [appendix/validation_sequence_gazebo_slam_amcl_nav2.md](appendix/validation_sequence_gazebo_slam_amcl_nav2.md) | Gazebo → SLAM → AMCL → Nav2 실행 검증 순서 |


### GitHub 업로드 직전

| 문서 | 확인할 것 |
|---|---|
| [GITHUB_UPLOAD_GUIDE.md](GITHUB_UPLOAD_GUIDE.md) | 업로드 대상, 제외 대상, grep 검수, 커밋 예시 |
| [FINAL_UPLOAD_AUDIT.md](FINAL_UPLOAD_AUDIT.md) | 최종 구조와 안전성 검사 결과 |
| [MODIFICATION_LOG.md](MODIFICATION_LOG.md) | 정제 작업 이력 |


### 문제가 발생했을 때

| 문서 | 확인할 것 |
|---|---|
| [appendix/troubleshooting_quick_diagnosis.md](appendix/troubleshooting_quick_diagnosis.md) | 증상별 첫 확인 명령과 이동 경로 |
| [appendix/ros2_navigation_debug_order.md](appendix/ros2_navigation_debug_order.md) | ROS graph -> topic -> message -> frame -> lifecycle 순서 |
| [appendix/troubleshooting_index.md](appendix/troubleshooting_index.md) | Day별 troubleshooting 문서 색인 |

### 중복되거나 충돌해 보이는 설명을 확인할 때

| 문서 | 확인할 것 |
|---|---|
| [appendix/content_consistency_map.md](appendix/content_consistency_map.md) | 개념별 기준 문서와 충돌 판단 순서 |
| [appendix/command_execution_conventions.md](appendix/command_execution_conventions.md) | package, namespace, topic, frame 구분 |
| [appendix/topic_frame_message_action_master_table.md](appendix/topic_frame_message_action_master_table.md) | topic/frame/message/action 기준 표 |

### ROS2 기본기만 복습

| 문서 | 확인할 것 |
|---|---|
| [day_06_09_ros2_foundation/02_workspace_package_node_topic.md](day_06_09_ros2_foundation/02_workspace_package_node_topic.md) | workspace, package, executable, node 관계 |
| [day_06_09_ros2_foundation/03_pubsub_service_action_interface.md](day_06_09_ros2_foundation/03_pubsub_service_action_interface.md) | topic/service/action 구분 |
| [day_06_09_ros2_foundation/04_launch_parameter_custom_msg_debug.md](day_06_09_ros2_foundation/04_launch_parameter_custom_msg_debug.md) | launch, parameter, custom interface |
| [day_06_09_ros2_foundation/05_tf2_sensor_rosbag_foundation.md](day_06_09_ros2_foundation/05_tf2_sensor_rosbag_foundation.md) | TF2, sensor topic, rosbag |

### SLAM / AMCL / Nav2 연결만 복습

| 문서 | 확인할 것 |
|---|---|
| [appendix/full_pipeline_reference.md](appendix/full_pipeline_reference.md) | 전체 pipeline |
| [appendix/validation_sequence_gazebo_slam_amcl_nav2.md](appendix/validation_sequence_gazebo_slam_amcl_nav2.md) | 검증 순서 |
| [day_11_slam/02_slam_concepts_and_data_model.md](day_11_slam/02_slam_concepts_and_data_model.md) | SLAM 입력/출력 |
| [day_12_amcl_mcl/03_amcl_data_flow_and_tf.md](day_12_amcl_mcl/03_amcl_data_flow_and_tf.md) | AMCL topic/TF 흐름 |
| [day_13_nav2/03_costmap_topic_frame_flow.md](day_13_nav2/03_costmap_topic_frame_flow.md) | costmap topic/frame 흐름 |
| [day_13_nav2/05_execution_split_and_goal_send.md](day_13_nav2/05_execution_split_and_goal_send.md) | goal 전송과 `/cmd_vel` 흐름 |

### 디버깅 중심으로 복습

| 문서 | 확인할 것 |
|---|---|
| [appendix/ros2_navigation_debug_order.md](appendix/ros2_navigation_debug_order.md) | 기본 확인 순서 |
| [appendix/troubleshooting_index.md](appendix/troubleshooting_index.md) | 문제 유형별 색인 |
| [11_navigation_debug_deep_dives/01_rosbag_topic_remap_vs_frame_id.md](11_navigation_debug_deep_dives/01_rosbag_topic_remap_vs_frame_id.md) | rosbag remap과 frame_id 차이 |
| [11_navigation_debug_deep_dives/02_dwb_local_controller_practical.md](11_navigation_debug_deep_dives/02_dwb_local_controller_practical.md) | DWB가 `/cmd_vel`을 못 내는 조건 |
| [11_navigation_debug_deep_dives/03_behavior_tree_nav2_practical.md](11_navigation_debug_deep_dives/03_behavior_tree_nav2_practical.md) | BT 단계별 실패 위치 |
| [11_navigation_debug_deep_dives/04_navigation_failure_diagnosis_map.md](11_navigation_debug_deep_dives/04_navigation_failure_diagnosis_map.md) | navigation 실패 분류 지도 |

---

## 4. 폴더별 상세 색인

### day_01_05_python_opencv_foundation

| 문서 | 주제 |
|---|---|
| [README.md](day_01_05_python_opencv_foundation/README.md) | Day 01~05 개요 |
| [01_python_env_numpy_matplotlib.md](day_01_05_python_opencv_foundation/01_python_env_numpy_matplotlib.md) | Python 환경, NumPy, Matplotlib |
| [02_oop_file_json_thread_sensor_sim.md](day_01_05_python_opencv_foundation/02_oop_file_json_thread_sensor_sim.md) | OOP, file/json, thread, sensor simulation |
| [03_opencv_basic_edge_color_tracking.md](day_01_05_python_opencv_foundation/03_opencv_basic_edge_color_tracking.md) | OpenCV 기본, edge, color tracking |
| [04_camera_calibration_foundation.md](day_01_05_python_opencv_foundation/04_camera_calibration_foundation.md) | camera calibration |
| [05_yolo_kalman_foundation.md](day_01_05_python_opencv_foundation/05_yolo_kalman_foundation.md) | YOLO, Kalman filter |
| [06_robot_camera_practice_and_raspberry_pi.md](day_01_05_python_opencv_foundation/06_robot_camera_practice_and_raspberry_pi.md) | robot camera, Raspberry Pi 실습 |
| [07_connection_to_ros2_camera_yolo.md](day_01_05_python_opencv_foundation/07_connection_to_ros2_camera_yolo.md) | ROS2 camera/YOLO 연결 |
| [08_day01_05_review_questions.md](day_01_05_python_opencv_foundation/08_day01_05_review_questions.md) | 복습 질문 |
| [09_runtime_observations_without_code_changes.md](day_01_05_python_opencv_foundation/09_runtime_observations_without_code_changes.md) | 실행 관찰 기록 |

### day_06_09_ros2_foundation

| 문서 | 주제 |
|---|---|
| [README.md](day_06_09_ros2_foundation/README.md) | Day 06~09 개요 |
| [01_overview_reading_order.md](day_06_09_ros2_foundation/01_overview_reading_order.md) | 읽기 순서 |
| [02_workspace_package_node_topic.md](day_06_09_ros2_foundation/02_workspace_package_node_topic.md) | workspace/package/node/topic |
| [03_pubsub_service_action_interface.md](day_06_09_ros2_foundation/03_pubsub_service_action_interface.md) | pubsub/service/action/interface |
| [04_launch_parameter_custom_msg_debug.md](day_06_09_ros2_foundation/04_launch_parameter_custom_msg_debug.md) | launch/parameter/custom msg/debug |
| [05_tf2_sensor_rosbag_foundation.md](day_06_09_ros2_foundation/05_tf2_sensor_rosbag_foundation.md) | TF2/sensor/rosbag |
| [06_camera_yolo_tf_flow.md](day_06_09_ros2_foundation/06_camera_yolo_tf_flow.md) | camera/YOLO/TF 흐름 |
| [07_connection_to_day10_13.md](day_06_09_ros2_foundation/07_connection_to_day10_13.md) | 이후 Day와 연결 |
| [08_ros2_execution_model_from_code.md](day_06_09_ros2_foundation/08_ros2_execution_model_from_code.md) | 코드 기준 실행 모델 |
| [09_runtime_observations_without_code_changes.md](day_06_09_ros2_foundation/09_runtime_observations_without_code_changes.md) | 실행 관찰 기록 |
| [10_day06_09_review_questions.md](day_06_09_ros2_foundation/10_day06_09_review_questions.md) | 복습 질문 |

### day_10_gazebo_urdf

| 문서 | 주제 |
|---|---|
| [README.md](day_10_gazebo_urdf/README.md) | Day 10 개요 |
| [01_overview_flow.md](day_10_gazebo_urdf/01_overview_flow.md) | 전체 흐름 |
| [02_urdf_xacro_modeling.md](day_10_gazebo_urdf/02_urdf_xacro_modeling.md) | URDF/Xacro modeling |
| [03_robot_state_publisher_tf_flow.md](day_10_gazebo_urdf/03_robot_state_publisher_tf_flow.md) | robot_state_publisher와 TF |
| [04_gazebo_plugin_topic_flow.md](day_10_gazebo_urdf/04_gazebo_plugin_topic_flow.md) | Gazebo plugin과 topic |
| [05_world_launch_namespace.md](day_10_gazebo_urdf/05_world_launch_namespace.md) | world, launch, namespace |
| [06_rosbag_rviz_remap.md](day_10_gazebo_urdf/06_rosbag_rviz_remap.md) | rosbag/RViz/remap |
| [07_lidar_avoidance_and_laserscan.md](day_10_gazebo_urdf/07_lidar_avoidance_and_laserscan.md) | LiDAR avoidance, LaserScan |
| [08_runtime_observations_without_code_changes.md](day_10_gazebo_urdf/08_runtime_observations_without_code_changes.md) | 실행 관찰 기록 |
| [09_day10_review_questions.md](day_10_gazebo_urdf/09_day10_review_questions.md) | 복습 질문 |

### day_11_slam

| 문서 | 주제 |
|---|---|
| [README.md](day_11_slam/README.md) | Day 11 개요 |
| [01_overview_flow.md](day_11_slam/01_overview_flow.md) | SLAM 흐름 |
| [02_slam_concepts_and_data_model.md](day_11_slam/02_slam_concepts_and_data_model.md) | SLAM 개념과 데이터 모델 |
| [03_slam_toolbox_setup.md](day_11_slam/03_slam_toolbox_setup.md) | SLAM Toolbox 설정 |
| [04_mapping_and_map_save.md](day_11_slam/04_mapping_and_map_save.md) | mapping과 map 저장 |
| [05_map_loading_lifecycle.md](day_11_slam/05_map_loading_lifecycle.md) | map loading, lifecycle |
| [06_rosbag_offline_slam.md](day_11_slam/06_rosbag_offline_slam.md) | rosbag offline SLAM |
| [07_my_environment_execution_notes.md](day_11_slam/07_my_environment_execution_notes.md) | 일반화된 실행 환경 기록 |
| [08_runtime_observations_without_code_changes.md](day_11_slam/08_runtime_observations_without_code_changes.md) | 실행 관찰 기록 |
| [09_day11_review_questions.md](day_11_slam/09_day11_review_questions.md) | 복습 질문 |

### day_12_amcl_mcl

| 문서 | 주제 |
|---|---|
| [README.md](day_12_amcl_mcl/README.md) | Day 12 개요 |
| [01_overview_flow.md](day_12_amcl_mcl/01_overview_flow.md) | AMCL 흐름 |
| [02_mcl_particle_filter_concepts.md](day_12_amcl_mcl/02_mcl_particle_filter_concepts.md) | MCL/particle filter |
| [03_amcl_data_flow_and_tf.md](day_12_amcl_mcl/03_amcl_data_flow_and_tf.md) | AMCL data flow와 TF |
| [04_amcl_parameters_and_tuning.md](day_12_amcl_mcl/04_amcl_parameters_and_tuning.md) | AMCL parameter tuning |
| [05_execution_split_and_integrated_launch.md](day_12_amcl_mcl/05_execution_split_and_integrated_launch.md) | 실행 분리와 통합 launch |
| [06_rviz_initialpose_and_validation.md](day_12_amcl_mcl/06_rviz_initialpose_and_validation.md) | RViz initialpose, 검증 |
| [07_my_environment_execution_notes.md](day_12_amcl_mcl/07_my_environment_execution_notes.md) | 일반화된 실행 환경 기록 |
| [08_runtime_observations_without_code_changes.md](day_12_amcl_mcl/08_runtime_observations_without_code_changes.md) | 실행 관찰 기록 |
| [09_day12_review_questions.md](day_12_amcl_mcl/09_day12_review_questions.md) | 복습 질문 |

### day_13_nav2

| 문서 | 주제 |
|---|---|
| [README.md](day_13_nav2/README.md) | Day 13 개요 |
| [01_overview_flow.md](day_13_nav2/01_overview_flow.md) | Nav2 전체 흐름 |
| [02_nav2_stack_lifecycle_bt.md](day_13_nav2/02_nav2_stack_lifecycle_bt.md) | Nav2 stack, lifecycle, BT |
| [03_costmap_topic_frame_flow.md](day_13_nav2/03_costmap_topic_frame_flow.md) | costmap topic/frame 흐름 |
| [04_planner_controller_dwb.md](day_13_nav2/04_planner_controller_dwb.md) | planner, controller, DWB |
| [05_execution_split_and_goal_send.md](day_13_nav2/05_execution_split_and_goal_send.md) | 실행 분리와 goal 전송 |
| [06_rviz_nav2_validation_and_debug.md](day_13_nav2/06_rviz_nav2_validation_and_debug.md) | RViz Nav2 검증/디버깅 |
| [07_my_environment_execution_notes.md](day_13_nav2/07_my_environment_execution_notes.md) | 일반화된 실행 환경 기록 |
| [08_runtime_observations_without_code_changes.md](day_13_nav2/08_runtime_observations_without_code_changes.md) | 실행 관찰 기록 |
| [09_day13_review_questions.md](day_13_nav2/09_day13_review_questions.md) | 복습 질문 |

### selected_deep_dives

| 문서 | 주제 |
|---|---|
| [10_selected_deep_dives/README.md](10_selected_deep_dives/README.md) | 선별 심화 개요 |
| [01_tf_topic_namespace_frame_id.md](10_selected_deep_dives/01_tf_topic_namespace_frame_id.md) | TF/topic/namespace/frame_id 구분 |
| [02_laserscan_odom_tf_to_slam.md](10_selected_deep_dives/02_laserscan_odom_tf_to_slam.md) | LaserScan/Odom/TF에서 SLAM까지 |
| [03_slam_vs_amcl.md](10_selected_deep_dives/03_slam_vs_amcl.md) | SLAM과 AMCL 차이 |
| [04_amcl_parameters_practical_meaning.md](10_selected_deep_dives/04_amcl_parameters_practical_meaning.md) | AMCL parameter 실전 의미 |
| [05_nav2_goal_to_cmd_vel.md](10_selected_deep_dives/05_nav2_goal_to_cmd_vel.md) | Nav2 goal에서 `/cmd_vel`까지 |
| [06_selected_deep_dive_review_questions.md](10_selected_deep_dives/06_selected_deep_dive_review_questions.md) | 심화 복습 질문 |

### navigation_debug_deep_dives

| 문서 | 주제 |
|---|---|
| [11_navigation_debug_deep_dives/README.md](11_navigation_debug_deep_dives/README.md) | Navigation 디버깅 심화 개요 |
| [01_rosbag_topic_remap_vs_frame_id.md](11_navigation_debug_deep_dives/01_rosbag_topic_remap_vs_frame_id.md) | rosbag topic remap vs frame_id |
| [02_dwb_local_controller_practical.md](11_navigation_debug_deep_dives/02_dwb_local_controller_practical.md) | DWB local controller |
| [03_behavior_tree_nav2_practical.md](11_navigation_debug_deep_dives/03_behavior_tree_nav2_practical.md) | Nav2 Behavior Tree |
| [04_navigation_failure_diagnosis_map.md](11_navigation_debug_deep_dives/04_navigation_failure_diagnosis_map.md) | Navigation failure diagnosis map |
| [05_navigation_debug_review_questions.md](11_navigation_debug_deep_dives/05_navigation_debug_review_questions.md) | 디버깅 복습 질문 |

---

## 5. Appendix 빠른 참조

| 문서 | 용도 |
|---|---|
| [appendix/README.md](appendix/README.md) | appendix 전체 시작점 |
| [appendix/background_knowledge_map.md](appendix/background_knowledge_map.md) | 필요한 배경지식 지도 |
| [appendix/full_command_quick_reference.md](appendix/full_command_quick_reference.md) | 명령어 빠른 참조 |
| [appendix/full_topic_frame_message_action_table.md](appendix/full_topic_frame_message_action_table.md) | 전체 topic/frame/message/action 표 |
| [appendix/glossary_ros2_navigation_pipeline.md](appendix/glossary_ros2_navigation_pipeline.md) | 용어집 |
| [appendix/external_package_boundary.md](appendix/external_package_boundary.md) | 내가 작성한 부분과 외부 패키지 경계 |
| [appendix/my_environment_reference.md](appendix/my_environment_reference.md) | 일반화된 환경 기준 |
| [appendix/rosbag_frame_debug_reference.md](appendix/rosbag_frame_debug_reference.md) | rosbag/frame 디버깅 참조 |
| [appendix/nav2_dwb_bt_debug_reference.md](appendix/nav2_dwb_bt_debug_reference.md) | Nav2 DWB/BT 디버깅 참조 |
| [appendix/final_review_checklist.md](appendix/final_review_checklist.md) | 최종 복습 체크리스트 |

---

## 6. GitHub 업로드 전 확인

업로드 전에는 [GITHUB_UPLOAD_GUIDE.md](GITHUB_UPLOAD_GUIDE.md)와 [MODIFICATION_LOG.md](MODIFICATION_LOG.md)를 기준으로 확인합니다.

```text
[ ] 원본 학습 자료가 아니라 upload-safe 정제본을 올리는가?
[ ] README.md가 저장소 목적을 과장 없이 설명하는가?
[ ] MASTER_INDEX.md의 링크가 실제 파일과 일치하는가?
[ ] 개인 경로, IP, hostname, 사용자명이 남아 있지 않은가?
[ ] rosbag, build, install, log 같은 생성/대용량 파일이 제외되었는가?
[ ] 명령어 예시의 placeholder를 실제 환경에 맞게 바꿔야 한다는 점이 명시되어 있는가?
```
