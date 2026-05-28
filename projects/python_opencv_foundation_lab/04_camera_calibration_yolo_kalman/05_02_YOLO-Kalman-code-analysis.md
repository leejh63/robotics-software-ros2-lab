# 05_02_YOLO-Kalman.ipynb 상세 분석

이 문서는 `prac/05_02_YOLO-Kalman.ipynb`를 처음 보는 사람도 따라갈 수 있도록, YOLOv8 객체 탐지와 Kalman Filter 추적 안정화 흐름을 코드 중심으로 풀어 쓴 해설 문서다.

이 노트북은 한마디로 말하면 다음 일을 한다.

```text
YOLOv8 모델 불러오기
        |
        v
이미지에서 객체 탐지
        |
        v
탐지된 박스, 신뢰도, 클래스, 중심점 좌표 읽기
        |
        v
필요한 클래스와 신뢰도 기준으로 결과 필터링
        |
        v
추론 속도, FPS 측정
        |
        v
Kalman Filter로 노이즈가 있는 위치 측정값을 부드럽게 보정
        |
        v
YOLO 중심점 좌표(cx, cy)에 Kalman Filter를 적용하는 구조 이해
```

---

## 1. 전체 목적

카메라 기반 로봇이나 자율주행 장비에서는 카메라 영상에서 물체를 찾는 것만으로는 부족하다.

YOLO는 다음 정보를 알려준다.

```text
무엇이 있는가?    예: person, bus, car
어디에 있는가?    예: x=120, y=80 부근
얼마나 확실한가?  예: confidence=0.87
```

하지만 실제 영상에서는 탐지 위치가 프레임마다 조금씩 흔들릴 수 있다.

```text
프레임 1: 사람 중심 x = 320
프레임 2: 사람 중심 x = 326
프레임 3: 사람 중심 x = 318
프레임 4: 사람 중심 x = 329
```

사람이 실제로는 거의 가만히 있어도, YOLO 탐지 박스가 매 프레임 조금씩 바뀌면 중심점도 흔들린다. 이 값을 그대로 로봇 제어에 넣으면 조향이나 정지 판단이 불안정해질 수 있다.

그래서 이 노트북은 다음 두 가지를 함께 배운다.

| 기술 | 역할 |
|---|---|
| YOLOv8 | 이미지 안에서 객체의 종류와 위치를 찾는다. |
| Kalman Filter | 흔들리는 위치 측정값을 예측과 보정으로 부드럽게 만든다. |

---

## 2. 먼저 알아야 할 핵심 용어

### 2.1 Object Detection

객체 탐지는 이미지 안에서 물체의 종류와 위치를 동시에 찾는 작업이다.

| 작업 | 질문 | 결과 |
|---|---|---|
| 이미지 분류 | 이미지 전체가 무엇인가? | `bus` |
| 객체 탐지 | 무엇이 어디에 있는가? | `person` at `[x1, y1, x2, y2]` |

로봇에서는 단순히 "사람이 있다"보다 "사람이 화면 왼쪽 앞에 있다"가 훨씬 중요하다. 위치 정보가 있어야 회피, 정지, 추종 같은 제어를 할 수 있기 때문이다.

### 2.2 Bounding Box

Bounding Box는 객체를 감싸는 사각형이다.

YOLO 결과에서는 주로 두 가지 좌표 표현을 사용한다.

| 표현 | 형태 | 의미 |
|---|---|---|
| `xyxy` | `[x1, y1, x2, y2]` | 왼쪽 위 점과 오른쪽 아래 점 |
| `xywh` | `[cx, cy, w, h]` | 중심점, 너비, 높이 |

예를 들어 `xyxy = [100, 50, 300, 250]`이면 다음 뜻이다.

```text
x1 = 100  왼쪽 경계
y1 = 50   위쪽 경계
x2 = 300  오른쪽 경계
y2 = 250  아래쪽 경계
```

이 박스의 중심점은 다음처럼 계산할 수 있다.

```python
cx = (x1 + x2) / 2
cy = (y1 + y2) / 2
```

`xywh`는 이 중심점을 이미 계산해서 제공한다.

### 2.3 Confidence

Confidence는 모델이 탐지 결과를 얼마나 확신하는지 나타내는 값이다.

```text
0.0에 가까움: 거의 믿기 어려움
1.0에 가까움: 매우 확실함
```

실무에서는 보통 너무 낮은 confidence를 버린다.

```python
model.predict("bus.jpg", conf=0.5)
```

위 코드는 confidence가 `0.5` 이상인 결과만 남기겠다는 뜻이다.

### 2.4 Class ID

YOLO는 물체 이름을 바로 문자열로만 다루지 않고, 내부적으로 숫자 ID를 사용한다.

COCO 데이터셋 기준으로 자주 쓰는 클래스는 다음과 같다.

| Class ID | 이름 |
|---:|---|
| `0` | `person` |
| `1` | `bicycle` |
| `2` | `car` |
| `5` | `bus` |
| `7` | `truck` |

코드에서는 `model.names`를 이용해서 ID를 이름으로 바꾼다.

```python
cls_id = int(box.cls[0])
label = model.names[cls_id]
```

---

## 3. 설치 코드 분석

노트북에는 CPU 환경 기준 설치 명령이 적혀 있다.

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install ultralytics numpy==1.26.4 opencv-python==4.10.0.84
```

각 패키지의 역할은 다음과 같다.

| 패키지 | 역할 |
|---|---|
| `torch` | 딥러닝 연산을 수행하는 PyTorch 본체 |
| `torchvision` | 이미지 처리와 비전 모델 관련 PyTorch 도구 |
| `ultralytics` | YOLOv8을 쉽게 사용할 수 있게 해주는 라이브러리 |
| `numpy` | 배열, 행렬 계산 |
| `opencv-python` | 이미지 읽기, 카메라 입력, 영상 처리 |
| `matplotlib` | 결과 시각화 |

주의할 점은 첫 번째 명령이 CPU 전용 PyTorch를 설치한다는 것이다.

```bash
--index-url https://download.pytorch.org/whl/cpu
```

이 옵션으로 설치하면 NVIDIA GPU가 있어도 PyTorch가 CUDA를 사용하지 못할 수 있다.

GPU 사용 방법은 문서 뒤쪽의 `12. CPU에서 GPU로 바꾸는 방법`에 따로 정리했다.

---

## 4. Import 코드 분석

노트북의 첫 번째 코드 셀이다.

```python
import time
import numpy as np
from ultralytics import YOLO
import cv2
import matplotlib.pyplot as plt
```

### 4.1 `import time`

`time`은 실행 시간을 측정할 때 사용한다.

노트북에서는 FPS 계산에 사용한다.

```python
start = time.time()
# 여러 번 추론
elapsed = time.time() - start
fps = N / elapsed
```

| 함수 | 인자 | 반환값 | 의미 |
|---|---|---|---|
| `time.time()` | 없음 | `float` | 현재 시각을 초 단위로 반환한다. |

`time.time()`의 반환값은 사람이 읽기 좋은 시각이라기보다는 "기준 시점 이후 몇 초가 지났는가"에 가까운 숫자다. 두 번 호출한 값을 빼면 걸린 시간을 알 수 있다.

### 4.2 `import numpy as np`

`numpy`는 행렬과 배열 계산에 사용한다.

노트북에서는 Kalman Filter의 행렬 계산에 핵심적으로 쓰인다.

```python
self.A = np.array([[1, dt],
                   [0,  1]], dtype=float)
