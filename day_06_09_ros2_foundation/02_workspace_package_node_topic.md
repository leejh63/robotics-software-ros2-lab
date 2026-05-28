# 02. Workspace, Package, Node, Topic 구분

## 한 줄 결론

ROS2에서 가장 먼저 잡아야 할 것은 이름 체계다. `workspace`, `package`, `source file`, `executable`, `node`, `topic`, `message type`, `frame`, `namespace`는 모두 다른 개념이다.

---

## 1. 실제 workspace 구조

이번 코드의 기준 workspace는 아래 구조다.

```text
projects/ros2_foundation_lab/
├── src/
│   ├── ros2_topic_examples/
│   ├── ros2_cpp_examples/
│   ├── ros2_foundation_interfaces/
│   ├── ros2_service_examples/
│   ├── ros2_action_examples/
│   ├── ros2_camera_examples/
│   ├── ros2_launch_examples/
│   └── ros2_tf_examples/
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

새 터미널을 열면 다시 source 해야 한다. source를 안 하면 `ros2 run ros2_camera_examples image_publisher` 같은 명령이 실패할 수 있다.

---

## 3. package와 build type

| package | build type | 등록 방식 |
|---|---|---|
| `ros2_topic_examples` | `ament_python` | `setup.py`의 `console_scripts` |
| `ros2_camera_examples` | `ament_python` | `setup.py`의 `console_scripts` |
| `ros2_service_examples` | `ament_python` | `setup.py`의 `console_scripts` |
| `ros2_action_examples` | `ament_python` | `setup.py`의 `console_scripts` |
| `ros2_launch_examples` | `ament_python` | `setup.py`의 `data_files`에 launch 설치 |
| `ros2_tf_examples` | `ament_python` | `setup.py`의 `console_scripts`와 launch 설치 |
| `ros2_cpp_examples` | `ament_cmake` | `CMakeLists.txt`의 `add_executable`와 `install` |
| `ros2_foundation_interfaces` | `ament_cmake` | `rosidl_generate_interfaces` |

Python 노드 패키지라고 해서 무조건 `ament_python`만 쓰는 것은 아니지만, 이번 실습에서는 Python 실행 노드는 대부분 `ament_python`이다. 반대로 custom msg/srv/action을 만드는 `ros2_foundation_interfaces`는 `ament_cmake` 구조다.

---

## 4. source file, executable, node name의 차이

### Python 예시

`ros2_topic_examples/setup.py`에는 아래 실행 이름이 등록되어 있다.

```python
'string_talker = ros2_topic_examples.string_talker:main'
'string_listener = ros2_topic_examples.string_listener:main'
'turtle_square = ros2_topic_examples.turtle_square:main'
```

따라서 실행은 이렇게 한다.

```bash
ros2 run ros2_topic_examples string_talker
ros2 run ros2_topic_examples string_listener
ros2 run ros2_topic_examples turtle_square
```

하지만 실제 node 이름은 source file 안에서 정해진다.

| source file | executable | node name | topic |
|---|---|---|---|
| `string_talker.py` | `string_talker` | `string_talker` | `chatter` publish |
| `string_listener.py` | `string_listener` | `string_listener` | `chatter` subscribe |
| `turtle_square.py` | `turtle_square` | `turtle_square` | `/turtle1/cmd_vel` publish |

즉 아래는 모두 다르다.

```text
file name  : string_talker.py
executable : string_talker
node name  : string_talker
topic name : chatter
```

### C++ 예시

`ros2_cpp_examples/CMakeLists.txt`에는 아래처럼 executable이 등록되어 있다.

```cmake
add_executable(cpp_talker src/cpp_talker.cpp)
add_executable(cpp_listener src/cpp_listener.cpp)
install(TARGETS cpp_talker cpp_listener DESTINATION lib/${PROJECT_NAME})
```

실행은 이렇게 한다.

```bash
ros2 run ros2_cpp_examples cpp_talker
ros2 run ros2_cpp_examples cpp_listener
```

C++ source 안의 node 이름은 아래처럼 별도로 정해진다.

```cpp
Talker() : Node("cpp_talker")
Listener() : Node("cpp_listener")
```

---

## 5. Topic과 message type

Topic은 데이터가 흐르는 채널 이름이고, message type은 데이터 구조다.

| topic | message type | 발행/구독 예시 |
|---|---|---|
| `chatter` | `std_msgs/msg/String` | `ros2_topic_examples/string_talker.py` -> `ros2_topic_examples/string_listener.py` |
| `cpp_chatter` | `std_msgs/msg/String` | `ros2_cpp_examples/cpp_talker.cpp` -> `ros2_cpp_examples/cpp_listener.cpp` |
| `/turtle1/cmd_vel` | `geometry_msgs/msg/Twist` | `ros2_topic_examples/turtle_square.py` |
| `/image_raw` | `sensor_msgs/msg/Image` | `ros2_camera_examples/image_publisher.py` |
| `/image_edge` | `sensor_msgs/msg/Image` | `ros2_camera_examples/image_edge_publisher.py` |
| `/image_yolo` | `sensor_msgs/msg/Image` | `ros2_camera_examples/yolo_image_publisher.py` |
| `/yolo_detections` | `ros2_foundation_interfaces/msg/ObjectDetectionArray` | `ros2_camera_examples/yolo_detection_publisher.py` |
| `/tf` | `tf2_msgs/msg/TFMessage` | `ros2_tf_examples` 관련 노드 |
| `/tf_static` | `tf2_msgs/msg/TFMessage` | static transform publisher |

Publisher와 Subscriber는 topic 이름만 같아서는 부족하다. message type도 같아야 한다.

---

## 6. Node name은 launch에서 바뀔 수 있다

`ros2_camera_examples/image_publisher.py` 내부 node 이름은 다음과 같다.

```python
super().__init__('image_publisher')
```

하지만 `ros2_launch_examples/launch/camera_yolo_pipeline.launch.py`에서는 아래처럼 실행한다.

```python
Node(
    package='ros2_camera_examples',
    executable='image_publisher',
    name='test',
    parameters=[config]
)
```

이 경우 실행 중 node 이름은 `/test`가 된다. 따라서 parameter YAML도 `test:` 아래에 들어가야 적용된다.

`ros2_camera_examples/config/pub_cam_params.yaml`은 아래 구조다.

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

`image_publisher.py`는 `/image_raw` topic으로 `sensor_msgs/Image`를 발행한다. 그런데 메시지 안의 `header.frame_id`는 `camera_link`다.

```text
topic name : /image_raw
message    : sensor_msgs/msg/Image
frame_id   : camera_link
```

이 둘을 섞으면 안 된다.

| 구분 | 예시 | 의미 |
|---|---|---|
| topic | `/image_raw` | 이미지 데이터가 흘러가는 채널 |
| frame | `camera_link` | 이 이미지가 어느 좌표계 기준 센서에서 왔는지 나타내는 이름 |
| TF | `base_link -> camera_link` | 좌표계 사이의 위치/자세 관계 |

RViz나 TF 기반 알고리즘은 topic만 보는 것이 아니라 `header.frame_id`와 TF tree도 같이 본다.

---

## 8. namespace

namespace는 이름 앞에 붙는 접두어다.

예시:

```text
/image_raw -> /robot1/image_raw
/cmd_vel    -> /robot_ns/cmd_vel
/scan       -> /robot_ns/scan
```

이번 Day 06~09 코드에서는 namespace가 아주 강하게 쓰이지는 않았지만, Day 10~13의 Gazebo/SLAM/AMCL/Nav2에서는 `/robot_ns` namespace 때문에 action/topic/service 이름이 바뀌는 문제가 계속 중요해진다.

---

## 9. 확인 명령어

```bash
# package 확인
ros2 pkg list | grep ros2_camera_examples
ros2 pkg executables ros2_camera_examples

# node 확인
ros2 node list
ros2 node info /test

# topic 확인
ros2 topic list
ros2 topic info /image_raw
ros2 topic echo /yolo_detections

# service/action 확인
ros2 service list
ros2 service type /add_two_num
ros2 action list
ros2 action info /move_robot
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
