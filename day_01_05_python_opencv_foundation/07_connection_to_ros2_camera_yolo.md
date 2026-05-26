# 07. Day 01~05에서 ROS2 Camera / YOLO로 이어지는 흐름

## 1. 왜 이 연결 문서가 필요한가

Day 01~05는 Python/OpenCV 기초처럼 보이고, Day 06~13은 ROS2/Gazebo/SLAM/Nav2처럼 보인다. 하지만 실제로는 끊어진 흐름이 아니다.

```text
Python / NumPy / OpenCV / YOLO / Kalman
  -> ROS2 camera node
  -> custom message
  -> object detection topic
  -> TF visualization
  -> rosbag recording
  -> Gazebo sensor topic
  -> SLAM / AMCL / Nav2
```

이 문서는 앞부분 기초가 뒤쪽 ROS2 코드에서 어떻게 다시 등장하는지 정리한다.

---

## 2. Python class -> ROS2 Node class

ROS2 Python node는 대개 class로 작성한다.

```python
class ImagePublisher(Node):
    def __init__(self):
        super().__init__('image_publisher1')
        ...
```

Day 01~02에서 class와 method를 익힌 이유가 여기서 연결된다.

| Python OOP | ROS2 node |
|---|---|
| `__init__()` | publisher/subscription/timer 초기화 |
| instance variable | node 상태 저장 |
| method | callback 함수 |
| class 역할 분리 | node 역할 분리 |

---

## 3. OpenCV frame -> ROS2 Image message

OpenCV 단독 코드에서는 frame이 바로 NumPy 배열이다.

```python
ret, frame = cap.read()
```

ROS2에서는 이미지가 message로 전달된다.

```text
sensor_msgs/Image
  -> cv_bridge
  -> OpenCV ndarray
```

`camera_pkg/imagePlee.py`는 OpenCV frame을 ROS2 Image message로 바꾸어 publish한다.

```text
cv2.VideoCapture(0)
  -> frame
  -> bridge.cv2_to_imgmsg(frame, encoding="bgr8")
  -> /image_raw0 publish
```

반대로 `imageOPENlee.py`, `imageYOLOlee.py`, `imgYOLOlee.py`는 Image message를 받아 OpenCV frame으로 바꾼다.

```text
/image_raw0 subscribe
  -> bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
  -> OpenCV/YOLO 처리
```

---

## 4. OpenCV edge -> ROS2 processed image topic

Day 03의 Canny 실습은 ROS2에서 아래 흐름으로 바뀐다.

```text
OpenCV 단독:
    frame -> cv2.Canny(frame) -> imshow

ROS2:
    /image_raw0 -> callback -> cv2.Canny(frame) -> /image_edge1 publish
```

즉, 알고리즘 자체는 같지만 입력과 출력의 형태가 바뀐다.

```text
단독 코드 입력/출력
  camera device / display window

ROS2 코드 입력/출력
  topic subscribe / topic publish
```

---

## 5. YOLO 결과 이미지와 YOLO 결과 데이터는 다르다

`imageYOLOlee.py`는 YOLO 결과를 이미지에 그려 `/image_yolo1`로 publish한다.

```text
/image_raw0
  -> YOLO inference
  -> rectangle/text drawing
  -> /image_yolo1
```

이것은 사람이 보기 좋은 결과다.

반면 `imgYOLOlee.py`는 YOLO 결과를 custom message로 발행한다.

```text
/image_raw0
  -> YOLO inference
  -> ObjectDetectionArray
  -> /img_yolo1
```

이것은 다른 node가 사용하기 좋은 결과다.

둘은 목적이 다르다.

| 출력 | 목적 |
|---|---|
| detection이 그려진 Image | RViz/화면 확인, 디버깅 |
| ObjectDetectionArray | 다른 node가 class/conf/bbox를 사용 |

---

## 6. Custom message와 bbox

`ObjectDetection.msg`는 다음 정보를 담는다.

