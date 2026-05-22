# Appendix README

이 폴더는 Day별 본문을 읽다가 빠르게 찾아봐야 하는 참조 문서 모음이다.

전체 참조 문서를 appendix에 모으고, 선별 심화 문서는 별도 `10_selected_deep_dives/` 폴더에 분리했다.

---

## 가장 먼저 볼 문서

```text
learning_flow_one_page.md
content_consistency_map.md
command_execution_conventions.md
my_environment_reference.md
full_command_quick_reference.md
validation_sequence_gazebo_slam_amcl_nav2.md
ros2_navigation_debug_order.md
troubleshooting_quick_diagnosis.md
troubleshooting_index.md
topic_frame_message_action_master_table.md
glossary_ros2_navigation_pipeline.md
```

---

## 선별 심화 문서와 함께 보면 좋은 문서

| 선별 심화 문서 | 같이 보면 좋은 appendix 문서 |
|---|---|
| `10_selected_deep_dives/01_tf_topic_namespace_frame_id.md` | `topic_frame_message_action_master_table.md`, `my_environment_reference.md` |
| `10_selected_deep_dives/02_laserscan_odom_tf_to_slam.md` | `slam_topic_frame_table.md`, `validation_sequence_gazebo_slam_amcl_nav2.md` |
| `10_selected_deep_dives/03_slam_vs_amcl.md` | `day11_to_day12_amcl_connection.md`, `full_pipeline_reference.md` |
| `10_selected_deep_dives/04_amcl_parameters_practical_meaning.md` | `amcl_parameter_quick_reference.md`, `amcl_topic_frame_table.md` |
| `10_selected_deep_dives/05_nav2_goal_to_cmd_vel.md` | `nav2_parameter_quick_reference.md`, `nav2_topic_frame_action_table.md` |

---


## 중복/충돌 기준

같은 개념이 여러 문서에 반복될 때는 `content_consistency_map.md`를 먼저 확인한다.

```text
개념 기준 문서가 필요함
  -> content_consistency_map.md

명령어 실행 기준이 필요함
  -> command_execution_conventions.md

전체 topic/frame/action 표가 필요함
  -> topic_frame_message_action_master_table.md
```

---

## 목적별 참조

### 전체 흐름 확인

```text
learning_flow_one_page.md
content_consistency_map.md
full_pipeline_reference.md
day01_05_to_day06_13_connection.md
day06_09_to_day10_13_connection.md
day10_to_day11_slam_connection.md
day11_to_day12_amcl_connection.md
day12_to_day13_nav2_connection.md
```

### 내 환경 기준 확인

```text
command_execution_conventions.md
my_environment_reference.md
full_command_quick_reference.md
validation_sequence_gazebo_slam_amcl_nav2.md
```

### topic/frame/action 확인

```text
topic_frame_message_action_master_table.md
full_topic_frame_message_action_table.md
topic_frame_table.md
slam_topic_frame_table.md
amcl_topic_frame_table.md
nav2_topic_frame_action_table.md
```

### 파라미터 확인

```text
amcl_parameter_quick_reference.md
nav2_parameter_quick_reference.md
```

### 문제 해결

```text
troubleshooting_quick_diagnosis.md
ros2_navigation_debug_order.md
troubleshooting_index.md
```

### 용어 확인

```text
glossary_ros2_navigation_pipeline.md
external_package_boundary.md
```
