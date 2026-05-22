# Selected Deep Dives - 선별 심화 보강

이 폴더는 Day 01~13 전체를 다시 깊게 파는 것이 아니라, 이후 학습/프로젝트/디버깅에서 계속 반복해서 등장하는 **핵심 개념 5개만 선별해서 깊게 정리**한 문서 모음이다.

현재 목표는 재현성 개선이 아니다.

```text
코드 수정 X
패키지 구조 변경 X
launch/config 수정 X
학습 이해도 보강 O
헷갈리는 개념 정리 O
내 환경 기준 해석 O
```

---

## 왜 전체를 더 파지 않고 5개만 골랐는가

SLAM, AMCL, Nav2는 끝까지 파면 범위가 너무 넓어진다.

예를 들어 AMCL만 해도 Bayes filter, motion model, sensor model, likelihood field, KLD sampling, resampling, covariance, TF drift까지 이어진다. Nav2도 behavior tree, planner, controller, DWB critic, costmap layer, lifecycle, action server까지 무한히 확장된다.

지금 단계에서 중요한 것은 모든 알고리즘을 논문 수준으로 외우는 것이 아니라, **내가 진행한 실습에서 데이터가 어디서 나오고 어디로 들어가는지 설명할 수 있는 것**이다.

그래서 아래 5개만 선별했다.

| 번호 | 문서 | 핵심 질문 |
|---|---|---|
| 1 | `01_tf_topic_namespace_frame_id.md` | topic 이름과 frame 이름은 왜 다르고, namespace는 어디에 적용되는가? |
| 2 | `02_laserscan_odom_tf_to_slam.md` | `/scan`, `/odom`, `/tf`는 SLAM에서 각각 어떤 역할을 하는가? |
| 3 | `03_slam_vs_amcl.md` | SLAM과 AMCL은 왜 동시에 같은 역할이 아니며, map->odom TF는 누가 발행하는가? |
| 4 | `04_amcl_parameters_practical_meaning.md` | AMCL 파라미터는 실제로 파티클 분포와 위치 추정에 어떤 영향을 주는가? |
| 5 | `05_nav2_goal_to_cmd_vel.md` | RViz/CLI goal은 어떻게 planner/controller를 거쳐 `/robot_ns/cmd_vel`로 바뀌는가? |

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

## 내 환경 기준

이 문서들은 아래 환경을 기준으로 설명한다.

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

## 이 폴더를 읽고 나면 설명할 수 있어야 하는 것

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

이 선별 심화 문서에서 일부러 깊게 들어가지 않은 것:

```text
- Nav2 Behavior Tree XML 커스터마이징
- DWB critic 수식 전체 분석
- SLAM backend graph optimization 수식
- AMCL 논문 수준의 확률 모델 전체
- Gazebo 물리 엔진 파라미터 튜닝
- package.xml/launch 경로 등 코드 재현성 개선
```

이 주제들은 이후 실제 프로젝트를 만들면서 필요해질 때 별도 단계로 다루는 것이 낫다.
