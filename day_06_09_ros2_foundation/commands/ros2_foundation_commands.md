# ROS2 Foundation 명령어 정리

## 1. 기본 build/source

```bash
cd $ROS2_WS
colcon build --symlink-install
source /opt/ros/humble/setup.bash
source install/setup.bash
```

패키지 하나만 다시 빌드할 때:

```bash
colcon build --symlink-install --packages-select camera_pkg
source install/setup.bash
```

interface 패키지를 고친 뒤에는 의존 패키지도 다시 빌드하는 것이 안전하다.

```bash
colcon build --symlink-install --packages-select my_if camera_pkg tf_pkg_example my_robot_service my_robot_action
source install/setup.bash
```

---

## 2. package / executable 확인

```bash
ros2 pkg list | grep -E 'this_test|lee_pkg|my_if|camera_pkg|tf_pkg_example'
ros2 pkg executables this_test
ros2 pkg executables lee_pkg
ros2 pkg executables camera_pkg
ros2 pkg executables my_robot_service
ros2 pkg executables my_robot_action
ros2 pkg executables tf_pkg_example
```

---

## 3. Python topic 실습

터미널 1:

```bash
ros2 run this_test lee_node
```

터미널 2:

```bash
ros2 run this_test lee_node2
```

확인:

```bash
ros2 node list
ros2 topic list
ros2 topic info /user_ns
ros2 topic echo /user_ns
```

---

## 4. C++ topic 실습

터미널 1:

```bash
ros2 run lee_pkg talker
```

터미널 2:

```bash
ros2 run lee_pkg listener
```

확인:

```bash
ros2 topic info /cpp_1
ros2 topic echo /cpp_1
```

---

## 5. turtlesim cmd_vel 실습

터미널 1:

```bash
ros2 run turtlesim turtlesim_node
ros2 service call /spawn turtlesim/srv/Spawn "{x: 5.5, y: 5.5, theta: 0.0, name: 'turtle3'}"
```

터미널 2:

```bash
ros2 run this_test lee_node3
```

parameter 확인/변경:

```bash
ros2 param list /turtle_square
ros2 param get /turtle_square test_val
ros2 param set /turtle_square test_val 1.0
```

---

## 6. Service 실습

AddTwoNum:

```bash
ros2 run my_robot_service add_server1
ros2 run my_robot_service add_client1
ros2 service call /add_two_num1 my_if/srv/AddTwoNum "{num1: 5, num2: 10}"
```

LedControl:

```bash
ros2 run my_robot_service led_server1
ros2 run my_robot_service led_client1
ros2 service call /set_led1 my_if/srv/LedControl "{state: true}"
ros2 service call /set_led1 my_if/srv/LedControl "{state: false}"
```

---

## 7. Action 실습

터미널 1:

```bash
ros2 run my_robot_action move_server1
```

터미널 2:

```bash
ros2 run my_robot_action move_client1
```

CLI로 직접 goal 보내기:

```bash
ros2 action list
ros2 action info /move_robot1
ros2 action send_goal /move_robot1 my_if/action/Movelee "{target_distance: 5.0}" --feedback
```

---

## 8. Interface 확인

```bash
ros2 interface show my_if/msg/ObjectDetection
ros2 interface show my_if/msg/ObjectDetectionArray
ros2 interface show my_if/srv/AddTwoNum
ros2 interface show my_if/srv/LedControl
ros2 interface show my_if/action/Movelee
```

---

## 9. Camera pipeline 실행

카메라 발행:

```bash
ros2 run camera_pkg image_pub1
```

Canny edge:

```bash
ros2 run camera_pkg image_edge1
```

YOLO image:

```bash
ros2 run camera_pkg image_yolo1
```

YOLO custom message:

```bash
ros2 run camera_pkg yolo_pub_l
```

snapshot service:

```bash
ros2 run camera_pkg image_proc1
ros2 param set /image_processor1 snapshot_target yolo
ros2 service call /capture_snapshot1 std_srvs/srv/Trigger "{}"
```

확인:

```bash
ros2 topic info /image_raw0
ros2 topic info /image_edge1
ros2 topic info /image_yolo1
ros2 topic info /img_yolo1
ros2 topic echo /img_yolo1 --once
```

---

## 10. Launch 실행

```bash
ros2 launch py_launch_example lee_bring_launch.py
ros2 launch py_launch_example lee_bring_launch.py use_rviz:=true

ros2 launch py_launch_example lee_ep_launch.py
ros2 launch py_launch_example lee_ep_launch.py use_rviz:=true
```

`use_rviz` 이름이지만 실제로는 `rqt_image_view` 조건 실행이다.
