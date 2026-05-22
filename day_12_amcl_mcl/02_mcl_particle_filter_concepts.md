# 02. MCL / Particle Filter / AMCL 개념

## 1. 한 문장으로 이해하기

MCL은 지도 위에 여러 개의 가짜 로봇 후보를 뿌려놓고, 실제 센서값과 잘 맞는 후보만 살아남게 해서 로봇 위치를 추정하는 방법이다.

```text
particle = "로봇이 여기 있을 수도 있다"라는 위치 후보
```

각 particle은 보통 아래와 같은 pose를 가진다.

```text
[x, y, theta]
```

의미:

```text
x      지도 좌표계에서 x 위치
y      지도 좌표계에서 y 위치
theta  로봇이 바라보는 방향
```

---

## 2. MCL이 해결하려는 문제

로봇은 실제 위치를 직접 알 수 없다. 대신 아래 데이터를 본다.

```text
1. 바퀴/시뮬레이터 odometry
2. LiDAR scan
3. 이미 저장된 map
```

odometry는 짧은 시간에는 부드럽지만 오차가 누적된다. LiDAR는 현재 주변 구조를 잘 알려주지만, “이 구조가 지도에서 어디인지”는 비교가 필요하다. MCL은 이 둘을 합친다.

```text
odom: 내가 얼마나 움직였는지 추정
scan + map: 내가 지도 어디쯤인지 보정
```

---

## 3. 로컬라이제이션 문제의 종류

### 3.1 위치 추적

초기 위치를 대략 알고 있고, 그 이후 계속 추적하는 상황이다.

```text
처음 위치는 알고 있음
움직일 때마다 odom과 scan으로 조금씩 보정
```

RViz의 `2D Pose Estimate`를 찍고 시작하는 AMCL 실습이 여기에 가깝다.

### 3.2 글로벌 로컬라이제이션

로봇이 지도 안 어디에 있는지 전혀 모르는 상태에서 시작한다.

```text
지도 전체에 particle을 넓게 뿌림
scan과 map이 잘 맞는 곳으로 particle이 점점 모임
```

계산량이 더 크고, 대칭적인 공간에서는 헷갈릴 수 있다.

### 3.3 납치된 로봇 문제

로봇이 추정 중이던 위치와 전혀 다른 곳으로 갑자기 옮겨진 상황이다.

```text
AMCL은 이미 "나는 여기 있다"고 믿고 있음
그런데 실제 로봇은 다른 곳에 있음
scan과 map이 계속 안 맞음
```

이 경우 particle을 다시 넓게 퍼뜨리거나 initialpose를 다시 줘야 한다.

---

## 4. MCL의 기본 루프

MCL은 아래 네 단계를 반복한다.

```text
1. 초기화
2. Motion Update
3. Sensor Update
4. Resampling
```

### 4.1 초기화

초기 위치를 아는 경우:

```text
initialpose 주변에 particle을 뿌린다.
```

초기 위치를 모르는 경우:

```text
지도 전체의 free space에 particle을 뿌린다.
```

노트북 예제에서는 `init_particles()`가 이 역할을 한다.

```python
particles, weights = init_particles(500, grid=occupancy_grid)
```

### 4.2 Motion Update

로봇이 움직였다고 odometry가 말하면, 모든 particle도 같은 식으로 움직인다.

```text
로봇이 앞으로 0.4m 갔다고 추정됨
-> 모든 particle도 대략 앞으로 0.4m 이동
-> 단, odom 오차를 반영해서 noise를 추가
```

노트북 예제에서는 `motion_update()`가 이 역할을 한다.

```python
particles = motion_update(particles, meas_delta)
```

### 4.3 Sensor Update

각 particle 위치에서 LiDAR를 쐈다고 가정한다. 그리고 실제 LiDAR와 비교한다.

```text
particle A에서 예상한 scan이 실제 scan과 비슷함
  -> weight 높음

particle B에서 예상한 scan이 실제 scan과 다름
  -> weight 낮음
```

노트북 예제에서는 `sensor_update()`가 이 역할을 한다.

```python
particles_weights = sensor_update(particles, get_scan(gt_pose), gt_pose)
```

### 4.4 Resampling

weight가 높은 particle은 더 많이 복제되고, 낮은 particle은 사라진다.

```text
잘 맞는 후보는 살아남음
안 맞는 후보는 제거됨
```

반복하면 particle들이 실제 위치 주변으로 모인다.

---

## 5. 노트북 예제와 실제 AMCL의 차이

Day 12 노트북은 원리를 이해하기 위한 교육용 코드다. 실제 AMCL과 완전히 같지는 않다.

특히 기존 `sensor_update()`는 `true_pose`를 알고 있는 형태로 작성되어 있다.

```python
dtheta = p[2] - true_pose[2]
pred_scan = get_scan(p, angle_offset=-dtheta)
```

이 구조는 “파티클 방향 차이를 정답 방향에 맞춰 보정한 뒤 scan을 비교”하는 효과가 있다. 그래서 위치 비교를 시각화하기에는 쉽지만, 실제 AMCL 사고방식과는 다르다.

실제 AMCL은 `true_pose`를 모른다.

```text
실제 AMCL 입력:
  /map
  /scan
  odom TF
  /initialpose

실제 AMCL이 모르는 것:
  Ground Truth pose
```

따라서 더 실제에 가까운 sensor update는 아래처럼 생각해야 한다.

```text
각 particle의 x, y, theta 그대로 예상 scan을 만든다.
실제 scan과 비교한다.
방향이 틀린 particle도 weight가 낮아진다.
```

---

## 6. AMCL에서 Adaptive의 의미

AMCL은 `Adaptive Monte Carlo Localization`이다. 기본 MCL과 다른 핵심은 particle 수를 상황에 따라 조절하는 것이다.

```text
위치가 불확실함
  -> particle을 많이 유지

위치가 안정적으로 수렴함
  -> particle을 줄여 계산량 감소
```

현재 파라미터와 연결하면 아래가 관련된다.

```yaml
min_particles: 500
max_particles: 2000
pf_err: 0.05
pf_z: 0.99
```

처음부터 이 값을 튜닝하려고 하기보다, 먼저 아래를 확인해야 한다.

```text
map이 맞는가?
scan이 들어오는가?
TF가 이어지는가?
initialpose를 줬는가?
world와 map이 같은 짝인가?
```

---

## 7. 직관적인 비유

AMCL은 여러 명의 후보 탐정이 지도 위에 흩어져 있는 것과 비슷하다.

```text
각 탐정 = particle
각 탐정의 위치 = 로봇이 있을 가능성이 있는 pose
각 탐정의 관측 = 그 위치에서 예상되는 LiDAR 모양
실제 관측과 잘 맞는 탐정 = 살아남음
실제 관측과 안 맞는 탐정 = 사라짐
```

처음에는 후보가 많지만, 시간이 지나면 후보들이 진짜 위치 근처로 모인다.
