# Day 01~05에서 Day 06~13으로 이어지는 연결

## 1. 큰 흐름

```text
Day 01~05
  Python / NumPy / OpenCV / Calibration / YOLO / Kalman

Day 06~09
  ROS2 node / topic / service / action / custom interface / TF / rosbag

Day 10~13
  Gazebo / SLAM / AMCL / Nav2
```

## 2. 데이터 처리 관점의 연결

```text
NumPy 배열
  -> Image/LaserScan/IMU/Odometry message의 숫자 데이터 이해

OpenCV frame
  -> ROS2 Image topic 처리

YOLO bbox
  -> ObjectDetection custom message

Kalman Filter
  -> 센서 노이즈와 추정의 기본 감각

Matplotlib
  -> 센서 로그, NIS, SLAM/AMCL 실험 결과 분석
```

## 3. 구조 관점의 연결

```text
Python class
  -> ROS2 Node class

function
  -> callback

file/json/yaml
  -> ROS2 parameter yaml, map yaml, camera info yaml

thread/queue
  -> sensor pipeline, callback 처리 지연, message queue 이해
```

## 4. 카메라 인식에서 ROS2 topic으로

```text
OpenCV 단독 코드:
    cap.read()
    frame processing
    cv2.imshow()

ROS2 코드:
    /image_raw0 subscribe
    cv_bridge 변환
    frame processing
    /image_edge1 또는 /image_yolo1 publish
```

YOLO 결과는 두 가지 방식으로 나뉜다.

```text
사람이 보기 좋은 결과
  -> box가 그려진 Image topic

다른 node가 쓰기 좋은 결과
  -> ObjectDetectionArray custom message topic
```

## 5. 한 문장 요약

Day 01~05는 Python/OpenCV 단독 실습이 아니라, ROS2에서 센서 데이터를 topic/message/TF/rosbag으로 다루기 위한 전처리 학습이다.
