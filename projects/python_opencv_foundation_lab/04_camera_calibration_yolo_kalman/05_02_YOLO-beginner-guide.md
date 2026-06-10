# YOLO 입문 설명서

이 문서는 `pract/05.02.YOLO-Kalman.pdf`의 YOLO 파트를 참고해서, 초보자가 로봇 카메라 실습에서 YOLO를 어떻게 이해하고 써야 하는지 정리한 문서다.

기존 `05_02_YOLO-Kalman-code-analysis.md`가 노트북 코드 전체를 따라가는 분석 문서라면, 이 문서는 YOLO 자체를 이해하는 데 집중한다.

---

## 1. YOLO를 한 문장으로 설명하면

YOLO는 이미지나 카메라 화면 안에서 물체가 무엇인지, 어디에 있는지를 빠르게 찾아주는 객체 탐지 모델이다.

예를 들어 카메라 화면에 사람이 보이면 YOLO는 다음과 같은 정보를 준다.

```text
물체 이름: person
위치: x1=120, y1=80, x2=260, y2=420
확신도: 0.86
```

이것을 로봇 입장에서 해석하면 다음과 같다.

```text
"화면 안에 사람이 있고,
그 사람은 이 사각형 영역에 있으며,
모델은 86% 정도 확신하고 있다."
```

즉 YOLO는 로봇의 눈 역할을 한다.

---

## 2. 이미지 분류와 객체 탐지의 차이

YOLO를 이해하려면 먼저 이미지 분류와 객체 탐지의 차이를 알아야 한다.

### 2.1 이미지 분류

이미지 분류는 이미지 전체를 보고 하나의 답을 고르는 작업이다.

```text
질문: 이 사진은 무엇인가?
답: 고양이
```

예시:

```text
이미지 전체 → "person"
```

문제는 위치를 알려주지 않는다는 점이다.

로봇이 주행 중일 때 단순히 "사람이 있다"만 알면 부족하다. 사람이 왼쪽에 있는지, 오른쪽에 있는지, 가까운지, 먼지 알아야 움직임을 결정할 수 있다.

### 2.2 객체 탐지

객체 탐지는 이미지 안의 물체 종류와 위치를 동시에 찾는다.

```text
질문: 무엇이 어디에 있는가?
답: 사람은 왼쪽, 자동차는 오른쪽, 버스는 중앙
```

YOLO는 객체 탐지 모델이다.

| 구분 | 이미지 분류 | 객체 탐지 |
|---|---|---|
| 질문 | 이미지 전체가 무엇인가? | 무엇이 어디에 있는가? |
| 출력 | 클래스 이름 하나 | 클래스 이름 + 위치 박스 |
| 예시 | `person` | `person`, `[x1, y1, x2, y2]` |
| 로봇 활용 | 제한적 | 매우 중요 |

---

## 3. YOLO라는 이름의 의미

YOLO는 `You Only Look Once`의 줄임말이다.

직역하면 "단 한 번만 본다"는 뜻이다.

### 3.1 왜 단 한 번만 보는가

예전 방식의 객체 탐지는 이미지 안에서 물체가 있을 법한 영역을 많이 만들어놓고 하나씩 검사했다.

```text
후보 영역 1 검사
후보 영역 2 검사
후보 영역 3 검사
...
후보 영역 수천 개 검사
```

이 방식은 정확할 수 있지만 느리다.

YOLO는 이미지 전체를 한 번에 신경망에 넣고, 한 번의 추론으로 여러 물체의 위치와 종류를 동시에 예측한다.

```text
이미지 한 장 입력
      |
      v
YOLO 모델 한 번 실행
      |
      v
모든 박스 + 클래스 + 확신도 출력
```

그래서 YOLO는 빠르다.

### 3.2 로봇에서 빠른 속도가 중요한 이유

로봇은 카메라 화면을 보고 바로 판단해야 한다.

