# 05. RRT* 정리

## 1. 이 알고리즘의 이름

`14.03.04.RRTstar.ipynb`에서 구현한 알고리즘은 **RRT\***다.

정확히는 다음에 가깝다.

```text
Goal-biased RRT*
```

한국어로 표현하면:

```text
목표점 편향이 들어간 RRT* 샘플링 기반 경로 계획 알고리즘
```

---

## 2. RRT*가 필요한 이유

기본 RRT는 경로를 빠르게 찾을 수 있지만, 경로 품질이 좋지 않을 수 있다.

기본 RRT는 새 노드를 만들면 보통 이렇게 한다.

```text
q_new.parent = q_near
```

즉, `q_rand`와 가장 가까운 노드인 `q_near`에 그냥 붙인다.

하지만 이것이 시작점에서 `q_new`까지 가는 가장 싼 연결이라는 보장은 없다.

RRT*는 이 문제를 개선한다.

```text
새 노드를 그냥 q_near에 붙이지 않는다.
주변 노드들을 확인해서 q_new까지 가장 싸게 갈 수 있는 부모를 선택한다.
그리고 기존 노드들도 q_new를 통해 더 싸게 갈 수 있으면 부모를 바꾼다.
```

이 두 과정이 핵심이다.

```text
Choose Parent
Rewire
```

---

## 3. RRT와 RRT*의 핵심 차이

| 항목 | RRT | RRT* |
|---|---|---|
| 새 노드 생성 | `q_near`에서 `q_rand` 방향으로 생성 | 동일 |
| 충돌 검사 | `q_near → q_new` 검사 | 동일 |
| 새 노드 부모 | 무조건 `q_near` | 주변 후보 중 최소 비용 부모 |
| 비용 관리 | 보통 없음 | 각 노드에 `cost` 저장 |
| 기존 노드 연결 수정 | 없음 | 더 싸게 연결 가능하면 부모 변경 |
| 경로 품질 | 비최적, 지그재그 가능 | 반복이 늘수록 개선됨 |
| 계산량 | 상대적으로 작음 | 주변 노드 탐색/충돌검사 때문에 더 큼 |

---

## 4. RRT* 노드 구조

RRT*에서는 기본 RRT 노드에 `cost`가 추가된다.

```python
class RRTStarNode:
    def __init__(self, x, y, parent_idx=None):
        self.x = x
        self.y = y
        self.parent_idx = parent_idx
        self.cost = 0.0
```

각 필드 의미는 다음과 같다.

| 필드 | 의미 |
|---|---|
| `x` | 노드의 x 좌표 |
| `y` | 노드의 y 좌표 |
| `parent_idx` | 부모 노드 인덱스 |
| `cost` | 시작점에서 이 노드까지의 누적 경로 비용 |

예를 들어 경로가 다음과 같다고 하자.

```text
Start → A → B → C
```

각 구간 거리가 다음이면:

```text
Start → A = 1.0m
A → B = 0.8m
B → C = 0.7m
```

각 노드의 cost는 다음과 같다.

```text
A.cost = 1.0
B.cost = 1.8
C.cost = 2.5
```

---

## 5. RRT* 주요 파라미터

```python
MAX_ITER = 2000
STEP_SIZE = 0.5
GOAL_THRESHOLD = 0.5
GOAL_SAMPLE_RATE = 10
REWIRE_RADIUS = 1.5
```

RRT와 비교했을 때 `REWIRE_RADIUS`가 추가된다.

| 파라미터 | 의미 |
|---|---|
| `MAX_ITER` | 최대 반복 횟수 |
| `STEP_SIZE` | 한 번에 확장하는 거리 |
| `GOAL_THRESHOLD` | 목표 도달 판정 거리 |
| `GOAL_SAMPLE_RATE` | 목표점을 직접 샘플링할 확률 |
| `REWIRE_RADIUS` | 주변 부모 후보와 rewiring 후보를 찾는 반경 |

