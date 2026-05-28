# 00. Day 01~05 소스 구성 요약

이 문서는 원본 `day_5.zip`의 Day 01~05 자료를 현재 저장소 구조에 맞춰 어디에 두고 어떻게 읽을지 정리한 기준 문서다.

현재 구조의 원칙은 다음이다.

```text
day_01_05_python_opencv_foundation/
  -> 학습 흐름 정리 문서

projects/python_opencv_foundation_lab/
  -> 실제 실행 가능한 코드, notebook, 이미지 샘플, 장비 설정 메모

appendix/
  -> 개념 심화와 보조 참고 문서
```

---

## 1. 전체 배치 기준

| 원본 | 정리 후 위치 | 성격 |
|---|---|---|
| `day_1/*` | `projects/python_opencv_foundation_lab/01_python_basics/` | Python/NumPy/Matplotlib 실습 |
| `day_2/*` | `projects/python_opencv_foundation_lab/02_sensor_data_concurrency/` | OOP, file/JSON, thread/process 실습 |
| `day_3/*` | `projects/python_opencv_foundation_lab/03_opencv_image_processing/` | OpenCV basic, edge, color tracking 실습 |
| `day_4/prac/*` | `projects/python_opencv_foundation_lab/04_camera_calibration_yolo_kalman/` | calibration, YOLO, Kalman 실행 코드 |
| `day_4/yolo_finetuning_pipeline_md/*` | `appendix/yolo_finetuning_pipeline/` | YOLO fine-tuning 보조 문서 |
| `day_5/in_rasp_install.md` | `projects/python_opencv_foundation_lab/05_raspberry_pi_turtlebot_camera_setup/` | Raspberry Pi/TurtleBot3 환경 메모 |

---

## 2. Day 01: Python / NumPy / Matplotlib 기초

| 파일 | 역할 | 학습 포인트 |
|---|---|---|
| `01_python_basics/hello.py` | NumPy import 확인, `test_1.py` 호출 | 모듈 import, 외부 파일 함수 호출 |
| `01_python_basics/test_1.py` | 계산 기록을 저장하는 CLI 계산기 | 함수, 예외 처리, match-case, list history |
| `01_python_basics/01_03_Python_Practice.ipynb` | Python 기본 실습 | 기본 자료형, 조건문, 반복문 |
| `01_python_basics/02_01_Python-Class.ipynb` | class 실습 | 객체, 속성, 메서드 |
| `01_python_basics/02_02_Python-NumPy.ipynb` | NumPy 실습 | ndarray, shape, vectorized operation |
| `01_python_basics/02_03_Python-Data-Simulation.ipynb` | 데이터 시뮬레이션 | 센서값 생성, 그래프 확인 |

Day 01은 뒤쪽 OpenCV와 ROS2 Python node를 읽기 위한 바닥이다. 다만 포트폴리오에서 핵심으로 밀 부분은 아니다.

---

## 3. Day 02: OOP / 파일 / JSON / Thread / Process

| 파일 | 역할 | 학습 포인트 |
|---|---|---|
| `02_sensor_data_concurrency/calib.json` | 설정/보정값 예시 파일 | JSON 설정 파일 감각 |
| `02_sensor_data_concurrency/03_01_Python-File-JSON.ipynb` | 파일/JSON 실습 | 저장/로드/재현성 |
| `02_sensor_data_concurrency/03_02_02_Python-Multi-Thread.py` | lidar/ultrasonic thread 예제 | 공유 데이터, Lock |
| `02_sensor_data_concurrency/03_02_03_Python-Process-Pool.py` | Process Pool 예제 | 독립 작업 병렬 처리 |
| `02_sensor_data_concurrency/03_02_04_Python-Process-Queue.py` | Process + Queue + Event | producer-consumer, 종료 신호 |
| `02_sensor_data_concurrency/03_02_05_Python-Thread-Practice.py` | Thread + Queue 예제 | 생산자/소비자 구조 |

이 파트는 ROS2 callback, timer, executor, queue 개념을 이해하기 위한 준비 단계다.

---

## 4. Day 03: OpenCV Basic / Edge / Color Tracking

Day 01~05에서 가장 우선순위가 높은 파트다.

