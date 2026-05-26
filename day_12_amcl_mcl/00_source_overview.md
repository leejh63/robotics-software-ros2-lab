# 00. Day 12 소스 구성 요약

이 문서는 Day 12 AMCL/MCL 실습에서 참고해야 할 문서, 코드, 설정 파일의 위치를 정리한다.

---

## 1. 원본 실습 정리 파일

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
workspace: projects/ros2_navigation_lab
package: lee_robot_description
map: src/lee_robot_description/maps/slam_map.yaml
world: slam.world
map topic: /lee/map
scan topic: /lee/scan
cmd_vel topic: /lee/cmd_vel
map frame: map_lee
odom frame: odom_lee
base frame: base_footprint
```

---

## 3. 실제 실행 관련 launch/config 파일

```text
projects/ros2_navigation_lab/src/lee_robot_description/launch/localization.launch.py
projects/ros2_navigation_lab/src/lee_robot_description/launch/nav2.launch.py
projects/ros2_navigation_lab/src/lee_robot_description/config/amcl_param.yaml
projects/ros2_navigation_lab/src/lee_robot_description/rviz/amcl.rviz
```

| 파일 | 역할 |
|---|---|
| `localization.launch.py` | Gazebo, robot_state_publisher, spawn_entity, map_server, amcl, lifecycle_manager, RViz를 한 번에 띄우는 localization 런치 |
| `nav2.launch.py` | `localization.launch.py`와 `nav2_navigation.launch.py`를 함께 include하는 상위 런치 |
| `amcl_param.yaml` | AMCL frame/topic, particle, motion model, laser model, update 조건 설정 |
| `amcl.rviz` | AMCL 확인용 RViz display 설정 |

주의:

```text
현재 폴더에는 legacy AMCL launch 파일이 없다.
AMCL 단독 확인은 localization.launch.py를 기준으로 본다.
Nav2까지 함께 실행할 때는 nav2.launch.py를 사용한다.
```

---

## 4. 명령어/트러블슈팅 실습 자료

```text
$SOURCE_NOTES/day_12/main/commands/amcl_local_cheatsheet.md
$SOURCE_NOTES/day_12/main/commands/amcl_현재_environment_topics.md
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
