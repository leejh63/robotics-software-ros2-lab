# 00. ROS2 소스 패키지 구성 요약

이 문서는 `$ROS2_WS/src`의 패키지들을 ROS2 관점에서 정리한 기준 문서다. 각 파일이 package, executable, node, topic, service, action, TF와 어떻게 연결되는지 확인하는 데 목적이 있다.

---

## 1. 전체 패키지 요약

| package | build type | 역할 | 주요 개념 |
|---|---|---|---|
| `this_test` | `ament_python` | Python topic pub/sub, turtlesim velocity publisher | node, topic, parameter |
| `lee_pkg` | `ament_cmake` | C++ topic pub/sub | rclcpp, CMakeLists, executable install |
| `my_if` | `ament_cmake` | custom msg/srv/action 정의 | rosidl code generation |
| `my_robot_service` | `ament_python` | service server/client | request/response |
| `my_robot_action` | `ament_python` | action server/client | goal/feedback/result |
| `camera_pkg` | `ament_python` | camera, OpenCV, YOLO, custom detection msg | sensor_msgs/Image, cv_bridge, parameter |
| `py_launch_example` | `ament_python` | camera_pkg 노드 묶음 실행 | launch, condition, parameter YAML |
| `tf_pkg_example` | `ament_python` | TF tree, TF listener, YOLO detection TF 변환 | /tf, /tf_static, frame_id |

---

## 2. this_test - Python 기본 pub/sub와 parameter

실제 파일:

```text
this_test/this_test/test.py
this_test/this_test/listener.py
this_test/this_test/ssss.py
this_test/setup.py
```

`setup.py`의 실행 이름:

| executable | source file | 실행 후 node name | 역할 |
|---|---|---|---|
| `lee_node` | `this_test.test:main` | `talker` | `std_msgs/String`를 `user_ns` topic으로 발행 |
| `lee_node2` | `this_test.listener:main` | `listener` | `user_ns` topic 구독 |
| `lee_node3` | `this_test.ssss:main` | `turtle_square` | `/turtle3/cmd_vel`로 `Twist` 발행 |

핵심 학습 포인트:

```text
file name != executable name != node name != topic name
```

예를 들어 `test.py`는 파일 이름이고, `lee_node`는 실행 이름이고, 실행 후 node 이름은 `talker`다. 발행 topic은 `user_ns`이다.

---

## 3. lee_pkg - C++ pub/sub

실제 파일:

```text
lee_pkg/src/cpp_test1.cpp
lee_pkg/src/cpp_test2.cpp
lee_pkg/CMakeLists.txt
```

`CMakeLists.txt` 기준:

| executable | source file | node name | topic | type |
|---|---|---|---|---|
| `talker` | `cpp_test1.cpp` | `talker1` | `cpp_1` | `std_msgs/msg/String` |
| `listener` | `cpp_test2.cpp` | `listener` | `cpp_1` | `std_msgs/msg/String` |

Python 패키지는 `setup.py`의 `console_scripts`로 executable을 만들고, C++ 패키지는 `CMakeLists.txt`의 `add_executable()`과 `install(TARGETS ...)`로 executable을 만든다.

---

## 4. my_if - custom interface 패키지

실제 파일:

```text
my_if/msg/ObjectDetection.msg
my_if/msg/ObjectDetectionArray.msg
my_if/srv/AddTwoNum.srv
my_if/srv/LedControl.srv
my_if/action/Movelee.action
my_if/CMakeLists.txt
```

정의된 interface:

| 종류 | 파일 | 의미 |
|---|---|---|
| msg | `ObjectDetection.msg` | YOLO 검출 1개: class name, confidence, bbox |
| msg | `ObjectDetectionArray.msg` | 여러 검출 결과 + Header |
| srv | `AddTwoNum.srv` | 두 정수 입력, 합산 결과와 문자열 반환 |
| srv | `LedControl.srv` | bool state 입력, success/message 반환 |
| action | `Movelee.action` | target distance goal, current distance feedback, reached result |

`my_if`는 실행 노드가 있는 패키지가 아니라, 다른 패키지들이 import해서 쓰는 타입 생성용 패키지다.

```text
my_robot_service -> from my_if.srv import AddTwoNum, LedControl
my_robot_action  -> from my_if.action import Movelee
camera_pkg       -> from my_if.msg import ObjectDetection, ObjectDetectionArray
tf_pkg_example       -> from my_if.msg import ObjectDetectionArray
```

---

## 5. my_robot_service - Service 실습

실제 파일:

```text
my_robot_service/my_robot_service/add_server.py
my_robot_service/my_robot_service/add_client.py
my_robot_service/my_robot_service/led_server.py
my_robot_service/my_robot_service/led_client.py
```

| executable | node name | service name | service type | 역할 |
|---|---|---|---|---|
| `add_server1` | `add_server1` | `add_two_num1` | `my_if/srv/AddTwoNum` | 두 정수 더하기 서버 |
| `add_client1` | `add_client1` | `add_two_num1` | `my_if/srv/AddTwoNum` | 더하기 요청 클라이언트 |
| `led_server1` | `led_service_server1` | `set_led1` | `my_if/srv/LedControl` | LED on/off 흉내 서버 |
| `led_client1` | `led_service_client1` | `set_led1` | `my_if/srv/LedControl` | LED 제어 요청 클라이언트 |

