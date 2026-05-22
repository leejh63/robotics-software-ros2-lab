# AMCL Topic / Frame 표

이 문서는 AMCL에서 자주 확인하는 topic과 frame을 빠르게 정리한 표다. AMCL 관련 topic은 launch namespace 방식에 따라 root에 있을 수도 있고 `/robot_ns` 아래에 있을 수도 있다. 실제 실행 전에는 항상 `ros2 topic list`와 `ros2 node info`로 현재 graph를 확인한다.

관련 상세 설명: [`amcl_namespace_cases.md`](amcl_namespace_cases.md)

---

## 0. 이 표의 역할

이 문서는 Day 12 AMCL 기준의 빠른 참조표다.

AMCL topic namespace case는 이 문서와 [`amcl_namespace_cases.md`](amcl_namespace_cases.md)를 함께 본다. 전체 기준표는 [`topic_frame_message_action_master_table.md`](topic_frame_message_action_master_table.md)를 우선한다.

---

## 1. 핵심 topic

| 논리 역할 | Root AMCL case | Namespaced AMCL case | Message | Producer | Consumer | 의미 |
|---|---|---|---|---|---|---|
| map | `/robot_ns/map` | `/robot_ns/map` | `nav_msgs/OccupancyGrid` | `map_server` | AMCL, RViz, Nav2 costmap | 저장 지도 |
| scan | `/robot_ns/scan` | `/robot_ns/scan` | `sensor_msgs/LaserScan` | Gazebo LiDAR plugin | AMCL, RViz, costmap | 현재 LiDAR 거리 |
| initial pose | `/initialpose` | `/robot_ns/initialpose` | `geometry_msgs/PoseWithCovarianceStamped` | RViz 또는 CLI | AMCL | 초기 위치 입력 |
| estimated pose | `/amcl_pose` | `/robot_ns/amcl_pose` | `geometry_msgs/PoseWithCovarianceStamped` | AMCL | RViz, 확인용 | map 기준 추정 pose |
| particle cloud | `/particle_cloud` | `/robot_ns/particle_cloud` | `nav2_msgs/ParticleCloud` | AMCL | RViz | 위치 후보 particle |
| velocity command | `/robot_ns/cmd_vel` | `/robot_ns/cmd_vel` | `geometry_msgs/Twist` | teleop, wall follower, Nav2 | Gazebo diff_drive | 속도 명령 |
| dynamic TF | `/robot_ns/tf` | `/robot_ns/tf` | `tf2_msgs/TFMessage` | AMCL, Gazebo, robot_state_publisher 등 | 여러 노드 | 동적 TF |
| static TF | `/robot_ns/tf_static` | `/robot_ns/tf_static` | `tf2_msgs/TFMessage` | robot_state_publisher 등 | 여러 노드 | 정적 TF |

Root AMCL case와 namespaced AMCL case 중 어느 쪽인지는 node 이름으로 먼저 판단한다.

```bash
ros2 node list | sort | grep amcl
```

```text
/amcl             -> root AMCL case
/robot_ns/amcl    -> namespaced AMCL case
```

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

Topic namespace와 frame 이름은 별개다. 예를 들어 `/robot_ns/scan` topic으로 메시지가 들어와도, 메시지 내부 `header.frame_id`는 보통 `base_scan`이다.

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

## 4. 일반 예시와 현재 이름 대응

| 일반 예시 | 현재 문서 기준 |
|---|---|
| `/map` | `/robot_ns/map` |
| `/scan` | `/robot_ns/scan` |
| `/cmd_vel` | `/robot_ns/cmd_vel` |
| `/tf` | `/robot_ns/tf` |
| `/tf_static` | `/robot_ns/tf_static` |
| `/initialpose` | `/initialpose` 또는 `/robot_ns/initialpose` |
| `/amcl_pose` | `/amcl_pose` 또는 `/robot_ns/amcl_pose` |
| `/particle_cloud` | `/particle_cloud` 또는 `/robot_ns/particle_cloud` |
| `map` | `map_robot_ns` |
| `odom` | `odom_robot_ns` |
| `base_link` | `base_footprint` 또는 `base_link` |
| `my_robot_description` | `lee_robot_description` |

---

## 5. 확인 명령 요약

공통 입력 확인:

```bash
ros2 topic echo /robot_ns/map --once
ros2 topic hz /robot_ns/scan
ros2 node list | sort | grep amcl
ros2 topic list | sort | grep -E 'initialpose|amcl_pose|particle_cloud'
```

Root AMCL case:

```bash
ros2 node info /amcl
ros2 topic echo /amcl_pose --once
ros2 topic echo /particle_cloud --once
```

Namespaced AMCL case:

```bash
ros2 node info /robot_ns/amcl
ros2 topic echo /robot_ns/amcl_pose --once
ros2 topic echo /robot_ns/particle_cloud --once
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
