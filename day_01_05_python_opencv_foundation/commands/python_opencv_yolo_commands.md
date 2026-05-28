# Python / OpenCV / YOLO 명령어 정리

이 문서는 Day 01~05 실습을 다시 확인할 때 쓸 수 있는 명령어 모음이다.

실제 실행 기준 위치는 다음이다.

```bash
cd projects/python_opencv_foundation_lab
```

---

## 1. Python 환경 확인

```bash
python --version
which python
python -m pip --version
```

---

## 2. 가상환경 생성

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

비활성화:

```bash
deactivate
```

---

## 3. 설치 확인

```bash
python -c "import numpy as np; print(np.__version__)"
python -c "import matplotlib; print(matplotlib.__version__)"
python -c "import cv2; print(cv2.__version__)"
python -c "from ultralytics import YOLO; print('ultralytics ok')"
python -c "import scipy; print(scipy.__version__)"
```

---

## 4. Python 파일 실행 예시

```bash
cd 01_python_basics
python test_1.py
python hello.py
```

thread/process 실습:

```bash
cd ../02_sensor_data_concurrency
python 03_02_01_Python-Thread-Daemon.py
python 03_02_02_Python-Multi-Thread.py
python 03_02_05_Python-Thread-Practice.py
python 03_02_04_Python-Process-Queue.py
```

일부 파일은 실습 중간 상태이므로 `09_runtime_notes.md`를 먼저 확인한다.

---

## 5. OpenCV 이미지 처리

```bash
cd ../03_opencv_image_processing/parc
jupyter notebook 04_01_OpenCV-Basic.ipynb
jupyter notebook 04_02_OpenCV-Canny-Sobel.ipynb
python 04_03_00_OpenCV-Practice.py
```

이미지 파일 확인:

```bash
python -c "import cv2; img=cv2.imread('road_image.jpg'); print(None if img is None else img.shape)"
```

파일 경로가 헷갈리면:

```bash
python - <<'PY'
from pathlib import Path
p = Path('road_image.jpg')
print(p.resolve())
print(p.exists())
PY
```

---

## 6. 웹캠 장치 확인

```bash
ls /dev/video*
v4l2-ctl --list-devices
```

OpenCV 카메라 확인:

```bash
python -c "import cv2; cap=cv2.VideoCapture(0); print(cap.isOpened()); ret, frame=cap.read(); print(ret, None if frame is None else frame.shape); cap.release()"
```

---

## 7. Camera Calibration

```bash
cd ../../04_camera_calibration_yolo_kalman/prac
python 05_01_01_OpenCV-Calib-Capture.py
python 05_01_02_OpenCV-Calib-Undistort.py
jupyter notebook 05_01_OpenCV-Calibration.ipynb
```

---

## 8. YOLO 기본 추론

```bash
yolo detect predict model=yolov8n.pt source=bus.jpg imgsz=640 conf=0.25 save=True
python 05_02_1_YOLO_test.py
jupyter notebook 05_02_YOLO-Kalman.ipynb
python 05_03_Robot-Camera-Practice.py
```

YOLO 첫 실행 시 `yolov8n.pt` 다운로드가 필요할 수 있다. 오프라인 환경이면 모델 파일을 미리 준비해야 한다.

---

## 9. Raspberry Pi / TurtleBot3 메모

```bash
cd ../../05_raspberry_pi_turtlebot_camera_setup
cat in_rasp_install.md
```

이 파일은 자동 실행 스크립트가 아니라 환경 구축 메모다.
