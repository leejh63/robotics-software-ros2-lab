# 06. Dijkstra, A*, RRT, RRT* 비교와 실전 보완점

## 1. 전체 비교표

| 항목 | Dijkstra | A* | RRT | RRT* |
|---|---|---|---|---|
| 계열 | Graph/Grid Search | Graph/Grid Search | Sampling/Tree | Sampling/Tree |
| 핵심 기준 | 최소 `g` | 최소 `g + h` | 랜덤 샘플 방향 확장 | 랜덤 확장 + 비용 최적화 |
| 자료구조 | open/closed, g_map, parent | open/closed, g_map, h, parent | nodes, edges, parent_idx | nodes, edges, parent_idx, cost |
| 목표 방향성 | 없음 | 휴리스틱으로 있음 | Goal bias로 일부 있음 | Goal bias로 일부 있음 |
| 최단경로 보장 | 조건 만족 시 보장 | 휴리스틱 조건 만족 시 보장 | 보장 안 함 | 반복 증가 시 최적에 가까워짐 |
| 경로 형태 | 격자 기반 | 격자 기반 | 연속 좌표 기반 트리 | 연속 좌표 기반 트리 |
| 장점 | 확실하고 이해 쉬움 | Dijkstra보다 빠를 수 있음 | 복잡한 연속 공간에 강함 | RRT보다 경로 품질 개선 |
| 단점 | 넓게 탐색 | 휴리스틱 설계 필요 | 지그재그, 비최적 | 계산량 증가, 구현 복잡 |

---

## 2. Dijkstra를 언제 쓰는가?

Dijkstra는 다음 상황에서 적합하다.

```text
격자 맵이 있고,
각 셀의 이동 비용이 있으며,
최단 비용 경로를 정확히 구하고 싶을 때
```

장점:

```text
최단경로 보장이 명확하다.
구현과 디버깅이 상대적으로 쉽다.
costmap과 잘 어울린다.
```

단점:

```text
목표 방향을 모르기 때문에 넓게 퍼져서 탐색한다.
맵이 커지면 비효율적일 수 있다.
```

---

## 3. A*를 언제 쓰는가?

A*는 Dijkstra에 목표 방향성을 추가한 방식이다.

```text
f(n) = g(n) + h(n)
```

여기서 `h(n)`은 목표까지의 추정 거리다.

예를 들어 2D 격자에서는 다음을 휴리스틱으로 쓸 수 있다.

```text
유클리드 거리
맨해튼 거리
대각선 거리
```

장점:

```text
Dijkstra보다 목표 방향으로 더 빠르게 탐색할 수 있다.
적절한 h를 쓰면 최단경로도 보장할 수 있다.
```

단점:

```text
h를 잘못 잡으면 최적성이 깨질 수 있다.
장애물 구조가 복잡하면 여전히 많은 영역을 탐색할 수 있다.
```

---

## 4. RRT를 언제 쓰는가?

RRT는 다음 상황에서 강점이 있다.

```text
연속 공간에서 경로를 찾고 싶을 때
공간이 넓거나 차원이 높을 때
격자 전체를 다 탐색하기 부담스러울 때
일단 충돌 없는 경로가 필요할 때
```

예를 들어:

```text
모바일 로봇의 연속 좌표 경로
로봇 팔 configuration space
복잡한 장애물 환경
```

장점:

```text
구현 개념이 단순하다.
공간을 빠르게 넓게 탐색한다.
고차원 공간에도 적용하기 좋다.
```

단점:

```text
기본 RRT는 최단경로를 보장하지 않는다.
경로가 지그재그일 수 있다.
실행할 때마다 결과가 달라질 수 있다.
충돌 검사 품질에 민감하다.
```

---

## 5. RRT*를 언제 쓰는가?

RRT*는 RRT보다 경로 품질을 개선하고 싶을 때 사용한다.

기본 RRT는 새 노드를 가장 가까운 노드에 붙인다.

```text
q_new.parent = q_near
```

RRT*는 새 노드 주변을 확인해서 더 싼 부모를 고른다.

```text
q_new.parent = best_parent
```

그리고 기존 노드도 새 노드를 통해 더 싸게 갈 수 있으면 부모를 바꾼다.

```text
rewire
```

장점:

```text
기본 RRT보다 경로가 짧아지고 정리되는 경향이 있다.
반복 횟수가 많아질수록 최적 경로에 가까워지는 성질이 있다.
```

단점:

```text
계산량이 늘어난다.
주변 노드 탐색과 추가 충돌 검사가 필요하다.
정확한 구현에는 cost propagation 같은 세부 처리가 필요하다.
```

---

## 6. Costmap 튜닝 요약

경로가 장애물에서 너무 멀리 떨어진다면 다음을 조정한다.

### 6.1 Inflation 범위 줄이기

```python
INFLATION_RADIUS_M = 0.15
```

기존 값이 0.5라면 cost가 넓게 퍼진다.

타이트한 경로를 원하면 0.15 또는 0.10부터 시험한다.

---

### 6.2 지수 감소 계수 키우기

기존:

```python
np.exp(-5.0 * factor)
```

개선 예:

```python
DECAY_RATE = 8.0
np.exp(-DECAY_RATE * factor)
```

값을 키우면 장애물에서 조금만 멀어져도 cost가 빠르게 낮아진다.

---

### 6.3 Planner cost weight 줄이기

Dijkstra 이동 비용식:

```python
move_cost = step_cost * RES * (1.0 + 5.0 * cell_cost)
```

더 타이트하게 가고 싶으면:

