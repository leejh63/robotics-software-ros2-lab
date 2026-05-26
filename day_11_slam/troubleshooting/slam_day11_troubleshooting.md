# SLAM Day 11 트러블슈팅

Day 11 SLAM 실습 중 자주 생기는 문제를 원인 중심으로 정리한다.

## 빠른 진단표

| 증상 | 먼저 확인할 것 | 확인 명령 | 가능성이 큰 원인 |
|---|---|---|---|
| package를 못 찾음 | build/source | `ros2 pkg list \| grep lee_robot_description` | `source install/setup.bash` 누락 또는 빌드 실패 |
| `/robot_ns/map`이 안 나옴 | scan, odom, TF | `ros2 topic echo /robot_ns/scan --once` | SLAM Toolbox 입력 데이터 부족 |
| RViz에서 map만 안 보임 | CLI map 발행 여부 | `ros2 topic echo /robot_ns/map --once` | RViz Fixed Frame/QoS/display topic 설정 |
| TF 오류 발생 | frame chain | `ros2 run tf2_ros tf2_echo odom_robot_ns base_footprint` | URDF, odom frame, scan frame 불일치 |
| rosbag offline SLAM 실패 | topic remap과 frame_id | `ros2 topic echo /robot_ns/scan --once \| grep frame_id` | remap은 topic만 바꾸고 frame_id는 그대로 남음 |

자세한 공통 진단 순서는 `appendix/troubleshooting_quick_diagnosis.md`와 `appendix/ros2_navigation_debug_order.md`를 기준으로 본다.

---


## 1. `Package 'lee_robot_description' not found`

원인:

```text
install/setup.bash를 source하지 않았다.
또는 colcon build가 안 되어 있다.
```

해결:

```bash
cd $ROS2_WS
source /opt/ros/humble/setup.bash
colcon build --packages-select lee_robot_description
source install/setup.bash
```

---

## 2. world 파일을 못 찾음

원인:

```text
worlds/에 파일을 추가했지만 install/share로 복사되지 않았다.
```

해결:

```bash
cd $ROS2_WS
colcon build --packages-select lee_robot_description
source install/setup.bash
ls $(ros2 pkg prefix lee_robot_description)/share/lee_robot_description/worlds
```

---

## 3. `/robot_ns/map`이 안 나옴

확인 순서:

```bash
ros2 topic echo /robot_ns/scan --once
ros2 topic echo /robot_ns/odom --once
ros2 topic list | grep tf
ros2 node info /slam_toolbox
```

가능한 원인:

```text
/robot_ns/scan이 안 나옴
TF remap이 안 맞음
slam_param.yaml의 frame 이름이 실제와 다름
use_sim_time과 /clock이 안 맞음
SLAM Toolbox가 scan topic을 다르게 보고 있음
```

현재 기준 핵심값:

```text
scan_topic: /robot_ns/scan
map_frame: map_robot_ns
odom_frame: odom_robot_ns
base_frame: base_footprint
```

---

## 4. RViz2에서 지도만 안 보임

확인:

```text
Fixed Frame = map_robot_ns
Map Topic = /robot_ns/map
Map Durability = Transient Local
LaserScan Topic = /robot_ns/scan
```

토픽 확인:

```bash
ros2 topic echo /robot_ns/map --once
```

---

## 5. TF 오류

증상:

```text
No transform from [base_scan] to [map_robot_ns]
No transform from [base_footprint] to [map_robot_ns]
```

확인:

```bash
ros2 run tf2_ros tf2_echo odom_robot_ns base_footprint \
  --ros-args \
  -r /tf:=/robot_ns/tf \
  -r /tf_static:=/robot_ns/tf_static
```

```bash
ros2 run tf2_ros tf2_echo base_link base_scan \
  --ros-args \
  -r /tf:=/robot_ns/tf \
  -r /tf_static:=/robot_ns/tf_static
```

SLAM 후 확인:

```bash
ros2 run tf2_ros tf2_echo map_robot_ns base_footprint \
  --ros-args \
  -r /tf:=/robot_ns/tf \
  -r /tf_static:=/robot_ns/tf_static
```

---

## 6. map_saver_cli 실패

### 6.1 `/map`을 기다리는 문제

문제 명령:

```bash
ros2 run nav2_map_server map_saver_cli -f ./slam_map
```

현재 환경에서는 `/robot_ns/map`을 써야 한다.

해결:

```bash
ros2 run nav2_map_server map_saver_cli \
  -t /robot_ns/map \
  -f ./slam_map
```

### 6.2 저장 폴더가 없는 문제

에러 예:

```text
Unable to open file ./maps/slam_map.pgm
```

해결:

```bash
mkdir -p maps
ros2 run nav2_map_server map_saver_cli \
  -t /robot_ns/map \
  -f ./maps/slam_map
```

---

## 7. teleop이 안 먹음

확인:

```text
teleop 터미널에 키보드 포커스가 있는가?
cmd_vel remap이 /robot_ns/cmd_vel인가?
Gazebo 로봇이 spawn되어 있는가?
```

정상 명령:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard \
  --ros-args \
  -r __node:=lee_teleop \
  -r cmd_vel:=/robot_ns/cmd_vel
```

---

## 8. `Entity [turtlebot] already exists`

원인:

```text
이전 Gazebo에 같은 entity가 남아 있다.
```

해결:

```bash
pkill -f gzserver
pkill -f gzclient
pkill -f gazebo
```

그 후 다시 launch한다.

---

## 9. offline SLAM에서 아무것도 안 나옴

확인:

```bash
ros2 topic list
ros2 topic echo /clock --once
ros2 topic echo /robot_ns/scan --once
ros2 topic echo /robot_ns/tf --once
```

가능한 원인:

```text
bag play에 --clock을 안 붙임
bag 내부 topic이 /robot_ns/scan이 아니라 /scan임
SLAM Toolbox가 /robot_ns/tf를 보는데 bag은 /tf를 발행함
frame_id가 현재 설정과 다름
Gazebo가 동시에 켜져 입력이 섞임
```

해결 후보:

```bash
ros2 bag play bags/slam_raw_01 --clock --rate 0.5
```

또는 namespace 없는 bag이면:

```bash
ros2 bag play rosbag2_2026_05_13-16_27_44 --clock --rate 0.5 \
  --remap /scan:=/robot_ns/scan \
  --remap /odom:=/robot_ns/odom \
  --remap /tf:=/robot_ns/tf \
  --remap /tf_static:=/robot_ns/tf_static
```

---

## 10. RViz2에서 LaserScan만 안 보임

확인:

```text
LaserScan Topic = /robot_ns/scan
Fixed Frame = map_robot_ns 또는 base_scan과 연결 가능한 frame
QoS 설정 확인
```

명령:

```bash
ros2 topic info /robot_ns/scan -v
```

필요하면 RViz2 LaserScan display의 Reliability를 Best Effort로 바꿔본다.

---

## 11. SLAM과 AMCL을 동시에 켠 경우

증상:

```text
TF가 흔들림
지도/로봇 위치가 이상하게 보임
map_robot_ns -> odom_robot_ns가 여러 곳에서 발행됨
```

원인:

```text
SLAM Toolbox와 AMCL이 모두 map_robot_ns -> odom_robot_ns를 발행할 수 있음
```

원칙:

```text
지도 생성할 때: SLAM Toolbox
저장 지도 위 위치 추정할 때: AMCL
둘을 동시에 같은 frame 구조로 켜지 않는다.
```
