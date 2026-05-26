# 04. RRT 충돌 검사 방식과 한계

## 1. 질문의 핵심

RRT에서 다음 상황이 생긴다.

```text
q_near에서 q_rand 방향으로 q_new를 만들었다.
그런데 q_near와 q_new 사이에 벽이 있는지 어떻게 판단하는가?
```

노트북에서는 다음 함수들이 이 판단을 담당한다.

```python
is_collision_line()
is_collision_point()
m_to_idx()
```

---

## 2. 충돌 검사 대상은 q_rand가 아니다

RRT에서 랜덤 점은 `q_rand`다.

하지만 실제로 검사하는 선분은 보통 다음이 아니다.

```text
q_near → q_rand
```

실제로 검사하는 것은 다음이다.

```text
q_near → q_new
```

이유는 `q_rand`는 방향을 유도하는 점이고, 실제로 트리에 추가하려는 점은 `q_new`이기 때문이다.

```text
q_near ---- q_new ---------------- q_rand
  ●          ◆                      ★

검사 대상: q_near → q_new
트리에 추가 후보: q_new
방향 유도점: q_rand
```

---

## 3. 충돌 검사 코드

노트북의 선분 충돌 검사는 다음과 같다.

```python
def is_collision_line(x1, y1, x2, y2, n_checks=20):
    for t in np.linspace(0, 1, n_checks):
        x = x1 + t * (x2 - x1)
        y = y1 + t * (y2 - y1)
        if is_collision_point(x, y):
            return True
    return False
```

이 함수는 선분을 연속적으로 완벽하게 검사하는 것이 아니다.

선분 위에 `n_checks`개의 점을 찍어서 검사한다.

현재 기본값은:

```text
n_checks = 20
```

이다.

---

## 4. np.linspace의 의미

```python
for t in np.linspace(0, 1, n_checks):
```

`np.linspace(0, 1, 20)`은 0부터 1까지 20개의 값을 만든다.

대략 다음과 같다.

```text
0.00, 0.05, 0.10, ..., 0.95, 1.00
```

각 `t`에 대해 선분 위의 한 점을 계산한다.

```python
x = x1 + t * (x2 - x1)
y = y1 + t * (y2 - y1)
```

`t = 0`이면 시작점이다.

```text
(x, y) = (x1, y1)
```

`t = 1`이면 끝점이다.

```text
(x, y) = (x2, y2)
```

`t = 0.5`이면 중간점이다.

---

## 5. 점 하나의 충돌 검사

각 샘플 점은 `is_collision_point()`로 검사된다.

```python
def is_collision_point(x, y):
    ix, iy = m_to_idx(x, y)
    return occupancy_grid[iy, ix] >= 100
```

먼저 미터 좌표 `(x, y)`를 grid index `(ix, iy)`로 바꾼다.

```python
def m_to_idx(x_m, y_m):
    ix = int(np.clip(np.floor(x_m / RES), 0, GRID_W - 1))
    iy = int(np.clip(np.floor(y_m / RES), 0, GRID_H - 1))
    return ix, iy
```

`RES = 0.1`이면:

```text
x = 1.23m → ix = floor(1.23 / 0.1) = 12
y = 4.56m → iy = floor(4.56 / 0.1) = 45
```

그다음 해당 셀 값을 본다.

```python
occupancy_grid[iy, ix] >= 100
```

의미는 다음과 같다.

```text
100 이상이면 장애물
100 미만이면 통과 가능
```

---

## 6. 전체 판단 흐름

RRT 루프에서는 다음 줄이 실행된다.

```python
if is_collision_line(q_near.x, q_near.y, q_new_pos[0], q_new_pos[1]):
    continue
```

내부 흐름은 다음과 같다.

```text
1. q_near와 q_new 사이의 선분을 20개의 점으로 쪼갠다.
2. 각 점을 미터 좌표에서 grid index로 변환한다.
3. 해당 grid 셀이 장애물인지 확인한다.
4. 하나라도 장애물에 걸리면 True를 반환한다.
5. True면 continue로 이번 확장을 버린다.
6. 전부 빈 공간이면 False를 반환한다.
7. False면 q_new를 트리에 추가한다.
```

---

## 7. 충돌이 있으면 어떻게 되는가?

충돌이 있으면 다음 코드 때문에 현재 반복이 끝난다.

```python
continue
```

그 결과:

```text
q_new 추가 안 함
edge 추가 안 함
nodes 변화 없음
이번 랜덤 샘플은 실패 처리
다음 반복에서 새로운 q_rand를 다시 뽑음
```

