# Appendix. Day 10 Gazebo에서 Day 11 SLAM으로 이어지는 연결

## 1. 핵심 연결

Day 10의 목표는 Gazebo에서 로봇과 센서 데이터를 만드는 것이고, Day 11의 목표는 그 데이터를 SLAM Toolbox가 사용해 지도를 만드는 것이다.

```text
Day 10
  Gazebo + URDF/XACRO + plugin
  -> /robot_ns/scan, /robot_ns/odom, /robot_ns/tf 생성

Day 11
  SLAM Toolbox
  -> /robot_ns/scan + TF 사용
  -> /robot_ns/map 생성
```

## 2. Day 10 산출물이 Day 11에서 쓰이는 방식

| Day 10에서 만든 것 | Day 11에서의 역할 |
|---|---|
| `turtlebot.xacro` | 로봇 link/joint 구조 제공 |
| `turtlebot_gaze.xacro` | Gazebo plugin으로 sensor/drive topic 생성 |
| `base_scan` frame | LiDAR가 로봇 어디에 붙어 있는지 표현 |
| `/robot_ns/scan` | SLAM Toolbox의 핵심 입력 |
| `/robot_ns/odom` | odometry 확인 및 디버깅 |
| `odom_robot_ns -> base_footprint` TF | 로봇의 odometry 기준 위치 |
| `/robot_ns/tf`, `/robot_ns/tf_static` | SLAM이 scan과 robot frame을 연결할 때 사용 |
| `/robot_ns/cmd_vel` | teleop으로 로봇을 움직여 지도를 확장하는 입력 |
| `slam.world` | SLAM 실습용 환경 |

## 3. SLAM Toolbox 입장에서 필요한 최소 조건

SLAM Toolbox가 지도를 만들기 위한 최소 조건은 다음이다.

```text
1. /robot_ns/scan이 발행된다.
2. /robot_ns/scan의 frame_id가 TF 트리에 연결된다.
3. odom_robot_ns -> base_footprint TF가 있다.
4. base_footprint -> base_link -> base_scan TF가 있다.
5. slam_param.yaml의 frame/topic 설정이 실제 값과 맞는다.
6. use_sim_time이 Gazebo 또는 bag의 /clock과 맞는다.
```

조건이 맞으면 SLAM Toolbox가 다음을 만든다.

```text
/robot_ns/map
map_robot_ns -> odom_robot_ns
```

## 4. 전체 데이터 흐름

```text
teleop_twist_keyboard
  -> /robot_ns/cmd_vel
  -> Gazebo diff_drive plugin
  -> 로봇 이동

로봇 이동 결과:
  Gazebo diff_drive plugin
    -> /robot_ns/odom
    -> odom_robot_ns -> base_footprint TF

  Gazebo LiDAR plugin
    -> /robot_ns/scan

  robot_state_publisher
    -> base_footprint -> base_link -> base_scan TF

SLAM Toolbox:
  입력:
    /robot_ns/scan
    /robot_ns/tf
    /robot_ns/tf_static

  출력:
    /robot_ns/map
    map_robot_ns -> odom_robot_ns TF

RViz2:
  표시:
    /robot_ns/map
    /robot_ns/scan
    RobotModel
    TF tree
```

## 5. 자주 생기는 착각

### 착각 1. `/robot_ns/scan`만 있으면 SLAM이 된다

아니다. `/robot_ns/scan`이 어느 좌표계에서 나온 값인지 알아야 하므로 TF가 필요하다.

```text
odom_robot_ns -> base_footprint -> base_link -> base_scan
```

이 체인이 끊기면 SLAM은 scan을 지도 위에 제대로 배치할 수 없다.

### 착각 2. `/robot_ns/map`과 `map_robot_ns`는 같은 것이다

아니다.

```text
/robot_ns/map
  지도 데이터가 오가는 topic

map_robot_ns
  지도 기준 좌표계 frame
```

둘은 이름이 비슷하지만 역할이 다르다.

### 착각 3. map_server도 SLAM이다

아니다.

```text
SLAM Toolbox
  센서 데이터로 새 지도를 만든다.

map_server
  이미 저장된 지도 파일을 다시 topic으로 발행한다.
```

### 착각 4. 오프라인 SLAM은 저장 지도 로딩이다

아니다.

```text
저장 지도 로딩
  slam_map.yaml -> map_server -> /robot_ns/map

오프라인 SLAM
  rosbag2의 /robot_ns/scan + TF -> SLAM Toolbox -> 새 /robot_ns/map
```

## 6. Day 12 AMCL로 이어지는 지점

Day 11에서 만든 `.pgm`/`.yaml` 지도는 Day 12 AMCL에서 사용된다.

```text
Day 11 SLAM
  /robot_ns/map 생성
  map_saver_cli로 slam_map.yaml + slam_map.pgm 저장

Day 12 AMCL
  map_server가 저장 지도를 발행
  AMCL이 /scan과 particle filter로 map 안에서 로봇 위치 추정
```

즉 Day 11의 최종 산출물은 Day 12의 입력이다.
