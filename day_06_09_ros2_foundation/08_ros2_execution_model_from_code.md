# 08. 실제 코드 기준 ROS2 실행 모델 정리

이 문서는 “내가 작성한 파일이 ROS2에서 어떻게 실행 단위가 되는가”를 실제 코드 기준으로 다시 정리한다.

---

## 1. Python node가 실행되기까지

예시: `camera_pkg/imagePlee.py`

```text
source file
  camera_pkg/camera_pkg/imagePlee.py

setup.py console_scripts
  image_pub1 = camera_pkg.imagePlee:main

build/install
  colcon build --symlink-install
  source install/setup.bash

run
  ros2 run camera_pkg image_pub1

runtime node
  /image_publisher1

launch에서 name='test'로 실행하면
  /test
```

핵심은 source file 이름과 실행 이름이 다를 수 있다는 점이다.

---

## 2. C++ node가 실행되기까지

예시: `lee_pkg/src/cpp_test1.cpp`

```text
source file
  lee_pkg/src/cpp_test1.cpp

CMakeLists.txt
  add_executable(talker src/cpp_test1.cpp)
  install(TARGETS talker listener DESTINATION lib/${PROJECT_NAME})

build/source
  colcon build --packages-select lee_pkg
  source install/setup.bash

run
  ros2 run lee_pkg talker

runtime node
  /talker1
```

C++에서는 `setup.py`가 아니라 CMake가 executable 등록을 담당한다.

---

## 3. Custom interface가 import되기까지

예시: `my_if/msg/ObjectDetectionArray.msg`

```text
interface source
  my_if/msg/ObjectDetectionArray.msg

CMakeLists.txt
  rosidl_generate_interfaces(...)

package.xml
  rosidl_default_generators
  rosidl_default_runtime
  member_of_group rosidl_interface_packages

build/source
  colcon build --packages-select my_if
  source install/setup.bash

Python import
  from my_if.msg import ObjectDetectionArray
```

interface를 수정한 뒤 build/source를 하지 않으면 기존 타입이 남아 있거나 import가 실패할 수 있다.

---

## 4. 실제 camera pipeline 실행 모델

```text
ros2 run camera_pkg image_pub1
  -> /image_publisher1
  -> publish /image_raw0, sensor_msgs/Image, frame_id=camera_frame

ros2 run camera_pkg image_edge1
  -> /image_edge_publisher1
  -> subscribe /image_raw0
  -> publish /image_edge1

ros2 run camera_pkg image_yolo1
  -> /image_yolo_publisher1
  -> subscribe /image_raw0
  -> publish /image_yolo1

ros2 run camera_pkg yolo_pub_l
  -> /image_yolo_publisher1
  -> subscribe /image_raw0
  -> publish /img_yolo1, my_if/ObjectDetectionArray
```

주의할 점: `image_yolo1`과 `yolo_pub_l`은 코드상 node name이 둘 다 `image_yolo_publisher1`이다. 동시에 실행하면 node name 중복 경고나 graph 혼동이 생길 수 있다. launch에서 name을 바꾸거나, 실행 목적을 분리해서 쓰는 것이 좋다.

---

## 5. 실제 service 실행 모델

```text
ros2 run my_robot_service add_server1
  -> node /add_server1
  -> service /add_two_num1 생성

ros2 run my_robot_service add_client1
  -> node /add_client1
  -> service /add_two_num1 요청
```

Service server가 먼저 떠 있어야 client가 요청할 수 있다. client 코드에서는 다음 구조로 서버를 기다린다.

```python
while not self.cli.wait_for_service(timeout_sec=1.0):
    self.get_logger().info('서버 대기 중...')
```

---

## 6. 실제 action 실행 모델

```text
ros2 run my_robot_action move_server1
  -> node /robot_move_server1
  -> action /move_robot1 생성

ros2 run my_robot_action move_client1
  -> node /robot_move_client1
  -> goal target_distance=5.0 전송
  -> feedback current_distance 수신
  -> result reached 수신
```

Action server도 먼저 떠 있어야 한다. client는 `wait_for_server()`로 기다린다.

---

## 7. 실제 TF 실행 모델

### tf_tree_demo_launch.py

```text
ros2 launch tf_pkg_example tf_tree_demo_launch.py use_listener:=true use_rqt_tree:=true
```

실행 흐름:

```text
tf_tree_simul
  -> map_robot_ns -> odom_robot_ns static TF
  -> odom_robot_ns -> base_link_robot_ns dynamic TF
  -> base_link_robot_ns -> m_lee dynamic TF
  -> base_link_robot_ns -> k_lee dynamic TF

tf_listener
  -> odom_robot_ns 기준 m_lee 위치 조회

rqt_tf_tree
  -> tree GUI 확인
```

### lee_yolo_launch.py

```text
ros2 launch tf_pkg_example lee_yolo_launch.py use_listener:=true use_rqt_tree:=true
```

실행 흐름:

```text
camera image publish
  -> /image_raw0
YOLO detection publish
  -> /img_yolo1
static TF
  -> map_robot_ns -> odom_robot_ns
odom_simul
  -> odom_robot_ns -> base_link_robot_ns
static TF
  -> base_link_robot_ns -> camera_frame
tf_broad_yolo
  -> camera_frame -> object_person_0
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
