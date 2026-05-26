# Architecture

이 문서는 `projects/ros2_navigation_lab`의 실행 구조를 정리합니다.

패키지는 표준 ROS2 Navigation 패키지를 하나의 simulation workflow로 연결합니다. 기본 namespace와 frame 구조는 아래와 같습니다.

```text
namespace: /lee
frame chain: map_lee -> odom_lee -> base_footprint
```

---

## Runtime Data Flow

```text
Gazebo
  -> LiDAR plugin을 통해 /lee/scan publish
  -> differential drive plugin을 통해 /lee/odom publish
  -> /lee/cmd_vel을 받아 로봇 속도 제어

robot_state_publisher
  -> xacro에서 생성된 robot_description 사용
  -> /lee/tf, /lee/tf_static에 robot link transform publish

slam_toolbox
  -> /lee/scan과 TF 사용
  -> mapping 중 /lee/map과 map 관련 update publish
  -> SLAM 중 map_lee -> odom_lee 보정 제공

nav2_map_server
  -> 저장된 map yaml/pgm pair load
  -> /lee/map publish

nav2_amcl
  -> /lee/scan, /lee/map, TF 사용
  -> /amcl_pose와 /particle_cloud publish
  -> localization 중 map_lee -> odom_lee 보정 제공

Nav2
  -> map, costmap, TF, odometry, goal 사용
  -> global path와 local control command 계산
  -> /lee/cmd_vel publish
```

---

## Launch 파일 역할

| Launch file | 역할 |
|---|---|
| `display.launch.py` | URDF/Xacro 시각화 확인 |
| `gazebo.launch.py` | Gazebo simulation, robot spawn, optional RViz, optional wall follower |
| `slam.launch.py` | Gazebo + `slam_toolbox` mapping flow |
| `gazebo_slam.launch.py` | `slam.launch.py`를 포함하는 SLAM entrypoint |
| `localization.launch.py` | Gazebo + map server + AMCL + lifecycle manager + RViz |
| `nav2_navigation.launch.py` | Localization이 실행 중일 때 Nav2 stack만 실행 |
| `nav2.launch.py` | Localization + Nav2 stack 통합 실행 |

---

## Namespace Boundary

`/lee`는 simulation과 Nav2 workflow에서 사용하는 robot namespace입니다. 현재 구성은 완전히 parameterized된 multi-robot namespace template이 아닙니다.

아래 값들은 launch, URDF, RViz, parameter 파일에 서로 연결되어 있습니다.

```text
/lee
map_lee
odom_lee
base_footprint
/lee/scan
/lee/odom
/lee/cmd_vel
```

`namespace:=...`만 바꾸면 전체 구성이 자동으로 바뀌지 않습니다. namespace를 바꿀 때는 URDF plugin namespace, Nav2 parameter, RViz display, topic remap, TF frame 가정을 함께 확인해야 합니다.