```

### 4.3 `from ultralytics import YOLO`

Ultralytics 라이브러리에서 YOLO 클래스를 가져온다.

```python
model = YOLO("yolov8n.pt")
```

`YOLO` 객체는 모델 로드, 추론, 학습, 저장, 결과 시각화 등을 처리하는 중심 객체다.

### 4.4 `import cv2`

OpenCV 라이브러리다.

노트북에서는 이미지를 읽는 데 사용한다.

```python
image = cv2.imread("bus.jpg")
```

OpenCV는 기본적으로 이미지를 BGR 순서로 읽는다. Matplotlib은 RGB 순서를 기대하므로 시각화할 때 색상 순서를 바꿔야 한다.

```python
plt.imshow(annotated[:, :, ::-1])
```

### 4.5 `import matplotlib.pyplot as plt`

그래프나 이미지를 출력할 때 사용한다.

```python
plt.figure(figsize=(10, 6))
plt.imshow(image)
plt.axis("off")
plt.show()
```

---

## 5. YOLO 모델 로드

노트북 코드다.

```python
# 1. 모델 로드 (Nano 모델 - 가장 가벼움)
model = YOLO('yolov8n.pt')
print(f"클래스 목록: {model.names}")
```

### 5.1 `YOLO('yolov8n.pt')`

`YOLO()`는 모델 파일을 읽어서 추론 가능한 객체로 만든다.

| 항목 | 설명 |
|---|---|
| 함수/클래스 | `YOLO()` |
| 주요 인자 | 모델 파일 경로 또는 모델 이름 |
| 예시 | `'yolov8n.pt'` |
| 반환값 | YOLO 모델 객체 |

`yolov8n.pt`의 의미는 다음과 같다.

```text
yolo     YOLO 계열 모델
v8       YOLOv8 버전
n        nano 모델
.pt      PyTorch 모델 파일
```

YOLOv8 모델 크기는 보통 다음 순서로 커진다.

```text
n < s < m < l < x
```

| 모델 | 특징 | 추천 상황 |
|---|---|---|
| `yolov8n.pt` | 가장 빠르고 가벼움 | 실습, 저사양 장비, 실시간 처리 |
| `yolov8s.pt` | 속도와 정확도 균형 | 일반적인 PC, 로봇 실습 |
| `yolov8m.pt` | 더 정확하지만 느림 | GPU가 있는 PC |
| `yolov8l.pt`, `yolov8x.pt` | 더 크고 무거움 | 정확도가 특히 중요한 분석 |

### 5.2 `model.names`

`model.names`는 클래스 번호와 이름의 매핑이다.

예시는 다음과 비슷하다.

```python
{
    0: "person",
    1: "bicycle",
    2: "car",
    ...
}
```

YOLO 결과의 `box.cls`는 숫자로 나오므로, 사람이 읽기 좋게 바꾸려면 `model.names`를 사용한다.

```python
label = model.names[int(box.cls[0])]
```

---

## 6. 이미지 파일 추론

노트북 코드다.

```python
# 2. 이미지 파일에서 추론
# https://ultralytics.com/images/bus.jpg
results = model.predict(source='bus.jpg', save=False)
```

### 6.1 `model.predict()`

`model.predict()`는 이미지, 영상, 웹캠, 배열 등을 입력으로 받아 객체 탐지를 수행한다.

| 항목 | 설명 |
|---|---|
| 함수 | `model.predict()` |
| 역할 | 입력 이미지나 영상에서 객체 탐지 |
| 반환값 | `Results` 객체들의 리스트 |

노트북에서 사용한 인자는 다음과 같다.

| 인자 | 값 | 의미 |
|---|---|---|
| `source` | `'bus.jpg'` | 추론할 이미지 파일 경로 |
| `save` | `False` | 탐지 결과 이미지를 파일로 저장하지 않음 |

자주 쓰는 추가 인자는 다음과 같다.

| 인자 | 예시 | 의미 |
|---|---|---|
| `conf` | `0.5` | confidence가 이 값 이상인 결과만 남김 |
| `classes` | `[0, 2]` | 특정 클래스 ID만 탐지 |
| `imgsz` | `320` 또는 `640` | 모델에 넣을 이미지 크기 |
| `verbose` | `False` | 추론 로그 출력 줄이기 |
| `stream` | `True` | 긴 영상이나 웹캠에서 결과를 generator로 받기 |
| `device` | `'cpu'`, `0`, `'cuda:0'` | CPU 또는 GPU 선택 |
| `half` | `True` | GPU에서 FP16 반정밀도 사용 |

### 6.2 반환값 `results`

`results`는 보통 리스트처럼 다룬다.

```python
results[0]
```

이미지 한 장을 넣으면 결과도 보통 한 개다. 여러 장을 넣으면 입력 개수만큼 결과가 들어간다.

```text
results
  |
  +-- results[0]  첫 번째 이미지의 탐지 결과
        |
        +-- boxes  탐지된 박스들
        +-- names  클래스 이름 정보
        +-- plot() 시각화 이미지 생성
```

### 6.3 `len(results[0].boxes)`

노트북 코드다.

```python
print(f"탐지된 객체 수: {len(results[0].boxes)}")
```

`results[0].boxes`는 탐지된 bounding box 목록이다.

| 코드 | 의미 |
|---|---|
| `results[0]` | 첫 번째 입력 이미지의 결과 |
| `.boxes` | 그 이미지에서 탐지된 박스들 |
| `len(...)` | 박스 개수, 즉 탐지된 객체 수 |

주의할 점은 "탐지된 객체 수"가 실제 객체 수와 항상 같지는 않다는 것이다. confidence가 낮아 누락될 수도 있고, 같은 물체가 중복 탐지될 수도 있다. YOLO 내부의 NMS가 중복 박스를 줄여주지만 완벽하지는 않다.

---

## 7. YOLO 결과에서 핵심 데이터 꺼내기

노트북 코드다.

```python
results = model('bus.jpg')
for result in results:
    boxes = result.boxes
    for box in boxes:
        x1, y1, x2, y2 = box.xyxy[0]   # 좌상단, 우하단 좌표
        conf = box.conf[0]             # 신뢰도 점수
        cls_id = int(box.cls[0])       # 클래스 번호
        label = model.names[cls_id]    # 물체 이름

        print(f"발견: {label:10s} | 위치: ({x1:.0f}, {y1:.0f}) ~ ({x2:.0f}, {y2:.0f}) | 확률: {conf:.2f}")
