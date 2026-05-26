# 01. Day 11 SLAM 전체 흐름

## 1. Day 11의 목적

Day 11의 목적은 “로봇을 목적지까지 보내기”가 아니다.  
목적은 **로봇이 센서로 본 공간을 2D 지도 파일로 만드는 것**이다.

```text
Day 10
  Gazebo에서 로봇과 센서를 만들었다.

Day 11
  그 센서 데이터를 SLAM Toolbox에 넣어 지도를 만든다.

Day 12
  만든 지도 위에서 AMCL로 현재 위치를 추정한다.

Day 13
  추정된 위치를 기반으로 Nav2가 목표점까지 주행한다.
```

---

## 2. 실습에서 실제로 한 일

Day 11에서 한 작업은 다음 흐름이다.

```text
1. Gazebo world 실행
2. turtlebot entity spawn
3. robot_state_publisher로 로봇 link/joint TF 발행
4. Gazebo plugin으로 /robot_ns/scan, /robot_ns/odom, /robot_ns/tf 생성
5. SLAM Toolbox 실행
6. SLAM Toolbox가 /robot_ns/scan과 TF를 이용해 /robot_ns/map 생성
7. RViz2에서 map, laser scan, robot model 확인
8. teleop으로 로봇 이동
9. 지도가 넓어지는지 확인
10. map_saver_cli로 slam_map.pgm, slam_map.yaml 저장
11. map_server로 저장 지도 재로딩 확인
12. rosbag으로 offline SLAM 재현
```

---

## 3. 핵심 데이터 흐름

### 3.1 센서와 이동 데이터 생성

```text
Gazebo diff_drive plugin
  -> /robot_ns/cmd_vel 구독
  -> /robot_ns/odom 발행
  -> odom_robot_ns -> base_footprint TF 발행

Gazebo LiDAR plugin
  -> /robot_ns/scan 발행
  -> header.frame_id = base_scan

robot_state_publisher
  -> base_footprint -> base_link -> base_scan TF 발행
```

### 3.2 SLAM Toolbox 입력

```text
SLAM Toolbox
  <- /robot_ns/scan
  <- /robot_ns/tf
  <- /robot_ns/tf_static
  <- slam_param.yaml
```

SLAM Toolbox가 필요한 것은 단순히 거리값 배열이 아니다.

```text
/robot_ns/scan
  지금 LiDAR가 본 벽/장애물 거리

base_scan frame
  LiDAR가 로봇 몸체에서 어디에 붙어 있는지

odom_robot_ns -> base_footprint
  로봇이 시간에 따라 얼마나 움직였다고 추정되는지

map_robot_ns
  최종 지도를 그릴 기준 좌표계
```

### 3.3 SLAM Toolbox 출력

```text
SLAM Toolbox
  -> /robot_ns/map
  -> /robot_ns/map_updates
  -> map_robot_ns -> odom_robot_ns TF
```

최종적으로 정상 구조는 다음이 된다.

```text
map_robot_ns
  -> odom_robot_ns
    -> base_footprint
      -> base_link
        -> base_scan
```

---

## 4. 왜 map과 odom을 분리하는가?

초보자 입장에서 가장 헷갈리는 부분이 이거다.

```text
odom_robot_ns
  바퀴 오도메트리 기준으로 부드럽게 움직이는 좌표계
  시간이 지나면 오차가 누적됨

map_robot_ns
  SLAM이 만든 지도 기준 좌표계
  벽/코너/루프 클로저를 통해 오차를 보정한 전역 기준
```

`odom_robot_ns -> base_footprint`는 로봇이 계속 움직일 때 매끄럽게 이어져야 한다.  
하지만 오도메트리는 시간이 지나면 틀어진다.  
SLAM은 그 누적 오차를 `map_robot_ns -> odom_robot_ns` transform으로 보정한다.

그래서 전체 구조는 이렇게 된다.

```text
map_robot_ns -> odom_robot_ns -> base_footprint
```

이 구조 덕분에 로봇의 짧은 시간 움직임은 부드럽게 유지하면서, 전체 지도 기준 위치는 SLAM이 보정할 수 있다.

---

## 5. live SLAM과 offline SLAM의 차이

### 5.1 Gazebo live SLAM

```text
Gazebo가 지금 센서 데이터를 생성
  -> SLAM Toolbox가 지금 바로 지도 생성
  -> teleop으로 로봇을 직접 움직임
```

장점:

```text
실습 흐름을 직관적으로 볼 수 있다.
로봇을 어디로 움직일지 직접 조정할 수 있다.
```

단점:

```text
실수하면 같은 실험을 똑같이 반복하기 어렵다.
Gazebo, RViz2, SLAM이 동시에 떠서 환경이 무거울 수 있다.
```

### 5.2 rosbag offline SLAM

```text
예전에 녹화한 /scan, /odom, /tf를 재생
  -> SLAM Toolbox가 같은 데이터를 다시 처리
  -> 지도 생성 과정을 재현
```

장점:

```text
같은 입력 데이터로 반복 실험할 수 있다.
SLAM parameter를 바꿔가며 결과 차이를 비교하기 좋다.
```

단점:

```text
bag에 필요한 토픽이 빠져 있으면 재현이 안 된다.
현재 namespace/frame 설정과 bag 내부 토픽 이름이 안 맞으면 remap이 필요하다.
```

---

## 6. Day 11 성공 기준

아래가 확인되면 Day 11의 기본 성공 조건은 충족한 것이다.

```text
/robot_ns/scan이 나온다.
/robot_ns/odom이 나온다.
/robot_ns/tf, /robot_ns/tf_static이 나온다.
/robot_ns/map이 나온다.
RViz2 Fixed Frame이 map_robot_ns일 때 로봇과 지도가 같이 보인다.
map_robot_ns -> odom_robot_ns -> base_footprint TF가 연결된다.
teleop으로 움직이면 지도 영역이 넓어진다.
map_saver_cli로 slam_map.pgm, slam_map.yaml을 저장할 수 있다.
map_server로 저장한 지도를 다시 /robot_ns/map에 띄울 수 있다.
```

---

## 7. 문제 발생 시 확인 순서

SLAM이 안 될 때는 아래 순서로 확인한다.

```text
1. source install/setup.bash 했는가?
2. lee_robot_description 패키지가 인식되는가?
3. /robot_ns/scan이 발행되는가?
4. /robot_ns/odom이 발행되는가?
5. /robot_ns/tf와 /robot_ns/tf_static이 발행되는가?
6. /robot_ns/scan의 header.frame_id가 base_scan인가?
7. slam_param.yaml의 scan_topic이 /robot_ns/scan인가?
8. slam_param.yaml의 map_frame, odom_frame, base_frame이 실제 TF와 맞는가?
9. use_sim_time과 /clock이 맞는가?
10. RViz2 Fixed Frame이 map_robot_ns인가?
```

대부분의 SLAM 문제는 알고리즘 문제가 아니라 **토픽 이름, frame 이름, simulation time, remap 불일치**에서 생긴다.
