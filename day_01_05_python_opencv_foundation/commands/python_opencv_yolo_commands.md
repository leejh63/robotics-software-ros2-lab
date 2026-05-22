# Python / OpenCV / YOLO Commands

이 문서는 Day 01~05 실습을 다시 확인할 때 쓸 수 있는 명령어 모음이다. 명령어만 외우지 말고, 각 명령이 무엇을 확인하는지 같이 본다.

---

## 1. Python 환경 확인

```bash
python --version
which python
python -m pip --version
```

목적:

```text
현재 어떤 Python으로 실행 중인지 확인한다.
pip가 같은 Python 환경을 바라보는지 확인한다.
```

---

## 2. 가상환경 생성

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

비활성화:

```bash
deactivate
```

---

## 3. 기본 패키지 설치

```bash
python -m pip install numpy matplotlib opencv-python
python -m pip install ultralytics
python -m pip install scipy
```

현재 환경 저장:

```bash
python -m pip freeze > requirements.txt
```

다른 환경에서 재설치:

```bash
python -m pip install -r requirements.txt
```

---

## 4. 설치 확인

```bash
python -c "import numpy as np; print(np.__version__)"
python -c "import matplotlib; print(matplotlib.__version__)"
python -c "import cv2; print(cv2.__version__)"
python -c "from ultralytics import YOLO; print('ultralytics ok')"
python -c "import scipy; print(scipy.__version__)"
```

---

## 5. Python 파일 실행 예시

```bash
cd day_1
python hello.py
python test_1.py
```

thread/process 실습:

```bash
cd day_2
python 03_02_01_Python-Thread-Daemon.py
python 03_02_02_Python-Multi-Thread.py
python 03_02_05_Python-Thread-Practice.py
```

주의:

```text
일부 파일은 실습 중간 상태이므로 Runtime Observations 문서를 먼저 확인한다.
```

---

## 6. OpenCV 이미지 파일 확인

```bash
python -c "import cv2; img=cv2.imread('test.jpg'); print(None if img is None else img.shape)"
```

파일 경로가 헷갈리면:

```bash
python - <<'PY'
from pathlib import Path
p = Path('test.jpg')
print(p.resolve())
print(p.exists())
PY
```

---

## 7. 웹캠 장치 확인

```bash
ls /dev/video*
v4l2-ctl --list-devices
```

OpenCV 카메라 확인:

```bash
python -c "import cv2; cap=cv2.VideoCapture(0); print(cap.isOpened()); ret, frame=cap.read(); print(ret, None if frame is None else frame.shape); cap.release()"
```

---

## 8. YOLO 기본 추론

```bash
yolo detect predict model=yolov8n.pt source=test.jpg imgsz=640 conf=0.25 save=True
yolo detect predict model=yolov8n.pt source=0 imgsz=640 conf=0.25 show=True
```

---

## 9. Kalman NIS 평가 흐름

```bash
python 05.02.02.Webcam-Kalman.py
python 05.02.03.Kalman-NIS-Eval.py
```

첫 번째 스크립트가 `nis_log.csv`를 만들어야 두 번째 분석 스크립트가 동작한다.
