# 02. Workspace, Package, Node, Topic 구분

## 한 줄 결론

ROS2에서 가장 먼저 잡아야 할 것은 이름 체계다. `workspace`, `package`, `source file`, `executable`, `node`, `topic`, `message type`, `frame`, `namespace`는 모두 다른 개념이다.

---

## 1. 실제 workspace 구조

이번 코드의 기준 workspace는 아래 구조다.

```text
$ROS2_WS/
├── src/
│   ├── this_test/
│   ├── lee_pkg/
│   ├── my_if/
│   ├── my_robot_service/
│   ├── my_robot_action/
│   ├── camera_pkg/
│   ├── py_launch_example/
│   └── tf_pkg_example/
├── build/      # colcon build 결과
├── install/    # ros2 run/launch가 찾는 설치 결과
└── log/        # build 로그
```

`ros2 run`과 `ros2 launch`는 보통 `src`의 파일을 직접 실행하는 느낌이 아니다. `colcon build` 후 `install/`에 등록된 package/executable 정보를 기준으로 찾는다.

---

## 2. source 명령의 의미

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
```

| 명령 | 의미 |
|---|---|
| `source /opt/ros/humble/setup.bash` | ROS2 Humble 기본 패키지를 현재 터미널에서 찾게 함 |
| `source install/setup.bash` | 현재 workspace에서 빌드한 패키지를 현재 터미널에서 찾게 함 |

새 터미널을 열면 다시 source 해야 한다. source를 안 하면 `ros2 run camera_pkg image_pub1` 같은 명령이 실패할 수 있다.

---

## 3. package와 build type

| package | build type | 등록 방식 |
|---|---|---|
| `this_test` | `ament_python` | `setup.py`의 `console_scripts` |
| `camera_pkg` | `ament_python` | `setup.py`의 `console_scripts` |
| `my_robot_service` | `ament_python` | `setup.py`의 `console_scripts` |
| `my_robot_action` | `ament_python` | `setup.py`의 `console_scripts` |
| `py_launch_example` | `ament_python` | `setup.py`의 `data_files`에 launch 설치 |
| `tf_pkg_example` | `ament_python` | `setup.py`의 `console_scripts`와 launch 설치 |
| `lee_pkg` | `ament_cmake` | `CMakeLists.txt`의 `add_executable`와 `install` |
| `my_if` | `ament_cmake` | `rosidl_generate_interfaces` |

Python 노드 패키지라고 해서 무조건 `ament_python`만 쓰는 것은 아니지만, 이번 실습에서는 Python 실행 노드는 대부분 `ament_python`이다. 반대로 custom msg/srv/action을 만드는 `my_if`는 `ament_cmake` 구조다.

---

## 4. source file, executable, node name의 차이

### Python 예시

`this_test/setup.py`에는 아래 실행 이름이 등록되어 있다.

```python
'lee_node = this_test.test:main'
'lee_node2 = this_test.listener:main'
'lee_node3 = this_test.ssss:main'
```

따라서 실행은 이렇게 한다.

```bash
ros2 run this_test lee_node
ros2 run this_test lee_node2
ros2 run this_test lee_node3
```

하지만 실제 node 이름은 source file 안에서 정해진다.

| source file | executable | node name | topic |
|---|---|---|---|
| `test.py` | `lee_node` | `talker` | `user_ns` publish |
| `listener.py` | `lee_node2` | `listener` | `user_ns` subscribe |
| `ssss.py` | `lee_node3` | `turtle_square` | `/turtle3/cmd_vel` publish |

즉 아래는 모두 다르다.

```text
file name  : test.py
executable : lee_node
node name  : talker
topic name : user_ns
```

### C++ 예시

`lee_pkg/CMakeLists.txt`에는 아래처럼 executable이 등록되어 있다.

```cmake
add_executable(talker src/cpp_test1.cpp)
add_executable(listener src/cpp_test2.cpp)
install(TARGETS talker listener DESTINATION lib/${PROJECT_NAME})
```

실행은 이렇게 한다.

```bash
ros2 run lee_pkg talker
ros2 run lee_pkg listener
```

C++ source 안의 node 이름은 아래처럼 별도로 정해진다.

```cpp
Talker() : Node("talker1")
Listener() : Node("listener")
```

---

## 5. Topic과 message type

Topic은 데이터가 흐르는 채널 이름이고, message type은 데이터 구조다.

| topic | message type | 발행/구독 예시 |
|---|---|---|
| `user_ns` | `std_msgs/msg/String` | `this_test/test.py` -> `this_test/listener.py` |
| `cpp_1` | `std_msgs/msg/String` | `lee_pkg/cpp_test1.cpp` -> `lee_pkg/cpp_test2.cpp` |
| `/turtle3/cmd_vel` | `geometry_msgs/msg/Twist` | `this_test/ssss.py` |
| `/image_raw0` | `sensor_msgs/msg/Image` | `camera_pkg/imagePlee.py` |
| `/image_edge1` | `sensor_msgs/msg/Image` | `camera_pkg/imageOPENlee.py` |
| `/image_yolo1` | `sensor_msgs/msg/Image` | `camera_pkg/imageYOLOlee.py` |
| `/img_yolo1` | `my_if/msg/ObjectDetectionArray` | `camera_pkg/imgYOLOlee.py` |
| `/tf` | `tf2_msgs/msg/TFMessage` | `tf_pkg_example` 관련 노드 |
| `/tf_static` | `tf2_msgs/msg/TFMessage` | static transform publisher |

Publisher와 Subscriber는 topic 이름만 같아서는 부족하다. message type도 같아야 한다.

---

## 6. Node name은 launch에서 바뀔 수 있다

`camera_pkg/imagePlee.py` 내부 node 이름은 다음과 같다.

```python
super().__init__('image_publisher1')
```

하지만 `py_launch_example/launch/robot_ns_ep_launch.py`에서는 아래처럼 실행한다.

```python
Node(
    package='camera_pkg',
    executable='image_pub1',
    name='test',
    parameters=[config]
)
```

이 경우 실행 중 node 이름은 `/test`가 된다. 따라서 parameter YAML도 `test:` 아래에 들어가야 적용된다.

현재 `camera_pkg/config/pub_cam_params.yaml`은 아래 구조다.

```yaml
test:
  ros__parameters:
    publish_rate: 10.0
    topic_name: "what"
    image_size: [320, 240]