```

여기서 `model('bus.jpg')`는 `model.predict('bus.jpg')`와 비슷하게 동작한다. Ultralytics YOLO 객체는 함수처럼 호출할 수 있게 만들어져 있다.

### 7.1 반복 구조

```python
for result in results:
```

입력 이미지가 여러 개일 수 있으므로 `results`를 반복한다.

```python
for box in boxes:
```

한 이미지 안에 탐지된 박스가 여러 개일 수 있으므로 `boxes`도 반복한다.

### 7.2 `box.xyxy`

```python
x1, y1, x2, y2 = box.xyxy[0]
```

| 코드 | 의미 |
|---|---|
| `box.xyxy` | 박스 좌표를 `[x1, y1, x2, y2]` 형태로 담은 텐서 |
| `[0]` | 첫 번째 박스 좌표 행을 꺼냄 |
| `x1, y1` | 왼쪽 위 좌표 |
| `x2, y2` | 오른쪽 아래 좌표 |

왜 `[0]`을 붙이는지 헷갈릴 수 있다. `box.xyxy`는 내부적으로 2차원 형태를 유지한다.

```text
[[x1, y1, x2, y2]]
```

그래서 실제 좌표 네 개를 꺼내려면 첫 번째 행인 `[0]`을 선택한다.

### 7.3 `box.conf`

```python
conf = box.conf[0]
```

`box.conf`는 해당 박스의 confidence다.

| 값 | 의미 |
|---|---|
| `0.20` | 낮은 확신 |
| `0.50` | 보통 기준선으로 자주 사용 |
| `0.90` | 매우 높은 확신 |

### 7.4 `box.cls`

```python
cls_id = int(box.cls[0])
```

`box.cls[0]`는 클래스 번호다. 텐서 형태로 나오기 때문에 `int()`로 일반 정수로 바꿔준다.

```python
label = model.names[cls_id]
```

그 정수를 클래스 이름으로 바꾼다.

### 7.5 출력 포맷

```python
f"{label:10s}"
```

문자열을 10칸 폭으로 맞춰 출력한다. 표처럼 정렬해서 보기 위해 사용한다.

```python
f"{x1:.0f}"
```

소수점 없이 출력한다. 좌표는 내부적으로 소수일 수 있지만, 화면 픽셀 좌표를 볼 때는 정수로 보는 것이 편하다.

```python
f"{conf:.2f}"
```

confidence를 소수점 둘째 자리까지 출력한다.

---

## 8. 중심점 좌표 계산

노트북 코드다.

```python
results = model('bus.jpg')
print("=== 탐지 결과 (중심점 좌표) ===")
for result in results:
    for box in result.boxes:
        # xywh: [center_x, center_y, width, height]
        cx, cy, w, h = box.xywh[0]
        conf = box.conf[0]
        label = model.names[int(box.cls[0])]

        # 로봇 제어 로직 예시: 사람이 감지되면 긴급 정지
        action = "긴급 정지!" if label == 'person' and conf > 0.5 else "계속 주행"
        print(f"[{label:10s}] 중심: ({cx:.0f}, {cy:.0f}) | 크기: {w:.0f}x{h:.0f} | conf: {conf:.2f} | 명령: {action}")
```

### 8.1 `box.xywh`

```python
cx, cy, w, h = box.xywh[0]
```

| 값 | 의미 |
|---|---|
| `cx` | bounding box 중심의 x 좌표 |
| `cy` | bounding box 중심의 y 좌표 |
| `w` | bounding box 너비 |
| `h` | bounding box 높이 |

로봇 제어에서는 `xyxy`보다 `xywh`가 더 직관적일 때가 많다.

예를 들어 화면 가운데가 `x=320`인 카메라에서 사람의 중심점 `cx`가 `200`이면 왼쪽에 있는 것이다.

```text
cx < 화면 중앙: 왼쪽
cx > 화면 중앙: 오른쪽
```

박스 높이 `h`나 너비 `w`는 거리 추정의 단서가 될 수도 있다. 같은 사람이라면 가까울수록 화면에서 크게 보인다.

### 8.2 조건부 명령

```python
action = "긴급 정지!" if label == 'person' and conf > 0.5 else "계속 주행"
```

이 코드는 Python의 조건 표현식이다.

```python
A if 조건 else B
```

뜻은 다음과 같다.

```text
조건이 참이면 A
조건이 거짓이면 B
```

노트북에서는 다음 조건을 사용한다.

```python
label == 'person' and conf > 0.5
```

즉, 탐지된 물체가 사람이고 confidence가 0.5보다 크면 긴급 정지를 출력한다.

실제 로봇에 연결할 때는 이 부분이 모터 정지 명령, 경고음, 제어 플래그 등으로 바뀔 수 있다.

---

## 9. 결과 시각화

노트북 코드다.

```python
results = model('bus.jpg')
for result in results:
    annotated = result.plot()  # BGR 배열 반환

plt.figure(figsize=(10, 6))
plt.imshow(annotated[:, :, ::-1])  # BGR -> RGB 변환
plt.title("YOLOv8 Detection")
plt.axis('off')
plt.tight_layout()
plt.show()
```

### 9.1 `result.plot()`

`result.plot()`은 탐지 박스와 라벨이 그려진 이미지를 만들어준다.

| 항목 | 설명 |
|---|---|
| 함수 | `result.plot()` |
| 인자 | 생략 가능 |
| 반환값 | 박스와 라벨이 그려진 이미지 배열 |
| 반환 배열 색상 | OpenCV 스타일의 BGR |

주의할 점은 `result.plot()`의 반환 이미지가 BGR 순서라는 것이다.

### 9.2 `annotated[:, :, ::-1]`

```python
plt.imshow(annotated[:, :, ::-1])
```

이 코드는 BGR 이미지를 RGB로 뒤집는다.

이미지 배열은 보통 다음 차원을 가진다.

```text
height x width x channel
```

채널 순서가 BGR이면 다음과 같다.

```text
channel 0 = Blue
channel 1 = Green
channel 2 = Red
```

`::-1`은 마지막 축을 거꾸로 뒤집는다는 뜻이다.

```text
BGR -> RGB
```

만약 이 변환을 하지 않으면 빨간색과 파란색이 뒤바뀐 이상한 색으로 보일 수 있다.

### 9.3 Matplotlib 함수들

| 함수 | 주요 인자 | 의미 |
|---|---|---|
| `plt.figure()` | `figsize=(10, 6)` | 출력 그림 크기 설정 |
| `plt.imshow()` | 이미지 배열 | 이미지를 화면에 표시 |
| `plt.title()` | 제목 문자열 | 그래프 제목 |
| `plt.axis('off')` | `'off'` | x/y 축 눈금 숨김 |
| `plt.tight_layout()` | 없음 | 여백 자동 정리 |
| `plt.show()` | 없음 | 실제 화면에 표시 |

---

## 10. 탐지 결과 필터링

노트북 코드다.

```python
# 사람(0)과 자동차(2)만 탐지, 신뢰도 0.5 이상만 표시
results = model.predict('bus.jpg', classes=[0, 2], conf=0.5)

print("=== 필터링 결과 (사람 + 자동차만) ===")
for result in results:
    for box in result.boxes:
        label = model.names[int(box.cls[0])]
        conf = box.conf[0]
        print(f"  {label}: conf={conf:.2f}")
