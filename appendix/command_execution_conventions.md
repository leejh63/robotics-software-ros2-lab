# 명령어 실행 규칙

이 문서는 저장소 안의 명령어 예시를 실행할 때 먼저 확인해야 하는 규칙을 정리한다.

현재 `projects/ros2_navigation_lab`의 실제 기본 실행값은 `/lee`, `map_lee`, `odom_lee`다. 반면 `/robot_ns`, `map_robot_ns`, `odom_robot_ns`는 여러 문서에서 namespace/frame 개념을 설명하기 위해 쓰는 일반 예시다.

---

## 1. 기본 전제

명령어 예시는 ROS2 Humble 기준이다.

대부분의 명령은 아래 준비가 되어 있다는 전제로 작성되어 있다.

```bash
cd $ROS2_WS
source /opt/ros/humble/setup.bash
source install/setup.bash
```

빌드 직후 또는 새 터미널을 열었을 때는 반드시 `source install/setup.bash`를 다시 실행한다.

---

## 2. 실제 실행값과 일반 예시 구분

| 구분 | 현재 실행 예시 | 일반 설명용 예시 | 의미 |
|---|---|---|---|
| namespace | `/lee` | `/robot_ns` | topic/node/action 이름 앞에 붙는 구분자 |
| map frame | `map_lee` | `map_robot_ns` | 지도 기준 TF frame |
| odom frame | `odom_lee` | `odom_robot_ns` | odometry 기준 TF frame |
| package name | `lee_robot_description` | 동일 | `ros2 launch`에서 사용하는 패키지명 |

중요한 기준:

```text
복사해서 실행하는 명령어:
  /lee, map_lee, odom_lee를 우선 사용한다.

개념 설명 문서:
  /robot_ns, map_robot_ns, odom_robot_ns를 placeholder로 사용할 수 있다.

전체 일괄 치환 금지:
  /robot_ns는 설명용 placeholder로 필요한 곳이 있다.
```

---

## 3. 명령어 블록 읽는 법

문서의 명령어 블록은 세 가지로 나뉜다.

| 구분 | 의미 | 실행 전 할 일 |
|---|---|---|
| 실제 실행 명령 | 현재 프로젝트 기본값 기준으로 바로 실행 가능한 형태 | workspace와 source 상태 확인 |
| placeholder 포함 명령 | `<bag_dir>`, `$ROS2_WS`, `/robot_ns` 같은 값을 포함 | 본인 환경 값으로 바꾼 뒤 실행 |
| 진단 명령 | 상태 확인용 명령 | 출력 결과를 보고 다음 단계 판단 |

예를 들어 현재 프로젝트의 실제 rosbag replay 예시는 아래처럼 `/lee` 기준으로 쓴다.

```bash
ros2 bag play <bag_dir> --clock \
  --remap /scan:=/lee/scan
```

반면 아래는 일반 설명용 예시다.

```bash
ros2 bag play <bag_dir> --clock \
  --remap /scan:=/robot_ns/scan
```

`<bag_dir>`은 실제 bag 디렉터리로 바꾸고, topic 이름은 항상 `ros2 topic list`로 확인한다.

---

## 4. 자주 쓰는 이름 구분

아래 이름들은 서로 다른 개념이다.

| 이름 | 현재 실행 예시 | 의미 |
|---|---|---|
| package name | `lee_robot_description` | `ros2 launch`, `ros2 pkg prefix`에서 쓰는 ROS2 패키지명 |
| namespace | `lee` | topic/node/action 이름 앞에 붙는 구분자 |
| topic name | `/lee/scan` | 실제 데이터가 흐르는 통신 채널 |
| frame name | `map_lee`, `odom_lee`, `base_footprint`, `base_scan` | TF tree에서 사용하는 좌표계 이름 |
| local path | `$ROS2_WS`, `$ROS2_WORK_DIR` | 파일 시스템 경로 |

`lee_robot_description`은 패키지명이고, `/lee`는 namespace다. 둘을 섞으면 실행 명령이 깨진다.

---

## 5. 실제 실행 전 확인 명령

패키지가 보이는지 확인한다.

