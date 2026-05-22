# 00. Source File Map: Day 01~05 실제 파일 기준 정리

이 문서는 Day 01~05 학습 자료에서 어떤 파일이 어떤 역할을 하는지 빠르게 찾기 위한 지도다. 코드를 수정하지 않고 문서화만 진행하는 기준에서 작성했다.

---

## 1. Day 01: Python / NumPy / Matplotlib 기초

| 파일 | 역할 | 학습 포인트 |
|---|---|---|
| `day_1/hello.py` | NumPy import 확인, `test_1.py` 호출 | 모듈 import, 외부 파일 함수 호출 |
| `day_1/test_1.py` | 계산 기록을 저장하는 CLI 계산기 | 함수, 예외 처리, match-case, list history |
| `day_1/01_03_Python_Practice.ipynb` | Python 기본 실습 | 기본 자료형, 조건문, 반복문 |
| `day_1/02_01_Python-Class.ipynb` | class 실습 | 객체, 속성, 메서드 |
| `day_1/02_02_Python-NumPy.ipynb` | NumPy 실습 | ndarray, shape, vectorized operation |
| `day_1/02_03_Python-Data-Simulation.ipynb` | 데이터 시뮬레이션 | 센서값 생성, 그래프 확인 |
| `day_1/python.md` | Python 기본 정리 | 문법 복습 |
| `day_1/numpy.md` | NumPy 정리 | 배열 처리 복습 |
| `day_1/matplotlib.md` | Matplotlib 정리 | 시각화 복습 |

Day 01은 뒤쪽 ROS2 코드의 직접 원형은 아니지만, ROS2 Python node를 읽기 위한 바닥이다.

```text
function
  -> callback 함수

class
  -> Node class

list/dict
  -> message field, parameter, detection list

exception
  -> camera open failure, file path error 처리
```

---

## 2. Day 02: OOP / 파일 / JSON / Thread / Process

| 파일 | 역할 | 학습 포인트 |
|---|---|---|
| `day_2/ioff.py` | Sensor 추상 클래스, LidarSensor 예제 | OOP, ABC, 센서 객체화 |
| `day_2/calib.json` | 설정/보정값 예시 파일 | JSON 설정 파일 감각 |
| `day_2/03_01_Python-File-JSON.ipynb` | 파일/JSON 실습 | 저장/로드/재현성 |
| `day_2/03_02_01_Python-Thread-Daemon.py` | daemon thread 예제 | 메인 종료와 thread 생명주기 |
| `day_2/03_02_02_Python-Multi-Thread.py` | lidar/ultrasonic thread 예제 | 공유 데이터, Lock |
| `day_2/03_02_02_02_Python-Multi-Thread..py` | counter race condition 예제 | Lock이 없을 때 생기는 경쟁 상태 |
| `day_2/03_02_03_Python-Process-Pool.py` | Pool map 예제 | CPU 작업 병렬화 감각 |
| `day_2/03_02_04_Python-Process-Queue.py` | Process + Queue + Event | producer-consumer, 종료 신호 |
| `day_2/03_02_05_Python-Thread-Practice.py` | Thread + Queue 실습 | thread-safe queue |
| `day_2/file_json_regex.md` | 파일/JSON/regex 정리 | 로그 파싱 |
| `day_2/threading_process.md` | thread/process 정리 | 동시성 기초 |

이 파트는 ROS2의 callback, timer, executor, sensor pipeline을 이해할 때 도움이 된다. ROS2 자체가 thread/process를 직접 많이 작성하게 하지는 않지만, “동시에 여러 데이터 흐름이 돈다”는 감각이 중요하다.

---

## 3. Day 03: OpenCV Basic

| 파일 | 역할 | 학습 포인트 |
|---|---|---|
| `day_3/opencv_basic.md` | OpenCV 기본 정리 | 이미지 로드, shape, 표시 |
| `day_3/opencv_canny_sobel_function_guide.md` | Canny/Sobel 정리 | edge 검출 |
| `day_3/opencv_realtime_color_tracking.md` | 색상 추적 정리 | HSV mask, contour |
| `day_3/parc/04_01_OpenCV-Basic.ipynb` | 이미지 기본 실습 | BGR/RGB/Gray |
| `day_3/parc/04_02_OpenCV-Canny-Sobel.ipynb` | edge 실습 | blur, gradient, canny |
| `day_3/parc/04_03_00_OpenCV-Practice.py` | 실시간 OpenCV 실습 | webcam loop, threshold, contour |
| `day_3/parc/*.jpg`, `*.png` | 입력/결과 이미지 | 실습용 영상 데이터 |