```

### 10.1 `classes=[0, 2]`

`classes`는 탐지하고 싶은 클래스 ID 목록이다.

```python
classes=[0, 2]
```

뜻은 다음과 같다.

```text
0번 person
2번 car
```

즉, 사람과 자동차만 남긴다.

장점은 다음과 같다.

| 장점 | 설명 |
|---|---|
| 결과가 단순해짐 | 관심 없는 객체를 무시할 수 있다. |
| 후처리 쉬움 | 로봇 제어 조건문이 단순해진다. |
| 오탐 대응 | 특정 작업과 무관한 클래스를 제거할 수 있다. |

### 10.2 `conf=0.5`

confidence가 0.5 이상인 결과만 반환한다.

낮게 설정하면 더 많이 탐지하지만 오탐이 늘 수 있다.

```text
conf 낮음: 민감함, 오탐 증가 가능
conf 높음: 보수적, 미탐 증가 가능
```

실습에서는 `0.5`가 이해하기 쉬운 기준값이지만, 실제 환경에서는 카메라 위치, 조명, 물체 종류에 따라 조정해야 한다.

---

## 11. FPS 측정

노트북 코드다.

```python
model = YOLO('yolov8n.pt')
image = cv2.imread('bus.jpg')

N = 30  # 측정 횟수
start = time.time()

for _ in range(N):
    results = model.predict(image, verbose=False)

elapsed = time.time() - start
fps = N / elapsed

print(f"평균 FPS: {fps:.1f} (총 {elapsed:.2f}초 / {N}회)")
print(f"실시간 제어 적합 여부: {'✓ 적합 (15FPS 이상)' if fps >= 15 else '✗ 부적합 (너무 느림)'}")
```

### 11.1 `cv2.imread()`

```python
image = cv2.imread('bus.jpg')
```

| 항목 | 설명 |
|---|---|
| 함수 | `cv2.imread()` |
| 인자 | 이미지 파일 경로 |
| 반환값 | 이미지 배열 또는 `None` |
| 색상 순서 | BGR |

이미지 경로가 틀리면 `None`을 반환한다. 실무에서는 다음 확인을 넣는 것이 좋다.

```python
image = cv2.imread("bus.jpg")
if image is None:
    raise FileNotFoundError("bus.jpg를 읽지 못했습니다.")
```

### 11.2 `N = 30`

30번 반복 추론해서 평균 속도를 잰다.

한 번만 측정하면 첫 실행 초기화 비용 때문에 값이 흔들릴 수 있다. 여러 번 반복하면 평균 속도를 더 안정적으로 볼 수 있다.

### 11.3 FPS 계산

```python
elapsed = time.time() - start
fps = N / elapsed
```

FPS는 Frames Per Second, 즉 1초에 처리한 이미지 수다.

예를 들어 30장을 2초에 처리하면 다음과 같다.

```text
FPS = 30 / 2 = 15
```

일반적인 기준은 다음과 같이 볼 수 있다.

| FPS | 느낌 |
|---:|---|
| 5 FPS 이하 | 많이 끊김 |
| 10 FPS | 느리지만 상황 파악 가능 |
| 15 FPS | 간단한 로봇 제어에 사용 가능 |
| 30 FPS 이상 | 꽤 부드러운 실시간 처리 |

### 11.4 `verbose=False`

```python
results = model.predict(image, verbose=False)
```

`verbose=False`는 매번 추론 로그가 출력되지 않게 한다.

반복 측정할 때 로그가 너무 많이 나오면 보기 불편하고, 출력 자체도 약간의 시간을 잡아먹을 수 있다.

---

## 12. `imgsz`로 속도 개선하기

노트북 코드다.

```python
# imgsz 축소로 속도 향상 비교
start = time.time()
for _ in range(N):
    results = model.predict(image, imgsz=320, verbose=False)
elapsed_small = time.time() - start
fps_small = N / elapsed_small

print(f"\nimgsz=640 (기본): {fps:.1f} FPS")
print(f"imgsz=320 (축소): {fps_small:.1f} FPS")
print(f"속도 향상 배율: {fps_small / fps:.1f}x")
```

### 12.1 `imgsz`

`imgsz`는 모델이 이미지를 처리할 때 사용할 입력 크기다.

```python
model.predict(image, imgsz=320)
```

`imgsz=320`은 이미지를 더 작게 줄여서 추론한다는 뜻이다.

| `imgsz` | 속도 | 정확도 |
|---:|---|---|
| `320` | 빠름 | 작은 물체를 놓칠 수 있음 |
| `640` | 기본적인 균형 | 일반적인 기준 |
| `1280` | 느림 | 작은 물체 탐지에 유리할 수 있음 |

로봇에서는 보통 속도가 중요하므로 `yolov8n.pt + imgsz=320` 같은 조합부터 시험해보는 경우가 많다. 다만 작은 장애물이나 멀리 있는 사람을 놓치면 안 되는 상황에서는 `imgsz`를 너무 낮추면 위험하다.

---

## 13. Kalman Filter 개념

Kalman Filter는 노이즈가 섞인 측정값을 더 안정적인 추정값으로 바꾸는 알고리즘이다.

핵심 아이디어는 두 단계를 반복하는 것이다.

```text
1. Predict
   이전 상태와 운동 모델을 이용해서 다음 상태를 예측한다.

2. Update
   실제 센서 측정값을 보고 예측값을 보정한다.
```

YOLO와 연결하면 다음처럼 생각할 수 있다.

```text
Predict:
    이전 프레임의 중심점과 속도를 보고 이번 프레임 중심점이 어디쯤일지 예측

Update:
    이번 프레임에서 YOLO가 측정한 중심점으로 예측값을 보정
```

### 13.1 상태 벡터

노트북의 1차원 Kalman Filter는 위치와 속도를 상태로 둔다.

```text
x = [ position
      velocity ]
```

Python 배열 모양으로는 다음과 같다.

```python
self.x = np.zeros((2, 1))
```

| 성분 | 의미 |
|---|---|
| `position` | 현재 위치 |
| `velocity` | 현재 속도 |

위치만 저장하지 않고 속도도 저장하는 이유는 다음 위치를 예측하기 위해서다.

```text
다음 위치 = 현재 위치 + 현재 속도 * 시간 간격
```

### 13.2 공분산 행렬 `P`

`P`는 현재 추정값을 얼마나 불확실하게 보는지 나타낸다.

```python
self.P = np.eye(2) * 100
```

| 값 | 의미 |
|---|---|
| 작음 | 현재 추정값을 꽤 믿는다. |
| 큼 | 현재 추정값을 잘 모른다고 본다. |

처음에는 물체 위치와 속도를 잘 모르므로 큰 값으로 시작한다.

노트북에는 공분산 행렬을 직접 만들어보는 예시도 있다.

```python
# "초기 위치는 ±5m, 속도는 ±2m/s 정도로 불확실하다" 고 가정
# 분산 = 표준편차² -> 5² = 25, 2² = 4
P_0 = np.array([[25, 0],
                [0,  4]], dtype=float)

