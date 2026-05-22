# 02. LaserScan / Odometry / TF가 SLAM으로 들어가는 흐름

SLAM Toolbox는 단순히 `/scan`만 받아서 지도를 만드는 것이 아니다. LiDAR 거리 데이터, 로봇의 움직임 추정, 좌표계 관계가 함께 맞아야 한다.

내 환경 기준으로 SLAM 입력은 아래처럼 보면 된다.

```text
/robot_ns/scan
  -> 현재 LiDAR가 본 주변 벽/장애물 거리

/robot_ns/tf, /robot_ns/tf_static
  -> base_scan, base_footprint, odom_robot_ns 등의 좌표계 관계

/robot_ns/odom
  -> Gazebo diff_drive plugin이 계산한 로봇 이동 추정
```

SLAM 출력은 대략 아래다.

```text
/robot_ns/map
  -> 만들어진 OccupancyGrid 지도

map_robot_ns -> odom_robot_ns TF
  -> 지도 좌표계와 오도메트리 좌표계 사이 보정 관계
```

---

## 1. SLAM을 너무 단순하게 보면 안 되는 이유

처음에는 이렇게 생각하기 쉽다.

```text
LiDAR가 벽까지 거리를 재니까 그걸 계속 찍으면 지도가 만들어지는 것 아닌가?
```

절반만 맞다.

LiDAR 한 번의 scan은 “현재 센서 위치에서 본 거리 배열”일 뿐이다. 지도를 만들려면 과거 scan들과 현재 scan들을 같은 좌표계 위에 누적해야 한다.

그러려면 SLAM은 계속 이 질문에 답해야 한다.

```text
방금 들어온 scan은 이전 scan에 비해 로봇이 얼마나 이동한 상태에서 들어온 것인가?
이 scan을 map 위 어디에 붙여야 하는가?
```

그래서 SLAM에는 적어도 아래 정보가 필요하다.

```text
1. LiDAR 거리 배열
2. LiDAR가 로봇의 어느 위치에 붙어 있는지
3. 로봇이 시간에 따라 어떻게 움직였는지
4. scan끼리 서로 얼마나 잘 맞는지
```

---

## 2. LaserScan은 무엇을 제공하는가

`/robot_ns/scan`은 `sensor_msgs/msg/LaserScan` 타입이다.

중요 필드:

```text
header.frame_id
  -> 이 scan이 어느 센서 좌표계 기준인지

angle_min
  -> ranges[0]이 가리키는 시작 각도

angle_increment
  -> ranges[index] 사이 각도 간격

range_min, range_max
  -> 센서가 유효하다고 보는 최소/최대 거리

ranges
  -> 각 방향의 거리 배열
```

거리 하나의 방향은 이렇게 계산한다.

```text
angle = angle_min + index * angle_increment
```

여기서 angle은 `base_scan` 기준 각도다.

즉, `ranges[100]`은 전역 map 기준이 아니라:

```text
base_scan 좌표계에서 angle_min + 100 * angle_increment 방향으로 본 거리
```

이다.

---

## 3. LaserScan 하나만으로는 지도가 안 되는 이유

한 시점의 scan은 이런 정보다.

```text
현재 센서 위치 기준으로
왼쪽 1.2m에 벽
앞쪽 2.0m에 벽
오른쪽 0.8m에 벽
```

그런데 로봇이 조금 움직인 뒤에도 비슷한 scan이 들어온다.

```text
현재 센서 위치 기준으로
왼쪽 1.1m에 벽
앞쪽 1.8m에 벽
오른쪽 0.9m에 벽
```

이 둘을 같은 map 위에 합치려면 로봇이 얼마나 이동했는지 알아야 한다.

그래서 `/robot_ns/odom`과 TF가 필요하다.

---

## 4. Odometry는 무엇을 제공하는가

`/robot_ns/odom`은 `nav_msgs/msg/Odometry` 타입이다.

내 환경 기준으로 보통 이런 관계를 가진다.

```text
header.frame_id: odom_robot_ns
child_frame_id: base_footprint
```

의미:

```text
odom_robot_ns 좌표계에서 봤을 때 base_footprint가 어디 있는가
```

Gazebo diff_drive plugin은 `/robot_ns/cmd_vel`을 받아 로봇을 움직이고, 그 결과를 `/robot_ns/odom`과 TF로 내보낸다.

흐름:

```text
/robot_ns/cmd_vel
  -> Gazebo diff_drive plugin
  -> 로봇 이동 시뮬레이션
  -> /robot_ns/odom
  -> odom_robot_ns -> base_footprint TF
```

SLAM은 이 오도메트리를 “로봇이 대략 이 정도 움직였을 것이다”라는 초기 추정으로 사용한다.

---

## 5. TF는 무엇을 연결하는가

SLAM이 scan을 사용하려면 아래 관계를 알아야 한다.

```text
odom_robot_ns -> base_footprint
base_footprint -> base_scan
```

그래야 현재 scan을 odom 기준으로 해석할 수 있다.

예시:

```text
LaserScan frame_id: base_scan
TF: base_footprint -> base_scan
TF: odom_robot_ns -> base_footprint
```

SLAM은 이 정보를 이용해:

```text
base_scan 기준 scan
-> base_footprint 기준 scan
-> odom_robot_ns 기준 scan
-> map_robot_ns 기준 누적 지도
```

으로 변환해간다.

---

## 6. SLAM Toolbox의 중요한 입력/출력

내 환경 기준:

