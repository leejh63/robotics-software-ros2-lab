# 08. 실제 코드 기준 ROS2 실행 모델 정리

이 문서는 “내가 작성한 파일이 ROS2에서 어떻게 실행 단위가 되는가”를 실제 코드 기준으로 다시 정리한다.

---

## 1. Python node가 실행되기까지

예시: `ros2_camera_examples/image_publisher.py`

```text
source file
  ros2_camera_examples/ros2_camera_examples/image_publisher.py

setup.py console_scripts
  image_publisher = ros2_camera_examples.image_publisher:main

build/install
  colcon build --symlink-install
  source install/setup.bash

run
  ros2 run ros2_camera_examples image_publisher

runtime node
  /image_publisher

launch에서 name='test'로 실행하면
  /test
```

핵심은 source file 이름과 실행 이름이 다를 수 있다는 점이다.

---

## 2. C++ node가 실행되기까지

예시: `ros2_cpp_examples/src/cpp_talker.cpp`

```text
source file
  ros2_cpp_examples/src/cpp_talker.cpp

CMakeLists.txt
  add_executable(cpp_talker src/cpp_talker.cpp)
  add_executable(cpp_listener src/cpp_listener.cpp)
  install(TARGETS cpp_talker cpp_listener DESTINATION lib/${PROJECT_NAME})

build/source
  colcon build --packages-select ros2_cpp_examples
  source install/setup.bash

run
  ros2 run ros2_cpp_examples cpp_talker

runtime node
  /cpp_talker
```

C++에서는 `setup.py`가 아니라 CMake가 executable 등록을 담당한다.

---

## 3. Custom interface가 import되기까지

예시: `ros2_foundation_interfaces/msg/ObjectDetectionArray.msg`

```text
interface source
  ros2_foundation_interfaces/msg/ObjectDetectionArray.msg

CMakeLists.txt
  rosidl_generate_interfaces(...)

package.xml
  rosidl_default_generators
  rosidl_default_runtime
  member_of_group rosidl_interface_packages

build/source
  colcon build --packages-select ros2_foundation_interfaces
  source install/setup.bash

Python import
  from ros2_foundation_interfaces.msg import ObjectDetectionArray
```

interface를 수정한 뒤 build/source를 하지 않으면 기존 타입이 남아 있거나 import가 실패할 수 있다.

---

## 4. 실제 camera pipeline 실행 모델

```text
ros2 run ros2_camera_examples image_publisher
  -> /image_publisher
  -> publish /image_raw, sensor_msgs/Image, frame_id=camera_link

ros2 run ros2_camera_examples image_edge_publisher
  -> /image_edge
  -> subscribe /image_raw
  -> publish /image_edge

ros2 run ros2_camera_examples yolo_image_publisher
  -> /yolo_image_publisher
  -> subscribe /image_raw
  -> publish /image_yolo

ros2 run ros2_camera_examples yolo_detection_publisher
  -> /yolo_detection_publisher
  -> subscribe /image_raw
  -> publish /yolo_detections, ros2_foundation_interfaces/msg/ObjectDetectionArray
```

두 노드는 입력으로 `/image_raw`를 공유하지만 출력 목적이 다르다. `yolo_image_publisher`는 사람이 보기 좋은 이미지 topic을 만들고, `yolo_detection_publisher`는 다른 노드가 처리하기 좋은 custom message topic을 만든다.

---

## 5. 실제 service 실행 모델

```text
ros2 run ros2_service_examples add_two_num_server
  -> node /add_two_num_server
  -> service /add_two_num 생성

ros2 run ros2_service_examples add_two_num_client
  -> node /add_two_num_client
  -> service /add_two_num 요청
```

Service server가 먼저 떠 있어야 client가 요청할 수 있다. client 코드에서는 다음 구조로 서버를 기다린다.

```python
while not self.cli.wait_for_service(timeout_sec=1.0):
    self.get_logger().info('Waiting for service...')
```

---

## 6. 실제 action 실행 모델

```text
ros2 run ros2_action_examples move_action_server
  -> node /robot_move_action_server
  -> action /move_robot 생성

ros2 run ros2_action_examples move_action_client
  -> node /robot_move_action_client
  -> goal target_distance=5.0 전송
  -> feedback current_distance 수신
  -> result reached 수신
```

Action server도 먼저 떠 있어야 한다. client는 `wait_for_server()`로 기다린다.

---

## 7. 실제 TF 실행 모델

### tf_tree_demo.launch.py

```text
ros2 launch ros2_tf_examples tf_tree_demo.launch.py use_listener:=true use_rqt_tree:=true
```

실행 흐름:

```text
tf_tree_simulator
  -> map -> odom static TF
  -> odom -> base_link dynamic TF
  -> base_link -> left_marker dynamic TF
  -> base_link -> right_marker dynamic TF

tf_listener
  -> odom 기준 left_marker 위치 조회

rqt_tf_tree
  -> tree GUI 확인
```

### yolo_tf_pipeline.launch.py

```text
ros2 launch ros2_tf_examples yolo_tf_pipeline.launch.py use_listener:=true use_rqt_tree:=true
```

실행 흐름:

```text
camera image publish
  -> /image_raw
YOLO detection publish
  -> /yolo_detections
static TF
  -> map -> odom
odom_simulator
  -> odom -> base_link
static TF
  -> base_link -> camera_link
yolo_tf_broadcaster
  -> camera_link -> object_person_example_0
```

---

## 8. 확인은 항상 ROS graph 기준으로 한다

코드를 읽는 것과 실행 결과를 확인하는 것은 다르다. 실행 후에는 항상 graph를 확인해야 한다.

```bash
ros2 node list
ros2 topic list
ros2 service list
ros2 action list
ros2 param list
ros2 run tf2_tools view_frames
```

코드상으로는 publish한다고 되어 있어도 실제 카메라가 열리지 않거나, model path가 틀리거나, parameter가 적용되지 않으면 원하는 topic이 나오지 않을 수 있다.

---

## 9. 실행 구조 정리 시 주의할 점

이번 문서화 단계의 목적은 “돌아가게 고치기”가 아니다.

현재 목적:

```text
- 어떤 코드가 어떤 ROS2 개념을 보여주는지 정리
- 실행 시 확인해야 할 명령어 정리
- 헷갈리는 naming/parameter/TF 지점 기록
- 뒤쪽 Gazebo/SLAM/AMCL/Nav2로 이어지는 기반 정리
```

수정 후보는 `09_runtime_notes.md`에 따로 기록한다.
