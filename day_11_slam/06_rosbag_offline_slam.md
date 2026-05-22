# 06. rosbag Offline SLAM

## 1. offline SLAM이란?

offline SLAM은 실시간 Gazebo를 켜서 센서를 새로 만드는 것이 아니라, 이미 녹화해둔 bag 데이터를 재생해서 SLAM을 다시 수행하는 방식이다.

```text
실시간 SLAM
  Gazebo가 지금 /robot_ns/scan, /robot_ns/odom, /robot_ns/tf를 생성
  SLAM Toolbox가 실시간으로 처리

offline SLAM
  rosbag이 예전에 저장한 /robot_ns/scan, /robot_ns/odom, /robot_ns/tf를 재생
  SLAM Toolbox가 같은 데이터를 다시 처리
```

장점:

```text
같은 입력으로 반복 실험 가능
SLAM parameter 변경 후 결과 비교 가능
실시간 조작 실수 영향을 줄일 수 있음
```

---

## 2. 현재 사용할 수 있는 bag 구분

### 2.1 현재 SLAM용 bag

```text
$ROS2_WS/bags/slam_raw_01
```

metadata 기준:

```text
Duration: 약 90.3초
Messages: 11700
Topics:
  /robot_ns/tf_static
  /robot_ns/scan
  /robot_ns/tf
  /robot_ns/odom
```

이 bag은 현재 `slam_param.yaml`의 `/robot_ns/scan`, `map_robot_ns`, `odom_robot_ns`, `base_footprint` 구조와 맞는 편이다.

### 2.2 이전 Day 9 계열 bag

```text
$ROS2_WS/rosbag2_2026_05_13-16_27_44
```

metadata 기준:

```text
Duration: 약 52.0초
Messages: 5323
Topics:
  /scan
  /odom
  /tf
  /tf_static
  /imu
  /cmd_vel
  /image_raw/compressed
```

이 bag은 `/robot_ns` namespace가 없다.  
현재 SLAM 설정과 맞추려면 remap을 고려해야 한다.

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
Gazebo도 /clock, /robot_ns/scan, /robot_ns/tf를 발행할 수 있다.
bag play도 /clock, /robot_ns/scan, /robot_ns/tf를 재생할 수 있다.
둘이 동시에 발행하면 SLAM 입력이 섞인다.
```

---

## 4. `/robot_ns` namespace bag으로 offline SLAM

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
  -r /map:=/robot_ns/map \
  -r /map_updates:=/robot_ns/map_updates \
  -r /tf:=/robot_ns/tf \
  -r /tf_static:=/robot_ns/tf_static
```

참고:

```text
slam_param.yaml 안에 scan_topic: /robot_ns/scan 이 있으므로 현재 bag 기준에서는 scan remap이 필수는 아니다.
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
  -r /tf:=/robot_ns/tf \
  -r /tf_static:=/robot_ns/tf_static
```

RViz2 확인값:

```text
Fixed Frame = map_robot_ns
Map Topic = /robot_ns/map
LaserScan Topic = /robot_ns/scan
```

---

### 터미널 3. bag 재생

```bash
cd $ROS2_WS
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 bag play bags/slam_raw_01 --clock
```

천천히 재생:

```bash
ros2 bag play bags/slam_raw_01 --clock --rate 0.5
```

반복 재생:

```bash
ros2 bag play bags/slam_raw_01 --clock --loop
```

---

## 5. namespace 없는 bag을 현재 `/robot_ns` 구조에 맞추는 방법

이전 bag은 토픽이 다음과 같다.

```text
/scan
/odom
/tf
/tf_static
```

현재 SLAM 설정은 다음을 기대한다.

```text
/robot_ns/scan
/robot_ns/tf
/robot_ns/tf_static
```

그래서 bag 재생 시 topic remap을 할 수 있다.

```bash
cd $ROS2_WS
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 bag play rosbag2_2026_05_13-16_27_44 --clock \
  --remap /scan:=/robot_ns/scan \
  --remap /tf:=/robot_ns/tf \
  --remap /tf_static:=/robot_ns/tf_static \
  --remap /odom:=/robot_ns/odom
```

중요한 주의:

```text
토픽 remap은 topic 이름만 바꾼다.
메시지 안의 header.frame_id나 child_frame_id를 자동으로 바꾸지 않는다.
```

즉, `/scan`을 `/robot_ns/scan`으로 바꿔도 scan 메시지 안의 `header.frame_id`가 `base_scan`인지, `laser`인지, 다른 이름인지는 따로 확인해야 한다.

확인:

```bash
ros2 topic echo /robot_ns/scan --once
ros2 topic echo /robot_ns/odom --once
```

`header.frame_id`, `child_frame_id`가 현재 `slam_param.yaml`의 frame 설정과 맞아야 한다.

---

## 6. offline SLAM 결과 확인

```bash
ros2 topic echo /robot_ns/map --once
ros2 topic hz /robot_ns/map
ros2 node info /slam_toolbox
```

TF 확인:

```bash
ros2 run tf2_ros tf2_echo map_robot_ns base_footprint \
  --ros-args \
  -r /tf:=/robot_ns/tf \
  -r /tf_static:=/robot_ns/tf_static
```

지도 저장:

```bash
ros2 run nav2_map_server map_saver_cli \
  -t /robot_ns/map \
  -f ./offline_slam_map
```

---

## 7. offline SLAM에서 자주 생기는 문제

### 7.1 `/clock` 문제

SLAM Toolbox와 RViz2가 `use_sim_time:=true`인데 bag을 `--clock` 없이 재생하면 시간이 흐르지 않는 것처럼 보일 수 있다.

현재 권장:

```bash
ros2 bag play bags/slam_raw_01 --clock
```

---

### 7.2 QoS 문제

일부 sensor topic은 QoS가 맞지 않으면 RViz2나 노드가 메시지를 못 받을 수 있다.  
특히 LaserScan은 best effort/reliable 차이로 문제가 생길 수 있다.

확인:

```bash
ros2 topic info /robot_ns/scan -v
```

---

### 7.3 frame 이름 문제

토픽 remap으로는 frame 이름이 바뀌지 않는다.

예:

```text
bag topic name: /scan
remap result: /robot_ns/scan
message header.frame_id: laser
```

이 경우 SLAM 설정이 `base_scan`을 기대한다면 TF가 연결되지 않을 수 있다.

---

## 8. offline SLAM의 결론

```text
offline SLAM은 같은 센서 데이터를 반복 재생해 SLAM을 다시 확인하는 방법이다.
현재 bags/slam_raw_01은 robot_ns namespace와 잘 맞는다.
이전 namespace 없는 bag은 topic remap이 필요할 수 있다.
단, topic remap은 frame_id를 바꾸지 않는다.
use_sim_time=true라면 bag play --clock을 같이 써야 한다.
```
