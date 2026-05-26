# Appendix

이 폴더는 날짜별 문서를 보다가 자주 다시 확인하게 되는 기준표, 명령어, 용어, 진단 순서를 모아둔 참조 영역이다. 모든 파일을 처음부터 끝까지 읽기보다, 필요한 상황에 맞춰 선택해서 본다.

---

## 1. 가장 먼저 볼 문서

| 문서 | 용도 |
|---|---|
| [learning_flow_one_page.md](learning_flow_one_page.md) | 전체 학습 흐름 1페이지 요약 |
| [full_pipeline_reference.md](full_pipeline_reference.md) | Gazebo → SLAM → AMCL → Nav2 연결 흐름 |
| [command_execution_conventions.md](command_execution_conventions.md) | 명령어 실행 전 package / namespace / topic / frame 구분 |
| [troubleshooting_quick_diagnosis.md](troubleshooting_quick_diagnosis.md) | 문제가 생겼을 때 첫 확인 순서 |
| [table_reference_guide.md](table_reference_guide.md) | 여러 topic/frame/action 표의 역할 구분 |

---

## 2. Topic / Frame / Message / Action 표

표 문서는 여러 개지만 역할이 다르다.

| 문서 | 언제 보는가 |
|---|---|
| [topic_frame_message_action_master_table.md](topic_frame_message_action_master_table.md) | 전체 기준표가 필요할 때 |
| [full_topic_frame_message_action_table.md](full_topic_frame_message_action_table.md) | Day 01~13 범위를 넓게 훑을 때 |
| [topic_frame_table.md](topic_frame_table.md) | Day 10 Gazebo/URDF 기준 topic-frame을 볼 때 |
| [slam_topic_frame_table.md](slam_topic_frame_table.md) | Day 11 SLAM topic/TF를 볼 때 |
| [amcl_topic_frame_table.md](amcl_topic_frame_table.md) | Day 12 AMCL topic/TF를 볼 때 |
| [nav2_topic_frame_action_table.md](nav2_topic_frame_action_table.md) | Day 13 Nav2 topic/frame/action을 볼 때 |

표끼리 표현이 다르게 보이면 [table_reference_guide.md](table_reference_guide.md)를 먼저 보고, 통합 기준은 [topic_frame_message_action_master_table.md](topic_frame_message_action_master_table.md)를 따른다.

---

## 3. 명령어와 검증 순서

| 문서 | 용도 |
|---|---|
| [full_command_quick_reference.md](full_command_quick_reference.md) | 전체 명령어 빠른 참조 |
| [validation_sequence_gazebo_slam_amcl_nav2.md](validation_sequence_gazebo_slam_amcl_nav2.md) | Gazebo → SLAM → AMCL → Nav2 순차 검증 |
| [ros2_navigation_debug_order.md](ros2_navigation_debug_order.md) | ROS graph → topic → message → frame → lifecycle 순서 점검 |
| [nav2_dwb_bt_debug_reference.md](nav2_dwb_bt_debug_reference.md) | Nav2 controller, DWB, Behavior Tree 문제 확인 |
| [rosbag_frame_debug_reference.md](rosbag_frame_debug_reference.md) | rosbag replay와 frame_id 문제 확인 |

---

## 4. 파라미터와 기능별 빠른 참조

| 문서 | 용도 |
|---|---|
| [amcl_parameter_quick_reference.md](amcl_parameter_quick_reference.md) | AMCL 주요 파라미터 의미 |
| [nav2_parameter_quick_reference.md](nav2_parameter_quick_reference.md) | Nav2 planner/controller/costmap 파라미터 의미 |
| [amcl_namespace_cases.md](amcl_namespace_cases.md) | AMCL topic namespace case 구분 |
| [gazebo_urdf_quick_reference.md](gazebo_urdf_quick_reference.md) | Gazebo / URDF / Xacro 핵심 구분 |
| [ros2_foundation_quick_reference.md](ros2_foundation_quick_reference.md) | ROS2 기본 통신 구조 빠른 참조 |
| [python_opencv_yolo_quick_reference.md](python_opencv_yolo_quick_reference.md) | Python / OpenCV / YOLO 기초 참조 |

---

## 5. 배경지식과 용어

| 문서 | 용도 |
|---|---|
| [background_knowledge_map.md](background_knowledge_map.md) | 필요한 배경지식 지도 |
| [background_urdf_xacro_gazebo.md](background_urdf_xacro_gazebo.md) | URDF, Xacro, Gazebo, RViz 관계 |
| [glossary_ros2_navigation_pipeline.md](glossary_ros2_navigation_pipeline.md) | ROS2 Navigation 용어집 |
| [environment_reference.md](environment_reference.md) | 예시 실행 환경 기준 |
| [external_package_boundary.md](external_package_boundary.md) | 직접 작성한 부분과 외부 패키지 경계 |
| [content_consistency_map.md](content_consistency_map.md) | 문서 간 설명이 다를 때 기준 문서 판단 |

---

## 6. Day 연결 문서

| 문서 | 연결 범위 |
|---|---|
| [day01_05_to_day06_13_connection.md](day01_05_to_day06_13_connection.md) | Python/OpenCV에서 ROS2 Navigation까지 |
| [day06_09_to_day10_13_connection.md](day06_09_to_day10_13_connection.md) | ROS2 기초에서 Gazebo/SLAM/AMCL/Nav2까지 |
| [day10_to_day11_slam_connection.md](day10_to_day11_slam_connection.md) | Gazebo/URDF에서 SLAM까지 |
| [day11_to_day12_amcl_connection.md](day11_to_day12_amcl_connection.md) | SLAM map에서 AMCL localization까지 |
| [day12_to_day13_nav2_connection.md](day12_to_day13_nav2_connection.md) | AMCL localization에서 Nav2 navigation까지 |

---

## 7. 문제 해결 색인

| 문서 | 용도 |
|---|---|
| [troubleshooting_quick_diagnosis.md](troubleshooting_quick_diagnosis.md) | 증상별 첫 확인 명령 |
| [troubleshooting_index.md](troubleshooting_index.md) | Day별 troubleshooting 문서 색인 |