OpenCV 파트는 뒤쪽 `camera_pkg`와 직접 연결된다.

```text
cv2.VideoCapture()
  -> ROS2 camera publisher node

cv2.cvtColor(), cv2.Canny()
  -> image processing subscriber node

cv2.imshow(), cv2.imwrite()
  -> ROS2 이미지 결과 확인 / snapshot service
```

---

## 4. Day 04: Camera Calibration / YOLO / Robot Camera

| 파일 | 역할 | 학습 포인트 |
|---|---|---|
| `day_4/05_01_OpenCV-Calibration.md` | 캘리브레이션 정리 | K, dist, 체커보드, 재투영 오차 |
| `day_4/05_01_OpenCV-Calibration-code-analysis.md` | 캘리브레이션 코드 분석 | capture, corner detection, undistort |
| `day_4/prac/05_01_01_OpenCV-Calib-Capture.py` | 체커보드 이미지 캡처 | calibration dataset 생성 |
| `day_4/prac/05_01_02_OpenCV-Calib-Undistort.py` | 실시간 왜곡 보정 | YAML 로드, undistort/remap |
| `day_4/05_02_YOLO-beginner-guide.md` | YOLO 입문 정리 | bbox, conf, class, NMS |
| `day_4/05_02_YOLO-Kalman-code-analysis.md` | YOLO/Kalman 코드 분석 | detection + tracking |
| `day_4/prac/05_02_1_YOLO_test.py` | YOLO detect/segment/pose 테스트 | Ultralytics 결과 파싱 |
| `day_4/prac/05_03_Robot-Camera-Practice.py` | 카메라+보정+YOLO+Kalman 통합 | perception pipeline |
| `day_4/yolo_finetuning_pipeline_md/*` | 파인튜닝 흐름 정리 | dataset, labeling, train, eval, export |

Day 04는 ROS2 perception 실습으로 이어지는 가장 중요한 연결부다.

---

## 5. Day 05: Raspberry Pi / TurtleBot 환경 메모

| 파일 | 역할 | 학습 포인트 |
|---|---|---|
| `day_5/in_rasp_install.md` | Raspberry Pi 환경 설정 메모 | SSH, netplan, swap, locale, TurtleBot 관련 설치 |

이 파일은 완성된 설치 매뉴얼이라기보다 실제 환경 구축 중 남긴 작업 기록에 가깝다. 나중에 실물 로봇 또는 보드에서 다시 재현할 때 참고용으로 분리해서 보는 것이 좋다.

---

## 6. Day 67에 남아 있는 Day 05 확장 코드

| 파일 | 역할 | 학습 포인트 |
|---|---|---|
| `day_67/code/05.02.02.Webcam-Kalman.py` | YOLOv8 + Kalman 실시간 webcam 추적 | bbox 중심점 안정화, Q/R 튜닝, NIS 로그 |
| `day_67/code/05.02.03.Kalman-NIS-Eval.py` | NIS 로그 분석 | 추정 일관성 평가, chi-square 기준 |

이 두 파일은 Day 05 개념을 더 실험적으로 확장한 코드다. 특히 NIS는 단순히 “필터를 붙였다”가 아니라 “필터 파라미터가 말이 되는지 평가한다”는 방향으로 넘어가는 좋은 학습 포인트다.

---

## 7. ROS2 Camera 쪽 연결 파일

Day 01~05 자체는 ROS2 패키지가 아니지만, 뒤에서 아래 파일들과 연결된다.

| 파일 | 연결되는 Day 01~05 개념 |
|---|---|
| `day_67/ws/src/camera_pkg/camera_pkg/imagePlee.py` | `cv2.VideoCapture()` + ROS2 Image publish |
| `day_67/ws/src/camera_pkg/camera_pkg/imageOPENlee.py` | `cv2.Canny()` + Image subscribe/publish |
| `day_67/ws/src/camera_pkg/camera_pkg/imageYOLOlee.py` | YOLO 결과를 이미지에 그려 재발행 |
| `day_67/ws/src/camera_pkg/camera_pkg/imgYOLOlee.py` | YOLO 결과를 custom message로 발행 |
| `day_67/ws/src/camera_pkg/camera_pkg/imageSlee.py` | 이미지 subscribe + snapshot service |
| `day_67/ws/src/my_if/msg/ObjectDetection.msg` | YOLO bbox/class/conf를 message field로 정의 |
| `day_67/ws/src/my_if/msg/ObjectDetectionArray.msg` | 여러 detection을 배열로 묶음 |

즉, Day 01~05의 흐름은 다음처럼 ROS2로 바뀐다.

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
