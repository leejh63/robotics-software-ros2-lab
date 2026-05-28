# ROS2 Foundation 명령어 정리

이 문서는 `projects/ros2_foundation_lab` 기준 명령어를 정리한다.

## 1. build/source

```bash
cd projects/ros2_foundation_lab
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```

패키지 하나만 다시 빌드할 때:

```bash
colcon build --symlink-install --packages-select ros2_camera_examples
source install/setup.bash
```

interface 패키지를 고친 뒤에는 의존 패키지도 함께 다시 빌드하는 것이 안전하다.

```bash
colcon build --symlink-install --packages-select   ros2_foundation_interfaces   ros2_service_examples   ros2_action_examples   ros2_camera_examples   ros2_tf_examples
source install/setup.bash
```

---

## 2. package / executable 확인

```bash
ros2 pkg list | grep -E 'ros2_topic_examples|ros2_cpp_examples|ros2_foundation_interfaces|ros2_camera_examples|ros2_tf_examples'

ros2 pkg executables ros2_topic_examples
ros2 pkg executables ros2_cpp_examples
ros2 pkg executables ros2_service_examples
ros2 pkg executables ros2_action_examples
ros2 pkg executables ros2_camera_examples
ros2 pkg executables ros2_tf_examples
```

---

## 3. Python topic 실습

터미널 1:

```bash
ros2 run ros2_topic_examples string_talker
```

터미널 2:

```bash
ros2 run ros2_topic_examples string_listener
```

확인:

```bash
ros2 node list
ros2 topic list
ros2 topic echo /chatter
```

---

## 4. C++ topic 실습

터미널 1:

```bash
ros2 run ros2_cpp_examples cpp_talker
```

터미널 2:

```bash
ros2 run ros2_cpp_examples cpp_listener
```

확인:

```bash
ros2 topic info /cpp_chatter
ros2 topic echo /cpp_chatter
```

---

## 5. turtlesim cmd_vel 실습

터미널 1:

```bash
ros2 run turtlesim turtlesim_node
```

터미널 2:

```bash
ros2 run ros2_topic_examples turtle_square
```

parameter 확인/변경:

```bash
ros2 param list /turtle_square
ros2 param get /turtle_square cmd_vel_topic
ros2 param get /turtle_square linear_speed
ros2 param set /turtle_square linear_speed 1.0
ros2 param set /turtle_square repeat false
```

---

## 6. Service 실습

AddTwoNum:

```bash
ros2 run ros2_service_examples add_two_num_server
ros2 run ros2_service_examples add_two_num_client
ros2 service call /add_two_num ros2_foundation_interfaces/srv/AddTwoNum "{num1: 5, num2: 10}"
```

LedControl:

```bash
ros2 run ros2_service_examples led_service_server
ros2 run ros2_service_examples led_service_client
ros2 service call /set_led ros2_foundation_interfaces/srv/LedControl "{state: true}"
ros2 service call /set_led ros2_foundation_interfaces/srv/LedControl "{state: false}"
```

---

## 7. Action 실습

터미널 1:

```bash
ros2 run ros2_action_examples move_action_server
```

터미널 2:

```bash
ros2 run ros2_action_examples move_action_client
```

CLI로 직접 goal 보내기:

```bash
ros2 action list
ros2 action info /move_robot
ros2 action send_goal /move_robot ros2_foundation_interfaces/action/MoveDistance "{target_distance: 5.0}" --feedback
```

---

## 8. Interface 확인

```bash
ros2 interface show ros2_foundation_interfaces/msg/ObjectDetection
ros2 interface show ros2_foundation_interfaces/msg/ObjectDetectionArray
ros2 interface show ros2_foundation_interfaces/srv/AddTwoNum
ros2 interface show ros2_foundation_interfaces/srv/LedControl
ros2 interface show ros2_foundation_interfaces/action/MoveDistance
```

---

## 9. Camera pipeline 실행

카메라 발행:

```bash
ros2 run ros2_camera_examples image_publisher
```

Canny edge:

```bash
ros2 run ros2_camera_examples image_edge_publisher
```

YOLO image:

```bash
ros2 run ros2_camera_examples yolo_image_publisher
```

YOLO custom message:

```bash
ros2 run ros2_camera_examples yolo_detection_publisher
```

snapshot service:

```bash
ros2 run ros2_camera_examples image_processor
ros2 param set /image_processor snapshot_target yolo
ros2 service call /capture_snapshot std_srvs/srv/Trigger "{}"
```

확인:

```bash
ros2 topic info /image_raw
ros2 topic info /image_edge
ros2 topic info /image_yolo
ros2 topic info /yolo_detections
ros2 topic echo /yolo_detections --once
```

---

## 10. Launch 실행

```bash
ros2 launch ros2_launch_examples camera_pipeline.launch.py
ros2 launch ros2_launch_examples camera_pipeline.launch.py use_viewer:=true
ros2 launch ros2_launch_examples camera_yolo_pipeline.launch.py
ros2 launch ros2_launch_examples camera_yolo_pipeline.launch.py use_viewer:=true
```
