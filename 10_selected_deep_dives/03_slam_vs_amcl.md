# 03. SLAM과 AMCL의 차이 심화 정리

SLAM과 AMCL은 둘 다 `map`, `scan`, `odom`, `TF`와 관련되어 있어서 처음 보면 비슷해 보인다. 하지만 목적이 다르다.

```text
SLAM
  -> 지도가 없거나 불완전할 때, 로봇 위치를 추정하면서 지도를 만든다.

AMCL
  -> 이미 만들어진 지도 위에서, 현재 로봇 위치만 추정한다.
```

이 차이를 정확히 잡아야 Day 11, Day 12, Day 13 흐름이 꼬이지 않는다.

---

## 1. 한 줄 결론

```text
SLAM은 map을 만든다.
AMCL은 저장된 map 위에서 pose를 찾는다.
```

더 정확히 말하면:

```text
SLAM = Localization + Mapping
AMCL = Localization only
```

SLAM은 “내가 어디 있는지”와 “주변 지도가 어떻게 생겼는지”를 동시에 추정한다.

AMCL은 “지도는 이미 있으니, 그 지도 위에서 내가 어디 있는지”만 추정한다.

---

## 2. Day 흐름으로 보면

```text
Day 10 Gazebo/URDF
  -> 로봇, LiDAR, odom, TF를 만든다.

Day 11 SLAM
  -> /robot_ns/scan + TF를 이용해 /robot_ns/map을 만든다.
  -> slam_map.yaml, slam_map.pgm을 저장한다.

Day 12 AMCL
  -> 저장된 slam_map.yaml을 map_server로 불러온다.
  -> /robot_ns/scan과 particle filter로 현재 pose를 추정한다.

Day 13 Nav2
  -> AMCL이 추정한 pose와 map/costmap을 이용해 goal까지 이동한다.
```

즉, SLAM과 AMCL은 같은 시점에 같은 역할로 쓰는 것이 아니라 보통 단계가 다르다.

---

## 3. SLAM 실행 시 데이터 흐름

SLAM 단계:

```text
Gazebo robot
  -> /robot_ns/scan
  -> /robot_ns/odom
  -> /robot_ns/tf

slam_toolbox
  subscribe: /robot_ns/scan, /robot_ns/tf
  output: /robot_ns/map
  output TF: map_robot_ns -> odom_robot_ns
```

SLAM은 scan을 누적해서 map을 만든다. 이때 로봇의 위치도 추정해야 하므로 `map_robot_ns -> odom_robot_ns` TF를 발행한다.

SLAM 결과 저장:

```text
slam_map.yaml
slam_map.pgm
possibly posegraph file
```

---

## 4. AMCL 실행 시 데이터 흐름

AMCL 단계:

```text
map_server
  load: slam_map.yaml
  publish: /robot_ns/map

Gazebo robot
  publish: /robot_ns/scan
  publish: /robot_ns/odom
  publish: /robot_ns/tf

amcl
  subscribe: /robot_ns/map
  subscribe: /robot_ns/scan
  use TF: odom_robot_ns, base_footprint, base_scan
  output: /amcl_pose 또는 namespace 적용된 pose topic
  output: /particle_cloud
  output TF: map_robot_ns -> odom_robot_ns
```

AMCL은 map을 새로 만들지 않는다. 저장된 map을 기준으로 현재 scan이 어디서 관측됐을 때 가장 잘 맞는지 찾는다.

---

## 5. 왜 SLAM과 AMCL을 동시에 켜면 안 될 수 있는가

SLAM과 AMCL은 둘 다 `map_robot_ns -> odom_robot_ns` TF를 발행할 수 있다.

```text
SLAM Toolbox
  -> map_robot_ns -> odom_robot_ns 발행 가능

AMCL
  -> map_robot_ns -> odom_robot_ns 발행 가능
```

둘을 동시에 켜면 같은 parent/child 관계를 두 노드가 서로 다른 값으로 publish할 수 있다.

그러면 TF tree가 불안정해지고 RViz/Nav2가 이상하게 동작할 수 있다.

그래서 보통은:

```text
지도 만들 때:
  slam_toolbox 사용
  AMCL 사용 X

저장된 지도에서 주행할 때:
  map_server + AMCL 사용
  SLAM Toolbox 사용 X
```

---

## 6. map->odom TF의 의미

ROS Navigation 계열에서 자주 쓰는 좌표 구조:

```text
map -> odom -> base_link/base_footprint -> sensor
```

각 frame의 의미:

```text
map
  -> 전역 지도 좌표계. 장기적으로 안정적이어야 한다.

odom
  -> 오도메트리 좌표계. 단기적으로 부드럽지만 장기적으로 drift가 생긴다.

base_footprint/base_link
  -> 로봇 본체 좌표계.
```

