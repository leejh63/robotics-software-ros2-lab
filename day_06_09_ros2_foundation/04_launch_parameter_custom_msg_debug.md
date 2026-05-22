# 04. Launch, Parameter, Custom Message, Debug

## 한 줄 결론

Launch는 여러 노드를 한 번에 켜는 파일이고, Parameter는 노드 동작을 외부에서 바꾸는 설정값이며, Custom Message는 기본 메시지로 표현하기 어려운 데이터를 구조화하는 방법이다.

---

## 1. Launch는 단순 명령어 모음이 아니다

Launch 파일은 ROS graph를 구성하는 선언 파일에 가깝다.

```text
어떤 package의 어떤 executable을 실행할지
node 이름을 무엇으로 바꿀지
parameter YAML을 적용할지
조건에 따라 실행할지
namespace/remap을 줄지
```

이번 코드의 launch 파일:

```text
py_launch_example/launch/robot_ns_bring_launch.py
py_launch_example/launch/robot_ns_ep_launch.py
tf_pkg_lee/launch/tf_tree_demo_launch.py
tf_pkg_lee/launch/robot_ns_yolo_launch.py
```

---

## 2. lee_bring_launch.py 해석

`lee_bring_launch.py`는 카메라 처리 노드들을 한 번에 실행한다.

실행되는 노드:

| package | executable | launch name | 역할 |
|---|---|---|---|
| `camera_pkg` | `image_pub1` | `image_publisher_l` | `/image_raw0` 발행 |
| `camera_pkg` | `image_yolo1` | `image_yolo_l` | `/image_yolo1` 발행 |
| `camera_pkg` | `image_edge1` | `img_canny_l` | `/image_edge1` 발행 |
| `rqt_image_view` | `rqt_image_view` | `rqt_image_view_l` | 조건부 GUI 실행 |

중요한 구조:

```python
use_rviz_arg = DeclareLaunchArgument(
    'use_rviz',
    default_value='false',
    description='Run rqt_image_view',
)
```

이 이름은 `use_rviz`지만 실제로 실행하는 것은 `rqt_image_view`다. 학습 코드에서는 이름이 완벽하지 않을 수 있으므로, 문서화할 때는 “RViz”가 아니라 “rqt_image_view 조건 실행”으로 보는 게 정확하다.

---

## 3. lee_ep_launch.py와 parameter YAML

`lee_ep_launch.py`는 `camera_pkg/config/pub_cam_params.yaml`을 `image_pub1` 노드에 적용한다.

```python
config = os.path.join(
    get_package_share_directory('camera_pkg'),
    'config',
    'pub_cam_params.yaml'
)

image_publisher = Node(
    package='camera_pkg',
    executable='image_pub1',
    name='test',
    parameters=[config]
)
```

여기서 중요한 점은 node 이름을 `test`로 바꾼다는 것이다.

따라서 YAML도 이렇게 되어 있다.

```yaml
test:
  ros__parameters:
    publish_rate: 10.0
    topic_name: "what"
    image_size: [320, 240]
```

ROS2 parameter YAML은 보통 아래 구조를 따른다.

```yaml
node_name:
  ros__parameters:
    parameter_name: value
```

node 이름과 YAML 최상위 키가 다르면 parameter가 적용되지 않을 수 있다.

---

## 4. imagePlee.py의 parameter 해석

`imagePlee.py`는 세 가지 parameter를 선언한다.

```python
self.declare_parameter('publish_rate', 15.0)
self.declare_parameter('topic_name', 'image_raw0')
self.declare_parameter('image_size', [640, 480])
```

역할:

| parameter | 의미 | 현재 코드에서의 사용 |
|---|---|---|
| `publish_rate` | 이미지 발행 주기 | timer 주기 변경에 사용 |
| `topic_name` | 발행 topic 이름으로 의도된 값 | 현재 publisher는 `image_raw0` 고정이라 실제 미사용 |
| `image_size` | resize 크기 | `cv2.resize(frame, tuple(self.size))`에 사용 |

주의할 점은 현재 코드에서 publisher가 아래처럼 고정되어 있다는 점이다.

```python
self.publisher_ = self.create_publisher(Image, 'image_raw0', 10)
# self.publisher_ = self.create_publisher(Image, self.topic, 10)
```

따라서 YAML에서 `topic_name: "what"`을 줘도 실제 발행 topic은 바뀌지 않는다. 이건 코드 수정 대상이 아니라, 현재 문서에서는 “학습 중 상태에서 관찰할 점”으로 기록한다.

---

## 5. parameter를 런타임에 바꾸는 흐름

