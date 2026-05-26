# Python / OpenCV / YOLO 트러블슈팅

이 문서는 Day 01~05 실습에서 자주 만날 수 있는 문제와 확인 방법을 정리한다.

---

## 1. `ModuleNotFoundError`

현재 실행 중인 Python 환경과 패키지를 설치한 환경이 다를 때 발생한다.

```bash
which python
python -m pip --version
pip --version
```

조치:

```bash
source .venv/bin/activate
python -m pip install opencv-python ultralytics scipy
```

---

## 2. `cv2.imread()`가 `None`을 반환함

파일 경로나 작업 디렉토리가 틀렸을 가능성이 높다.

```python
from pathlib import Path
p = Path('test.jpg')
print(p.resolve())
print(p.exists())
```

---

## 3. 이미지 색이 이상함

OpenCV는 BGR, Matplotlib은 RGB 기준으로 보는 경우가 많다.

```python
img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
```

---

## 4. `cv2.imshow()` 창이 안 뜸

SSH, WSL, Docker, headless 환경에서는 GUI가 없을 수 있다. 이 경우는 저장 방식으로 확인한다.

```python
cv2.imwrite('debug.jpg', frame)
```

---

## 5. 웹캠이 열리지 않음

```bash
ls /dev/video*
v4l2-ctl --list-devices
```

`VideoCapture(0)`이 안 되면 `0`, `1`, `2`를 바꿔본다. Docker/WSL이면 장치 접근 자체가 안 될 수 있다.

---

## 6. HSV mask가 원하는 색을 못 잡음

```text
조명 변화가 큼
HSV 범위가 너무 좁음
빨간색처럼 Hue가 양 끝으로 나뉘는 색을 한 범위로만 잡음
노이즈가 많음
```

트랙바로 H/S/V 범위를 조정하고, 빨간색은 낮은 Hue 범위와 높은 Hue 범위를 둘 다 잡는다.

---

## 7. Canny edge가 너무 많거나 너무 적음

```python
blur = cv2.GaussianBlur(gray, (5, 5), 0)
edges = cv2.Canny(blur, 50, 150)
```

threshold와 blur를 같이 조정한다.

---

## 8. 체커보드 코너 검출 실패

```text
내부 코너 개수를 잘못 입력했다.
체커보드가 너무 작거나 흐리다.
조명 반사가 심하다.
사진이 흔들렸다.
체커보드 일부가 잘렸다.
```

체커보드 전체가 선명하게 보이도록 다양한 각도/거리에서 다시 찍는다.

---

## 9. YOLO가 아무것도 탐지하지 못함

```text
confidence threshold가 너무 높다.
모델이 해당 객체를 학습하지 않았다.
이미지 크기/조명/각도가 학습 데이터와 다르다.
custom model 경로가 틀렸다.
```

확인:

```bash
yolo detect predict model=yolov8n.pt source=test.jpg conf=0.05 save=True
```

---

## 10. YOLO가 너무 느림

```text
CPU로 돌고 있는가?
모델이 너무 큰가?
imgsz가 너무 큰가?
camera resolution이 너무 큰가?
show=True, save=True 때문에 느린가?
```

---

## 11. Kalman Filter가 너무 늦게 따라옴

```text
R이 너무 크다 -> YOLO 관측을 덜 믿음
Q가 너무 작다 -> 움직임 변화가 작다고 가정함
```

---

## 12. Kalman Filter가 너무 흔들림

```text
R이 너무 작다 -> YOLO 관측을 너무 믿음
Q가 너무 크다 -> 모델 불확실성이 너무 큼
```

---

## 13. NIS 평가 스크립트가 안 돌아감

`nis_log.csv`가 먼저 필요하고, `scipy`가 설치되어 있어야 한다.

```bash
ls nis_log.csv
python -m pip install scipy
```

---

## 14. 확인 순서

```text
1. 어떤 Python 환경인가?
2. 필요한 패키지가 설치되어 있는가?
3. 파일 경로와 working directory가 맞는가?
4. 카메라 장치가 열리는가?
5. GUI 환경이 있는가?
6. 모델 파일 경로가 맞는가?
7. threshold/parameter 문제가 아닌가?
8. 로그나 저장 결과로 확인할 수 있는가?
```
