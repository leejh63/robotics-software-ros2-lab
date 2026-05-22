# 04. AMCL 파라미터와 튜닝 기준

이 문서는 `lee_robot_description/config/amcl_param.yaml`을 읽을 때 무엇을 봐야 하는지 정리한다. 처음에는 값을 바꾸기보다 **각 파라미터가 MCL의 어느 단계와 연결되는지**를 이해하는 것이 중요하다.

---

## 1. 현재 파라미터 파일 위치

```text
$ROS2_WS/lee_robot_description/config/amcl_param.yaml
```

핵심 구조:

```yaml
amcl:
  ros__parameters:
    use_sim_time: true
    global_frame_id: map_robot_ns
    odom_frame_id: odom_robot_ns
    base_frame_id: base_footprint
    scan_topic: /robot_ns/scan
    tf_broadcast: true
```

---

## 2. MCL 단계와 파라미터 연결

| MCL 단계 | 관련 파라미터 | 의미 |
|---|---|---|
| 초기화 | `min_particles`, `max_particles`, `set_initial_pose`, `initial_pose` | particle 수와 시작 위치 |
| Motion Update | `robot_model_type`, `alpha1~alpha5` | odometry 오차 모델 |
| Sensor Update | `laser_model_type`, `z_hit`, `z_rand`, `sigma_hit`, `laser_likelihood_max_dist` | LiDAR와 map 비교 방식 |
| Resampling | `resample_interval`, `pf_err`, `pf_z` | particle 재선택과 adaptive sampling |
| TF 출력 | `global_frame_id`, `odom_frame_id`, `base_frame_id`, `tf_broadcast` | map/odom/base frame 연결 |
| 업데이트 조건 | `update_min_d`, `update_min_a` | 얼마나 움직였을 때 update할지 |

---

## 3. 현재 환경에서 반드시 맞아야 하는 값

```yaml
use_sim_time: true
global_frame_id: map_robot_ns
odom_frame_id: odom_robot_ns
base_frame_id: base_footprint
scan_topic: /robot_ns/scan
tf_broadcast: true
```

틀리면 생기는 문제:

```text
global_frame_id가 map이면:
  RViz Fixed Frame map_robot_ns와 맞지 않음

odom_frame_id가 odom이면:
  실제 TF odom_robot_ns와 연결 안 됨

base_frame_id가 base_link이면:
  현재 로봇 기준 base_footprint와 다를 수 있음

scan_topic이 /scan이면:
  현재 Gazebo LiDAR의 /robot_ns/scan을 못 봄

tf_broadcast가 false면:
  map_robot_ns -> odom_robot_ns TF가 나오지 않음
```

---

## 4. Particle 관련 파라미터

```yaml
min_particles: 500
max_particles: 2000
pf_err: 0.05
pf_z: 0.99
```

의미:

```text
min_particles
  위치가 어느 정도 안정됐을 때도 유지하는 최소 particle 수

max_particles
  위치가 불확실할 때 허용하는 최대 particle 수

pf_err
  KLD sampling에서 허용하는 근사 오차

pf_z
  KLD sampling에서 요구하는 신뢰도
```

직관:

```text
particle이 너무 적음
  계산은 가볍지만 잘못된 위치로 수렴할 수 있음

particle이 너무 많음
  안정성은 올라갈 수 있지만 CPU 사용량이 증가함
```

현재는 학습용 Gazebo 환경이므로 `500~2000` 범위는 무난한 시작점이다.

---

## 5. Motion Model 관련 파라미터

현재 설정:

```yaml
robot_model_type: "nav2_amcl::DifferentialMotionModel"
alpha1: 0.2
alpha2: 0.2
alpha3: 0.2
alpha4: 0.2
alpha5: 0.2
```

차동 구동 로봇은 좌우 바퀴 속도 차이로 회전한다. TurtleBot 계열이나 Gazebo diff_drive plugin 기반 로봇은 대체로 differential motion model로 보는 것이 자연스럽다.

