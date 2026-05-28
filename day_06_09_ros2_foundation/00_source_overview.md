# 00. ROS2 소스 패키지 구성 요약

이 문서는 `projects/ros2_foundation_lab/src`의 패키지를 ROS2 관점에서 정리한 기준 문서다. 각 패키지가 package, executable, node, topic, service, action, TF와 어떻게 연결되는지 확인하는 데 목적이 있다.

---

## 1. 전체 패키지 요약

| package | build type | 역할 | 주요 개념 |
|---|---|---|---|
| `ros2_topic_examples` | `ament_python` | Python topic pub/sub, turtlesim velocity publisher | node, topic, parameter |
| `ros2_cpp_examples` | `ament_cmake` | C++ topic pub/sub | rclcpp, CMakeLists, executable install |
| `ros2_foundation_interfaces` | `ament_cmake` | custom msg/srv/action 정의 | rosidl code generation |
| `ros2_service_examples` | `ament_python` | service server/client | request/response |
| `ros2_action_examples` | `ament_python` | action server/client | goal/feedback/result |
| `ros2_camera_examples` | `ament_python` | camera, OpenCV, YOLO, custom detection msg | sensor_msgs/Image, cv_bridge, parameter |
| `ros2_launch_examples` | `ament_python` | camera/perception pipeline launch | launch, condition, parameter YAML |
| `ros2_tf_examples` | `ament_python` | TF tree, TF listener, YOLO detection TF 변환 | /tf, /tf_static, frame_id |


---

## 2. ros2_topic_examples - Python 기본 pub/sub와 parameter

주요 파일:

```text
ros2_topic_examples/ros2_topic_examples/string_talker.py
ros2_topic_examples/ros2_topic_examples/string_listener.py
ros2_topic_examples/ros2_topic_examples/turtle_square.py
ros2_topic_examples/setup.py
```

| executable | source file | 실행 후 node name | 역할 |
|---|---|---|---|
| `string_talker` | `string_talker.py` | `string_talker` | `std_msgs/String` topic 발행 |
| `string_listener` | `string_listener.py` | `string_listener` | 문자열 topic 구독 |
| `turtle_square` | `turtle_square.py` | `turtle_square` | `/turtle1/cmd_vel` 기본값으로 `Twist` 발행 |

핵심 학습 포인트는 다음이다.

```text
file name != executable name != node name != topic name
```

---

## 3. ros2_cpp_examples - C++ pub/sub

주요 파일:

```text
ros2_cpp_examples/src/cpp_talker.cpp
ros2_cpp_examples/src/cpp_listener.cpp
ros2_cpp_examples/CMakeLists.txt
```

| executable | source file | node name | topic | type |
|---|---|---|---|---|
| `cpp_talker` | `cpp_talker.cpp` | `cpp_talker` | `cpp_chatter` | `std_msgs/msg/String` |
| `cpp_listener` | `cpp_listener.cpp` | `cpp_listener` | `cpp_chatter` | `std_msgs/msg/String` |

Python 패키지는 `setup.py`의 `console_scripts`로 executable을 만들고, C++ 패키지는 `CMakeLists.txt`의 `add_executable()`과 `install(TARGETS ...)`로 executable을 만든다.

---

## 4. ros2_foundation_interfaces - custom interface 패키지

주요 파일:

```text
ros2_foundation_interfaces/msg/ObjectDetection.msg
ros2_foundation_interfaces/msg/ObjectDetectionArray.msg
ros2_foundation_interfaces/srv/AddTwoNum.srv
ros2_foundation_interfaces/srv/LedControl.srv
ros2_foundation_interfaces/action/MoveDistance.action
ros2_foundation_interfaces/CMakeLists.txt
```

| 종류 | 파일 | 의미 |
|---|---|---|
| msg | `ObjectDetection.msg` | YOLO 검출 1개: class name, confidence, bbox |
| msg | `ObjectDetectionArray.msg` | 여러 검출 결과 + Header |
| srv | `AddTwoNum.srv` | 두 정수 입력, 합산 결과와 문자열 반환 |
| srv | `LedControl.srv` | bool state 입력, success/message 반환 |
| action | `MoveDistance.action` | target distance goal, current distance feedback, reached result |

이 패키지는 실행 노드가 있는 패키지가 아니라, 다른 패키지에서 import해서 쓰는 타입 생성용 패키지다.

```text
ros2_service_examples -> from ros2_foundation_interfaces.srv import AddTwoNum, LedControl
ros2_action_examples  -> from ros2_foundation_interfaces.action import MoveDistance
ros2_camera_examples  -> from ros2_foundation_interfaces.msg import ObjectDetection, ObjectDetectionArray
ros2_tf_examples      -> from ros2_foundation_interfaces.msg import ObjectDetectionArray
```

