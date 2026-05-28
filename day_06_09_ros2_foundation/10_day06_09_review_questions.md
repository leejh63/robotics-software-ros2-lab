# 10. Day 06~09 복습 질문

이 문서는 Day 06~09를 제대로 이해했는지 확인하기 위한 질문 목록이다. 답을 외우기보다 실제 코드 파일을 열어보면서 확인하는 것이 좋다.

---

## 1. Workspace / Package / Node

1. `projects/ros2_foundation_lab/src/ros2_camera_examples`는 workspace인가 package인가?
2. `ros2_camera_examples/ros2_camera_examples/image_publisher.py`는 package 이름인가 source file 이름인가?
3. `ros2 run ros2_camera_examples image_publisher`에서 `ros2_camera_examples`와 `image_publisher`은 각각 무엇인가?
4. `image_publisher.py` 내부의 `super().__init__('image_publisher')`는 무엇을 정하는가?
5. launch에서 `name='test'`를 주면 node 이름은 어떻게 되는가?
6. parameter YAML의 최상위 키가 node 이름과 맞아야 하는 이유는 무엇인가?

---

## 2. Topic

1. `ros2_topic_examples/string_talker.py`가 publish하는 topic은 무엇인가?
2. `ros2_topic_examples/string_listener.py`가 subscribe하는 topic과 message type은 무엇인가?
3. `ros2_cpp_examples`의 C++ talker/listener는 어떤 topic으로 연결되는가?
4. `/image_raw`와 `/image_yolo`의 message type은 무엇인가?
5. `/yolo_detections`는 왜 `sensor_msgs/Image`가 아니라 custom message인가?
6. topic 이름과 frame 이름은 어떻게 다른가?

---

## 3. Service

1. `AddTwoNum.srv`에서 `---` 위와 아래는 각각 무엇인가?
2. `add_server.py`는 어떤 service name을 생성하는가?
3. `add_client.py`가 서버를 기다리는 코드는 어디에 있는가?
4. `image_processor.py`의 `capture_snapshot`은 왜 topic보다 service가 자연스러운가?
5. service가 카메라 이미지 스트림에 부적합한 이유는 무엇인가?

---

## 4. Action

1. `MoveDistance.action`의 goal/result/feedback 필드는 각각 무엇인가?
2. `move_client.py`는 goal을 어떻게 전송하는가?
3. `move_server.py`는 feedback을 언제 발행하는가?
4. action이 service와 다른 가장 큰 차이는 무엇인가?
5. Nav2의 `NavigateToPose`가 action인 이유는 무엇인가?

---

## 5. Launch / Parameter

1. `camera_pipeline.launch.py`는 어떤 노드들을 실행하는가?
2. `use_viewer` argument는 실제로 어떤 프로그램을 조건부 실행하는가?
3. `camera_yolo_pipeline.launch.py`에서 `get_package_share_directory('ros2_camera_examples')`는 왜 필요한가?
4. `pub_cam_params.yaml`의 최상위 키가 `image_publisher`여야 하는 이유는 무엇인가?
5. `image_publisher.py`에서 `topic_name`, `image_size`, `frame_id` parameter는 각각 어디에 반영되는가?
6. parameter를 바꾼 뒤 timer 주기를 다시 만드는 이유는 무엇인가?

---

## 6. Custom Interface

1. `ros2_foundation_interfaces`는 왜 일반 Python node 패키지가 아니라 interface 패키지로 봐야 하는가?
2. `.msg`, `.srv`, `.action`의 차이는 무엇인가?
3. `ObjectDetectionArray.msg`에 Header가 필요한 이유는 무엇인가?
4. interface 파일을 수정한 뒤 왜 다시 build/source해야 하는가?
5. `ros2_camera_examples`와 `ros2_tf_examples`는 `ros2_foundation_interfaces`의 어떤 message를 사용하는가?

---

## 7. TF2

1. `/tf`와 `/tf_static`의 차이는 무엇인가?
2. `odom_simulator.py`는 어떤 parent/child frame을 발행하는가?
3. `tf_tree_simulator.py`가 만드는 TF tree를 그려볼 수 있는가?
4. `tf_listener.py`의 target frame과 source frame은 어떤 의미인가?
5. `yolo_tf_broadcaster.py`는 detection message를 어떤 object frame으로 바꾸는가?
6. `fixed_depth`를 쓰는 YOLO TF 실습을 실제 3D 위치 추정이라고 말하면 안 되는 이유는 무엇인가?

---

## 8. Day 10~13 연결

1. SLAM/AMCL/Nav2에서 `/scan` topic만 있으면 충분하지 않은 이유는 무엇인가?
2. `map -> odom -> base_link -> sensor` TF chain이 왜 중요한가?
3. RViz에서 map이 안 보일 때 topic보다 먼저 확인해야 할 frame 설정은 무엇인가?
4. Nav2 Goal이 안 먹을 때 topic list만 보면 부족한 이유는 무엇인가?
5. lifecycle node가 있는 시스템에서 node가 떠 있는 것과 active 상태인 것은 왜 다른가?

---

## 9. 스스로 설명해보기

아래 문장을 스스로 설명할 수 있으면 Day 06~09의 큰 흐름은 잡힌 것이다.

```text
ros2_camera_examples/image_publisher.py는 웹캠 이미지를 sensor_msgs/Image로 바꿔 /image_raw topic에 발행한다.
이 메시지는 header.frame_id=camera_link를 가지므로, 공간적으로 해석하려면 camera_link가 TF tree에 연결되어 있어야 한다.
yolo_detection_publisher.py는 /image_raw를 구독해 YOLO detection 결과를 ros2_foundation_interfaces/msg/ObjectDetectionArray로 /yolo_detections에 발행한다.
yolo_tf_broadcaster.py는 /yolo_detections을 구독하고 bbox 중심과 fixed_depth를 이용해 object_person_example_0 같은 검증용 object frame을 발행한다.
이 구조는 뒤쪽 SLAM/AMCL/Nav2에서 sensor topic과 TF frame을 함께 봐야 하는 이유를 이해하기 위한 기초 실습이다.
```
