# 05. YOLO / Kalman Foundation

## 1. 이 문서에서 다루는 것

Day 04~05의 YOLO/Kalman 파트는 카메라 영상에서 객체를 찾고, 그 결과가 프레임마다 흔들릴 때 더 안정적으로 추정하는 흐름을 다룬다.

```text
camera frame
  -> YOLO inference
  -> bounding box / confidence / class
  -> bbox 중심점 계산
  -> Kalman Filter로 중심점 안정화
  -> 결과 표시 / 로그 / ROS2 message로 확장
```

---

## 2. 관련 실습 파일

```text
day_4/05_02_YOLO-beginner-guide.md
day_4/05_02_YOLO-Kalman-code-analysis.md
day_4/prac/05_02_1_YOLO_test.py
day_4/prac/05_02_YOLO-Kalman.ipynb
day_4/prac/05_03_Robot-Camera-Practice.py
day_4/yolo_finetuning_pipeline_md/*
$SOURCE_NOTES/code/05.02.02.Webcam-Kalman.py
$SOURCE_NOTES/code/05.02.03.Kalman-NIS-Eval.py
```

---

## 3. YOLO가 주는 결과

YOLO는 이미지에서 객체 위치와 종류를 예측한다.

| 값 | 의미 |
|---|---|
| `xyxy` | box 좌상단/우하단 좌표: `x1, y1, x2, y2` |
| `xywh` | 중심점과 크기: `cx, cy, width, height` |
| `conf` | confidence score |
| `cls` | class id |
| `names` | class id를 class name으로 바꾸는 mapping |

OpenCV에 사각형을 그릴 때는 보통 `xyxy`가 편하다.

```python
x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
```

중심점은 직접 계산할 수 있다.

```python
cx = (x1 + x2) / 2
cy = (y1 + y2) / 2
```

로봇 제어에서는 전체 이미지보다 이 중심점, box 크기, class, confidence가 더 중요해질 수 있다.

---

## 4. Confidence threshold와 오탐/미탐

`conf` threshold는 “얼마나 확신할 때 결과로 인정할 것인가”를 정하는 값이다.

```text
conf threshold 낮음
  -> 더 많이 잡음
  -> 오탐 증가 가능

conf threshold 높음
  -> 확실한 것만 잡음
  -> 미탐 증가 가능
```

처음에는 `0.25`, `0.5` 같은 값을 써볼 수 있지만, 실제 카메라 환경에서는 조명, 각도, 거리, 객체 크기에 따라 조정해야 한다.

---

## 5. NMS와 IoU

YOLO는 같은 객체 주변에 여러 box를 낼 수 있다. NMS는 중복 box를 줄이는 후처리다.

```text
IoU = 겹친 면적 / 합집합 면적
```

NMS threshold가 너무 낮으면 필요한 box까지 지워질 수 있고, 너무 높으면 중복 box가 남을 수 있다.

학습 단계에서는 다음 정도로 이해하면 된다.

```text
confidence
  -> 이 box 자체를 믿을지

IoU / NMS
  -> 겹치는 box 중 무엇을 남길지
```

---

## 6. 모델 크기와 실시간성

실시간 로봇에서는 정확도만 볼 수 없다.

속도에 영향을 주는 요소는 다음과 같다.

```text
YOLO 모델 크기
input image size(imgsz)
CPU/GPU 사용 여부
camera resolution
전처리/후처리 비용
show/save 옵션
```

예를 들어 `yolov8n.pt`는 가벼운 모델이라 실습에 적합하다. 하지만 정확도가 더 필요한 경우 큰 모델을 쓸 수 있고, 그만큼 FPS가 떨어질 수 있다.

---

## 7. Kalman Filter를 붙이는 이유

YOLO bbox는 프레임마다 조금씩 흔들릴 수 있다.

```text
객체는 가만히 있는데 box 중심점이 흔들림
조명 변화로 confidence가 흔들림
일부 프레임에서 detection이 끊김
객체가 빠르게 움직일 때 box가 튐
```

Kalman Filter는 이전 상태 예측과 현재 관측을 함께 사용해 더 안정적인 추정값을 만든다.

```text
predict
  이전 상태와 motion model로 현재 상태를 예측

update
  실제 관측값을 받아 예측을 보정
```

---

## 8. 상태 벡터 예시

`$SOURCE_NOTES/code/05.02.02.Webcam-Kalman.py`의 `BBoxKalmanTracker`는 bbox 중심점을 추적한다.

상태는 다음처럼 볼 수 있다.

```text
x = [cx, vx, cy, vy]^T
```

의미는 아래다.

| 상태 | 의미 |
|---|---|
| `cx` | bbox 중심 x 좌표 |
| `vx` | x 방향 속도 |
| `cy` | bbox 중심 y 좌표 |
| `vy` | y 방향 속도 |

관측값은 YOLO에서 얻은 중심점이다.

```text
z = [cx, cy]^T
```

