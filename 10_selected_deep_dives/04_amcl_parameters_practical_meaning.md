# 04. AMCL 파라미터의 실제 의미

AMCL 파라미터는 처음 보면 숫자가 많아서 감이 잘 안 온다. 하지만 큰 묶음으로 나누면 이해하기 쉽다.

이 저장소의 예시 `amcl_param.yaml`은 대략 아래 그룹으로 구성되어 있다.

```text
1. frame/topic 설정
2. particle 개수와 적응 샘플링 설정
3. motion model 노이즈 설정
4. laser sensor model 설정
5. update 주기와 initial pose 설정
```

이 문서는 각 파라미터를 “실제 위치 추정에 어떤 영향을 주는지” 중심으로 정리한다.

---

## 1. AMCL 파라미터를 보는 큰 기준

AMCL은 particle filter다.

반복 흐름:

```text
1. particle 여러 개를 지도 위에 뿌린다.
2. 로봇이 움직이면 particle도 motion model에 따라 움직인다.
3. 실제 LiDAR scan과 map이 잘 맞는 particle에 높은 weight를 준다.
4. weight가 높은 particle 위주로 다시 뽑는다.
5. particle들이 실제 위치 근처로 모이면 localization이 수렴한다.
```

따라서 파라미터도 이 흐름과 연결해서 보면 된다.

```text
particle 수 관련
  -> 후보 pose를 얼마나 많이 유지할 것인가

motion model 관련
  -> odometry 움직임을 얼마나 믿고, 얼마나 노이즈를 넣을 것인가

sensor model 관련
  -> scan과 map의 일치를 어떻게 점수화할 것인가

update 관련
  -> 얼마나 자주 particle을 갱신할 것인가

frame/topic 관련
  -> 어떤 map/odom/base/scan 이름을 쓸 것인가
```

---

## 2. frame/topic 설정

예시 환경 기준:

```yaml
global_frame_id: map_robot_ns
odom_frame_id: odom_robot_ns
base_frame_id: base_footprint
scan_topic: /robot_ns/scan
tf_broadcast: true
transform_tolerance: 1.0
```

의미:

| 파라미터 | 의미 |
|---|---|
| `global_frame_id` | AMCL이 위치를 추정하는 전역 map frame |
| `odom_frame_id` | odometry 기준 frame |
| `base_frame_id` | 로봇 본체 기준 frame |
| `scan_topic` | AMCL이 구독할 LaserScan topic |
| `tf_broadcast` | AMCL이 `map_robot_ns -> odom_robot_ns` TF를 발행할지 여부 |
| `transform_tolerance` | TF 시간 오차를 어느 정도 허용할지 |

여기서 가장 중요한 것은 frame 이름이 실제 TF tree와 맞아야 한다는 점이다.

```text
global_frame_id = map_robot_ns
odom_frame_id = odom_robot_ns
base_frame_id = base_footprint
```

이렇게 설정했으면 TF에서도 최소한 아래 관계가 가능해야 한다.

```text
odom_robot_ns -> base_footprint
base_footprint -> base_scan
map_robot_ns -> odom_robot_ns  # AMCL이 발행
```

---

## 3. particle 개수 설정

```yaml
min_particles: 500
max_particles: 2000
pf_err: 0.05
pf_z: 0.99
resample_interval: 1
```

### min_particles / max_particles

```text
min_particles
  -> 최소한 유지할 particle 개수

max_particles
  -> 많이 필요할 때 허용할 최대 particle 개수
```

particle이 많으면:

```text
장점: 여러 위치 후보를 더 잘 탐색한다.
단점: 계산량이 증가한다.
```

particle이 적으면:

```text
장점: 가볍다.
단점: 위치를 잃었을 때 회복이 어렵다.
```

현재 값 `500~2000`은 학습/시뮬레이션 환경에서 비교적 넉넉하게 잡은 편으로 볼 수 있다.

### pf_err / pf_z

이 값들은 AMCL의 적응적 particle 수 조절과 관련된다.

직관적으로 보면:

```text
pf_err
  -> particle 분포 근사가 어느 정도 오차까지 허용되는가

pf_z
  -> 그 근사에 대한 신뢰 수준
```

정확한 수식보다 지금 단계에서는 이렇게 이해하면 충분하다.

```text
AMCL이 상황에 따라 particle 수를 늘리거나 줄일 때 참고하는 기준
```

