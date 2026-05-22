# 06. Camera -> YOLO -> Custom Message -> TF 흐름

## 한 줄 결론

이번 camera/YOLO/TF 실습은 Day 01~05의 OpenCV/YOLO 코드를 ROS2 graph 안으로 넣는 과정이다. 핵심은 이미지 topic, detection custom message, TF frame이 어떻게 이어지는지 보는 것이다.

---

## 1. 전체 데이터 흐름

```text
웹캠
  -> camera_pkg/imagePlee.py
  -> /image_raw0              sensor_msgs/msg/Image
  -> camera_pkg/imageYOLOlee.py
  -> /image_yolo1             sensor_msgs/msg/Image, 박스가 그려진 이미지

웹캠
  -> camera_pkg/imagePlee.py
  -> /image_raw0              sensor_msgs/msg/Image
  -> camera_pkg/imgYOLOlee.py
  -> /img_yolo1               my_if/msg/ObjectDetectionArray
  -> tf_pkg_lee/tf_broad_yolo.py
  -> object_person_lee_0      TF frame
```

`/image_yolo1`와 `/img_yolo1`를 반드시 구분해야 한다.

| topic | type | 의미 |
|---|---|---|
| `/image_yolo1` | `sensor_msgs/msg/Image` | YOLO bbox가 그려진 이미지 |
| `/img_yolo1` | `my_if/msg/ObjectDetectionArray` | class/confidence/bbox 데이터 구조 |

---

## 2. imagePlee.py - image source node

`imagePlee.py`는 OpenCV로 웹캠을 열고 ROS Image로 변환해 발행한다.

```python
self.cap = cv2.VideoCapture(0)
ret, frame = self.cap.read()
resized = cv2.resize(frame, tuple(self.size))
img_msg = self.bridge.cv2_to_imgmsg(resized, encoding="bgr8")
img_msg.header.frame_id = "camera_lee"
self.publisher_.publish(img_msg)
```

ROS2 관점:

```text
node       : image_publisher1 또는 launch에서 test
publish    : /image_raw0
msg type   : sensor_msgs/msg/Image
frame_id   : camera_lee
parameters : publish_rate, topic_name, image_size
```

---

## 3. imageOPENlee.py - Canny edge node

`imageOPENlee.py`는 `/image_raw0`를 받아 Canny edge를 적용하고 `/image_edge1`로 발행한다.

```python
self.subscription = self.create_subscription(Image, 'image_raw0', self.image_callback, 10)
self.edge_publisher = self.create_publisher(Image, 'image_edge1', 10)
```

OpenCV 처리:

```python
edge = cv2.Canny(self.current_frame, 50, 300)
edge_msg = self.bridge.cv2_to_imgmsg(edge, encoding="mono8")
```

여기서 중요한 점은 output image의 header를 input image에서 이어받는다는 것이다.

```python
edge_msg.header.stamp = msg.header.stamp
edge_msg.header.frame_id = msg.header.frame_id
```

즉 edge image도 원본 camera frame 기준으로 해석된다.

---

## 4. imageSlee.py - snapshot service node

`imageSlee.py`는 raw/yolo/canny 이미지를 구독하고, service 요청이 오면 이미지를 파일로 저장한다.

구독 topic:

```text
/image_raw0
/image_yolo1
/image_edge1
```

service:

```text
/capture_snapshot1, std_srvs/srv/Trigger
```

parameter:

```text
snapshot_target = raw | yolo | canny
```

실습 명령 예시:

```bash
ros2 run camera_pkg image_proc1
ros2 param set /image_processor1 snapshot_target yolo
ros2 service call /capture_snapshot1 std_srvs/srv/Trigger "{}"
```

이 구조는 service가 왜 필요한지 보여준다. 이미지는 topic으로 계속 받고, 저장 명령은 service로 한 번 요청한다.

---

## 5. imageYOLOlee.py - YOLO image publisher

`imageYOLOlee.py`는 `/image_raw0`를 받아 YOLO를 실행하고, bbox가 그려진 이미지를 `/image_yolo1`로 발행한다.

```python
results = self.model(frame, verbose=False)
cv2.rectangle(...)
img_msg = self.bridge.cv2_to_imgmsg(frame, encoding="bgr8")
self.publisher_.publish(img_msg)
```

이 노드는 사람 눈으로 보기 좋은 결과를 만든다.

```text
입력 : /image_raw0, sensor_msgs/Image
출력 : /image_yolo1, sensor_msgs/Image
용도 : rqt_image_view/RViz 등에서 시각 확인
```

---

