# Python / OpenCV Foundation Lab

이 폴더는 Day 01~05에서 직접 다룬 Python, NumPy, 파일/JSON, Thread/Process, OpenCV, Camera Calibration, YOLO, Kalman Filter 실습 코드를 모아 둔 프로젝트 폴더다.

상위 `day_01_05_python_opencv_foundation/` 폴더가 학습 흐름을 설명하는 문서라면, 이 폴더는 실제 `.py`, `.ipynb`, 이미지 샘플, 장비 설정 메모를 확인하는 위치다.

> 이 폴더는 완성 애플리케이션이 아니라 ROS2 perception 실습으로 넘어가기 전 단계의 foundation lab이다. 따라서 `ros2_foundation_lab`, `ros2_navigation_lab`, `ros2_pid_arm_lab`처럼 패키지화된 실행 프로젝트와는 성격이 다르다.

---

## 1. 정리 기준

이번 정리에서는 단순 Python 문법보다 OpenCV 기반 perception 흐름에 더 무게를 둔다.

```text
Python / NumPy 기본기
  -> 이미지가 NumPy 배열이라는 사실 이해

Sensor data / Thread / Process
  -> 센서 데이터가 주기적으로 들어오고, 처리 흐름이 분리될 수 있다는 감각 정리

OpenCV Basic / Edge / Color Tracking
  -> 이미지 처리 파이프라인 이해

Camera Calibration
  -> 카메라 내부 파라미터와 왜곡 보정 이해

YOLO / Kalman
  -> detection 결과를 후처리하고 추적값을 안정화하는 흐름 이해

Raspberry Pi / TurtleBot3 메모
  -> 이후 실물 카메라/로봇 환경으로 연결
```

---

## 2. 폴더 구성

```text
01_python_basics/
  Python 기본 문법, class, NumPy, Matplotlib 실습

02_sensor_data_concurrency/
  파일/JSON, sensor class, thread/process/queue 실습

03_opencv_image_processing/
  OpenCV 기본, edge, color tracking, webcam loop 실습

04_camera_calibration_yolo_kalman/
  Camera calibration, undistort, YOLO, Kalman, robot camera practice 실습

05_raspberry_pi_turtlebot_camera_setup/
  Raspberry Pi / TurtleBot3 / ROS2 Humble / camera setup 메모
```

원본 강의/참고 자료를 그대로 복사한 중복 폴더는 이 프로젝트 폴더에서 제외했다. 이 폴더는 직접 실습 코드와 해당 실습을 설명하는 문서만 남기는 방향으로 정리한다.

---

## 3. 우선 봐야 할 파일

OpenCV 중심으로 복습한다면 아래 순서가 좋다.

```text
03_opencv_image_processing/opencv_basic.md
03_opencv_image_processing/opencv_canny_sobel_function_guide.md
03_opencv_image_processing/opencv_realtime_color_tracking.md
03_opencv_image_processing/parc/04_01_OpenCV-Basic.ipynb
03_opencv_image_processing/parc/04_02_OpenCV-Canny-Sobel.ipynb
03_opencv_image_processing/parc/04_03_00_OpenCV-Practice.py
04_camera_calibration_yolo_kalman/05_01_OpenCV-Calibration.md
04_camera_calibration_yolo_kalman/prac/05_01_01_OpenCV-Calib-Capture.py
04_camera_calibration_yolo_kalman/prac/05_01_02_OpenCV-Calib-Undistort.py
04_camera_calibration_yolo_kalman/05_02_YOLO-beginner-guide.md
04_camera_calibration_yolo_kalman/prac/05_02_1_YOLO_test.py
04_camera_calibration_yolo_kalman/prac/05_03_Robot-Camera-Practice.py
```

Python/Thread 파트는 OpenCV/ROS2로 넘어가기 위한 기반이다. 포트폴리오 설명에서는 Python 기초를 길게 강조하기보다, 카메라 데이터를 처리하기 위한 준비 단계로 짧게 연결하는 편이 낫다.

---

## 4. 실행 전 준비

```bash
cd projects/python_opencv_foundation_lab
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

GUI가 필요한 OpenCV 실습은 WSL/SSH/headless 환경에서 창이 뜨지 않을 수 있다. 그런 경우에는 이미지 저장 방식으로 확인하거나, 실제 Ubuntu Desktop/라즈베리파이/노트북 GUI 환경에서 실행한다.

---

## 5. 실행 명령어

실행 명령어는 [`RUN_COMMANDS.md`](RUN_COMMANDS.md)에 따로 정리했다.

---

## 6. 정리하면서 제외한 것

다음 항목은 다른 `projects/` 코드와 비교했을 때 공개용 실행 코드로 보기 어렵거나, 중복/생성물 성격이 강해서 제외했다.

```text
reference_training_materials/
  -> 직접 실습 코드가 아니라 원본 참고 자료 중복본이므로 제외

02_sensor_data_concurrency/03.02.02.02.Python-Multi-Thread.py
  -> re import 누락, 파일 생성 순서 문제, top-level 실행 문제로 제외

02_sensor_data_concurrency/03_02_02_02_Python-Multi-Thread..py
  -> race condition 관찰용 중간 코드이고 파일명도 정리본에 부적절해서 제외

02_sensor_data_concurrency/ioff.py
  -> matplotlib 실시간 시각화 중간 실습 코드이며 top-level 실행 구조라 제외

02_sensor_data_concurrency/pickle.plk
  -> 실습 중 생성된 데이터 파일 성격이라 제외

03_opencv_image_processing/parc/output_gray.png
  -> 실행 결과물 성격의 대용량 이미지라 제외
```

---

## 7. 주의할 점

`.ipynb` 파일은 수업/실습 흐름을 따라가기 위한 자료다. 일부 셀에는 학습용 TODO나 실험 흔적이 남아 있을 수 있다.

공개용으로 강조할 코드는 다음 쪽을 우선 기준으로 본다.

```text
03_opencv_image_processing/parc/04_03_00_OpenCV-Practice.py
04_camera_calibration_yolo_kalman/prac/05_01_01_OpenCV-Calib-Capture.py
04_camera_calibration_yolo_kalman/prac/05_01_02_OpenCV-Calib-Undistort.py
04_camera_calibration_yolo_kalman/prac/05_02_1_YOLO_test.py
04_camera_calibration_yolo_kalman/prac/05_03_Robot-Camera-Practice.py
```