예를 들어 사람이 갑자기 앞에 나타났는데 탐지가 1초 늦으면 위험할 수 있다.

```text
카메라 프레임 입력
      |
      v
객체 탐지
      |
      v
사람이면 정지
      |
      v
모터 제어
```

이 전체 흐름이 빠르게 반복되어야 한다. 그래서 로봇에서는 정확도만큼 속도도 중요하다.

---

## 4. 1-Stage와 2-Stage 탐지 모델

객체 탐지 모델은 크게 1-Stage와 2-Stage 방식으로 나눌 수 있다.

### 4.1 2-Stage 방식

2-Stage 방식은 두 단계로 탐지한다.

```text
1단계: 물체가 있을 법한 후보 영역을 찾는다.
2단계: 각 후보 영역이 무엇인지 분류한다.
```

대표 모델은 Faster R-CNN, Mask R-CNN 등이 있다.

장점은 정확도가 높은 편이라는 것이다. 단점은 느리다는 것이다.

### 4.2 1-Stage 방식

1-Stage 방식은 위치 예측과 분류를 한 번에 처리한다.

```text
이미지 입력 → 위치와 클래스를 동시에 예측
```

YOLO는 1-Stage 계열이다.

| 구분 | 1-Stage | 2-Stage |
|---|---|---|
| 대표 모델 | YOLO, SSD, RetinaNet | Faster R-CNN, Mask R-CNN |
| 처리 방식 | 위치와 분류를 한 번에 예측 | 후보 영역을 찾고 나중에 분류 |
| 속도 | 빠름 | 느림 |
| 로봇 실시간성 | 유리함 | 불리함 |

로봇 카메라 실습에서 YOLO를 쓰는 이유는 바로 이 빠른 속도 때문이다.

---

## 5. YOLO가 실제로 주는 결과

YOLO를 실행하면 단순히 "사람"이라는 문자열만 나오는 것이 아니다.

주로 다음 네 가지를 받는다.

| 항목 | 예시 | 의미 |
|---|---|---|
| 클래스 | `person` | 물체 종류 |
| 클래스 ID | `0` | 물체 종류를 나타내는 숫자 |
| 바운딩 박스 | `[x1, y1, x2, y2]` | 물체 위치 |
| 신뢰도 | `0.86` | 모델이 얼마나 확신하는지 |

이 네 가지를 이해하면 YOLO 결과를 거의 다룰 수 있다.

---

## 6. Bounding Box 이해하기

Bounding Box는 물체를 감싸는 사각형이다.

YOLO는 물체 위치를 보통 사각형 좌표로 알려준다.

```text
(x1, y1) ----------------
   |                    |
   |       person       |
   |                    |
   ---------------- (x2, y2)
```

### 6.1 `xyxy`

`xyxy`는 왼쪽 위 좌표와 오른쪽 아래 좌표를 의미한다.

```python
x1, y1, x2, y2 = box.xyxy[0]
```

| 값 | 의미 |
|---|---|
| `x1` | 박스 왼쪽 좌표 |
| `y1` | 박스 위쪽 좌표 |
| `x2` | 박스 오른쪽 좌표 |
| `y2` | 박스 아래쪽 좌표 |

예를 들어 다음 값이 있다고 하자.

```text
x1 = 100
y1 = 50
x2 = 300
y2 = 450
```

뜻은 다음과 같다.

```text
왼쪽 위 점: (100, 50)
오른쪽 아래 점: (300, 450)
```

### 6.2 `xywh`

`xywh`는 중심점과 크기를 의미한다.

```python
cx, cy, w, h = box.xywh[0]
```

| 값 | 의미 |
|---|---|
| `cx` | 박스 중심 x 좌표 |
| `cy` | 박스 중심 y 좌표 |
| `w` | 박스 너비 |
| `h` | 박스 높이 |

로봇 제어에서는 `cx`, `cy`가 특히 중요하다.

