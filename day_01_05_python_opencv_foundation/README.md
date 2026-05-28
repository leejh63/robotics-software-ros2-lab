# Day 01~05 Python / OpenCV Foundation

이 폴더는 Day 01~05 학습 흐름을 정리한 문서 폴더다.

실제 `.py`, `.ipynb`, 이미지 샘플, Raspberry Pi 환경 메모는 아래 실행용 프로젝트 폴더에 둔다.

```text
projects/python_opencv_foundation_lab/
```

즉, 이 폴더는 코드 보관소가 아니라 “무엇을 왜 배웠고, 뒤쪽 ROS2/Navigation 실습과 어떻게 이어지는지”를 설명하는 위치다.

---

## 1. 이 파트의 위치

Day 01~05는 ROS2 실습으로 넘어가기 전의 Python/OpenCV 기반 perception 준비 단계다.

```text
Day 01~02
  Python, NumPy, Matplotlib, OOP, file/JSON, thread/process

Day 03
  OpenCV basic, color space, edge, contour, webcam loop

Day 04
  Camera calibration, YOLO, Kalman Filter, robot camera practice

Day 05
  Raspberry Pi / TurtleBot3 / ROS2 Humble / camera setup memo

Day 06~15
  ROS2 node/topic/message/TF/rosbag/Gazebo/SLAM/AMCL/Nav2로 확장
```

이번 정리에서 중심은 Python 문법 자체가 아니라 **OpenCV를 중심으로 한 카메라 데이터 처리 흐름**이다.

---

## 2. 왜 OpenCV 쪽을 더 중요하게 보는가

Python 기본기는 필요하지만, 포트폴리오 관점에서 강하게 연결되는 부분은 OpenCV 이후다.

```text
OpenCV image/frame 처리
  -> ROS2 Image topic 처리

Camera calibration
  -> CameraInfo, camera model, image rectification 이해

YOLO detection
  -> object detection topic, custom message, perception node 이해

Kalman Filter
  -> noisy measurement를 추정/보정하는 사고방식

Raspberry Pi camera setup
  -> 실제 TurtleBot3/카메라 환경과 연결
```

따라서 이 문서 세트는 `03_opencv_basic_edge_color_tracking.md`부터 `07_connection_to_ros2_camera_yolo.md`까지를 핵심 흐름으로 본다.

---

## 3. 기준 자료

정리 기준은 다음과 같다.

```text
원본 day_5.zip
  day_1/
  day_2/
  day_3/
  day_4/
  day_5/
  tranning/

정리 후 실행 코드 위치
  projects/python_opencv_foundation_lab/
```

`tranning/` 폴더에는 Day 01~05 외의 Day 09, Day 11, Day 12, Day 14 자료도 섞여 있었다. 현재 정리본에서는 `projects/python_opencv_foundation_lab/`를 직접 실습 코드 중심으로 유지하기 위해 원본 참고자료 중복본은 제외했다.

---

## 4. 읽는 순서

처음부터 복습한다면 아래 순서가 좋다.

1. `00_source_overview.md`
2. `01_python_env_numpy_matplotlib.md`
3. `02_oop_file_json_thread_sensor_sim.md`
4. `03_opencv_basic_edge_color_tracking.md`
5. `04_camera_calibration_foundation.md`
6. `05_yolo_kalman_foundation.md`
7. `06_robot_camera_practice_and_raspberry_pi.md`
8. `07_connection_to_ros2_camera_yolo.md`
9. `08_day01_05_review_questions.md`
10. `09_runtime_notes.md`
11. `commands/python_opencv_yolo_commands.md`
12. `commands/raspberry_pi_camera_setup_commands.md`
13. `troubleshooting/python_opencv_yolo_troubleshooting.md`

OpenCV 중심으로 빠르게 보고 싶다면 아래 순서를 우선한다.

```text
03_opencv_basic_edge_color_tracking.md
04_camera_calibration_foundation.md
05_yolo_kalman_foundation.md
06_robot_camera_practice_and_raspberry_pi.md
07_connection_to_ros2_camera_yolo.md
commands/python_opencv_yolo_commands.md
troubleshooting/python_opencv_yolo_troubleshooting.md
```

---

## 5. 실제 코드 위치

```text
projects/python_opencv_foundation_lab/01_python_basics/
projects/python_opencv_foundation_lab/02_sensor_data_concurrency/
projects/python_opencv_foundation_lab/03_opencv_image_processing/
projects/python_opencv_foundation_lab/04_camera_calibration_yolo_kalman/
projects/python_opencv_foundation_lab/05_raspberry_pi_turtlebot_camera_setup/
```

이 분리는 전체 저장소 구조 기준과 맞추기 위한 것이다.

```text
day_* 폴더
  -> 학습 흐름 정리 문서

projects/
  -> 실제 실행 가능한 코드 / workspace / notebook

appendix/
  -> 개념 심화, 참고 표, 보조 자료
```

---

## 6. 이 파트에서 반드시 잡고 넘어갈 것

```text
OpenCV 이미지는 NumPy 배열이다.
img[y, x]와 좌표 (x, y)는 순서가 다르다.
BGR/RGB/Gray/HSV는 목적이 다르다.
mask, edge, contour는 전통적인 image processing 흐름이다.
Camera calibration은 K와 distortion coefficient를 구하는 과정이다.
YOLO bbox는 이미지 좌표의 2D detection 결과다.
Kalman Filter는 detection 중심점의 흔들림을 줄이는 데 사용할 수 있다.
ROS2에서는 frame 처리 코드가 Image topic subscribe/publish 구조로 바뀐다.
```
