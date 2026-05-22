# Command Execution Conventions

이 문서는 저장소 안의 명령어 예시를 실행할 때 먼저 확인해야 하는 규칙을 정리한다.

명령어 문서는 실제 실습 환경에서 사용한 흐름을 기반으로 하지만, GitHub 학습 노트 브랜치에서 재사용하기 쉽도록 일부 경로와 namespace는 일반화되어 있다. 따라서 그대로 복사하기 전에 아래 기준을 확인한다.

---

## 1. 기본 전제

명령어 예시는 주로 ROS2 Humble 기준이다.

대부분의 명령은 아래 준비가 되어 있다는 전제로 작성되어 있다.

```bash
cd $ROS2_WS
source /opt/ros/humble/setup.bash
source install/setup.bash
```

빌드 직후 또는 새 터미널을 열었을 때는 반드시 `source install/setup.bash`를 다시 실행한다.

## 2. 명령어 블록 읽는 법

문서의 명령어 블록은 세 가지로 나뉜다.

| 구분 | 의미 | 실행 전 할 일 |
|---|---|---|
| 실제 실행 명령 | 실습 환경에서 바로 실행할 수 있는 형태 | workspace와 source 상태 확인 |
| placeholder 포함 명령 | `<bag_dir>`, `$ROS2_WS`, `robot_ns` 같은 값을 포함 | 본인 환경 값으로 바꾼 뒤 실행 |
| 진단 명령 | 상태 확인용 명령 | 출력 결과를 보고 다음 단계 판단 |

예를 들어 아래 명령은 placeholder 포함 명령이다.

```bash
ros2 bag play <bag_dir> --clock \
  --remap /scan:=/robot_ns/scan
```

`<bag_dir>`은 실제 bag 디렉터리로 바꾸고, `/robot_ns/scan`은 현재 실습의 topic 이름과 맞는지 `ros2 topic list`로 확인한다.

---

## 3. 자주 쓰는 이름 구분

아래 이름들은 서로 다른 개념이다.

| 이름 | 예시 | 의미 |
|---|---|---|
| package name | `lee_robot_description` | `ros2 launch`, `ros2 pkg prefix`에서 쓰는 ROS2 패키지명 |
| namespace | `robot_ns` | topic/node/action 이름 앞에 붙는 구분자 |
| topic name | `/robot_ns/scan` | 실제 데이터가 흐르는 통신 채널 |
| frame name | `map_robot_ns`, `odom_robot_ns`, `base_footprint`, `base_scan` | TF tree에서 사용하는 좌표계 이름 |
| local path | `$ROS2_WS`, `$ROS2_WORK_DIR` | 파일 시스템 경로 |

특히 `robot_ns`는 namespace 예시이고, `lee_robot_description`은 패키지명 예시다. 둘을 섞으면 실행 명령이 깨진다.

---

## 4. 실제 실행 전 확인 명령

패키지가 보이는지 확인한다.

```bash
ros2 pkg list | grep lee_robot_description
```

launch 파일 인자를 확인한다.

```bash
ros2 launch lee_robot_description nav2.launch.py --show-args
ros2 launch lee_robot_description nav2_navigation.launch.py --show-args
```

현재 topic 이름이 namespace를 쓰는지 확인한다.

```bash
ros2 topic list | sort | grep -E 'scan|odom|tf|map|cmd_vel|amcl|particle|initialpose'
```

현재 node 이름이 namespace를 쓰는지 확인한다.

```bash
ros2 node list | sort | grep -E 'map_server|amcl|planner|controller|bt_navigator|costmap|lifecycle'
```

---

## 5. namespace가 붙는 경우와 안 붙는 경우

문서에서는 주로 아래 형태를 기준으로 설명한다.

```text
/robot_ns/scan
/robot_ns/odom
/robot_ns/tf
/robot_ns/cmd_vel
/robot_ns/navigate_to_pose
```

하지만 launch 구조에 따라 AMCL이나 map_server 관련 topic/node는 아래처럼 보일 수도 있다.

```text
/amcl
/amcl_pose
/particle_cloud
/initialpose
/map_server
```

또는 아래처럼 namespace가 붙을 수도 있다.

```text
/robot_ns/amcl
/robot_ns/amcl_pose
/robot_ns/particle_cloud
/robot_ns/initialpose
/robot_ns/map_server
```

따라서 문서의 명령어가 바로 동작하지 않으면 먼저 `ros2 topic list`와 `ros2 node list`로 실제 이름을 확인한다.

---

## 6. rosbag remap 주의

`ros2 bag play --remap`은 topic 이름만 바꾼다.

```bash
ros2 bag play <bag_dir> --clock \
  --remap /scan:=/robot_ns/scan
```

위 명령은 `/scan` topic을 `/robot_ns/scan`으로 바꿔서 재생한다. 하지만 message 안의 `header.frame_id`는 바꾸지 않는다.

따라서 rosbag replay 문제를 볼 때는 항상 아래 둘을 따로 확인한다.

```bash
ros2 topic echo /robot_ns/scan --once
ros2 run tf2_ros tf2_echo odom_robot_ns base_footprint
```

---

## 7. goal / initialpose CLI 작성 규칙

`NavigateToPose` goal과 `/initialpose`는 YAML 문자열을 사용한다. frame 이름은 문자열이므로 따옴표를 붙이는 형태를 우선 사용한다.

```bash
ros2 action send_goal /robot_ns/navigate_to_pose nav2_msgs/action/NavigateToPose \
"{pose: {header: {frame_id: 'map_robot_ns'}, pose: {position: {x: 1.0, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}}"
```

RViz에서 `2D Pose Estimate`가 가능하면 처음에는 CLI보다 RViz를 쓰는 편이 실수 가능성이 낮다.

---

## 8. 명령어가 실패했을 때 우선순위

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

이 순서가 중요한 이유는 Nav2 문제의 상당수가 알고리즘 문제가 아니라 이름, frame, lifecycle, sim time 불일치에서 발생하기 때문이다.