Service는 “계속 흐르는 데이터”가 아니라 “한 번 요청하고 한 번 응답받는 구조”다.

---

## 6. my_robot_action - Action 실습

실제 파일:

```text
my_robot_action/my_robot_action/move_server.py
my_robot_action/my_robot_action/move_client.py
```

| executable | node name | action name | action type | 역할 |
|---|---|---|---|---|
| `move_server1` | `robot_move_server1` | `move_robot1` | `my_if/action/Movelee` | 목표 거리까지 진행 feedback 발행 |
| `move_client1` | `robot_move_client1` | `move_robot1` | `my_if/action/Movelee` | goal 전송, feedback/result 수신 |

Action은 Nav2의 `NavigateToPose`를 이해하기 위한 가장 중요한 기초다.

```text
Service: 요청 -> 응답
Action : goal -> feedback 반복 -> result
```

---

## 7. camera_pkg - Camera/OpenCV/YOLO 실습

실제 파일:

```text
camera_pkg/camera_pkg/imagePlee.py
camera_pkg/camera_pkg/imageOPENlee.py
camera_pkg/camera_pkg/imageSlee.py
camera_pkg/camera_pkg/imageYOLOlee.py
camera_pkg/camera_pkg/imgYOLOlee.py
camera_pkg/config/pub_cam_params.yaml
```

| executable | source file | node name | 주요 입출력 |
|---|---|---|---|
| `image_pub1` | `imagePlee.py` | `image_publisher1` 또는 launch에서 `test` | `/image_raw0` publish |
| `image_edge1` | `imageOPENlee.py` | `image_edge_publisher1` | `/image_raw0` subscribe, `/image_edge1` publish |
| `image_proc1` | `imageSlee.py` | `image_processor1` | raw/yolo/canny subscribe, `capture_snapshot1` service |
| `image_yolo1` | `imageYOLOlee.py` | `image_yolo_publisher1` | `/image_raw0` subscribe, `/image_yolo1` publish |
| `yolo_pub_l` | `imgYOLOlee.py` | `image_yolo_publisher1` | `/image_raw0` subscribe, `/img_yolo1` custom msg publish |

중요한 차이:

```text
/image_yolo1 : YOLO 박스가 그려진 Image topic
/img_yolo1   : YOLO detection 결과를 담은 ObjectDetectionArray custom msg topic
```

---

## 8. py_launch_example - Launch 실습

실제 파일:

```text
py_launch_example/launch/robot_ns_bring_launch.py
py_launch_example/launch/robot_ns_ep_launch.py
```

| launch file | 실행되는 주요 노드 | 특징 |
|---|---|---|
| `lee_bring_launch.py` | image publisher, YOLO image, Canny, rqt_image_view 조건 실행 | 여러 노드를 한 번에 실행 |
| `lee_ep_launch.py` | image publisher + YAML parameter, YOLO custom msg publisher, rqt_image_view 조건 실행 | `get_package_share_directory()`와 parameter YAML 사용 |

Launch는 단순히 명령어를 줄여주는 파일이 아니라 ROS graph 구성을 선언하는 파일이다.

---

## 9. tf_pkg_example - TF 실습

실제 파일:

```text
tf_pkg_example/tf_pkg_example/odom_simul.py
tf_pkg_example/tf_pkg_example/tf_tree_simul.py
tf_pkg_example/tf_pkg_example/tf_listener.py
tf_pkg_example/tf_pkg_example/tf_broad_yolo.py
tf_pkg_example/launch/tf_tree_demo_launch.py
tf_pkg_example/launch/robot_ns_yolo_launch.py
```

| executable | source file | 역할 |
|---|---|---|
| `odom_simul` | `odom_simul.py` | `odom_robot_ns -> base_link_robot_ns` 동적 TF 발행 |
| `tf_tree_simul` | `tf_tree_simul.py` | `map_robot_ns -> odom_robot_ns -> base_link_robot_ns -> m_lee/k_lee` TF tree 발행 |
| `tf_listener` | `tf_listener.py` | target/source frame 사이 transform 조회 |
| `tf_broad_yolo` | `tf_broad_yolo.py` | `/img_yolo1` detection을 object TF frame으로 변환 |

`lee_yolo_launch.py`는 camera, YOLO custom message, TF broadcaster, TF listener, RViz/rqt_tf_tree를 하나로 묶는 종합 실습이다.

---

## 10. 현재 문서화 기준

이 문서에서는 코드를 고치지 않는다. 다만 아래처럼 실행상 주의가 필요한 부분은 별도 observation 문서에 기록한다.

```text
- package.xml 의존성 누락 가능성
- YOLO model_path 상대경로 문제
- imagePlee.py에서 topic_name parameter를 선언하지만 publisher는 image_raw0로 고정된 점
- py_launch_example의 config 설치 구조와 실제 config 폴더 존재 여부
- launch에서 RViz 경로가 절대경로로 박혀 있는 점
- camera_frame / camera_link_lee / base_link_robot_ns 같은 frame 이름 혼용 가능성
```

자세한 내용은 `09_runtime_notes.md`에 정리했다.
