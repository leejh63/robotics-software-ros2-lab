# 02. YOLO 학습 환경 구축

## 1. 권장 환경

YOLO 학습은 가능하면 GPU가 있는 환경에서 한다.

```text
학습:
    데스크탑 GPU
    노트북 NVIDIA GPU
    Colab
    서버 GPU

배포:
    라즈베리파이
    Jetson
    x86 mini PC
    로봇 onboard computer
```

CPU로도 가능하지만 느리다.

---

## 2. Python 가상환경 생성

```bash
mkdir -p ~/work/yolo_project
cd ~/work/yolo_project

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
```

---

## 3. Ultralytics 설치

```bash
pip install ultralytics
```

설치 확인:

```bash
yolo version
```

Python 확인:

```bash
python - <<'PY'
from ultralytics import YOLO
print("ultralytics import ok")
PY
```

---

## 4. GPU 확인

```bash
python - <<'PY'
import torch

print("torch:", torch.__version__)
print("cuda available:", torch.cuda.is_available())

if torch.cuda.is_available():
    print("device count:", torch.cuda.device_count())
    print("device 0:", torch.cuda.get_device_name(0))
PY
```

출력이 아래처럼 나오면 GPU 사용 가능이다.

```text
cuda available: True
device 0: NVIDIA ...
```

`False`라면 CPU로 학습하거나 PyTorch CUDA 설치를 다시 확인해야 한다.

---

## 5. 프로젝트 폴더 구조

추천 구조:

```text
yolo_project/
├── datasets/
│   └── my_dataset/
│       ├── images/
│       ├── labels/
│       └── data.yaml
│
├── runs/
│   └── detect/
│
├── scripts/
│   ├── train_baseline.sh
│   ├── train_freeze10.sh
│   ├── train_two_stage.py
│   └── predict_webcam.py
│
├── exports/
│   ├── onnx/
│   └── engine/
│
└── notes/
    └── experiment_log.md
```

---

## 6. data.yaml 경로 확인

학습 전에 data.yaml을 확인한다.

```bash
cat datasets/my_dataset/data.yaml
```

예시:

```yaml
path: /path/to/yolo_project/datasets/my_dataset

train: images/train
val: images/val
test: images/test

names:
  0: red_led
  1: blue_led
  2: button
```

---

## 7. Smoke test

정식 학습 전에 짧게 돌려야 한다.

목적:

```text
데이터셋 경로가 맞는지
라벨을 정상적으로 읽는지
CUDA 문제가 없는지
학습이 시작되는지
```

명령어:

```bash
yolo detect train \
  model=yolo26n.pt \
  data=datasets/my_dataset/data.yaml \
  epochs=3 \
  imgsz=640 \
  batch=4 \
  device=0 \
  name=smoke_test
```

CPU만 있다면:

```bash
yolo detect train \
  model=yolo26n.pt \
  data=datasets/my_dataset/data.yaml \
  epochs=3 \
  imgsz=640 \
  batch=2 \
  device=cpu \
  name=smoke_test_cpu
```

---

## 8. 자주 쓰는 CLI 기본형

```bash
yolo detect train \
  model=yolo26n.pt \
  data=/path/to/data.yaml \
  epochs=100 \
  imgsz=640 \
  batch=16 \
  device=0 \
  name=experiment_name
```

각 옵션 의미:

```text
detect:
    객체 탐지 작업

train:
    학습 모드

model:
    pretrained 모델 또는 기존 best.pt

data:
    data.yaml 경로

epochs:
    전체 데이터셋 반복 횟수

imgsz:
    입력 이미지 크기

batch:
    한 번에 학습할 이미지 수

device:
    0이면 첫 번째 GPU, cpu면 CPU

name:
    runs/detect 아래에 생성될 실험 이름
```

---

## 9. Python API 기본형

```python
from ultralytics import YOLO

model = YOLO("yolo26n.pt")

results = model.train(
    data="datasets/my_dataset/data.yaml",
    epochs=100,
    imgsz=640,
    batch=16,
    device=0,
    name="baseline_python",
)
```

---

## 10. 결과 폴더

학습 후 보통 아래에 결과가 생긴다.

```text
runs/detect/baseline_python/
├── weights/
│   ├── best.pt
│   └── last.pt
├── results.csv
├── results.png
├── confusion_matrix.png
├── labels.jpg
└── ...
```

중요한 파일:

```text
best.pt:
    val 기준 가장 좋은 모델

last.pt:
    마지막 epoch 모델

results.csv:
    epoch별 loss, metric 기록

results.png:
    학습 곡선 이미지

confusion_matrix.png:
    클래스별 혼동 행렬
```

---

## 11. 재현성 관리

실험을 비교하려면 seed를 고정한다.

```bash
yolo detect train \
  model=yolo26n.pt \
  data=datasets/my_dataset/data.yaml \
  epochs=100 \
  imgsz=640 \
  batch=16 \
  seed=42 \
  name=baseline_seed42
```

다만 GPU 연산 특성상 완전히 동일한 결과가 항상 보장되는 것은 아니다.

---

## 12. 실험 이름 규칙

실험 이름을 대충 지으면 나중에 비교가 어렵다.

추천:

```text
날짜_모델_전략_imgsz_epoch
```

예:

```text
0429_yolo26n_baseline_img640_ep100
0429_yolo26n_freeze10_img640_ep100
0429_yolo26s_twostage_img960_ep80
```

---

## 13. 학습 로그 정리 예시

`notes/experiment_log.md`를 만들어서 기록한다.

```markdown
# Experiment Log

## exp01_baseline

- date: 2026-04-29
- model: yolo26n.pt
- data: my_dataset_v1
- epochs: 100
- imgsz: 640
- batch: 16
- freeze: none
- result:
  - mAP50:
  - mAP50-95:
  - precision:
  - recall:
- observation:
  - red_led는 잘 잡음
  - button은 작은 경우 미탐 많음
- next:
  - button 데이터 추가
  - imgsz=960 비교
```

---

## 14. GPU 메모리 부족 시

에러 예:

```text
CUDA out of memory
```

해결 순서:

```text
1. batch 줄이기
2. imgsz 줄이기
3. 더 작은 모델 사용
4. freeze 적용
5. mixed precision 기본 설정 확인
```

예:

```bash
yolo detect train \
  model=yolo26n.pt \
  data=datasets/my_dataset/data.yaml \
  epochs=100 \
  imgsz=640 \
  batch=4 \
  device=0
```

---

## 15. 환경 구축 완료 기준

아래가 되면 학습 환경 준비 완료다.

```text
[ ] python 가상환경 생성
[ ] ultralytics 설치
[ ] yolo version 확인
[ ] torch.cuda.is_available() 확인
[ ] data.yaml 경로 확인
[ ] smoke test 3 epoch 성공
[ ] runs/detect/smoke_test 생성 확인
```
