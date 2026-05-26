# AMCL Day 12 트러블슈팅

AMCL 문제는 파라미터를 바꾸기 전에 map, scan, odom, TF, initialpose 흐름 중 어디서 끊겼는지 먼저 확인한다.

## 빠른 진단표

| 증상 | 먼저 확인할 것 | 확인 명령 | 가능성이 큰 원인 |
|---|---|---|---|
| map이 안 보임 | map_server lifecycle와 map topic | `ros2 lifecycle get /map_server` | map_server inactive, map topic/QoS 문제 |
| scan이 안 보임 | scan topic과 frame_id | `ros2 topic echo /robot_ns/scan --once` | Gazebo sensor topic, LaserScan QoS, TF 문제 |
| `/amcl_pose` 또는 `/robot_ns/amcl_pose`가 안 나옴 | AMCL lifecycle와 initialpose topic 위치 | `ros2 node list \| grep amcl` | AMCL inactive, initialpose 누락, topic namespace 오해 |
| `map_robot_ns -> odom_robot_ns` TF가 없음 | AMCL 입력 데이터 | `ros2 run tf2_ros tf2_echo map_robot_ns odom_robot_ns` | initialpose, scan, map, odom TF 중 하나가 끊김 |
| particle이 퍼져 있음 | map/world 일치와 covariance | RViz `ParticleCloud` 확인 | 초기 위치 오차, map/world 불일치, sensor model 문제 |

AMCL은 파라미터 튜닝보다 입력 데이터와 frame 관계 확인이 먼저다. 공통 진단 순서는 `appendix/troubleshooting_quick_diagnosis.md`를 기준으로 본다.

---


## 1. 전체 판단 순서

```text
1. Gazebo가 떠 있는가?
2. /robot_ns/scan이 나오는가?
3. /robot_ns/map이 나오는가?
4. map_server와 amcl이 active인가?
5. odom_robot_ns -> base_footprint TF가 있는가?
6. initialpose를 줬는가?
7. map_robot_ns -> odom_robot_ns TF가 생겼는가?
8. /particle_cloud가 수렴하는가?
9. scan과 map이 RViz에서 대략 맞는가?
```

---

## 2. Map이 안 보임

확인:

```bash
ros2 lifecycle get /map_server
ros2 topic echo /robot_ns/map --once
```

정상이어야 하는 것:

```text
/map_server active [3]
/robot_ns/map header.frame_id: map_robot_ns
```

RViz 설정:

```text
Fixed Frame: map_robot_ns
Map Topic: /robot_ns/map
Durability Policy: Transient Local
Reliability Policy: Reliable
```

해결:

```text
1. Map display 체크박스를 껐다 켠다.
2. Map display를 삭제 후 /robot_ns/map으로 다시 추가한다.
3. map_yaml 경로가 맞는지 확인한다.
4. frame_id가 map_robot_ns인지 확인한다.
```

---

## 3. LaserScan이 안 보임

확인:

```bash
ros2 topic echo /robot_ns/scan --once
ros2 topic hz /robot_ns/scan
```

정상이어야 하는 것:

```text
header.frame_id: base_scan
ranges 배열 존재
```

RViz 설정:

```text
LaserScan Topic: /robot_ns/scan
Reliability Policy: Best Effort
```

TF 확인:

```bash
ros2 run tf2_ros tf2_echo base_footprint base_scan \
  --ros-args \
  -r /tf:=/robot_ns/tf \
  -r /tf_static:=/robot_ns/tf_static
```

---

## 4. /amcl_pose가 안 나옴

먼저 AMCL node와 topic이 root인지 namespace 아래인지 확인한다.

```bash
ros2 node list | sort | grep amcl
ros2 topic list | sort | grep -E 'initialpose|amcl_pose|particle_cloud'
```

Root AMCL case라면:

```bash
ros2 lifecycle get /amcl
ros2 node info /amcl
ros2 topic echo /initialpose --once
ros2 topic echo /amcl_pose --once
```

Namespaced AMCL case라면:

```bash
ros2 lifecycle get /robot_ns/amcl
ros2 node info /robot_ns/amcl
ros2 topic echo /robot_ns/initialpose --once
ros2 topic echo /robot_ns/amcl_pose --once
```

가능한 원인:

```text
1. /amcl이 active가 아님
2. `/initialpose` 또는 `/robot_ns/initialpose`를 아직 주지 않음
3. /robot_ns/map을 못 받고 있음
4. /robot_ns/scan을 못 받고 있음
5. TF 연결이 안 됨
6. AMCL이 구독하는 initialpose topic과 RViz/CLI가 발행하는 topic이 서로 다름
```

---

## 5. map_robot_ns -> odom_robot_ns TF가 안 나옴

확인:

```bash
ros2 run tf2_ros tf2_echo map_robot_ns odom_robot_ns \
  --ros-args \
  -r /tf:=/robot_ns/tf \
  -r /tf_static:=/robot_ns/tf_static
```

가능한 원인:

```text
tf_broadcast가 false
AMCL이 active가 아님
initialpose가 없음
scan/map/odom 입력이 안 들어옴
/tf remap을 빼고 확인함
```

`tf2_echo`에도 반드시 remap을 넣는다.

---

## 6. scan과 map이 안 맞음

가장 먼저 확인:

```text
world와 map이 같은 짝인가?
```

정상 조합:

```text
slam.world       <-> slam_map.yaml
lee_world.world  <-> room_map.yaml
```

그 다음 확인:

```text
initialpose 위치와 방향이 맞는가?
Fixed Frame이 map_robot_ns인가?
LaserScan frame이 base_scan인가?
base_scan TF가 있는가?
```

---

## 7. ParticleCloud가 이상함

증상:

```text
particle이 너무 넓게 퍼짐
particle이 엉뚱한 곳으로 모임
particle이 보이지 않음
```

확인:

```bash
ros2 topic echo /particle_cloud --once
```

RViz plugin:

```bash
sudo apt install ros-humble-nav2-rviz-plugins
```

해석:

```text
initialpose 직후 잠깐 퍼짐
  정상 가능성 있음

이동해도 계속 수렴하지 않음
  scan-map-TF-world-map 짝 문제 가능성
```

---

## 8. lifecycle이 active가 아님

확인:

```bash
ros2 lifecycle get /map_server
ros2 lifecycle get /amcl
```

통합 런치라면:

```text
lifecycle_manager_localization 로그 확인
node_names: ['map_server', 'amcl'] 확인
```

분리 실행이라면 lifecycle_manager를 따로 실행한다.

```bash
ros2 run nav2_lifecycle_manager lifecycle_manager \
  --ros-args \
  -p node_names:="['map_server', 'amcl']" \
  -p autostart:=true \
  -p use_sim_time:=true
```

---

## 9. 바로 파라미터를 바꾸면 안 되는 경우

아래 문제가 있는 상태에서는 AMCL 파라미터 튜닝을 해도 의미가 없다.

```text
/robot_ns/map 없음
/robot_ns/scan 없음
TF chain 없음
initialpose 없음
world-map 짝 안 맞음
lifecycle inactive
RViz Fixed Frame 틀림
```

파라미터 튜닝은 위 입력들이 정상인 뒤에 한다.