## 6. imgYOLOlee.py - YOLO custom message publisher

`imgYOLOlee.py`는 같은 `/image_raw0`를 받아 YOLO를 실행하지만, 출력은 이미지가 아니라 custom message다.

```python
detection_msg = ObjectDetection()
detection_msg.class_name = class_name
detection_msg.confidence = confidence
detection_msg.bbox = [int(x1), int(y1), int(x2), int(y2)]
detection_array_msg.detections.append(detection_msg)
```

발행 topic:

```text
/img_yolo1, my_if/msg/ObjectDetectionArray
```

이 노드는 기계가 처리하기 좋은 결과를 만든다.

```text
입력 : /image_raw0, sensor_msgs/Image
출력 : /img_yolo1, my_if/msg/ObjectDetectionArray
용도 : TF 변환, 후처리, 다른 로직 연결
```

---

## 7. tf_broad_yolo.py - detection을 TF frame으로 바꾸기

`tf_broad_yolo.py`는 `/img_yolo1`을 구독한다.

```python
self.create_subscription(
    ObjectDetectionArray,
    self.detection_topic,
    self.callback,
    10)
```

각 detection에 대해 object frame 이름을 만든다.

```python
object_person_lee_0
```

parent frame은 우선순위가 있다.

```text
1. parent_frame parameter가 있으면 그것 사용
2. msg.header.frame_id가 있으면 그것 사용
3. 없으면 fallback_parent_frame 사용
```

현재 launch 흐름에서는 image header가 `camera_lee`이므로 보통 object frame은 `camera_lee` 아래에 붙는다.

```text
camera_lee -> object_person_lee_0
```

---

## 8. lee_yolo_launch.py - 전체 묶음

`lee_yolo_launch.py`는 아래를 한 번에 실행한다.

```text
camera_pkg/image_pub1
camera_pkg/yolo_pub_l
tf2_ros/static_transform_publisher: map_robot_ns -> odom_robot_ns
tf_pkg_lee/odom_simul: odom_robot_ns -> base_link_robot_ns
tf2_ros/static_transform_publisher: base_link_robot_ns -> camera_lee
tf_pkg_lee/tf_broad_yolo: camera_lee -> object_person_lee_0
조건부 tf_listener
조건부 rqt_tf_tree
조건부 rviz2
```

결과 TF tree는 대략 아래처럼 된다.

```text
map_robot_ns
└── odom_robot_ns
    └── base_link_robot_ns
        └── camera_lee
            └── object_person_lee_0
```

---

## 9. 이 실습의 정확한 의미

이 실습은 “YOLO로 물체를 검출하고, 그 검출 결과를 TF tree에 붙여보는 연습”이다.

하지만 정확한 3D 위치 추정은 아니다. 이유는 depth가 실제 센서값이 아니라 parameter로 지정한 고정값이기 때문이다.

```python
self.declare_parameter('fixed_depth', 1.0)
trans.transform.translation.x = depth
```

따라서 정확한 표현은 아래다.

```text
2D bbox 중심과 고정 depth를 이용한 임시 object frame 시각화
```

추후 진짜 3D 위치 추정을 하려면 아래 중 하나가 필요하다.

```text
- depth camera
- stereo camera
- LiDAR와 camera calibration
- known object size 기반 거리 추정
- camera intrinsic을 사용한 geometry 계산
```

---

## 10. 확인 명령어

```bash
# camera image 확인
ros2 topic info /image_raw0
ros2 topic echo /image_raw0 --once
rqt_image_view

# YOLO image 확인
ros2 topic info /image_yolo1

# YOLO custom message 확인
ros2 topic info /img_yolo1
ros2 topic echo /img_yolo1 --once

# TF 확인
ros2 run tf2_tools view_frames
ros2 run tf2_ros tf2_echo camera_lee object_person_lee_0
ros2 run tf2_ros tf2_echo odom_robot_ns object_person_lee_0
```

---

## 11. 뒤쪽 학습과의 연결

이 흐름은 Day 10~13의 sensor/TF 문제로 이어진다.

```text
camera_lee frame이 TF tree에 없으면 object frame도 tree에 붙지 않는다.
laser frame이 TF tree에 없으면 SLAM/AMCL/Nav2가 /scan을 제대로 해석하지 못한다.
map_robot_ns -> odom_robot_ns가 없으면 RViz Fixed Frame을 map_robot_ns로 놓았을 때 로봇이 연결되지 않는다.
```

즉 Day 09의 YOLO TF 실습은 SLAM/AMCL/Nav2를 위한 TF 감각을 만드는 중간 단계다.
