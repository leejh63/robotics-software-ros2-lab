# 01. Day 06~09 전체 읽는 순서

## 한 줄 결론

Day 06~09는 ROS2에서 “코드가 노드가 되고, 노드가 topic/service/action/TF를 통해 연결되는 과정”을 배우는 구간이다. 뒤쪽 Gazebo, SLAM, AMCL, Nav2는 전부 이 기본 구조 위에서 돌아간다.

---

## 1. 먼저 봐야 하는 큰 흐름

```text
1. workspace 생성
2. package 생성
3. Python/C++ source file 작성
4. setup.py 또는 CMakeLists.txt에 executable 등록
5. colcon build
6. source install/setup.bash
7. ros2 run 또는 ros2 launch로 실행
8. ros2 node/topic/service/action/param/tf 명령으로 확인
```

이 흐름을 모르면 “파일은 있는데 실행이 안 됨”, “노드는 켜졌는데 topic이 안 보임”, “topic은 보이는데 RViz에서 안 보임” 같은 문제가 계속 생긴다.

---

## 2. 실제로 연결한 코드 흐름

### 2.1 가장 작은 예시: Python topic

```text
this_test/test.py
  -> executable: lee_node
  -> node: talker
  -> publish: user_ns, std_msgs/String

this_test/listener.py
  -> executable: lee_node2
  -> node: listener
  -> subscribe: user_ns, std_msgs/String
```

이 예시는 ROS2 topic의 최소 구조다.

### 2.2 C++에서도 같은 구조

```text
lee_pkg/src/cpp_test1.cpp
  -> executable: talker
  -> node: talker1
  -> publish: cpp_1, std_msgs/String

lee_pkg/src/cpp_test2.cpp
  -> executable: listener
  -> node: listener
  -> subscribe: cpp_1, std_msgs/String
```

Python이든 C++이든 ROS graph 관점에서는 “node가 topic을 publish/subscribe한다”는 점이 같다.

### 2.3 Service와 Action으로 확장

```text
my_robot_service
  -> add_two_num1 service
  -> set_led1 service

my_robot_action
  -> move_robot1 action
```

Service는 요청과 응답이 짧게 끝나는 구조다. Action은 goal을 보내고, 중간 feedback을 받다가, 마지막 result를 받는 구조다.

### 2.4 Camera와 YOLO로 sensor data 처리

```text
imagePlee.py
  -> /image_raw0 publish

imageOPENlee.py
  -> /image_raw0 subscribe
  -> /image_edge1 publish

imageYOLOlee.py
  -> /image_raw0 subscribe
  -> /image_yolo1 publish

imgYOLOlee.py
  -> /image_raw0 subscribe
  -> /img_yolo1 publish
```

Day 01~05의 OpenCV/YOLO가 여기서 ROS2 topic으로 연결된다.

### 2.5 Custom message와 TF로 확장

```text
my_if/msg/ObjectDetectionArray.msg
  -> YOLO 결과를 구조화한 메시지

camera_pkg/imgYOLOlee.py
  -> /img_yolo1 publish

tf_pkg_lee/tf_broad_yolo.py
  -> /img_yolo1 subscribe
  -> object_person_lee_0 같은 TF frame publish
```

이 흐름은 “인식 결과를 좌표계에 붙인다”는 연습이다. 실제 거리 추정은 고정 depth 기반의 단순화이므로 정확한 3D 인식으로 과장하면 안 된다.

---

## 3. Day 06~09와 Day 10~13의 연결

```text
Day 06 workspace/package/node/topic
  -> Gazebo/SLAM/AMCL/Nav2 패키지 실행과 확인의 기본

Day 07 pub/sub/service/action
  -> sensor topic, lifecycle service, NavigateToPose action 이해

Day 08 launch/parameter/custom interface
  -> Gazebo/SLAM/AMCL/Nav2를 launch와 YAML로 묶는 구조 이해

Day 09 TF2/sensor/rosbag
  -> map/odom/base_link/sensor frame과 재현 실험 이해
```

뒤쪽에서 문제가 생기면 바로 알고리즘을 의심하지 말고, 아래 순서로 확인해야 한다.

```text
1. build/source가 되었는가?
2. package/executable 이름이 맞는가?
3. node가 실제로 떠 있는가?
4. topic/service/action 이름과 타입이 맞는가?
5. parameter가 적용되었는가?
6. TF frame이 연결되어 있는가?
7. namespace가 붙어서 실제 이름이 바뀐 것은 아닌가?
```

---

## 4. 이번 폴더의 읽기 순서

```text
00_source_package_map.md
  -> 실제 코드 지도

02_workspace_package_node_topic.md
  -> 이름 체계와 실행 구조

03_pubsub_service_action_interface.md
  -> 통신 방식 선택 기준

04_launch_parameter_custom_msg_debug.md
  -> launch, parameter, interface 생성 구조

05_tf2_sensor_rosbag_foundation.md
  -> TF, sensor message, rosbag 기초

06_camera_yolo_tf_flow.md
  -> camera -> YOLO -> detection msg -> object TF 흐름

08_ros2_execution_model_from_code.md
  -> 실제 코드 기준으로 실행 모델 다시 정리

09_runtime_observations_without_code_changes.md
  -> 지금 코드를 실행할 때 조심할 부분
```

---

## 5. 이 단계에서 특히 헷갈리면 안 되는 것

| 헷갈리는 것 | 정확한 구분 |
|---|---|
| package와 node | package는 빌드/배포 단위, node는 실행 중인 프로세스 단위 |
| file name과 executable | 파일명은 source 파일 이름, executable은 `setup.py`/`CMakeLists.txt`에서 등록한 실행 이름 |
| topic과 message type | topic은 통신 채널 이름, message type은 데이터 구조 |
| topic 이름과 frame 이름 | `/image_raw0`는 topic, `camera_lee`는 frame |
| service와 action | service는 짧은 요청/응답, action은 goal/feedback/result |
| launch와 shell script | launch는 여러 ROS node와 parameter, condition, namespace를 선언하는 ROS 실행 구성 |
| TF와 일반 topic | TF는 좌표계 사이의 시간 포함 변환 관계를 관리하는 특수한 데이터 흐름 |
