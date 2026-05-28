# Python / OpenCV Foundation Lab 실행 명령어

이 문서는 `projects/python_opencv_foundation_lab/` 기준으로 실행한다.

```bash
cd projects/python_opencv_foundation_lab
```

---

## 1. Python 환경 준비

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

설치 확인:

```bash
python -c "import numpy as np; print(np.__version__)"
python -c "import cv2; print(cv2.__version__)"
python -c "import matplotlib; print(matplotlib.__version__)"
python -c "from ultralytics import YOLO; print('ultralytics ok')"
```

---

## 2. Python 기본 실습

```bash
cd 01_python_basics
python test_1.py
python hello.py
```

`hello.py`는 `test_1.py`를 import한 뒤 계산기 함수를 실행하므로, 입력형 CLI가 시작된다.

---

## 3. Sensor / Thread / Process 실습

```bash
cd ../02_sensor_data_concurrency
python 03_02_01_Python-Thread-Daemon.py
python 03_02_02_Python-Multi-Thread.py
python 03_02_03_Python-Process-Pool.py
python 03_02_04_Python-Process-Queue.py
python 03_02_05_Python-Thread-Practice.py
```

이 파트는 완성 로봇 코드를 만들기보다, 센서 데이터 생산/소비 흐름과 동시성 기본 구조를 확인하기 위한 예제다.

---

## 4. OpenCV 이미지 처리 실습

```bash
cd ../03_opencv_image_processing/parc
jupyter notebook 04_01_OpenCV-Basic.ipynb
jupyter notebook 04_02_OpenCV-Canny-Sobel.ipynb
```

웹캠 기반 HSV color tracking:

```bash
python 04_03_00_OpenCV-Practice.py
```

웹캠 장치 확인:

```bash
ls /dev/video*
v4l2-ctl --list-devices
python -c "import cv2; cap=cv2.VideoCapture(0); print(cap.isOpened()); ret, frame=cap.read(); print(ret, None if frame is None else frame.shape); cap.release()"
```

---

## 5. Camera Calibration 실습

```bash
cd ../../04_camera_calibration_yolo_kalman/prac
python 05_01_01_OpenCV-Calib-Capture.py
python 05_01_02_OpenCV-Calib-Undistort.py
```

캘리브레이션 notebook:

```bash
jupyter notebook 05_01_OpenCV-Calibration.ipynb
```

카메라 보정 결과 파일 이름은 코드마다 `camera_info.yaml`, `camera_calibration.yml` 등을 기대할 수 있으므로 실행 전 파일명을 확인한다.

---

## 6. YOLO / Kalman 실습

정적 이미지 또는 기본 모델 확인:

```bash
yolo detect predict model=yolov8n.pt source=bus.jpg imgsz=640 conf=0.25 save=True
python 05_02_1_YOLO_test.py
```

YOLO + Kalman notebook:

```bash
jupyter notebook 05_02_YOLO-Kalman.ipynb
```

Robot camera practice:

```bash
python 05_03_Robot-Camera-Practice.py
```

`yolov8n.pt`가 없으면 Ultralytics가 자동 다운로드를 시도할 수 있다. 오프라인 환경에서는 모델 파일을 미리 준비해야 한다.

---

## 7. Raspberry Pi / TurtleBot3 / Camera 메모

```bash
cd ../../05_raspberry_pi_turtlebot_camera_setup
cat in_rasp_install.md
```

이 파일은 실행 스크립트가 아니라 환경 구축 메모다. 네트워크 이름, IP, 장비 포트, ROS_DOMAIN_ID는 실제 장비 환경에 맞게 바꿔야 한다.
