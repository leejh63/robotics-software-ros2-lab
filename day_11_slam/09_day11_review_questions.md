# 09. Day 11 복습 질문

이 문서는 Day 11 SLAM 학습 내용을 스스로 점검하기 위한 질문이다.

---

## 1. 전체 흐름

1. Day 10의 Gazebo/URDF 실습 결과가 Day 11 SLAM의 어떤 입력으로 이어지는가?
2. SLAM Toolbox가 `/robot_ns/scan` 하나만으로 지도를 만들 수 없는 이유는 무엇인가?
3. `/robot_ns/scan`, `/robot_ns/odom`, `/robot_ns/tf`는 각각 어떤 역할을 하는가?
4. `slam.launch.py`는 어떤 노드들을 동시에 실행하는가?
5. live SLAM과 offline SLAM의 차이는 무엇인가?

---

## 2. Topic과 message

1. `/robot_ns/scan`의 메시지 타입은 무엇인가?
2. `/robot_ns/map`의 메시지 타입은 무엇인가?
3. `LaserScan.header.frame_id`가 중요한 이유는 무엇인가?
4. map_saver_cli에서 `-t /robot_ns/map`을 빼면 왜 문제가 생길 수 있는가?
5. topic remap과 frame_id 변경은 왜 다른 문제인가?

---

## 3. Frame과 TF

1. `map_robot_ns`, `odom_robot_ns`, `base_footprint`는 각각 어떤 좌표계인가?
2. SLAM 전과 SLAM 후 TF tree는 어떻게 달라지는가?
3. `map_robot_ns -> odom_robot_ns`는 누가 발행하는가?
4. SLAM, AMCL, static_transform_publisher가 동시에 `map_robot_ns -> odom_robot_ns`를 발행하면 왜 문제가 되는가?
5. `tf2_echo map_robot_ns base_footprint`를 확인할 때 왜 `/tf:=/robot_ns/tf` remap이 필요한가?

---

## 4. 지도 파일

1. `.pgm`과 `.yaml`은 각각 무엇을 저장하는가?
2. `resolution: 0.05`는 무슨 뜻인가?
3. `origin`은 왜 필요한가?
4. `slam_map.yaml` 안의 `image: slam_map.pgm`이 상대 경로라는 점은 왜 중요한가?
5. `.posegraph`와 `.data`는 `.pgm/.yaml`과 무엇이 다른가?

---

## 5. SLAM 개념

1. SLAM에서 localization과 mapping은 왜 서로 의존하는가?
2. scan matching은 무엇을 맞춰보는 과정인가?
3. loop closure는 왜 지도 품질을 개선하는가?
4. pose graph에서 node와 edge는 각각 무엇을 의미하는가?
5. 좋은 지도를 만들려면 로봇을 어떻게 움직이는 것이 좋은가?

---

## 6. 내 환경 기준 확인

1. 현재 workspace 경로는 어디인가?
2. 현재 SLAM parameter 파일은 어디에 있는가?
3. 현재 SLAM용 bag `bags/slam_raw_01`에는 어떤 topic이 들어 있는가?
4. 이전 namespace 없는 bag을 `/robot_ns` 구조에 맞추려면 어떤 remap이 필요한가?
5. `use_sim_time:=true`일 때 offline bag 재생에서 왜 `--clock`이 필요한가?

---

## 7. 스스로 설명해보기

아래 문장을 보고 말로 설명할 수 있어야 한다.

```text
Gazebo가 /robot_ns/scan과 /robot_ns/odom을 만들고,
robot_state_publisher와 Gazebo plugin이 TF를 만들며,
SLAM Toolbox는 scan과 TF를 이용해 /robot_ns/map과 map_robot_ns -> odom_robot_ns를 만든다.
map_saver_cli는 이 /robot_ns/map을 slam_map.pgm과 slam_map.yaml로 저장한다.
```

이 문장을 자연스럽게 설명할 수 있으면 Day 11의 핵심은 잡은 것이다.
