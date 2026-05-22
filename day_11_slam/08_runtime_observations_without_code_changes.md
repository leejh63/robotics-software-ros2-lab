# 08. Runtime Observations Without Code Changes

이 문서는 Day 11 SLAM 실습에서 실행 중 문제가 될 수 있는 부분을 기록한다.  
현재 단계에서는 코드를 고치지 않고, “왜 문제가 생길 수 있는지”와 “어떻게 확인할지”만 정리한다.

---

## 1. `/map`과 `/robot_ns/map` 혼동

현재 SLAM 결과는 `/robot_ns/map`이다.

```text
SLAM Toolbox output: /robot_ns/map
map_saver_cli 기본값: /map
RViz2에서 볼 topic: /robot_ns/map
```

증상:

```text
map_saver_cli가 지도를 못 받음
RViz2에서 지도 안 보임
ros2 topic echo /map은 안 나오는데 /robot_ns/map은 나옴
```

확인:

```bash
ros2 topic list | grep map
ros2 topic echo /robot_ns/map --once
```

---

## 2. `/tf`와 `/robot_ns/tf` 혼동

현재 launch는 TF도 `/robot_ns/tf`, `/robot_ns/tf_static`으로 remap한다.

증상:

```text
tf2_echo가 transform을 못 찾음
RViz2에서 Fixed Frame 오류
SLAM Toolbox가 scan frame을 map/odom/base와 연결하지 못함
```

확인:

```bash
ros2 topic list | grep tf
ros2 run tf2_ros tf2_echo map_robot_ns base_footprint \
  --ros-args \
  -r /tf:=/robot_ns/tf \
  -r /tf_static:=/robot_ns/tf_static
```

---

## 3. topic remap은 frame_id를 바꾸지 않는다

이전 bag을 재생할 때 `/scan:=/robot_ns/scan`으로 remap할 수 있다.

하지만 이것은 topic 이름만 바꾼다.

```text
바뀌는 것:
  /scan -> /robot_ns/scan

자동으로 안 바뀌는 것:
  msg.header.frame_id
  odom child_frame_id
  TF message 안의 frame_id/child_frame_id
```

따라서 namespace 없는 bag을 현재 설정에 맞출 때는 frame 이름도 확인해야 한다.

확인:

```bash
ros2 topic echo /robot_ns/scan --once
ros2 topic echo /robot_ns/odom --once
```

---

## 4. Gazebo와 bag play 동시 실행 주의

offline SLAM을 할 때 Gazebo가 켜져 있으면 입력이 섞일 수 있다.

문제:

```text
Gazebo도 /clock 발행
bag play도 --clock으로 /clock 발행
Gazebo도 /robot_ns/scan 발행
bag play도 /robot_ns/scan 재생
TF도 여러 소스에서 발행될 수 있음
```

권장:

```bash
pkill -f gzserver
pkill -f gzclient
pkill -f gazebo
pkill -f rviz2
```

---

## 5. `use_sim_time`과 `--clock` 짝 맞추기

SLAM Toolbox와 RViz2가 `use_sim_time:=true`라면 시간이 `/clock`에서 와야 한다.

live Gazebo:

```text
Gazebo가 /clock 발행
```

offline bag:

```bash
ros2 bag play bags/slam_raw_01 --clock
```

`--clock`이 없으면 시간이 안 흐르는 것처럼 보일 수 있다.

---

## 6. map_robot_ns -> odom_robot_ns 발행 주체 중복 주의

SLAM 중에는 SLAM Toolbox가 `map_robot_ns -> odom_robot_ns`를 발행한다.

AMCL 중에는 AMCL이 `map_robot_ns -> odom_robot_ns`를 발행한다.

확인 과정에서는 static_transform_publisher가 발행할 수 있다.

동시에 켜면 안 좋은 조합:

```text
SLAM Toolbox + AMCL
SLAM Toolbox + static map_robot_ns -> odom_robot_ns
AMCL + static map_robot_ns -> odom_robot_ns
```

같은 parent-child transform을 여러 노드가 동시에 발행하면 TF가 불안정해질 수 있다.

---

## 7. world 파일 수정 후 build 누락

`worlds/slam.world`를 추가하거나 수정했는데 launch에서 예전 world가 뜨는 경우가 있다.

원인:

```text
ros2 launch는 install/share의 파일을 참조한다.
source 폴더만 바꾸고 colcon build를 하지 않으면 install 경로가 갱신되지 않는다.
```

해결:

```bash
cd $ROS2_WS
colcon build --packages-select lee_robot_description
source install/setup.bash
```

확인:

```bash
ls $(ros2 pkg prefix lee_robot_description)/share/lee_robot_description/worlds
```

---

## 8. map 저장 폴더 없음

증상:

```text
Failed to write map
Unable to open file ./maps/slam_map.pgm
```

원인:

```text
./maps 폴더가 없음
```

해결:

```bash
mkdir -p maps
ros2 run nav2_map_server map_saver_cli \
  -t /robot_ns/map \
  -f ./maps/slam_map
```

---

## 9. RViz2 Fixed Frame 설정 실수

현재 기준 Fixed Frame은 `map_robot_ns`다.

문제 설정:

```text
Fixed Frame = map
Map Topic = /map
```

현재 권장:

```text
Fixed Frame = map_robot_ns
Map Topic = /robot_ns/map
LaserScan Topic = /robot_ns/scan
```

---

## 10. 현재 단계에서 남겨둘 코드 구조상 관찰

현재 학습 문서 단계에서는 다음을 코드 수정 대상으로 바로 처리하지 않는다.

```text
lee_robot_description 패키지가 ws/src가 아니라 ws 루트에 있음
map 파일이 package share의 maps/가 아니라 workspace root에 있음
일부 launch는 확인용/실습용 성격이 섞여 있음
robot_ns namespace와 frame 이름이 학습 도중 여러 단계에서 바뀐 흔적이 있음
```

이 내용은 이후 2주 프로젝트나 포트폴리오용 repo를 만들 때 정리하면 된다.  
지금은 “왜 이렇게 동작하는지”를 이해하는 것이 우선이다.
