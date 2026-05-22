# Initial Pose CLI Examples

RViz `2D Pose Estimate` 대신 CLI로 `/initialpose`를 발행하는 예시다.

주의: launch namespace 설정에 따라 topic 이름이 `/initialpose`가 아니라 `/robot_ns/initialpose`일 수 있다. 먼저 `ros2 topic list | grep initialpose`로 실제 이름을 확인한다.

---

## 1. 메시지 타입

```text
geometry_msgs/msg/PoseWithCovarianceStamped
```

핵심 필드:

```text
header.frame_id: map_robot_ns
pose.pose.position.x
pose.pose.position.y
pose.pose.orientation
pose.covariance
```

---

## 2. yaw = 0 근처 예시

```bash
ros2 topic pub --once /initialpose geometry_msgs/msg/PoseWithCovarianceStamped "
header:
  frame_id: 'map_robot_ns'
pose:
  pose:
    position:
      x: 0.0
      y: 0.0
      z: 0.0
    orientation:
      x: 0.0
      y: 0.0
      z: 0.0
      w: 1.0
  covariance:
  - 0.25
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.25
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0
  - 0.0685
"
```

---

## 3. orientation z/w 계산

2D yaw를 quaternion으로 바꿀 때는 아래 관계를 쓴다.

```text
z = sin(yaw / 2)
w = cos(yaw / 2)
```

예:

```text
yaw = 0 rad
  z = 0
  w = 1

yaw = 1.5708 rad
  z = 0.7071
  w = 0.7071

yaw = 3.1416 rad
  z = 1.0
  w = 0.0
```

---

## 4. covariance를 어떻게 볼 것인가

처음에는 엄밀하게 계산하기보다 직관적으로 본다.

```text
x/y covariance가 작음
  위치를 꽤 확신한다.
  particle이 좁게 퍼질 수 있다.

x/y covariance가 큼
  위치를 대략만 안다.
  particle이 넓게 퍼질 수 있다.

yaw covariance가 작음
  방향을 꽤 확신한다.

yaw covariance가 큼
  방향도 불확실하다.
```

학습할 때는 RViz 2D Pose Estimate가 더 편하다. CLI 발행은 자동화 테스트나 RViz가 불편할 때 사용한다.
