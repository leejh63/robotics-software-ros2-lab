# 03. Pub/Sub, Service, Action, Interface 구분

## 한 줄 결론

ROS2 통신 방식은 데이터 성격에 따라 골라야 한다.

```text
계속 흐르는 데이터        -> Topic
짧은 요청과 즉시 응답      -> Service
오래 걸리는 목표와 피드백  -> Action
데이터 구조 자체를 정의    -> Interface(msg/srv/action)
```

---

## 1. Topic - 계속 흘러가는 데이터

Topic은 센서값, 상태값, 명령처럼 계속 갱신되는 데이터를 흘려보내는 구조다.

이번 코드의 topic 예시:

| publisher | topic | type | subscriber |
|---|---|---|---|
| `ros2_topic_examples/string_talker.py` | `chatter` | `std_msgs/msg/String` | `ros2_topic_examples/string_listener.py` |
| `ros2_cpp_examples/cpp_talker.cpp` | `cpp_chatter` | `std_msgs/msg/String` | `ros2_cpp_examples/cpp_listener.cpp` |
| `ros2_topic_examples/turtle_square.py` | `/turtle1/cmd_vel` | `geometry_msgs/msg/Twist` | turtlesim node |
| `ros2_camera_examples/image_publisher.py` | `/image_raw` | `sensor_msgs/msg/Image` | OpenCV/YOLO 관련 노드 |
| `ros2_camera_examples/image_edge_publisher.py` | `/image_edge` | `sensor_msgs/msg/Image` | viewer/snapshot node |
| `ros2_camera_examples/yolo_image_publisher.py` | `/image_yolo` | `sensor_msgs/msg/Image` | viewer/snapshot node |
| `ros2_camera_examples/yolo_detection_publisher.py` | `/yolo_detections` | `ros2_foundation_interfaces/msg/ObjectDetectionArray` | `ros2_tf_examples/yolo_tf_broadcaster.py` |

Topic이 적합한 경우:

```text
- 카메라 이미지처럼 계속 들어오는 데이터
- 라이다/IMU/odom처럼 최신 상태가 계속 갱신되는 데이터
- /cmd_vel처럼 주기적으로 갱신되는 명령
- 여러 노드가 동시에 받아도 되는 데이터
```

---

## 2. Publisher/Subscriber 코드 구조

### Python publisher

`ros2_topic_examples/string_talker.py`의 구조:

```python
self.publisher_ = self.create_publisher(String, 'chatter', 10)
self.timer = self.create_timer(0.5, self.timer_callback)
```

핵심은 아래다.

```text
메시지 타입: String
topic 이름 : chatter
큐 크기    : 10
주기       : 0.5초마다 timer_callback 실행
```

### Python subscriber

`ros2_topic_examples/string_listener.py`의 구조:

```python
self.subscription = self.create_subscription(
    String, 'chatter', self.listener_callback, 10)
```

메시지가 들어오면 `listener_callback()`이 실행된다.

### C++도 구조는 같다

`ros2_cpp_examples/cpp_talker.cpp`:

```cpp
publisher_ = this->create_publisher<std_msgs::msg::String>("cpp_chatter", 10);
```

`ros2_cpp_examples/cpp_listener.cpp`:

```cpp
subscription_ = this->create_subscription<std_msgs::msg::String>(
    "cpp_chatter", 10,
    std::bind(&Listener::listener_callback, this, std::placeholders::_1));
```

Python과 C++ 문법은 다르지만 ROS graph 관점은 같다.

---

## 3. Service - 한 번 요청하고 한 번 응답

Service는 request/response 구조다.

이번 코드의 service:

| server | client | service name | type |
|---|---|---|---|
| `add_server.py` | `add_client.py` | `add_two_num` | `ros2_foundation_interfaces/srv/AddTwoNum` |
| `led_server.py` | `led_client.py` | `set_led` | `ros2_foundation_interfaces/srv/LedControl` |
| `image_processor.py` | CLI 또는 client | `capture_snapshot` | `std_srvs/srv/Trigger` |

Service가 적합한 경우:

```text
- 한 번 요청하면 바로 답이 나오는 작업
- 현재 상태 조회
- 설정 변경
- 스냅샷 저장 요청
- lifecycle 전환 요청
```

Service가 부적합한 경우:

```text
- 카메라 이미지처럼 계속 들어오는 데이터
- 로봇 주행처럼 시간이 오래 걸리고 중간 상태가 필요한 작업
- 중간 취소가 필요한 작업
```

---

## 4. AddTwoNum.srv 해석

`ros2_foundation_interfaces/srv/AddTwoNum.srv`:

```text
int32 num1
int32 num2
---
int32 result
string message
```

`---` 위는 request, 아래는 response다.

`add_client.py`는 request를 채운다.

```python
self.req.num1 = num1
self.req.num2 = num2
```

`add_server.py`는 response를 채운다.

