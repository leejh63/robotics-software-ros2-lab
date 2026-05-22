# AMCL Namespace Case 정리

AMCL 관련 topic은 launch 구조에 따라 root namespace에 있을 수도 있고, robot namespace 아래에 있을 수도 있다. 이 문서에서는 `/amcl_pose`, `/particle_cloud`, `/initialpose`를 확인할 때 어떤 경우를 먼저 의심해야 하는지 정리한다.

---

## 1. 핵심 결론

AMCL topic 이름은 고정해서 외우면 안 된다. 먼저 실제 ROS graph를 확인해야 한다.

```bash
ros2 node list | sort | grep -E 'amcl|map_server|localization'
ros2 topic list | sort | grep -E 'amcl_pose|particle_cloud|initialpose|map|scan|tf'
```

가능한 형태는 크게 두 가지다.

| Case | AMCL node 예시 | AMCL 입출력 topic 예시 | 해석 |
|---|---|---|---|
| A. root AMCL | `/amcl` | `/amcl_pose`, `/particle_cloud`, `/initialpose` | AMCL node가 root namespace에서 실행되는 구조 |
| B. namespaced AMCL | `/robot_ns/amcl` | `/robot_ns/amcl_pose`, `/robot_ns/particle_cloud`, `/robot_ns/initialpose` | AMCL node가 robot namespace 안에서 실행되는 구조 |

이 저장소의 문서에서는 설명 편의를 위해 root AMCL case와 namespaced sensor topic이 섞여 등장할 수 있다. 따라서 실행 전에 반드시 `ros2 topic list`와 `ros2 node info`로 현재 graph를 기준으로 확인한다.

---

## 2. Case A - AMCL node가 root namespace에 있는 경우

예시 node:

```text
/amcl
/map_server
/lifecycle_manager_localization
```

예시 topic:

```text
/robot_ns/map
/robot_ns/scan
/initialpose
/amcl_pose
/particle_cloud
/robot_ns/tf
/robot_ns/tf_static
```

이 경우 AMCL은 root namespace의 node로 떠 있지만, 입력 sensor topic이나 TF topic은 launch/remap으로 `/robot_ns/...`를 구독할 수 있다.

확인 명령:

```bash
ros2 node info /amcl
ros2 topic echo /initialpose --once
ros2 topic echo /amcl_pose --once
ros2 topic echo /particle_cloud --once
```

`ros2 node info /amcl`에서 아래처럼 보이면 root AMCL case로 보면 된다.

```text
Subscribers:
  /robot_ns/map
  /robot_ns/scan
  /initialpose
  /robot_ns/tf
  /robot_ns/tf_static

Publishers:
  /amcl_pose
  /particle_cloud
  /robot_ns/tf
```

---

## 3. Case B - AMCL node가 robot namespace 아래에 있는 경우

예시 node:

```text
/robot_ns/amcl
/robot_ns/map_server
/robot_ns/lifecycle_manager_localization
```

예시 topic:

```text
/robot_ns/map
/robot_ns/scan
/robot_ns/initialpose
/robot_ns/amcl_pose
/robot_ns/particle_cloud
/robot_ns/tf
/robot_ns/tf_static
```

이 경우 RViz `2D Pose Estimate` 또는 CLI initialpose 발행도 `/robot_ns/initialpose`를 향해야 한다.

확인 명령:

```bash
ros2 node info /robot_ns/amcl
ros2 topic echo /robot_ns/initialpose --once
ros2 topic echo /robot_ns/amcl_pose --once
ros2 topic echo /robot_ns/particle_cloud --once
```

---

## 4. RViz initialpose에서 자주 생기는 문제

RViz의 `2D Pose Estimate`는 설정된 topic으로 `geometry_msgs/msg/PoseWithCovarianceStamped`를 발행한다. AMCL이 실제로 구독하는 topic과 RViz가 발행하는 topic이 다르면 initialpose를 찍어도 AMCL이 반응하지 않는다.

확인 순서:

```bash
ros2 node info /amcl | grep initialpose -A 2
ros2 node info /robot_ns/amcl | grep initialpose -A 2
ros2 topic list | grep initialpose
```

root AMCL이면 보통:

```text
/initialpose
```

namespaced AMCL이면 보통:

```text
/robot_ns/initialpose
```

실제 topic 이름을 확인한 뒤 RViz 또는 CLI 발행 대상을 맞춘다.

---

## 5. CLI initialpose 발행 예시

### root AMCL case

```bash
ros2 topic pub --once /initialpose geometry_msgs/msg/PoseWithCovarianceStamped "
header:
  frame_id: 'map_robot_ns'
pose:
  pose:
    position: {x: 0.0, y: 0.0, z: 0.0}
    orientation: {z: 0.0, w: 1.0}
  covariance: [0.25, 0.0, 0.0, 0.0, 0.0, 0.0,
               0.0, 0.25, 0.0, 0.0, 0.0, 0.0,
               0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
               0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
               0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
               0.0, 0.0, 0.0, 0.0, 0.0, 0.068]
"
```

### namespaced AMCL case

```bash
ros2 topic pub --once /robot_ns/initialpose geometry_msgs/msg/PoseWithCovarianceStamped "
header:
  frame_id: 'map_robot_ns'
pose:
  pose:
    position: {x: 0.0, y: 0.0, z: 0.0}
    orientation: {z: 0.0, w: 1.0}
  covariance: [0.25, 0.0, 0.0, 0.0, 0.0, 0.0,
               0.0, 0.25, 0.0, 0.0, 0.0, 0.0,
               0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
               0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
               0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
               0.0, 0.0, 0.0, 0.0, 0.0, 0.068]
"
```

중요한 점은 topic 이름이 다르더라도 `header.frame_id`는 map frame인 `map_robot_ns`를 기준으로 둔다는 것이다.

---

## 6. 헷갈리면 이 순서로 본다

```text
1. AMCL node 이름 확인
2. AMCL node info에서 실제 subscriber/publisher 확인
3. initialpose topic 이름 확인
4. amcl_pose / particle_cloud topic 이름 확인
5. TF topic remap 확인
6. map_robot_ns -> odom_robot_ns TF 확인
```

명령어:

```bash
ros2 node list | sort | grep amcl
ros2 topic list | sort | grep -E 'initialpose|amcl_pose|particle_cloud'
ros2 node info /amcl
ros2 node info /robot_ns/amcl
```

마지막 두 명령 중 실제 존재하는 node에 대해서만 성공한다. 실패하는 쪽은 현재 graph에 없는 case다.
