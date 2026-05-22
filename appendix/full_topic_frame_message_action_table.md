# Appendix - Full Topic / Frame / Message / Action Table

이 문서는 Day 01~13에서 반복적으로 등장한 topic, frame, message, action을 한 장으로 정리한 표다.

---

## 1. Topic 전체표

| Topic | Message 계열 | 주 사용 단계 | Producer | Consumer | 의미 |
|---|---|---|---|---|---|
| `/robot_ns/scan` | `sensor_msgs/LaserScan` | Day 10~13 | Gazebo LiDAR plugin 또는 rosbag | RViz, SLAM Toolbox, AMCL, costmap | LiDAR 거리 데이터 |
| `/robot_ns/odom` | `nav_msgs/Odometry` | Day 10~13 | Gazebo diff_drive plugin | RViz, SLAM/AMCL/Nav2 참고 | 바퀴 기반 odometry |
| `/robot_ns/cmd_vel` | `geometry_msgs/Twist` | Day 10, 13 | teleop, Nav2 controller | Gazebo diff_drive plugin | 로봇 속도 명령 |
| `/robot_ns/map` | `nav_msgs/OccupancyGrid` | Day 11~13 | SLAM Toolbox 또는 map_server | RViz, AMCL, Nav2 costmap | 지도 |
| `/robot_ns/map_updates` | map update 계열 | Day 11 | SLAM Toolbox | RViz/SLAM 관련 | 지도 부분 업데이트 |
| `/robot_ns/tf` | `tf2_msgs/TFMessage` | Day 10~13 | 여러 노드 | 여러 노드 | 동적 TF |
| `/robot_ns/tf_static` | `tf2_msgs/TFMessage` | Day 10~13 | robot_state_publisher 등 | 여러 노드 | 정적 TF |
| `/clock` | `rosgraph_msgs/Clock` | Day 10~13 | Gazebo 또는 rosbag | use_sim_time node | 시뮬레이션 시간 |
| `/initialpose` | `PoseWithCovarianceStamped` | Day 12~13 | RViz 또는 CLI | AMCL | 초기 위치 입력 |
| `/amcl_pose` | `PoseWithCovarianceStamped` | Day 12~13 | AMCL | RViz, 확인용 | AMCL 추정 pose |
| `/particle_cloud` | `nav2_msgs/ParticleCloud` 또는 PoseArray 계열 | Day 12~13 | AMCL | RViz | particle 후보군 |
| `/robot_ns/global_costmap/costmap` | `nav_msgs/OccupancyGrid` | Day 13 | Nav2 global costmap | planner/RViz | global planning 비용 지도 |
| `/robot_ns/local_costmap/costmap` | `nav_msgs/OccupancyGrid` | Day 13 | Nav2 local costmap | controller/RViz | local control 비용 지도 |
| `/robot_ns/plan` | `nav_msgs/Path` | Day 13 | planner_server | RViz, controller | global path |
| `/robot_ns/local_plan` | `nav_msgs/Path` 계열 | Day 13 | controller_server | RViz | local trajectory/path |
| `/clicked_point` | `geometry_msgs/PointStamped` | Day 13 | RViz | 사용자가 확인 | RViz publish point |
| `/robot_ns/image_raw` | `sensor_msgs/Image` | Day 06~10 | camera driver/plugin | OpenCV/YOLO/RViz | 카메라 이미지 |
| `/robot_ns/imu` | `sensor_msgs/Imu` | Day 09~10 | Gazebo IMU plugin | RViz/필터/확인용 | IMU 데이터 |
| `/robot_ns/joint_states` | `sensor_msgs/JointState` | Day 10 | Gazebo/robot state | robot_state_publisher | joint 상태 |

---

## 2. Frame 전체표

| Frame | 주 사용 단계 | 의미 | 주 생성/사용 주체 |
|---|---|---|---|
| `map_robot_ns` | Day 11~13 | 지도 기준 전역 좌표계 | SLAM Toolbox, map_server, AMCL, Nav2 |
| `odom_robot_ns` | Day 10~13 | odometry 기준 지역 좌표계 | Gazebo odom, SLAM/AMCL 보정 대상 |
| `base_footprint` | Day 10~13 | 로봇 바닥 중심 | odometry/URDF/TF |
| `base_link` | Day 10~13 | 로봇 본체 중심 | URDF/TF |
| `base_scan` | Day 10~13 | LiDAR 센서 좌표계 | URDF/robot_state_publisher |
| `camera_link` | Day 06~10 | 카메라 좌표계 | URDF/camera pipeline |
| `imu_link` | Day 09~10 | IMU 좌표계 | URDF/IMU plugin |

정상 navigation 기준 TF chain:

```text
map_robot_ns -> odom_robot_ns -> base_footprint -> base_link -> base_scan
```

URDF 구성에 따라 `base_link`가 생략되거나 `base_footprint -> base_scan`처럼 더 단순하게 보일 수도 있다. 실제 확인은 `tf2_echo`와 `view_frames`를 기준으로 한다.

---

## 3. Action 전체표

| Action | Type | 주 사용 단계 | 역할 |
|---|---|---|---|
| `/robot_ns/navigate_to_pose` | `nav2_msgs/action/NavigateToPose` | Day 13 | 단일 goal pose로 주행 |
| `/robot_ns/navigate_through_poses` | `nav2_msgs/action/NavigateThroughPoses` | Day 13 | 여러 goal pose 순차 주행 |
| `/robot_ns/compute_path_to_pose` | `nav2_msgs/action/ComputePathToPose` | Day 13 | 목표까지 global path 계산 |
| `/robot_ns/follow_path` | `nav2_msgs/action/FollowPath` | Day 13 | path 추종 |

실습에서 직접 다룬 핵심은 `/robot_ns/navigate_to_pose`다.

---

## 4. Service / CLI로 자주 보는 것

| 용도 | 예시 | 설명 |
|---|---|---|
| map 저장 | `map_saver_cli` | `/robot_ns/map`을 `.pgm/.yaml`로 저장 |
| lifecycle 전환 | `ros2 lifecycle set` | map_server/amcl/nav2 node 활성화 확인 |
| spawn | `spawn_entity.py` | Gazebo에 robot entity 생성 |
| parameter 확인 | `ros2 param get` | controller_plugins, use_sim_time 등 확인 |

---

## 5. Message와 frame_id의 관계

ROS2 sensor/navigation 메시지는 대개 header를 가진다.

```text
header.stamp     메시지가 생성된 시간
header.frame_id  이 데이터가 어떤 좌표계 기준인지
```

예시:

```text
/robot_ns/scan topic의 LaserScan.header.frame_id = base_scan
/robot_ns/map topic의 OccupancyGrid.header.frame_id = map_robot_ns
NavigateToPose goal의 header.frame_id = map_robot_ns
```

즉, topic 이름과 frame_id는 같은 것이 아니다.

---

## 6. 단계별 최소 정상 조건

| 단계 | 최소 정상 조건 |
|---|---|
| Gazebo | `/robot_ns/scan`, `/robot_ns/odom`, `/robot_ns/tf`, `/robot_ns/cmd_vel` subscriber 확인 |
| SLAM | `/robot_ns/scan` 수신, TF chain 연결, `/robot_ns/map` 발행 |
| Map Save | `/robot_ns/map` 존재, map_saver remap/저장 경로 정상 |
| AMCL | `/robot_ns/map`, `/robot_ns/scan`, initialpose, `map_robot_ns->odom_robot_ns` 발행 |
| Nav2 | lifecycle active, costmap 발행, `/robot_ns/navigate_to_pose` action server, `/robot_ns/cmd_vel` 발행 |
