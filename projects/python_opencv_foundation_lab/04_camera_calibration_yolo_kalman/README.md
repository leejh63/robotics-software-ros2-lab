# 04. Camera Calibration / YOLO / Kalman

OpenCV 실습을 perception 파이프라인으로 확장하는 폴더다.

핵심 흐름:

```text
camera calibration
  -> camera matrix / distortion coefficients
  -> undistort
  -> YOLO detection
  -> bbox center extraction
  -> Kalman filtering
  -> detection log / warning logic
```

주요 파일:

```text
05_01_OpenCV-Calibration.md
05_01_OpenCV-Calibration-code-analysis.md
prac/05_01_01_OpenCV-Calib-Capture.py
prac/05_01_02_OpenCV-Calib-Undistort.py
05_02_YOLO-beginner-guide.md
05_02_YOLO-Kalman-code-analysis.md
prac/05_02_1_YOLO_test.py
prac/05_02_YOLO-Kalman.ipynb
prac/05_03_Robot-Camera-Practice.py
```