```text
cx가 화면 중앙보다 작다 → 물체가 왼쪽에 있음
cx가 화면 중앙보다 크다 → 물체가 오른쪽에 있음
```

### 6.3 중심점 직접 계산

`xyxy`만 가지고 있어도 중심점은 직접 계산할 수 있다.

```python
cx = (x1 + x2) // 2
cy = (y1 + y2) // 2
```

예시:

```text
x1 = 100, x2 = 300
cx = (100 + 300) / 2 = 200
```

---

## 7. Confidence 이해하기

Confidence는 모델의 확신도다.

```python
conf = box.conf[0]
```

값은 보통 0과 1 사이로 나온다.

| confidence | 해석 |
|---:|---|
| `0.10` | 거의 믿기 어려움 |
| `0.45` | 애매함 |
| `0.70` | 어느 정도 믿을 수 있음 |
| `0.95` | 매우 확실함 |

실습에서는 보통 `0.5` 이상만 사용한다.

```python
results = model.predict("image.jpg", conf=0.5)
```

이 코드는 confidence가 0.5보다 낮은 탐지 결과를 버린다.

### 7.1 `conf` 값을 낮추면

더 많은 물체를 잡는다.

하지만 잘못 잡는 경우도 늘어난다.

```text
장점: 놓치는 물체가 줄어들 수 있음
단점: 오탐이 늘어날 수 있음
```

### 7.2 `conf` 값을 높이면

확실한 물체만 잡는다.

하지만 진짜 물체를 놓칠 수도 있다.

```text
장점: 결과가 깔끔해짐
단점: 멀리 있거나 작게 보이는 물체를 놓칠 수 있음
```

로봇 안전 정지처럼 놓치면 위험한 작업은 너무 높게 잡으면 안 된다. 반대로 휴대폰 감지처럼 오탐이 귀찮은 작업은 조금 높게 잡아도 된다.

---

## 8. Class와 `model.names`

YOLO 내부에서는 물체 이름을 숫자로 다룬다.

예를 들어 COCO 데이터셋 기준으로 자주 보는 클래스는 다음과 같다.

| ID | 이름 |
|---:|---|
| `0` | `person` |
| `1` | `bicycle` |
| `2` | `car` |
| `3` | `motorcycle` |
| `5` | `bus` |
| `7` | `truck` |
| `67` | `cell phone` |

YOLO 결과에서 클래스 ID를 꺼내는 코드는 다음과 같다.

```python
cls_id = int(box.cls[0])
```

이 숫자를 사람이 읽는 이름으로 바꾸려면 `model.names`를 사용한다.

```python
label = model.names[cls_id]
```

전체 흐름은 다음과 같다.

```python
cls_id = int(box.cls[0])
label = model.names[cls_id]
print(label)
```

---

## 9. YOLOv8 모델 종류

YOLOv8에는 크기가 다른 모델들이 있다.

```text
n < s < m < l < x
```

왼쪽으로 갈수록 빠르고 가볍다. 오른쪽으로 갈수록 더 무겁고 정확한 편이다.

| 모델 | 이름 | 특징 | 추천 상황 |
|---|---|---|---|
| `yolov8n.pt` | Nano | 가장 가볍고 빠름 | 실습, 웹캠, 저사양 장비 |
| `yolov8s.pt` | Small | 속도와 정확도 균형 | 일반 PC, 로봇 실습 |
| `yolov8m.pt` | Medium | 더 정확하지만 느림 | GPU 있는 PC |
| `yolov8l.pt` | Large | 무겁고 정확함 | 연구, 고성능 환경 |
| `yolov8x.pt` | X-Large | 가장 무거운 편 | 정확도 우선 분석 |

현재 실습에서는 `yolov8n.pt`가 적합하다.

```python
model = YOLO("yolov8n.pt")
```

처음 배우는 단계에서는 빠르게 실행되는 모델로 전체 흐름을 이해하는 것이 좋다.

---

## 10. YOLO 설치와 기본 실행