---

## 5. ros2_service_examples - Service 실습

| executable | node name | service name | service type | 역할 |
|---|---|---|---|---|
| `add_two_num_server` | `add_two_num_server` | `add_two_num` | `ros2_foundation_interfaces/srv/AddTwoNum` | 두 정수 더하기 서버 |
| `add_two_num_client` | `add_two_num_client` | `add_two_num` | `ros2_foundation_interfaces/srv/AddTwoNum` | 더하기 요청 클라이언트 |
| `led_service_server` | `led_service_server` | `set_led` | `ros2_foundation_interfaces/srv/LedControl` | LED on/off 흉내 서버 |
| `led_service_client` | `led_service_client` | `set_led` | `ros2_foundation_interfaces/srv/LedControl` | LED 제어 요청 클라이언트 |

Service는 계속 흐르는 데이터가 아니라 한 번 요청하고 한 번 응답받는 구조다.

---

## 6. ros2_action_examples - Action 실습

| executable | node name | action name | action type | 역할 |
|---|---|---|---|---|
| `move_action_server` | `robot_move_action_server` | `move_robot` | `ros2_foundation_interfaces/action/MoveDistance` | 목표 거리까지 진행 feedback 발행 |
| `move_action_client` | `robot_move_action_client` | `move_robot` | `ros2_foundation_interfaces/action/MoveDistance` | goal 전송, feedback/result 수신 |

Action은 Nav2의 `NavigateToPose`를 이해하기 위한 중요한 기초다.

```text
Service: request -> response
Action : goal -> feedback 반복 -> result
```

---

## 7. ros2_camera_examples - Camera/OpenCV/YOLO 실습

| executable | source file | node name | 주요 입출력 |
|---|---|---|---|
| `image_publisher` | `image_publisher.py` | `image_publisher` | `/image_raw` publish |
| `image_edge_publisher` | `image_edge_publisher.py` | `image_edge_publisher` | `/image_raw` subscribe, `/image_edge` publish |
| `image_processor` | `image_processor.py` | `image_processor` | raw/yolo/canny subscribe, `capture_snapshot` service |
| `yolo_image_publisher` | `yolo_image_publisher.py` | `yolo_image_publisher` | `/image_raw` subscribe, `/image_yolo` publish |
| `yolo_detection_publisher` | `yolo_detection_publisher.py` | `yolo_detection_publisher` | `/image_raw` subscribe, `/yolo_detections` custom msg publish |

중요한 차이는 다음이다.

```text
/image_yolo : YOLO 박스가 그려진 Image topic
/yolo_detections   : YOLO detection 결과를 담은 ObjectDetectionArray custom msg topic
```

---

## 8. ros2_launch_examples - Launch 실습

| launch file | 실행되는 주요 노드 | 특징 |
|---|---|---|
| `camera_pipeline.launch.py` | image publisher, YOLO image, Canny, rqt_image_view 조건 실행 | 여러 노드를 한 번에 실행 |
| `camera_yolo_pipeline.launch.py` | image publisher + YAML parameter, YOLO custom msg publisher, rqt_image_view 조건 실행 | `get_package_share_directory()`와 parameter YAML 사용 |

Launch는 단순히 명령어를 줄이는 파일이 아니라 ROS graph 구성을 선언하는 파일이다.

---

## 9. ros2_tf_examples - TF 실습

| executable | source file | 역할 |
|---|---|---|
| `odom_simulator` | `odom_simulator.py` | `odom -> base_link` 동적 TF 발행 |
| `tf_tree_simulator` | `tf_tree_simulator.py` | `map -> odom -> base_link -> left_marker/right_marker` TF tree 발행 |
| `tf_listener` | `tf_listener.py` | target/source frame 사이 transform 조회 |
| `yolo_tf_broadcaster` | `yolo_tf_broadcaster.py` | YOLO detection message를 object TF frame으로 변환 |

| launch file | 역할 |
|---|---|
| `tf_tree_demo.launch.py` | 기본 TF tree와 listener/rqt_tf_tree 선택 실행 |
| `yolo_tf_pipeline.launch.py` | camera + YOLO detection + TF broadcaster + RViz/rqt_tf_tree 선택 실행 |

TF 실습의 핵심은 topic 이름과 frame 이름을 구분하는 것이다. `/tf`는 transform message가 흐르는 topic이고, `map`, `odom`, `base_link`, `camera_link`는 transform 안에 들어 있는 frame 이름이다.
