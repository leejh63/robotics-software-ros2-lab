# 03. 기본 RRT 정리

## 1. 이 알고리즘의 이름

`14.03.03.RRT.ipynb`에서 구현한 알고리즘은 **RRT**다.

정확히는 다음에 가깝다.

```text
Goal-biased Basic RRT
```

한국어로 표현하면:

```text
목표점 편향이 들어간 기본 RRT 경로 탐색 알고리즘
```

---

## 2. RRT란?

RRT는 **Rapidly-exploring Random Tree**의 약자다.

말 그대로:

```text
랜덤 샘플을 이용해서 공간을 빠르게 탐색하는 트리 알고리즘
```

이다.

Dijkstra/A*처럼 모든 격자 셀을 비용 기준으로 차근차근 확장하는 방식이 아니다.

RRT는 다음처럼 동작한다.

```text
시작점에 트리의 뿌리를 만든다.
맵 전체에서 랜덤 점을 찍는다.
현재 트리에서 그 랜덤 점과 가장 가까운 노드를 찾는다.
그 노드에서 랜덤 점 방향으로 일정 거리만큼 가지를 뻗는다.
장애물과 충돌하지 않으면 새 노드로 추가한다.
이 과정을 목표 근처에 도달할 때까지 반복한다.
```

---

## 3. RRT와 Dijkstra/A*의 사고방식 차이

### Dijkstra/A*

```text
맵을 격자 그래프로 보고,
각 셀까지의 비용을 계산하면서 확장한다.
```

핵심 변수:

```text
g_map
open_list
closed_list/visited
parent
```

### RRT

```text
연속 공간에 랜덤 점을 찍고,
시작점에서 자라는 트리를 그 방향으로 조금씩 확장한다.
```

핵심 변수:

```text
q_rand
q_near
q_new
nodes
edges
parent_idx
```

---

## 4. RRT의 핵심 파라미터

노트북 코드의 주요 파라미터는 다음이다.

```python
MAX_ITER = 2000
STEP_SIZE = 0.5
GOAL_THRESHOLD = 0.5
GOAL_SAMPLE_RATE = 10
```

| 파라미터 | 의미 |
|---|---|
| `MAX_ITER` | 최대 몇 번 랜덤 확장을 시도할지 |
| `STEP_SIZE` | 한 번에 트리를 얼마나 뻗을지 |
| `GOAL_THRESHOLD` | 목표점에 도달했다고 판단하는 반경 |
| `GOAL_SAMPLE_RATE` | 랜덤 점 대신 목표점을 직접 선택할 확률 |

현재 설정의 의미는 다음과 같다.

```text
최대 2000번 시도
한 번에 최대 0.5m 확장
목표점 0.5m 이내에 들어오면 성공
10% 확률로 q_rand를 goal로 설정
```

---

## 5. RRTNode 구조

코드에서 RRT 노드는 다음 정보를 가진다.

```python
class RRTNode:
    def __init__(self, x, y, parent_idx=None):
        self.x = x
        self.y = y
        self.parent_idx = parent_idx
```

각 필드 의미는 다음과 같다.

| 필드 | 의미 |
|---|---|
| `x` | 노드의 x 좌표, 미터 단위 |
| `y` | 노드의 y 좌표, 미터 단위 |
| `parent_idx` | 이 노드를 만든 부모 노드의 인덱스 |

예를 들어:

```text
nodes[0] = Start, parent_idx = None
nodes[1] = 새 노드, parent_idx = 0
nodes[2] = 새 노드, parent_idx = 1
```

이면 트리는 다음처럼 연결된다.

```text
nodes[0] → nodes[1] → nodes[2]
```

---

## 6. 처음 상태

처음에는 시작점 하나만 트리에 들어간다.

```python
nodes = [RRTNode(START_M[0], START_M[1], None)]
edges = []
```

상태는 다음과 같다.

```text
nodes[0] = (1.0, 1.0)
parent_idx = None
```

그림으로 보면:

```text
Start
  ●
```

아직 가지도 없고 경로도 없다.

---

## 7. 1단계: 랜덤 점 q_rand 생성

코드는 다음과 같다.

```python
if rng.random() * 100 < GOAL_SAMPLE_RATE:
    q_rand = np.array([GOAL_M[0], GOAL_M[1]])
else:
    q_rand = np.array([rng.uniform(0, MAP_W), rng.uniform(0, MAP_H)])
```

즉:

```text
10% 확률: q_rand = Goal
90% 확률: q_rand = 맵 안의 랜덤 점
```

여기서 `q_rand`는 실제로 트리에 추가되는 점이 아니다.

`q_rand`는 방향을 유도하기 위한 점이다.

```text
q_rand = 이번에는 이 방향으로 트리를 뻗어보자고 정하는 참고점
```

---

## 8. 2단계: q_rand와 가장 가까운 q_near 찾기

코드는 다음과 같다.

```python
distances = [np.hypot(n.x - q_rand[0], n.y - q_rand[1]) for n in nodes]
near_idx = int(np.argmin(distances))
q_near = nodes[near_idx]
```

현재 트리에 있는 모든 노드와 `q_rand` 사이의 거리를 계산한다.

그리고 가장 거리가 짧은 노드를 고른다.

```text
q_near = 현재 트리에서 q_rand와 가장 가까운 노드
```

처음 반복에서는 트리에 시작점 하나밖에 없으므로 `q_near`는 시작점이다.

