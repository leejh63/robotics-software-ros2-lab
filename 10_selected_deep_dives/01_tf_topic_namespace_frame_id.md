# 01. TF / Topic / Namespace / Frame ID 심화 정리

ROS2 Navigation에서 가장 많이 헷갈리는 부분은 `topic 이름`, `namespace`, `frame_id`, `TF frame`이 서로 비슷해 보이지만 실제로는 완전히 다른 층위의 개념이라는 점이다.

이 문서는 Day 06~13 전체를 관통하는 좌표계/이름 문제를 정리한다.

---

## 1. 먼저 결론

```text
topic 이름
  -> ROS graph에서 메시지가 지나가는 통신 채널 이름

namespace
  -> topic/node/service/action 이름 앞에 붙는 이름 공간

frame_id
  -> 메시지 안에 들어 있는 좌표계 이름

TF frame
  -> 로봇 좌표계 그래프에 등장하는 좌표계 노드 이름

TF topic
  -> TF 변환 메시지가 흘러가는 topic 이름
```

즉, `/robot_ns/scan`과 `base_scan`은 같은 종류의 이름이 아니다.

```text
/robot_ns/scan
  -> LaserScan 메시지가 발행되는 topic 이름

base_scan
  -> LaserScan 데이터가 어느 센서 좌표계 기준인지 나타내는 frame_id
```

---

## 2. 예시 환경 기준 예시

현재 네 환경에서 중요한 이름들은 아래처럼 나뉜다.

| 구분 | 이름 | 의미 |
|---|---|---|
| namespace | `/robot_ns` | 로봇 관련 topic/action을 묶기 위한 이름 공간 |
| scan topic | `/robot_ns/scan` | LiDAR 거리 배열이 publish되는 topic |
| odom topic | `/robot_ns/odom` | wheel odometry가 publish되는 topic |
| cmd_vel topic | `/robot_ns/cmd_vel` | 로봇 속도 명령을 받는 topic |
| TF topic | `/robot_ns/tf`, `/robot_ns/tf_static` | 좌표 변환 메시지가 흐르는 topic |
| map frame | `map_robot_ns` | 전역 지도 좌표계 |
| odom frame | `odom_robot_ns` | 오도메트리 누적 좌표계 |
| base frame | `base_footprint` | 로봇 기준 좌표계 |
| scan frame | `base_scan` | LiDAR 센서 기준 좌표계 |

중요한 점은 `/robot_ns`가 붙는 것은 주로 **ROS graph 이름**이고, `map_robot_ns`, `odom_robot_ns`, `base_scan`은 **좌표계 이름**이라는 점이다.

---

## 3. Topic 이름은 통신 채널이다

예를 들어 Gazebo LiDAR plugin이 LaserScan을 publish한다고 하자.

```text
publisher: Gazebo ray sensor plugin
message: sensor_msgs/msg/LaserScan
topic: /robot_ns/scan
```

이때 `/robot_ns/scan`은 메시지가 지나가는 통로 이름이다.

확인 명령:

```bash
ros2 topic list | grep scan
ros2 topic info /robot_ns/scan
ros2 topic echo /robot_ns/scan --once
```

`ros2 topic echo /robot_ns/scan --once`를 보면 메시지 안에 이런 필드가 있다.

```text
header:
  frame_id: base_scan
angle_min: ...
angle_increment: ...
ranges: [...]
```

여기서 topic 이름은 `/robot_ns/scan`이지만, 메시지 내부 좌표계는 `base_scan`이다.

---

## 4. frame_id는 메시지 데이터의 기준 좌표계다

센서 데이터는 반드시 “어느 좌표계 기준으로 측정된 값인지”가 필요하다.

LiDAR 예시:

```text
ranges[0] = 센서 기준 angle_min 방향으로 측정한 거리
ranges[1] = 센서 기준 angle_min + angle_increment 방향으로 측정한 거리
...
```

그러면 이 `센서 기준`이 무엇인지 알려주는 이름이 `header.frame_id`다.

```text
header.frame_id = base_scan
```

즉, `base_scan`은 “LiDAR 센서 좌표계”다.

SLAM Toolbox나 AMCL은 이걸 보고 생각한다.

```text
이 LaserScan은 base_scan 기준 데이터구나.
그럼 base_scan이 base_footprint와 어떤 관계인지 TF에서 찾아야겠다.
base_footprint가 odom_robot_ns와 어떤 관계인지도 TF에서 찾아야겠다.
그러면 이 scan이 map_robot_ns 위에서 어디에 해당하는지 계산할 수 있겠다.
```

---

## 5. TF topic과 TF frame은 다르다

이것도 많이 헷갈리는 부분이다.

```text
/robot_ns/tf
  -> 좌표 변환 메시지가 흐르는 topic 이름

map_robot_ns, odom_robot_ns, base_footprint, base_scan
  -> TF tree에 등장하는 frame 이름
```

즉, `/robot_ns/tf`는 통로이고, `map_robot_ns -> odom_robot_ns -> base_footprint -> base_scan`은 그 통로 안에 담기는 좌표 관계다.

확인 명령:

```bash
ros2 topic echo /robot_ns/tf --once
```

대략 이런 구조가 나온다.

```text
transforms:
- header:
    frame_id: odom_robot_ns
  child_frame_id: base_footprint
  transform:
    translation: ...
    rotation: ...
```

