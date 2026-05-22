# Background - QoS, Callback, Executor, Lifecycle 최소 배경지식

이 문서는 Day 06~09를 이해하는 데 필요한 추가 배경지식만 간단히 정리한다.

---

## 1. QoS란 무엇인가

QoS는 Quality of Service의 약자다. ROS2 topic 통신에서 메시지를 얼마나 보관할지, 신뢰성 있게 보낼지, 늦게 들어온 subscriber에게 이전 메시지를 줄지 등을 정하는 정책이다.

이번 코드에서는 대부분 간단히 `10`을 넘긴다.

```python
self.create_publisher(Image, 'image_raw0', 10)
self.create_subscription(Image, 'image_raw0', self.image_callback, 10)
```

여기서 `10`은 queue depth로 보면 된다. subscriber가 잠깐 처리하지 못해도 최근 메시지를 몇 개까지 쌓아둘지에 대한 값이다.

Day 10~13에서는 QoS가 더 중요해진다. 예를 들어 sensor data는 BEST_EFFORT QoS를 쓰는 경우가 있고, RViz subscriber QoS와 맞지 않으면 topic이 있는데도 안 보일 수 있다.

---

## 2. Callback이란 무엇인가

Callback은 어떤 이벤트가 왔을 때 ROS2가 대신 호출해주는 함수다.

예시:

| 이벤트 | callback |
|---|---|
| timer 주기가 됨 | `timer_callback()` |
| topic 메시지 수신 | `image_callback(msg)` |
| service 요청 수신 | `add_callback(request, response)` |
| action goal 실행 | `execute_callback(goal_handle)` |
| parameter 변경 요청 | `parameter_callback(params)` |

ROS2 node 코드는 대부분 callback 중심으로 움직인다.

---

## 3. rclpy.spin()의 의미

`rclpy.spin(node)`는 node가 callback을 계속 처리하게 만드는 루프다.

```python
rclpy.init()
node = Talker()
rclpy.spin(node)
```

`spin()`이 없으면 timer callback이나 subscriber callback이 계속 실행되지 않는다.

---

## 4. Executor란 무엇인가

Executor는 callback을 실제로 실행하는 주체다. `rclpy.spin(node)`를 쓰면 기본 executor가 node의 callback들을 처리한다.

초반에는 executor를 깊게 몰라도 되지만, 나중에 여러 callback이 동시에 실행되어야 하거나 action/server/service가 복잡해지면 SingleThreadedExecutor, MultiThreadedExecutor 개념이 중요해진다.

이번 실습에서는 대부분 단일 node, 단순 callback 구조라 기본 spin으로 충분하다.

---

## 5. Lifecycle Node란 무엇인가

Lifecycle node는 상태를 가진 node다.

일반 node는 실행되면 바로 동작하는 경우가 많다. 하지만 Nav2의 많은 node는 아래 상태 전환을 거친다.

```text
unconfigured -> inactive -> active -> finalized
```

그래서 Nav2에서는 node가 떠 있는 것과 실제로 active 상태인 것이 다르다.

Day 06~09의 service 개념이 여기서 다시 등장한다. lifecycle 전환은 service 호출로 이루어진다.

---

## 6. 지금 단계에서 기억할 정도

```text
QoS      : topic 메시지 전달 정책
Callback : 이벤트가 발생했을 때 실행되는 함수
spin     : callback 처리를 계속 돌리는 루프
Executor : callback 실행을 관리하는 주체
Lifecycle: node에 상태 전환 개념을 추가한 구조
```

Day 06~09에서는 용어만 잡고, Day 13 Nav2에서 lifecycle을 더 구체적으로 보면 된다.
