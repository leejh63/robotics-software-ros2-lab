# 04. Camera Calibration Foundation

## 1. 이 문서에서 다루는 것

카메라를 켜면 이미지는 나오지만, 그 이미지가 정확한 측정 데이터라는 뜻은 아니다. 렌즈 왜곡이 있고, 픽셀 좌표와 실제 공간 좌표의 관계도 모른다.

Camera calibration은 다음 정보를 추정하는 과정이다.

```text
카메라 내부 파라미터
렌즈 왜곡 계수
픽셀 좌표와 카메라 좌표계 사이의 관계
```

---

## 2. 관련 원본 파일

```text
day_4/05_01_OpenCV-Calibration.md
day_4/05_01_OpenCV-Calibration-code-analysis.md
day_4/prac/05_01_01_OpenCV-Calib-Capture.py
day_4/prac/05_01_02_OpenCV-Calib-Undistort.py
day_4/prac/05_01_OpenCV-Calibration.ipynb
```

---

## 3. 카메라 모델을 왜 알아야 하는가

이미지의 한 점 `(u, v)`는 그냥 픽셀 위치다. 이 픽셀 하나만 보고 바로 실제 거리나 3D 위치를 정확히 알 수는 없다.

```text
3D world point
  -> camera coordinate
  -> lens projection
  -> image plane
  -> pixel coordinate
```

캘리브레이션은 이 과정 중 카메라 내부 특성을 추정한다. 그래야 왜곡을 보정하거나, 3D-2D 투영 관계를 사용할 수 있다.

---

## 4. 핀홀 카메라 모델

가장 기본 모델은 핀홀 카메라 모델이다.

카메라 내부 행렬은 보통 다음 형태다.

```text
K = [ fx   0  cx
       0  fy  cy
       0   0   1 ]
```

| 값 | 의미 |
|---|---|
| `fx` | x 방향 초점거리, 픽셀 단위 |
| `fy` | y 방향 초점거리, 픽셀 단위 |
| `cx` | 주점 x 좌표 |
| `cy` | 주점 y 좌표 |
| `K` | camera matrix |

`fx`, `fy`는 물리 단위 mm가 아니라 픽셀 단위로 표현되는 경우가 많다. 그래서 같은 렌즈라도 해상도와 이미지 스케일에 따라 값이 달라질 수 있다.

---

## 5. 왜곡 계수

실제 렌즈는 이상적인 핀홀 모델처럼 동작하지 않는다.

| 왜곡 | 의미 |
|---|---|
| radial distortion | 중심에서 멀어질수록 휘는 왜곡 |
| tangential distortion | 렌즈와 센서가 완전히 평행하지 않아 생기는 왜곡 |

OpenCV에서는 보통 아래 형태의 왜곡 계수를 사용한다.

```text
dist = [k1, k2, p1, p2, k3]
```

이 값들을 이용해서 원본 이미지를 보정한다.

```python
undistorted = cv2.undistort(frame, camera_matrix, dist_coeffs)
```

---

## 6. 체커보드를 쓰는 이유

체커보드는 실제 위치를 알고 있는 점들을 쉽게 만들 수 있다.

```text
object points
  실제 체커보드 코너의 3D 좌표

image points
  이미지에서 검출된 체커보드 코너의 2D 픽셀 좌표
```

여러 각도와 위치에서 체커보드를 찍으면, OpenCV가 3D 점과 2D 점의 대응을 이용해 카메라 파라미터를 추정한다.

중요한 실수 포인트는 “체커보드 칸 수”와 “내부 코너 수”가 다르다는 점이다.

```text
체커보드가 10 x 7 칸이라면
내부 코너는 보통 9 x 6일 수 있다.
```

OpenCV의 `findChessboardCorners()`에는 내부 코너 수를 넣어야 한다.

---

## 7. 캘리브레이션 데이터 수집 기준

좋은 캘리브레이션을 위해서는 다양한 이미지가 필요하다.

```text
정면만 찍지 않는다.
가장자리까지 체커보드를 이동시킨다.
여러 거리에서 찍는다.
여러 기울기에서 찍는다.
흔들리거나 흐린 사진은 제외한다.
체커보드 전체가 보이게 한다.
```

왜냐하면 렌즈 왜곡은 특히 이미지 가장자리에서 크게 나타나기 때문이다. 중앙만 찍은 데이터로는 가장자리 왜곡을 잘 추정하기 어렵다.

---

## 8. 재투영 오차

캘리브레이션 결과가 괜찮은지 확인할 때 재투영 오차를 본다.

```text
추정한 카메라 파라미터로 3D 체커보드 점을 다시 이미지에 투영한다.
실제 검출된 이미지 코너와 얼마나 차이 나는지 계산한다.
```

오차가 작을수록 모델이 관측값을 잘 설명한다. 하지만 숫자 하나만 믿으면 안 되고, 보정 전/후 이미지를 직접 비교해야 한다.

---

## 9. Day 04 코드 흐름

캘리브레이션 실습 코드는 크게 두 단계다.

```text
05_01_01_OpenCV-Calib-Capture.py
  -> 체커보드 이미지를 여러 장 저장

05_01_02_OpenCV-Calib-Undistort.py
  -> 저장된 calibration 결과를 로드
  -> 실시간 frame에 왜곡 보정 적용
```

실제 사용 흐름은 아래와 같다.

```text
카메라 연결
  -> 체커보드 촬영
  -> corner 검출
  -> object point / image point 누적
  -> calibrateCamera()
  -> camera_matrix, dist_coeffs 저장
  -> undistort/remap으로 보정 확인
```

---

## 10. ROS2와 연결되는 부분

ROS2에서는 카메라 영상만 중요한 것이 아니라 카메라 정보도 중요하다.

```text
sensor_msgs/Image
  -> 픽셀 데이터

sensor_msgs/CameraInfo
  -> K, D, R, P 같은 카메라 파라미터
```

Day 04 캘리브레이션 결과는 나중에 `CameraInfo`나 camera calibration YAML과 연결될 수 있다.

다만 현재 학습 코드에서는 카메라 보정과 YOLO 추론을 OpenCV 단독 코드로 다뤘고, ROS2 `CameraInfo`까지 완전히 통합한 단계는 아니다. 문서에서는 이 경계를 명확히 해야 한다.

---

## 11. YOLO 전에 undistort를 해야 하는가

항상 정답은 아니다.

```text
정확한 위치/거리 추정이 중요하다
  -> undistort 후 detection을 고려할 수 있음

단순히 객체가 있는지만 보면 된다
  -> 원본 frame으로도 충분할 수 있음

실시간성이 중요하다
  -> undistort 비용과 정확도 개선을 비교해야 함
```

즉, 캘리브레이션은 무조건 모든 영상 처리 앞에 붙이는 장식이 아니라, 필요한 정확도와 비용을 비교해서 넣는 단계다.

---

## 12. 현재 단계에서의 결론

Camera Calibration에서 가져갈 것은 아래다.

```text
카메라 이미지는 왜곡이 있을 수 있다.
K는 카메라 내부 파라미터이고 dist는 렌즈 왜곡 계수다.
체커보드는 3D-2D 대응점을 만들기 위한 도구다.
재투영 오차와 보정 전/후 이미지를 함께 봐야 한다.
ROS2에서는 Image뿐 아니라 CameraInfo도 중요하다.
```
