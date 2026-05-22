# map_robot_ns / odom_robot_ns frame 이름을 쓰는 이유

이 문서는 일반 ROS/Nav2 예제에서 자주 보는 `map`, `odom`과, 이 학습 노트에서 사용하는 `map_robot_ns`, `odom_robot_ns`의 관계를 정리한다.

결론부터 말하면 `map_robot_ns`, `odom_robot_ns`는 완전히 새로운 개념이 아니다. 일반 예제의 `map`, `odom`에 **로봇 namespace 의미를 붙인 frame 이름**으로 보면 된다.

---

## 1. 일반 예제에서의 기본 TF 구조

Nav2, SLAM, AMCL 예제에서는 보통 아래 frame 이름을 쓴다.

```text
map -> odom -> base_link -> laser
```

의미는 다음과 같다.

| Frame | 의미 |
|---|---|
| `map` | 저장된 지도 기준 전역 좌표계 |
| `odom` | odometry 기준 지역 좌표계 |
| `base_link` | 로봇 본체 기준 좌표계 |
| `laser` 또는 `base_scan` | LiDAR 센서 기준 좌표계 |

이름이 단순해서 처음 배우기에는 좋다. 하지만 여러 robot namespace를 쓰거나, rosbag replay와 simulation을 섞거나, 여러 사람이 같은 ROS graph를 볼 때는 `map`, `odom` 같은 공통 이름이 충돌하기 쉽다.

---

## 2. 이 학습 노트의 frame 이름

이 학습 노트에서는 아래처럼 frame을 일반화해서 기록한다.

```text
map_robot_ns -> odom_robot_ns -> base_footprint -> base_link -> base_scan
```

각 frame의 의미는 다음과 같다.

| Frame | 일반 예제 대응 | 의미 |
|---|---|---|
| `map_robot_ns` | `map` | `robot_ns` 로봇의 지도 기준 전역 frame |
| `odom_robot_ns` | `odom` | `robot_ns` 로봇의 odometry 기준 지역 frame |
| `base_footprint` | `base_link` 또는 `base_footprint` | navigation에서 쓰는 로봇 기준 frame |
| `base_link` | `base_link` | URDF의 로봇 본체 link frame |
| `base_scan` | `laser` 또는 `base_scan` | LiDAR frame |

즉, 핵심 구조는 그대로다.

```text
map -> odom -> base
```

다만 현재 문서에서는 충돌을 피하기 위해 아래처럼 쓴다.

```text
map_robot_ns -> odom_robot_ns -> base_footprint
```

---

## 3. 왜 frame 이름에도 namespace 의미를 붙였는가

ROS2에서 topic namespace와 TF frame 이름은 같은 것이 아니다.

예를 들어 topic은 namespace를 붙여 이렇게 분리할 수 있다.

```text
/robot_ns/scan
/robot_ns/odom
/robot_ns/cmd_vel
```

하지만 message 안의 `header.frame_id`와 TF frame 이름은 문자열이다. topic namespace를 바꾼다고 frame 이름이 자동으로 바뀌지 않는다.

예를 들어 bag이나 simulation에서 아래처럼 topic만 namespace 아래에 있어도:

```text
Topic: /robot_ns/scan
```

LaserScan message 내부는 여전히 이렇게 되어 있을 수 있다.

```text
header.frame_id: base_scan
```

마찬가지로 `/robot_ns/tf` topic 안에 들어 있는 TF frame 이름도 자동으로 `/robot_ns/map`, `/robot_ns/odom`이 되는 것이 아니다. TF frame은 보통 `/`를 붙인 topic처럼 다루지 않고, frame 이름 문자열로 다룬다.

그래서 여러 로봇 또는 여러 namespace 상황을 고려하면 frame 이름 자체도 분리하는 편이 안전하다.

```text
robot_ns용 map frame  -> map_robot_ns
robot_ns용 odom frame -> odom_robot_ns
```

---

## 4. 충돌을 피해야 하는 상황

단일 로봇만 실행할 때는 `map`, `odom`을 써도 동작할 수 있다. 하지만 아래 상황에서는 문제가 생길 수 있다.

