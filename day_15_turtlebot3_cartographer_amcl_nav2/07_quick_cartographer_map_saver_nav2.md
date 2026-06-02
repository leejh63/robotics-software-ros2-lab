# 07. Cartographer SLAM에서 Navigation2까지 빠른 실습 흐름

## 1. 목표

TurtleBot3를 직접 조종하면서 Cartographer로 지도를 만들고, `map_saver_cli`로 지도 파일을 저장한 뒤, 저장된 지도를 사용해서 Navigation2 목표 주행까지 확인한다.

전체 흐름:

```text
TurtleBot3/Gazebo 실행
-> Cartographer SLAM 실행
-> teleop_keyboard로 주행하며 지도 작성
-> map_saver_cli로 pgm/yaml 지도 저장
-> navigation2.launch.py에 저장 지도 전달
-> RViz에서 2D Pose Estimate와 Navigation2 Goal 지정
```

## 2. 공통 준비

각 터미널에서 먼저 환경을 적용한다.

```bash
export TB3_WS=~/turtlebot3_ws
cd "$TB3_WS"
source ~/envs/tb3_humble.bash
```

지도 저장 폴더:

```bash
mkdir -p "$TB3_WS/maps"
```

## 3. 터미널 1 - TurtleBot3 또는 Gazebo 실행

시뮬레이션 기준이면 Gazebo를 실행한다.

```bash
cd "$TB3_WS"
source ~/envs/tb3_humble.bash

ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

실제 TurtleBot3에서 실행 중이라면 로봇 bringup이 이미 되어 있어야 한다.

## 4. 터미널 2 - Cartographer SLAM 실행

```bash
cd "$TB3_WS"
source ~/envs/tb3_humble.bash

ros2 launch turtlebot3_cartographer cartographer.launch.py use_sim_time:=True
```

실제 로봇에서 `/clock`을 쓰지 않는 경우에는 `use_sim_time:=True`를 빼거나 `False`로 둔다.

```bash
ros2 launch turtlebot3_cartographer cartographer.launch.py
```

이 단계부터 SLAM이 진행되고 `/map`이 생성된다.

## 5. 터미널 3 - 키보드 조종으로 지도 만들기

```bash
cd "$TB3_WS"
source ~/envs/tb3_humble.bash

ros2 run turtlebot3_teleop teleop_keyboard
```

주행할 때는 벽과 장애물 주변을 천천히 돌면서 이미 지나간 구역을 다시 지나가면 지도가 더 안정적으로 맞춰진다.

## 6. 터미널 4 - 지도 저장

Cartographer가 `/map`을 발행 중인 상태에서 현재 지도를 저장한다.

```bash
cd "$TB3_WS"
source ~/envs/tb3_humble.bash
mkdir -p "$TB3_WS/maps"

ros2 run nav2_map_server map_saver_cli -f "$TB3_WS/maps/tb3_map"
```

생성 결과:

```text
$TB3_WS/maps/tb3_map.pgm
$TB3_WS/maps/tb3_map.yaml
```

확인:

```bash
ls -lh "$TB3_WS/maps"
```

`map_saver_cli`는 현재 `/map`을 바로 `.pgm + .yaml`로 저장한다. Cartographer의 pose graph 상태까지 보존해야 하면 `02_cartographer_slam_map_save.md`의 `.pbstream` 저장 방식을 사용한다.

## 7. 기존 SLAM 노드 정리

저장된 지도로 Navigation2를 실행하기 전에 SLAM 관련 프로세스가 남아 있으면 정리한다.

```bash
pkill -f cartographer
pkill -f teleop_keyboard
pkill -f rviz2
```

Gazebo 또는 실제 로봇 bringup은 계속 필요하다.

## 8. Navigation2 실행

저장한 지도 경로를 `map:=` 인자로 전달한다.

```bash
cd "$TB3_WS"
source ~/envs/tb3_humble.bash

ros2 launch turtlebot3_navigation2 navigation2.launch.py \
use_sim_time:=True \
map:="$TB3_WS/maps/tb3_map.yaml"
```

실제 로봇에서 `/clock`을 쓰지 않는 경우에는 `use_sim_time:=True`를 빼거나 `False`로 둔다.

```bash
ros2 launch turtlebot3_navigation2 navigation2.launch.py \
map:="$TB3_WS/maps/tb3_map.yaml"
```

## 9. RViz에서 위치 추정과 목표 지정

Navigation2가 실행되면 RViz에서 다음 순서로 확인한다.

```text
Fixed Frame = map
2D Pose Estimate로 현재 로봇 위치 지정
Navigation2 Goal로 목표 위치 지정
```

정상 동작하면 AMCL이 현재 위치를 추정하고, Nav2가 global path와 local control을 만들어 로봇을 목표 위치로 이동시킨다.

확인 명령:

```bash
ros2 topic echo /amcl_pose --once
ros2 action list | grep navigate
ros2 run tf2_ros tf2_echo map odom
```