| 파일 | 역할 | 학습 포인트 |
|---|---|---|
| `03_opencv_image_processing/opencv_basic.md` | OpenCV 기본 정리 | 이미지 로드, shape, 표시 |
| `03_opencv_image_processing/opencv_canny_sobel_function_guide.md` | Canny/Sobel 정리 | edge 검출 |
| `03_opencv_image_processing/opencv_realtime_color_tracking.md` | 색상 추적 정리 | HSV mask, contour |
| `03_opencv_image_processing/parc/04_01_OpenCV-Basic.ipynb` | 이미지 기본 실습 | BGR/RGB/Gray |
| `03_opencv_image_processing/parc/04_02_OpenCV-Canny-Sobel.ipynb` | edge 실습 | blur, gradient, canny |
| `03_opencv_image_processing/parc/04_03_00_OpenCV-Practice.py` | 실시간 OpenCV 실습 | webcam loop, threshold, contour |

OpenCV 파트는 뒤쪽 ROS2 camera 실습과 직접 연결된다.

```text
cv2.VideoCapture()
  -> ROS2 camera publisher node

cv2.cvtColor(), cv2.Canny()
  -> image processing subscriber node

cv2.imshow(), cv2.imwrite()
  -> ROS2 이미지 결과 확인 / snapshot service
```

---

## 5. Day 04: Camera Calibration / YOLO / Kalman

| 파일 | 역할 | 학습 포인트 |
|---|---|---|
| `04_camera_calibration_yolo_kalman/05_01_OpenCV-Calibration.md` | 캘리브레이션 정리 | K, dist, 체커보드, 재투영 오차 |
| `04_camera_calibration_yolo_kalman/05_01_OpenCV-Calibration-code-analysis.md` | 캘리브레이션 코드 분석 | capture, corner detection, undistort |
| `04_camera_calibration_yolo_kalman/prac/05_01_01_OpenCV-Calib-Capture.py` | 체커보드 이미지 캡처 | calibration dataset 생성 |
| `04_camera_calibration_yolo_kalman/prac/05_01_02_OpenCV-Calib-Undistort.py` | 실시간 왜곡 보정 | YAML 로드, undistort/remap |
| `04_camera_calibration_yolo_kalman/05_02_YOLO-beginner-guide.md` | YOLO 입문 정리 | bbox, conf, class, NMS |
| `04_camera_calibration_yolo_kalman/05_02_YOLO-Kalman-code-analysis.md` | YOLO/Kalman 코드 분석 | detection + tracking |
| `04_camera_calibration_yolo_kalman/prac/05_02_1_YOLO_test.py` | YOLO detect/segment/pose 테스트 | Ultralytics 결과 파싱 |
| `04_camera_calibration_yolo_kalman/prac/05_03_Robot-Camera-Practice.py` | 카메라+보정+YOLO+Kalman 통합 | perception pipeline |

Day 04는 ROS2 perception 실습으로 이어지는 핵심 연결부다.

---

## 6. Day 05: Raspberry Pi / TurtleBot3 / Camera 환경 메모

| 파일 | 역할 | 학습 포인트 |
|---|---|---|
| `05_raspberry_pi_turtlebot_camera_setup/in_rasp_install.md` | Raspberry Pi/TurtleBot3/ROS2/camera 설정 메모 | SSH, netplan, swap, locale, ROS2 Humble, TurtleBot3, v4l2 camera, OpenCR |

이 파일은 자동 설치 스크립트가 아니라 실제 장비 설정 중 남긴 작업 기록이다. 실행 전 IP, hostname, Wi-Fi, device path, ROS_DOMAIN_ID를 현재 환경에 맞게 확인해야 한다.

---

## 7. ROS2 Camera 쪽 연결

Day 01~05 자체는 ROS2 패키지가 아니지만, 뒤쪽 ROS2 코드에서 아래 흐름으로 바뀐다.

```text
OpenCV 단독 코드
  frame = cap.read()
  edge = cv2.Canny(frame)
  results = model(frame)

ROS2 코드
  /image_raw0 subscribe
  cv_bridge로 frame 변환
  OpenCV/YOLO 처리
  /image_edge1, /image_yolo1, /img_yolo1 publish
```

즉, Day 01~05는 “카메라 데이터를 어떻게 읽고 처리할 것인가”를 익히는 구간이고, Day 06 이후는 이것을 ROS2 node/topic/message 구조로 옮기는 구간이다.
