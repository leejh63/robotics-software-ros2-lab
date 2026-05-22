# 08. Day 01~05 복습 질문

이 문서는 Day 01~05를 제대로 이해했는지 확인하기 위한 질문 모음이다. 답을 외우기보다, 실제 코드 파일을 열어보면서 설명할 수 있는지를 기준으로 삼는다.

---

## 1. Python / NumPy

1. `hello.py`에서 `import test_1 as c`를 하는 이유는 무엇인가?
2. `if __name__ == "__main__"` 블록은 언제 실행되는가?
3. Python list와 NumPy ndarray는 어떤 차이가 있는가?
4. OpenCV 이미지의 shape가 `(480, 640, 3)`일 때 각각 무엇을 의미하는가?
5. `img[y, x]`와 `(x, y)` 좌표 표기가 왜 헷갈리는가?
6. bool mask 배열은 어떤 상황에서 쓰이는가?
7. Matplotlib은 단순 시각화 외에 어떤 디버깅 역할을 할 수 있는가?

---

## 2. OOP / File / Thread

1. 센서를 class로 묶으면 어떤 장점이 있는가?
2. 추상 클래스 `Sensor`가 있으면 어떤 구조적 이점이 생기는가?
3. NumPy 배열을 JSON으로 바로 저장하기 어려운 이유는 무엇인가?
4. JSON과 YAML은 ROS2에서 각각 어떤 파일들과 연결되는가?
5. daemon thread는 메인 프로그램 종료 시 어떻게 되는가?
6. race condition은 어떤 상황에서 발생하는가?
7. Lock과 Queue는 각각 어떤 문제를 해결하는가?
8. thread와 process를 구분해야 하는 이유는 무엇인가?

---

## 3. OpenCV

1. OpenCV가 BGR을 기본으로 쓰는 것이 왜 문제가 될 수 있는가?
2. HSV 색공간은 색상 추적에서 왜 유용한가?
3. 빨간색 HSV mask를 만들 때 범위가 두 개 필요할 수 있는 이유는 무엇인가?
4. blur를 edge 검출 전에 적용하는 이유는 무엇인가?
5. Sobel과 Canny의 차이를 어떻게 설명할 수 있는가?
6. contour로 만든 bounding box와 YOLO bbox는 무엇이 다른가?
7. `cv2.waitKey(1)`은 왜 `imshow()`와 함께 자주 쓰이는가?

---

## 4. Camera Calibration

1. 카메라 이미지는 나오는데 왜 calibration이 필요한가?
2. camera matrix `K`의 `fx`, `fy`, `cx`, `cy`는 각각 무엇인가?
3. 왜곡 계수 `k1, k2, p1, p2, k3`는 어떤 왜곡을 설명하는가?
4. 체커보드의 칸 수와 내부 코너 수는 왜 다를 수 있는가?
5. 다양한 각도와 위치에서 체커보드를 찍어야 하는 이유는 무엇인가?
6. 재투영 오차는 무엇을 의미하는가?
7. ROS2에서 `Image`와 `CameraInfo`는 어떤 차이가 있는가?

---

## 5. YOLO / Kalman

1. YOLO 결과의 `xyxy`, `xywh`, `conf`, `cls`는 각각 무엇인가?
2. confidence threshold를 낮추면 어떤 장단점이 있는가?
3. NMS는 왜 필요한가?
4. YOLO box 중심점을 계산하는 이유는 무엇인가?
5. Kalman Filter의 predict와 update는 무엇이 다른가?
6. 상태벡터 `[cx, vx, cy, vy]`에서 직접 관측되는 값은 무엇인가?
7. `R`을 크게 잡으면 필터 결과가 어떻게 변할 수 있는가?
8. `Q`를 너무 작게 잡으면 어떤 문제가 생길 수 있는가?
9. NIS는 무엇을 평가하기 위한 값인가?

---

## 6. ROS2 연결

1. OpenCV `VideoCapture` 루프는 ROS2에서 어떤 구조로 바뀌는가?
2. `cv_bridge`가 필요한 이유는 무엇인가?
3. YOLO 결과를 이미지에 그려 publish하는 것과 custom message로 publish하는 것은 무엇이 다른가?
4. `ObjectDetection.msg`에는 어떤 필드가 있고, 각각 YOLO 결과의 무엇과 연결되는가?
5. `frame_id = "camera_lee"`는 단순 이름인가, 좌표계 의미를 가질 수 있는가?
6. 단안 카메라 YOLO bbox만으로 정확한 3D 위치를 말하기 어려운 이유는 무엇인가?
7. JSON log와 rosbag은 각각 어떤 재현성 도구인가?

---

## 7. 이 파트를 끝냈다고 볼 수 있는 기준

아래 흐름을 말로 설명할 수 있으면 Day 01~05 학습 흐름은 어느 정도 잡힌 것이다.

```text
카메라 frame을 OpenCV로 읽는다.
필요하면 calibration 결과로 왜곡을 보정한다.
YOLO로 객체를 찾는다.
bbox에서 중심점과 class/confidence를 뽑는다.
Kalman Filter로 중심점 흔들림을 줄인다.
결과를 화면/로그로 확인한다.
ROS2에서는 이 결과를 Image topic 또는 custom message topic으로 publish한다.
```