| 구분 | 이름 | 역할 |
|---|---|---|
| input topic | `/robot_ns/scan` | LiDAR 거리 데이터 |
| input TF | `/robot_ns/tf`, `/robot_ns/tf_static` | scan/base/odom 좌표계 관계 |
| odom frame | `odom_robot_ns` | 단기적으로 부드러운 이동 기준 |
| base frame | `base_footprint` | 로봇 기준 좌표계 |
| map frame | `map_robot_ns` | 전역 지도 좌표계 |
| output topic | `/robot_ns/map` | OccupancyGrid 지도 |
| output TF | `map_robot_ns -> odom_robot_ns` | 오도메트리 누적 오차를 map 기준으로 보정 |

SLAM이 발행하는 `map_robot_ns -> odom_robot_ns`는 매우 중요하다.

오도메트리는 시간이 지나면 누적 오차가 생긴다. SLAM은 scan matching과 loop closure를 통해 이 오차를 map 기준으로 보정한다. 그 보정 관계가 `map_robot_ns -> odom_robot_ns`이다.

---

## 7. scan matching을 직관적으로 이해하기

scan matching은 복잡하게 보면 알고리즘이 많지만, 직관은 단순하다.

```text
이전 scan과 현재 scan을 겹쳐봤을 때
어느 위치/각도로 옮기면 벽 모양이 가장 잘 맞는가?
```

예를 들어 복도에서 로봇이 앞으로 조금 이동했다면, 현재 scan은 이전 scan보다 벽이 살짝 가까워지거나 멀어진 형태일 것이다.

SLAM은 오도메트리로 “대략 여기쯤 움직였겠지”라고 예측한 뒤, scan matching으로 “실제로 scan 모양이 가장 잘 맞는 위치”를 찾는다.

```text
odometry: 초기 추정
scan matching: 센서 관측 기반 보정
loop closure: 예전에 왔던 장소를 다시 만났을 때 전체 지도 보정
```

---

## 8. OccupancyGrid는 무엇인가

SLAM 결과인 `/robot_ns/map`은 `nav_msgs/msg/OccupancyGrid` 타입이다.

지도는 이미지처럼 보이지만 실제로는 격자 배열이다.

각 cell 값은 대략 이렇게 해석한다.

```text
0   : 비어 있을 가능성이 높음
100 : 장애물일 가능성이 높음
-1  : 아직 모름
```

저장하면 보통 두 파일이 생긴다.

```text
slam_map.yaml
slam_map.pgm
```

`pgm`은 지도 이미지이고, `yaml`은 해상도, 원점, occupied/free threshold 같은 메타데이터를 가진다.

---

## 9. 내 환경에서 SLAM 입력 확인 순서

### 1단계: scan 확인

```bash
ros2 topic hz /robot_ns/scan
ros2 topic echo /robot_ns/scan --once | grep frame_id
```

기대:

```text
frame_id: base_scan
```

### 2단계: odom 확인

```bash
ros2 topic hz /robot_ns/odom
ros2 topic echo /robot_ns/odom --once | grep -E 'frame_id|child_frame_id'
```

기대:

```text
frame_id: odom_robot_ns
child_frame_id: base_footprint
```

### 3단계: TF 확인

```bash
ros2 run tf2_ros tf2_echo odom_robot_ns base_footprint
ros2 run tf2_ros tf2_echo base_footprint base_scan
```

### 4단계: SLAM 출력 확인

```bash
ros2 topic list | grep map
ros2 topic echo /robot_ns/map --once
ros2 run tf2_ros tf2_echo map_robot_ns odom_robot_ns
```

---

## 10. rosbag offline SLAM에서 특히 조심할 점

bag에 저장된 topic이 현재 launch 구조와 다를 수 있다.

예를 들어 이전 bag:

```text
/scan
/odom
/tf
/tf_static
```

현재 구조:

```text
/robot_ns/scan
/robot_ns/odom
/robot_ns/tf
/robot_ns/tf_static
```

이 경우 topic remap이 필요하다.

```bash
ros2 bag play rosbag2_xxx \
  --clock \
  --remap /scan:=/robot_ns/scan \
  --remap /odom:=/robot_ns/odom \
  --remap /tf:=/robot_ns/tf \
  --remap /tf_static:=/robot_ns/tf_static
```

하지만 다시 강조하면:

```text
topic remap은 frame_id를 바꾸지 않는다.
```

bag 안의 LaserScan `header.frame_id`가 현재 TF tree에 없는 이름이면, topic 이름을 맞춰도 SLAM은 실패할 수 있다.

---

## 11. 핵심 요약

```text
SLAM은 /robot_ns/scan만으로 map을 만들지 않는다.
/robot_ns/scan은 현재 센서가 본 거리 배열이다.
/robot_ns/odom은 로봇이 대략 어떻게 움직였는지 알려준다.
TF는 base_scan, base_footprint, odom_robot_ns의 좌표 관계를 알려준다.
SLAM은 scan matching으로 odometry 오차를 보정한다.
SLAM의 주요 출력은 /robot_ns/map과 map_robot_ns -> odom_robot_ns TF다.
rosbag replay에서는 topic remap과 frame_id/TF 일치를 따로 확인해야 한다.
```

---

## 12. 이 문서와 연결되는 기존 문서

```text
day_10_gazebo_urdf/07_lidar_avoidance_and_laserscan.md
day_11_slam/02_slam_concepts_and_data_model.md
day_11_slam/background/scan_matching_loop_closure_minimum.md
day_11_slam/background/occupancy_grid_yaml_pgm_posegraph.md
appendix/slam_topic_frame_table.md
appendix/validation_sequence_gazebo_slam_amcl_nav2.md
```
