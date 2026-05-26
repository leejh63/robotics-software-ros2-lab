# Selected Deep Dives - 선별 심화 보강

이 폴더는 ROS2 Navigation 학습에서 반복해서 등장하는 핵심 개념을 선별해 정리한 문서 모음입니다.

코드 변경 내역이 아니라, 실습 중 자주 헷갈리는 데이터 흐름과 디버깅 기준을 이해하는 데 초점을 둡니다.

---

## 왜 5개 주제만 골랐는가

SLAM, AMCL, Nav2는 각각 별도의 깊은 주제입니다. 모든 알고리즘과 내부 구현을 한 번에 다루기보다, 실습 재현과 디버깅에 직접 연결되는 개념을 먼저 정리합니다.

이 폴더의 기준은 다음 질문에 답할 수 있는지입니다.

```text
1. 데이터가 어느 topic에서 publish 되는가?
2. message 내부 header.frame_id는 어떤 frame을 가리키는가?
3. TF tree는 어떤 frame 사이를 연결하는가?
4. SLAM, AMCL, Nav2 중 어느 패키지가 어떤 역할을 하는가?
5. 문제가 생겼을 때 topic, frame, parameter 중 어디부터 확인해야 하는가?
```

---

## 문서 목록

| 번호 | 문서 | 핵심 질문 |
|---|---|---|
| 1 | `01_tf_topic_namespace_frame_id.md` | topic 이름과 frame 이름은 왜 다르고, namespace는 어디에 적용되는가? |
| 2 | `02_laserscan_odom_tf_to_slam.md` | `/scan`, `/odom`, `/tf`는 SLAM에서 각각 어떤 역할을 하는가? |
| 3 | `03_slam_vs_amcl.md` | SLAM과 AMCL은 왜 같은 역할이 아니며, `map -> odom` TF는 누가 발행하는가? |
| 4 | `04_amcl_parameters_practical_meaning.md` | AMCL 파라미터는 파티클 분포와 위치 추정에 어떤 영향을 주는가? |
| 5 | `05_nav2_goal_to_cmd_vel.md` | RViz/CLI goal은 어떻게 planner/controller를 거쳐 `/robot_ns/cmd_vel`로 바뀌는가? |
| 6 | `06_selected_deep_dive_review_questions.md` | 핵심 개념 복습 질문 |

---

## 추천 읽기 순서

처음 보는 경우:

```text
01_tf_topic_namespace_frame_id.md
-> 02_laserscan_odom_tf_to_slam.md
-> 03_slam_vs_amcl.md
-> 04_amcl_parameters_practical_meaning.md
-> 05_nav2_goal_to_cmd_vel.md
```

문제가 생겨서 디버깅하는 경우:

```text
05_nav2_goal_to_cmd_vel.md
-> 01_tf_topic_namespace_frame_id.md
-> 02_laserscan_odom_tf_to_slam.md
-> 03_slam_vs_amcl.md
-> 04_amcl_parameters_practical_meaning.md
```

---

## 예시 환경 기준

이 문서들은 아래와 같은 예시 구조를 기준으로 설명합니다.

```text
workspace: $ROS2_WS
main package: lee_robot_description
localization launch: lee_robot_description/launch/nav2.launch.py
navigation launch: lee_robot_description/launch/nav2_navigation.launch.py
slam launch: lee_robot_description/launch/slam.launch.py
amcl params: lee_robot_description/config/amcl_param.yaml
nav2 params: lee_robot_description/config/nav2_params.yaml

main namespace: /robot_ns
map topic: /robot_ns/map
scan topic: /robot_ns/scan
odom topic: /robot_ns/odom
cmd_vel topic: /robot_ns/cmd_vel
TF topic: /robot_ns/tf, /robot_ns/tf_static
Nav2 action: /robot_ns/navigate_to_pose

map frame: map_robot_ns
odom frame: odom_robot_ns
base frame: base_footprint
scan frame: base_scan
```

---

## 읽고 나서 설명할 수 있어야 하는 것

```text
1. /robot_ns/scan이라는 topic 이름과 base_scan이라는 frame 이름이 왜 다른가
2. topic remap을 해도 header.frame_id가 자동으로 바뀌지 않는 이유
3. Gazebo plugin이 /robot_ns/scan, /robot_ns/odom, /robot_ns/cmd_vel을 어떻게 연결하는가
4. SLAM이 map을 만드는 과정과 AMCL이 map 위에서 위치를 찾는 과정의 차이
5. AMCL의 min_particles, max_particles, alpha*, z_hit, z_rand가 대략 어떤 의미인지
6. Nav2 goal이 들어왔을 때 planner_server와 controller_server가 각각 무엇을 하는지
7. /robot_ns/cmd_vel이 나오지 않을 때 어디부터 확인해야 하는지
```

---

## 범위 밖으로 둔 것

이 선별 심화 문서에서는 아래 주제를 깊게 다루지 않습니다.

```text
- Nav2 Behavior Tree XML 커스터마이징
- DWB critic 수식 전체 분석
- SLAM backend graph optimization 수식
- AMCL 확률 모델의 전체 수식 유도
- Gazebo 물리 엔진 파라미터 튜닝
- package.xml/launch 경로 등 재현성 개선 작업
```

위 주제들은 실제 프로젝트 요구사항이 생길 때 별도 문서로 분리하는 편이 낫습니다.
