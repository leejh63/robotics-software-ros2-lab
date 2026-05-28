# 06. YOLO 파인튜닝 트러블슈팅 체크리스트

## 1. 학습이 시작되지 않음

### 증상

```text
dataset not found
images not found
labels not found
No labels found
```

### 확인

```text
data.yaml의 path가 맞는가?
train 경로가 맞는가?
val 경로가 맞는가?
images와 labels 구조가 맞는가?
라벨 파일 이름이 이미지 파일 이름과 같은가?
```

### 예

```text
images/train/img001.jpg
labels/train/img001.txt
```

---

## 2. 라벨을 못 읽음

### 원인

```text
라벨 txt가 없음
좌표 형식이 틀림
class id가 범위를 벗어남
라벨 파일이 비어 있는데 정책이 불명확함
```

### 정상 형식

```text
0 0.512 0.433 0.200 0.150
```

### 잘못된 형식

```text
0 512 433 200 150
```

위는 픽셀 좌표라서 틀렸다. YOLO는 0~1 정규화 좌표를 사용한다.

---

## 3. 학습은 되는데 아무것도 탐지 못함

### 가능한 원인

```text
class id와 names가 안 맞음
라벨 좌표가 잘못됨
객체 박스가 너무 작거나 이상함
데이터가 너무 적음
학습 epoch가 너무 적음
conf threshold가 너무 높음
```

### 확인 방법

```bash
yolo detect predict \
  model=runs/detect/train/weights/best.pt \
  source=test_images/ \
  conf=0.05 \
  save=True
```

conf를 낮춰서 뭔가 나오기는 하는지 본다.

---

## 4. train 성능은 좋은데 실제 카메라에서 안 됨

### 원인

```text
train 데이터와 실제 환경이 다름
조명/각도/거리 다양성이 부족함
배경이 너무 단순함
실제 카메라 해상도/왜곡/노이즈가 다름
과적합
```

### 해결

```text
실제 카메라로 데이터 추가 수집
val/test에 실제 환경 이미지 포함
freeze=10 실험
augmentation 조정
negative sample 추가
```

---

## 5. 오탐이 많음

### 증상

```text
없는 객체를 있다고 함
비슷한 배경을 객체로 잡음
반사광을 LED로 잡음
나사를 버튼으로 잡음
```

### 해결

```text
negative sample 추가
conf threshold 증가
라벨 기준 명확화
비슷한 물체를 배경으로 포함
클래스 정의 재검토
```

예:

```bash
yolo detect predict \
  model=best.pt \
  source=0 \
  conf=0.45
```

---

## 6. 미탐이 많음

### 증상

```text
실제 객체가 있는데 못 찾음
작은 객체를 놓침
어두운 환경에서 못 찾음
각도가 바뀌면 못 찾음
```

### 해결

```text
해당 상황 이미지 추가
imgsz 증가
객체가 크게 보이도록 촬영
해당 클래스 데이터 추가
conf threshold 낮춤
모델 크기 증가
```

예:

```bash
yolo detect train \
  model=yolo26s.pt \
  data=data.yaml \
  epochs=100 \
  imgsz=960 \
  name=fix_false_negative_img960
```

---

## 7. 특정 클래스만 성능이 낮음

### 원인

```text
해당 클래스 데이터 부족
라벨이 부정확함
다른 클래스와 시각적으로 비슷함
class id 오류
해당 클래스 객체가 작음
```

### 확인

```text
confusion_matrix.png
class별 mAP
해당 클래스 라벨 샘플
```

### 해결

```text
해당 클래스 이미지 추가
라벨 재검수
클래스 정의 구체화
비슷한 클래스 병합 여부 검토
```

---

## 8. 박스가 부정확함

### 원인

```text
라벨 박스가 대충 달림
객체 경계가 애매함
imgsz가 낮음
학습 부족
motion blur
```

### 해결

```text
라벨 박스 재검수
imgsz 증가
더 선명한 이미지 추가
epoch 증가
```

