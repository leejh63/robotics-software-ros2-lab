# 11. Navigation Debug Deep Dives

이 폴더는 ROS2 Navigation 학습 중 실제 디버깅에서 자주 부딪힐 가능성이 높은 주제를 따로 모은 심화 문서다.

기본 개념 심화 문서에서는 ROS2 Navigation 전체에서 계속 헷갈릴 핵심 개념을 정리했고, 이 폴더에서는 그중 실제 실패 원인 분석에 직접 연결되는 주제를 다룬다.

```text
1. rosbag replay와 frame_id 문제
2. DWB local controller가 /cmd_vel을 고르는 방식
3. Behavior Tree가 Nav2 주행 절차를 관리하는 방식
```

---

## 1. 이 심화 문서를 따로 분리한 이유

이 세 주제는 모두 “코드가 문법적으로 맞는데 로봇이 안 움직이는 상황”과 연결된다.

예를 들면 다음과 같다.

```text
/robot_ns/scan은 보이는데 SLAM이 map을 못 만든다.
/robot_ns/map은 나오는데 AMCL particle이 수렴하지 않는다.
Nav2 action goal은 받는데 /robot_ns/cmd_vel이 나오지 않는다.
/robot_ns/cmd_vel은 나오는데 로봇이 벽 앞에서 이상하게 돈다.
RViz Goal은 실패하는데 CLI action goal은 성공한다.
```

이런 문제는 단순히 명령어를 외워서는 해결하기 어렵다. topic, frame, TF, costmap, controller, Behavior Tree의 역할을 구분해야 한다.

---

## 2. 문서 목록

| 문서 | 목적 |
|---|---|
| `01_rosbag_topic_remap_vs_frame_id.md` | rosbag의 topic remap과 message 내부 frame_id 차이 정리 |
| `02_dwb_local_controller_practical.md` | DWB가 여러 속도 후보 중 하나를 골라 `/cmd_vel`로 내는 흐름 정리 |
| `03_behavior_tree_nav2_practical.md` | BT Navigator가 planner/controller/recovery를 어떤 순서로 호출하는지 정리 |
| `04_navigation_failure_diagnosis_map.md` | 증상별로 rosbag/frame/DWB/BT 중 어디를 의심해야 하는지 정리 |
| `05_navigation_debug_review_questions.md` | Navigation Debug Deep Dive 복습 질문 |

---

## 3. 이번 단계의 범위

이번 단계는 코드 수정이나 재현성 개선이 아니다.

```text
코드 수정 X
launch/config 수정 X
패키지 구조 변경 X
colcon build 재검증 X
```

대신 아래를 목표로 한다.

```text
문제가 생겼을 때 원인을 분류할 수 있게 만들기
SLAM/AMCL/Nav2 실패 원인을 topic/frame/controller/BT 관점에서 나누기
예시 환경의 robot_ns namespace와 frame 구조를 기준으로 설명하기
```

---

## 4. 우선순위

셋 중 가장 중요도가 높은 것은 `rosbag topic remap vs frame_id` 문제다.

이유는 간단하다.

```text
rosbag replay는 학습/디버깅에서 계속 사용한다.
topic 이름은 remap할 수 있지만 message 내부 frame_id는 그대로 남는다.
frame이 안 맞으면 SLAM, AMCL, Nav2가 모두 연쇄적으로 실패할 수 있다.
```

DWB와 Behavior Tree는 지금 단계에서는 “튜닝 전문가 수준”까지 파지 않는다. 대신 Nav2가 왜 `/robot_ns/cmd_vel`을 만들거나 만들지 못하는지 판단할 수 있는 수준으로 정리한다.
