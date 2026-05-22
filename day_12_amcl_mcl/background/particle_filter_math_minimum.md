# Particle Filter 최소 배경지식

이 문서는 AMCL을 이해하는 데 필요한 확률/수식 배경만 최소한으로 정리한다.

---

## 1. 로봇 위치는 하나의 값이 아니라 확률분포다

로봇은 자기 위치를 완벽하게 알 수 없다. 그래서 위치를 하나의 정답값으로만 보지 않고 “어디에 있을 가능성이 높은지”로 본다.

```text
확실한 위치:
  로봇은 정확히 (x=1.0, y=2.0, theta=0.0)에 있다.

확률적 위치:
  로봇은 (1.0, 2.0) 근처에 있을 가능성이 높고,
  다른 곳에 있을 가능성은 낮다.
```

Particle Filter는 이 확률분포를 수식이 아니라 여러 개의 샘플로 표현한다.

```text
particle 여러 개 = 위치 확률분포의 샘플 표현
```

---

## 2. 각 particle은 가중치를 가진다

particle 하나는 pose 후보이고, weight는 그 후보가 얼마나 그럴듯한지를 나타낸다.

```text
particle_i = [x_i, y_i, theta_i]
weight_i = 이 particle이 실제 위치일 가능성
```

weight는 보통 전체 합이 1이 되도록 정규화한다.

```text
w1 + w2 + ... + wn = 1
```

---

## 3. 예측과 보정

Particle Filter는 크게 두 단계를 반복한다.

```text
예측 prediction:
  odometry를 보고 particle들을 움직인다.

보정 correction:
  LiDAR와 map을 비교해서 particle weight를 갱신한다.
```

Kalman Filter와 비슷하게 “예측 + 보정” 구조를 가지지만, Particle Filter는 분포를 입자 샘플로 표현한다는 점이 다르다.

---

## 4. Sensor Update의 점수 직관

어떤 particle 위치에서 예상한 scan과 실제 scan이 비슷하면 높은 점수를 준다.

```text
오차가 작음 -> weight 큼
오차가 큼 -> weight 작음
```

노트북의 단순화된 점수는 Gaussian 모양으로 볼 수 있다.

```text
error가 0에 가까움
  exp 값이 1에 가까움

error가 커짐
  exp 값이 0에 가까움
```

여기서 중요한 것은 수식 암기가 아니다.

```text
scan-map 비교 결과를 확률 점수로 바꾸고,
그 점수를 이용해 particle을 살리거나 버린다.
```

---

## 5. Resampling이 필요한 이유

Sensor Update 후 weight가 높은 particle과 낮은 particle이 생긴다.

그 상태로 계속 두면 계산 자원이 낮은 확률 후보에도 낭비된다.

Resampling은 아래처럼 동작한다.

```text
weight 높은 particle
  더 많이 복제됨

weight 낮은 particle
  사라짐
```

결과적으로 particle들이 가능성 높은 위치 주변으로 모인다.

---

## 6. Particle Filter의 한계

Particle Filter는 강력하지만 한계도 있다.

```text
1. particle 수가 너무 적으면 잘못 수렴할 수 있다.
2. map이 실제 환경과 다르면 scan 비교가 틀어진다.
3. 긴 복도처럼 대칭적인 공간에서는 여러 위치가 비슷해 보일 수 있다.
4. initialpose가 너무 틀리면 수렴이 오래 걸리거나 실패할 수 있다.
5. odom/scan/TF 시간 동기 문제가 있으면 update가 불안정하다.
```

그래서 AMCL 문제를 볼 때는 파라미터보다 입력 데이터 품질을 먼저 확인해야 한다.
