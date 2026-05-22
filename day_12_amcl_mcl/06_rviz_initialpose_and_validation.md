# 06. RViz, initialpose, 수렴 확인

AMCL 실습에서 RViz는 단순 시각화 도구가 아니다. AMCL이 실제로 위치를 잘 잡는지 확인하는 핵심 도구다.

---

## 1. RViz 기본 설정

Global Options:

```text
Fixed Frame: map_robot_ns
```

Map:

```text
Topic: /robot_ns/map
Reliability Policy: Reliable
Durability Policy: Transient Local
```

LaserScan:

```text
Topic: /robot_ns/scan
Reliability Policy: Best Effort
```

RobotModel:

```text
Description Topic: /robot_ns/robot_description
```

ParticleCloud:

```text
Topic: /particle_cloud
```

필요하면 설치:

```bash
sudo apt install ros-humble-nav2-rviz-plugins
```

---

## 2. initialpose가 필요한 이유

AMCL은 지도를 알고 있어도 로봇이 지도 위 어디에서 시작하는지는 모른다.

그래서 초기 위치를 넣어야 한다.

```text
RViz 2D Pose Estimate
또는
/initialpose topic 발행
```

initialpose는 AMCL에게 이렇게 말하는 것이다.

```text
"로봇은 대충 이 위치와 이 방향 근처에서 시작한다."
```

그러면 AMCL은 그 주변에 particle을 뿌리고, scan과 map을 비교하면서 위치를 좁혀간다.

---

## 3. RViz에서 2D Pose Estimate 사용

가장 쉬운 방법:

```text
1. RViz Fixed Frame을 map_robot_ns로 둔다.
2. /robot_ns/map이 보이는지 확인한다.
3. /robot_ns/scan이 보이는지 확인한다.
4. 상단의 2D Pose Estimate 버튼을 누른다.
5. 지도 위 로봇 위치를 클릭하고 방향을 드래그한다.
6. /particle_cloud가 로봇 주변으로 모이는지 확인한다.
```

주의:

```text
지도 위 위치뿐 아니라 방향도 중요하다.
방향이 크게 틀리면 scan과 map이 맞지 않아 particle이 이상하게 퍼질 수 있다.
```

---

## 4. CLI로 initialpose 발행하기

RViz가 불편하거나 테스트를 자동화하고 싶으면 `/initialpose`를 직접 발행할 수 있다.

예시는 `commands/initialpose_cli_examples.md`에 분리했다.

핵심은 message type이다.

```text
geometry_msgs/msg/PoseWithCovarianceStamped
```

중요 필드:

```text
header.frame_id: map_robot_ns
pose.pose.position.x
pose.pose.position.y
pose.pose.orientation
pose.covariance
```

---

## 5. 수렴 확인 기준

AMCL이 제대로 동작하면 아래가 관찰된다.

```text
1. /particle_cloud가 initialpose 주변에 생긴다.
2. 로봇을 조금 움직이면 particle들이 더 모인다.
3. /amcl_pose가 map_robot_ns 기준으로 나온다.
4. map_robot_ns -> odom_robot_ns TF가 나온다.
5. RViz에서 LaserScan 점이 map 벽과 대략 맞는다.
```

확인 명령:

```bash
ros2 topic echo /amcl_pose --once
ros2 topic echo /particle_cloud --once
ros2 run tf2_ros tf2_echo map_robot_ns odom_robot_ns --ros-args -r /tf:=/robot_ns/tf -r /tf_static:=/robot_ns/tf_static
```

---

## 6. scan과 map이 안 맞을 때

가장 먼저 world-map 짝을 확인한다.

```text
slam.world       <-> slam_map.yaml
lee_world.world  <-> room_map.yaml
```

그 다음 확인할 것:

```text
Fixed Frame이 map_robot_ns인가?
Map topic이 /robot_ns/map인가?
LaserScan topic이 /robot_ns/scan인가?
LaserScan frame_id가 base_scan인가?
base_footprint -> base_scan TF가 있는가?
initialpose 방향을 제대로 줬는가?
```

---

## 7. RViz 표시 문제와 실제 AMCL 문제를 구분하기

RViz에서 안 보인다고 항상 AMCL이 죽은 것은 아니다.

먼저 CLI로 확인한다.

```bash
ros2 lifecycle get /map_server
ros2 lifecycle get /amcl
ros2 topic echo /robot_ns/map --once
ros2 topic echo /robot_ns/scan --once
ros2 topic echo /amcl_pose --once
```

CLI는 정상인데 RViz만 안 보이면 RViz display 설정 문제일 가능성이 크다.

```text
Map display를 껐다 켜기
Map display 삭제 후 /robot_ns/map 기준으로 다시 추가
Durability Policy를 Transient Local로 설정
Fixed Frame을 map_robot_ns로 확인
```

---

## 8. 성공/실패를 빠르게 판단하는 표

| 현상 | 의미 | 먼저 볼 것 |
|---|---|---|
| `/robot_ns/map` 안 나옴 | map_server 문제 | lifecycle, yaml path |
| `/robot_ns/scan` 안 나옴 | Gazebo LiDAR 문제 | Gazebo plugin, topic name |
| `/amcl_pose` 안 나옴 | AMCL 미활성/초기화 문제 | lifecycle, initialpose |
| `map_robot_ns -> odom_robot_ns` 없음 | AMCL TF 출력 문제 | tf_broadcast, initialpose, remap |
| scan이 map과 안 맞음 | world-map mismatch 가능성 | world/map 짝, initialpose 방향 |
| particle이 계속 퍼짐 | 위치 불확실 | scan-map 정합, map 품질, 파라미터 |
