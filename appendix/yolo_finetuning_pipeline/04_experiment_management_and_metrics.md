# 04. 실험 관리와 평가 지표

## 1. 왜 실험 관리가 필요한가?

YOLO 파인튜닝은 한 번에 끝나는 작업이 아니다.

```text
baseline
freeze
two-stage
imgsz 변경
모델 크기 변경
augmentation 변경
데이터셋 버전 변경
```

이걸 기록하지 않으면 나중에 어떤 모델이 왜 좋은지 모른다.

---

## 2. 실험 폴더 이름 규칙

추천 형식:

```text
날짜_모델_전략_imgsz_epoch_데이터버전
```

예:

```text
0429_yolo26n_baseline_img640_ep100_dsv1
0429_yolo26n_freeze10_img640_ep100_dsv1
0429_yolo26s_baseline_img960_ep100_dsv1
0501_yolo26n_twostage_img640_dsv2
```

---

## 3. 실험 로그 템플릿

```markdown
# Experiment Log

## exp01_baseline

- date:
- model:
- dataset version:
- data.yaml:
- epochs:
- imgsz:
- batch:
- freeze:
- lr0:
- augmentation:
- result:
  - precision:
  - recall:
  - mAP50:
  - mAP50-95:
- actual test:
  - webcam FPS:
  - false positive:
  - false negative:
- observation:
- next action:
```

---

## 4. 주요 평가 지표

### Precision

모델이 찾았다고 한 것 중 실제로 맞은 비율이다.

```text
Precision 높음:
    오탐이 적다.

Precision 낮음:
    엉뚱한 것을 자주 잡는다.
```

예:

```text
모델이 button이라고 100개 예측
그중 진짜 button이 80개

Precision = 80 / 100 = 0.8
```

### Recall

실제로 존재하는 객체 중 모델이 찾아낸 비율이다.

```text
Recall 높음:
    미탐이 적다.

Recall 낮음:
    실제 객체를 많이 놓친다.
```

예:

```text
이미지 안에 실제 button이 100개 있음
모델이 70개 찾음

Recall = 70 / 100 = 0.7
```

### mAP50

IoU 0.5 기준 평균 precision이다.

```text
mAP50 높음:
    대략적인 위치까지 포함해서 잘 찾는다.
```

### mAP50-95

IoU 0.5부터 0.95까지 여러 기준을 평균낸 값이다.

```text
mAP50은 높은데 mAP50-95가 낮음:
    찾기는 하지만 박스가 정밀하지 않을 수 있다.
```

---

## 5. IoU란?

IoU는 예측 박스와 정답 박스가 얼마나 겹치는지 나타낸다.

```text
IoU = 겹치는 영역 / 합쳐진 영역
```

예:

```text
IoU 0.9:
    거의 정확히 박스를 그림

IoU 0.5:
    대충 맞음

IoU 0.1:
    거의 틀림
```

---

## 6. Validation 실행

```bash
yolo detect val \
  model=runs/detect/exp01_baseline/weights/best.pt \
  data=data.yaml \
  imgsz=640 \
  device=0
```

Python:

```python
from ultralytics import YOLO

model = YOLO("runs/detect/exp01_baseline/weights/best.pt")
metrics = model.val(data="data.yaml", imgsz=640)

print("mAP50-95:", metrics.box.map)
print("mAP50:", metrics.box.map50)
```

---

## 7. 실제 이미지 추론 비교

```bash
yolo detect predict \
  model=runs/detect/exp01_baseline/weights/best.pt \
  source=test_images/ \
  imgsz=640 \
  conf=0.25 \
  save=True \
  name=predict_exp01
```

결과는 보통 아래에 생긴다.

```text
runs/detect/predict_exp01/
```

---

## 8. conf threshold 조정

`conf`는 confidence threshold다.

```bash
yolo detect predict \
  model=best.pt \
  source=test.jpg \
  conf=0.25
```

낮추면:

```text
더 많이 검출
미탐 감소 가능
오탐 증가 가능
```

올리면:

```text
더 확실한 것만 검출
오탐 감소 가능
미탐 증가 가능
```

실전에서는 conf 값을 여러 개로 비교한다.

```bash
conf=0.15
conf=0.25
conf=0.40
conf=0.60
```

---

## 9. 클래스별 성능 확인

전체 mAP만 보면 안 된다.

예:

```text
red_led mAP 높음
blue_led mAP 높음
button mAP 낮음
```

이 경우 전체 성능이 괜찮아 보여도 button 데이터가 문제다.

확인할 것:

```text
button 이미지 수 부족
button 라벨 박스 부정확
button이 너무 작음
button과 배경이 비슷함
button이 다른 클래스와 혼동됨
```

---

## 10. Confusion matrix 해석

`confusion_matrix.png`를 본다.

예:

```text
red_led가 blue_led로 잘못 분류됨
button이 background로 빠짐
background가 red_led로 오탐됨
```

해석:

