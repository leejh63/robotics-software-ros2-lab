# 05. Runtime Notes

이 문서는 TurtleBot3 Day 15 실습을 실행하면서 확인한 판단 기준과 주의사항을 정리한다. 명령어만 빠르게 확인할 때는 `commands/turtlebot3_day15_commands.md`를 먼저 본다.

## 1. 환경 적용 기준

TurtleBot3 실습 환경은 `~/.bashrc`에 고정하지 않고, 각 터미널에서 필요한 시점에만 적용한다.

```bash
source ~/envs/tb3_humble.bash
cd "$TB3_WS"
```

이 방식은 다른 ROS 2 workspace와 TurtleBot3 실습 환경이 섞이는 것을 줄인다.

## 2. 지도 저장 경로 기준

지도 파일은 다음 경로를 기준으로 설명한다.

```text
$TB3_WS/maps/tb3_map.pbstream
$TB3_WS/maps/tb3_map.pgm
$TB3_WS/maps/tb3_map.yaml
```

개인 실제 경로는 문서에 직접 넣지 않는다.

## 3. Cartographer 저장 지도 흐름

Cartographer로 지도를 만들 때는 `.pbstream`을 먼저 저장하고, 그다음 ROS map 형식인 `.pgm + .yaml`로 변환한다.

```bash
ros2 service call /write_state cartographer_ros_msgs/srv/WriteState "{filename: '$TB3_WS/maps/tb3_map.pbstream'}"

ros2 run cartographer_ros cartographer_pbstream_to_ros_map -pbstream_filename $TB3_WS/maps/tb3_map.pbstream -map_filestem $TB3_WS/maps/tb3_map -resolution 0.05
```

이후 AMCL/Nav2에서는 `$TB3_WS/maps/tb3_map.yaml`을 사용한다.

## 4. map_server 확인 기준

`map_server`는 lifecycle node이므로 실행만 했다고 바로 `/map`을 정상 발행한다고 보면 안 된다. active 상태인지 확인한다.

```bash
ros2 lifecycle get /map_server
```

정상 예시는 다음과 같다.

```text
active [3]
```

`/map`은 transient local QoS로 확인하는 편이 안전하다.

```bash
ros2 topic echo /map nav_msgs/msg/OccupancyGrid --once --qos-durability transient_local --qos-reliability reliable
```

## 5. AMCL/Nav2에서 static TF를 쓰지 않는 기준

지도 확인만 할 때는 임시로 `static_transform_publisher map odom`을 사용할 수 있다. 하지만 AMCL/Nav2 본 흐름에서는 사용하지 않는다.

```text
Part 2 단순 지도 확인: 필요 시 static TF 사용 가능
AMCL/Nav2 본 흐름: static TF 사용하지 않음
map -> odom은 AMCL이 발행
```

임시 static TF가 남아 있으면 AMCL이 발행해야 할 `map -> odom`과 충돌하거나, 실제 localization 문제를 가릴 수 있다.

## 6. AMCL 초기 위치 기준

AMCL은 초기 위치를 `map` 프레임 기준으로 받아야 한다. RViz에서 `2D Pose Estimate`를 사용할 때는 Fixed Frame을 먼저 확인한다.

```text
RViz Global Options -> Fixed Frame = map
```

명령어로 직접 넣을 때는 `frame_id: 'map'`을 명시한다.

```bash
ros2 topic pub --once /initialpose geometry_msgs/msg/PoseWithCovarianceStamped "{header: {frame_id: 'map'}, pose: {pose: {position: {x: 0.0, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}}"
```

## 7. Navigation2 통합 실행 기준

`turtlebot3_navigation2 navigation2.launch.py`를 사용할 때는 개별 실행한 `map_server`, `amcl`, `lifecycle_manager`와 중복되지 않게 정리한다.

```bash
pkill -f map_server
pkill -f lifecycle_manager
pkill -f amcl
pkill -f static_transform_publisher
```

그다음 통합 launch를 실행한다.

```bash
ros2 launch turtlebot3_navigation2 navigation2.launch.py use_sim_time:=True map:=$TB3_WS/maps/tb3_map.yaml
```

## 8. Explore Lite 흐름은 별도 확장으로 본다

Explore Lite 자동 탐색은 저장 지도 기반 AMCL/Nav2 흐름과 다르다.

```text
기존 흐름: Cartographer로 지도 생성 -> 저장 지도 -> AMCL -> Nav2
추가 흐름: slam_toolbox online SLAM -> Nav2 -> explore_lite 자동 탐색
```

Explore Lite 흐름에서는 AMCL, 저장 지도용 map_server, 임시 `static_transform_publisher map odom`을 함께 실행하지 않는다. `slam_toolbox`가 SLAM을 수행하면서 `/map`과 `map -> odom` 관계를 제공하고, `explore_lite`가 frontier 목표를 Nav2로 보낸다.
