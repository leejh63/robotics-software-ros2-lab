# 03. AMCL 데이터 흐름과 TF 구조

## 1. AMCL의 필수 입력

AMCL이 위치를 추정하려면 최소한 네 가지가 필요하다.

```text
1. 저장된 지도
2. 현재 LiDAR scan
3. odometry 기반 TF
4. 초기 위치 힌트
```

현재 환경 기준:

| 입력 | 현재 이름 | 역할 |
|---|---|---|
| 지도 | `/robot_ns/map` | Day 11에서 만든 static map |
| LiDAR | `/robot_ns/scan` | 현재 로봇 주변 장애물 거리 |
| odom TF | `odom_robot_ns -> base_footprint` | 로봇이 상대적으로 얼마나 움직였는지 |
| 초기 위치 | `/initialpose` 또는 `/robot_ns/initialpose` | 지도 위에서 처음 어느 근처에 있는지 |

---

## 2. AMCL의 출력

AMCL 출력은 세 가지로 보면 된다.

| 출력 | 의미 |
|---|---|
| `/amcl_pose` 또는 `/robot_ns/amcl_pose` | `map_robot_ns` 기준 현재 추정 위치와 covariance |
| `/particle_cloud` 또는 `/robot_ns/particle_cloud` | 위치 후보 particle들의 분포 |
| `map_robot_ns -> odom_robot_ns` TF | odom drift를 map 기준으로 보정하는 변환 |

중요한 해석:

```text
/amcl_pose는 사람이 확인하기 좋은 결과 토픽이다.
Nav2와 RViz 좌표계 연결에서 더 중요한 것은 map_robot_ns -> odom_robot_ns TF다.
```

### AMCL topic namespace case

AMCL 관련 topic은 launch 구조에 따라 root namespace에 있을 수도 있고, robot namespace 아래에 있을 수도 있다.

```text
Case A - root AMCL:
  /amcl
  /initialpose
  /amcl_pose
  /particle_cloud

Case B - namespaced AMCL:
  /robot_ns/amcl
  /robot_ns/initialpose
  /robot_ns/amcl_pose
  /robot_ns/particle_cloud
```

중요한 것은 외운 이름으로 바로 echo하지 않는 것이다. 먼저 현재 graph를 확인한다.

```bash
ros2 node list | sort | grep amcl
ros2 topic list | sort | grep -E 'initialpose|amcl_pose|particle_cloud'
ros2 node info /amcl
ros2 node info /robot_ns/amcl
```

실제 node가 `/amcl`이면 root AMCL case를 보고, `/robot_ns/amcl`이면 namespaced AMCL case를 본다. 자세한 기준은 [`../appendix/amcl_namespace_cases.md`](../appendix/amcl_namespace_cases.md)를 참고한다.

---

## 3. 왜 map_robot_ns -> odom_robot_ns TF가 필요한가

일반 ROS/Nav2 예제에서는 보통 `map -> odom -> base_link` 구조를 사용한다. 이 학습 노트에서는 같은 구조를 아래처럼 namespace 의미가 드러나는 frame 이름으로 기록한다.

```text
map_robot_ns -> odom_robot_ns -> base_footprint
```

즉, `map_robot_ns`는 일반 예제의 `map`, `odom_robot_ns`는 일반 예제의 `odom`에 대응한다. 이렇게 이름을 붙인 이유는 여러 robot namespace, rosbag replay, 다른 사용자의 ROS graph가 섞이는 상황에서 TF frame 충돌을 줄이기 위해서다. 자세한 배경은 [`background/map_odom_namespace_frames.md`](background/map_odom_namespace_frames.md)를 참고한다.

로봇의 바퀴 odom은 짧은 시간에는 부드럽다. 하지만 시간이 지나면 오차가 누적된다.

```text
odom_robot_ns -> base_footprint
  로봇이 시작점 기준으로 얼마나 움직였는지 알려준다.
  부드럽지만 drift가 쌓인다.
```

반면 지도 좌표계는 전역 기준이다.

```text
map_robot_ns
  저장된 지도 기준 좌표계
  장기적으로 맞아야 하는 기준
```

