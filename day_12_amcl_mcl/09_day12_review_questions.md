# 09. Day 12 복습 질문

아래 질문에 답할 수 있으면 Day 12 AMCL/MCL 흐름을 어느 정도 이해한 것이다.

---

## 1. SLAM과 AMCL

```text
1. SLAM과 AMCL의 가장 큰 차이는 무엇인가?
2. Day 11에서 만든 slam_map.yaml은 Day 12에서 어떤 노드의 입력이 되는가?
3. AMCL은 왜 지도를 새로 만들지 않는가?
4. AMCL을 실행할 때 world와 map이 짝이 맞아야 하는 이유는 무엇인가?
```

---

## 2. Particle Filter

```text
1. particle 하나는 무엇을 의미하는가?
2. particle의 [x, y, theta]는 어떤 좌표계 기준인가?
3. Motion Update는 어떤 데이터를 사용해서 particle을 움직이는가?
4. Sensor Update는 무엇과 무엇을 비교하는가?
5. Resampling은 왜 필요한가?
6. AMCL에서 Adaptive라는 말은 무엇을 뜻하는가?
```

---

## 3. Topic / Frame / TF

```text
1. 현재 환경에서 map topic 이름은 무엇인가?
2. 현재 환경에서 scan topic 이름은 무엇인가?
3. 현재 환경에서 map frame 이름은 무엇인가?
4. 현재 환경에서 odom frame 이름은 무엇인가?
5. /amcl_pose와 map_robot_ns -> odom_robot_ns TF는 무엇이 다른가?
6. topic remap과 frame_id 변경은 왜 다른 문제인가?
```

---

## 4. initialpose와 RViz

```text
1. AMCL에서 initialpose가 필요한 이유는 무엇인가?
2. RViz 2D Pose Estimate를 찍을 때 방향까지 중요한 이유는 무엇인가?
3. ParticleCloud가 넓게 퍼져 있다는 것은 어떤 의미인가?
4. ParticleCloud가 로봇 주변으로 모인다는 것은 어떤 의미인가?
5. RViz에서 map이 안 보일 때 AMCL 문제인지 RViz 표시 문제인지 어떻게 구분할 수 있는가?
```

---

## 5. 파라미터

```text
1. global_frame_id는 현재 어떤 값이어야 하는가?
2. odom_frame_id는 현재 어떤 값이어야 하는가?
3. base_frame_id는 현재 어떤 값이어야 하는가?
4. scan_topic은 현재 어떤 값이어야 하는가?
5. min_particles와 max_particles는 어떤 역할을 하는가?
6. alpha1~alpha4는 무엇을 의미하는가?
7. laser_model_type: likelihood_field는 어떤 방식으로 scan과 map을 비교하는가?
8. update_min_d와 update_min_a는 어떤 조건을 의미하는가?
```

---

## 6. 예시 환경 실행

```text
1. 통합 AMCL 실행 명령은 무엇인가?
2. 작은 방 world와 map을 쓰려면 어떤 인자를 줘야 하는가?
3. map_server와 amcl이 active인지 확인하는 명령은 무엇인가?
4. map_robot_ns -> odom_robot_ns TF를 확인하는 명령은 무엇인가?
5. teleop을 /robot_ns/cmd_vel로 보내려면 어떤 remap이 필요한가?
```

---

## 7. Day 13으로 넘어가기 전 체크

```text
1. /robot_ns/map이 정상인가?
2. /robot_ns/scan이 정상인가?
3. /amcl_pose가 나오는가?
4. map_robot_ns -> odom_robot_ns -> base_footprint TF chain이 이어지는가?
5. scan 점이 map 벽과 대략 맞는가?
6. particle_cloud가 수렴하는가?
```

이 질문들에 답하기 전에는 Nav2 planner/controller 문제로 넘어가지 않는 것이 좋다. AMCL이 안정되지 않으면 Nav2도 정상적으로 판단하기 어렵다.

---

## 추가 복습 질문 - frame naming

```text
1. 일반 예제의 map/odom과 이 문서의 map_robot_ns/odom_robot_ns는 어떤 관계인가?
2. /robot_ns/map과 map_robot_ns는 왜 같은 것이 아닌가?
3. topic namespace를 remap해도 TF frame 이름이 자동으로 바뀌지 않는 이유는 무엇인가?
4. AMCL parameter의 global_frame_id와 odom_frame_id가 실제 TF tree와 다르면 어떤 문제가 생기는가?
5. 왜 이 문서에서는 `map`, `odom` 대신 `map_robot_ns`, `odom_robot_ns`를 쓰는가?
```