하지만 반복이 진행되어 트리가 커지면, `q_near`는 시작점이 아니라 트리 내부의 다른 노드일 수 있다.

---

## 9. 3단계: q_near에서 q_rand 방향으로 q_new 생성

코드는 다음과 같다.

```python
direction = q_rand - np.array([q_near.x, q_near.y])
dist = np.hypot(direction[0], direction[1])
if dist < 1e-6:
    continue
direction = direction / dist
step = min(STEP_SIZE, dist)
q_new_pos = np.array([q_near.x, q_near.y]) + direction * step
```

이 단계가 RRT의 핵심이다.

`q_rand`까지 한 번에 연결하지 않는다.

대신:

```text
q_near에서 q_rand 방향으로 STEP_SIZE만큼만 이동한 q_new를 만든다.
```

`STEP_SIZE = 0.5`이므로 최대 0.5m만 뻗는다.

그림으로 보면:

```text
q_near ---- q_new ------------------------ q_rand
  ●          ◆                              ★
```

트리에 실제로 추가하려는 후보는 `q_new`다.

`q_rand`는 방향점일 뿐이다.

---

## 10. 4단계: q_near → q_new 충돌 검사

코드는 다음과 같다.

```python
if is_collision_line(q_near.x, q_near.y, q_new_pos[0], q_new_pos[1]):
    continue
```

의미는 다음과 같다.

```text
q_near에서 q_new까지 가는 짧은 직선 구간에 장애물이 있으면
이번 확장은 실패 처리하고 다음 랜덤 점으로 넘어간다.
```

충돌이 있으면 `continue` 때문에 아래의 노드 추가 코드가 실행되지 않는다.

```text
q_new 추가 안 함
edge 추가 안 함
트리 변화 없음
다음 q_rand 생성
```

---

## 11. 5단계: 충돌이 없으면 트리에 추가

충돌이 없으면 새 노드를 만든다.

```python
new_node = RRTNode(q_new_pos[0], q_new_pos[1], near_idx)
new_idx = len(nodes)
nodes.append(new_node)
edges.append((near_idx, new_idx))
```

여기서 `parent_idx = near_idx`다.

즉:

```text
q_new의 부모는 q_near다.
```

트리는 다음처럼 자란다.

```text
Start
  ●
   \
    ◆ q_new
```

---

## 12. 6단계: 목표점 근처인지 확인

새 노드를 추가한 뒤 목표점까지의 거리를 확인한다.

```python
d_to_goal = np.hypot(q_new_pos[0] - GOAL_M[0], q_new_pos[1] - GOAL_M[1])
if d_to_goal <= GOAL_THRESHOLD:
    goal_reached = True
    goal_node_idx = new_idx
    break
```

`GOAL_THRESHOLD = 0.5`다.

즉:

```text
q_new가 goal에서 0.5m 안에 들어오면 성공
```

주의할 점은 목표점에 정확히 도달하는 것이 아니라는 점이다.

```text
정확한 Goal 도착이 아니라 Goal 근처 도착
```

---

## 13. 최종 경로 복원

RRT는 탐색 중에 최종 경로를 계속 저장하지 않는다.

각 노드가 자신의 부모 인덱스를 저장한다.

```text
node.parent_idx = 부모 노드 인덱스
```

목표 근처 노드에 도달하면, 그 노드에서 부모를 거꾸로 따라간다.

```python
def reconstruct_path(nodes, goal_idx):
    path = []
    idx = goal_idx
    while idx is not None:
        path.append(nodes[idx])
        idx = nodes[idx].parent_idx
    return path[::-1]
```

흐름은 다음과 같다.

```text
Goal 근처 노드
→ 부모
→ 부모의 부모
→ ...
→ Start
```

이것은 거꾸로 된 경로이므로 마지막에 뒤집는다.

```text
Start → ... → Goal 근처
```

---

## 14. 한 번의 RRT 반복을 짧게 정리

```text
1. q_rand를 찍는다.
2. 현재 트리에서 q_rand와 가장 가까운 q_near를 찾는다.
3. q_near에서 q_rand 방향으로 STEP_SIZE만큼 q_new를 만든다.
4. q_near → q_new 사이에 장애물이 있는지 검사한다.
5. 장애물이 있으면 이번 시도는 실패 처리한다.
6. 장애물이 없으면 q_new를 트리에 추가한다.
7. q_new가 목표점 근처면 성공 처리한다.
```

---

## 15. RRT가 최단경로 알고리즘이 아닌 이유

기본 RRT는 새 노드를 추가할 때 가장 가까운 노드에 그냥 붙인다.

```text
q_new.parent = q_near
```

하지만 이 연결이 전체 경로 비용 관점에서 가장 좋은지는 확인하지 않는다.

따라서 RRT는 다음을 보장하지 않는다.

```text
최단경로
가장 부드러운 경로
가장 안전한 경로
가장 비용이 낮은 경로
```

RRT의 기본 목적은 다음에 가깝다.

```text
일단 충돌 없는 경로를 빠르게 찾기
```

---

## 16. RRT를 한 문장으로 정리

```text
RRT는 랜덤 점을 찍고, 현재 트리에서 그 점과 가장 가까운 노드를 찾아, 그 방향으로 일정 거리만큼 새 노드를 만들고, 충돌이 없으면 트리에 추가하는 방식으로 시작점에서 목표점 근처까지 트리를 성장시키는 샘플링 기반 경로 탐색 알고리즘이다.
```
