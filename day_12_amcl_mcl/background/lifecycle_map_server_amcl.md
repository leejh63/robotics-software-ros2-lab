# Lifecycle Node: map_server와 amcl

Nav2 계열 노드 중 일부는 lifecycle node다. `map_server`와 `amcl`도 여기에 해당한다.

---

## 1. lifecycle node란 무엇인가

일반 노드는 실행되면 바로 동작을 시작하는 경우가 많다. 하지만 lifecycle node는 상태 전이가 있다.

```text
unconfigured
  아직 설정되지 않음

inactive
  설정은 되었지만 실제 동작은 비활성

active
  실제 publish/subscribe 동작 수행

finalized
  종료 상태
```

그래서 프로세스가 떠 있다고 해서 바로 정상 동작한다고 보면 안 된다.

---

## 2. 왜 Nav2에서 lifecycle을 쓰는가

Navigation은 여러 노드가 순서대로 준비되어야 한다.

```text
map_server가 먼저 map을 준비
AMCL이 map/scan/TF를 보고 위치 추정 준비
planner/controller가 costmap과 TF를 보고 경로 계산 준비
```

lifecycle은 이런 노드들을 제어 가능한 상태 머신으로 관리하기 위해 사용된다.

---

## 3. 현재 AMCL 실습의 lifecycle 대상

분리 실행 기준:

```text
map_server
amcl
```

확인:

```bash
ros2 lifecycle get /map_server
ros2 lifecycle get /amcl
```

정상:

```text
active [3]
active [3]
```

---

## 4. lifecycle_manager 역할

수동으로 하나씩 configure/activate할 수도 있지만, 실습에서는 lifecycle_manager를 쓴다.

```bash
ros2 run nav2_lifecycle_manager lifecycle_manager \
  --ros-args \
  -p node_names:="['map_server', 'amcl']" \
  -p autostart:=true \
  -p use_sim_time:=true
```

이 노드는 지정된 lifecycle node들을 자동으로 active 상태까지 올린다.

---

## 5. 흔한 문제

### 노드는 있는데 map이 안 나옴

```text
map_server가 active가 아닐 수 있음
```

확인:

```bash
ros2 lifecycle get /map_server
```

### AMCL 노드는 있는데 /amcl_pose가 안 나옴

가능성:

```text
amcl이 active가 아님
initialpose가 아직 없음
/robot_ns/map 또는 /robot_ns/scan을 못 받고 있음
TF가 연결되지 않음
```

확인:

```bash
ros2 lifecycle get /amcl
ros2 node info /amcl
```

---

## 6. 통합 런치에서의 lifecycle

`amcl_full.launch.py`는 아래를 포함한다.

```text
lifecycle_manager_localization
  node_names: ['map_server', 'amcl']
  autostart: True
```

그래서 통합 런치에서는 별도 터미널로 lifecycle_manager를 실행하지 않아도 된다.

분리 실행에서는 직접 실행해야 한다.