```text
클래스 간 혼동:
    두 클래스가 시각적으로 비슷하거나 라벨 기준이 애매함

background 오탐:
    negative sample 부족 가능

background 미탐:
    객체가 작거나 흐리거나 라벨 품질 문제
```

---

## 11. train loss와 val metric 관계

### 정상적인 경우

```text
train loss 감소
val mAP 증가
```

### 과적합 의심

```text
train loss 계속 감소
val mAP 정체 또는 감소
실제 테스트 성능 낮음
```

대응:

```text
데이터 추가
freeze 적용
augmentation 강화
epoch 줄이기
모델 크기 줄이기
train/val 분리 재검토
```

### 학습 부족 의심

```text
train loss 높음
val mAP 낮음
둘 다 개선 여지 있음
```

대응:

```text
epoch 증가
learning rate 조정
모델 크기 증가
라벨 오류 확인
```

---

## 12. 실험 비교표 예시

| 실험 | 모델 | 전략 | imgsz | mAP50 | mAP50-95 | 실제 FPS | 관찰 |
|---|---|---:|---:|---:|---:|---:|---|
| exp01 | yolo26n | baseline | 640 | 0.82 | 0.51 | 35 | button 미탐 |
| exp02 | yolo26n | freeze10 | 640 | 0.84 | 0.53 | 36 | 오탐 감소 |
| exp03 | yolo26n | two-stage | 640 | 0.87 | 0.57 | 35 | 가장 안정적 |
| exp04 | yolo26s | baseline | 640 | 0.89 | 0.60 | 24 | 정확도 좋음, 느림 |
| exp05 | yolo26n | baseline | 960 | 0.88 | 0.59 | 18 | 작은 객체 개선 |

---

## 13. 데이터 버전 관리

데이터셋도 버전을 나눠야 한다.

```text
my_dataset_v1:
    최초 라벨링

my_dataset_v2:
    실제 카메라 미탐 이미지 추가

my_dataset_v3:
    라벨 오류 수정
    negative sample 추가
```

실험할 때 반드시 데이터 버전을 기록한다.

```text
exp01_baseline_dsv1
exp02_freeze10_dsv1
exp03_baseline_dsv2
```

---

## 14. 오탐/미탐 분석법

실제 테스트 후 이미지를 세 폴더로 나눈다.

```text
analysis/
├── false_positive/
├── false_negative/
├── bad_box/
└── good/
```

### false_positive

모델이 없는 객체를 있다고 함.

대응:

```text
negative sample 추가
conf threshold 증가
라벨 기준 재검토
비슷한 배경 이미지 추가
```

### false_negative

실제 객체가 있는데 못 찾음.

대응:

```text
해당 상황 이미지 추가
imgsz 증가
객체가 작으면 촬영 방식 변경
해당 클래스 라벨 품질 확인
```

### bad_box

객체는 찾았지만 박스가 부정확함.

대응:

```text
라벨 박스 재검수
imgsz 증가
epoch 증가
데이터 다양화
```

---

## 15. 실제 카메라 테스트

학습 후 반드시 실제 카메라에서 본다.

```bash
yolo detect predict \
  model=runs/detect/exp03_stage2/weights/best.pt \
  source=0 \
  imgsz=640 \
  conf=0.25 \
  show=True
```

실제 카메라에서 확인할 것:

```text
조명 바뀌면 되는가?
각도 바뀌면 되는가?
거리 바뀌면 되는가?
배경이 복잡해도 되는가?
FPS가 충분한가?
오탐이 안전상 문제를 만들지 않는가?
미탐이 서비스상 문제를 만들지 않는가?
```

---

## 16. 성공 기준을 미리 정하라

프로젝트마다 성공 기준이 다르다.

예:

```text
공장 불량 탐지:
    Recall이 매우 중요
    불량을 놓치면 안 됨

로봇 장애물 탐지:
    미탐이 위험
    실시간성 중요

상품 인식:
    Precision 중요
    엉뚱한 상품으로 인식하면 안 됨

LED 상태 인식:
    조명/반사 오탐이 중요
```

성공 기준 예시:

```text
mAP50 >= 0.90
Recall >= 0.95
Precision >= 0.90
실제 장비 FPS >= 20
오탐 유형 중 치명적 케이스 0건
```

---

## 17. 최종 모델 선정 기준

단순히 mAP가 가장 높은 모델이 최종 모델은 아니다.

최종 기준:

```text
val mAP
test mAP
실제 카메라 성능
FPS
모델 크기
배포 환경 호환성
오탐/미탐 위험도
유지보수 편의성
라이선스 조건
```

예를 들어 `yolo26s`가 mAP는 높지만 라즈베리파이에서 너무 느리면 `yolo26n`이 더 좋은 선택일 수 있다.

---

## 18. 결론

실험 관리는 아래 원칙을 따르면 된다.

```text
1. 한 번에 하나의 변수만 바꾼다.
2. 실험 이름에 설정을 남긴다.
3. 데이터 버전을 기록한다.
4. mAP만 보지 말고 실제 카메라를 본다.
5. 오탐/미탐 이미지를 모아 다음 데이터셋에 반영한다.
```