print("초기 공분산 행렬 P_0:")
print(P_0)
```

이 코드는 다음 행렬을 만든다.

```text
[25  0]
[ 0  4]
```

| 값 | 의미 |
|---|---|
| `25` | 위치 오차의 분산. 표준편차 5m를 제곱한 값 |
| `4` | 속도 오차의 분산. 표준편차 2m/s를 제곱한 값 |
| `0` | 위치 오차와 속도 오차가 서로 관계없다고 가정 |

여기서 중요한 개념은 분산이 표준편차의 제곱이라는 점이다.

```text
표준편차 = 5
분산 = 5 * 5 = 25
```

Kalman Filter에서는 불확실성을 보통 표준편차가 아니라 분산 또는 공분산 행렬로 표현한다.

#### `np.array()`

| 항목 | 설명 |
|---|---|
| 함수 | `np.array()` |
| 역할 | Python 리스트를 NumPy 배열로 변환 |
| 주요 인자 | 배열로 만들 데이터, `dtype` |
| 반환값 | NumPy 배열 |

```python
np.array([[25, 0], [0, 4]], dtype=float)
```

`dtype=float`는 배열 값을 실수로 저장하겠다는 뜻이다. Kalman Filter 계산은 나눗셈과 행렬 연산이 많으므로 정수보다 실수 배열을 쓰는 편이 안전하다.

### 13.3 프로세스 노이즈 `Q`

```python
self.Q = np.eye(2) * process_noise
```

`Q`는 내가 세운 운동 모델이 얼마나 틀릴 수 있는지를 나타낸다.

예를 들어 "물체가 등속 운동한다"고 가정했지만 실제 사람은 갑자기 멈추거나 방향을 바꿀 수 있다. 이런 예측 모델의 불완전함을 `Q`로 표현한다.

| `process_noise` | 의미 |
|---:|---|
| 작음 | 예측 모델을 많이 믿음 |
| 큼 | 예측 모델이 자주 틀릴 수 있다고 봄 |

#### `np.eye()`

```python
np.eye(2)
```

`np.eye(2)`는 2x2 단위 행렬을 만든다.

```text
[1  0]
[0  1]
```

그래서 다음 코드는 대각선 값이 `process_noise`인 2x2 행렬을 만든다.

```python
self.Q = np.eye(2) * process_noise
```

예를 들어 `process_noise=0.1`이면 다음과 같다.

```text
[0.1  0.0]
[0.0  0.1]
```

### 13.4 센서 노이즈 `R`

```python
self.R = np.array([[sensor_noise]], dtype=float)
```

`R`은 센서 측정값을 얼마나 불확실하게 보는지 나타낸다.

YOLO 중심점 좌표에 적용한다면 `R`은 "YOLO가 알려준 중심점이 몇 픽셀 정도 흔들릴 수 있는가"에 해당한다.

| `sensor_noise` | 의미 |
|---:|---|
| 작음 | 측정값을 많이 믿음 |
| 큼 | 측정값을 덜 믿음 |

노트북에는 GPS 노이즈를 가짜로 만들고 분산을 구하는 예시가 있다.

```python
# R: 센서를 고정하고 반복 측정 -> 분산으로 계산 (비교적 쉬움)
np.random.seed(42)
gps_readings = np.random.normal(loc=0.0, scale=2.5, size=1000)  # ±2.5m 오차 시뮬레이션
R = np.var(gps_readings)
print(f"GPS 노이즈 분산 R = {R:.4f} (표준편차 ≈ {np.sqrt(R):.2f}m)")
```

이 코드는 "실제로는 0m 위치에 고정되어 있는데 GPS 측정값만 흔들리는 상황"을 흉내 낸다.

#### `np.random.seed()`

| 항목 | 설명 |
|---|---|
| 함수 | `np.random.seed()` |
| 인자 | seed 숫자 |
| 반환값 | 없음 |
| 의미 | 랜덤 결과가 매번 같게 나오도록 고정 |

```python
np.random.seed(42)
```

이렇게 하면 실습을 다시 실행해도 같은 난수 흐름이 만들어진다.

#### `np.random.normal()`

| 항목 | 설명 |
|---|---|
| 함수 | `np.random.normal()` |
| 역할 | 정규분포를 따르는 랜덤 값 생성 |
| `loc` | 평균 |
| `scale` | 표준편차 |
| `size` | 생성할 개수 |
| 반환값 | NumPy 배열 |

```python
gps_readings = np.random.normal(loc=0.0, scale=2.5, size=1000)
```

뜻은 다음과 같다.

```text
평균 0.0
표준편차 2.5
총 1000개의 랜덤 측정값 생성
```

#### `np.var()`

```python
R = np.var(gps_readings)
```

`np.var()`는 배열의 분산을 계산한다.

| 항목 | 설명 |
|---|---|
| 함수 | `np.var()` |
| 인자 | 숫자 배열 |
| 반환값 | 분산 |

센서 측정값이 많이 흔들릴수록 분산이 커진다. Kalman Filter에서 이 값은 `R`로 사용할 수 있다.

#### `np.sqrt()`

```python
np.sqrt(R)
```

`np.sqrt()`는 제곱근을 구한다.

분산의 제곱근은 표준편차다.

```text
표준편차 = sqrt(분산)
```

출력에서 표준편차를 같이 보여주는 이유는 사람이 해석하기 더 쉽기 때문이다. 예를 들어 `R=6.25`라고 보는 것보다 `표준편차 약 2.5m`라고 보는 편이 직관적이다.

### 13.5 상태 전이 행렬 `A`

```python
self.A = np.array([[1, dt],
                   [0,  1]], dtype=float)
```

`A`는 현재 상태가 다음 상태로 어떻게 바뀌는지 나타낸다.

상태가 `[position, velocity]`일 때 등속 운동은 다음과 같다.

```text
new_position = old_position + old_velocity * dt
new_velocity = old_velocity
```

행렬로 쓰면 다음과 같다.

```text
[ new_position ]   [ 1  dt ] [ old_position ]
[ new_velocity ] = [ 0   1 ] [ old_velocity ]
```

### 13.6 제어 행렬 `B`

```python
self.B = np.array([[0.5 * dt**2],
                   [dt]], dtype=float)
```

`B`는 외부 제어 입력 `u`를 상태에 반영할 때 사용한다.

노트북에서는 `u`를 가속도라고 가정한다.

```text
position 변화량 = 0.5 * acceleration * dt^2
velocity 변화량 = acceleration * dt
```

그래서 `B`가 위 형태가 된다.

가속도 입력을 쓰지 않는다면 기본값 `u=0.0`으로 두면 된다.

### 13.7 센서 행렬 `C`

```python
self.C = np.array([[1, 0]], dtype=float)
```

`C`는 상태 중에서 센서가 직접 측정하는 값만 꺼내는 역할을 한다.

상태는 `[position, velocity]`인데 GPS나 YOLO 중심점은 보통 위치만 알려준다.

```text
측정값 z = position
```

그래서 `C = [1, 0]`이다.

```text
[1  0] [ position ] = position
       [ velocity ]
```

---

## 14. `KalmanFilter1D` 클래스 분석

노트북 코드의 핵심 클래스다.

```python
class KalmanFilter1D:
    """
    1D 위치-속도 칼만 필터
    상태벡터: [position, velocity]
    """
