# 03. OpenCV Basic / Edge / Color Tracking

## 1. 이 문서에서 다루는 것

Day 03의 목적은 이미지를 “파일”이 아니라 “실시간으로 들어오는 센서 데이터”처럼 다루는 것이다.

```text
이미지를 읽는다.
NumPy 배열로 본다.
색공간을 바꾼다.
mask를 만든다.
blur/edge/contour를 적용한다.
웹캠 frame을 반복 처리한다.
```

이 흐름은 뒤의 ROS2 `camera_pkg`에서 거의 그대로 다시 등장한다.

---

## 2. 관련 원본 파일

```text
day_3/opencv_basic.md
day_3/opencv_canny_sobel_function_guide.md
day_3/opencv_realtime_color_tracking.md
day_3/parc/04_01_OpenCV-Basic.ipynb
day_3/parc/04_02_OpenCV-Canny-Sobel.ipynb
day_3/parc/04_03_00_OpenCV-Practice.py
day_3/parc/baboon.jpg
day_3/parc/road_image.jpg
day_3/parc/sample.jpg
```

---

## 3. OpenCV 이미지는 NumPy 배열이다

```python
import cv2

img = cv2.imread("image.jpg")
print(img.shape)
print(img.dtype)
```

보통 컬러 이미지는 아래 형태다.

```text
(height, width, channel)
```

그래서 픽셀 접근은 다음처럼 한다.

```python
pixel = img[y, x]
```

하지만 사각형을 그릴 때는 좌표를 `(x, y)` 순서로 준다.

```python
cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
```

이 차이는 YOLO bbox를 OpenCV 화면에 그릴 때도 계속 나온다.

---

## 4. BGR / RGB / Gray / HSV

OpenCV는 기본적으로 BGR 순서를 쓴다. Matplotlib은 보통 RGB처럼 표시한다.

```python
img_bgr = cv2.imread("image.jpg")
img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
```

| 색공간 | 사용 목적 |
|---|---|
| BGR | OpenCV 기본 이미지 처리 |
| RGB | Matplotlib 표시 |
| Gray | edge, threshold, contour 전처리 |
| HSV | 색상 추적, 색상 기반 mask |

HSV에서 빨간색은 Hue 범위가 0 근처와 180 근처로 나뉠 수 있다. 그래서 빨간 물체를 추적할 때는 mask를 두 개 만들어 합치는 경우가 많다.

---

## 5. Mask의 의미

mask는 “어떤 픽셀을 남길 것인가”를 나타내는 흑백 이미지다.

```python
mask = cv2.inRange(hsv, lower, upper)
result = cv2.bitwise_and(frame, frame, mask=mask)
```

흐름은 아래와 같다.

```text
BGR frame
  -> HSV 변환
  -> lower/upper 범위로 mask 생성
  -> mask가 흰색인 영역만 원본에서 남김
```

이것은 YOLO 이전의 전통적 객체 검출 방식이다. YOLO가 학습 기반으로 box를 낸다면, mask 방식은 사람이 정한 색상 조건으로 후보 영역을 만든다.

---

## 6. Blur를 먼저 하는 이유

edge나 contour를 바로 찾으면 노이즈까지 같이 잡힐 수 있다. 그래서 blur로 작은 노이즈를 줄인다.

| 함수 | 특징 |
|---|---|
| `cv2.blur()` | 단순 평균 |
| `cv2.GaussianBlur()` | 가장 자주 쓰는 smoothing |
| `cv2.medianBlur()` | salt-and-pepper 노이즈에 강함 |
| `cv2.bilateralFilter()` | edge를 비교적 보존 |

OpenCV 실습에서 blur는 “이미지를 흐리게 만들기”가 목적이 아니라, 뒤 단계가 안정적으로 동작하도록 노이즈를 줄이는 전처리다.

---

## 7. Sobel과 Canny

Sobel은 밝기 변화의 방향별 기울기를 계산한다.

```python
grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
```

Canny는 edge 검출 파이프라인을 묶은 알고리즘이다.

```python
edges = cv2.Canny(gray, 100, 200)
```

처음에는 내부 수식보다 아래 감각이 중요하다.

```text
threshold가 낮다
  -> edge가 많이 잡힘, 노이즈도 늘어남

threshold가 높다
  -> 확실한 edge만 남음, 필요한 선도 사라질 수 있음
```

ROS2 camera 실습의 `imageOPENlee.py`는 이 흐름을 ROS2 topic으로 바꾼 예다.

```text
/image_raw0 subscribe
  -> cv_bridge로 OpenCV frame 변환
  -> cv2.Canny()
  -> /image_edge1 publish
```

---

## 8. Contour와 bounding box

mask나 edge 결과에서 연결된 영역을 찾으면 contour가 된다.

```python
contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

for cnt in contours:
    area = cv2.contourArea(cnt)
    if area < 500:
        continue
    x, y, w, h = cv2.boundingRect(cnt)
    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
```

이 구조는 YOLO bbox와 비교해서 이해하면 좋다.

| 방식 | box가 나오는 이유 |
|---|---|
| contour | 색상/edge/threshold 조건으로 생긴 영역을 감쌈 |
| YOLO | 학습된 모델이 객체 위치를 예측함 |

둘 다 최종적으로는 `x, y, w, h` 또는 `x1, y1, x2, y2` 형태의 box로 이어진다.

---

## 9. 실시간 웹캠 루프

OpenCV 웹캠 실습은 아래 패턴으로 돌아간다.

```python
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # processing
    cv2.imshow("frame", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
```

`cv2.waitKey(1)`은 단순히 1ms 기다리는 함수가 아니다. OpenCV 창 이벤트 처리와 키 입력 확인도 같이 한다. 그래서 `imshow()`를 쓸 때는 거의 항상 같이 들어간다.

---

## 10. ROS2로 바뀌면 무엇이 달라지는가

OpenCV 단독 코드는 내가 직접 loop를 돈다.

```text
while True:
    cap.read()
    process(frame)
    imshow(frame)
```

ROS2에서는 frame이 topic으로 들어오고 callback이 호출된다.

```text
camera node
  -> /image_raw0
  -> subscriber callback
  -> process(frame)
  -> publish result
```

즉, 핵심 처리 함수는 비슷하지만 데이터가 들어오는 방식이 바뀐다.

---

## 11. 현재 단계에서의 결론

OpenCV Basic에서 가져갈 것은 아래다.

```text
OpenCV 이미지는 NumPy 배열이다.
배열 접근은 img[y, x]이고 좌표 표기는 보통 (x, y)다.
BGR/RGB/Gray/HSV는 목적에 따라 바꿔 쓴다.
mask/edge/contour는 전통적 객체 후보 검출 흐름이다.
webcam loop는 ROS2 camera callback 구조로 이어진다.
```
