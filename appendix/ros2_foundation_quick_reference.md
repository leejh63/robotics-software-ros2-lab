# ROS2 기초 빠른 참조

## 이름 구분

| 구분 | 예시 | 확인 명령 |
|---|---|---|
| workspace | `$ROS2_WS` | `pwd` |
| package | `ros2_camera_examples` | `ros2 pkg list` |
| executable | `image_publisher` | `ros2 pkg executables ros2_camera_examples` |
| node | `/image_publisher1`, `/test` | `ros2 node list` |
| topic | `/image_raw0` | `ros2 topic list` |
| service | `/add_two_num1` | `ros2 service list` |
| action | `/move_robot1` | `ros2 action list` |
| frame | `camera_frame` | `ros2 run tf2_tools view_frames` |
| parameter | `publish_rate` | `ros2 param list /node` |

## 실제 패키지 요약

| package | 핵심 |
|---|---|
| `ros2_topic_examples` | Python topic pub/sub, turtlesim cmd_vel |
| `ros2_cpp_examples` | C++ topic pub/sub |
| `ros2_foundation_interfaces` | custom msg/srv/action |
| `ros2_service_examples` | AddTwoNum, LedControl service |
| `ros2_action_examples` | MoveDistance action |
| `ros2_camera_examples` | Image, Canny, Snapshot, YOLO image/msg |
| `ros2_launch_examples` | launch/parameter 실습 |
| `ros2_tf_examples` | TF tree, listener, YOLO TF |

## 통신 선택 기준

| 상황 | 구조 |
|---|---|
| 계속 흐르는 센서/상태/명령 | Topic |
| 짧은 요청/응답 | Service |
| 오래 걸리는 목표 + feedback/result | Action |
| 새 데이터 구조 필요 | msg/srv/action interface |

## 필수 확인 명령

```bash
colcon build --symlink-install
source install/setup.bash
ros2 pkg executables <package>
ros2 node list
ros2 topic list
ros2 topic info <topic>
ros2 service list
ros2 action list
ros2 param list <node>
ros2 run tf2_tools view_frames
```