---

## 6. RRT* 전체 흐름

RRT*의 전체 흐름은 다음과 같다.

```text
1. 시작점 노드 생성
2. q_rand 샘플링
3. q_rand와 가장 가까운 q_near 찾기
4. q_near에서 q_rand 방향으로 q_new 생성
5. q_near → q_new 충돌 검사
6. q_new 주변의 near_indices 찾기
7. Choose Parent: q_new의 최적 부모 선택
8. q_new를 트리에 추가
9. Rewire: 기존 주변 노드 중 q_new를 거치면 더 싸지는 노드의 부모 변경
10. q_new가 목표 근처면 성공
11. parent_idx를 역추적해서 최종 경로 복원
```

1~5번은 기본 RRT와 거의 같다.

RRT*의 핵심은 6~9번이다.

---

## 7. 1~5단계: 기본 RRT와 같은 부분

먼저 랜덤 점을 찍는다.

```python
if rng.random() * 100 < GOAL_SAMPLE_RATE:
    q_rand = np.array([GOAL_M[0], GOAL_M[1]])
else:
    q_rand = np.array([rng.uniform(0, MAP_W), rng.uniform(0, MAP_H)])
```

그 다음 현재 트리에서 `q_rand`와 가장 가까운 노드 `q_near`를 찾는다.

```python
distances = [np.hypot(n.x - q_rand[0], n.y - q_rand[1]) for n in nodes]
near_idx = int(np.argmin(distances))
q_near = nodes[near_idx]
```

그 다음 `q_near`에서 `q_rand` 방향으로 `STEP_SIZE`만큼 이동한 `q_new`를 만든다.

```text
q_near ---- q_new ---------------- q_rand
  ●          ◆                      ★
```

그리고 `q_near → q_new` 사이가 장애물과 충돌하면 이번 확장은 버린다.

```python
if is_collision_line(q_near.x, q_near.y, q_new_pos[0], q_new_pos[1]):
    continue
```

여기까지는 기본 RRT와 동일하다.

---

## 8. RRT* 핵심 1: 주변 노드 찾기

충돌이 없으면, RRT*는 `q_new` 주변의 기존 노드들을 찾는다.

```python
near_indices = []
for idx, n in enumerate(nodes):
    if calc_distance_pos(n.x, n.y, q_new_pos[0], q_new_pos[1]) <= REWIRE_RADIUS:
        near_indices.append(idx)
```

`REWIRE_RADIUS = 1.5`이므로, `q_new`에서 1.5m 안에 있는 노드들이 후보가 된다.

이 후보들은 두 용도로 사용된다.

```text
1. q_new의 부모 후보
2. q_new를 통해 더 싸게 연결할 수 있는 기존 노드 후보
```

---

## 9. RRT* 핵심 2: Choose Parent

기본 RRT에서는 새 노드의 부모가 무조건 `q_near`다.

RRT*에서는 그렇지 않다.

먼저 `q_near`를 부모로 가정한다.

```python
min_cost = q_near.cost + calc_distance(q_near, RRTStarNode(q_new_pos[0], q_new_pos[1]))
best_parent_idx = near_idx
```

그 다음 주변 후보 노드들을 검사한다.

```python
for idx in near_indices:
    n = nodes[idx]
    d = calc_distance_pos(n.x, n.y, q_new_pos[0], q_new_pos[1])
    if not is_collision_line(n.x, n.y, q_new_pos[0], q_new_pos[1]):
        new_cost = n.cost + d
        if new_cost < min_cost:
            min_cost = new_cost
            best_parent_idx = idx
```

의미는 다음과 같다.

```text
주변 노드 n에서 q_new로 직접 연결할 수 있는가?
연결 가능하다면 n.cost + n에서 q_new까지의 거리를 계산한다.
그 값이 현재 min_cost보다 작으면 q_new의 부모를 n으로 바꾼다.
```