### 10.1 설치

강의자료에서는 CPU 기준 설치를 사용한다.

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install ultralytics numpy==1.26.4 opencv-python==4.10.0.84
```

각 라이브러리의 역할은 다음과 같다.

| 라이브러리 | 역할 |
|---|---|
| `torch` | 딥러닝 연산 |
| `torchvision` | 이미지 관련 PyTorch 도구 |
| `ultralytics` | YOLOv8 사용 라이브러리 |
| `numpy` | 배열 계산 |
| `opencv-python` | 이미지/영상 처리 |

### 10.2 가장 기본 코드

```python
from ultralytics import YOLO

model = YOLO("yolov8n.pt")
results = model.predict(source="bus.jpg", save=False)
```

이 코드는 다음 일을 한다.

```text
1. YOLO 클래스를 가져온다.
2. yolov8n.pt 모델을 불러온다.
3. bus.jpg 이미지에서 객체를 탐지한다.
4. 탐지 결과를 results에 저장한다.
```

---

## 11. `YOLO()` 함수 이해하기

```python
model = YOLO("yolov8n.pt")
```

`YOLO()`는 모델 파일을 읽어서 추론 가능한 모델 객체를 만든다.

| 항목 | 설명 |
|---|---|
| 입력 | 모델 파일 경로 또는 모델 이름 |
| 예시 | `"yolov8n.pt"` |
| 반환 | YOLO 모델 객체 |

`yolov8n.pt` 파일이 현재 폴더에 없으면 인터넷에서 자동 다운로드를 시도할 수 있다.

인터넷이 안 되는 환경에서는 미리 모델 파일을 준비해야 한다.

---

## 12. `model.predict()` 이해하기

```python
results = model.predict(source="bus.jpg", save=False)
```

`model.predict()`는 실제 추론을 실행하는 함수다.

| 인자 | 예시 | 의미 |
|---|---|---|
| `source` | `"bus.jpg"` | 입력 이미지, 영상, 폴더, 웹캠 번호 |
| `save` | `False` | 결과 이미지를 파일로 저장할지 여부 |
| `conf` | `0.5` | 최소 confidence 기준 |
| `classes` | `[0, 2]` | 특정 클래스만 탐지 |
| `imgsz` | `320` | 입력 이미지 크기 |
| `stream` | `True` | 결과를 generator 방식으로 받기 |
| `verbose` | `False` | 로그 출력을 줄이기 |
| `device` | `"cpu"` 또는 `0` | CPU/GPU 선택 |

### 12.1 이미지 파일 추론

```python
results = model.predict(source="bus.jpg")
```

### 12.2 웹캠 추론

```python
results = model.predict(source=0, show=True)
```

`source=0`은 기본 웹캠을 의미한다.

카메라가 여러 개면 `0`, `1`, `2` 중 맞는 번호를 찾아야 한다.

### 12.3 OpenCV 프레임 추론

로봇 카메라 실습에서는 보통 OpenCV로 프레임을 읽고 YOLO에 넣는다.

```python
success, frame = cap.read()
results = model.predict(frame, verbose=False)
```

이때 `frame`은 NumPy 배열이다.

---

## 13. `results` 객체 이해하기

YOLO 추론 결과는 `results`에 들어간다.

```python
results = model.predict("bus.jpg")
```

이미지 한 장을 넣으면 보통 `results[0]`에 결과가 들어 있다.

```python
result = results[0]
```

`result` 안에서 자주 쓰는 속성은 다음과 같다.

| 코드 | 의미 |
|---|---|
| `result.boxes` | 탐지된 박스 목록 |
| `result.plot()` | 박스와 라벨이 그려진 이미지 반환 |
| `result.names` | 클래스 이름 정보 |

---

## 14. 탐지 결과를 하나씩 읽기

기본 패턴은 다음과 같다.

```python
results = model.predict("bus.jpg", verbose=False)