`alpha` 값들은 odometry 오차를 얼마나 크게 볼지 결정한다.

```text
alpha 값이 작음
  odom을 많이 믿음
  particle이 덜 퍼짐

alpha 값이 큼
  odom을 덜 믿음
  particle이 더 많이 퍼짐
```

튜닝 전 확인:

```text
Gazebo odom이 정상인가?
odom_robot_ns -> base_footprint TF가 나오는가?
로봇이 실제로 /robot_ns/cmd_vel에 반응하는가?
```

---

## 6. Laser Model 관련 파라미터

현재 설정:

```yaml
laser_model_type: "likelihood_field"
laser_min_range: 0.12
laser_max_range: 3.5
laser_likelihood_max_dist: 2.0
max_beams: 60
z_hit: 0.5
z_rand: 0.5
z_short: 0.05
z_max: 0.05
sigma_hit: 0.2
lambda_short: 0.1
```

핵심은 `laser_model_type`이다.

```text
beam model
  각 beam을 ray casting처럼 직접 비교하는 사고방식

likelihood field model
  scan endpoint가 지도 장애물에 얼마나 가까운지로 점수를 주는 방식
```

현재 설정은 `likelihood_field`다. 실습에서는 이 방식을 먼저 이해하는 것이 좋다.

```text
scan 점이 map의 벽 근처에 찍힘
  -> 높은 likelihood

scan 점이 map의 벽과 멀리 떨어짐
  -> 낮은 likelihood
```

`laser_min_range`, `laser_max_range`는 URDF/Gazebo LiDAR 설정과 맞아야 한다.

현재 Day 10/11 기준:

```text
LiDAR min range: 0.12 m
LiDAR max range: 3.5 m
```

---

## 7. Update 관련 파라미터

```yaml
update_min_d: 0.10
update_min_a: 0.10
save_pose_rate: 0.5
```

의미:

```text
update_min_d
  로봇이 이 거리 이상 움직였을 때 AMCL update 수행

update_min_a
  로봇이 이 각도 이상 회전했을 때 AMCL update 수행

save_pose_rate
  마지막 pose 저장 빈도
```

값이 너무 크면:

```text
로봇이 조금 움직여도 AMCL이 갱신되지 않는 것처럼 보일 수 있음
```

값이 너무 작으면:

```text
AMCL update가 너무 자주 일어나 계산량이 늘 수 있음
```

---

## 8. 초기 위치 관련 파라미터

```yaml
set_initial_pose: false
always_reset_initial_pose: false
initial_pose:
  x: 0.0
  y: 0.0
  z: 0.0
  yaw: 0.0
```

현재 설정에서는 자동 초기 위치보다 RViz `2D Pose Estimate` 또는 `/initialpose`를 통해 직접 주는 흐름이 기본이다.

학습할 때는 이 방식이 더 좋다.

```text
initialpose 전후로 particle_cloud가 어떻게 달라지는지 볼 수 있기 때문
```

---

## 9. 튜닝 순서

AMCL이 이상하면 파라미터부터 바꾸지 말고 아래 순서로 확인한다.

```text
1. world와 map이 같은 짝인가?
2. /robot_ns/map이 frame_id: map_robot_ns로 나오는가?
3. /robot_ns/scan이 frame_id: base_scan으로 나오는가?
4. odom_robot_ns -> base_footprint TF가 나오는가?
5. AMCL이 active 상태인가?
6. /initialpose를 줬는가?
7. map_robot_ns -> odom_robot_ns TF가 나오는가?
8. 그 다음 particle/laser/motion 파라미터를 본다.
```

딱 잘라 말하면, 처음부터 `alpha`, `z_hit`, `sigma_hit`를 건드리면 안 된다. 대부분의 초반 문제는 파라미터 튜닝 문제가 아니라 topic/frame/lifecycle/initialpose 문제다.