즉:

```text
q_new에 가장 가까운 노드가 아니라,
시작점에서 q_new까지의 전체 누적 비용이 가장 작아지는 노드를 부모로 선택한다.
```

---

## 10. Choose Parent 예시

새 노드 `X`가 생겼다고 하자.

기본 RRT는 가장 가까운 노드 A에 붙인다.

```text
A → X
```

하지만 주변에 B가 있고 비용이 다음과 같다고 해보자.

```text
A.cost = 8.0
A → X 거리 = 0.5
A를 부모로 하면 X.cost = 8.5

B.cost = 5.0
B → X 거리 = 1.0
B를 부모로 하면 X.cost = 6.0
```

B가 X에서 더 멀지만, 시작점에서 B까지 이미 훨씬 싸게 와 있다.

따라서 전체 비용은 B가 더 싸다.

```text
6.0 < 8.5
```

그러면 RRT*는 다음처럼 선택한다.

```text
X.parent = B
X.cost = 6.0
```

이게 Choose Parent다.

---

## 11. 새 노드 추가

최적 부모를 고른 뒤 새 노드를 만든다.

```python
new_node = RRTStarNode(q_new_pos[0], q_new_pos[1], best_parent_idx)
new_node.cost = nodes[best_parent_idx].cost + calc_distance(nodes[best_parent_idx], new_node)
new_idx = len(nodes)
nodes.append(new_node)
edges.append((best_parent_idx, new_idx))
```

의미는 다음과 같다.

```text
q_new의 부모 = best_parent_idx
q_new.cost = best_parent.cost + best_parent에서 q_new까지 거리
```

---

## 12. RRT* 핵심 3: Rewire

Rewire는 기존 노드의 부모를 바꾸는 과정이다.

새 노드 `q_new`가 추가되면, 주변의 기존 노드들이 `q_new`를 거쳐 가는 것이 더 싸질 수 있다.

코드는 다음과 같다.

```python
for idx in near_indices:
    if idx == best_parent_idx:
        continue

    n = nodes[idx]
    d = calc_distance(new_node, n)

    if new_node.cost + d < n.cost:
        if not is_collision_line(new_node.x, new_node.y, n.x, n.y):
            n.parent_idx = new_idx
            n.cost = new_node.cost + d
            edges = [(p, c) for (p, c) in edges if c != idx]
            edges.append((new_idx, idx))
```

의미는 다음과 같다.

```text
기존 노드 n에 대해,
기존 n.cost보다 q_new를 거쳐 가는 비용이 더 싼가?
그리고 q_new → n 연결이 장애물과 충돌하지 않는가?
그렇다면 n의 부모를 q_new로 바꾼다.
```

---

## 13. Rewire 예시

기존 트리가 다음과 같다고 하자.

```text
Start → A → C
C.cost = 10
```

새 노드 X가 추가되었다.

```text
Start → B → X
X.cost = 6
X → C 거리 = 1
```

X를 통해 C로 가면 비용은 다음이다.

```text
X.cost + X→C = 6 + 1 = 7
```

기존 C.cost는 10이었다.

```text
7 < 10
```

그러면 RRT*는 C의 부모를 바꾼다.

```text
기존: A → C
변경: X → C
```

이것이 Rewire다.

---

## 14. edges를 수정하는 이유

`edges`는 시각화용 부모-자식 연결 목록이다.

새 노드를 추가할 때는 다음 간선을 넣는다.

```python
edges.append((best_parent_idx, new_idx))
```

Rewire할 때는 기존에 `idx`로 들어오던 간선을 제거하고 새 간선을 추가한다.

```python
edges = [(p, c) for (p, c) in edges if c != idx]
edges.append((new_idx, idx))
```

의미는 다음과 같다.

```text
idx 노드의 기존 부모 연결 제거
q_new → idx 연결 추가
```

