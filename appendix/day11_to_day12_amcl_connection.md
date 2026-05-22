# Day 11 SLAM 결과가 Day 12 AMCL 입력으로 이어지는 흐름

## 1. 연결 요약

Day 11에서 한 일:

```text
Gazebo world를 띄움
/robot_ns/scan, /robot_ns/odom, /robot_ns/tf를 SLAM Toolbox에 입력
SLAM Toolbox가 /robot_ns/map 생성
map_saver_cli로 slam_map.yaml, slam_map.pgm 저장
```

Day 12에서 하는 일:

```text
slam_map.yaml을 map_server로 다시 로드
/robot_ns/map으로 static map 발행
AMCL이 /robot_ns/map, /robot_ns/scan, odom TF를 이용해 위치 추정
```

---

## 2. 파일 기준 연결

Day 11 산출물:

```text
$ROS2_WS/slam_map.yaml
$ROS2_WS/slam_map.pgm
```

Day 12 map_server 입력:

```bash
ros2 run nav2_map_server map_server \
  --ros-args \
  -p yaml_filename:=$ROS2_WS/slam_map.yaml \
  -p use_sim_time:=true \
  -p frame_id:=map_robot_ns \
  -r /map:=/robot_ns/map
```

---

## 3. topic 기준 연결

Day 11 SLAM 중:

```text
/robot_ns/scan  -> SLAM Toolbox 입력
/robot_ns/odom  -> odometry 입력
/robot_ns/tf    -> TF 입력
/robot_ns/map   -> SLAM Toolbox 출력
```

Day 12 AMCL 중:

```text
/robot_ns/map   -> map_server 출력, AMCL 입력
/robot_ns/scan  -> Gazebo LiDAR 출력, AMCL 입력
/robot_ns/tf    -> odom_robot_ns -> base_footprint 등 TF 입력, AMCL 출력도 포함
```

같은 `/robot_ns/map` 이름을 쓰더라도 의미가 다르다.

```text
Day 11의 /robot_ns/map:
  SLAM Toolbox가 실시간으로 만들어내는 지도

Day 12의 /robot_ns/map:
  map_server가 저장된 yaml/pgm을 읽어서 발행하는 정적 지도
```

---

## 4. frame 기준 연결

Day 11 SLAM에서 map frame을 `map_robot_ns`로 맞췄다면 Day 12도 `map_robot_ns`를 유지해야 한다.

```text
Day 11 map frame: map_robot_ns
Day 12 map frame: map_robot_ns
```

AMCL 파라미터도 그에 맞춰야 한다.

```yaml
global_frame_id: map_robot_ns
odom_frame_id: odom_robot_ns
base_frame_id: base_footprint
```

---

## 5. world와 map은 한 쌍이다

SLAM으로 만든 지도는 특정 world에서 주행하며 만든 결과다.

따라서 AMCL 때도 같은 구조의 world와 map을 써야 한다.

```text
slam.world      <-> slam_map.yaml
lee_world.world <-> room_map.yaml
```

틀린 조합:

```text
slam.world + room_map.yaml
lee_world.world + slam_map.yaml
```

틀린 조합을 쓰면:

```text
/robot_ns/map은 정상 발행됨
/robot_ns/scan도 정상 발행됨
하지만 scan 점이 map 벽과 맞지 않음
AMCL이 엉뚱한 위치로 수렴하거나 수렴하지 못함
```

---

## 6. map_robot_ns -> odom_robot_ns 발행 주체

SLAM 중에는 SLAM Toolbox가 `map_robot_ns -> odom_robot_ns`에 해당하는 보정 관계를 만든다.

AMCL 중에는 AMCL이 이 관계를 만든다.

따라서 아래를 동시에 켜면 안 된다.

```text
SLAM Toolbox mapping/localization 노드
AMCL
static map_robot_ns -> odom_robot_ns publisher
```

Day 12 AMCL 실습에서는 AMCL만 이 TF를 발행해야 한다.
