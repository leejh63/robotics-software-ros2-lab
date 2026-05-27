# 06. rosbag Offline SLAM

## 1. offline SLAM이란?

offline SLAM은 실시간 Gazebo를 켜서 센서를 새로 만드는 것이 아니라, 이미 녹화해둔 bag 데이터를 재생해서 SLAM을 다시 수행하는 방식이다.

```text
실시간 SLAM
  Gazebo가 지금 /lee/scan, /lee/odom, /lee/tf를 생성
  SLAM Toolbox가 실시간으로 처리

offline SLAM
  rosbag이 예전에 저장한 /lee/scan, /lee/odom, /lee/tf를 재생
  SLAM Toolbox가 같은 데이터를 다시 처리
```

장점:

```text
같은 입력으로 반복 실험 가능
SLAM parameter 변경 후 결과 비교 가능
실시간 조작 실수 영향을 줄일 수 있음
```

---

## 2. rosbag 데이터 포함 여부와 입력 전제

이 저장소에는 rosbag 원본 데이터를 포함하지 않는다. rosbag은 용량이 크고 실행 환경마다 다르므로 Git에 올리지 않고, 사용자가 직접 준비한 bag 디렉토리를 `$BAG_DIR`로 지정해서 사용한다.

```bash
export BAG_DIR=/path/to/rosbag_directory
ros2 bag info "$BAG_DIR"
```

이 문서에서 전제하는 최소 topic은 다음과 같다.

```text
/scan 또는 /lee/scan
/odom 또는 /lee/odom
/tf 또는 /lee/tf
/tf_static 또는 /lee/tf_static
```

특히 namespace 없는 bag을 `/lee` 구조에 맞출 때는 `ros2 bag play`의 topic remap을 사용한다. 단, topic remap은 message 내부의 `header.frame_id`, `child_frame_id`를 바꾸지 않는다. 따라서 `ros2 bag info`, `ros2 topic echo`, `tf2_echo`로 실제 frame 이름을 확인해야 한다.

---

## 3. offline SLAM 전 정리

Gazebo와 RViz2가 이미 떠 있으면 topic이 섞일 수 있다.

```bash
pkill -f gzserver
pkill -f gzclient
pkill -f gazebo
pkill -f rviz2
```

이유:

```text
Gazebo도 /clock, /lee/scan, /lee/tf를 발행할 수 있다.
bag play도 /clock, /lee/scan, /lee/tf를 재생할 수 있다.
둘이 동시에 발행하면 SLAM 입력이 섞인다.
```

---

## 4. `/lee` namespace bag으로 offline SLAM

### 터미널 1. SLAM Toolbox 실행

```bash
cd $ROS2_WS
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 run slam_toolbox async_slam_toolbox_node \
  --ros-args \
  -r __node:=slam_toolbox \
  --params-file $PWD/lee_robot_description/config/slam_param.yaml \
  -p use_sim_time:=true \
  -r /map:=/lee/map \
  -r /map_updates:=/lee/map_updates \
  -r /tf:=/lee/tf \
  -r /tf_static:=/lee/tf_static
```

참고:

```text
slam_param.yaml 안에 scan_topic: /lee/scan 이 있으므로 현재 bag 기준에서는 scan remap이 필수는 아니다.
```

---

### 터미널 2. RViz2 실행

```bash
cd $ROS2_WS
source /opt/ros/humble/setup.bash
source install/setup.bash

rviz2 -d $(ros2 pkg prefix lee_robot_description)/share/lee_robot_description/rviz/slam.rviz \
  --ros-args \
  -p use_sim_time:=true \
  -r /tf:=/lee/tf \
  -r /tf_static:=/lee/tf_static
```

RViz2 확인값:

```text
Fixed Frame = map_lee
Map Topic = /lee/map
LaserScan Topic = /lee/scan
```

---

### 터미널 3. bag 재생

```bash
cd $ROS2_WS
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 bag play "$BAG_DIR" --clock
```

천천히 재생:

```bash
ros2 bag play "$BAG_DIR" --clock --rate 0.5
```

반복 재생:

```bash
ros2 bag play "$BAG_DIR" --clock --loop
```

---

## 5. namespace 없는 bag을 현재 `/lee` 구조에 맞추는 방법

이전 bag은 토픽이 다음과 같다.

```text
/scan
/odom
/tf
/tf_static
```

현재 SLAM 설정은 다음을 기대한다.

```text
/lee/scan
/lee/tf
/lee/tf_static
```

그래서 bag 재생 시 topic remap을 할 수 있다.

```bash
cd $ROS2_WS
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 bag play "$BAG_DIR" --clock \
  --remap /scan:=/lee/scan \
  --remap /tf:=/lee/tf \
  --remap /tf_static:=/lee/tf_static \
  --remap /odom:=/lee/odom
```

중요한 주의:

```text
토픽 remap은 topic 이름만 바꾼다.
메시지 안의 header.frame_id나 child_frame_id를 자동으로 바꾸지 않는다.
```

즉, `/scan`을 `/lee/scan`으로 바꿔도 scan 메시지 안의 `header.frame_id`가 `base_scan`인지, `laser`인지, 다른 이름인지는 따로 확인해야 한다.

확인:

```bash
ros2 topic echo /lee/scan --once
ros2 topic echo /lee/odom --once
```

`header.frame_id`, `child_frame_id`가 현재 `slam_param.yaml`의 frame 설정과 맞아야 한다.

---

## 6. offline SLAM 결과 확인

```bash
ros2 topic echo /lee/map --once
ros2 topic hz /lee/map
ros2 node info /slam_toolbox
```

TF 확인:

```bash
ros2 run tf2_ros tf2_echo map_lee base_footprint \
  --ros-args \
  -r /tf:=/lee/tf \
  -r /tf_static:=/lee/tf_static
```

지도 저장:

```bash
ros2 run nav2_map_server map_saver_cli \
  -t /lee/map \
  -f ./offline_slam_map
```

---

## 7. offline SLAM에서 자주 생기는 문제

### 7.1 `/clock` 문제

SLAM Toolbox와 RViz2가 `use_sim_time:=true`인데 bag을 `--clock` 없이 재생하면 시간이 흐르지 않는 것처럼 보일 수 있다.

현재 권장:

```bash
ros2 bag play "$BAG_DIR" --clock
```

---

### 7.2 QoS 문제

일부 sensor topic은 QoS가 맞지 않으면 RViz2나 노드가 메시지를 못 받을 수 있다.
특히 LaserScan은 best effort/reliable 차이로 문제가 생길 수 있다.

확인:

```bash
ros2 topic info /lee/scan -v
```

---

### 7.3 frame 이름 문제

토픽 remap으로는 frame 이름이 바뀌지 않는다.

예:

```text
bag topic name: /scan
remap result: /lee/scan
message header.frame_id: laser
```

이 경우 SLAM 설정이 `base_scan`을 기대한다면 TF가 연결되지 않을 수 있다.

---

## 8. offline SLAM의 결론

```text
offline SLAM은 같은 센서 데이터를 반복 재생해 SLAM을 다시 확인하는 방법이다.
실제 bag 구조는 `ros2 bag info "$BAG_DIR"`로 확인한다.
이전 namespace 없는 bag은 topic remap이 필요할 수 있다.
단, topic remap은 frame_id를 바꾸지 않는다.
use_sim_time=true라면 bag play --clock을 같이 써야 한다.
```