```text
1. 여러 로봇을 같은 ROS_DOMAIN_ID에서 실행하는 경우
2. 다른 사람이 실행한 /tf, /map, /odom 정보가 같은 graph에 보이는 경우
3. rosbag replay topic은 remap했지만 frame_id는 그대로 남아 있는 경우
4. simulation과 bag replay를 동시에 확인하는 경우
5. Nav2 parameter는 map_robot_ns/odom_robot_ns를 보는데 실제 TF는 map/odom으로 나오는 경우
```

대표적인 충돌은 다음과 같다.

```text
Topic은 /robot_ns/scan으로 맞음
하지만 LaserScan.header.frame_id는 다른 TF tree와 연결됨
또는 AMCL parameter는 map_robot_ns를 보는데 map topic의 header.frame_id는 map임
```

이런 경우 topic list만 보면 정상처럼 보여도 RViz, AMCL, Nav2는 좌표계를 연결하지 못할 수 있다.

---

## 5. AMCL에서 특히 중요한 이유

AMCL parameter에는 frame 이름이 직접 들어간다.

```yaml
global_frame_id: map_robot_ns
odom_frame_id: odom_robot_ns
base_frame_id: base_footprint
```

이 값들은 topic 이름이 아니라 TF frame 이름이다.

AMCL은 아래 데이터를 함께 사용한다.

```text
map topic
scan topic
odom_robot_ns -> base_footprint TF
initialpose
```

그리고 최종적으로 아래 TF를 만든다.

```text
map_robot_ns -> odom_robot_ns
```

따라서 다음 네 가지가 서로 맞아야 한다.

| 항목 | 맞아야 하는 값 |
|---|---|
| map message `header.frame_id` | `map_robot_ns` |
| AMCL `global_frame_id` | `map_robot_ns` |
| AMCL `odom_frame_id` | `odom_robot_ns` |
| 실제 odom TF | `odom_robot_ns -> base_footprint` |

하나라도 다르면 `/amcl_pose`가 나와도 RViz나 Nav2에서 전체 TF chain이 이어지지 않을 수 있다.

---

## 6. SLAM과 AMCL에서 발행 주체 차이

`map_robot_ns -> odom_robot_ns` 성격의 TF는 상황에 따라 발행 주체가 다르다.

| 상황 | 주 발행자 | 의미 |
|---|---|---|
| SLAM 중 | SLAM Toolbox | scan/odom으로 지도를 만들면서 map과 odom 관계 추정 |
| 저장된 map으로 localization 중 | AMCL | 저장된 map과 scan을 비교해 odom drift 보정 |
| Nav2 주행 중 | AMCL이 계속 유지 | Nav2는 이 TF chain을 사용해 costmap과 goal을 해석 |

중요한 점은 `map_server`는 map topic을 발행할 뿐, `map_robot_ns -> odom_robot_ns` TF를 만들어주는 node가 아니라는 것이다.

---

## 7. 확인 명령

현재 frame 이름이 무엇인지 외우지 말고 직접 확인한다.

```bash
ros2 topic echo /robot_ns/map --once | grep frame_id
ros2 topic echo /robot_ns/scan --once | grep frame_id
ros2 run tf2_ros tf2_echo odom_robot_ns base_footprint
ros2 run tf2_ros tf2_echo map_robot_ns odom_robot_ns
```

TF topic이 namespace 아래에 있는 환경에서는 remap이 필요할 수 있다.

```bash
ros2 run tf2_ros tf2_echo map_robot_ns odom_robot_ns   --ros-args -r /tf:=/robot_ns/tf -r /tf_static:=/robot_ns/tf_static
```

Nav2 goal도 같은 기준을 써야 한다.

```text
NavigateToPose goal header.frame_id: map_robot_ns
```

---

## 8. 이 문서에서 쓰는 표기 기준

이 저장소에서는 아래 표기를 기본으로 둔다.

```text
robot namespace: robot_ns
map topic      : /robot_ns/map
scan topic     : /robot_ns/scan
cmd_vel topic  : /robot_ns/cmd_vel
map frame      : map_robot_ns
odom frame     : odom_robot_ns
base frame     : base_footprint
scan frame     : base_scan
```

정리하면 다음과 같다.

```text
/robot_ns/map은 topic 이름이고,
map_robot_ns는 frame 이름이다.

/robot_ns/odom은 topic 이름이고,
odom_robot_ns는 frame 이름이다.
```

topic 이름과 frame 이름을 섞지 않는 것이 SLAM, AMCL, Nav2 디버깅의 핵심이다.