이 말은:

```text
odom_robot_ns 좌표계에서 봤을 때 base_footprint가 어디에 있는지
```

를 뜻한다.

---

## 6. Namespace는 topic/node/action 이름에 주로 적용된다

`/robot_ns` namespace는 여러 로봇이 있거나, 실습 중 다른 사람의 topic과 충돌하지 않도록 이름을 묶기 위해 사용한다.

예를 들어 namespace가 없으면:

```text
/scan
/odom
/cmd_vel
/map
/navigate_to_pose
```

namespace를 적용하면:

```text
/robot_ns/scan
/robot_ns/odom
/robot_ns/cmd_vel
/robot_ns/map
/robot_ns/navigate_to_pose
```

하지만 namespace가 붙었다고 해서 `frame_id`가 자동으로 바뀌지는 않는다.

예를 들어 아래처럼 topic remap을 해도:

```bash
ros2 bag play some_bag --remap /scan:=/robot_ns/scan
```

메시지 내부의 `header.frame_id`가 자동으로 `base_scan`이나 `robot_ns/base_scan`으로 바뀌는 것은 아니다.

```text
바뀌는 것: topic 이름
자동으로 안 바뀌는 것: header.frame_id, child_frame_id
```

이 점 때문에 rosbag replay에서 topic은 맞는데 TF가 안 맞는 문제가 자주 생긴다.

---

## 7. 왜 topic remap만으로 부족할 수 있는가

예를 들어 오래된 bag 안에 이런 데이터가 있다고 하자.

```text
topic: /scan
header.frame_id: laser
```

현재 시스템은 이런 구조를 기대한다.

```text
topic: /robot_ns/scan
header.frame_id: base_scan
TF tree: odom_robot_ns -> base_footprint -> base_scan
```

이때 단순히:

```bash
--remap /scan:=/robot_ns/scan
```

만 하면 topic 이름은 맞지만 메시지 내부는 여전히:

```text
header.frame_id: laser
```

일 수 있다.

그러면 SLAM/AMCL은 TF에서 `laser` frame을 찾으려고 한다. 그런데 현재 TF tree에 `laser`가 없으면 아래와 같은 문제가 생긴다.

```text
Could not transform laser to odom_robot_ns
Lookup would require extrapolation
Frame laser does not exist
```

즉, topic 이름이 맞는 것과 TF frame이 맞는 것은 별개다.

---

## 8. 예시 환경에서 확인해야 할 최소 명령

### topic 이름 확인

```bash
ros2 topic list | sort | grep '^/robot_ns'
```

기대:

```text
/robot_ns/scan
/robot_ns/odom
/robot_ns/cmd_vel
/robot_ns/map
/robot_ns/tf
/robot_ns/tf_static
```

### LaserScan frame_id 확인

```bash
ros2 topic echo /robot_ns/scan --once | grep frame_id
```

기대:

```text
frame_id: base_scan
```

### Odometry frame 확인

```bash
ros2 topic echo /robot_ns/odom --once | grep -E 'frame_id|child_frame_id'
```

기대:

```text
frame_id: odom_robot_ns
child_frame_id: base_footprint
```

### TF 연결 확인

```bash
ros2 run tf2_ros tf2_echo odom_robot_ns base_footprint
ros2 run tf2_ros tf2_echo base_footprint base_scan
```

AMCL 또는 SLAM 실행 후:

```bash
ros2 run tf2_ros tf2_echo map_robot_ns odom_robot_ns
```

---

## 9. RViz에서 자주 터지는 이유

RViz에는 `Fixed Frame`이 있다.

만약 Fixed Frame을 `map`으로 두었는데 실제 frame이 `map_robot_ns`라면 RViz가 데이터를 제대로 표시하지 못할 수 있다.

예시 환경에서는 보통 아래 기준이 맞다.

```text
Fixed Frame: map_robot_ns
LaserScan topic: /robot_ns/scan
Map topic: /robot_ns/map
TF topic remap: /tf -> /robot_ns/tf, /tf_static -> /robot_ns/tf_static
```

다만 RViz는 기본적으로 `/tf`, `/tf_static`을 보는 경우가 많아서, launch 파일에서 remapping을 넣었는지 확인해야 한다.

---

## 10. 핵심 요약

```text
/robot_ns/scan은 topic 이름이다.
base_scan은 LaserScan 데이터의 기준 좌표계다.
/robot_ns/tf는 TF 메시지가 지나가는 topic이다.
map_robot_ns, odom_robot_ns, base_footprint는 TF tree의 frame 이름이다.
namespace는 topic/node/action 이름에 붙는 것이지, frame_id를 자동 변경하지 않는다.
topic remap은 frame_id를 바꾸지 않는다.
SLAM/AMCL/Nav2 문제의 상당수는 topic 이름은 맞는데 frame_id/TF가 안 맞아서 생긴다.
```

---

## 11. 이 문서와 연결되는 기존 문서

```text
day_06_09_ros2_foundation/background/ros2_name_resolution_and_namespace.md
day_10_gazebo_urdf/background/tf_frame_topic_namespace.md
day_11_slam/background/map_odom_base_frame_relationship.md
appendix/topic_frame_message_action_master_table.md
appendix/environment_reference.md
```
