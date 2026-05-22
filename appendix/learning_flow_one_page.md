# Learning Flow One Page

이 문서는 Day 01~13 전체 흐름을 한 페이지로 다시 잡기 위한 요약이다.

---

## 1. 전체 흐름

```text
Python / NumPy / OpenCV
  -> 이미지와 센서 데이터를 코드로 다루는 기초

Camera Calibration / YOLO / Kalman
  -> 카메라 입력, 객체 인식, 추적/필터링

ROS2 Foundation
  -> package, node, topic, service, action, launch, parameter, custom interface

TF2 / rosbag / sensor
  -> 좌표계 관계, 실험 기록, 데이터 재생

Gazebo / URDF / Xacro
  -> 가상 로봇, 링크/조인트, 센서 plugin, /scan, /odom, /cmd_vel

SLAM
  -> /robot_ns/scan + TF + odom을 이용해 /robot_ns/map 생성

AMCL
  -> 저장된 map 위에서 particle filter로 현재 위치 추정

Nav2
  -> AMCL pose + costmap + goal을 이용해 /robot_ns/cmd_vel 생성
```

---

## 2. 내 환경 기준 핵심 이름

```text
namespace: /robot_ns
map topic: /robot_ns/map
scan topic: /robot_ns/scan
odom topic: /robot_ns/odom
cmd_vel topic: /robot_ns/cmd_vel
TF topic: /robot_ns/tf, /robot_ns/tf_static
Nav2 action: /robot_ns/navigate_to_pose

map frame: map_robot_ns
odom frame: odom_robot_ns
base frame: base_footprint
scan frame: base_scan
```

---

## 3. Gazebo -> SLAM -> AMCL -> Nav2

```text
Gazebo plugin
  -> /robot_ns/scan
  -> /robot_ns/odom
  -> /robot_ns/cmd_vel 입력 대기

robot_state_publisher / Gazebo
  -> /robot_ns/tf, /robot_ns/tf_static

SLAM Toolbox
  input: /robot_ns/scan, /robot_ns/tf
  output: /robot_ns/map, map_robot_ns -> odom_robot_ns

Map Server
  input: slam_map.yaml
  output: /robot_ns/map

AMCL
  input: /robot_ns/map, /robot_ns/scan, TF
  output: particle cloud, pose, map_robot_ns -> odom_robot_ns

Nav2
  input: current pose, /robot_ns/map, /robot_ns/scan, goal
  output: /robot_ns/cmd_vel
```

---

## 4. 선별 심화에서 따로 깊게 본 핵심

```text
1. topic 이름과 frame 이름은 다르다.
2. namespace는 topic/node/action 이름에 붙지만 frame_id를 자동으로 바꾸지 않는다.
3. SLAM은 /scan만 보는 것이 아니라 odom/TF와 함께 map을 만든다.
4. AMCL은 map을 만들지 않고 저장된 map 위에서 pose를 찾는다.
5. Nav2 goal은 planner/controller/velocity smoother를 거쳐 /robot_ns/cmd_vel이 된다.
```

자세한 내용:

```text
10_selected_deep_dives/README.md
```

---

## 5. 지금 단계에서 제일 중요한 자기 설명

아래 문장을 스스로 설명할 수 있으면 현재 학습 정리의 핵심은 잡은 것이다.

```text
내 Gazebo 로봇은 /robot_ns/scan, /robot_ns/odom, /robot_ns/tf를 낸다.
SLAM은 이 데이터를 이용해 /robot_ns/map과 map_robot_ns -> odom_robot_ns를 만든다.
AMCL은 저장된 map과 현재 scan을 비교해 현재 pose를 찾고 map_robot_ns -> odom_robot_ns를 발행한다.
Nav2는 AMCL pose, costmap, goal을 이용해 path와 velocity command를 만들고 /robot_ns/cmd_vel로 내보낸다.
이 과정에서 topic 이름과 frame 이름은 다르며, topic remap은 frame_id를 자동으로 바꾸지 않는다.
```