for result in results:
    for box in result.boxes:
        x1, y1, x2, y2 = box.xyxy[0]
        conf = box.conf[0]
        cls_id = int(box.cls[0])
        label = model.names[cls_id]

        print(label, conf, x1, y1, x2, y2)
```

이 코드를 천천히 풀면 다음과 같다.

```text
results 안에는 이미지별 결과가 들어 있다.
result.boxes 안에는 한 이미지에서 탐지된 박스들이 들어 있다.
box 하나는 물체 하나의 탐지 결과다.
box.xyxy는 위치다.
box.conf는 확신도다.
box.cls는 클래스 번호다.
model.names는 클래스 번호를 이름으로 바꿔준다.
```

### 14.1 왜 `box.xyxy[0]`인가

`box.xyxy`는 내부적으로 이런 모양이다.

```text
[[x1, y1, x2, y2]]
```

그래서 좌표 4개를 꺼내려면 `[0]`을 붙인다.

```python
x1, y1, x2, y2 = box.xyxy[0]
```

### 14.2 왜 `int(box.cls[0])`인가

`box.cls[0]`은 텐서 형태의 값이다.

`model.names`에서 이름을 찾으려면 일반 정수로 바꿔주는 것이 안전하다.

```python
cls_id = int(box.cls[0])
```

---

## 15. 결과 시각화

YOLO 결과를 화면에 그리는 가장 쉬운 방법은 `plot()`이다.

```python
results = model.predict("bus.jpg")
annotated = results[0].plot()
```

`annotated`는 박스와 라벨이 그려진 이미지 배열이다.

OpenCV로 보여주려면 다음처럼 쓴다.

```python
cv2.imshow("YOLO Result", annotated)
cv2.waitKey(0)
cv2.destroyAllWindows()
```

웹캠에서는 매 프레임마다 보여준다.

```python
cv2.imshow("YOLO Result", annotated)
```

주의할 점은 `cv2.imshow()`는 GUI 화면을 띄울 수 있는 환경에서만 동작한다는 것이다. 서버나 WSL 환경처럼 화면 출력이 제한된 곳에서는 문제가 생길 수 있다.

---

## 16. 특정 클래스만 탐지하기

예를 들어 사람과 자동차만 탐지하고 싶다면 `classes`를 사용한다.

```python
results = model.predict("bus.jpg", classes=[0, 2], conf=0.5)
```

뜻은 다음과 같다.

```text
0번 person
2번 car
confidence 0.5 이상
```

이렇게 하면 관심 없는 클래스가 줄어든다.

로봇 실습에서는 다음처럼 활용할 수 있다.

```python
if label == "person" and conf > 0.5:
    print("긴급 정지")
```

---

## 17. NMS 이해하기

NMS는 Non-Maximum Suppression의 줄임말이다.

YOLO는 같은 물체에 대해 여러 박스를 후보로 만들 수 있다.

예를 들어 사람 한 명을 두고 다음처럼 여러 박스가 나올 수 있다.

```text
박스 A: confidence 0.92
박스 B: confidence 0.81
박스 C: confidence 0.63
```

NMS는 겹치는 박스들 중 가장 좋은 박스만 남긴다.

```text
겹치는 박스 여러 개
      |
      v
confidence 가장 높은 박스만 유지
```

### 17.1 IoU

NMS에서 겹침 정도를 판단할 때 IoU를 사용한다.

IoU는 Intersection over Union의 줄임말이다.

간단히 말하면 두 박스가 얼마나 겹치는지를 0부터 1 사이로 나타낸 값이다.

```text
0에 가까움: 거의 안 겹침
1에 가까움: 거의 같은 박스
```

초보 단계에서는 NMS를 직접 구현할 필요는 거의 없다. YOLO가 내부에서 처리해준다. 다만 같은 물체에 박스가 여러 개 생겼을 때 왜 하나만 남는지 이해하면 된다.

---

## 18. 실시간 웹캠 YOLO 구조

실시간 카메라 코드는 보통 다음 구조를 가진다.

```python
import cv2
from ultralytics import YOLO

