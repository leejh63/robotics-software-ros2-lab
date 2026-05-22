# Background - Scan Matching, Loop Closure, Pose Graph 최소 배경지식

## 1. Scan Matching

Scan Matching은 LiDAR로 본 벽 모양을 기존 지도 또는 이전 scan과 맞춰보는 과정이다.

직관적인 예:

```text
오도메트리: 로봇이 1.0m 앞으로 갔다고 말함
LiDAR scan: 벽 모양을 맞춰보니 실제로는 0.95m 정도가 더 자연스러움
SLAM: 로봇 pose를 조금 보정
```

---

## 2. 왜 scan matching이 필요한가?

오도메트리는 시간이 지나면 틀어진다.

```text
바퀴 미끄러짐
회전 오차
시뮬레이션/현실 차이
노면 상태
```

LiDAR는 주변 구조를 본다.  
그래서 scan matching을 하면 “바퀴 기준 추정”과 “벽 모양 기준 추정”을 비교해 위치를 보정할 수 있다.

---

## 3. Loop Closure

Loop Closure는 예전에 지나갔던 장소에 다시 왔다는 것을 인식하는 것이다.

```text
처음 위치 주변 scan
이후 다시 돌아온 위치의 scan
두 모양이 비슷함
=> 같은 장소일 가능성이 높음
```

SLAM은 이 정보를 이용해서 누적 오차를 전체적으로 줄인다.

---

## 4. Pose Graph

Pose Graph는 로봇의 이동 궤적을 그래프로 보는 방식이다.

```text
pose = 특정 시점의 로봇 위치
edge = pose 사이의 관계
```

edge 종류:

```text
odometry edge
scan matching edge
loop closure edge
```

Loop closure edge가 생기면 그래프 전체를 다시 최적화해서 지도 왜곡을 줄일 수 있다.

---

## 5. 실습에서 기억할 것

```text
scan matching은 현재 scan을 기존 정보와 맞춰보는 것
loop closure는 예전에 온 곳을 다시 알아보는 것
pose graph는 로봇 경로와 제약조건을 그래프로 저장한 것
좋은 loop closure를 얻으려면 로봇이 이미 지나간 곳으로 돌아와야 한다
```
