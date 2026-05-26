# 02. Open List, Closed List, Dijkstra와 A* 차이

## 1. 핵심 결론

Dijkstra와 A*의 가장 큰 차이는 Open List에서 노드를 고르는 기준이다.

```text
Dijkstra: g(n)이 가장 작은 노드를 선택
A*:       f(n) = g(n) + h(n)이 가장 작은 노드를 선택
```

Open List와 Closed List는 Dijkstra와 A* 모두에서 사용할 수 있는 노드 관리 방식이다. 둘의 차이점 자체가 Open/Closed가 아니다.

---

## 2. g, h, f 의미

| 기호 | 의미 |
|---|---|
| `g(n)` | 시작점에서 현재 노드 n까지 실제로 누적된 비용 |
| `h(n)` | 현재 노드 n에서 목표점까지 남은 비용의 추정값 |
| `f(n)` | A*에서 사용하는 평가값. `f(n) = g(n) + h(n)` |

Dijkstra는 `h`를 사용하지 않는다.

Dijkstra를 A* 관점으로 보면 다음처럼 볼 수도 있다.

```text
Dijkstra = h(n) = 0인 A*
f(n) = g(n) + 0 = g(n)
```

---

## 3. Open List란?

Open List는 다음 의미다.

```text
탐색 과정에서 발견되었지만 아직 주변 이웃으로 확장하지 않은 후보 노드 목록
```

Dijkstra에서는 Open List 안에서 `g`가 가장 작은 노드를 먼저 꺼낸다.

```text
Dijkstra Open List 기준 = 최소 g
```

A*에서는 Open List 안에서 `f = g + h`가 가장 작은 노드를 먼저 꺼낸다.

```text
A* Open List 기준 = 최소 f
```

---

## 4. Closed List란?

Closed List는 다음 의미다.

```text
이미 선택되어 주변 이웃 검사까지 끝난 노드 목록
```

Dijkstra 코드에서는 `visited`가 Closed List 역할을 한다.

```python
if visited[cy, cx]:
    continue
visited[cy, cx] = True
```

의미는 다음과 같다.

```text
이 노드는 이미 확장 완료했다.
다시 확장하지 않는다.
```

Closed List는 중복 탐색을 줄이고, 같은 노드를 반복해서 처리하는 것을 막는다.

---

## 5. Dijkstra에서 Closed 처리의 의미

Dijkstra에서는 어떤 셀이 Open List에서 가장 작은 `g`로 꺼내지는 순간, 그 셀까지의 최단 비용이 확정된다.

이유는 모든 이동 비용이 0 이상이기 때문이다.

```text
음수 비용이 없다
→ 나중에 돌아와서 더 싸지는 일이 없다
→ 최소 g로 꺼낸 순간 확정 가능
```

그래서 Dijkstra에서는 다음 흐름이 성립한다.

```text
Open List에서 최소 g 노드 꺼냄
→ 그 노드의 최단거리 확정
→ Closed List로 보냄
→ 주변 이웃 검사
```

---

## 6. A*에서 Closed 처리의 주의점

A*도 Open List와 Closed List를 사용할 수 있다.

하지만 A*에서 최단경로 보장을 하려면 휴리스틱 `h(n)`이 적절해야 한다.

중요한 조건은 다음이다.

```text
h(n)이 실제 남은 비용을 과대평가하지 않아야 한다.
```

예를 들어 목표까지 실제로 최소 10m가 남았는데, `h(n)`을 100m라고 추정하면 알고리즘이 잘못된 판단을 할 수 있다.

초보 단계에서는 이렇게 이해하면 충분하다.

```text
Dijkstra: 목표 방향을 모름. g만 보고 넓게 퍼짐.
A*: 목표 방향을 추정함. g + h를 보고 목표 쪽으로 더 빠르게 감.
```

---

## 7. Dijkstra 예시

후보 노드가 다음과 같다고 하자.

```text
A: g = 10
B: g = 4
C: g = 7
```

Dijkstra는 `g`가 가장 작은 B를 먼저 선택한다.

```text
선택 순서: B → C → A
```

목표점이 어디 있는지는 고려하지 않는다.

---

## 8. A* 예시

후보 노드가 다음과 같다고 하자.

```text
A: g = 10, h = 1  → f = 11
B: g = 4,  h = 9  → f = 13
C: g = 7,  h = 2  → f = 9
```

Dijkstra라면 B를 먼저 본다. `g = 4`가 가장 작기 때문이다.

하지만 A*는 C를 먼저 본다. `f = 9`가 가장 작기 때문이다.

즉, A*는 현재까지의 비용뿐 아니라 목표까지 가까워 보이는지도 같이 본다.

---

## 9. Dijkstra와 A* 비교

| 항목 | Dijkstra | A* |
|---|---|---|
| 우선순위 기준 | `g(n)` | `f(n) = g(n) + h(n)` |
| 목표 방향 고려 | 안 함 | 함 |
| 탐색 모양 | 시작점 기준으로 사방으로 퍼짐 | 목표 방향으로 치우쳐 탐색 |
| 최단경로 보장 | 모든 비용이 0 이상이면 보장 | 휴리스틱이 적절하면 보장 |
| 보통 속도 | 느릴 수 있음 | 더 빠른 경우가 많음 |
| 구현 난이도 | 상대적으로 단순 | 휴리스틱 설계 필요 |

---

## 10. Open/Closed에 대한 정확한 정리

다음 문장은 A* 설명에 더 가깝다.

```text
Open List 내부에서 총합 평가 지수 f(n)이 가장 작은 노드가 맨 앞으로 오도록 정렬한다.
```

Dijkstra에 대해서는 다음처럼 표현하는 것이 더 정확하다.

```text
Open List 내부에서 누적 비용 g(n)이 가장 작은 노드를 먼저 선택한다.
```

또는 Dijkstra를 A*의 특수한 경우로 표현하면 다음도 가능하다.

```text
Dijkstra는 h(n) = 0인 A*처럼 볼 수 있으므로 f(n) = g(n)이다.
```

---

## 11. 최종 정리

```text
Open List
= 발견은 되었지만 아직 주변 확장이 끝나지 않은 후보 노드들

Closed List
= 이미 선택되어 주변 확장까지 끝난 노드들

Dijkstra
= Open List에서 g가 가장 작은 노드를 꺼냄

A*
= Open List에서 f = g + h가 가장 작은 노드를 꺼냄
```

따라서 Dijkstra와 A*의 본질적 차이는 다음 한 줄이다.

```text
Dijkstra는 현재까지 실제 비용 g만 보고, A*는 현재까지 비용 g와 목표까지 추정 비용 h를 함께 본다.
```