model = YOLO("yolov8n.pt")
cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    results = model.predict(frame, stream=True, verbose=False)

    for result in results:
        annotated_frame = result.plot()
        cv2.imshow("YOLO", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
```

이 코드는 다음 순서로 동작한다.

```text
1. 웹캠 열기
2. 프레임 한 장 읽기
3. YOLO에 프레임 입력
4. 탐지 결과 그리기
5. 화면 출력
6. q 키를 누르면 종료
```

---

## 19. `stream=True`는 왜 쓰는가

```python
results = model.predict(frame, stream=True)
```

`stream=True`는 결과를 한꺼번에 리스트로 만들지 않고 generator 방식으로 처리하게 한다.

웹캠이나 영상처럼 프레임이 계속 들어오는 상황에서 메모리를 아끼고 지연을 줄이는 데 도움이 된다.

초보자 관점에서는 이렇게 기억하면 된다.

```text
이미지 한 장 테스트: stream 없어도 됨
웹캠/영상 처리: stream=True 권장
```

---

## 20. FPS와 속도 최적화

FPS는 Frames Per Second의 줄임말이다.

```text
1초에 몇 장의 프레임을 처리하는가
```

로봇 실습에서는 최소 15 FPS 이상, 가능하면 30 FPS에 가까울수록 좋다.

### 20.1 모델 크기 줄이기

가장 쉬운 방법은 작은 모델을 쓰는 것이다.

```python
model = YOLO("yolov8n.pt")
```

`yolov8n.pt`는 정확도는 조금 낮을 수 있지만 가장 빠르다.

### 20.2 이미지 크기 줄이기

```python
results = model.predict(frame, imgsz=320)
```

`imgsz`를 낮추면 빠르다.

하지만 작은 물체를 놓칠 수 있다.

| `imgsz` | 속도 | 작은 물체 탐지 |
|---:|---|---|
| `320` | 빠름 | 약해질 수 있음 |
| `640` | 기본 | 보통 |
| `1280` | 느림 | 좋아질 수 있음 |

### 20.3 confidence 조절

```python
results = model.predict(frame, conf=0.5)
```

`conf`를 적절히 조절하면 불필요한 결과를 줄일 수 있다.

### 20.4 GPU 사용

NVIDIA GPU가 있다면 GPU를 쓰는 것이 훨씬 빠를 수 있다.

```python
results = model.predict(frame, device=0)
```

또는:

```python
results = model.predict(frame, device="cuda:0")
```

CPU만 있는 노트북에서는 `yolov8n.pt`, `imgsz=320`, `conf=0.5` 정도로 시작하는 것이 좋다.

---

## 21. 로봇 제어에 필요한 YOLO 데이터

로봇이 YOLO 결과에서 주로 필요한 값은 다음과 같다.

| 값 | 로봇에서 쓰는 이유 |
|---|---|
| `label` | 어떤 물체인지 판단 |
| `conf` | 결과를 믿을지 판단 |
| `cx`, `cy` | 물체가 화면 어디에 있는지 판단 |
| `w`, `h` | 물체 크기, 거리 추정 단서 |

예를 들어 사람을 보면 멈추는 로직은 다음처럼 만들 수 있다.

```python
if label == "person" and conf > 0.5:
    command = "stop"
else:
    command = "go"
```

사람이 화면 왼쪽에 있으면 왼쪽으로 회전하는 로직은 다음처럼 생각할 수 있다.

```python
frame_center_x = frame.shape[1] // 2

if cx < frame_center_x:
    command = "turn_left"
else:
    command = "turn_right"
```

실제 로봇에서는 더 부드러운 제어가 필요하지만, 기본 아이디어는 이렇다.

---

## 22. YOLO와 거리 추정

YOLO 자체가 정확한 실제 거리를 바로 알려주는 것은 아니다.

YOLO는 픽셀 좌표를 알려준다.

```text
사람 박스 높이: 300픽셀
```

실제 거리로 바꾸려면 카메라 초점거리와 실제 물체 크기가 필요하다.

사람 키를 기준으로 아주 단순화하면 다음 식을 사용할 수 있다.

```python
distance = (REAL_HEIGHT * focal_length) / pixel_height
```

| 값 | 의미 |
|---|---|
| `REAL_HEIGHT` | 실제 물체 높이. 예: 사람 1.7m |
| `focal_length` | 카메라 초점거리. 캘리브레이션으로 얻음 |
| `pixel_height` | YOLO 박스의 픽셀 높이 |

이 방식은 단순한 추정이다.

사람이 구부정하게 있거나, 카메라 각도가 다르거나, 박스가 부정확하면 오차가 커질 수 있다. 그래도 실습 단계에서는 거리 개념을 이해하는 데 좋다.

---

## 23. YOLO 결과가 흔들리는 이유

웹캠에서 YOLO를 돌려보면 박스가 조금씩 흔들릴 수 있다.

이유는 다음과 같다.

```text
조명 변화
카메라 노이즈
사람의 작은 움직임
모델의 프레임별 판단 차이
```

그래서 같은 사람이 가만히 있어도 중심점이 조금씩 바뀐다.

```text
프레임 1: cx = 320
프레임 2: cx = 326
프레임 3: cx = 318
프레임 4: cx = 323
```

로봇 제어에 이 값을 그대로 넣으면 움직임이 떨릴 수 있다.

이때 Kalman Filter를 붙이면 중심점 움직임을 부드럽게 만들 수 있다.

```text
YOLO: 현재 프레임에서 중심점 측정
Kalman Filter: 이전 움직임을 참고해서 중심점 안정화
```

---

## 24. YOLO를 처음 쓸 때 자주 나는 문제

### 24.1 모델 파일을 못 찾음

```text
FileNotFoundError 또는 자동 다운로드 실패
```

해결:

```text
yolov8n.pt 파일이 현재 실행 폴더에 있는지 확인한다.
인터넷이 안 되면 미리 모델 파일을 받아둔다.
```

### 24.2 이미지 파일 경로 오류

```python
results = model.predict("bus.jpg")
```

현재 작업 디렉터리에 `bus.jpg`가 없으면 실패한다.

해결:

```python
results = model.predict("/home/jaeholee/work/roooooboot/day_4/prac/bus.jpg")
```

처럼 절대 경로를 사용하면 헷갈림이 줄어든다.

### 24.3 카메라 번호 오류

```python
cap = cv2.VideoCapture(0)
```

기본 카메라가 꼭 0번이 아닐 수 있다.

노트북, USB 카메라, 가상 카메라가 섞이면 `1`, `2`일 수도 있다.

### 24.4 너무 느림

CPU에서 YOLO를 돌리면 느릴 수 있다.

해결 순서:

```text
1. yolov8n.pt 사용
2. imgsz=320 사용
3. conf 적절히 조절
4. GPU 가능하면 device=0 사용
5. 엣지 장치에서는 ONNX, TensorRT 같은 변환 고려
```

### 24.5 탐지 결과가 너무 많음

필요한 클래스만 남긴다.

```python
results = model.predict(frame, classes=[0], conf=0.5)
```

위 코드는 사람만 탐지한다.

---

## 25. 실습용 최소 예제

이미지 한 장에서 YOLO 결과를 출력하는 최소 예제다.

```python
from ultralytics import YOLO

model = YOLO("yolov8n.pt")
results = model.predict("bus.jpg", conf=0.5, verbose=False)

for result in results:
    for box in result.boxes:
        x1, y1, x2, y2 = box.xyxy[0]
        cx, cy, w, h = box.xywh[0]
        conf = box.conf[0]
        cls_id = int(box.cls[0])
        label = model.names[cls_id]

        print(f"{label}: conf={conf:.2f}, center=({cx:.0f}, {cy:.0f})")
```

이 코드를 이해하면 YOLO 기본기는 잡힌 것이다.

---

## 26. 로봇 카메라용 기본 예제

웹캠에서 사람만 탐지하고 중심점을 표시하는 예제다.

```python
import cv2
from ultralytics import YOLO

model = YOLO("yolov8n.pt")
cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    results = model.predict(frame, classes=[0], conf=0.5, imgsz=320, verbose=False)

    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2

            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
            cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
            cv2.putText(frame, "person",
                        (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (255, 255, 255),
                        2)

    cv2.imshow("YOLO Person Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
```

이 예제의 핵심은 다음이다.

```text
classes=[0]  → 사람만 탐지
conf=0.5     → 50% 이상 확신하는 결과만 사용
imgsz=320    → 속도를 높이기 위해 작은 입력 크기 사용
```

---

## 27. YOLO 공부 순서 추천

처음부터 복잡한 구조 논문을 보려고 하면 어렵다.

지금 단계에서는 다음 순서가 좋다.

1. 이미지 한 장에서 YOLO 실행하기
2. `result.boxes`에서 좌표, confidence, class 꺼내기
3. 웹캠 프레임에 YOLO 적용하기
4. `classes`, `conf`, `imgsz`로 결과 조절하기
5. FPS 측정하기
6. 중심점 `cx`, `cy`를 로봇 제어 값으로 넘기기
7. 박스 흔들림이 보이면 Kalman Filter 붙이기
8. 속도가 부족하면 GPU, ONNX, TensorRT 같은 최적화 고민하기

---

## 28. 꼭 기억할 요약

YOLO를 처음 배울 때는 아래만 확실히 잡아도 된다.

| 키워드 | 의미 |
|---|---|
| YOLO | 빠른 객체 탐지 모델 |
| Object Detection | 물체 종류와 위치를 동시에 찾는 작업 |
| Bounding Box | 물체를 감싸는 사각형 |
| `xyxy` | 왼쪽 위, 오른쪽 아래 좌표 |
| `xywh` | 중심점, 너비, 높이 |
| Confidence | 모델의 확신도 |
| Class ID | 물체 종류를 나타내는 숫자 |
| `model.names` | Class ID를 이름으로 바꾸는 딕셔너리 |
| `conf` | 낮은 신뢰도 결과를 제거하는 기준 |
| `classes` | 원하는 클래스만 탐지하는 옵션 |
| `imgsz` | 속도와 정확도를 조절하는 입력 크기 |
| `stream=True` | 웹캠/영상에서 효율적으로 처리하는 옵션 |

---

## 29. 실습 체크리스트

아래 항목을 직접 해보면 YOLO 기초는 충분히 잡힌다.

```text
[ ] yolov8n.pt 모델을 불러올 수 있다.
[ ] 이미지 한 장에서 객체 탐지를 실행할 수 있다.
[ ] 탐지 결과에서 label, confidence, xyxy 좌표를 출력할 수 있다.
[ ] xyxy 좌표로 중심점 cx, cy를 계산할 수 있다.
[ ] classes=[0]으로 사람만 탐지할 수 있다.
[ ] conf=0.5로 낮은 신뢰도 결과를 제거할 수 있다.
[ ] 웹캠 프레임에 YOLO를 적용할 수 있다.
[ ] imgsz=320과 imgsz=640의 속도 차이를 비교할 수 있다.
[ ] 탐지 중심점을 로봇 제어 명령으로 연결하는 아이디어를 설명할 수 있다.
```

---

## 30. 이 문서에서 참고한 자료

- `/home/jaeholee/work/roooooboot/pract/05.02.YOLO-Kalman.pdf`
- `/home/jaeholee/work/roooooboot/day_4/05_02_YOLO-Kalman-code-analysis.md`