### resample_interval

```yaml
resample_interval: 1
```

의미:

```text
몇 번 update마다 resampling을 할 것인가
```

`1`이면 매 update마다 resampling한다.

resampling은 weight가 높은 particle을 더 많이 복제하고, 낮은 particle을 제거하는 단계다.

---

## 4. recovery_alpha_slow / recovery_alpha_fast

```yaml
recovery_alpha_slow: 0.001
recovery_alpha_fast: 0.1
```

이 값들은 위치를 잃었을 때 recovery 동작과 관련된다.

직관:

```text
slow average
  -> 장기적인 sensor likelihood 평균

fast average
  -> 최근 sensor likelihood 평균
```

최근 관측 점수가 장기 평균보다 갑자기 나빠지면, AMCL은 “위치를 잃었을 수도 있다”고 판단할 수 있다.

그 경우 random particle을 추가해서 다시 위치를 찾는 데 도움을 준다.

이 실습에서는 이렇게 이해하면 된다.

```text
위치를 잃었을 때 particle을 다시 넓게 뿌려 회복하는 데 관여하는 값
```

---

## 5. motion model 파라미터 alpha1~alpha5

```yaml
robot_model_type: "nav2_amcl::DifferentialMotionModel"
alpha1: 0.2
alpha2: 0.2
alpha3: 0.2
alpha4: 0.2
alpha5: 0.2
```

AMCL은 odometry를 그대로 100% 믿지 않는다. 로봇이 움직였다고 보고된 값에는 오차가 있을 수 있기 때문이다.

그래서 particle을 움직일 때 노이즈를 넣는다.

```text
odometry가 이렇게 움직였다고 말한다.
하지만 실제로는 조금 더/덜 움직였을 수도 있다.
각 particle을 조금씩 다르게 움직여보자.
```

`alpha` 값들은 이 노이즈의 크기와 관련된다.

일반적인 직관:

```text
alpha 값이 커질수록
  -> odometry를 덜 믿고 particle을 더 퍼뜨린다.

alpha 값이 작아질수록
  -> odometry를 더 믿고 particle을 덜 퍼뜨린다.
```

너무 작으면:

```text
odometry가 틀렸을 때 particle들이 실제 위치를 못 따라간다.
```

너무 크면:

```text
particle이 지나치게 퍼져서 위치 추정이 흔들릴 수 있다.
```

현재 값 `0.2`는 학습 환경에서 “너무 빡빡하게 믿지는 않겠다”는 정도로 이해하면 된다.

---

## 6. laser model 파라미터

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

### laser_model_type

현재는:

```yaml
laser_model_type: "likelihood_field"
```

Likelihood field 방식은 각 beam이 map의 장애물과 얼마나 가까운지 보고 점수를 준다.

직관:

```text
이 particle 위치에서 scan을 봤다고 가정했을 때,
각 scan endpoint가 map의 벽 근처에 잘 떨어지는가?
```

벽 근처에 잘 떨어지면 점수가 높다.

### laser_min_range / laser_max_range

센서의 유효 거리 범위다.

현재:

```yaml
laser_min_range: 0.12
laser_max_range: 3.5
```

`laser_max_range`는 URDF/Xacro의 LiDAR 설정과 맞아야 한다. map/scan 평가에서 너무 먼 값이나 유효하지 않은 값을 어떻게 처리할지와 관련된다.

### max_beams

```yaml
max_beams: 60
```

LaserScan의 모든 beam을 다 쓰면 계산량이 커진다. 그래서 일부 beam만 샘플링해서 sensor update에 사용한다.

```text
max_beams가 크면
  -> scan 정보를 더 많이 반영하지만 계산량 증가

max_beams가 작으면
  -> 계산은 가볍지만 scan 정보가 부족할 수 있음
```

### z_hit / z_rand / z_short / z_max

이 값들은 sensor model에서 관측이 어떤 원인으로 나왔는지를 섞어서 해석하는 가중치다.

간단히:

```text
z_hit
  -> map과 잘 맞는 정상 측정값을 얼마나 믿을지

z_rand
  -> 랜덤한 측정/노이즈 가능성을 얼마나 둘지

z_short
  -> 예상보다 짧게 나온 측정값 가능성

z_max
  -> max range로 나온 측정값 가능성
```

현재 `z_hit: 0.5`, `z_rand: 0.5`는 정상 매칭과 랜덤 노이즈를 반반 섞어 보는 느낌이다.

