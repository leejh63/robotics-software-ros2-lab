# Day 06~09 ROS2 Foundation

이 폴더는 Day 06~09에서 진행한 ROS2 기본 실습을 정리한 문서 모음이다. 정리 기준은 실제로 작성한 ROS2 workspace 코드이며, `tranning/` 폴더의 자료는 개념 확인을 위한 참고 자료로만 사용했다.

실행 가능한 정리 코드는 아래 프로젝트 폴더에 둔다.

```text
projects/ros2_foundation_lab/
```

Day 10~15 구간은 이미 별도 문서와 프로젝트로 정리되어 있으므로, 이 문서에서는 Gazebo, SLAM, AMCL, Nav2로 넘어가기 전 필요한 ROS2 기본 구조를 다룬다.

---

## 1. 정리 기준

Day 06~09의 실습 코드는 ROS2 기초 요소를 기준으로 다시 묶었다. 공개용 정리본에서는 패키지 이름만 봐도 역할을 알 수 있도록 다음과 같이 구성했다.

| 패키지명 | 역할 |
|---|---|
| `ros2_topic_examples` | Python topic publisher/subscriber, turtlesim `cmd_vel` 실습 |
| `ros2_cpp_examples` | C++ topic publisher/subscriber 실습 |
| `ros2_foundation_interfaces` | custom msg/srv/action 정의 |
| `ros2_service_examples` | service server/client 실습 |
| `ros2_action_examples` | action server/client 실습 |
| `ros2_camera_examples` | camera, OpenCV, YOLO image/custom message 실습 |
| `ros2_launch_examples` | launch, parameter, pipeline 실행 실습 |
| `ros2_tf_examples` | TF tree, TF listener, object TF 변환 실습 |

원본 workspace의 임시 패키지명은 `09_runtime_notes.md`에 정리 과정 참고용으로만 남겼다.


## 2. 실제 코드 구조

```text
projects/ros2_foundation_lab/
├── README.md
├── .gitignore
└── src/
    ├── ros2_topic_examples/
    ├── ros2_cpp_examples/
    ├── ros2_foundation_interfaces/
    ├── ros2_service_examples/
    ├── ros2_action_examples/
    ├── ros2_camera_examples/
    ├── ros2_launch_examples/
    └── ros2_tf_examples/
```

이 구간에서 중요한 것은 코드 한 파일 자체보다, 그 파일이 ROS graph 안에서 어떤 이름과 통신 구조를 만드는지 확인하는 것이다.

```text
package는 무엇인가?
executable 이름은 무엇인가?
실행 후 node 이름은 무엇인가?
어떤 topic/service/action을 만들거나 사용하는가?
message type은 무엇인가?
launch 파일이 어떤 노드 조합을 실행하는가?
parameter가 실제 동작에 어떻게 반영되는가?
TF frame 이름과 topic 이름은 어떻게 구분되는가?
```

---

## 3. 문서 구성

```text
day_06_09_ros2_foundation/
├── README.md
├── 00_source_overview.md
├── 01_overview_reading_order.md
├── 02_workspace_package_node_topic.md
├── 03_pubsub_service_action_interface.md
├── 04_launch_parameter_custom_msg_debug.md
├── 05_tf2_sensor_rosbag_foundation.md
├── 06_camera_yolo_tf_flow.md
├── 07_connection_to_day10_13.md
├── 08_ros2_execution_model_from_code.md
├── 09_runtime_notes.md
├── 10_day06_09_review_questions.md
├── background/
├── commands/
└── troubleshooting/
```

처음 볼 때는 아래 순서가 좋다.

```text
1. 00_source_overview.md
2. 01_overview_reading_order.md
3. 02_workspace_package_node_topic.md
4. 03_pubsub_service_action_interface.md
5. 04_launch_parameter_custom_msg_debug.md
6. 05_tf2_sensor_rosbag_foundation.md
7. 06_camera_yolo_tf_flow.md
8. 08_ros2_execution_model_from_code.md
9. 09_runtime_notes.md
10. 10_day06_09_review_questions.md
```

명령어만 확인할 때는 `commands/`를 보면 된다. 실행 중 막히면 `troubleshooting/ros2_foundation_troubleshooting.md`를 먼저 확인한다.

---

## 4. 핵심 관점

ROS2 초반 실습에서 가장 중요한 것은 다음 구분이다.

```text
file name != executable name != node name != topic name
```

예를 들어 `ros2_camera_examples/ros2_camera_examples/image_publisher.py`는 단순한 웹캠 코드가 아니라 다음 구성을 가진 ROS2 node다.

```text
package      : ros2_camera_examples
source file  : ros2_camera_examples/image_publisher.py
executable   : image_publisher
node name    : image_publisher
publish topic: /image_raw
message type : sensor_msgs/msg/Image
frame_id     : camera_link
parameter    : publish_rate, topic_name, image_size, frame_id
```

이 관점을 잡아야 Day 10~15에서 만나는 SLAM, AMCL, Nav2 문제도 더 쉽게 추적할 수 있다. 대부분의 문제는 알고리즘 이전에 이름, 타입, namespace, parameter, TF, lifecycle에서 먼저 발생한다.
