# 배경지식 지도

이 문서는 Day별 실습을 이해하기 위해 필요한 배경지식 지도를 정리한다.

---

## 1. 큰 흐름

```text
데이터 처리 기초
-> ROS2 통신 구조
-> 좌표계/센서 데이터
-> 시뮬레이션 로봇
-> 지도 생성
-> 위치 추정
-> 경로 계획과 제어
```

---

## 2. 개념 연결표

| 개념 | 연결되는 실습 | 왜 필요한가 |
|---|---|---|
| NumPy 배열 | OpenCV, camera image | 이미지가 결국 행렬/배열로 처리되기 때문 |
| Camera calibration | YOLO, robot camera | 이미지 좌표와 실제 카메라 왜곡을 이해하기 위해 필요 |
| ROS2 topic | 거의 모든 ROS2 실습 | 센서 데이터와 명령이 topic으로 흐르기 때문 |
| Service | spawn, map save 등 | 요청-응답형 작업에 필요 |
| Action | Nav2 goal | 오래 걸리는 작업의 goal/feedback/result 처리에 필요 |
| TF | Gazebo, SLAM, AMCL, Nav2 | 센서와 로봇, map/odom/base 좌표계를 연결하기 위해 필요 |
| Rosbag | sensor, SLAM, debug | 같은 데이터를 반복 재생하며 실험하기 위해 필요 |
| URDF/Xacro | Gazebo, RViz | 로봇의 link/joint 구조를 표현하기 위해 필요 |
| SLAM | map 생성 | 모르는 환경에서 지도를 만들기 위해 필요 |
| AMCL | localization | 이미 만든 지도에서 현재 위치를 추정하기 위해 필요 |
| Costmap | Nav2 | 장애물과 이동 가능 영역을 판단하기 위해 필요 |
| Planner/Controller | Nav2 | 경로 생성과 실제 속도 명령 생성을 나누기 위해 필요 |

---

## 3. 반복해서 확인할 핵심 질문

```text
이 데이터는 topic인가, TF인가, parameter인가?
이 이름은 topic 이름인가, frame 이름인가, node 이름인가?
이 기능은 직접 작성한 코드인가, ROS2 패키지가 제공한 기능인가?
이 결과는 RViz에서만 보이는 것인가, 실제 topic/TF로 발행되는 것인가?
```
