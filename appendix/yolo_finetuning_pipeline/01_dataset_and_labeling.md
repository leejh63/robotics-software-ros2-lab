# 01. YOLO 데이터셋 준비와 라벨링

## 1. 데이터셋이 가장 중요하다

YOLO 파인튜닝 성능의 대부분은 데이터셋에서 결정된다.

모델을 바꾸기 전에 먼저 확인해야 할 것은 아래다.

```text
이미지가 실제 사용 환경과 비슷한가?
라벨 박스가 정확한가?
클래스 번호가 맞는가?
train/val 분리가 제대로 되었는가?
작은 물체가 너무 작게 찍히지 않았는가?
```

---

## 2. YOLO detection 데이터셋 구조

가장 일반적인 구조는 아래다.

```text
my_dataset/
├── images/
│   ├── train/
│   │   ├── img_0001.jpg
│   │   ├── img_0002.jpg
│   │   └── ...
│   ├── val/
│   │   ├── img_1001.jpg
│   │   ├── img_1002.jpg
│   │   └── ...
│   └── test/
│       ├── img_2001.jpg
│       └── ...
│
├── labels/
│   ├── train/
│   │   ├── img_0001.txt
│   │   ├── img_0002.txt
│   │   └── ...
│   ├── val/
│   │   ├── img_1001.txt
│   │   ├── img_1002.txt
│   │   └── ...
│   └── test/
│       ├── img_2001.txt
│       └── ...
│
└── data.yaml
```

이미지와 라벨 파일 이름은 같아야 한다.

```text
images/train/img_0001.jpg
labels/train/img_0001.txt
```

이미지에 객체가 없으면 빈 txt 파일을 둘 수 있다.

```text
labels/train/no_object_0001.txt
```

---

## 3. YOLO 라벨 형식

라벨 파일은 한 객체당 한 줄이다.

```text
class_id x_center y_center width height
```

예시:

```text
0 0.5123 0.4312 0.1200 0.0800
1 0.3000 0.6210 0.0500 0.0300
```

의미:

```text
class_id:
    0부터 시작하는 클래스 번호

x_center:
    박스 중심 x 좌표 / 이미지 너비

y_center:
    박스 중심 y 좌표 / 이미지 높이

width:
    박스 너비 / 이미지 너비

height:
    박스 높이 / 이미지 높이
```

중요한 점:

```text
좌표는 픽셀값이 아니다.
항상 0~1 사이로 정규화되어야 한다.
```

---

## 4. class id 예시

내 클래스가 아래와 같다고 하자.

```yaml
names:
  0: red_led
  1: blue_led
  2: button
```

그러면 라벨 파일에서 `0`은 red_led다.

```text
0 0.5123 0.4312 0.1200 0.0800
```

`1`은 blue_led다.

```text
1 0.3000 0.6210 0.0500 0.0300
```

`2`는 button이다.

```text
2 0.7100 0.2200 0.1800 0.1200
```

---

## 5. data.yaml 작성

예시:

```yaml
path: /home/jaeholee/datasets/my_dataset

train: images/train
val: images/val
test: images/test

names:
  0: red_led
  1: blue_led
  2: button
```

`path` 아래에 `train`, `val`, `test` 경로가 붙는다고 보면 된다.

```text
/home/jaeholee/datasets/my_dataset/images/train
/home/jaeholee/datasets/my_dataset/images/val
/home/jaeholee/datasets/my_dataset/images/test
```

---

## 6. train / val / test 분리

추천 비율:

```text
train: 70~80%
val:   10~20%
test:  10%
```

단순히 랜덤 분할하면 안 되는 경우가 많다.

### 나쁜 예

동영상에서 연속 프레임을 뽑고 랜덤 분할:

```text
frame_0001 train
frame_0002 val
frame_0003 train
frame_0004 val
```

이렇게 하면 train과 val이 거의 같은 이미지가 된다.

결과:

```text
val 성능은 높게 나옴
실제 환경에서는 성능 낮음
```

### 좋은 예

촬영 환경 기준으로 분리:

```text
train:
    1일차 오전 조명
    1일차 오후 조명
    실내 A 환경

val:
    2일차 조명
    실내 B 환경

test:
    완전히 다른 날
    실제 배포 위치
```

---

## 7. 데이터 수집 체크리스트

좋은 데이터셋은 다양성이 있다.

```text
거리:
    가까움
    중간
    멀리 있음

각도:
    정면
    측면
    위/아래
    기울어진 상태

조명:
    밝음
    어두움
    역광
    그림자
    LED 반사

배경:
    단순 배경
    복잡한 배경
    비슷한 색상 배경

상태:
    일부 가림
    흐림
    노이즈
    움직임
```

---

## 8. Negative sample

객체가 없는 이미지도 중요하다.

예를 들어 LED를 탐지하는 모델이라면, LED가 없는 보드 이미지도 넣어야 한다.

```text
객체 있음:
    red_led 있음
    blue_led 있음
    button 있음

객체 없음:
    빈 보드
    비슷한 색 점
    반사광
    나사
    스티커
```