`odom -> base_footprint`는 보통 wheel odometry나 Gazebo diff_drive가 발행한다.

`map -> odom`은 SLAM 또는 AMCL 같은 localization 계층이 발행한다.

왜 이렇게 나누는가?

```text
odom -> base는 부드럽게 움직여야 한다.
map -> odom은 누적 오차를 보정하는 역할을 한다.
```

AMCL이 로봇 위치를 “아, 실제 지도 기준으로는 odom 추정보다 조금 왼쪽이네”라고 판단하면, `map -> odom` 관계를 조정해서 전체 위치를 보정한다.

---

## 7. AMCL에서 particle이 하는 역할

AMCL은 하나의 pose만 믿지 않는다. 여러 개의 pose 후보를 뿌린다.

```text
particle = 로봇이 있을 법한 pose 후보
pose = x, y, yaw
```

각 particle은 이렇게 평가된다.

```text
이 particle 위치에서 LiDAR를 쐈다고 가정하면
현재 실제 /robot_ns/scan과 얼마나 잘 맞는가?
```

잘 맞는 particle의 weight는 커지고, 안 맞는 particle은 사라진다. 반복하면 particle들이 실제 위치 근처로 모인다.

---

## 8. SLAM의 scan matching과 AMCL의 sensor update는 비슷하지만 목적이 다르다

둘 다 scan을 사용한다.

하지만 목적은 다르다.

### SLAM

```text
현재 scan을 기존 map/pose graph에 어떻게 붙일까?
지도 자체도 계속 업데이트한다.
```

### AMCL

```text
이미 있는 map에서 현재 scan이 가장 잘 맞는 pose는 어디일까?
지도는 업데이트하지 않는다.
```

즉:

```text
SLAM: map을 만든다.
AMCL: map을 믿고 pose를 찾는다.
```

---

## 9. 예시 환경에서 구분하는 실행 방식

### SLAM 실행

```bash
cd $ROS2_WS
source install/setup.bash
ros2 launch lee_robot_description slam.launch.py
```

이때 핵심 확인:

```bash
ros2 topic echo /robot_ns/map --once
ros2 run tf2_ros tf2_echo map_robot_ns odom_robot_ns
```

### AMCL 실행

```bash
cd $ROS2_WS
source install/setup.bash
ros2 launch lee_robot_description nav2.launch.py
```

이 launch는 localization 쪽을 담당한다.

```text
Gazebo
robot_state_publisher
spawn_entity
map_server
amcl
lifecycle_manager_localization
RViz
```

AMCL 확인:

```bash
ros2 topic list | grep -E 'amcl|particle|map|scan'
ros2 run tf2_ros tf2_echo map_robot_ns odom_robot_ns
```

---

## 10. 흔한 오해

### 오해 1. AMCL도 map을 만든다

아니다. AMCL은 map을 새로 만들지 않는다.

AMCL은 map_server가 publish하는 `/robot_ns/map`을 사용해서 현재 위치를 찾는다.

### 오해 2. SLAM이 끝났으면 AMCL이 필요 없다

아니다. SLAM으로 만든 map을 저장한 뒤, 다음에 로봇을 다시 켜면 현재 위치를 다시 찾아야 한다. 이때 AMCL이 필요하다.

### 오해 3. map topic이 보이면 localization도 되는 것이다

아니다. map은 단지 지도 데이터다. localization이 되려면 AMCL pose, particle cloud, map->odom TF가 정상이어야 한다.

### 오해 4. map->odom TF는 Gazebo가 발행한다

보통 Gazebo diff_drive는 `odom -> base_footprint`를 담당한다. `map -> odom`은 SLAM 또는 AMCL이 담당한다.

---

## 11. 핵심 요약

```text
SLAM은 지도 생성 + 위치 추정이다.
AMCL은 저장된 지도 위에서 위치 추정만 한다.
SLAM과 AMCL은 둘 다 map->odom TF를 발행할 수 있으므로 동시에 켜면 충돌할 수 있다.
Gazebo/diff_drive는 보통 odom->base를 담당한다.
SLAM 또는 AMCL은 map->odom을 담당한다.
Nav2 주행은 보통 map_server + AMCL이 준비된 뒤 시작한다.
```

---

## 12. 이 문서와 연결되는 기존 문서

```text
day_11_slam/README.md
day_11_slam/background/map_odom_base_frame_relationship.md
day_12_amcl_mcl/README.md
day_12_amcl_mcl/background/lifecycle_map_server_amcl.md
appendix/day11_to_day12_amcl_connection.md
appendix/validation_sequence_gazebo_slam_amcl_nav2.md
```
