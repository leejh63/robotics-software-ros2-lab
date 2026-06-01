# 실행 환경 기준

이 문서는 학습 정리본에서 반복적으로 등장하는 실행 환경 기준값을 한 곳에 모은 것이다.

문서의 목적은 “정답 환경”을 강제하는 것이 아니라, 명령어 예시를 해석할 때 필요한 기준값을 제공하는 것이다.

---

## 1. 기본 작업 경로

```bash
cd $ROS2_WS
source install/setup.bash
```

이 저장소의 예시 workspace:

```text
$ROS2_WS
```

주요 패키지:

```text
lee_robot_description
ros2_topic_examples
ros2_cpp_examples
ros2_foundation_interfaces
ros2_service_examples
ros2_action_examples
ros2_camera_examples
ros2_launch_examples
ros2_tf_examples
pid_arm_lab
```

원본 실습명으로 남아 있던 `camera_pkg`, `my_if`, `tf_pkg_example` 등은 현재 정리본에서 각각 `ros2_camera_examples`, `ros2_foundation_interfaces`, `ros2_tf_examples`처럼 역할 기준 패키지명으로 분리했다.

---

## 2. Navigation 기준 패키지

```text
package: lee_robot_description
```

주요 파일:

```text
lee_robot_description/urdf/turtlebot.xacro
lee_robot_description/urdf/turtlebot_gaze.xacro
lee_robot_description/launch/gazebo.launch.py
lee_robot_description/launch/slam.launch.py
lee_robot_description/launch/localization.launch.py
lee_robot_description/launch/nav2.launch.py
lee_robot_description/launch/nav2_navigation.launch.py
lee_robot_description/config/slam_param.yaml
lee_robot_description/config/amcl_param.yaml
lee_robot_description/config/nav2_params.yaml
lee_robot_description/worlds/slam.world
lee_robot_description/worlds/robot_ns_world.world
```

---

## 3. 주요 namespace/topic/action

| 구분 | 이름 |
|---|---|
| namespace | `/robot_ns` |
| scan topic | `/robot_ns/scan` |
| odom topic | `/robot_ns/odom` |
| cmd_vel topic | `/robot_ns/cmd_vel` |
| map topic | `/robot_ns/map` |
| dynamic TF topic | `/robot_ns/tf` |
| static TF topic | `/robot_ns/tf_static` |
| Nav2 action | `/robot_ns/navigate_to_pose` |
| plan topic | `/robot_ns/plan` |
| local costmap | `/robot_ns/local_costmap/costmap` |
| global costmap | `/robot_ns/global_costmap/costmap` |

주의:

```text
/robot_ns는 topic/action/node 이름 공간에 가깝다.
frame 이름 앞에 자동으로 /robot_ns가 붙는 것은 아니다.
```

---

## 4. 주요 frame

| frame | 의미 |
|---|---|
| `map_robot_ns` | 저장 지도 기준 전역 좌표계 |
| `odom_robot_ns` | odometry 기준 지역 좌표계 |
| `base_footprint` | 로봇 바닥 중심 좌표계 |
| `base_link` | 로봇 본체 좌표계 |
| `base_scan` | LiDAR 센서 좌표계 |
| `camera_link` | 카메라 센서 좌표계 |

핵심 TF chain:

```text
map_robot_ns -> odom_robot_ns -> base_footprint -> base_link -> base_scan
```

SLAM/AMCL/Nav2가 정상 동작하려면 위 chain이 끊기지 않아야 한다.

---

## 5. world-map 조합

문서에서 반복적으로 기준으로 삼는 조합:

```text
slam.world       <-> slam_map.yaml
lee_world.world  <-> room_map.yaml
```

주의:

```text
맵 파일은 world와 맞아야 한다.
다른 world에서 저장한 map을 사용하면 AMCL particle이 잘 수렴하지 않거나 Nav2 경로가 이상하게 나올 수 있다.
```

---

## 6. 실습 실행 기본 구조

### Gazebo + robot 확인

```bash
cd $ROS2_WS
source install/setup.bash
ros2 launch lee_robot_description gazebo.launch.py
```

### SLAM

```bash
cd $ROS2_WS
source install/setup.bash
ros2 launch lee_robot_description slam.launch.py
```

### AMCL/localization

```bash
cd $ROS2_WS
source install/setup.bash
ros2 launch lee_robot_description localization.launch.py
```

### Nav2 통합 실행

```bash
cd $ROS2_WS
source install/setup.bash
ros2 launch lee_robot_description nav2.launch.py
```

### Nav2 navigation

```bash
cd $ROS2_WS
source install/setup.bash
ros2 launch lee_robot_description nav2_navigation.launch.py
```

---

## 7. 기본 진단 명령

```bash
ros2 node list | sort
ros2 topic list | sort
ros2 action list | sort
ros2 service list | sort
```

topic 확인:

```bash
ros2 topic echo /robot_ns/scan --once
ros2 topic echo /robot_ns/odom --once
ros2 topic echo /robot_ns/map --once
```

TF 확인:

```bash
ros2 run tf2_ros tf2_echo map_robot_ns odom_robot_ns
ros2 run tf2_ros tf2_echo odom_robot_ns base_footprint
ros2 run tf2_ros tf2_echo base_footprint base_scan
```

Nav2 action 확인:

```bash
ros2 action list | grep navigate
ros2 action info /robot_ns/navigate_to_pose
```

lifecycle 확인:

```bash
ros2 lifecycle nodes
ros2 lifecycle get /robot_ns/map_server
ros2 lifecycle get /robot_ns/amcl
ros2 lifecycle get /robot_ns/planner_server
ros2 lifecycle get /robot_ns/controller_server
```

---

## 8. 가장 중요한 주의사항

```text
topic remap은 topic 이름만 바꾼다.
message 안의 header.frame_id는 자동으로 바뀌지 않는다.
```

예를 들어:

```bash
ros2 bag play old_bag --remap /scan:=/robot_ns/scan
```

이렇게 해도 LaserScan 메시지 안의 `header.frame_id`가 자동으로 `base_scan`이나 다른 frame 이름으로 바뀌는 것은 아니다.

따라서 rosbag을 사용할 때는 아래를 같이 확인해야 한다.

```bash
ros2 topic echo /robot_ns/scan --once | grep frame_id
ros2 topic echo /robot_ns/odom --once | grep frame_id -A 2
```
