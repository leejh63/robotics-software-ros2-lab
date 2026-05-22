# 00. Day 12 Source File Map

이 문서는 Day 12 AMCL/MCL 정리에 사용한 실제 파일 위치를 정리한다. 목적은 “어떤 문서가 어떤 코드/설정 파일을 설명하는지”를 빠르게 찾는 것이다.

---

## 1. 실습 정리 파일

```text
$SOURCE_NOTES/day_12/README.md
$SOURCE_NOTES/day_12/amcl_mcl_beginner_notes_lee.md
$SOURCE_NOTES/day_12/amcl_params_lee_example.yaml
$SOURCE_NOTES/day_12/12_01_AMCL-MCL.ipynb
```

역할:

```text
README.md
  Day 12 전체 자료의 원래 안내 문서

amcl_mcl_beginner_notes_lee.md
  노트북 예제와 AMCL 개념을 연결한 초보자용 정리

amcl_params_lee_example.yaml
  현재 frame/topic 이름에 맞춘 AMCL 파라미터 예시

12_01_AMCL-MCL.ipynb
  Python으로 particle filter / MCL 동작을 직접 보는 교육용 노트북
```

---

## 2. Day 12 main 문서

```text
$SOURCE_NOTES/day_12/main/amcl_day12_integrated_guide.md
```

역할:

```text
기존 AMCL 실습 흐름을 현재 lee_robot_description 환경에 맞게 다시 번역한 통합 문서
```

이 문서에서 가져온 핵심 기준:

```text
workspace: $ROS2_WS
package: lee_robot_description
map: $ROS2_WS/slam_map.yaml
world: slam.world
map topic: /robot_ns/map
scan topic: /robot_ns/scan
cmd_vel topic: /robot_ns/cmd_vel
map frame: map_robot_ns
odom frame: odom_robot_ns
base frame: base_footprint
```

---

## 3. 실제 실행 관련 launch/config 파일

```text
$ROS2_WS/lee_robot_description/launch/amcl.launch.py
$ROS2_WS/lee_robot_description/launch/amcl_full.launch.py
$ROS2_WS/lee_robot_description/config/amcl_param.yaml
$ROS2_WS/lee_robot_description/rviz/amcl.rviz
```

| 파일 | 역할 |
|---|---|
| `amcl.launch.py` | Gazebo, robot_state_publisher, spawn_entity, RViz를 띄우는 분리 실행용 런치 |
| `amcl_full.launch.py` | Gazebo, robot_state_publisher, spawn_entity, map_server, amcl, lifecycle_manager, RViz를 한 번에 띄우는 통합 런치 |
| `amcl_param.yaml` | AMCL frame/topic, particle, motion model, laser model, update 조건 설정 |
| `amcl.rviz` | AMCL 확인용 RViz display 설정 |

주의:

```text
amcl.launch.py는 map_server와 amcl을 직접 실행하지 않는다.
amcl_full.launch.py는 map_server와 amcl까지 같이 실행한다.
```

---

## 4. 명령어/트러블슈팅 실습 자료

```text
$SOURCE_NOTES/day_12/main/commands/amcl_local_cheatsheet.md
$SOURCE_NOTES/day_12/main/commands/amcl_current_environment_topics.md
$SOURCE_NOTES/day_12/main/commands/amcl_full_launch_progress.md
$SOURCE_NOTES/day_12/main/commands/nav2_action_goal_direct_guide.md
$SOURCE_NOTES/day_12/main/troubleshooting/amcl_troubleshooting.md
```

현재 AMCL 범위에 맞춰 아래로 재분리했다.

```text
commands/amcl_local_cheatsheet.md
commands/amcl_topic_tf_diagnostics.md
commands/initialpose_cli_examples.md
troubleshooting/amcl_day12_troubleshooting.md
```

---

## 5. Python 노트북과 실제 AMCL의 관계

```text
12_01_AMCL-MCL.ipynb
  파티클 필터 원리를 보기 위한 교육용 시뮬레이션

nav2_amcl
  실제 ROS2/Nav2에서 동작하는 AMCL 노드
```

노트북은 이해용이다. 실제 AMCL과 다른 점이 있다.

```text
노트북은 Ground Truth pose를 알고 있는 교육용 코드가 일부 포함되어 있다.
실제 AMCL은 Ground Truth를 모르고 /map, /scan, TF, /initialpose만으로 위치를 추정한다.
```

따라서 노트북을 볼 때는 “AMCL 구현체를 그대로 재현했다”가 아니라 “AMCL 내부 사고방식을 시각화했다”로 이해해야 한다.
