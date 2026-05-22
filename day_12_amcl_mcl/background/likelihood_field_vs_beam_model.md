# Likelihood Field Model과 Beam Model

AMCL의 Sensor Update는 LiDAR scan과 map이 얼마나 잘 맞는지를 평가한다. 이때 대표적인 방식이 beam model과 likelihood field model이다.

---

## 1. Beam Model 직관

Beam model은 각 LiDAR beam을 지도에 직접 쏘는 방식으로 생각하면 된다.

```text
particle 위치에서 beam을 쏜다.
지도에서 벽까지 예상 거리를 구한다.
실제 LiDAR 거리와 비교한다.
```

예:

```text
예상 거리: 2.0m
실제 거리: 2.1m
오차: 0.1m -> 잘 맞음
```

장점:

```text
직관적이다.
ray casting과 연결해서 이해하기 쉽다.
```

단점:

```text
각 particle마다 여러 beam을 지도에 직접 쏴야 해서 계산량이 클 수 있다.
작은 지도 오차나 센서 오차에 민감할 수 있다.
```

---

## 2. Likelihood Field Model 직관

Likelihood field model은 beam 전체의 예상 거리보다는 scan endpoint가 지도 장애물에 얼마나 가까운지를 본다.

```text
LiDAR endpoint를 지도 좌표계로 변환한다.
그 endpoint가 가장 가까운 장애물 셀에서 얼마나 떨어져 있는지 본다.
가까우면 높은 점수, 멀면 낮은 점수.
```

예:

```text
scan 점이 지도 벽 바로 근처에 찍힘
  -> 높은 likelihood

scan 점이 지도 벽과 멀리 떨어짐
  -> 낮은 likelihood
```

현재 `amcl_param.yaml`은 이 방식을 쓴다.

```yaml
laser_model_type: "likelihood_field"
```

---

## 3. 왜 likelihood field가 실습에서 이해하기 좋은가

RViz에서 보면 아래처럼 생각할 수 있다.

```text
빨간 LaserScan 점들이 지도 벽 위에 잘 겹침
  -> AMCL이 높은 점수를 줄 가능성이 큼

빨간 LaserScan 점들이 지도 벽과 어긋남
  -> AMCL이 낮은 점수를 줄 가능성이 큼
```

즉, RViz에서 scan과 map의 정합을 눈으로 보는 것이 likelihood field model의 직관과 잘 맞는다.

---

## 4. 관련 파라미터

```yaml
laser_likelihood_max_dist: 2.0
sigma_hit: 0.2
z_hit: 0.5
z_rand: 0.5
```

대략적 의미:

```text
laser_likelihood_max_dist
  장애물에서 얼마나 멀리 떨어진 scan endpoint까지 고려할지

sigma_hit
  장애물 근처에서 점수가 얼마나 빨리 줄어드는지

z_hit
  map과 잘 맞는 정상 측정에 주는 비중

z_rand
  랜덤 노이즈나 예상 밖 측정에 주는 비중
```

초기 학습 단계에서는 값을 바꾸기보다 이 값들이 “scan endpoint와 map 장애물의 거리 기반 점수”와 연결된다는 점을 이해하면 된다.

---

## 5. Beam model과 likelihood field 비교

| 구분 | Beam Model | Likelihood Field Model |
|---|---|---|
| 사고방식 | 각 beam의 예상 거리와 실제 거리 비교 | scan endpoint가 장애물에 얼마나 가까운지 비교 |
| 직관 | ray casting | 거리장(distance field) |
| 계산 | beam별 ray casting 부담 가능 | 미리 계산된 거리장 활용 가능 |
| 민감도 | 지도/센서 오차에 민감할 수 있음 | 작은 오차에 비교적 부드러움 |
| 현재 설정 | 사용 안 함 | 사용 중 |

---

## 6. 현재 실습에서 확인하는 방법

RViz에서 아래를 본다.

```text
Map: /robot_ns/map
LaserScan: /robot_ns/scan
Fixed Frame: map_robot_ns
```

정상에 가까운 상태:

```text
LaserScan 점들이 지도 벽과 대략 겹친다.
ParticleCloud가 로봇 주변으로 모인다.
```

비정상 가능성:

```text
LaserScan 점들이 지도 벽과 크게 어긋난다.
ParticleCloud가 퍼지거나 엉뚱한 곳으로 모인다.
```

이때 바로 `z_hit`, `sigma_hit`를 고치지 말고 먼저 world-map 짝, initialpose 방향, TF chain을 확인한다.
