# 01. Occupancy Grid, Inflation Costmap, Dijkstra 정리

## 1. 이 실습에서 다루는 문제

목표는 복잡한 2D 맵에서 시작점에서 목표점까지 충돌하지 않는 경로를 찾는 것이다.

실습 맵은 다음 조건을 가진다.

```text
GRID_W, GRID_H = 100, 100
RES = 0.1 m/cell
전체 맵 크기 = 10m x 10m
START_M = (1.0, 1.0)
GOAL_M  = (9.0, 9.0)
```

즉, 지도는 100x100 셀이고, 한 셀은 0.1m이다.

---

## 2. Occupancy Grid란?

Occupancy Grid는 각 셀이 비어 있는지, 장애물인지 나타내는 격자 지도다.

실습 코드에서는 다음처럼 사용한다.

```text
0   = free space
100 = occupied obstacle
```

즉, `occupancy_grid[y, x]` 값이 100이면 해당 셀은 장애물이다.

이 단계에서는 단순히 “벽이냐 아니냐”만 본다.

```text
빈 공간: 지나갈 수 있음
장애물: 지나갈 수 없음
```

하지만 실제 로봇 경로 계획에서는 이것만으로 부족하다. 로봇은 점이 아니라 크기가 있기 때문이다.

---

## 3. Inflation Costmap이 필요한 이유

Occupancy Grid만 사용하면 경로가 벽에 너무 바짝 붙을 수 있다.

예를 들어 로봇 중심점 기준으로는 벽을 안 밟았지만, 실제 로봇 몸체는 벽에 닿을 수 있다.

```text
벽     로봇 중심 경로     벽
███        ·             ███

중심점은 통과하지만 실제 로봇 반지름 때문에 충돌할 수 있음
```

그래서 장애물 주변에 위험 비용을 퍼뜨린다. 이게 Inflation Costmap이다.

실습 코드에서는 다음 값들을 사용한다.

```python
ROBOT_RADIUS_M = 0.25
INFLATION_RADIUS_M = 0.5
LETHAL_COST = 254
INSCRIBED_COST = 253
```

의미는 다음과 같다.

| 값 | 의미 |
|---|---|
| `LETHAL_COST = 254` | 장애물 자체. 통과 불가 |
| `INSCRIBED_COST = 253` | 로봇 반지름 안쪽. 사실상 접촉 위험 영역 |
| `ROBOT_RADIUS_M` | 로봇 반지름 |
| `INFLATION_RADIUS_M` | 로봇 반지름 바깥으로 추가로 비용을 퍼뜨리는 거리 |

---

## 4. Inflation Costmap 생성 흐름

코드 흐름은 크게 두 단계다.

```text
1. 각 셀에서 가장 가까운 장애물까지의 거리 dist_m 계산
2. 거리 dist_m에 따라 cost 값 부여
```

### 4.1 장애물까지 거리 계산

모든 장애물 셀은 거리 0으로 시작한다.

```text
장애물 셀: dist = 0
나머지 셀: dist = inf
```

그 다음 BFS 방식으로 주변 셀의 거리를 퍼뜨린다.

```text
장애물에서 1칸 떨어진 셀 → dist = 1
장애물에서 2칸 떨어진 셀 → dist = 2
...
```

마지막에 grid 단위 거리를 미터 단위로 바꾼다.

```python
dist_m = dist * RES
```

`RES = 0.1`이므로 grid 거리 3칸은 0.3m이다.

---

### 4.2 거리별 cost 부여

실습 코드의 핵심 조건은 다음이다.

```python
if d == 0.0 and occ_grid[y, x] >= 100:
    cost[y, x] = LETHAL_COST
elif d <= robot_r_m:
    cost[y, x] = INSCRIBED_COST
elif d <= robot_r_m + inflation_r_m:
    factor = (d - robot_r_m) / inflation_r_m
    c = int(INSCRIBED_COST * np.exp(-5.0 * factor))
    cost[y, x] = min(INSCRIBED_COST, max(1, c))
else:
    cost[y, x] = 0
```

의미는 다음과 같다.

```text
장애물 자체
→ cost = 254

장애물에서 로봇 반지름 이내
→ cost = 253

로봇 반지름 바깥이지만 inflation 범위 안
→ 거리 증가에 따라 지수적으로 cost 감소

inflation 범위 밖
→ cost = 0
```

---

## 5. Costmap이 너무 퍼져 보일 때 조정하는 법

경로가 장애물에서 너무 멀리 돌아간다면 다음 값을 조정한다.

### 5.1 `INFLATION_RADIUS_M` 줄이기

가장 먼저 볼 값은 `INFLATION_RADIUS_M`이다.

```python
INFLATION_RADIUS_M = 0.5
```

이 값이 크면 장애물 주변 cost가 넓게 퍼진다.

더 타이트하게 접근하고 싶으면 예를 들어 다음처럼 줄인다.

```python
INFLATION_RADIUS_M = 0.15
```

또는 더 공격적으로:

```python
INFLATION_RADIUS_M = 0.10
```

---

### 5.2 지수 감소 계수 키우기

현재 코드는 다음처럼 cost를 감소시킨다.

```python
np.exp(-5.0 * factor)
```

여기서 `5.0`을 키우면 cost가 더 빨리 떨어진다.

```python
DECAY_RATE = 8.0
c = int(INSCRIBED_COST * np.exp(-DECAY_RATE * factor))
```

추천 시작값은 다음 정도다.

```text
INFLATION_RADIUS_M = 0.15
DECAY_RATE = 8.0
```

---