실제 튜닝에서는 `z_hit`을 더 높게 주는 경우도 많지만, 지금 문서 단계에서는 “센서 관측 점수의 구성 요소”로 이해하면 된다.

### sigma_hit

```yaml
sigma_hit: 0.2
```

정상 측정값이 map의 장애물에서 얼마나 벗어나도 괜찮게 볼지와 관련된다.

```text
작을수록
  -> map과 scan이 매우 정확히 맞아야 높은 점수

클수록
  -> 조금 떨어져도 어느 정도 높은 점수
```

---

## 7. update_min_d / update_min_a

```yaml
update_min_d: 0.10
update_min_a: 0.10
```

의미:

```text
로봇이 최소 얼마 이상 이동하거나 회전했을 때 AMCL update를 수행할 것인가
```

`update_min_d: 0.10`:

```text
0.10m 이상 이동하면 update 후보
```

`update_min_a: 0.10`:

```text
0.10 rad 이상 회전하면 update 후보
```

너무 작으면:

```text
업데이트가 너무 자주 일어나 계산량 증가
```

너무 크면:

```text
로봇이 움직였는데도 localization 반영이 늦음
```

---

## 8. initial_pose 관련

```yaml
set_initial_pose: false
always_reset_initial_pose: false
initial_pose:
  x: 0.0
  y: 0.0
  z: 0.0
  yaw: 0.0
```

현재 `set_initial_pose: false`라면, AMCL은 YAML의 initial_pose를 자동으로 강제 적용하지 않는다.

대신 RViz의 `2D Pose Estimate`나 `/initialpose` topic으로 초기 위치를 줄 수 있다.

초기 pose가 중요한 이유:

```text
particle을 어디 주변에 뿌릴지 결정하기 때문이다.
```

초기 pose를 실제 위치와 너무 다르게 주면:

```text
particle들이 엉뚱한 곳에서 시작한다.
scan과 map이 맞지 않는다.
localization 수렴이 느리거나 실패한다.
```

---

## 9. 튜닝을 할 때 보는 증상별 기준

### particle이 너무 넓게 퍼져 있고 수렴이 느림

확인할 것:

```text
initialpose가 실제 위치와 너무 다른가?
scan_topic이 맞는가?
LaserScan frame_id가 TF tree와 맞는가?
map이 현재 world와 맞는가?
```

파라미터 후보:

```text
min_particles / max_particles
alpha 값
laser model 관련 z_hit, sigma_hit
```

### pose가 너무 흔들림

확인할 것:

```text
odom이 안정적인가?
scan이 정상적으로 들어오는가?
TF timestamp 문제가 있는가?
```

파라미터 후보:

```text
alpha 값을 너무 크게 잡지 않았는지
update_min_d/update_min_a가 너무 작지 않은지
sigma_hit가 너무 큰지
```

### AMCL pose가 아예 안 나옴

먼저 파라미터보다 시스템 연결을 봐야 한다.

```bash
ros2 topic echo /robot_ns/map --once
ros2 topic echo /robot_ns/scan --once
ros2 run tf2_ros tf2_echo odom_robot_ns base_footprint
ros2 run tf2_ros tf2_echo base_footprint base_scan
```

AMCL은 파라미터만 맞아도 되는 게 아니라 map/scan/TF가 모두 맞아야 한다.

---

## 10. 핵심 요약

```text
AMCL 파라미터는 particle filter의 각 단계와 연결된다.
min/max_particles는 pose 후보 수를 조절한다.
alpha 값은 odometry motion model의 노이즈를 조절한다.
laser model 값들은 scan과 map의 일치도를 어떻게 점수화할지 결정한다.
update_min_d/a는 AMCL update 빈도를 조절한다.
initialpose는 particle이 어디서 시작할지를 결정하므로 매우 중요하다.
파라미터 튜닝 전에 map, scan, TF, frame 이름이 맞는지 먼저 확인해야 한다.
```

---

## 11. 이 문서와 연결되는 기존 문서

```text
day_12_amcl_mcl/04_amcl_parameters_and_tuning.md
day_12_amcl_mcl/background/particle_filter_math_minimum.md
day_12_amcl_mcl/background/likelihood_field_vs_beam_model.md
day_12_amcl_mcl/background/initial_pose_covariance_and_convergence.md
appendix/amcl_parameter_quick_reference.md
```
