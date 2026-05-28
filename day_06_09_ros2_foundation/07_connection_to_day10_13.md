# 07. Day 06~09 기본기가 Day 10~13에 연결되는 방식

## 한 줄 결론

Day 10~13의 Gazebo, SLAM, AMCL, Nav2는 이름만 거창해 보이지만, 디버깅의 대부분은 Day 06~09의 ROS2 기본기에서 나온다.

---

## 1. 전체 연결도

```text
Day 06 workspace/package/node/topic
  -> 모든 ROS2 패키지 실행과 확인의 기본

Day 07 pub/sub/service/action/interface
  -> sensor topic, lifecycle service, NavigateToPose action 이해

Day 08 launch/parameter/custom msg/debug
  -> Gazebo/SLAM/AMCL/Nav2 launch와 YAML 설정 이해

Day 09 TF2/sensor/rosbag
  -> map/odom/base/sensor frame, offline replay 이해

Day 10 Gazebo/URDF/Xacro
  -> simulated robot, sensor plugin, robot_state_publisher

Day 11 SLAM
  -> /scan + /odom + /tf로 map 생성

Day 12 AMCL
  -> 저장 map + /scan + /tf로 localization

Day 13 Nav2
  -> localization + costmap + planner/controller + /cmd_vel
```

---

## 2. Day 06의 이름 구분이 뒤쪽에서 왜 중요한가

Day 10~13에서는 아래 이름들이 계속 나온다.

```text
package      : lee_robot_description, nav2_bringup, slam_toolbox
launch file  : nav2.launch.py, slam.launch.py, navigation_launch.py
node         : map_server, amcl, controller_server, planner_server
namespace    : /robot_ns
topic        : /robot_ns/scan, /robot_ns/odom, /robot_ns/map, /robot_ns/cmd_vel
frame        : map, odom, base_link, base_scan
message type : LaserScan, Odometry, OccupancyGrid, Twist
```

이 구분이 안 되면 다음 문제를 정확히 설명하기 어렵다.

```text
노드는 떠 있는데 topic이 없다.
topic은 있는데 type이 다르다.
RViz에 topic을 추가했는데 Fixed Frame 오류가 난다.
Nav2 action 이름이 /navigate_to_pose인지 /robot_ns/navigate_to_pose인지 헷갈린다.
```

---

## 3. Topic, Service, Action 연결

Day 10~13의 통신 구조는 아래처럼 나뉜다.

| 구분 | 예시 | 역할 |
|---|---|---|
| Topic | `/robot_ns/scan` | LiDAR scan stream |
| Topic | `/robot_ns/odom` | odometry stream |
| Topic | `/tf`, `/tf_static` | frame transform stream |
| Topic | `/robot_ns/cmd_vel` | controller가 내보내는 속도 명령 |
| Service | lifecycle configure/activate | node 상태 전환 |
| Service | map save/load, clear costmap | 한 번 요청하고 응답 |
| Action | `/robot_ns/navigate_to_pose` | 목표 지점으로 이동 |

Nav2 Goal은 topic publish가 아니다. `NavigateToPose` action이다. 그래서 `ros2 topic list`만 보면 부족하고 `ros2 action list`도 봐야 한다.

---

## 4. Launch와 Parameter 연결

Day 10~13은 거의 launch 중심으로 실행된다.

```text
Gazebo 실행
robot_state_publisher 실행
spawn_entity 실행
slam_toolbox 실행
map_server 실행
amcl 실행
Nav2 planner/controller/bt_navigator 실행
RViz 실행
```

각 노드는 parameter YAML을 많이 사용한다. 특히 Nav2는 parameter가 맞지 않으면 node가 떠도 내부 plugin 설정이 비어 있을 수 있다.

확인 예시:

```bash
ros2 param get /controller_server controller_plugins
ros2 param get /controller_server goal_checker_plugins
ros2 param get /controller_server progress_checker_plugin
```

parameter 확인은 “실행됐다”와 “제대로 설정됐다”를 구분하기 위한 도구다.

---

## 5. TF 연결

Day 09 실습의 TF tree:

```text
map
└── odom
    └── base_link
        └── camera_link
            └── object_person_example_0
```

Day 10~13에서 필요한 TF tree:

```text
map
└── odom
    └── base_footprint 또는 base_link
        ├── base_scan 또는 lidar frame
        └── camera frame
```

각 구간의 의미:

| transform | 누가 발행하는가 | 의미 |
|---|---|---|
| `map -> odom` | SLAM 또는 AMCL | 지도 기준 보정 |
| `odom -> base` | Gazebo odom plugin 또는 odom publisher | 로봇 이동 추정 |
| `base -> sensor` | robot_state_publisher/static TF | 센서 장착 위치 |

SLAM/AMCL/Nav2 문제는 대개 이 chain 중 하나가 끊어졌을 때 발생한다.

---

## 6. Sensor message 연결

Day 09에서 Image header를 봤다면, Day 10~13에서는 LaserScan/Odometry header를 봐야 한다.

| message | 중요한 필드 | 의미 |
|---|---|---|
| `sensor_msgs/Image` | `header.frame_id` | 이미지 센서 frame |
| `sensor_msgs/LaserScan` | `header.frame_id`, `angle_min`, `angle_increment`, `ranges` | LiDAR frame과 각도별 거리 |
| `nav_msgs/Odometry` | `header.frame_id`, `child_frame_id`, pose/twist | odom frame 기준 robot 상태 |
| `nav_msgs/OccupancyGrid` | `header.frame_id`, resolution, origin, data | map frame 기준 점유 격자 |

LaserScan의 `ranges[index]`는 그냥 “몇 번째 거리값”이 아니다.

```text
angle = angle_min + index * angle_increment
```

이 계산을 통해 해당 거리값이 어느 방향인지 알 수 있다.

---

## 7. rosbag 연결

Day 11의 offline SLAM은 rosbag 개념과 직접 연결된다.

```text
record bag
  -> /scan, /odom, /tf, /tf_static 기록
play bag
  -> slam_toolbox가 같은 데이터를 다시 처리
map 생성 재현
```

bag에 `/scan`만 있고 `/tf`가 없으면 scan이 어느 frame에서 들어온 것인지 알고리즘이 해석하지 못할 수 있다.

---

## 8. 디버깅 순서

큰 시스템이 안 될 때는 아래 순서로 본다.

```text
1. workspace build/source 확인
2. package/executable 확인
3. node list 확인
4. topic list/type 확인
5. service/action list 확인
6. parameter 적용 확인
7. TF tree 확인
8. lifecycle state 확인
9. RViz Fixed Frame/display 확인
10. 알고리즘 파라미터 튜닝
```

처음부터 SLAM/AMCL/Nav2 알고리즘 자체를 의심하면 시간이 오래 걸린다. 대부분은 이름, type, namespace, parameter, TF, lifecycle에서 먼저 걸린다.

---

## 9. 흔한 착각 정리

| 착각 | 실제 |
|---|---|
| topic이 보이면 알고리즘이 무조건 쓴다 | topic type, QoS, timestamp, frame이 맞아야 한다 |
| RViz에서 안 보이면 topic이 없다 | Fixed Frame 또는 TF 문제일 수 있다 |
| Nav2 Goal은 topic이다 | `NavigateToPose` action이다 |
| `/map` topic과 `map` frame은 같다 | topic 이름과 frame 이름은 다르다 |
| node가 active처럼 보여도 parameter가 맞다 | `ros2 param get`으로 확인해야 한다 |
| launch는 그냥 여러 명령어를 적은 파일이다 | node name, parameter, condition, namespace를 선언하는 실행 구성이다 |