```python
response.result = request.num1 + request.num2
response.message = f'{request.num1} + {request.num2} = {response.result}'
```

---

## 5. LedControl.srv 해석

`ros2_foundation_interfaces/srv/LedControl.srv`:

```text
bool state
---
bool success
string message
```

이 예시는 실제 하드웨어 LED를 제어한다기보다, service request/response 흐름을 익히는 실습에 가깝다.

```text
request.state = True
  -> "LED 켜기 요청 수신"
  -> response.success = True
  -> response.message = "LED turned on."
```

---

## 6. Action - goal, feedback, result

Action은 오래 걸리는 목표 작업에 적합하다.

이번 코드:

```text
ros2_action_examples/move_server.py
ros2_action_examples/move_client.py
ros2_foundation_interfaces/action/MoveDistance.action
```

`MoveDistance.action`:

```text
float32 target_distance
---
bool reached
---
float32 current_distance
```

구조:

| 구간 | 의미 |
|---|---|
| Goal | 목표 거리 `target_distance` |
| Result | 최종 도달 여부 `reached` |
| Feedback | 현재 이동 거리 `current_distance` |

`move_client.py`는 목표를 보낸다.

```python
goal_msg = MoveDistance.Goal()
goal_msg.target_distance = distance
self._action_client.send_goal_async(goal_msg, feedback_callback=self.feedback_callback)
```

`move_server.py`는 1초마다 feedback을 발행한다.

```python
feedback_msg.current_distance = float(i)
goal_handle.publish_feedback(feedback_msg)
```

마지막에 성공 처리한다.

```python
goal_handle.succeed()
result.reached = True
```

---

## 7. Service와 Action의 실제 차이

| 질문 | Service | Action |
|---|---|---|
| 요청 후 바로 끝나는가? | 그렇다 | 아니다 |
| 중간 feedback이 필요한가? | 보통 없다 | 있다 |
| 취소가 필요한가? | 보통 아니다 | 가능하다 |
| 예시 | LED on/off, snapshot, map save | 이동 목표, navigation goal |

Nav2의 `/navigate_to_pose`가 service가 아니라 action인 이유도 같다. 목표 지점까지 이동하는 동안 시간이 걸리고, 중간 feedback과 최종 result가 필요하기 때문이다.

---

## 8. Interface 패키지 ros2_foundation_interfaces

`ros2_foundation_interfaces`는 직접 실행하는 노드가 아니다. 메시지 타입을 정의해서 다른 패키지에서 import하게 해주는 패키지다.

```text
.msg    -> Topic 데이터 구조
.srv    -> Service request/response 구조
.action -> Action goal/result/feedback 구조
```

`ros2_foundation_interfaces/CMakeLists.txt`의 핵심:

```cmake
rosidl_generate_interfaces(${PROJECT_NAME}
  "srv/LedControl.srv"
  "srv/AddTwoNum.srv"
  "action/MoveDistance.action"
  "msg/ObjectDetection.msg"
  "msg/ObjectDetectionArray.msg"
  DEPENDENCIES std_msgs
)
```

빌드 후 Python에서는 이런 식으로 import한다.

```python
from ros2_foundation_interfaces.srv import AddTwoNum
from ros2_foundation_interfaces.action import MoveDistance
from ros2_foundation_interfaces.msg import ObjectDetectionArray
```

---

## 9. ObjectDetectionArray.msg 해석

`ObjectDetection.msg`:

```text
string class_name
float64 confidence
int32[4] bbox
```

`ObjectDetectionArray.msg`:

```text
std_msgs/Header header
ObjectDetection[] detections
```

여기서 Header가 중요하다.

```text
header.stamp    -> 이 detection이 어느 시각의 이미지에서 나왔는가
header.frame_id -> 이 detection을 어느 camera frame 기준으로 해석할 것인가
```

`yolo_detection_publisher.py`는 원본 이미지 메시지의 header를 detection array에 그대로 복사한다.

```python
detection_array_msg.header = msg.header
```

그래서 뒤의 `yolo_tf_broadcaster.py`가 detection message의 `header.frame_id`를 parent frame으로 사용할 수 있다.

---

## 10. 선택 기준 정리

| 만들고 싶은 기능 | 적합한 ROS2 구조 |
|---|---|
| 문자열을 계속 보내기 | Topic |
| 카메라 이미지를 계속 보내기 | Topic |
| 로봇 속도 명령을 계속 보내기 | Topic |
| 스냅샷 저장 요청 | Service |
| LED 켜기/끄기 요청 | Service |
| 목표 거리만큼 이동하고 중간 진행률 보기 | Action |
| 목표 위치까지 주행하기 | Action |
| YOLO bbox 결과 구조 정의 | Custom msg |
| 두 숫자 더하기 request/response 정의 | Custom srv |
| 이동 goal/feedback/result 정의 | Custom action |
