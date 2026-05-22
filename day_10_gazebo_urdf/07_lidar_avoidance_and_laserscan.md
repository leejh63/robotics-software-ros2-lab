# 07. LiDAR 회피 노드와 LaserScan 해석

## 1. 현재 노드의 성격

`scripts/lidar_wall_follower.py`는 이름만 보면 벽 따라가기처럼 보이지만, 현재 로직은 더 단순하다.

```text
/robot_ns/scan을 구독한다.
정면 각도 범위의 거리값만 본다.
가까운 장애물이 있으면 회전한다.
장애물이 없으면 직진한다.
/robot_ns/cmd_vel로 Twist를 발행한다.
```

즉 “wall follower”라기보다 **정면 장애물 회피 예제**에 가깝다.

---

## 2. 노드 입출력

| 구분 | topic | message type | 의미 |
|---|---|---|---|
| subscribe | `/robot_ns/scan` | `sensor_msgs/msg/LaserScan` | Gazebo LiDAR plugin이 발행한 거리 배열 |
| publish | `/robot_ns/cmd_vel` | `geometry_msgs/msg/Twist` | Gazebo diff drive plugin으로 들어가는 속도 명령 |

흐름:

```text
Gazebo LiDAR plugin
        ↓
/robot_ns/scan
        ↓
lidar_wall_follower.py
        ↓
/robot_ns/cmd_vel
        ↓
Gazebo diff_drive plugin
        ↓
robot moves
```

---

## 3. 주요 parameter

| parameter | 기본값 | 의미 |
|---|---:|---|
| `scan_topic` | `/robot_ns/scan` | 입력 LaserScan topic |
| `cmd_vel_topic` | `/robot_ns/cmd_vel` | 출력 Twist topic |
| `obstacle_distance` | `0.55` | 이 거리보다 가까우면 장애물로 판단 |
| `front_angle_deg` | `25.0` | 정면으로 간주할 각도 범위 |
| `forward_speed` | `0.16` | 전진 속도 |
| `turn_speed` | `0.45` | 회전 속도 |
| `turn_direction` | `right` | 장애물 발견 시 회전 방향 |
| `control_rate` | `10.0` | 제어 주기 Hz |

---

## 4. LaserScan 메시지 구조

`sensor_msgs/msg/LaserScan`에서 핵심 필드는 다음이다.

```text
angle_min
  ranges[0]이 가리키는 각도

angle_max
  마지막 range가 가리키는 각도

angle_increment
  ranges 배열에서 인접한 값 사이의 각도 간격

range_min / range_max
  유효 거리 범위

ranges
  각 방향별 거리값 배열
```

중요한 계산식:

```python
angle = scan.angle_min + index * scan.angle_increment
```

이 식은 `ranges[index]`가 어느 각도 방향의 거리인지 계산하는 식이다.

---

## 5. 왜 index로 angle을 계산하는가

LiDAR 메시지는 보통 “각도별 거리값”을 배열로 보낸다. 그런데 배열 index만 보고는 그 값이 정면인지 왼쪽인지 오른쪽인지 알 수 없다.

예를 들어 현재 Gazebo LiDAR 설정은 대략 다음과 같다.

```text
min_angle = -3.14159
max_angle =  3.14159
samples   = 360
```

즉 약 -180도부터 +180도까지 360개 샘플이 있다.

```text
ranges[0]   -> 약 -180도 방향
ranges[90]  -> 약 -90도 방향
ranges[180] -> 약 0도 방향
ranges[270] -> 약 +90도 방향
```

하지만 이것은 현재 설정 기준의 예시일 뿐이다. 모든 LiDAR에서 `ranges[180]`이 정면이라고 외우면 안 된다. 반드시 `angle_min`, `angle_increment`로 계산해야 한다.

---

## 6. 현재 코드의 정면 거리 계산

현재 코드는 대략 이런 방식이다.

```python
half_angle = math.radians(self.front_angle_deg)
front_ranges = []

for index, distance in enumerate(scan.ranges):
    if not math.isfinite(distance):
        continue
    if distance < scan.range_min or distance > scan.range_max:
        continue

    angle = scan.angle_min + index * scan.angle_increment
    if -half_angle <= angle <= half_angle:
        front_ranges.append(distance)

return min(front_ranges) if front_ranges else math.inf
```

의미:

```text
1. ranges 전체를 돈다.
2. inf, nan, 유효 범위 밖 거리값은 제외한다.
3. index를 각도로 변환한다.
4. -front_angle_deg ~ +front_angle_deg 범위만 정면으로 본다.
5. 그중 가장 가까운 거리값을 정면 장애물 거리로 사용한다.
```

---

## 7. 제어 로직

```text
latest_scan이 아직 없다
  -> 정지 명령 publish

front_distance < obstacle_distance
  -> linear.x = 0.0
  -> angular.z = turn_speed 또는 -turn_speed

front_distance >= obstacle_distance
  -> linear.x = forward_speed
  -> angular.z = 0.0
```

이 로직은 매우 단순하다. 벽과 일정 거리를 유지하는 제어가 아니라, 정면 충돌만 피하는 반응형 제어다.

---

## 8. teleop과 동시에 쓰면 생기는 문제

`teleop_twist_keyboard`와 `lidar_wall_follower.py`를 동시에 실행하면 둘 다 `/robot_ns/cmd_vel`을 발행할 수 있다.

```text
teleop_twist_keyboard -> /robot_ns/cmd_vel
lidar_wall_follower.py -> /robot_ns/cmd_vel
```

이 경우 마지막으로 도착한 Twist가 로봇 움직임을 결정하므로 조작이 이상하게 보일 수 있다.

학습할 때는 둘 중 하나만 켜는 것이 좋다.

```bash
# 회피 노드 끄고 수동 조작
ros2 launch lee_robot_description gaze.launch.py use_avoidance:=false

# 회피 노드만 켜고 자동 움직임 확인
ros2 launch lee_robot_description gaze.launch.py use_avoidance:=true
```

---

## 9. 핵심 결론

```text
LaserScan의 ranges 배열은 거리값만 담고 있다.
각 range가 어느 방향인지 알려면 angle_min + index * angle_increment를 계산해야 한다.
```

이 이해는 Day 11 SLAM, Day 12 AMCL, 장애물 회피, costmap 이해로 그대로 이어진다.
