# Day 01~05 Python / OpenCV / YOLO 학습 정리

이 폴더는 ROS2 실습으로 넘어가기 전에 다룬 Python, NumPy, Matplotlib, OpenCV, Camera Calibration, YOLO, Kalman Filter, Raspberry Pi 관련 내용을 정리한다.

핵심은 단순 문법 복습이 아니라, 뒤쪽 ROS2 camera, custom message, TF, rosbag, Nav2 실습으로 이어지는 데이터 처리 기준을 잡는 것이다.

---

## 1. 이 파트의 위치

Day 01~05는 로봇 시스템을 직접 다루기 전의 데이터 처리 기초에 해당한다.

```text
Day 01~02
  Python 문법, 함수, class, 파일, JSON, thread/process

Day 03
  OpenCV 이미지 처리, 색공간, edge, contour, webcam loop

Day 04
  Camera calibration, YOLO, Kalman Filter, robot camera practice

Day 05
  Raspberry Pi / TurtleBot 계열 환경 설정 메모

Day 06~13
  위 내용을 ROS2 node/topic/message/TF/rosbag/Gazebo/SLAM/AMCL/Nav2로 확장
```

여기서 중요한 점은 Day 01~05가 따로 떨어진 기초 문법이 아니라는 것이다. 뒤쪽 ROS2 실습에서 계속 다시 등장한다.

| Day 01~05에서 배운 것 | 뒤에서 연결되는 것 |
|---|---|
| Python class | `rclpy.node.Node`를 상속한 ROS2 node |
| dict/list | parameter, detection list, class id-name mapping |
| NumPy ndarray | OpenCV image, LaserScan ranges, bbox 좌표 |
| JSON/YAML | camera info, map yaml, nav2 params |
| thread/queue | camera loop, callback, producer-consumer 구조 이해 |
| OpenCV frame 처리 | ROS2 `sensor_msgs/Image` 처리 |
| YOLO detection | custom message, object detection topic |
| Kalman Filter | 센서 관측값의 흔들림 완화, 추정/보정 사고방식 |

---

## 2. 기준 자료

이 정리본은 아래 실습 자료를 기준으로 한다.

```text
$SOURCE_ARCHIVE/day_1
$SOURCE_ARCHIVE/day_2
$SOURCE_ARCHIVE/day_3
$SOURCE_ARCHIVE/day_4
$SOURCE_ARCHIVE/day_5
$SOURCE_NOTES/code
$ROS2_WS/src/camera_pkg
$ROS2_WS/src/my_if/msg
```

기존 자료는 흐름 확인용 참고이며, 이 정리본은 직접 실습한 코드와 노트를 기준으로 한다.

---

## 3. 읽는 순서

처음부터 다시 복습한다면 아래 순서가 좋다.

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
12. `troubleshooting/python_opencv_yolo_troubleshooting.md`

---

## 4. 이 폴더에서 확인할 내용

```text
- 실제 파일명 기준 소스 구성
- Python 기본기가 ROS2 node로 이어지는 이유
- NumPy shape/dtype/axis와 image/LiDAR/bbox 연결
- thread/process/queue가 sensor pipeline과 닮은 점
- OpenCV 색공간, mask, edge, contour의 역할
- Camera calibration의 내부 파라미터/왜곡 계수 의미
- YOLO 결과값 xyxy/conf/class와 custom message 연결
- Kalman Filter의 predict/update/P/Q/R/NIS 개념
- Raspberry Pi 환경 설정 메모의 의미
- 실행 시 주의해야 할 부분
```

---

## 5. 이 파트에서 반드시 잡고 넘어갈 것

Day 01~05를 끝내고 아래 질문에 답할 수 있으면 된다.

```text
Python list와 NumPy ndarray는 왜 다르게 쓰는가?
OpenCV 이미지에서 img[y, x]와 좌표 (x, y)는 왜 헷갈리는가?
BGR/RGB/HSV/Gray는 각각 언제 쓰는가?
Camera calibration 결과 K, dist는 무엇을 의미하는가?
YOLO bbox의 xyxy, xywh, conf, cls는 각각 무엇인가?
Kalman Filter에서 predict와 update는 무엇이 다른가?
Q, R, P를 크게/작게 잡으면 어떤 현상이 생기는가?
ROS2에서 Image message를 왜 cv_bridge로 OpenCV frame으로 바꾸는가?
YOLO 결과를 화면에 그리는 것과 topic으로 publish하는 것은 무엇이 다른가?
```
