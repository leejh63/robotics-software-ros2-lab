# Nav2 Topic / Frame / Action Table

이 문서는 Day 13 Nav2 실습에서 자주 확인하는 topic, frame, action을 모은 표다.

---

## 1. Topic

| topic | type 후보 | 제공 주체 | 소비 주체 | 의미 |
|---|---|---|---|---|
| `/robot_ns/map` | `nav_msgs/msg/OccupancyGrid` | map_server | global costmap, RViz, AMCL | 저장 지도 |
| `/robot_ns/scan` | `sensor_msgs/msg/LaserScan` | Gazebo laser plugin | AMCL, costmap | LiDAR 거리 데이터 |
| `/robot_ns/odom` | `nav_msgs/msg/Odometry` | Gazebo diff_drive plugin | controller, velocity_smoother | odometry |
| `/robot_ns/tf` | `tf2_msgs/msg/TFMessage` | AMCL, Gazebo, robot_state_publisher | Nav2, RViz | 동적 TF |
| `/robot_ns/tf_static` | `tf2_msgs/msg/TFMessage` | robot_state_publisher | Nav2, RViz | 정적 TF |
| `/amcl_pose` | `geometry_msgs/msg/PoseWithCovarianceStamped` | AMCL | RViz, debug | 추정 pose |
| `/particle_cloud` | `geometry_msgs/msg/PoseArray` | AMCL | RViz | particle 분포 |
| `/initialpose` | `geometry_msgs/msg/PoseWithCovarianceStamped` | RViz/user | AMCL | 초기 위치 지정 |
| `/robot_ns/global_costmap/costmap` | `nav_msgs/msg/OccupancyGrid` | global costmap | RViz, planner | 전역 costmap |
| `/robot_ns/local_costmap/costmap` | `nav_msgs/msg/OccupancyGrid` | local costmap | RViz, controller | 로컬 costmap |
| `/robot_ns/plan` | `nav_msgs/msg/Path` | planner_server | controller, RViz | 전역 경로 |
| `/robot_ns/cmd_vel` | `geometry_msgs/msg/Twist` | controller/velocity_smoother | Gazebo diff_drive plugin | 속도 명령 |

---

## 2. Frame

| frame | 의미 | 주 제공 주체 |
|---|---|---|
| `map_robot_ns` | 저장 지도 기준 전역 좌표계 | map_server/AMCL 기준 |
| `odom_robot_ns` | odom 누적 기준 좌표계 | Gazebo/AMCL 연결 |
| `base_footprint` | 로봇 바닥 중심 | Gazebo diff_drive, robot_state_publisher |
| `base_link` | 로봇 본체 기준 | robot_state_publisher |
| `base_scan` | LiDAR 센서 기준 | robot_state_publisher |
| `camera_link` | 카메라 센서 기준 | robot_state_publisher |

핵심 TF chain:

```text
map_robot_ns -> odom_robot_ns -> base_footprint -> base_link -> base_scan
```

---

## 3. Action

| action | type | server | 의미 |
|---|---|---|---|
| `/robot_ns/navigate_to_pose` | `nav2_msgs/action/NavigateToPose` | bt_navigator | 단일 목표 지점까지 이동 |
| `/robot_ns/navigate_through_poses` | `nav2_msgs/action/NavigateThroughPoses` | bt_navigator | 여러 pose를 순차적으로 경유 |

---

## 4. Lifecycle node

| node | 역할 |
|---|---|
| `/map_server` | map yaml/pgm 로드 및 `/robot_ns/map` 발행 |
| `/amcl` | particle filter localization |
| `/robot_ns/planner_server` | global path 생성 |
| `/robot_ns/controller_server` | path 추종 속도 생성 |
| `/robot_ns/bt_navigator` | NavigateToPose action 처리 |
| `/robot_ns/behavior_server` | recovery behavior 제공 |
| `/robot_ns/smoother_server` | path smoothing |
| `/robot_ns/waypoint_follower` | waypoint 주행 |
| `/robot_ns/velocity_smoother` | velocity smoothing |

---

## 5. 빠른 확인 명령

```bash
ros2 action list | grep navigate
ros2 lifecycle get /robot_ns/planner_server
ros2 topic echo /robot_ns/plan --once
ros2 topic echo /robot_ns/cmd_vel
ros2 run tf2_ros tf2_echo map_robot_ns odom_robot_ns
```

