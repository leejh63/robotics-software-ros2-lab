# Background - ROS2 이름 해석과 Namespace 최소 배경지식

## 1. 왜 이름이 어려운가

ROS2에서는 이름이 여러 층으로 존재한다.

```text
package name
executable name
node name
topic name
service name
action name
parameter name
frame name
namespace
```

이름이 비슷해 보여도 역할이 다르다. 실습 초반의 많은 오류는 이름을 잘못 찾는 데서 나온다.

---

## 2. 절대 이름과 상대 이름

ROS2 이름에는 `/`로 시작하는 절대 이름과, `/` 없이 쓰는 상대 이름이 있다.

```text
/image_raw  -> 절대 topic 이름
image_raw   -> 현재 namespace 아래에서 해석되는 상대 이름
```

namespace가 없으면 둘이 거의 비슷하게 보일 수 있다. 하지만 namespace가 붙으면 차이가 커진다.

```text
namespace=/robot_ns
relative name image_raw -> /robot_ns/image_raw
absolute name /image_raw -> /image_raw
```

---

## 3. 이번 코드에서 볼 수 있는 예

`ros2_topic_examples/string_talker.py`는 기본 topic을 `chatter`로 만든다.

```python
self.create_publisher(String, topic_name, 10)
```

`topic_name`의 기본값은 `chatter`이므로 namespace 없이 실행하면 `/chatter`처럼 보인다. namespace를 붙여 실행하면 상대 이름 규칙에 따라 `/some_namespace/chatter`가 될 수 있다.

`turtle_square.py`는 `cmd_vel_topic` parameter를 통해 발행 topic을 고를 수 있게 했다. 기본값은 `/turtle1/cmd_vel`이다.

```python
self.declare_parameter('cmd_vel_topic', '/turtle1/cmd_vel')
```

절대 이름을 쓰면 namespace가 자동으로 붙지 않는다. namespace 실습이 필요하면 `cmd_vel_topic`을 상대 이름으로 바꿔 실행하면서 차이를 확인할 수 있다.

---

## 4. frame name은 topic namespace와 별개다

`camera_link` 같은 frame 이름은 topic namespace와 자동으로 같이 바뀌지 않는다.

```text
/image_raw topic에 namespace를 붙여 /robot1/image_raw로 만들었다고 해서
header.frame_id가 자동으로 robot1/camera_link가 되는 것은 아니다.
```

frame 이름은 코드나 parameter에서 별도로 맞춰야 한다.

---

## 5. Day 10~13에서 왜 중요해지는가

Nav2에서 `/navigate_to_pose`와 `/robot_ns/navigate_to_pose`는 다르다. RViz가 goal을 `/navigate_to_pose`로 보내는데 Nav2가 `/robot_ns/navigate_to_pose`를 기다리면 연결되지 않는다.

SLAM/AMCL에서도 `/scan`과 `/robot_ns/scan`은 다르다. parameter가 `scan_topic: scan`인지 `/scan`인지 `/robot_ns/scan`인지에 따라 실제 연결이 달라진다.

---

## 6. 확인 습관

이름이 헷갈릴 때는 추측하지 말고 실제 graph를 확인한다.

```bash
ros2 node list
ros2 topic list
ros2 service list
ros2 action list
ros2 node info /node_name
ros2 topic info /topic_name
```

특히 namespace가 들어간 시스템에서는 list 결과에 실제로 어떤 이름이 생성되었는지 먼저 봐야 한다.