```

이 클래스는 1차원 위치 하나를 추적한다. 예를 들어 x 좌표 하나만 추적할 수 있다.

YOLO 중심점은 `(cx, cy)`처럼 2차원이므로 실제로는 필터를 두 개 만들면 된다.

```python
kf_x = KalmanFilter1D(...)
kf_y = KalmanFilter1D(...)
```

### 14.1 `__init__()`

```python
def __init__(self, dt=0.1, process_noise=1.0, sensor_noise=5.0):
```

객체를 처음 만들 때 호출되는 초기화 함수다.

| 인자 | 기본값 | 의미 |
|---|---:|---|
| `dt` | `0.1` | 한 스텝 사이의 시간 간격. 초 단위로 생각하면 된다. |
| `process_noise` | `1.0` | 예측 모델의 불확실성 |
| `sensor_noise` | `5.0` | 센서 측정값의 불확실성 |

예시:

```python
kf = KalmanFilter1D(dt=0.1, process_noise=0.1, sensor_noise=5.0)
```

이 예시는 다음 의미다.

```text
프레임 간격은 0.1초라고 가정
운동 모델은 비교적 믿음
센서 측정값은 어느 정도 노이즈가 있다고 봄
```

### 14.2 주요 속성

| 속성 | 모양 | 의미 |
|---|---|---|
| `self.x` | `(2, 1)` | 현재 상태 `[position, velocity]` |
| `self.P` | `(2, 2)` | 현재 상태 추정의 불확실성 |
| `self.A` | `(2, 2)` | 상태 전이 행렬 |
| `self.B` | `(2, 1)` | 제어 입력 행렬 |
| `self.C` | `(1, 2)` | 센서 측정 행렬 |
| `self.Q` | `(2, 2)` | 프로세스 노이즈 |
| `self.R` | `(1, 1)` | 센서 노이즈 |

### 14.3 `predict()`

노트북의 원래 코드는 TODO로 비어 있다.

```python
def predict(self, u=0.0):
    """
    Predict 단계: 운동 모델로 다음 상태 예측
    u: 제어 입력 (가속도)
    반환: 예측된 위치
    """
    # TODO: 여기에 구현하세요
    # 힌트 1: self.x = self.A @ self.x + self.B * u
    # 힌트 2: self.P = self.A @ self.P @ self.A.T + self.Q
    return self.x[0, 0]
```

완성하면 다음과 같다.

```python
def predict(self, u=0.0):
    self.x = self.A @ self.x + self.B * u
    self.P = self.A @ self.P @ self.A.T + self.Q
    return self.x[0, 0]
```

#### `predict()` 인자와 반환값

| 항목 | 설명 |
|---|---|
| 인자 `u` | 제어 입력. 여기서는 가속도. 기본값은 `0.0` |
| 반환값 | 예측된 위치 `position` |
| 내부 변경 | `self.x`, `self.P`가 예측값으로 갱신됨 |

#### `@` 연산자

```python
self.A @ self.x
```

`@`는 Python의 행렬 곱셈 연산자다. NumPy 배열끼리 행렬 곱을 할 때 사용한다.

### 14.4 `update()`

노트북의 원래 코드는 TODO로 비어 있다.

```python
def update(self, z):
    """
    Update 단계: 실제 센서 측정값으로 상태 보정
    z: 실제 측정값 (위치)
    반환: 보정된 위치
    """
    # TODO: 여기에 구현하세요
    return self.x[0, 0]
```

완성하면 다음과 같다.

```python
def update(self, z):
    z = np.array([[z]])
    innovation = z - self.C @ self.x
    S = self.C @ self.P @ self.C.T + self.R
    K = self.P @ self.C.T @ np.linalg.inv(S)
    self.x = self.x + K @ innovation
    self.P = (np.eye(2) - K @ self.C) @ self.P
    return self.x[0, 0]
```

#### `update()` 인자와 반환값

| 항목 | 설명 |
|---|---|
| 인자 `z` | 실제 센서 측정값. 여기서는 위치 |
| 반환값 | 측정값으로 보정된 위치 |
| 내부 변경 | `self.x`, `self.P`가 보정 후 값으로 갱신됨 |

#### `z = np.array([[z]])`

스칼라 숫자 하나를 `(1, 1)` 모양의 행렬로 바꾼다.

Kalman Filter 식은 행렬 계산이므로, 모양을 맞추는 것이 중요하다.

```text
z = 3.2
```

를 다음처럼 바꾼다.

```text
[[3.2]]
```

#### `innovation`

```python
innovation = z - self.C @ self.x
```

innovation은 실제 측정값과 예측 측정값의 차이다.

```text
innovation = 실제 측정값 - 예측값
```

예를 들어 예측 위치가 `10`, 센서 측정 위치가 `13`이면 innovation은 `3`이다.

#### `S`

```python
S = self.C @ self.P @ self.C.T + self.R
```

`S`는 innovation의 불확실성이다.

예측도 불확실하고 센서도 불확실하므로, 두 불확실성을 합쳐서 "이번 차이를 얼마나 믿을 것인가"를 판단한다.

#### `K`

```python
K = self.P @ self.C.T @ np.linalg.inv(S)
```

`K`는 Kalman Gain이다.

| 상황 | Kalman Gain 경향 | 의미 |
|---|---|---|
| 예측이 불확실하고 센서가 정확함 | 커짐 | 센서 측정값을 더 믿음 |
| 예측이 정확하고 센서가 불안정함 | 작아짐 | 예측값을 더 믿음 |

#### 상태 보정

```python
self.x = self.x + K @ innovation
```

예측 상태에 innovation의 일부를 더해서 보정한다.

#### 불확실성 보정

```python
self.P = (np.eye(2) - K @ self.C) @ self.P
```

측정값을 보고 상태를 보정했으므로, 일반적으로 불확실성도 줄어든다.

### 14.5 `get_state()`

```python
def get_state(self):
    """현재 상태 [position, velocity] 반환"""
    return self.x[0, 0], self.x[1, 0]
```

| 항목 | 설명 |
|---|---|
| 인자 | 없음 |
| 반환값 | `(position, velocity)` 튜플 |

현재 추정 위치와 속도를 동시에 보고 싶을 때 사용한다.

---

## 15. Kalman Filter 테스트 코드

노트북의 테스트 코드는 가짜 GPS 데이터를 만들어서 Kalman Filter가 노이즈를 줄이는지 확인한다.

### 15.1 난수 고정

```python
np.random.seed(42)
```

난수 seed를 고정하면 매번 같은 랜덤 값이 나온다.

실습 문서나 수업에서는 결과가 매번 달라지면 설명이 어려우므로 seed를 고정하는 경우가 많다.

### 15.2 테스트 설정

```python
dt = 0.1
N = 50  # 시뮬레이션 스텝 수
kf = KalmanFilter1D(dt=dt, process_noise=0.1, sensor_noise=5.0)
```

| 변수 | 의미 |
|---|---|
| `dt` | 시뮬레이션 한 스텝의 시간 간격 |
| `N` | 총 스텝 수 |
| `kf` | Kalman Filter 객체 |

### 15.3 실제 위치 생성

```python
true_positions = [i * dt * 1.0 for i in range(N)]
```

이 코드는 속도 `1.0 m/s`로 등속 운동하는 물체의 실제 위치를 만든다.

```text
0.0, 0.1, 0.2, 0.3, ...
```

리스트 컴프리헨션을 풀어 쓰면 다음과 같다.

```python
true_positions = []
for i in range(N):
    true_positions.append(i * dt * 1.0)