`imagePlee.py`에는 parameter callback이 있다.

```python
self.add_on_set_parameters_callback(self.parameter_callback)
```

`publish_rate`가 바뀌면 기존 timer를 취소하고 새 timer를 만든다.

```python
self.timer.cancel()
self.timer = self.create_timer(1.0 / self.rate, self.timer_callback)
```

실습 명령 예시:

```bash
ros2 param list /test
ros2 param get /test publish_rate
ros2 param set /test publish_rate 5.0
ros2 param set /test image_size "[320, 240]"
```

node 이름이 launch에서 `test`로 바뀌었으면 `/image_publisher1`가 아니라 `/test`를 대상으로 확인해야 한다.

---

## 6. Custom message가 필요한 이유

YOLO 결과를 문자열로 보내는 것도 가능은 하다.

```text
"person 0.91 [10, 20, 100, 200]"
```

하지만 이렇게 보내면 subscriber가 다시 문자열을 파싱해야 하고, bbox나 confidence의 타입 안정성이 없다.

그래서 `my_if/msg/ObjectDetection.msg`를 정의했다.

```text
string class_name
float64 confidence
int32[4] bbox
```

그리고 여러 detection을 묶기 위해 `ObjectDetectionArray.msg`를 만들었다.

```text
std_msgs/Header header
ObjectDetection[] detections
```

이 구조 덕분에 `camera_pkg/imgYOLOlee.py`는 detection 결과를 명확한 타입으로 발행할 수 있고, `tf_pkg_lee/tf_broad_yolo.py`는 그 메시지를 받아 TF frame으로 바꿀 수 있다.

---

## 7. Interface build 흐름

`my_if`는 `rosidl_generate_interfaces()`로 msg/srv/action 코드를 생성한다.

```text
.msg/.srv/.action 파일 작성
  -> CMakeLists.txt에 등록
  -> package.xml에 rosidl 의존성 선언
  -> colcon build
  -> install/setup.bash source
  -> Python/C++에서 import 가능
```

중요한 점:

```text
interface 파일을 수정한 뒤에는 다시 build해야 한다.
source install/setup.bash도 다시 해야 한다.
```

그렇지 않으면 Python에서 새 필드가 보이지 않거나 import 오류가 발생할 수 있다.

---

## 8. Debug 명령어

### package/executable 확인

```bash
ros2 pkg executables camera_pkg
ros2 pkg executables this_test
ros2 pkg executables my_robot_service
ros2 pkg executables my_robot_action
```

### node/topic 확인

```bash
ros2 node list
ros2 topic list
ros2 topic info /image_raw0
ros2 topic echo /img_yolo1
```

### parameter 확인

```bash
ros2 param list /test
ros2 param dump /test
ros2 param get /test publish_rate
```

### interface 확인

```bash
ros2 interface show my_if/msg/ObjectDetection
ros2 interface show my_if/msg/ObjectDetectionArray
ros2 interface show my_if/srv/AddTwoNum
ros2 interface show my_if/action/Movelee
```

### service/action 확인

```bash
ros2 service list
ros2 service type /add_two_num1
ros2 service call /add_two_num1 my_if/srv/AddTwoNum "{num1: 5, num2: 10}"

ros2 action list
ros2 action info /move_robot1
ros2 action send_goal /move_robot1 my_if/action/Movelee "{target_distance: 5.0}" --feedback
```

---

## 9. Launch에서 자주 헷갈리는 것

| 헷갈리는 부분 | 설명 |
|---|---|
| `package` | 실행할 executable이 들어 있는 ROS2 package 이름 |
| `executable` | `setup.py`나 `CMakeLists.txt`에서 등록한 실행 이름 |
| `name` | 실행 후 ROS graph에 보이는 node 이름. 코드 내부 이름을 덮어쓸 수 있음 |
| `parameters` | YAML 파일이나 dict로 넘기는 parameter |
| `condition` | 특정 launch argument가 true일 때만 실행 |
| `LaunchConfiguration` | 실행 시 바꿀 수 있는 argument 값 |
| `get_package_share_directory` | install/share 아래에 설치된 패키지 리소스 경로 찾기 |

---

## 10. 핵심 기억

```text
launch는 여러 노드를 한 번에 켜는 도구다.
parameter는 코드 수정 없이 노드 동작을 바꾸는 설정값이다.
custom message는 문자열 대신 구조화된 데이터를 주고받기 위한 타입이다.
node name을 launch에서 바꾸면 parameter YAML의 최상위 키도 그 이름에 맞아야 한다.
```