```bash
ros2 pkg list | grep lee_robot_description
```

launch 파일 인자를 확인한다.

```bash
ros2 launch lee_robot_description gazebo.launch.py --show-args
ros2 launch lee_robot_description slam.launch.py --show-args
ros2 launch lee_robot_description localization.launch.py --show-args
ros2 launch lee_robot_description nav2.launch.py --show-args
ros2 launch lee_robot_description nav2_navigation.launch.py --show-args
```

현재 topic 이름이 namespace를 쓰는지 확인한다.

```bash
ros2 topic list | sort | grep -E 'lee|scan|odom|tf|map|cmd_vel|amcl|particle|initialpose'
```

현재 node 이름이 namespace를 쓰는지 확인한다.

```bash
ros2 node list | sort | grep -E 'map_server|amcl|planner|controller|bt_navigator|costmap|lifecycle'
```

---

## 6. namespace가 붙는 경우와 안 붙는 경우

현재 프로젝트의 센서/지도/Nav2 관련 주요 topic은 대체로 아래 형태를 기준으로 본다.

```text
/lee/scan
/lee/odom
/lee/tf
/lee/cmd_vel
/lee/navigate_to_pose
/lee/map
```

하지만 `localization.launch.py`에서 `map_server`와 `amcl` node 이름은 root namespace로 보일 수 있다.

```text
/map_server
/amcl
/amcl_pose
/particle_cloud
/initialpose
```

또는 launch 구조를 바꾸면 아래처럼 namespace가 붙을 수도 있다.

```text
/lee/map_server
/lee/amcl
/lee/amcl_pose
/lee/particle_cloud
/lee/initialpose
```

따라서 문서의 명령어가 바로 동작하지 않으면 먼저 `ros2 topic list`와 `ros2 node list`로 실제 이름을 확인한다.

---

## 7. rosbag remap 주의

`ros2 bag play --remap`은 topic 이름만 바꾼다.

```bash
ros2 bag play <bag_dir> --clock \
  --remap /scan:=/lee/scan
```

위 명령은 `/scan` topic을 `/lee/scan`으로 바꿔서 재생한다. 하지만 message 안의 `header.frame_id`는 바꾸지 않는다.

따라서 rosbag replay 문제를 볼 때는 항상 아래 둘을 따로 확인한다.

```bash
ros2 topic echo /lee/scan --once
ros2 run tf2_ros tf2_echo odom_lee base_footprint \
  --ros-args -r /tf:=/lee/tf -r /tf_static:=/lee/tf_static
```

bag 기반 workflow에서는 기록 당시 frame이 `odom`일 수도 있다. 그 경우에는 `odom_lee`가 아니라 실제 bag 안의 frame 이름을 기준으로 확인한다.

---

## 8. goal / initialpose CLI 작성 규칙

`NavigateToPose` goal과 `/initialpose`는 YAML 문자열을 사용한다. frame 이름은 문자열이므로 따옴표를 붙이는 형태를 우선 사용한다.

현재 프로젝트 기본값 기준 goal 예시:

```bash
ros2 action send_goal /lee/navigate_to_pose nav2_msgs/action/NavigateToPose \
"{pose: {header: {frame_id: 'map_lee'}, pose: {position: {x: 1.0, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}}"
```

초기 위치는 가능하면 RViz의 `2D Pose Estimate`로 먼저 준다. CLI를 쓸 경우 frame과 topic 이름을 실제 실행값에 맞춘다.

---

## 9. 명령어가 실패했을 때 우선순위

명령어가 실패하면 바로 parameter를 바꾸기보다 아래 순서로 확인한다.

```text
1. source install/setup.bash를 했는가?
2. 패키지명이 실제로 존재하는가?
3. launch 파일 인자 이름이 맞는가?
4. topic/node/action 이름에 namespace가 붙어 있는가?
5. topic 이름은 맞지만 frame_id가 다른 것은 아닌가?
6. lifecycle node가 active 상태인가?
7. use_sim_time과 /clock이 필요한 상황인가?
```

Nav2 문제의 상당수는 알고리즘 문제가 아니라 이름, frame, lifecycle, sim time 불일치에서 발생한다.