즉, 사용자가 이해한 것처럼:

```text
그 사이에 벽이 있으면 이번 시도는 실패 처리하고 다음 랜덤값으로 넘어간다.
```

이게 맞다.

---

## 8. 이 방식의 한계: 벽을 놓칠 수 있는가?

가능하다.

현재 방식은 선분 전체를 수학적으로 정확히 검사하는 것이 아니라, 선 위의 일부 샘플 점만 검사한다.

따라서 운이 나쁘면 다음 상황이 생길 수 있다.

```text
q_near ---- . ---- . ---- . ---- q_new
              █
             벽
```

샘플 점 `.`들이 벽 셀을 밟지 않으면, 실제 선분이 벽을 지나가도 충돌을 못 잡을 수 있다.

이런 문제를 tunneling 문제처럼 볼 수 있다.

```text
검사 간격이 듬성듬성해서 얇은 장애물을 통과해버리는 문제
```

---

## 9. 현재 노트북 설정에서는 어느 정도 안전한가?

현재 설정은 대략 다음이다.

```text
STEP_SIZE = 0.5m
n_checks = 20
RES = 0.1m/cell
```

검사 간격은 대략:

```text
0.5m / 19 ≈ 0.026m
```

맵 한 칸은 0.1m이므로, 현재 설정에서는 꽤 촘촘하게 검사하는 편이다.

그래서 실습에서는 큰 문제가 잘 안 보일 수 있다.

하지만 `STEP_SIZE`를 키우거나 `n_checks`를 줄이면 위험해진다.

---

## 10. 개선 1: 거리 기반 샘플링

현재는 항상 20개 점을 검사한다.

더 좋은 방식은 선분 길이에 따라 검사 개수를 자동으로 정하는 것이다.

```python
def is_collision_line(x1, y1, x2, y2):
    dist = np.hypot(x2 - x1, y2 - y1)
    check_step = RES * 0.5
    n_checks = max(2, int(np.ceil(dist / check_step)) + 1)

    for t in np.linspace(0.0, 1.0, n_checks):
        x = x1 + t * (x2 - x1)
        y = y1 + t * (y2 - y1)
        if is_collision_point(x, y):
            return True

    return False
```

이렇게 하면 검사 간격이 대략 `RES * 0.5` 이하가 된다.

`RES = 0.1`이면 약 0.05m 이하 간격으로 검사한다.

---

## 11. 개선 2: 선분이 지나가는 모든 grid cell 검사

더 정확한 방식은 선분 위의 몇 개 점만 보는 것이 아니라, 선분이 통과하는 모든 grid cell을 검사하는 것이다.

이런 방식은 보통 다음 이름으로 불린다.

```text
Bresenham
DDA
Grid ray tracing
```

개념 차이는 다음과 같다.

```text
현재 방식:
선 위의 일부 점만 검사

더 정확한 방식:
선이 지나가는 모든 grid cell 검사
```

실제 로봇 경로 계획에서는 이 방식이 더 안전하다.

---

## 12. 개선 3: 로봇 크기 고려

현재 `is_collision_point()`는 점 하나만 검사한다.

```python
return occupancy_grid[iy, ix] >= 100
```

즉, 로봇을 점으로 본다.

하지만 실제 로봇은 반지름 또는 footprint가 있다.

따라서 실제 로봇 기준으로는 다음 중 하나가 필요하다.

```text
1. occupancy grid를 로봇 반지름만큼 inflate한다.
2. 각 점에서 로봇 footprint가 장애물과 겹치는지 검사한다.
```

가장 쉬운 방법은 장애물을 미리 부풀리는 것이다.

```text
원래 장애물:
█

inflate 후:
█████
█████
█████
```

그러면 RRT는 점 검사만 해도 실제로는 로봇 반지름만큼 안전거리를 확보하게 된다.

---

## 13. 최종 정리

RRT의 충돌 판단은 다음처럼 진행된다.

```text
q_near → q_new 선분 위에 여러 샘플 점을 찍는다.
각 점을 grid index로 변환한다.
해당 grid 셀이 장애물이면 충돌로 판단한다.
하나라도 충돌이면 이번 q_new는 버린다.
모든 점이 free이면 q_new를 트리에 추가한다.
```

다만 이 방식은 근사 검사다.

더 정확한 구현을 원하면 다음 순서로 개선하는 것이 좋다.

```text
1. 고정 n_checks 대신 RES 기반 거리 샘플링 사용
2. 가능하면 DDA/Bresenham으로 모든 통과 셀 검사
3. 실제 로봇 적용 시 inflation 또는 footprint collision check 추가
```