즉, 속도는 직접 측정하지 않고 필터 내부에서 추정한다.

---

## 9. A, C, P, Q, R의 의미

Kalman Filter에서 자주 나오는 기호는 아래처럼 이해하면 된다.

| 기호 | 의미 | 실습에서의 감각 |
|---|---|---|
| `A` | 상태 전이 행렬 | 이전 위치/속도로 다음 위치 예측 |
| `C` 또는 `H` | 관측 행렬 | 상태 중 실제 측정되는 값만 꺼냄 |
| `P` | 현재 추정의 불확실성 | 내 추정이 얼마나 불안한가 |
| `Q` | motion model의 불확실성 | 움직임 예측을 얼마나 못 믿는가 |
| `R` | 센서 관측의 불확실성 | YOLO 중심점을 얼마나 못 믿는가 |

감각적으로는 다음과 같다.

```text
R을 크게 잡음
  -> YOLO 관측값을 덜 믿음
  -> 결과가 부드럽지만 늦게 따라갈 수 있음

R을 작게 잡음
  -> YOLO 관측값을 많이 믿음
  -> 빠르게 따라가지만 흔들림도 따라갈 수 있음

Q를 크게 잡음
  -> 움직임이 급변할 수 있다고 봄
  -> 예측 불확실성이 빨리 커짐

Q를 작게 잡음
  -> 움직임이 일정하다고 강하게 가정
  -> 급격한 움직임을 못 따라갈 수 있음
```

---

## 10. NIS가 왜 나오는가

`$SOURCE_NOTES/code/05.02.03.Kalman-NIS-Eval.py`는 `nis_log.csv`를 읽어 NIS를 분석한다.

NIS는 Normalized Innovation Squared의 줄임말이다.

```text
innovation
  = 실제 관측값 - 예측 관측값

NIS
  = innovation이 예상 불확실성에 비해 얼마나 큰지 보는 값
```

측정값이 `cx, cy` 두 개라면 측정 차원은 2다. 평균 NIS가 대략 2 근처라면 관측 노이즈 R 설정이 어느 정도 일관적이라고 볼 수 있다.

```text
평균 NIS가 너무 큼
  -> 실제 관측 오차가 예상보다 큼
  -> R을 너무 작게 잡았을 가능성

평균 NIS가 너무 작음
  -> 관측을 지나치게 불확실하다고 봄
  -> R을 너무 크게 잡았을 가능성
```

이 부분은 단순 실습을 넘어 “필터를 어떻게 평가할 것인가”로 이어지는 좋은 배경지식이다.

---

## 11. YOLO 파인튜닝 문서의 위치

`day_4/yolo_finetuning_pipeline_md/`에는 YOLO 파인튜닝 과정이 정리되어 있다.

```text
문제 정의
데이터 수집
라벨링
data.yaml 작성
baseline 학습
freeze/full/two-stage 실험
precision/recall/mAP 확인
export
실제 카메라 테스트
```

이 문서에서는 이 내용을 “이미 학습 모델을 완성했다”로 해석하면 안 된다. 대신 다음처럼 보는 것이 맞다.

```text
이후 특정 객체를 인식하는 프로젝트를 할 때 필요한 절차를 미리 정리한 자료
```

실제 프로젝트에서 중요한 것은 모델을 무작정 바꾸는 것이 아니라 데이터셋 품질, 라벨 일관성, 평가 기준, 실환경 테스트다.

---

## 12. ROS2 custom message와 연결

OpenCV 단독 YOLO 코드에서는 box를 화면에 그리면 끝날 수 있다.

ROS2에서는 다른 node가 결과를 써야 하므로 message로 publish해야 한다.

```text
YOLO result
  -> class_name
  -> confidence
  -> bbox [x1, y1, x2, y2]
  -> ObjectDetection.msg
  -> ObjectDetectionArray.msg
  -> topic publish
```

실제 연결 파일은 아래다.

```text
$ROS2_WS/src/ros2_foundation_interfaces/msg/ObjectDetection.msg
$ROS2_WS/src/ros2_foundation_interfaces/msg/ObjectDetectionArray.msg
$ROS2_WS/src/ros2_camera_examples/ros2_camera_examples/yolo_detection_publisher.py
```

이 흐름을 이해하면 “YOLO를 돌렸다”에서 끝나지 않고, detection 결과를 로봇 시스템의 데이터로 바꾸는 관점으로 넘어갈 수 있다.

---

## 13. 정리

YOLO/Kalman에서 가져갈 것은 아래다.

```text
YOLO는 class, confidence, bbox를 준다.
bbox 중심점과 크기는 로봇 판단에 사용할 수 있다.
conf threshold와 NMS는 오탐/미탐/중복 box를 조절한다.
Kalman Filter는 흔들리는 관측값을 예측/보정 구조로 안정화한다.
Q, R, P는 필터의 믿음과 불확실성을 조절하는 값이다.
NIS는 필터 파라미터가 말이 되는지 확인하는 평가 도구다.
```
