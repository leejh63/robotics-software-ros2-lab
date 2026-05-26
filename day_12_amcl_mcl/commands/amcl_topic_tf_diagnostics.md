# AMCL Topic / TF 진단 명령어

AMCL 문제가 발생하면 topic, lifecycle, TF 순서로 끊긴 지점을 확인한다.

---

## 1. 노드 확인

```bash
ros2 node list
```

기대 노드 예시는 launch namespace 방식에 따라 달라질 수 있다.

```text
Root AMCL case:
  /map_server
  /amcl
  /lifecycle_manager_localization

Namespaced AMCL case:
  /robot_ns/map_server
  /robot_ns/amcl
  /robot_ns/lifecycle_manager_localization
```

노드 상세는 실제 존재하는 이름으로 확인한다.

```bash
ros2 node info /amcl
ros2 node info /robot_ns/amcl
ros2 node info /map_server
ros2 node info /robot_ns/map_server
```

`/amcl` 또는 `/robot_ns/amcl`에서 확인할 것:

```text
Subscribers:
  /robot_ns/map
  /robot_ns/scan
  /initialpose 또는 /robot_ns/initialpose
  /robot_ns/tf
  /robot_ns/tf_static

Publishers:
  /amcl_pose 또는 /robot_ns/amcl_pose
  /particle_cloud 또는 /robot_ns/particle_cloud
  /robot_ns/tf
```

---

## 2. lifecycle 확인

```bash
ros2 lifecycle get /map_server
ros2 lifecycle get /amcl
# namespaced AMCL case라면:
ros2 lifecycle get /robot_ns/map_server
ros2 lifecycle get /robot_ns/amcl
```

정상:

```text
active [3]
```

active가 아니면 lifecycle_manager 또는 파라미터 오류를 본다.

---

## 3. map 확인

```bash
ros2 topic info /robot_ns/map -v
ros2 topic echo /robot_ns/map --once
```

확인 포인트:

```text
header.frame_id: map_robot_ns
width > 0
height > 0
data 존재
```

RViz에서 map이 안 보이면:

```text
Map topic: /robot_ns/map
Durability Policy: Transient Local
Fixed Frame: map_robot_ns
```

---

## 4. scan 확인

```bash
ros2 topic info /robot_ns/scan -v
ros2 topic hz /robot_ns/scan
ros2 topic echo /robot_ns/scan --once
```

확인 포인트:

```text
header.frame_id: base_scan
ranges 배열 존재
range_min: 0.12 근처
range_max: 3.5 근처
```

---

## 5. TF 확인

동적 TF topic이 `/robot_ns/tf`로 remap되어 있으므로 `tf2_echo`에도 remap을 넣는다.

```bash
ros2 run tf2_ros tf2_echo odom_robot_ns base_footprint \
  --ros-args \
  -r /tf:=/robot_ns/tf \
  -r /tf_static:=/robot_ns/tf_static
```

initialpose 후:

```bash
ros2 run tf2_ros tf2_echo map_robot_ns odom_robot_ns \
  --ros-args \
  -r /tf:=/robot_ns/tf \
  -r /tf_static:=/robot_ns/tf_static
```

정상:

```text
transform이 계속 출력됨
```

비정상:

```text
Invalid frame ID
Lookup would require extrapolation
Could not transform
```

---

## 6. initialpose 확인

먼저 실제 initialpose topic 이름을 확인한다.

```bash
ros2 topic list | sort | grep initialpose
```

Root AMCL case:

```bash
ros2 topic echo /initialpose --once
```

Namespaced AMCL case:

```bash
ros2 topic echo /robot_ns/initialpose --once
```

RViz 2D Pose Estimate를 찍은 직후, AMCL이 구독하는 쪽 topic에 메시지가 나와야 한다.

header:

```text
frame_id: map_robot_ns
```

---

## 7. AMCL 출력 확인

먼저 실제 출력 topic 이름을 확인한다.

```bash
ros2 topic list | sort | grep -E 'amcl_pose|particle_cloud'
```

Root AMCL case:

```bash
ros2 topic echo /amcl_pose --once
ros2 topic echo /particle_cloud --once
```

Namespaced AMCL case:

```bash
ros2 topic echo /robot_ns/amcl_pose --once
ros2 topic echo /robot_ns/particle_cloud --once
```

`/amcl_pose` 확인 포인트:

```text
header.frame_id: map_robot_ns
pose.pose.position.x/y 값 존재
pose.covariance 존재
```

`/particle_cloud` 확인 포인트:

```text
particles 배열 존재
```

---

## 8. topic과 frame 대응표

| 확인 대상 | 기대값 |
|---|---|
| map topic | `/robot_ns/map` |
| map frame | `map_robot_ns` |
| scan topic | `/robot_ns/scan` |
| scan frame | `base_scan` |
| odom frame | `odom_robot_ns` |
| base frame | `base_footprint` |
| tf topic | `/robot_ns/tf` |
| tf_static topic | `/robot_ns/tf_static` |
| initialpose topic | `/initialpose` 또는 `/robot_ns/initialpose` |
| amcl pose topic | `/amcl_pose` 또는 `/robot_ns/amcl_pose` |
| particle topic | `/particle_cloud` 또는 `/robot_ns/particle_cloud` |