```text
string class_name
float64 confidence
int32[4] bbox
```

이것은 YOLO 결과에서 직접 가져올 수 있다.

```text
class_name
  result.names[class_id]

confidence
  float(box.conf[0])

bbox
  [x1, y1, x2, y2]
```

여러 객체는 `ObjectDetectionArray.msg`로 묶는다.

```text
std_msgs/Header header
ObjectDetection[] detections
```

이 구조를 이해하면 “커스텀 메시지를 왜 만들었는지”가 명확해진다. YOLO 결과를 단순 화면 표시가 아니라 ROS2 데이터로 바꾸기 위한 것이다.

---

## 7. frame_id가 왜 중요한가

`imagePlee.py`는 Image message의 header에 frame id를 넣는다.

```python
img_msg.header.frame_id = "camera_frame"
```

이 값은 단순 문자열이 아니라 TF와 연결될 수 있는 좌표계 이름이다.

```text
image message의 frame_id
  -> 이 이미지가 어느 좌표계의 센서에서 나온 것인지 표시
```

이후 object detection을 TF로 시각화하려면 아래 정보가 필요하다.

```text
camera frame
bbox 중심점
깊이 또는 거리 가정
카메라 모델
base_link와 camera frame 사이의 TF
```

단순 YOLO bbox 중심점 `(cx, cy)`는 이미지 픽셀 좌표다. 이것을 바로 3D 위치라고 하면 안 된다.

---

## 8. object TF로 이어질 때 조심할 점

YOLO box 중심은 이미지 좌표다.

```text
(cx, cy) in pixel coordinate
```

3D object 위치를 만들려면 추가 정보가 필요하다.

```text
depth camera
stereo camera
LiDAR fusion
known object size
ground plane assumption
camera intrinsic K
camera extrinsic TF
```

따라서 현재 학습 단계에서는 다음 표현이 안전하다.

```text
YOLO detection 결과를 바탕으로 object 후보 정보를 topic으로 발행했다.
필요하면 단순 가정 기반 위치를 TF로 시각화할 수 있다.
```

피해야 할 표현은 아래다.

```text
카메라 하나만으로 정확한 3D 위치를 복원했다.
```

---

## 9. JSON log -> rosbag

Day 02~05에서는 JSON log를 저장했다.

```text
내가 원하는 구조로 값을 저장
```

ROS2에서는 rosbag을 사용해 topic message를 시간순으로 저장할 수 있다.

```text
/image_raw0
/image_yolo1
/img_yolo1
/tf
/tf_static
```

rosbag은 단순 저장이 아니라 재현 실험 도구다.

```text
실시간 카메라가 없어도 같은 topic을 replay할 수 있다.
YOLO node만 다시 테스트할 수 있다.
파라미터 변경 전/후 결과를 비교할 수 있다.
```

---

## 10. Day 01~05가 Day 10~13까지 이어지는 큰 그림

```text
Python / OpenCV
  -> 카메라 데이터를 처리할 수 있음

YOLO / Kalman
  -> 인식 결과와 흔들림 완화 개념을 이해함

ROS2 topic / custom msg
  -> 인식 결과를 시스템 데이터로 바꿈

TF
  -> 센서와 로봇 좌표계를 연결함

rosbag
  -> 실험 데이터를 재현 가능하게 만듦

Gazebo / SLAM / AMCL / Nav2
  -> 로봇 위치추정과 주행 실습으로 확장
```

---

## 11. 정리

Day 01~05는 뒤쪽과 분리된 “기초 문법 파트”가 아니다.

```text
OpenCV frame 처리 능력
  -> ROS2 Image 처리 능력

YOLO 결과 파싱 능력
  -> custom message 설계 능력

Kalman Filter 감각
  -> 센서 노이즈와 추정 개념 이해

파일/JSON/YAML 감각
  -> calibration, map, parameter 파일 이해
```

이 연결을 잡아두면 Day 06~13의 ROS2 실습이 훨씬 덜 뜬금없어진다.