Negative sample이 없으면 모델이 비슷한 모든 것을 객체로 착각할 수 있다.

---

## 9. 라벨링 도구

대표적인 선택지는 아래다.

```text
LabelImg
CVAT
Roboflow
Label Studio
makesense.ai
Ultralytics Platform
```

초보자는 웹 기반 도구가 편하다.

하지만 프로젝트가 커지면 다음을 관리해야 한다.

```text
라벨 버전
작업자별 라벨 품질
클래스 정의서
라벨링 규칙
검수 절차
```

---

## 10. 라벨링 규칙 예시

프로젝트 시작 전에 반드시 규칙을 정한다.

예:

```text
1. 객체가 일부 가려져 있어도 보이는 부분만 박스로 친다.
2. 너무 흐려서 사람도 구분하기 어려운 객체는 라벨링하지 않는다.
3. LED 반사광은 LED로 라벨링하지 않는다.
4. button의 외곽 플라스틱 전체를 박스로 잡는다.
5. red_led와 blue_led는 실제 발광 색 기준으로 구분한다.
```

이 규칙이 없으면 같은 객체를 사람마다 다르게 라벨링한다.

그 결과 모델이 혼란스러워진다.

---

## 11. 작은 객체 데이터 주의사항

작은 객체는 YOLO가 어려워한다.

예:

```text
멀리 있는 작은 부품
작은 나사
작은 LED
작은 마커
작은 QR 위치
```

해결 방법:

```text
원본 해상도를 높인다.
imgsz를 키운다.
객체가 너무 작지 않게 촬영한다.
crop 기반 데이터셋을 만든다.
라벨 박스를 정확하게 단다.
```

작은 객체가 많은 경우 학습 명령어 예시:

```bash
yolo detect train \
  model=yolo26s.pt \
  data=data.yaml \
  epochs=100 \
  imgsz=960 \
  batch=8 \
  device=0 \
  name=small_object_img960
```

---

## 12. 데이터셋 검증 스크립트

학습 전에 최소한 파일 매칭은 확인한다.

```python
from pathlib import Path

dataset = Path("/home/jaeholee/datasets/my_dataset")

for split in ["train", "val", "test"]:
    image_dir = dataset / "images" / split
    label_dir = dataset / "labels" / split

    if not image_dir.exists():
        print(f"[WARN] missing image dir: {image_dir}")
        continue

    image_files = list(image_dir.glob("*.jpg")) + list(image_dir.glob("*.png")) + list(image_dir.glob("*.jpeg"))

    missing = []
    for img in image_files:
        label = label_dir / f"{img.stem}.txt"
        if not label.exists():
            missing.append(img.name)

    print(f"[{split}] images={len(image_files)}, missing_labels={len(missing)}")

    if missing[:10]:
        print("examples:", missing[:10])
```

---

## 13. 라벨 좌표 검증 스크립트

```python
from pathlib import Path

label_root = Path("/home/jaeholee/datasets/my_dataset/labels")
num_classes = 3

bad_files = []

for txt in label_root.rglob("*.txt"):
    lines = txt.read_text().strip().splitlines()

    for idx, line in enumerate(lines, start=1):
        if not line.strip():
            continue

        parts = line.split()
        if len(parts) != 5:
            bad_files.append((txt, idx, "field count != 5"))
            continue

        cls, x, y, w, h = parts

        try:
            cls = int(cls)
            values = [float(x), float(y), float(w), float(h)]
        except ValueError:
            bad_files.append((txt, idx, "parse error"))
            continue

        if not (0 <= cls < num_classes):
            bad_files.append((txt, idx, f"class id out of range: {cls}"))

        if not all(0.0 <= v <= 1.0 for v in values):
            bad_files.append((txt, idx, f"coord out of range: {values}"))

        if values[2] <= 0 or values[3] <= 0:
            bad_files.append((txt, idx, f"invalid box size: {values}"))

print(f"bad labels: {len(bad_files)}")

for item in bad_files[:30]:
    print(item)
```

---

## 14. 초보자용 데이터셋 기준

처음 실험 기준:

```text
클래스당 최소 50~100장:
    smoke test 가능

클래스당 300장 이상:
    어느 정도 비교 실험 가능

클래스당 1000장 이상:
    실전 성능 튜닝 가능

하지만:
    양보다 라벨 품질과 실제 환경 유사성이 더 중요하다.
```

---

## 15. 데이터셋 완성 기준

학습 전에 아래를 만족해야 한다.

```text
[ ] images/train, images/val 존재
[ ] labels/train, labels/val 존재
[ ] 이미지와 라벨 파일명이 일치
[ ] class id가 0부터 시작
[ ] data.yaml의 names와 라벨 class id 일치
[ ] 좌표가 0~1 정규화
[ ] 빈 이미지에는 빈 txt가 있거나 누락 정책이 명확함
[ ] train/val이 너무 비슷하지 않음
[ ] 실제 사용 환경 이미지가 val/test에 포함됨
```
