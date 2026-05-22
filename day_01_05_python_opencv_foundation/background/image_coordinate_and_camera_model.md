# Background: 이미지 좌표계와 카메라 모델

## 1. 이미지 좌표계

이미지 좌표는 보통 왼쪽 위가 원점이다.

```text
x: 오른쪽으로 증가
y: 아래쪽으로 증가
```

OpenCV 배열 접근은 다음과 같다.

```python
pixel = img[y, x]
```

반면 좌표를 말하거나 사각형을 그릴 때는 보통 `(x, y)` 순서다.

```python
cv2.rectangle(img, (x1, y1), (x2, y2), color, thickness)
```

---

## 2. 픽셀 좌표와 실제 공간 좌표는 다르다

YOLO가 주는 bbox는 이미지 안의 픽셀 좌표다.

```text
bbox = [x1, y1, x2, y2]
```

이 값만으로 실제 3D 위치를 바로 알 수는 없다. 3D 위치를 얻으려면 camera intrinsic, depth, object size, camera TF 같은 추가 정보가 필요하다.

---

## 3. ROS2에서 연결되는 개념

```text
sensor_msgs/Image
  -> 픽셀 데이터

sensor_msgs/CameraInfo
  -> 카메라 내부 파라미터

TF
  -> camera frame이 robot frame에 대해 어디 있는지
```

카메라 인식 결과를 로봇 좌표계에서 쓰려면 Image, CameraInfo, TF를 함께 이해해야 한다.