---

## 9. 과적합 의심

### 증상

```text
train loss는 계속 감소
val mAP는 정체 또는 감소
실제 카메라에서 성능 낮음
```

### 해결

```text
데이터 추가
freeze 적용
augmentation 강화
모델 크기 줄임
epoch 줄임
train/val 분리 재검토
```

명령어:

```bash
yolo detect train \
  model=yolo26n.pt \
  data=data.yaml \
  epochs=100 \
  imgsz=640 \
  freeze=10 \
  name=fix_overfit_freeze10
```

---

## 10. 학습 부족 의심

### 증상

```text
train loss도 높음
val mAP도 낮음
epoch 끝날 때까지 계속 좋아지는 중
```

### 해결

```text
epoch 증가
모델 크기 증가
learning rate 조정
라벨 오류 확인
데이터 수 증가
```

---

## 11. CUDA out of memory

### 해결 순서

```text
1. batch 줄이기
2. imgsz 줄이기
3. 모델 크기 줄이기
4. freeze 적용
5. 다른 GPU 사용
```

예:

```bash
yolo detect train \
  model=yolo26n.pt \
  data=data.yaml \
  epochs=100 \
  imgsz=640 \
  batch=4 \
  device=0
```

더 줄이기:

```bash
batch=2
batch=1
```

---

## 12. 학습이 너무 느림

### 원인

```text
CPU로 학습 중
모델이 큼
imgsz가 큼
batch가 작음
디스크가 느림
```

### 확인

```bash
nvidia-smi
```

### 해결

```text
device=0 설정
n 모델 사용
imgsz 감소
데이터를 SSD에 둠
batch 조정
```

---

## 13. 작은 객체를 못 찾음

### 우선순위

```text
1. 라벨이 정확한가?
2. 객체가 이미지에서 충분히 큰가?
3. imgsz가 충분한가?
4. 모델이 너무 작은가?
5. 해당 객체 데이터가 충분한가?
```

### 해결

```text
imgsz 640 -> 960 또는 1280
더 가까운 이미지 추가
crop 데이터셋 고려
yolo26s/m 비교
```

---

## 14. val 성능은 좋은데 배포 장비에서 느림

### 해결

```text
yolo26n 사용
imgsz 감소
ONNX export
TensorRT/OpenVINO 사용
conf threshold 조정
프레임 스킵 적용
ROI crop 적용
```

예:

```text
매 프레임 YOLO 실행하지 않고 3프레임에 한 번 실행
관심 영역만 crop해서 추론
```

---

## 15. 데이터셋 문제 빠른 체크리스트

```text
[ ] 이미지와 라벨 파일명이 일치하는가?
[ ] 라벨 좌표가 0~1인가?
[ ] class id가 0부터 시작하는가?
[ ] data.yaml의 names와 class id가 일치하는가?
[ ] train/val이 너무 비슷하지 않은가?
[ ] 실제 사용 환경 이미지가 val/test에 있는가?
[ ] negative sample이 있는가?
[ ] 클래스별 데이터 수가 너무 불균형하지 않은가?
```

---

## 16. 모델 학습 문제 빠른 체크리스트

```text
[ ] smoke test 3 epoch가 성공했는가?
[ ] baseline 결과가 있는가?
[ ] freeze=10 결과와 비교했는가?
[ ] results.png를 확인했는가?
[ ] confusion_matrix.png를 확인했는가?
[ ] 실제 이미지 폴더로 predict 해봤는가?
[ ] 웹캠으로 테스트했는가?
```

---

## 17. 최종 판단

문제가 생겼을 때 바로 모델을 바꾸지 말고 아래 순서로 본다.

```text
1. data.yaml 경로
2. 라벨 형식
3. class id
4. 라벨 품질
5. train/val 분리
6. 실제 환경 데이터
7. 학습 전략
8. 모델 크기
9. export/배포 최적화
```
