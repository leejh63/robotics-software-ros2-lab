# AMCL Topic / Frame 표

## 1. 핵심 topic

| Topic | Message | Producer | Consumer | 의미 |
|---|---|---|---|---|
| `/robot_ns/map` | `nav_msgs/OccupancyGrid` | `map_server` | AMCL, RViz, Nav2 costmap | 저장 지도 |
| `/robot_ns/scan` | `sensor_msgs/LaserScan` | Gazebo LiDAR plugin | AMCL, RViz, costmap | 현재 LiDAR 거리 |
| `/amcl_pose` | `geometry_msgs/PoseWithCovarianceStamped` | AMCL | RViz, 확인용 | map 기준 추정 pose |
| `/particle_cloud` | `nav2_msgs/ParticleCloud` | AMCL | RViz | 위치 후보 particle |
| `/initialpose` | `geometry_msgs/PoseWithCovarianceStamped` | RViz 또는 CLI | AMCL | 초기 위치 입력 |
| `/robot_ns/cmd_vel` | `geometry_msgs/Twist` | teleop, wall follower, Nav2 | Gazebo diff_drive | 속도 명령 |
| `/robot_ns/tf` | `tf2_msgs/TFMessage` | AMCL, Gazebo, robot_state_publisher 등 | 여러 노드 | 동적 TF |
| `/robot_ns/tf_static` | `tf2_msgs/TFMessage` | robot_state_publisher 등 | 여러 노드 | 정적 TF |

---

## 2. 핵심 frame

| Frame | 역할 |
|---|---|
| `map_robot_ns` | 저장 지도 기준 전역 좌표계 |
| `odom_robot_ns` | odometry 기준 지역 좌표계 |
| `base_footprint` | 로봇 바닥 중심 좌표계 |
| `base_link` | 로봇 본체 좌표계 |
| `base_scan` | LiDAR 센서 좌표계 |
| `camera_link` | 카메라 좌표계 |

---

## 3. 기대 TF chain

```text
map_robot_ns
  -> odom_robot_ns
      -> base_footprint
          -> base_link
              -> base_scan
              -> camera_link
```

발행 주체:

| TF | 발행 주체 | 설명 |
|---|---|---|
| `map_robot_ns -> odom_robot_ns` | AMCL | odom drift를 map 기준으로 보정 |
| `odom_robot_ns -> base_footprint` | Gazebo diff_drive/odometry | 로봇의 상대 이동 |
| `base_footprint -> base_link` | robot_state_publisher | 로봇 모델 내부 고정 관계 |
| `base_link -> base_scan` | robot_state_publisher | LiDAR 장착 위치 |
| `base_link -> camera_link` | robot_state_publisher | 카메라 장착 위치 |

---

## 4. PDF 이름과 현재 이름 대응

| PDF/일반 예시 | 현재 환경 |
|---|---|
| `/map` | `/robot_ns/map` |
| `/scan` | `/robot_ns/scan` |
| `/cmd_vel` | `/robot_ns/cmd_vel` |
| `/tf` | `/robot_ns/tf` |
| `/tf_static` | `/robot_ns/tf_static` |
| `map` | `map_robot_ns` |
| `odom` | `odom_robot_ns` |
| `base_link` | `base_footprint` 또는 `base_link` |
| `my_robot_description` | `lee_robot_description` |

---

## 5. 확인 명령 요약

```bash
ros2 topic echo /robot_ns/map --once
ros2 topic hz /robot_ns/scan
ros2 topic echo /amcl_pose --once
ros2 topic echo /particle_cloud --once
ros2 node info /amcl
```

TF:

```bash
ros2 run tf2_ros tf2_echo map_robot_ns odom_robot_ns \
  --ros-args \
  -r /tf:=/robot_ns/tf \
  -r /tf_static:=/robot_ns/tf_static

ros2 run tf2_ros tf2_echo odom_robot_ns base_footprint \
  --ros-args \
  -r /tf:=/robot_ns/tf \
  -r /tf_static:=/robot_ns/tf_static
```