```

이것은 launch에서 node name을 `test`로 바꾸는 구조와 맞물린다.

---

## 7. topic 이름과 frame 이름은 다르다

`imagePlee.py`는 `/image_raw0` topic으로 `sensor_msgs/Image`를 발행한다. 그런데 메시지 안의 `header.frame_id`는 `camera_frame`다.

```text
topic name : /image_raw0
message    : sensor_msgs/msg/Image
frame_id   : camera_frame
```

이 둘을 섞으면 안 된다.

| 구분 | 예시 | 의미 |
|---|---|---|
| topic | `/image_raw0` | 이미지 데이터가 흘러가는 채널 |
| frame | `camera_frame` | 이 이미지가 어느 좌표계 기준 센서에서 왔는지 나타내는 이름 |
| TF | `base_link_robot_ns -> camera_frame` | 좌표계 사이의 위치/자세 관계 |

RViz나 TF 기반 알고리즘은 topic만 보는 것이 아니라 `header.frame_id`와 TF tree도 같이 본다.

---

## 8. namespace

namespace는 이름 앞에 붙는 접두어다.

예시:

```text
/image_raw0 -> /robot1/image_raw0
/cmd_vel    -> /robot_ns/cmd_vel
/scan       -> /robot_ns/scan
```

이번 Day 06~09 코드에서는 namespace가 아주 강하게 쓰이지는 않았지만, Day 10~13의 Gazebo/SLAM/AMCL/Nav2에서는 `/robot_ns` namespace 때문에 action/topic/service 이름이 바뀌는 문제가 계속 중요해진다.

---

## 9. 확인 명령어

```bash
# package 확인
ros2 pkg list | grep camera_pkg
ros2 pkg executables camera_pkg

# node 확인
ros2 node list
ros2 node info /test

# topic 확인
ros2 topic list
ros2 topic info /image_raw0
ros2 topic echo /img_yolo1

# service/action 확인
ros2 service list
ros2 service type /add_two_num1
ros2 action list
ros2 action info /move_robot1
```

---

## 10. 핵심 기억

```text
package는 빌드/배포 단위다.
executable은 ros2 run에서 부르는 실행 이름이다.
node는 실행 중 ROS graph에 등록되는 프로세스 이름이다.
topic은 데이터 채널이다.
message type은 topic으로 흐르는 데이터 구조다.
frame은 좌표계 이름이다.
namespace는 이름 앞에 붙는 접두어다.
```
