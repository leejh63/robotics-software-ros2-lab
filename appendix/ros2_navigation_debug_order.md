# ROS2 Navigation 디버깅 순서

이 문서는 문제가 생겼을 때 확인 순서를 정리한 것이다.

가장 중요한 원칙:

```text
화면에 안 보이는 문제를 RViz 설정부터 의심하지 말고,
ROS graph -> topic -> message -> frame -> lifecycle -> parameter 순서로 본다.
```

---

## 1. 먼저 확인할 것

```bash
ros2 node list | sort
ros2 topic list | sort
ros2 action list | sort
ros2 service list | sort
```

질문:

```text
기대한 node가 떠 있는가?
기대한 topic이 있는가?
기대한 action server가 있는가?
namespace가 /robot_ns로 붙어 있는가?
```

---

## 2. topic이 있는지와 데이터가 나오는지는 다르다

```bash
ros2 topic info /robot_ns/scan
ros2 topic echo /robot_ns/scan --once
ros2 topic hz /robot_ns/scan
```

해석:

```text
topic list에 있음      -> 이름은 존재한다.
topic echo가 됨       -> 실제 메시지가 흐른다.
topic hz가 안정적임   -> 주기적으로 발행된다.
```

---

## 3. message type 확인

```bash
ros2 topic info /robot_ns/scan
ros2 interface show sensor_msgs/msg/LaserScan
```

Nav2/SLAM/AMCL은 message type이 맞아야 한다.

| topic | 주로 기대하는 type |
|---|---|
| `/robot_ns/scan` | `sensor_msgs/msg/LaserScan` |
| `/robot_ns/odom` | `nav_msgs/msg/Odometry` |
| `/robot_ns/map` | `nav_msgs/msg/OccupancyGrid` |
| `/robot_ns/cmd_vel` | `geometry_msgs/msg/Twist` |
| `/robot_ns/plan` | `nav_msgs/msg/Path` |

---

## 4. frame_id 확인

```bash
ros2 topic echo /robot_ns/scan --once | grep frame_id
ros2 topic echo /robot_ns/map --once | grep frame_id
```

주의:

```text
topic 이름과 frame_id는 다르다.
remap으로 topic 이름을 바꿔도 frame_id는 자동으로 바뀌지 않는다.
```

---

## 5. TF chain 확인

```bash
ros2 run tf2_ros tf2_echo odom_robot_ns base_footprint
ros2 run tf2_ros tf2_echo map_robot_ns odom_robot_ns
ros2 run tf2_tools view_frames
```

해석:

```text
odom_robot_ns -> base_footprint
  Gazebo odom/robot_state_publisher 쪽 문제를 확인한다.

map_robot_ns -> odom_robot_ns
  SLAM 또는 AMCL 쪽 문제를 확인한다.

base_footprint -> base_scan
  URDF/Xacro/sensor frame 문제를 확인한다.
```

---

## 6. lifecycle 확인

Nav2 관련 node는 떠 있어도 inactive면 실제 기능을 하지 않을 수 있다.

```bash
ros2 lifecycle nodes
ros2 lifecycle get /robot_ns/map_server
ros2 lifecycle get /robot_ns/amcl
ros2 lifecycle get /robot_ns/planner_server
ros2 lifecycle get /robot_ns/controller_server
ros2 lifecycle get /robot_ns/bt_navigator
```

정상 기대:

```text
active
```

---

## 7. parameter 확인

```bash
ros2 param get /robot_ns/amcl base_frame_id
ros2 param get /robot_ns/amcl odom_frame_id
ros2 param get /robot_ns/amcl global_frame_id
```

Nav2 controller 확인:

```bash
ros2 param get /robot_ns/controller_server controller_plugins
ros2 param get /robot_ns/controller_server goal_checker_plugins
ros2 param get /robot_ns/controller_server progress_checker_plugin
```

parameter가 예상과 다르면 launch/config YAML이 제대로 적용되지 않았을 수 있다.

---

## 8. RViz 문제인지 ROS 문제인지 구분

RViz에 안 보인다고 해서 ROS graph가 망가진 것은 아니다.

먼저 CLI로 확인한다.

```bash
ros2 topic echo /robot_ns/map --once
ros2 topic echo /amcl_pose --once
ros2 action info /robot_ns/navigate_to_pose
```

CLI는 정상인데 RViz만 이상하면:

```text
- Fixed Frame 설정 확인
- display topic 이름 확인
- namespace 확인
- Goal tool action namespace 확인
- QoS 설정 확인
```

---

## 9. Nav2 goal이 실패할 때 확인 순서

```text
1. /robot_ns/navigate_to_pose action server가 있는가?
2. goal frame_id가 map_robot_ns인가?
3. map_robot_ns -> odom_robot_ns -> base_footprint TF가 있는가?
4. /robot_ns/map이 발행되는가?
5. global/local costmap이 발행되는가?
6. /robot_ns/plan이 발행되는가?
7. /robot_ns/cmd_vel이 발행되는가?
8. Gazebo diff_drive plugin이 /robot_ns/cmd_vel을 받고 있는가?
```

---

## 10. 문제를 기록할 때 남길 정보

문제를 다음에 다시 분석하려면 아래를 남긴다.

```bash
ros2 node list | sort
ros2 topic list | sort
ros2 action list | sort
ros2 lifecycle nodes
ros2 topic echo /robot_ns/scan --once
ros2 topic echo /robot_ns/odom --once
ros2 topic echo /robot_ns/map --once
ros2 run tf2_ros tf2_echo map_robot_ns odom_robot_ns
ros2 run tf2_ros tf2_echo odom_robot_ns base_footprint
```

추가로 캡처하면 좋은 것:

```text
- 실행한 launch 명령어
- 터미널 에러 로그
- RViz Fixed Frame 설정
- map/world 조합
- 사용한 bag 이름과 remap 명령어
```