AMCL은 LiDAR와 map을 비교해서 odom의 누적 오차를 보정한다. 그 보정 관계가 아래 TF다.

```text
map_robot_ns -> odom_robot_ns
```

전체 TF chain:

```text
map_robot_ns
  -> odom_robot_ns
      -> base_footprint
          -> base_link
              -> base_scan
```

RViz가 로봇과 scan을 map 위에 표시하려면 이 chain이 이어져야 한다.

---

## 4. map_server는 TF를 만들지 않는다

`map_server`는 지도를 topic으로 발행한다.

```text
map_server 출력:
  /robot_ns/map
```

하지만 `map_server`가 `map_robot_ns -> odom_robot_ns` TF를 만들어주는 것은 아니다.

```text
map_server 역할:
  저장된 map을 발행

AMCL 역할:
  map과 scan을 비교해서 map_robot_ns -> odom_robot_ns TF를 발행
```

따라서 `/robot_ns/map`이 나온다고 해서 AMCL 위치 추정이 된 것은 아니다.

---

## 5. initialpose 전후 차이

AMCL은 지도를 알고 있어도 로봇이 지도 위 어디에서 시작하는지는 모른다. 그래서 초기 위치 힌트가 필요하다.

initialpose 전:

```text
map은 보일 수 있음
scan도 보일 수 있음
하지만 particle이 제대로 모이지 않을 수 있음
map_robot_ns -> odom_robot_ns TF가 안정적이지 않을 수 있음
```

initialpose 후:

```text
particle이 지정한 위치 주변에 뿌려짐
scan과 map 비교가 시작됨
particle이 점점 수렴함
/amcl_pose가 의미 있는 값이 됨
map_robot_ns -> odom_robot_ns TF가 안정됨
```

---

## 6. /particle_cloud 해석

`/particle_cloud`는 “정답 위치”가 아니라 “후보 위치 분포”다.

```text
넓게 퍼져 있음
  아직 위치가 불확실함

로봇 주변에 모여 있음
  위치 추정이 수렴 중이거나 수렴했음

지도와 전혀 안 맞는 곳에 모임
  initialpose, map-world 짝, scan frame, TF 문제 가능성
```

ParticleCloud를 RViz에서 볼 때는 일반 PointCloud가 아니라 Nav2 AMCL용 display가 필요할 수 있다.

---

## 7. topic 이름과 frame 이름을 같이 맞춰야 하는 이유

AMCL에서 흔한 착각:

```text
/scan을 /robot_ns/scan으로 remap했으니 frame도 자동으로 맞겠지?
```

그렇지 않다.

```text
topic remap:
  ROS graph에서 topic 이름만 바꿈

frame_id:
  메시지 내부 header.frame_id 또는 TF tree의 좌표계 이름
```

예를 들어 `/robot_ns/scan` 메시지 내부가 아래처럼 되어 있어야 한다.

```text
header.frame_id: base_scan
```

그리고 TF tree에는 아래 경로가 있어야 한다.

```text
base_footprint -> base_scan
```

AMCL은 scan topic만 보는 것이 아니라 scan의 frame과 TF도 함께 사용한다.

---

## 8. Day 13 Nav2와 연결되는 지점

Day 13 Nav2는 AMCL 결과를 직접적으로 의존한다.

```text
Nav2가 필요한 것:
  /robot_ns/map
  /robot_ns/scan
  map_robot_ns -> odom_robot_ns -> base_footprint TF
  현재 pose
```

AMCL이 안 되면 Nav2는 목표 지점까지 이동할 수 없다. 그래서 Day 13으로 넘어가기 전에는 아래를 먼저 확인해야 한다.

```bash
ros2 lifecycle get /map_server
ros2 lifecycle get /amcl
ros2 topic list | grep -E 'amcl_pose|particle_cloud|initialpose'
ros2 topic echo /amcl_pose --once            # root AMCL case
ros2 topic echo /robot_ns/amcl_pose --once   # namespaced AMCL case
ros2 run tf2_ros tf2_echo map_robot_ns odom_robot_ns --ros-args -r /tf:=/robot_ns/tf -r /tf_static:=/robot_ns/tf_static
```
