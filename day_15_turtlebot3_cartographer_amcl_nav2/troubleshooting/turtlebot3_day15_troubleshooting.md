# TurtleBot3 Day 15 Troubleshooting

이번 실습 중 실제로 겪은 문제와 해결 방법을 정리한다.

## 1. 환경 파일 경로 오류

### 증상

```text
bash: /home/<user>/Workspace/turtlebot3_ws/install/setup.bash: No such file or directory
```

### 원인

환경 파일 안에 PDF 예시 경로가 고정되어 있었다.

```bash
source ~/Workspace/turtlebot3_ws/install/setup.bash
```

하지만 실제 워크스페이스는 다음이었다.

```bash
$TB3_WS
```

### 해결

환경 파일을 실제 경로 기준으로 수정하거나, 현재 위치 기준으로 `install/setup.bash`를 자동 탐색하도록 구성한다.

## 2. RViz에서 Map이 보이지 않음

### 증상

RViz에서 `/map` Display가 있지만 다음처럼 보였다.

```text
Resolution 0
Width 0
Height 0
Status: Warn
```

### 확인

```bash
ros2 lifecycle get /map_server
```

정상:

```text
active [3]
```

```bash
ros2 topic info /map -v
```

정상 조건:

```text
Publisher count: 1
Reliability: RELIABLE
Durability: TRANSIENT_LOCAL
```

```bash
ros2 topic echo /map nav_msgs/msg/OccupancyGrid --once \
--qos-durability transient_local \
--qos-reliability reliable
```

정상 출력 예:

```yaml
info:
  resolution: 0.05
  width: 125
  height: 116
```

### 해결

1. RViz Map Display를 삭제 후 `By topic -> /map -> Map`으로 다시 추가한다.
2. Map QoS를 맞춘다.

```text
Reliability: Reliable
Durability: Transient Local
```

3. RViz를 `use_sim_time`으로 실행한다.

```bash
rviz2 --ros-args -p use_sim_time:=true
```

## 3. Message Filter dropping message

### 증상

```text
Message Filter dropping message: frame 'map' at time 22.400
reason 'the timestamp on the message is earlier than all the data in the transform cache'
```

### 원인

`/map` 메시지는 Gazebo sim time 기준인데, TF cache에는 wall time 또는 다른 시간축의 transform이 섞여 있었다.

### 해결

기존 노드를 정리한다.

```bash
pkill -f rviz2
pkill -f map_server
pkill -f lifecycle_manager
pkill -f amcl
pkill -f static_transform_publisher
```

다시 실행할 때는 관련 노드에 `use_sim_time:=true`를 준다.

```bash
rviz2 --ros-args -p use_sim_time:=true
```

## 4. `/initialpose`가 AMCL에서 무시됨

### 증상

```text
initialPoseReceived
Ignoring initial pose in frame "odom"; initial poses must be in the global frame, "map"
```

### 원인

RViz에서 `2D Pose Estimate`를 눌렀지만 `/initialpose` 메시지가 `odom` 프레임으로 발행되었다.

AMCL은 초기 위치를 `map` 프레임 기준으로 받아야 한다.

### 해결

RViz에서:

```text
Global Options -> Fixed Frame = map
```

또는 명령어로 직접 `frame_id: map`을 지정한다.

```bash
ros2 topic pub --once /initialpose geometry_msgs/msg/PoseWithCovarianceStamped \
"{header: {frame_id: 'map'}, pose: {pose: {position: {x: 0.0, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}}"
```

## 5. `Frame [map] does not exist`

### 증상

RViz에서:

```text
Global Status: Error
Fixed Frame: Frame [map] does not exist
```

### 원인

static TF를 사용하지 않는 AMCL 방식에서는 초기 위치를 넣기 전까지 AMCL이 `map -> odom`을 발행하지 않는다.

따라서 처음에는 RViz가 `map` 프레임을 못 찾을 수 있다.

### 해결

AMCL이 active 상태인지 확인한 뒤 초기 위치를 넣는다.

```bash
ros2 lifecycle get /amcl
```

초기 위치:

```bash
ros2 topic pub --once /initialpose geometry_msgs/msg/PoseWithCovarianceStamped \
"{header: {frame_id: 'map'}, pose: {pose: {position: {x: 0.0, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}}"
```

그 다음 확인:

```bash
ros2 run tf2_ros tf2_echo map odom
```

## 6. 긴 `/initialpose` 명령이 불편함

### 원인

`PoseWithCovarianceStamped`의 covariance는 36개 값을 가지므로 전체를 직접 쓰면 명령이 길어진다.

### 해결

테스트용 초기 위치는 covariance를 생략한 짧은 형태로 발행할 수 있다.

```bash
ros2 topic pub --once /initialpose geometry_msgs/msg/PoseWithCovarianceStamped \
"{header: {frame_id: 'map'}, pose: {pose: {position: {x: 0.0, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}}"
```

필요하면 이 명령을 `~/envs/tb3_humble.bash`에 함수로 등록한다.


## 7. Explore Lite 관련 문제

### 7.1 `explore_lite`가 움직이지 않음

확인할 것:

```bash
ros2 action list | grep navigate
```

`/navigate_to_pose`가 없으면 Nav2 navigation stack이 제대로 뜨지 않은 것이다.

```bash
ros2 topic list | grep map
```

`/map`이 없으면 slam_toolbox가 지도를 발행하지 못하는 상태다.

```bash
ros2 run tf2_ros tf2_echo map odom
```

`map -> odom`이 없으면 SLAM과 TF가 연결되지 않은 상태다.

### 7.2 frontier가 보이지 않음

RViz에서 다음 토픽을 추가한다.

```text
/explore/frontiers
```

Marker 또는 MarkerArray 타입으로 추가해서 확인한다.

### 7.3 AMCL과 함께 실행해서 꼬임

Explore Lite 자동 탐색 흐름에서는 AMCL을 실행하지 않는다.

```text
slam_toolbox가 SLAM과 map -> odom을 담당
explore_lite가 frontier 목표 생성
Nav2가 이동 수행
```

따라서 기존 AMCL 실습 노드가 남아 있으면 먼저 종료한다.

```bash
pkill -f amcl
pkill -f map_server
pkill -f lifecycle_manager
```

### 7.4 시간이 꼬이는 문제

Gazebo, slam_toolbox, Nav2, RViz, explore_lite 모두 시뮬레이션 시간을 사용해야 한다.

```bash
use_sim_time:=True
```

또는:

```bash
--ros-args -p use_sim_time:=true
```
