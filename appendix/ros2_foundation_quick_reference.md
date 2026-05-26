# ROS2 기초 빠른 참조

## 이름 구분

| 구분 | 예시 | 확인 명령 |
|---|---|---|
| workspace | `$ROS2_WS` | `pwd` |
| package | `camera_pkg` | `ros2 pkg list` |
| executable | `image_pub1` | `ros2 pkg executables camera_pkg` |
| node | `/image_publisher1`, `/test` | `ros2 node list` |
| topic | `/image_raw0` | `ros2 topic list` |
| service | `/add_two_num1` | `ros2 service list` |
| action | `/move_robot1` | `ros2 action list` |
| frame | `camera_frame` | `ros2 run tf2_tools view_frames` |
| parameter | `publish_rate` | `ros2 param list /node` |

## 실제 패키지 요약

| package | 핵심 |
|---|---|
| `this_test` | Python pub/sub, turtlesim cmd_vel |
| `lee_pkg` | C++ pub/sub |
| `my_if` | custom msg/srv/action |
| `my_robot_service` | AddTwoNum, LedControl service |
| `my_robot_action` | Movelee action |
| `camera_pkg` | Image, Canny, Snapshot, YOLO image/msg |
| `py_launch_example` | launch/parameter 실습 |
| `tf_pkg_example` | TF tree, listener, YOLO TF |

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