```

### 15.4 노이즈가 있는 GPS 측정값 생성

```python
gps_measurements = [p + np.random.normal(0, 2.0) for p in true_positions]
```

`np.random.normal(0, 2.0)`은 평균 0, 표준편차 2.0인 정규분포 노이즈를 만든다.

| 인자 | 의미 |
|---|---|
| `0` | 평균 |
| `2.0` | 표준편차 |

즉 실제 위치 `p`에 흔들리는 측정 오차를 더해서 GPS처럼 만든다.

### 15.5 Predict와 Update 반복

```python
predicted_positions = []
filtered_positions = []

for i, z in enumerate(gps_measurements):
    pred_pos = kf.predict()
    filt_pos = kf.update(z)
    predicted_positions.append(pred_pos)
    filtered_positions.append(filt_pos)
```

한 스텝마다 다음 순서로 실행한다.

```text
1. kf.predict()
   현재 상태로 다음 위치를 예측한다.

2. kf.update(z)
   실제 GPS 측정값 z로 예측값을 보정한다.

3. 결과 저장
   예측 위치와 필터링된 위치를 리스트에 저장한다.
```

### 15.6 결과 출력

```python
gps_err = abs(gps_measurements[i] - true_positions[i])
filt_err = abs(filtered_positions[i] - true_positions[i])
```

| 값 | 의미 |
|---|---|
| `gps_err` | 노이즈가 있는 GPS 측정값의 오차 |
| `filt_err` | Kalman Filter 결과의 오차 |

이론적으로는 `filt_err`가 항상 모든 순간에 더 작지는 않다. 하지만 전체적으로는 노이즈가 줄어들고 곡선이 부드러워지는 효과를 기대한다.

### 15.7 결과 시각화

```python
plt.plot(t, true_positions,     'g-', label='True Position', linewidth=2)
plt.plot(t, gps_measurements,   'r.', label='GPS Measurement (Noisy)', alpha=0.6, markersize=8)
plt.plot(t, filtered_positions, 'b-', label='Kalman Filter Output', linewidth=2)
```

| 스타일 | 의미 |
|---|---|
| `'g-'` | 초록색 실선 |
| `'r.'` | 빨간색 점 |
| `'b-'` | 파란색 실선 |

그래프에서 기대하는 모양은 다음과 같다.

```text
초록색: 실제 위치, 매끄러운 직선
빨간색: 노이즈가 있는 측정값, 위아래로 흔들림
파란색: Kalman Filter 결과, 빨간색보다 부드러움
```

---

## 16. YOLO와 Kalman Filter 연결 방식

노트북 마지막 부분의 핵심 문장이다.

```text
YOLO 탐지 결과의 중심점 (cx, cy)에 칼만 필터를 적용하여 떨림을 안정화합니다.
```

YOLO의 박스 중심점은 2차원이다.

```text
cx: 화면 가로 방향 위치
cy: 화면 세로 방향 위치
```

`KalmanFilter1D`는 1차원만 처리하므로 x용 필터와 y용 필터를 각각 만들면 된다.

```python
kf_x = KalmanFilter1D(dt=1/30, process_noise=1.0, sensor_noise=20.0)
kf_y = KalmanFilter1D(dt=1/30, process_noise=1.0, sensor_noise=20.0)
```

웹캠 프레임마다 다음 순서로 처리한다.

```python
results = model.predict(frame, conf=0.5, verbose=False)

for result in results:
    for box in result.boxes:
        label = model.names[int(box.cls[0])]

        if label == "person":
            cx, cy, w, h = box.xywh[0]

            pred_x = kf_x.predict()
            pred_y = kf_y.predict()

            smooth_x = kf_x.update(float(cx))
            smooth_y = kf_y.update(float(cy))
```

여기서 중요한 값은 다음과 같다.

| 값 | 의미 |
|---|---|
| `cx`, `cy` | YOLO가 이번 프레임에서 측정한 중심점 |
| `pred_x`, `pred_y` | Kalman Filter가 예측한 중심점 |
| `smooth_x`, `smooth_y` | YOLO 측정값까지 반영해 보정된 중심점 |

실제 화면에 그릴 때는 원래 YOLO 중심점 대신 `smooth_x`, `smooth_y`를 사용할 수 있다.

```python
cv2.circle(frame, (int(smooth_x), int(smooth_y)), 5, (0, 255, 0), -1)
```

이렇게 하면 프레임마다 흔들리는 점이 조금 더 안정적으로 움직인다.

---

## 17. CPU에서 GPU로 바꾸는 방법

현재 노트북 설치 명령은 CPU 전용 PyTorch를 설치한다.

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

GPU를 쓰려면 세 가지가 맞아야 한다.

```text
1. NVIDIA GPU가 있어야 한다.
2. NVIDIA 드라이버가 정상 설치되어 있어야 한다.
3. CUDA 지원 PyTorch가 설치되어 있어야 한다.
```

### 17.1 GPU 확인

터미널에서 확인한다.

```bash
nvidia-smi
```

정상이라면 GPU 이름, 드라이버 버전, 메모리 사용량 같은 정보가 나온다.

Python에서 확인하려면 다음을 실행한다.

```python
import torch

print(torch.cuda.is_available())
print(torch.cuda.get_device_name(0))
```

| 결과 | 의미 |
|---|---|
| `True` | PyTorch가 CUDA GPU를 사용할 수 있음 |
| `False` | GPU를 못 찾았거나 CPU 버전 PyTorch가 설치됨 |

### 17.2 CUDA용 PyTorch 설치

가장 안전한 방법은 PyTorch 공식 설치 페이지에서 본인 환경을 선택하고 명령어를 복사하는 것이다.

선택 예시는 다음과 같다.

```text
OS: Linux 또는 Windows
Package: Pip
Language: Python
Compute Platform: CUDA 버전
```

CPU 전용 PyTorch가 이미 설치되어 있다면 먼저 제거한 뒤 다시 설치하는 것이 깔끔하다.

```bash
pip uninstall torch torchvision torchaudio
```

그 다음 공식 페이지에서 안내하는 CUDA용 명령을 사용한다.

예를 들어 CUDA 12.4용 wheel을 쓰는 환경이라면 명령 형태는 다음과 비슷하다.

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
```

단, CUDA wheel 주소는 PyTorch 버전과 지원 CUDA 버전에 따라 달라질 수 있다. 반드시 PyTorch 공식 설치 페이지에서 현재 본인 환경에 맞는 명령을 확인하는 것이 좋다.

### 17.3 YOLO 코드에서 GPU 지정

PyTorch CUDA 설치가 끝났다면 YOLO 추론에서 `device`를 지정할 수 있다.

```python
results = model.predict("bus.jpg", device=0)
```

