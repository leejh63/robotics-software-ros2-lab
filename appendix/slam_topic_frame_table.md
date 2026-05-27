# SLAM Topic / Frame Table

Day 11 SLAM 기준 topic과 frame을 정리한다.

---

## 0. 이 표의 역할

이 문서는 Day 11 SLAM 기준의 빠른 참조표다.

전체 topic/frame/message/action 기준은 [`topic_frame_message_action_master_table.md`](topic_frame_message_action_master_table.md)를 본다. 다른 표들의 역할은 [`table_reference_guide.md`](table_reference_guide.md)를 본다.

---

## 1. Live SLAM topic

| Topic | Type | Publisher | Subscriber | 의미 |
|---|---|---|---|---|
| `/robot_ns/scan` | `sensor_msgs/msg/LaserScan` | Gazebo LiDAR plugin | SLAM Toolbox, RViz2 | LiDAR 거리 데이터 |
| `/robot_ns/odom` | `nav_msgs/msg/Odometry` | Gazebo diff_drive plugin | 확인/디버깅용 | 오도메트리 |
| `/robot_ns/tf` | `tf2_msgs/msg/TFMessage` | Gazebo plugin, robot_state_publisher, SLAM Toolbox | SLAM Toolbox, RViz2 | 동적 TF |
| `/robot_ns/tf_static` | `tf2_msgs/msg/TFMessage` | robot_state_publisher | SLAM Toolbox, RViz2 | 정적 TF |
| `/robot_ns/map` | `nav_msgs/msg/OccupancyGrid` | SLAM Toolbox 또는 map_server | RViz2, map_saver_cli, AMCL/Nav2 | 지도 |
| `/robot_ns/map_updates` | `map_msgs/msg/OccupancyGridUpdate` | SLAM Toolbox | RViz2 등 | 지도 업데이트 |
| `/robot_ns/cmd_vel` | `geometry_msgs/msg/Twist` | teleop/Nav2 | Gazebo diff_drive plugin | 속도 명령 |
| `/clock` | `rosgraph_msgs/msg/Clock` | Gazebo 또는 rosbag play --clock | use_sim_time 노드 | 시뮬레이션 시간 |

---

## 2. Frame tree

SLAM 전:

```text
odom_robot_ns
  -> base_footprint
    -> base_link
      -> base_scan
      -> camera_link
      -> imu_link
      -> wheel_left_link
      -> wheel_right_link
```

SLAM 후:

```text
map_robot_ns
  -> odom_robot_ns
    -> base_footprint
      -> base_link
        -> base_scan
```

---

## 3. Frame 발행 주체

| Transform | 발행 주체 | 설명 |
|---|---|---|
| `odom_robot_ns -> base_footprint` | Gazebo diff_drive plugin | 오도메트리 기준 로봇 위치 |
| `base_footprint -> base_link` | robot_state_publisher | URDF fixed/mobile joint 기반 |
| `base_link -> base_scan` | robot_state_publisher | LiDAR 장착 위치 |
| `map_robot_ns -> odom_robot_ns` | SLAM Toolbox | SLAM이 오도메트리 오차 보정 |

---

## 4. rosbag 차이

이 저장소에는 rosbag 원본 데이터를 포함하지 않는다. rosbag을 사용할 때는 사용자가 직접 준비한 bag 디렉토리를 `$BAG_DIR`로 지정한다.

```bash
export BAG_DIR=/path/to/rosbag_directory
ros2 bag info "$BAG_DIR"
```

rosbag topic 구조는 크게 두 가지로 나눠서 본다.

```text
namespace 있는 bag 예시:
  /robot_ns/scan
  /robot_ns/odom
  /robot_ns/tf
  /robot_ns/tf_static

namespace 없는 bag 예시:
  /scan
  /odom
  /tf
  /tf_static
```

namespace 없는 bag을 현재 `projects/ros2_navigation_lab`의 `/lee` 실행 구조에 맞추려면 topic remap이 필요할 수 있다. 아래 명령은 이 표의 일반 placeholder가 아니라 현재 실행 예시다.

```bash
ros2 bag play "$BAG_DIR" --clock \
  --remap /scan:=/lee/scan \
  --remap /odom:=/lee/odom \
  --remap /tf:=/lee/tf \
  --remap /tf_static:=/lee/tf_static
```

단, topic remap은 `header.frame_id`를 바꾸지 않는다.
