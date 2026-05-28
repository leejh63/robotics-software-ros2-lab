# 02. SLAM 지도 생성 및 저장

## 1. 목표

Gazebo에서 TurtleBot3 Burger를 움직이면서 Cartographer SLAM으로 지도를 만들고, 결과를 Nav2에서 사용할 수 있는 지도 파일로 저장한다.

최종 결과물:

```text
maps/tb3_map.pbstream
maps/tb3_map.pgm
maps/tb3_map.yaml
```

## 2. 공통 준비

각 터미널에서 먼저 실행한다.

```bash
cd "$TB3_WS"
source ~/envs/tb3_humble.bash
```

지도 저장 폴더 생성:

```bash
mkdir -p "$TB3_WS/maps"
```

## 3. 터미널 1 — Gazebo 실행

```bash
cd "$TB3_WS"
source ~/envs/tb3_humble.bash

ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

Gazebo가 실행되고 TurtleBot3 Burger 월드가 보이면 정상이다.

## 4. 터미널 2 — Cartographer SLAM 실행

```bash
cd "$TB3_WS"
source ~/envs/tb3_humble.bash

ros2 launch turtlebot3_cartographer cartographer.launch.py use_sim_time:=True
```

`use_sim_time:=True`는 Gazebo의 `/clock`을 기준 시간으로 사용하기 위해 필요하다.

## 5. 터미널 3 — Teleop 조종

```bash
cd "$TB3_WS"
source ~/envs/tb3_humble.bash

ros2 run turtlebot3_teleop teleop_keyboard
```

주행 팁:

- 너무 빠르게 움직이지 않는다.
- 벽과 장애물 주변을 천천히 이동한다.
- 이미 지나간 곳으로 다시 돌아오면 loop closure가 발생하여 지도가 더 잘 정렬될 수 있다.

## 6. 터미널 4 — Cartographer 상태 저장

Cartographer가 실행 중인 상태에서 실행한다.

```bash
ros2 service call /write_state cartographer_ros_msgs/srv/WriteState \
"{filename: '$TB3_WS/maps/tb3_map.pbstream'}"
```

환경 변수 사용:

```bash
ros2 service call /write_state cartographer_ros_msgs/srv/WriteState \
"{filename: '${TB3_WS}/maps/tb3_map.pbstream'}"
```

## 7. pbstream을 pgm/yaml로 변환

```bash
ros2 run cartographer_ros cartographer_pbstream_to_ros_map \
-pbstream_filename $TB3_WS/maps/tb3_map.pbstream \
-map_filestem $TB3_WS/maps/tb3_map \
-resolution 0.05
```

환경 변수 사용:

```bash
ros2 run cartographer_ros cartographer_pbstream_to_ros_map \
-pbstream_filename "$TB3_WS/maps/tb3_map.pbstream" \
-map_filestem "$TB3_WS/maps/tb3_map" \
-resolution 0.05
```

확인:

```bash
ls -lh $TB3_WS/maps
```

예상:

```text
tb3_map.pbstream
tb3_map.pgm
tb3_map.yaml
```

## 8. 파일 의미

| 파일 | 의미 |
|---|---|
| `tb3_map.pbstream` | Cartographer 포즈 그래프와 서브맵을 보존하는 원본 |
| `tb3_map.pgm` | Nav2에서 사용하는 지도 이미지 |
| `tb3_map.yaml` | 지도 해상도, 원점, 점유 임계값 등의 메타데이터 |

## 9. map_server 단독 확인

저장된 지도가 제대로 로드되는지 확인하려면 다음 명령을 사용할 수 있다.

```bash
ros2 run nav2_map_server map_server \
--ros-args \
-p yaml_filename:=$TB3_WS/maps/tb3_map.yaml \
-p use_sim_time:=True
```

`map_server`는 lifecycle node이므로 `lifecycle_manager`도 함께 실행한다.

```bash
ros2 run nav2_lifecycle_manager lifecycle_manager \
--ros-args \
-p node_names:='["map_server"]' \
-p autostart:=True \
-p use_sim_time:=True
```

확인:

```bash
ros2 lifecycle get /map_server

ros2 topic echo /map nav_msgs/msg/OccupancyGrid --once \
--qos-durability transient_local \
--qos-reliability reliable
```