그래야 시각화에서 바뀐 부모 관계가 제대로 보인다.

---

## 15. 목표 도달과 경로 복원

새 노드를 추가한 뒤 목표점과의 거리를 확인한다.

```python
d_to_goal = np.hypot(q_new_pos[0] - GOAL_M[0], q_new_pos[1] - GOAL_M[1])
if d_to_goal <= GOAL_THRESHOLD:
    goal_reached = True
    goal_node_idx = new_idx
    break
```

`GOAL_THRESHOLD = 0.5`다.

즉, 목표점에서 0.5m 안에 들어오면 성공으로 처리한다.

경로 복원은 기본 RRT와 같다.

```python
def reconstruct_path(nodes, goal_idx):
    path = []
    idx = goal_idx
    while idx is not None:
        path.append(nodes[idx])
        idx = nodes[idx].parent_idx
    return path[::-1]
```

`goal_idx`에서 부모를 따라 시작점까지 올라간 뒤 뒤집는다.

---

## 16. RRT*가 최적이라는 말의 의미

RRT*가 “최적”이라는 말은 다음 뜻이 아니다.

```text
한 번 실행하면 반드시 최단경로가 나온다.
```

정확한 의미는 다음에 가깝다.

```text
샘플 수가 충분히 많아지고 조건이 적절하면,
반복이 늘어날수록 최적 경로에 점점 가까워지는 성질이 있다.
```

이것을 점근적 최적성이라고 한다.

따라서 실습에서 나온 RRT* 경로도 진짜 전역 최단경로라고 단정하면 안 된다.

더 정확히는:

```text
기본 RRT보다 경로를 점진적으로 개선하는 알고리즘
```

이라고 이해하는 것이 맞다.

---

## 17. 이 노트북 구현의 주의점

### 17.1 충돌 검사가 샘플링 기반이다

RRT와 마찬가지로 선분 위에 일부 점을 찍어서 검사한다.

```python
def is_collision_line(x1, y1, x2, y2, n_checks=20):
```

얇은 장애물을 놓칠 가능성이 있으므로, `RES` 기반 검사 또는 DDA/Bresenham 방식이 더 안전하다.

---

### 17.2 로봇 크기를 고려하지 않는다

현재 충돌 검사는 점 기준이다.

```python
occupancy_grid[iy, ix] >= 100
```

실제 로봇에는 장애물 inflation 또는 footprint collision check가 필요하다.

---

### 17.3 Goal에 정확히 연결하지 않는다

현재는 goal 근처에 들어오면 성공이다.

```text
Goal 정확 도착이 아니라 Goal 주변 도착
```

더 정확히 하려면:

```text
q_new가 goal 근처에 들어왔을 때
q_new → goal 직선 충돌 검사
충돌이 없으면 goal 노드를 추가
```

하는 방식이 좋다.

---

### 17.4 Rewire 후 자식 노드 cost 전파가 부족할 수 있다

현재 코드에서 어떤 노드 `n`이 rewiring되면 다음이 바뀐다.

```python
n.parent_idx = new_idx
n.cost = new_node.cost + d
```

하지만 `n`의 자식, 손자 노드들의 cost까지 재귀적으로 갱신하지 않는다.

예를 들어:

```text
A → B → C
```

에서 B의 부모가 바뀌어 B.cost가 줄어들면 C.cost도 같이 줄어야 한다.

정확한 RRT* 구현에서는 subtree cost propagation이 필요하다.

---

## 18. RRT*를 한 문장으로 정리

```text
RRT*는 RRT처럼 랜덤 샘플링으로 트리를 확장하되, 각 노드의 시작점 기준 누적 비용 cost를 관리하면서 새 노드의 부모를 가장 싼 후보로 선택하고, 기존 노드들도 새 노드를 통해 더 싸게 연결될 수 있으면 부모를 바꾸는 방식으로 경로를 점진적으로 최적화하는 알고리즘이다.
```
