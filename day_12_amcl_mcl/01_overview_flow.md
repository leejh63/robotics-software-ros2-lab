# 01. Day 12 AMCL 전체 흐름

## 1. Day 11에서 Day 12로 넘어가는 이유

Day 11 SLAM에서 만든 결과물은 보통 아래 파일이다.

```text
slam_map.yaml
slam_map.pgm
```

이 파일은 “로봇이 움직이며 만든 지도”다. Day 12에서는 이 지도를 다시 불러온다. 그리고 로봇이 그 지도 위에서 현재 어디에 있는지 추정한다.

```text
Day 11 결과물: 저장된 지도
Day 12 목표: 저장된 지도 위에서 현재 위치 추정
```

---

## 2. SLAM과 AMCL의 차이

| 구분 | SLAM | AMCL |
|---|---|---|
| 목적 | 지도 생성 + 위치 추정 | 이미 있는 지도에서 위치 추정 |
| 지도 입력 | 없어도 시작 가능 | 반드시 필요 |
| 지도 출력 | `/map`, `.yaml`, `.pgm`, `.posegraph` | 새 지도는 만들지 않음 |
| 핵심 입력 | LiDAR, odom, TF | static map, LiDAR, odom, TF, initial pose |
| 대표 노드 | `slam_toolbox` | `nav2_map_server`, `nav2_amcl` |
| 핵심 출력 | map, map->odom 보정 | `/amcl_pose`, `/particle_cloud`, map->odom 보정 |

AMCL은 SLAM의 대체재가 아니다. 역할이 다르다.

```text
지도가 없을 때: SLAM
지도가 이미 있을 때: AMCL
```

---

## 3. 현재 환경의 데이터 흐름

일반 예제 흐름:

```text
map_server -> /map
LiDAR      -> /scan
Odometry   -> odom -> base_link TF
AMCL       -> map -> odom TF, /amcl_pose, /particle_cloud
```

현재 환경 흐름:

```text
map_server -> /robot_ns/map
LiDAR      -> /robot_ns/scan
Odometry   -> odom_robot_ns -> base_footprint TF
AMCL       -> map_robot_ns -> odom_robot_ns TF, /amcl_pose, /particle_cloud
```

그림으로 보면 아래와 같다.

```text
slam_map.yaml / slam_map.pgm
          |
          v
+----------------+
|  map_server    | ----> /robot_ns/map --------------------+
+----------------+                                      |
                                                        v
/robot_ns/scan ------------------------------------------> +------+ ----> /amcl_pose
odom_robot_ns -> base_footprint TF ----------------------> | AMCL | ----> /particle_cloud
/initialpose ---------------------------------------> +------+ ----> map_robot_ns -> odom_robot_ns TF
```

---

## 4. 노드별 역할

### Gazebo

가상 환경과 로봇의 물리 시뮬레이션을 담당한다.

Gazebo plugin이 만들어주는 핵심 데이터:

```text
/robot_ns/scan
/robot_ns/odom
/robot_ns/cmd_vel 구독
```

### robot_state_publisher

URDF/Xacro의 link/joint 관계를 읽어서 로봇 내부 TF를 발행한다.

예:

```text
base_footprint -> base_link
base_link -> base_scan
base_link -> camera_link
```

### map_server

`slam_map.yaml`과 `slam_map.pgm`을 읽어서 static map을 발행한다.

```text
입력: slam_map.yaml
출력: /robot_ns/map
message type: nav_msgs/OccupancyGrid
frame_id: map_robot_ns
```

### AMCL

지도, LiDAR, odom TF, initialpose를 이용해서 로봇의 현재 위치를 추정한다.

```text
입력:
  /robot_ns/map
  /robot_ns/scan
  odom_robot_ns -> base_footprint TF
  /initialpose

출력:
  /amcl_pose
  /particle_cloud
  map_robot_ns -> odom_robot_ns TF
```

### lifecycle_manager

`map_server`와 `amcl`은 lifecycle node다. 단순히 프로세스가 떠 있는 것만으로는 동작 준비가 끝난 것이 아니다.

```text
unconfigured -> inactive -> active
```

AMCL 실습에서는 `active` 상태까지 올라가야 정상으로 본다.

---

## 5. Day 12의 성공 기준

Day 12에서 최소 성공 기준은 아래다.

```text
1. /robot_ns/map이 나온다.
2. /robot_ns/scan이 나온다.
3. /amcl이 active 상태다.
4. RViz에서 /robot_ns/map과 /robot_ns/scan이 보인다.
5. RViz 2D Pose Estimate 또는 /initialpose로 초기 위치를 준다.
6. /particle_cloud가 로봇 주변으로 모인다.
7. /amcl_pose가 map_robot_ns 기준으로 나온다.
8. map_robot_ns -> odom_robot_ns -> base_footprint TF chain이 이어진다.
```

이 중에서 가장 중요한 것은 마지막 TF chain이다.

```text
map_robot_ns -> odom_robot_ns -> base_footprint
```

이 체인이 있어야 Day 13 Nav2가 현재 위치와 목표 위치를 같은 좌표계에서 계산할 수 있다.
