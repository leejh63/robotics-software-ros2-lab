# 05. TF2, Sensor Message, Rosbag Foundation

## 한 줄 결론

ROS2에서 센서 데이터는 topic으로 흐르고, 그 센서가 로봇의 어디에 붙어 있는지는 TF가 설명한다. rosbag은 이 topic과 TF를 기록해서 이후 다시 재생하는 도구다.

---

## 1. Topic과 TF의 차이

카메라 이미지를 예로 들면:

```text
/image_raw
  -> 이미지 데이터가 흐르는 topic

sensor_msgs/msg/Image.header.frame_id = camera_link
  -> 이 이미지가 camera_link 좌표계 기준이라는 의미

base_link -> camera_link TF
  -> camera_link가 로봇 본체 기준 어디에 붙어 있는지 설명
```

즉 topic만 있어서는 부족하다. 센서 데이터를 공간적으로 해석하려면 frame과 TF가 필요하다.

---

## 2. 이번 코드의 TF 관련 파일

```text
ros2_tf_examples/ros2_tf_examples/odom_simulator.py
ros2_tf_examples/ros2_tf_examples/tf_tree_simulator.py
ros2_tf_examples/ros2_tf_examples/tf_listener.py
ros2_tf_examples/ros2_tf_examples/yolo_tf_broadcaster.py
ros2_tf_examples/launch/tf_tree_demo.launch.py
ros2_tf_examples/launch/yolo_tf_pipeline.launch.py
```

---

## 3. odom_simulator.py - 동적 TF 발행

`odom_simulator.py`는 20 Hz 주기로 아래 TF를 발행한다.

```text
odom -> base_link
```

코드 구조:

```python
self.br = TransformBroadcaster(self)
self.timer = self.create_timer(0.05, self.timer_callback)
```

매 timer마다 원운동 위치를 계산한다.

```python
x = radius * cos(omega * t)
y = radius * sin(omega * t)
yaw = omega * t + pi / 2
```

그리고 quaternion으로 변환해서 `TransformStamped`에 넣는다.

```python
qx, qy, qz, qw = quaternion_from_euler(roll, pitch, yaw)
```

이 실습의 의미는 “로봇 base frame이 odom frame 안에서 시간에 따라 움직인다”는 것을 시각화하는 것이다.

---

## 4. tf_tree_simulator.py - TF tree 구조 연습

`tf_tree_simulator.py`는 아래와 같은 tree를 만든다.

```text
map
└── odom
    └── base_link
        ├── left_marker
        └── right_marker
```

`map -> odom`는 static transform으로 한 번 발행한다.

```python
self.static_br = StaticTransformBroadcaster(self)
self.publish_static_map_to_odom()
```

`odom -> base_link`, `base_link -> left_marker`, `base_link -> right_marker`는 동적 transform으로 계속 발행한다.

이 구조는 Day 10~13의 frame 구조를 이해하기 위한 축소판이다.

```text
map
└── odom
    └── base_link
        ├── camera
        └── laser
```

---

## 5. tf_listener.py - transform 조회

`tf_listener.py`는 target frame과 source frame 사이의 변환을 조회한다.

```python
trans = self.tf_buffer.lookup_transform(
    self.target_frame,
    self.source_frame,
    rclpy.time.Time())
```

기본 parameter:

```text
target_frame = base_link
source_frame = camera_linright_marker
```

launch에서는 아래처럼 바꿔서 쓴다.

```python
parameters=[{
    'target_frame': 'odom',
    'source_frame': 'left_marker',
}]
```

또는 YOLO TF 실습에서는:

```text
target_frame = odom
source_frame = object_person_example_0
```

조회 실패 유형:

| 예외 | 의미 |
|---|---|
| `LookupException` | frame 이름을 못 찾음 |
| `ConnectivityException` | 두 frame이 같은 tree로 연결되어 있지 않음 |
| `ExtrapolationException` | 시간 기준 transform을 맞출 수 없음 |

---

## 6. /tf와 /tf_static

| topic | 의미 | 예시 |
|---|---|---|
| `/tf` | 시간에 따라 바뀌는 동적 transform | `odom -> base_link` |
| `/tf_static` | 거의 변하지 않는 고정 transform | `base_link -> camera_link` |