```python
COST_WEIGHT = 2.0
move_cost = step_cost * RES * (1.0 + COST_WEIGHT * cell_cost)
```

단, cost를 너무 약하게 보면 장애물 근처를 지나가 충돌 위험이 커질 수 있다.

---

## 7. RRT/RRT* 파라미터 튜닝 요약

### 7.1 STEP_SIZE

```python
STEP_SIZE = 0.5
```

| 값 | 효과 |
|---|---|
| 작게 | 더 촘촘하게 확장, 좁은 통로에 유리, 느려짐 |
| 크게 | 빠르게 뻗음, 경로 거칠어짐, 장애물 통과 위험 증가 |

좁은 공간에서는 0.3m 정도가 더 안정적일 수 있다.

---

### 7.2 GOAL_SAMPLE_RATE

```python
GOAL_SAMPLE_RATE = 10
```

| 값 | 효과 |
|---|---|
| 작게 | 공간 전체를 더 고르게 탐색 |
| 크게 | 목표 방향으로 더 빨리 가려 함 |

보통 5~20% 정도가 실습용으로 무난하다.

---

### 7.3 GOAL_THRESHOLD

```python
GOAL_THRESHOLD = 0.5
```

| 값 | 효과 |
|---|---|
| 크게 | 성공 판정이 쉬움, 목표에 덜 정확함 |
| 작게 | 목표에 더 정확히 접근, 성공이 어려워질 수 있음 |

정확히 목표에 연결하고 싶으면 threshold만 줄이는 것보다 `q_new → goal` 마지막 직선 연결을 추가하는 것이 더 깔끔하다.

---

### 7.4 REWIRE_RADIUS

RRT* 전용 파라미터다.

```python
REWIRE_RADIUS = 1.5
```

| 값 | 효과 |
|---|---|
| 작게 | 주변 후보가 적어 계산 빠름, 최적화 효과 약함 |
| 크게 | 더 많은 후보 비교, 경로 개선 가능성 증가, 계산량 증가 |

---

## 8. 충돌 검사 실전 보완점

현재 RRT/RRT* 충돌 검사는 선분 위에 점을 여러 개 찍는 방식이다.

```python
for t in np.linspace(0, 1, n_checks):
    ...
```

이 방식은 근사 검사라서 얇은 장애물을 놓칠 가능성이 있다.

추천 개선 순서는 다음이다.

```text
1. 고정 n_checks 대신 RES 기반 샘플 간격 사용
2. DDA/Bresenham으로 선분이 통과하는 모든 grid cell 검사
3. 실제 로봇 크기를 고려해 obstacle inflation 또는 footprint collision check 적용
```

---

## 9. Goal 연결 보완

현재 RRT/RRT*는 다음 방식으로 성공 판정을 한다.

```text
q_new가 goal에서 GOAL_THRESHOLD 안에 들어오면 성공
```

즉, 실제 goal 좌표에 정확히 연결하지 않을 수 있다.

더 깔끔한 방식은 다음이다.

```text
1. q_new가 goal 근처에 들어옴
2. q_new → goal 직선 충돌 검사
3. 충돌이 없으면 goal 노드를 트리에 추가
4. goal 노드부터 parent_idx를 역추적
```

이렇게 하면 최종 경로가 실제 목표점까지 이어진다.

---

## 10. RRT* 구현 보완: subtree cost propagation

현재 RRT* 구현에서 rewiring이 발생하면 해당 노드의 cost는 갱신된다.

```python
n.parent_idx = new_idx
n.cost = new_node.cost + d
```

하지만 그 노드의 자식, 손자 노드 cost까지 갱신하지 않으면 내부 cost 정보가 틀어질 수 있다.

예를 들어:

```text
A → B → C
```

에서 B.cost가 줄어들면 C.cost도 줄어들어야 한다.

정확한 RRT* 구현에서는 다음 처리가 필요하다.

```text
rewire된 노드의 모든 자식 subtree를 따라가며 cost 재계산
```

---

## 11. 학습 관점에서 반드시 잡아야 할 핵심

### Dijkstra

```text
경로 자체를 계속 저장하는 것이 아니라,
각 셀의 최적 이전 셀 parent를 저장하고,
마지막에 parent를 역추적해서 경로를 만든다.
```

### A*

```text
Dijkstra의 g에 목표까지의 추정값 h를 더해 f = g + h로 후보 선택 순서를 바꾼다.
```

### RRT

```text
랜덤 점을 직접 연결하지 않는다.
랜덤 점 방향으로 STEP_SIZE만큼만 q_new를 만들고,
q_near → q_new가 충돌하지 않으면 트리에 추가한다.
```

### RRT*

```text
q_new를 q_near에 바로 붙이지 않는다.
주변 후보 중 cost가 가장 낮아지는 부모를 선택하고,
기존 노드도 더 싸게 연결되면 부모를 바꾼다.
```

---

## 12. 최종 요약

```text
Dijkstra/A*
= grid 기반으로 비용을 계산하며 후보 셀을 확장하는 방식

RRT/RRT*
= 랜덤 샘플을 이용해 시작점에서 트리를 성장시키는 방식

RRT
= 빠르게 충돌 없는 경로를 찾는 데 초점

RRT*
= RRT에 비용 최적화 과정을 추가해 경로 품질을 개선
```

실제 로봇 경로 계획기로 발전시키려면 다음이 필요하다.

```text
1. 안전한 collision checking
2. 로봇 footprint 또는 inflation 반영
3. goal 정확 연결
4. path smoothing
5. local planner/controller와의 연동
6. 동적 장애물 대응
```
