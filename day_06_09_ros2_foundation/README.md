# Day 06~09 ROS2 Foundation README

이 폴더는 `$ROS2_WS/src`에 들어 있는 실제 ROS2 학습 코드를 기준으로, ROS2의 기본 실행 구조를 다시 정리한 문서 묶음이다.

이 문서 묶음의 방향은 포트폴리오용 설명이 아니라, ROS2 기본기를 실제 실습 흐름과 연결하는 것이다. 목표는 아래에 가깝다.

```text
내가 작성하거나 실행한 ROS2 패키지를 기준으로
workspace / package / executable / node / topic / service / action / launch / parameter / TF / rosbag을
초보자도 다시 따라갈 수 있게 정리한다.
```

---

## 1. 이 폴더에서 다루는 실제 코드

주요 기준 코드는 `$SOURCE_ARCHIVE` 안의 아래 경로다.

```text
$ROS2_WS/src/
├── this_test/          # Python pub/sub, turtlesim cmd_vel parameter 실습
├── lee_pkg/            # C++ pub/sub 실습
├── my_if/              # msg/srv/action custom interface 정의
├── my_robot_service/   # AddTwoNum, LedControl service server/client
├── my_robot_action/    # Movelee action server/client
├── camera_pkg/         # camera image, Canny, snapshot service, YOLO image/msg
├── py_launch_example/  # camera 관련 노드 launch 묶음
└── tf_pkg_example/         # TF tree, TF listener, YOLO detection -> object TF
```

Day 06~09는 뒤쪽 Gazebo/SLAM/AMCL/Nav2로 넘어가기 전의 기반이다. 그래서 이 폴더에서는 큰 알고리즘보다 아래 질문을 우선한다.

```text
이 파일은 어떤 package에 속하는가?
이 파일은 어떤 executable로 실행되는가?
실행되면 node 이름은 무엇인가?
어떤 topic/service/action을 만들거나 사용하는가?
message type은 무엇인가?
launch 파일이 이 노드들을 어떤 조합으로 띄우는가?
parameter가 실제 코드 동작을 어떻게 바꾸는가?
TF frame 이름이 topic 이름과 어떻게 다른가?
```

---

## 2. 문서 구성

```text
day_06_09_ros2_foundation/
├── README.md
├── 00_source_package_map.md
├── 01_overview_reading_order.md
├── 02_workspace_package_node_topic.md
├── 03_pubsub_service_action_interface.md
├── 04_launch_parameter_custom_msg_debug.md
├── 05_tf2_sensor_rosbag_foundation.md
├── 06_camera_yolo_tf_flow.md
├── 07_connection_to_day10_13.md
├── 08_ros2_execution_model_from_code.md
├── 09_runtime_observations_without_code_changes.md
├── 10_day06_09_review_questions.md
├── background/
│   ├── ros2_name_resolution_and_namespace.md
│   └── qos_callback_executor_lifecycle_minimum.md
├── commands/
│   ├── ros2_foundation_commands.md
│   ├── launch_parameter_debug_commands.md
│   └── tf2_rosbag_sensor_commands.md
└── troubleshooting/
    └── ros2_foundation_troubleshooting.md
```

---

## 3. 추천 읽는 순서

처음 볼 때는 아래 순서가 좋다.

```text
1. 00_source_package_map.md
2. 01_overview_reading_order.md
3. 02_workspace_package_node_topic.md
4. 03_pubsub_service_action_interface.md
5. 04_launch_parameter_custom_msg_debug.md
6. 05_tf2_sensor_rosbag_foundation.md
7. 06_camera_yolo_tf_flow.md
8. 08_ros2_execution_model_from_code.md
9. 09_runtime_observations_without_code_changes.md
10. 10_day06_09_review_questions.md
```

명령어만 다시 확인할 때는 `commands/`를 보면 된다. 실행 중 막히면 `troubleshooting/ros2_foundation_troubleshooting.md`를 먼저 본다.

---

## 4. 핵심 결론

ROS2 초반 실습에서 가장 중요한 것은 “코드 한 파일”이 아니라, **그 파일이 ROS graph 안에서 어떤 이름으로 실행되고 어떤 통신을 만드는가**다.

예를 들어 `camera_pkg/camera_pkg/imagePlee.py`는 그냥 웹캠 코드가 아니다.

```text
package      : camera_pkg
source file  : camera_pkg/imagePlee.py
executable   : image_pub1
node name    : image_publisher1 또는 launch에서 name='test'
publish topic: /image_raw0
message type : sensor_msgs/msg/Image
frame_id     : camera_frame
parameter    : publish_rate, topic_name, image_size
```

이런 식으로 봐야 Day 10~13에서 아래 문제를 해석할 수 있다.

```text
Gazebo plugin이 /scan을 발행했는데 RViz에 안 보임
SLAM Toolbox가 /scan을 못 읽음
AMCL particle이 안 보임
Nav2 Goal 버튼을 눌러도 action이 연결되지 않음
TF tree가 끊겨서 map/odom/base_link가 연결되지 않음
```

대부분의 문제는 알고리즘 이전에 이름, 타입, namespace, parameter, TF, lifecycle에서 먼저 발생한다.