동적 TF는 계속 갱신되어야 한다. static TF는 한 번 발행해도 latched처럼 유지된다.

Day 10~13에서는 이 구분이 중요하다.

```text
robot_state_publisher
  -> URDF의 fixed joint를 /tf_static 또는 /tf로 발행

Gazebo odom plugin
  -> odom -> base 계열 동적 TF 발행

SLAM/AMCL
  -> map -> odom 계열 TF 발행
```

---

## 7. Sensor message와 Header

센서 메시지는 대부분 Header를 가진다.

```text
std_msgs/Header header
  stamp
  frame_id
```

예를 들어 `sensor_msgs/Image`는 이미지 픽셀 데이터뿐 아니라, 이 이미지가 언제 찍혔고 어떤 frame 기준인지도 갖는다.

이번 코드에서 `image_publisher.py`는 다음처럼 설정한다.

```python
img_msg.header.stamp = self.get_clock().now().to_msg()
img_msg.header.frame_id = "camera_link"
```

`yolo_detection_publisher.py`는 이 header를 detection array에 복사한다.

```python
detection_array_msg.header = msg.header
```

`yolo_tf_broadcaster.py`는 detection array의 header frame을 parent frame으로 쓴다.

```python
if msg.header.frame_id:
    return msg.header.frame_id
```

이 흐름 때문에 `camera_link` frame이 TF tree에 연결되어 있어야 YOLO object frame도 tree에 붙는다.

---

## 8. YOLO detection -> TF 변환의 한계

`yolo_tf_broadcaster.py`는 bbox 중심을 이용해서 object frame을 만든다.

```python
center_x = (x_min + x_max) / 2
center_y = (y_min + y_max) / 2
normalized_x = (center_x - image_width / 2.0) / image_width
normalized_y = (center_y - image_height / 2.0) / image_height
```

그리고 depth는 실제 측정값이 아니라 `fixed_depth` parameter를 쓴다.

```python
trans.transform.translation.x = fixed_depth
trans.transform.translation.y = -normalized_x
trans.transform.translation.z = -normalized_y
```

따라서 이 실습은 정확한 3D 위치 추정이 아니다.

정확한 표현:

```text
YOLO bbox 결과를 고정 depth 값과 함께 TF frame으로 시각화하는 실습
```

부정확한 표현:

```text
카메라만으로 물체의 실제 3D 위치를 정확히 추정했다
```

---

## 9. rosbag의 역할

rosbag은 topic 데이터를 기록하고 재생하는 도구다.

```bash
ros2 bag record /image_raw /image_yolo /yolo_detections /tf /tf_static
ros2 bag play <bag_dir>
```

SLAM/AMCL/Nav2에서는 특히 중요하다.

```text
/scan만 기록하면 부족할 수 있다.
/odom, /tf, /tf_static, /clock까지 같이 필요할 수 있다.
```

왜냐하면 알고리즘은 센서 데이터만 보는 게 아니라, 센서 데이터가 어느 좌표계에서 어느 시간에 들어왔는지도 같이 해석하기 때문이다.

---

## 10. 확인 명령어

```bash
# TF tree 보기
ros2 run tf2_tools view_frames
ros2 run rqt_tf_tree rqt_tf_tree

# 특정 frame 사이 변환 조회
ros2 run tf2_ros tf2_echo odom base_link
ros2 run tf2_ros tf2_echo odom object_person_example_0

# TF topic 확인
ros2 topic echo /tf
ros2 topic echo /tf_static

# sensor header 확인
ros2 topic echo /image_raw --once
ros2 topic echo /yolo_detections --once
```

---

## 11. Day 10~13으로 이어지는 핵심

Day 10~13의 frame 문제는 Day 09 TF 실습의 확장이다.

```text
Day 09:
map -> odom -> base_link -> camera_link -> object_person_example_0

Day 10~13:
map -> odom -> base_footprint/base_link -> laser/camera
```

RViz에서 보이지 않는다고 해서 항상 topic 문제가 아니다. Fixed Frame, message header.frame_id, TF tree 연결이 더 자주 원인이다.