또는 다음처럼 쓸 수 있다.

```python
results = model.predict("bus.jpg", device="cuda:0")
```

| 값 | 의미 |
|---|---|
| `device="cpu"` | CPU 사용 |
| `device=0` | 첫 번째 CUDA GPU 사용 |
| `device="cuda:0"` | 첫 번째 CUDA GPU 사용 |
| `device="cuda:1"` | 두 번째 CUDA GPU 사용 |

모델을 GPU에 올려두는 방식도 가능하다.

```python
model = YOLO("yolov8n.pt")
model.to("cuda")

results = model.predict("bus.jpg")
```

### 17.4 GPU에서 속도를 더 올리는 옵션

GPU에서는 `half=True`를 사용할 수 있다.

```python
results = model.predict("bus.jpg", device=0, half=True)
```

`half=True`는 FP16 반정밀도 연산을 사용한다. GPU에서 속도와 메모리 사용량에 유리할 수 있다.

다만 모든 환경에서 항상 이득은 아니므로 직접 FPS를 측정해야 한다.

### 17.5 CPU/GPU 자동 선택 코드

실습 코드에서는 다음처럼 자동 선택을 넣으면 편하다.

```python
import torch
from ultralytics import YOLO

device = 0 if torch.cuda.is_available() else "cpu"

model = YOLO("yolov8n.pt")
results = model.predict("bus.jpg", device=device, verbose=False)

print("사용 장치:", "cuda:0" if device == 0 else "cpu")
```

### 17.6 GPU 사용 시 주의점

| 주의점 | 설명 |
|---|---|
| 첫 추론은 느릴 수 있음 | 모델 로딩, CUDA 초기화 때문에 첫 실행은 오래 걸릴 수 있다. |
| 작은 이미지는 CPU와 차이가 작을 수 있음 | GPU로 보내고 받는 비용도 있기 때문이다. |
| 너무 큰 모델은 GPU 메모리 부족 가능 | `yolov8n`부터 시작해서 올리는 것이 좋다. |
| `numpy` 변환이 많으면 느려질 수 있음 | GPU 결과를 CPU로 자주 가져오면 병목이 생길 수 있다. |
| 노트북 커널 재시작 필요 가능 | PyTorch를 다시 설치했다면 Jupyter 커널을 재시작해야 한다. |

---

## 18. 초보자가 자주 헷갈리는 부분

### 18.1 `model.predict()`와 `model()`은 다른가?

대부분의 기본 추론에서는 비슷하게 사용할 수 있다.

```python
results = model.predict("bus.jpg")
results = model("bus.jpg")
```

초보자 입장에서는 `model.predict()`를 쓰는 것이 더 명확하다. "예측을 실행한다"는 의미가 코드에 드러나기 때문이다.

### 18.2 왜 `box.xyxy[0]`처럼 `[0]`을 붙이나?

YOLO 결과가 텐서 형태로 저장되기 때문이다.

좌표 하나도 내부적으로는 다음처럼 들어 있다.

```text
[[x1, y1, x2, y2]]
```

바깥 리스트 한 겹을 벗기기 위해 `[0]`을 붙인다.

### 18.3 왜 `int(box.cls[0])`을 하나?

`box.cls[0]`은 텐서 형태의 숫자다. `model.names`의 key로 사용하려면 일반 정수로 바꾸는 것이 안전하다.

```python
cls_id = int(box.cls[0])
label = model.names[cls_id]
```

### 18.4 왜 OpenCV 이미지는 색이 이상하게 보이나?

OpenCV는 BGR 순서, Matplotlib은 RGB 순서를 사용한다.

그래서 Matplotlib으로 보여줄 때는 다음 변환이 필요하다.

```python
image_rgb = image_bgr[:, :, ::-1]
```

### 18.5 Kalman Filter는 항상 정답에 가까워지나?

항상은 아니다. `process_noise`, `sensor_noise`, `dt` 설정이 상황과 너무 다르면 오히려 반응이 느리거나 이상해질 수 있다.

대략적인 튜닝 방향은 다음과 같다.

| 문제 상황 | 조정 방향 |
|---|---|
| 결과가 너무 늦게 따라옴 | `process_noise`를 키우거나 `sensor_noise`를 줄인다. |
| 결과가 너무 흔들림 | `sensor_noise`를 키우거나 `process_noise`를 줄인다. |
| 빠른 움직임을 놓침 | `dt`와 실제 FPS가 맞는지 확인하고 `process_noise`를 키운다. |

---

## 19. 노트북을 실행할 때 체크리스트

1. `ultralytics`, `torch`, `opencv-python`, `numpy`, `matplotlib`이 설치되어 있는지 확인한다.
2. `bus.jpg`가 현재 작업 디렉터리에 있는지 확인한다.
3. `YOLO('yolov8n.pt')` 실행 시 모델 파일이 없으면 자동 다운로드될 수 있다.
4. 인터넷이 막혀 있으면 미리 `yolov8n.pt` 파일을 준비해야 한다.
5. Kalman Filter 클래스의 `predict()`와 `update()` TODO를 완성해야 테스트 결과가 의미 있게 나온다.
6. GPU를 쓰려면 CPU 전용 PyTorch가 아니라 CUDA 지원 PyTorch가 설치되어 있어야 한다.
7. FPS를 볼 때는 첫 추론을 제외하거나 여러 번 반복해서 평균을 본다.

---

## 20. 완성된 `KalmanFilter1D` 참고 코드

노트북의 TODO 부분까지 채우면 클래스는 다음처럼 된다.

```python
class KalmanFilter1D:
    """
    1D 위치-속도 칼만 필터
    상태벡터: [position, velocity]
    """
    def __init__(self, dt=0.1, process_noise=1.0, sensor_noise=5.0):
        self.dt = dt

        self.A = np.array([[1, dt],
                           [0,  1]], dtype=float)

        self.B = np.array([[0.5 * dt**2],
                           [dt]], dtype=float)

        self.C = np.array([[1, 0]], dtype=float)

        self.Q = np.eye(2) * process_noise
        self.R = np.array([[sensor_noise]], dtype=float)

        self.x = np.zeros((2, 1))
        self.P = np.eye(2) * 100

    def predict(self, u=0.0):
        self.x = self.A @ self.x + self.B * u
        self.P = self.A @ self.P @ self.A.T + self.Q
        return self.x[0, 0]

    def update(self, z):
        z = np.array([[z]])
        innovation = z - self.C @ self.x
        S = self.C @ self.P @ self.C.T + self.R
        K = self.P @ self.C.T @ np.linalg.inv(S)
        self.x = self.x + K @ innovation
        self.P = (np.eye(2) - K @ self.C) @ self.P
        return self.x[0, 0]

    def get_state(self):
        return self.x[0, 0], self.x[1, 0]
```

---

## 21. 참고 자료

- PyTorch 공식 설치 안내: https://docs.pytorch.org/get-started/locally/
- Ultralytics YOLO 공식 문서: https://docs.ultralytics.com/
- Ultralytics predict mode 문서: https://github.com/ultralytics/ultralytics/blob/main/docs/en/modes/predict.md
