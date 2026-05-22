# 07. 내 환경 기준 실행 메모

이 문서는 현재 내 실습 환경에서 바로 확인하기 위한 메모다.  
일반 설명보다 “내 컴퓨터에서 어떤 경로, 어떤 명령, 어떤 토픽을 기준으로 봐야 하는가”에 초점을 둔다.

---

## 1. 현재 기준 경로

```text
워크스페이스:
$ROS2_WS

패키지:
$ROS2_WS/lee_robot_description

SLAM launch:
$ROS2_WS/lee_robot_description/launch/slam.launch.py

SLAM parameter:
$ROS2_WS/lee_robot_description/config/slam_param.yaml

RViz config:
$ROS2_WS/lee_robot_description/rviz/slam.rviz

SLAM용 bag:
$ROS2_WS/bags/slam_raw_01

저장 지도:
$ROS2_WS/slam_map.yaml
$ROS2_WS/slam_map.pgm
```

---

## 2. 모든 터미널 공통 준비

새 터미널을 열 때마다 다음을 먼저 실행한다.

```bash
cd $ROS2_WS
source /opt/ros/humble/setup.bash
source install/setup.bash
```

패키지 인식 확인:

```bash
ros2 pkg prefix lee_robot_description
```

정상이라면 install 경로가 나온다.

---

## 3. 수정 후 빌드 기준

아래 파일을 바꿨다면 다시 빌드해야 한다.

```text
lee_robot_description/launch/*
lee_robot_description/config/*
lee_robot_description/urdf/*
lee_robot_description/rviz/*
lee_robot_description/worlds/*
lee_robot_description/CMakeLists.txt
lee_robot_description/package.xml
```

명령:

```bash
cd $ROS2_WS
colcon build --packages-select lee_robot_description
source install/setup.bash
```

world 파일이 install 경로에 들어갔는지 확인:

```bash
ls $(ros2 pkg prefix lee_robot_description)/share/lee_robot_description/worlds
```

---

## 4. 내 환경 기준 live SLAM 실행

터미널 1:

```bash
cd $ROS2_WS
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 launch lee_robot_description slam.launch.py world:=slam.world
```

터미널 2:

```bash
cd $ROS2_WS
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 run teleop_twist_keyboard teleop_twist_keyboard \
  --ros-args \
  -r __node:=lee_teleop \
  -r cmd_vel:=/robot_ns/cmd_vel
```

RViz2 확인:

```text
Fixed Frame: map_robot_ns
Map Topic: /robot_ns/map
LaserScan Topic: /robot_ns/scan
```

---

## 5. 내 환경 기준 빠른 점검 명령

```bash
ros2 topic list | sort
```

기대 토픽:

```text
/robot_ns/scan
/robot_ns/odom
/robot_ns/map
/robot_ns/tf
/robot_ns/tf_static
/robot_ns/cmd_vel
/robot_ns/robot_description
/clock
```

각 토픽 1회 확인:

```bash
ros2 topic echo /robot_ns/scan --once
ros2 topic echo /robot_ns/odom --once
ros2 topic echo /robot_ns/map --once
```

TF 확인:

```bash
ros2 run tf2_ros tf2_echo map_robot_ns base_footprint \
  --ros-args \
  -r /tf:=/robot_ns/tf \
  -r /tf_static:=/robot_ns/tf_static
```

---

## 6. 내 환경 기준 지도 저장

workspace root에 저장:

```bash
cd $ROS2_WS
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 run nav2_map_server map_saver_cli \
  -t /robot_ns/map \
  -f ./slam_map
```

`maps/` 폴더에 저장:

```bash
cd $ROS2_WS
mkdir -p maps

ros2 run nav2_map_server map_saver_cli \
  -t /robot_ns/map \
  -f ./maps/slam_map
```

확인:

```bash
ls -lh slam_map.yaml slam_map.pgm
cat slam_map.yaml
```

---

## 7. 내 환경 기준 offline SLAM

현재 추천 bag:

```text
bags/slam_raw_01
```

터미널 1. SLAM Toolbox:

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

터미널 2. RViz2:

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

터미널 3. bag play:

```bash
cd $ROS2_WS
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 bag play bags/slam_raw_01 --clock --rate 0.5
```

---

## 8. 이전 namespace 없는 bag을 쓸 때

이전 bag:

```text
rosbag2_2026_05_13-16_27_44
```

토픽 구조:

```text
/scan
/odom
/tf
/tf_static
```

현재 문서 기준 구조:

```text
/robot_ns/scan
/robot_ns/odom
/robot_ns/tf
/robot_ns/tf_static
```

재생 시 remap:

```bash
ros2 bag play rosbag2_2026_05_13-16_27_44 --clock --rate 0.5 \
  --remap /scan:=/robot_ns/scan \
  --remap /odom:=/robot_ns/odom \
  --remap /tf:=/robot_ns/tf \
  --remap /tf_static:=/robot_ns/tf_static
```

단, 이건 topic 이름만 바꾸는 것이다.  
`header.frame_id`, `child_frame_id`는 바뀌지 않는다.

확인:

```bash
ros2 topic echo /robot_ns/scan --once
ros2 topic echo /robot_ns/odom --once
```

---

## 9. 내 환경에서 특히 조심할 것

```text
1. source install/setup.bash 누락
2. world 파일 수정 후 colcon build 누락
3. /map과 /robot_ns/map 혼동
4. /tf와 /robot_ns/tf 혼동
5. bag play --clock 누락
6. Gazebo와 bag play 동시 실행
7. teleop remap 누락: cmd_vel:=/robot_ns/cmd_vel
8. RViz2 Fixed Frame을 map으로 두는 실수. 현재는 map_robot_ns
9. map_saver_cli에서 -t /robot_ns/map 누락
10. namespace 없는 bag을 /robot_ns 구조에 그대로 넣으려는 실수
```

---

## 10. 지금 단계에서 코드 수정은 하지 않는다

현재 목표는 코드 변경이 아니다.

```text
지금 할 일:
  실행 흐름 이해
  명령어 정리
  frame/topic 관계 이해
  산출물 의미 정리
  문제 상황 기록

나중에 할 일:
  패키지 위치 정리
  map 파일을 package share 아래로 이동
  launch 구조 정리
  README/프로젝트화
```
