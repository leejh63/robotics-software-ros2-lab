# Background - map, odom, base frame 관계

## 1. 세 frame의 역할

현재 실습 기준:

```text
map_robot_ns
  전역 지도 기준 좌표계

odom_robot_ns
  오도메트리 기준 좌표계

base_footprint
  로봇 바닥 중심 기준 좌표계
```

---

## 2. 왜 map과 odom이 둘 다 필요한가?

`odom_robot_ns`는 짧은 시간의 움직임을 부드럽게 표현한다.

장점:

```text
연속적이고 부드럽다.
로봇 제어에 유리하다.
```

단점:

```text
바퀴 미끄러짐, 회전 오차 때문에 시간이 지날수록 틀어진다.
```

`map_robot_ns`는 지도 기준 전역 좌표계다.

장점:

```text
벽, 코너, loop closure를 이용해 전역 오차를 보정할 수 있다.
```

단점:

```text
보정이 들어가면 위치가 순간적으로 조정될 수 있다.
```

그래서 둘을 분리한다.

```text
map_robot_ns -> odom_robot_ns -> base_footprint
```

---

## 3. 발행 주체

Day 11 SLAM:

```text
Gazebo diff_drive plugin
  odom_robot_ns -> base_footprint

SLAM Toolbox
  map_robot_ns -> odom_robot_ns
```

Day 12 AMCL:

```text
Gazebo diff_drive plugin
  odom_robot_ns -> base_footprint

AMCL
  map_robot_ns -> odom_robot_ns
```

따라서 SLAM과 AMCL을 동시에 켜면 같은 transform을 서로 발행할 수 있다.

---

## 4. base_link와 base_footprint

`base_footprint`는 보통 로봇 바닥 기준의 2D 주행 중심이다.  
`base_link`는 로봇 몸체 기준 frame이다.

2D navigation에서는 `base_footprint`를 base frame으로 쓰는 경우가 많다.  
현재 SLAM 설정도 다음과 같다.

```yaml
base_frame: base_footprint
```

---

## 5. base_scan

LiDAR frame은 현재 `base_scan`이다.

```text
base_footprint
  -> base_link
    -> base_scan
```

`/robot_ns/scan.header.frame_id`가 `base_scan`이면, SLAM Toolbox는 TF를 통해 이 scan을 로봇 기준과 map 기준으로 변환할 수 있다.
