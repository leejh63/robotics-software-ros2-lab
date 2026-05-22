# 03. Costmap, Topic, Frame 흐름

Nav2에서 가장 많이 헷갈리는 지점은 costmap이다.  
Costmap은 단순히 RViz에 보이는 색칠된 지도라기보다, planner와 controller가 실제 판단에 쓰는 비용 지도다.

---

## 1. Costmap이 하는 일

Costmap은 공간을 격자로 나누고 각 칸에 비용을 준다.

```text
0
  자유 공간. 지나갈 수 있음.

1~253
  장애물 근처의 위험 영역. 지나갈 수는 있지만 비용이 큼.

254
  lethal obstacle. 사실상 통과 불가.

255
  unknown. 모르는 영역.
```

Nav2는 경로를 만들 때 단순히 거리가 짧은 길만 고르지 않는다.  
비용이 낮은 칸을 따라가려고 한다.

```text
짧지만 벽에 붙는 길 < 조금 멀어도 안전한 길
```

---

## 2. Global Costmap과 Local Costmap

Nav2에는 costmap이 두 개 있다.

| 구분 | Global Costmap | Local Costmap |
|---|---|---|
| 목적 | 전체 경로 계획 | 로봇 주변 실시간 회피 |
| 기준 frame | `map_robot_ns` | `odom_robot_ns` |
| 크기 | 전체 지도 또는 넓은 영역 | 로봇 주변 rolling window |
| 주요 입력 | static map, obstacle, inflation | scan 기반 obstacle, inflation |
| 소비자 | planner_server | controller_server, behavior_server |
| 대표 출력 | `/robot_ns/global_costmap/costmap` | `/robot_ns/local_costmap/costmap` |

쉽게 말하면 다음과 같다.

```text
Global Costmap
  지도를 보고 큰 길을 고르는 용도

Local Costmap
  지금 눈앞에서 부딪히지 않게 속도를 조절하는 용도
```

---

## 3. Costmap Layer 구조

Costmap은 여러 레이어를 합쳐서 만든다.

```text
Static Layer
  SLAM으로 만든 저장 지도에서 벽/공간 정보를 가져온다.

Obstacle Layer 또는 Voxel Layer
  /robot_ns/scan 같은 실시간 센서로 장애물을 찍고 지운다.

Inflation Layer
  장애물 주변에 안전 여유 비용을 퍼뜨린다.
```

레이어가 합쳐지는 흐름:

```text
저장 지도 벽 정보
  + 실시간 LiDAR 장애물
  + 장애물 주변 inflation
  = 최종 costmap
```

현재 `nav2_params.yaml` 기준으로는 local costmap에 static layer를 넣지 않았다.

```text
local_costmap
  odom_robot_ns 기준 rolling window
  /robot_ns/scan 기반 obstacle layer
  inflation layer
```

이 구조는 자연스럽다. local costmap은 전체 지도보다 로봇 주변의 실시간 장애물 반영이 중요하기 때문이다.

---

## 4. 현재 환경의 주요 topic

현재 `/robot_ns` namespace 기준으로 주요 topic은 다음과 같다.

| topic | 의미 | 주로 보는 곳 |
|---|---|---|
| `/robot_ns/map` | map_server가 발행하는 저장 지도 | RViz Map, global costmap static layer |
| `/robot_ns/scan` | LiDAR 거리 데이터 | AMCL, local/global obstacle layer |
| `/robot_ns/odom` | odometry | controller, velocity_smoother, TF 흐름 |
| `/robot_ns/global_costmap/costmap` | 전체 지도 기준 비용 지도 | RViz Map display |
| `/robot_ns/local_costmap/costmap` | 로봇 주변 비용 지도 | RViz Map display |
| `/robot_ns/plan` | planner_server가 만든 global path | RViz Path display |
| `/robot_ns/cmd_vel` | 최종 속도 명령 | Gazebo diff_drive plugin |
| `/amcl_pose` | AMCL 위치 추정 결과 | RViz Pose, topic echo |
| `/particle_cloud` | AMCL particle cloud | RViz PoseArray |

주의할 점:

```text
Localization 노드 이름은 /amcl, /map_server처럼 namespace가 없을 수 있다.
하지만 해당 노드가 발행/구독하는 topic은 /robot_ns/map, /robot_ns/scan처럼 remap되어 있을 수 있다.
```

노드 이름과 topic 이름을 같은 것으로 보면 안 된다.

---

## 5. 현재 환경의 frame 흐름

자율주행에 필요한 TF 체인은 다음이다.

```text
map_robot_ns -> odom_robot_ns -> base_footprint -> base_scan
```

각 frame의 의미:

```text
map_robot_ns
  저장 지도 기준의 전역 좌표계

odom_robot_ns
  로봇이 출발한 뒤 odometry로 누적한 지역 좌표계

base_footprint
  로봇 바닥 중심 프레임

base_scan
  LiDAR 센서 프레임
```

각 transform을 제공하는 주체:

| transform | 제공 주체 | 의미 |
|---|---|---|
| `map_robot_ns -> odom_robot_ns` | AMCL | 지도 기준으로 odom 오차 보정 |
| `odom_robot_ns -> base_footprint` | Gazebo/diff_drive/odometry | 로봇의 주행 위치 변화 |
| `base_footprint -> base_scan` | robot_state_publisher | 로봇 모델상 센서 장착 위치 |

---

## 6. frame_id와 topic 이름 구분

Action goal을 보낼 때 아래처럼 쓴다.

```bash
ros2 action send_goal /robot_ns/navigate_to_pose nav2_msgs/action/NavigateToPose \
"{pose: {header: {frame_id: 'map_robot_ns'}, pose: {position: {x: 1.0, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}}"
```

여기서 `/robot_ns/navigate_to_pose`는 action topic 이름이고, `map_robot_ns`는 goal pose가 표현되는 좌표계다.

```text
/robot_ns/navigate_to_pose
  데이터를 보내는 통신 경로

map_robot_ns
  pose 값 x, y, yaw를 해석할 기준 좌표계
```

둘은 완전히 다른 개념이다.

---

## 7. costmap 문제가 생길 때 보는 순서

```text
1. /robot_ns/map이 나오는가?
2. /robot_ns/scan이 나오는가?
3. map_robot_ns -> odom_robot_ns TF가 있는가?
4. odom_robot_ns -> base_footprint TF가 있는가?
5. /robot_ns/global_costmap/costmap이 나오는가?
6. /robot_ns/local_costmap/costmap이 나오는가?
7. 목표점이 벽이나 inflation 영역 안에 찍힌 것은 아닌가?
```

명령어:

```bash
ros2 topic echo /robot_ns/map --once
ros2 topic hz /robot_ns/scan
ros2 run tf2_ros tf2_echo map_robot_ns odom_robot_ns
ros2 run tf2_ros tf2_echo odom_robot_ns base_footprint
ros2 topic echo /robot_ns/global_costmap/costmap --once
ros2 topic echo /robot_ns/local_costmap/costmap --once
```

