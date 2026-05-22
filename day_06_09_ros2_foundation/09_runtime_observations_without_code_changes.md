# 09. Runtime Observations Without Code Changes

이 문서는 코드를 수정하지 않고, 현재 학습 코드 상태에서 실행할 때 주의해야 할 부분만 정리한다. 지금 단계의 목적은 문제를 바로 고치는 것이 아니라, 이후 정리/실행할 때 헷갈리지 않도록 관찰점을 남기는 것이다.

---

## 1. package.xml 의존성 누락 가능성

### this_test

`this_test/this_test/ssss.py`는 아래 import를 사용한다.

```python
from geometry_msgs.msg import Twist
```

하지만 `this_test/package.xml`에는 현재 `geometry_msgs` 의존성이 보이지 않는다.

관찰:

```text
현재 환경에 geometry_msgs가 이미 설치되어 있으면 실행될 수 있다.
하지만 재현 가능한 패키지 기준으로는 package.xml에 geometry_msgs 의존성을 추가하는 것이 맞다.
```

### camera_pkg

`camera_pkg/imagePlee.py`는 아래 import를 사용한다.

```python
from rcl_interfaces.msg import SetParametersResult
```

`package.xml`에는 `rcl_interfaces`가 명시되어 있지 않다.

관찰:

```text
runtime에서 바로 터지지 않을 수도 있지만, 패키지 의존성 문서화 기준으로는 명시하는 것이 좋다.
```

### my_robot_action

`my_robot_action/package.xml`에 아래 의존성이 있다.

```xml
<depend>rclpy_action</depend>
```

코드에서는 실제로 다음을 쓴다.

```python
from rclpy.action import ActionClient
from rclpy.action import ActionServer
```

관찰:

```text
일반적으로 rclpy 안의 action API를 쓰는 구조이므로 rclpy가 핵심 의존성이다.
rclpy_action이라는 별도 의존성 명칭은 재검토 대상이다.
```

---

## 2. YOLO model_path 상대경로 문제

`imageYOLOlee.py`와 `imgYOLOlee.py`는 기본 model path를 아래처럼 둔다.

```python
self.declare_parameter('model_path', 'yolov8n.pt')
```

이 방식은 실행 위치에 따라 모델 파일을 찾지 못할 수 있다.

관찰:

```text
workspace 루트에서 실행하면 우연히 찾을 수 있다.
다른 디렉터리에서 launch/run하면 못 찾을 수 있다.
학습 정리 문서에서는 model_path를 parameter로 명시하는 습관을 같이 기록하는 것이 좋다.
```

확인 명령 예시:

```bash
ros2 run camera_pkg yolo_pub_l --ros-args -p model_path:=/absolute/path/to/yolov8n.pt
```

---

## 3. imagePlee.py의 topic_name parameter가 실제 publisher에 반영되지 않음

`imagePlee.py`는 parameter를 선언한다.

```python
self.declare_parameter('topic_name', 'image_raw0')
self.topic = self.get_parameter('topic_name').value
```

하지만 publisher는 현재 고정 topic을 쓴다.

```python
self.publisher_ = self.create_publisher(Image, 'image_raw0', 10)
# self.publisher_ = self.create_publisher(Image, self.topic, 10)
```

관찰:

```text
YAML에서 topic_name을 바꿔도 실제 발행 topic은 image_raw0 그대로다.
이건 코드 수정 대상이지만, 현재 문서 정리 범위에서는 수정하지 않는다.
```

---

## 4. py_launch_example의 config 설치 구조 점검 대상

`py_launch_example/setup.py`에는 아래 설치 규칙이 있다.

```python
(os.path.join('share', package_name, 'config'), glob('config/*.yaml'))
```

그런데 현재 `py_launch_example` 자체에 config 폴더가 보이지 않고, `lee_ep_launch.py`는 `camera_pkg`의 config를 사용한다.

```python
get_package_share_directory('camera_pkg')
```

관찰:

```text
실행 자체는 camera_pkg/config/pub_cam_params.yaml이 설치되어 있으면 가능하다.
다만 py_launch_example의 setup.py에 config 설치 규칙이 남아 있는 것은 학습 중 흔적으로 보인다.
```

---

## 5. launch의 use_rviz 이름과 실제 실행 프로그램

`py_launch_example/launch/robot_ns_bring_launch.py`에는 `use_rviz` argument가 있지만, 실제로 실행하는 것은 `rqt_image_view`다.

```python
viewer_node = Node(
    package='rqt_image_view',
    executable='rqt_image_view',
    condition=IfCondition(LaunchConfiguration('use_rviz')),
)
```

관찰:

```text
학습 중 이름을 편의상 use_rviz로 둔 것으로 보인다.
문서에서는 RViz가 아니라 rqt_image_view 조건 실행이라고 설명하는 것이 정확하다.
```

---

## 6. tf_pkg_example/robot_ns_yolo_launch.py의 RViz 절대경로

`lee_yolo_launch.py`에는 아래 절대경로가 들어 있다.

```python
arguments=['-d', '$ROS2_WS/rviz_conf_exap.rviz']
```

관찰:

```text
사용자 로컬 환경에서는 동작할 수 있다.
다른 컴퓨터나 다른 workspace 경로에서는 깨질 수 있다.
이후 정리할 때는 RViz config를 패키지 share에 넣고 get_package_share_directory()로 찾는 방식이 좋다.
```

---

## 7. frame 이름 혼용 가능성

코드 안에는 아래 frame 이름들이 보인다.

```text
camera_frame
camera_link_lee
base_link_robot_ns
odom_robot_ns
map_robot_ns
```

`imagePlee.py`는 image header를 `camera_frame`로 설정한다. `tf_listener.py` 기본값은 `camera_link_lee`를 source frame으로 둔다. launch에서는 `base_link_robot_ns -> camera_frame` static TF를 만든다.

관찰:

```text
실행할 때 어떤 frame 이름을 쓰는지 launch 기준으로 맞춰야 한다.
default parameter만 보고 판단하면 실제 launch 실행과 다를 수 있다.
```

---

## 8. YOLO image node와 YOLO custom message node의 node name 중복 가능성

`imageYOLOlee.py`와 `imgYOLOlee.py`는 둘 다 내부 node name이 아래와 같다.

```python
super().__init__('image_yolo_publisher1')
```

관찰:

```text
두 노드를 동시에 ros2 run으로 실행하면 node name 중복 경고가 생길 수 있다.
launch에서 name을 다르게 지정하거나, 목적에 따라 하나만 실행하는 것이 좋다.
```

---

## 9. OpenCV GUI 환경 문제

`imageSlee.py`는 `cv2.imshow()`를 사용한다.

```python
cv2.imshow("Camera View", self.raw_frame)
cv2.waitKey(1)
```

관찰:

```text
GUI가 없는 환경, SSH, Docker, WSL DISPLAY 설정이 안 된 환경에서는 화면 표시가 실패할 수 있다.
이 경우 topic 자체가 안 나오는 문제와 GUI 표시 문제를 분리해서 봐야 한다.
```

---

## 10. 현재 문서 정리 범위에서 하지 않는 일

이번 문서 정리 범위에서는 아래를 하지 않는다.

```text
- package.xml 수정
- launch 파일 수정
- frame 이름 통일
- YOLO model path 구조 변경
- RViz config 경로 수정
- node name 중복 수정
```

현재는 학습 문서화 단계이므로, 위 항목은 “이후 실행 재현성 개선 단계”에서 다룬다.
