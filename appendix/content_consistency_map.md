# 문서 기준과 중복 관리

이 문서는 저장소 안에서 같은 개념이 여러 번 반복될 때 어떤 문서를 기준으로 볼지 정리한 기준표다.

학습 노트 특성상 Day별 문서에는 같은 개념이 여러 번 등장한다. 반복 자체는 문제는 아니지만, 오래된 설명과 최신 설명이 충돌하지 않도록 기준 문서를 정해둔다.

---

## 1. 문서 유형별 역할

| 문서 유형 | 역할 | 충돌 시 우선순위 |
|---|---|---:|
| `README.md` | 저장소 목적과 읽기 순서 안내 | 1 |
| `MASTER_INDEX.md` | 전체 색인과 학습 경로 안내 | 1 |
| `appendix/*_reference.md` | 빠른 참조, 표, 실행 기준 | 2 |
| `10_selected_deep_dives/` | 핵심 개념의 기준 설명 | 2 |
| `11_navigation_debug_deep_dives/` | 디버깅 상황의 기준 설명 | 2 |
| `day_*` 본문 | 날짜별 학습 흐름과 실습 기록 | 3 |
| `commands/`, `troubleshooting/` | 실행/문제 해결 상황별 보조 문서 | 3 |
| `00_source_overview.md` | 실습 파일의 역할 지도 | 4 |

기준은 간단하다.

```text
개념을 다시 확인할 때:
  deep_dive 또는 appendix reference를 우선 본다.

그날 무엇을 어떻게 진행했는지 볼 때:
  day_* 문서를 본다.

```

---

## 2. 핵심 개념별 기준 문서

| 개념 | 기준 문서 | 보조 문서 |
|---|---|---|
| 전체 파이프라인 | `appendix/full_pipeline_reference.md` | `appendix/learning_flow_one_page.md` |
| package / namespace / topic / frame 구분 | `appendix/command_execution_conventions.md` | `10_selected_deep_dives/01_tf_topic_namespace_frame_id.md` |
| topic / frame / message / action 표 기준 | `appendix/table_reference_guide.md`, `appendix/topic_frame_message_action_master_table.md` | `appendix/full_topic_frame_message_action_table.md`, Day별 topic/frame 보조표 |
| rosbag remap과 frame_id 차이 | `11_navigation_debug_deep_dives/01_rosbag_topic_remap_vs_frame_id.md` | `10_selected_deep_dives/01_tf_topic_namespace_frame_id.md` |
| LaserScan / odom / TF에서 SLAM까지 | `10_selected_deep_dives/02_laserscan_odom_tf_to_slam.md` | `day_11_slam/02_slam_concepts_and_data_model.md` |
| SLAM과 AMCL 차이 | `10_selected_deep_dives/03_slam_vs_amcl.md` | `appendix/day11_to_day12_amcl_connection.md` |
| `map_robot_ns` / `odom_robot_ns` frame 이름을 쓰는 이유 | `day_12_amcl_mcl/background/map_odom_namespace_frames.md` | `appendix/topic_frame_message_action_master_table.md` |
| `map_robot_ns -> odom_robot_ns` 발행 주체 | `10_selected_deep_dives/03_slam_vs_amcl.md` | `day_12_amcl_mcl/03_amcl_data_flow_and_tf.md` |
| AMCL parameter 의미 | `10_selected_deep_dives/04_amcl_parameters_practical_meaning.md` | `appendix/amcl_parameter_quick_reference.md` |
| Nav2 goal에서 `/cmd_vel`까지 | `10_selected_deep_dives/05_nav2_goal_to_cmd_vel.md` | `day_13_nav2/05_execution_split_and_goal_send.md` |
| DWB local controller | `11_navigation_debug_deep_dives/02_dwb_local_controller_practical.md` | `day_13_nav2/04_planner_controller_dwb.md` |
| Behavior Tree | `11_navigation_debug_deep_dives/03_behavior_tree_nav2_practical.md` | `day_13_nav2/02_nav2_stack_lifecycle_bt.md` |
| Navigation 실패 진단 | `11_navigation_debug_deep_dives/04_navigation_failure_diagnosis_map.md` | `appendix/ros2_navigation_debug_order.md` |

---

## 3. 중복을 유지해도 되는 경우

아래 중복은 학습 문서에서 허용한다.

```text
1. 같은 개념을 Day 흐름 안에서 다시 설명하는 경우
2. 초보자용 개념 설명과 명령어 참조가 분리된 경우
3. 개념 문서와 troubleshooting 문서의 관점이 다른 경우
4. review question에서 핵심 내용을 반복해서 확인하는 경우
```

예를 들어 `topic remap은 frame_id를 바꾸지 않는다`는 내용은 여러 문서에 반복되어도 괜찮다. 이 개념은 SLAM, AMCL, Nav2 디버깅에서 계속 등장하는 핵심 함정이기 때문이다.

---

## 4. 정리해야 하는 중복

아래 중복은 줄이는 것이 좋다.

```text
1. 거의 같은 문장이 여러 파일에 그대로 반복되는 경우
2. 서로 다른 frame 이름을 같은 환경 기준처럼 설명하는 경우
3. package name 자리에 namespace가 들어간 경우
4. namespace 예시가 일부 문서에서는 robot_ns이고 일부 문서에서는 다른 값인 경우
5. 오래된 실행 방식과 현재 추천 실행 방식이 같은 우선순위로 보이는 경우
```

표 역할 자체가 헷갈릴 때는 `appendix/table_reference_guide.md`를 먼저 본다.

현재 저장소의 기본 표기 기준은 다음이다.

```text
package name 예시: lee_robot_description
namespace 예시: robot_ns
map frame 예시: map_robot_ns
odom frame 예시: odom_robot_ns
base frame 예시: base_footprint
scan frame 예시: base_scan
workspace 경로 예시: $ROS2_WS
```

---

## 5. 충돌이 의심될 때 판단 기준

문서끼리 다르게 보이면 아래 순서로 판단한다.

```text
1. 실제 실행 기준인지, 개념 설명 예시인지 먼저 구분한다.
2. package name, namespace, topic name, frame name 중 무엇을 말하는지 분리한다.
3. 명령어라면 appendix/command_execution_conventions.md 기준을 먼저 적용한다.
4. topic/frame/action 표라면 appendix/table_reference_guide.md에서 표 역할을 확인하고, appendix/topic_frame_message_action_master_table.md를 기준으로 본다.
5. SLAM/AMCL/Nav2 개념 충돌이면 10_selected_deep_dives 또는 11_navigation_debug_deep_dives를 기준으로 본다.
6. 날짜별 day_* 문서는 당시 학습 흐름 기록으로 보고, 최신 기준 문서와 다르면 기준 문서를 우선한다.
```

---

## 6. 현재 정리 상태

바로 삭제하지 않고 유지하는 중복도 있다. 이유는 다음과 같다.

```text
- Day별 흐름을 보존해야 이후 학습 과정을 추적할 수 있다.
- GitHub에서 처음 보는 사람은 같은 개념을 여러 위치에서 다시 만나는 편이 이해하기 쉽다.
- 다만 충돌 가능성이 있는 개념은 이 문서에서 기준 문서를 명확히 지정한다.
```

따라서 이 저장소는 `중복 제거형 문서`라기보다 `기준 문서를 둔 학습 노트형 문서`로 관리한다.
