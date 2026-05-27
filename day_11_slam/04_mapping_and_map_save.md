# 04. Gazebo Live SLAM과 지도 저장

## 1. live SLAM 기본 실행

터미널 1에서 실행한다.

```bash
cd $ROS2_WS
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 launch lee_robot_description slam.launch.py world:=slam.world
```

이 명령으로 실행되는 것:

```text
Gazebo
robot_state_publisher
spawn_entity.py
slam_toolbox
RViz2
```

---

## 2. teleop으로 로봇 움직이기

터미널 2에서 실행한다.

```bash
cd $ROS2_WS
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 run teleop_twist_keyboard teleop_twist_keyboard \
  --ros-args \
  -r __node:=lee_teleop \
  -r cmd_vel:=/lee/cmd_vel
```

주의:

```text
키 입력은 Gazebo 창이 아니라 teleop 터미널에 포커스가 있어야 한다.
로봇을 너무 빠르게 움직이면 scan matching 품질이 떨어질 수 있다.
벽을 따라 천천히 움직이고, 이미 지나간 곳으로 다시 돌아오면 loop closure 확인에 좋다.
```

---

## 3. RViz2에서 확인할 것

`slam.rviz` 기준 확인값:

```text
Fixed Frame = map_lee
Map Topic = /lee/map
LaserScan Topic = /lee/scan
RobotModel Description Topic = /lee/robot_description
TF Topic = /lee/tf, /lee/tf_static remap 기준
```

정상 상태:

```text
로봇 모델이 보인다.
로봇 주변 LaserScan 점이 보인다.
로봇이 움직이면 /lee/map의 흰색/검은색 영역이 늘어난다.
TF tree가 map_lee -> odom_lee -> base_footprint로 이어진다.
```

---

## 4. 상태 확인 명령

토픽 목록:

```bash
ros2 topic list
```

핵심 토픽 확인:

```bash
ros2 topic echo /lee/scan --once
ros2 topic echo /lee/odom --once
ros2 topic echo /lee/map --once
```

주기 확인:

```bash
ros2 topic hz /lee/scan
ros2 topic hz /lee/map
```

노드 확인:

```bash
ros2 node list
ros2 node info /slam_toolbox
```

TF 확인:

```bash
ros2 run tf2_ros tf2_echo map_lee base_footprint \
  --ros-args \
  -r /tf:=/lee/tf \
  -r /tf_static:=/lee/tf_static
```

---

## 5. 좋은 지도를 만들기 위한 주행 방식

처음에는 아래처럼 움직이는 것이 좋다.

```text
1. 시작 위치에서 천천히 좌우를 돌며 주변 scan 확보
2. 벽을 따라 천천히 직진
3. 코너에서는 급회전하지 않고 천천히 회전
4. 회색 unknown 영역 쪽으로 이동해 공간을 채움
5. 이미 지나간 경로로 다시 돌아와 loop closure 유도
6. 지도 외곽이 충분히 채워지면 저장
```

나쁜 주행:

```text
너무 빠른 회전
벽에서 너무 멀리 떨어져 이동
한 방향으로만 계속 이동
좁은 공간에서 급가속/급정지
같은 위치를 다시 방문하지 않음
```

---

## 6. 지도 저장

`/lee/map`이 정상적으로 나오면 저장할 수 있다.

현재 폴더에 저장:

```bash
cd $ROS2_WS
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 run nav2_map_server map_saver_cli \
  -t /lee/map \
  -f ./slam_map
```

`maps/` 폴더에 저장:

```bash
cd $ROS2_WS
mkdir -p maps

ros2 run nav2_map_server map_saver_cli \
  -t /lee/map \
  -f ./maps/slam_map
```

결과:

```text
slam_map.pgm
slam_map.yaml
```

---

## 7. `-t /lee/map`이 중요한 이유

`map_saver_cli`의 기본 map topic은 보통 `/map`이다.
하지만 현재 SLAM 결과는 `/lee/map`으로 나온다.

따라서 아래처럼 실행하면 실패할 수 있다.

```bash
ros2 run nav2_map_server map_saver_cli -f ./slam_map
```

문제:

```text
map_saver_cli가 /map을 기다림
현재 지도는 /lee/map으로 발행됨
결과적으로 지도를 못 받고 timeout 또는 spin 실패
```

현재 환경에서는 이렇게 해야 한다.

```bash
ros2 run nav2_map_server map_saver_cli \
  -t /lee/map \
  -f ./slam_map
```

---

## 8. 저장된 yaml 해석

현재 예시 `slam_map.yaml`:

```yaml
image: slam_map.pgm
mode: trinary
resolution: 0.05
origin: [-4.98, -4.98, 0]
negate: 0
occupied_thresh: 0.65
free_thresh: 0.25
```

해석:

```text
image
  실제 지도 이미지 파일

resolution
  픽셀 하나가 0.05m를 의미

origin
  지도 이미지의 원점이 map frame에서 어디인지

occupied_thresh
  이 threshold보다 점유 확률이 높으면 벽/장애물

free_thresh
  이 threshold보다 낮으면 이동 가능 공간
```

---

## 9. 지도 저장 후 확인

```bash
ls -lh slam_map.yaml slam_map.pgm
cat slam_map.yaml
```

PGM이 정상인지 간단히 확인:

```bash
file slam_map.pgm
```

RViz2에서 다시 로딩하려면 Day 12/13의 map_server, AMCL, Nav2 흐름과 연결된다.
Day 11에서는 저장 파일이 만들어지는 것까지가 핵심이다.

---

## 10. 이 단계의 결론

```text
SLAM 결과는 RViz2 화면이 아니라 /lee/map topic이다.
map_saver_cli는 /lee/map을 .pgm + .yaml 파일로 저장한다.
현재 환경에서는 -t /lee/map 옵션을 명시해야 한다.
좋은 지도는 좋은 주행에서 나온다.
```