### 5.3 Planner의 cost penalty 줄이기

Dijkstra 이동 비용 계산부에는 다음 식이 있다.

```python
cell_cost = costmap[ny, nx] / 254.0
move_cost = step_cost * RES * (1.0 + 5.0 * cell_cost)
```

여기서 `5.0`은 costmap을 얼마나 강하게 회피할지 결정한다.

너무 멀리 돈다면 다음처럼 줄일 수 있다.

```python
COST_WEIGHT = 2.0
move_cost = step_cost * RES * (1.0 + COST_WEIGHT * cell_cost)
```

권장 조정 순서는 다음과 같다.

```text
1. INFLATION_RADIUS_M 줄이기
2. DECAY_RATE 키우기
3. COST_WEIGHT 줄이기
4. ROBOT_RADIUS_M은 실제 로봇 크기 기준으로 유지
```

`ROBOT_RADIUS_M`을 줄이면 경로는 더 벽에 붙지만 실제 충돌 위험이 커진다.

---

## 6. Dijkstra의 핵심 자료구조

Dijkstra는 다음 네 가지를 중심으로 동작한다.

```python
g_map
parent
visited
open_list
```

| 변수 | 의미 |
|---|---|
| `g_map[y, x]` | 시작점에서 `(x, y)`까지의 현재까지 알려진 최소 누적 비용 |
| `parent[y, x]` | `(x, y)`에 가장 싸게 도착할 때의 직전 셀 |
| `visited[y, x]` | 최단 비용이 확정된 셀인지 여부 |
| `open_list` | 아직 확장할 후보 셀 우선순위 큐 |

---

## 7. Dijkstra 전체 흐름

```text
1. 시작점과 목표점을 grid index로 변환한다.
2. 모든 셀의 g_map을 무한대로 초기화한다.
3. 시작점의 비용만 0으로 둔다.
4. open_list에 시작점을 넣는다.
5. open_list에서 g가 가장 작은 셀을 꺼낸다.
6. 그 셀을 visited로 확정한다.
7. 주변 8방향 이웃을 확인한다.
8. 장애물, 맵 밖, 이미 확정된 셀은 건너뛴다.
9. 현재 셀을 거쳐 이웃으로 가는 new_g를 계산한다.
10. new_g가 기존 g_map보다 작으면 g_map과 parent를 갱신한다.
11. 목표점이 확정되면 종료한다.
12. parent를 목표점부터 역추적해서 최종 경로를 만든다.
```

---

## 8. Open List는 무엇인가?

Dijkstra의 Open List는 아직 확장되지 않은 후보 셀이다.

코드에서는 `heapq`를 사용한다.

```python
heapq.heappush(open_list, (new_g, nx, ny))
g, cx, cy = heapq.heappop(open_list)
```

`heapq`는 튜플의 첫 번째 값으로 정렬한다. 따라서 `(new_g, nx, ny)`를 넣으면 `new_g`가 가장 작은 셀이 먼저 나온다.

즉, Dijkstra는 항상 다음 기준으로 후보를 고른다.

```text
시작점에서 현재 셀까지의 누적 비용 g가 가장 작은 셀
```

---

## 9. Closed List는 무엇인가?

코드에서는 `visited`가 Closed List 역할을 한다.

```python
if visited[cy, cx]:
    continue
visited[cy, cx] = True
```

의미는 다음과 같다.

```text
이 셀은 open_list에서 가장 작은 g로 꺼내졌다.
따라서 시작점에서 이 셀까지의 최단 비용이 확정되었다.
이제 다시 확장하지 않는다.
```

Dijkstra에서는 모든 이동 비용이 0 이상이면, 한 번 가장 작은 비용으로 꺼내진 노드는 나중에 더 싼 경로가 나올 수 없다.

---

## 10. parent는 어디에 쓰이는가?

Dijkstra는 탐색 중에 최종 경로 리스트를 계속 들고 다니지 않는다.

대신 각 셀에 대해 다음 정보를 저장한다.

```text
이 셀에 가장 싸게 도착하려면 바로 직전에 어느 셀에서 와야 하는가?
```

그 저장소가 `parent`다.

```python
parent[ny, nx] = [cx, cy]
```

의미는 다음과 같다.

```text
(nx, ny)에 가장 싸게 도착하는 직전 셀은 (cx, cy)다.
```

---

## 11. 최종 경로 복원

탐색이 끝난 뒤 목표점에서부터 parent를 따라간다.

```python
def reconstruct_path(parent, gx, gy):
    path = []
    cx, cy = gx, gy
    if parent[cy, cx, 0] == -1:
        return []
    while cx != -1 and cy != -1:
        path.append((cx, cy))
        px, py = parent[cy, cx]
        if px == cx and py == cy:
            break
        cx, cy = px, py
    return path[::-1]
```

처음에는 목표점에서 시작한다.

```text
Goal
→ Goal의 부모
→ 그 부모의 부모
→ ...
→ Start
```

이 방향은 거꾸로다.

그래서 마지막에 뒤집는다.

```python
return path[::-1]
```

결과는 다음 순서가 된다.

```text
Start → ... → Goal
```

---

## 12. Dijkstra를 한 문장으로 정리

Dijkstra는 다음 알고리즘이다.

```text
시작점에서 각 셀까지의 누적 비용 g를 관리하면서, open_list에서 g가 가장 작은 셀부터 확장하고, 더 싼 경로가 발견될 때마다 g_map과 parent를 갱신한 뒤, 목표점에서 parent를 역추적해 최종 경로를 만드는 알고리즘이다.
```
