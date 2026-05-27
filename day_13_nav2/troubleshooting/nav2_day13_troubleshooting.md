# Nav2 Day 13 트러블슈팅

Nav2 문제는 `Localization -> Lifecycle -> Action -> Planner -> Controller -> Gazebo` 순서로 구간을 나누어 확인한다.

## 빠른 진단표

| 증상 | 먼저 확인할 것 | 확인 명령 | 가능성이 큰 원인 |
|---|---|---|---|
| RViz Goal 버튼이 안 먹음 | action namespace | `ros2 action list \| grep navigate` | RViz Goal tool이 `/lee/navigate_to_pose`를 못 봄 |
| action server not available | bt_navigator와 lifecycle | `ros2 lifecycle get /lee/bt_navigator` | Nav2 launch 미실행, namespace 불일치, inactive 상태 |
| `No critics defined for FollowPath` | controller parameter | `ros2 param get /lee/controller_server FollowPath.critics` | DWB plugin YAML 구조 불일치 |
| path는 나오는데 `/cmd_vel`이 없음 | controller/DWB | `ros2 topic echo /lee/cmd_vel` | controller_server inactive, DWB 평가 실패 |
| `/cmd_vel`은 나오는데 로봇이 안 움직임 | Gazebo plugin subscribe topic | `ros2 topic info /lee/cmd_vel -v` | diff_drive plugin topic 불일치 |
| goal이 계속 실패함 | map, costmap, TF, BT 단계 | `ros2 topic echo /lee/plan --once` | planner/controller/BT 중간 단계 실패 |

Nav2는 `goal -> BT -> planner -> controller -> cmd_vel -> Gazebo plugin` 순서로 끊긴 지점을 찾는다. 공통 진단 순서는 `appendix/troubleshooting_quick_diagnosis.md`를 기준으로 본다.

---


## 1. RViz Nav2 Goal 버튼이 안 먹음

### 증상

```text
RViz Navigation2 패널에 unknown 표시
Nav2 Goal을 눌러도 로봇이 움직이지 않음
action feedback이 안 보임
```

### 판단 기준

```text
Nav2 서버 자체가 안 되는 문제가 아니다.
RViz Goal 도구가 /lee/navigate_to_pose를 보지 못하는 namespace 연결 문제일 가능성이 높다.
```

### 확인

```bash
ros2 action list | grep navigate
```

정상:

```text
/lee/navigate_to_pose
```

### 조치

일단 action goal로 직접 보낸다.

```bash
ros2 action send_goal /lee/navigate_to_pose nav2_msgs/action/NavigateToPose \
"{pose: {header: {frame_id: 'map_lee'}, pose: {position: {x: 0.0, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}}"
```

이후 고칠 부분:

```text
RViz Nav2 panel/action/lifecycle target을 lee namespace 기준으로 맞추기
RViz 설정 파일 별도 저장
```

---

## 2. action server not available

### 증상

```text
Waiting for an action server to become available...
```

### 원인 후보

```text
bt_navigator가 안 떠 있음
bt_navigator가 active가 아님
action 이름을 /navigate_to_pose로 잘못 보냄
namespace가 /lee인데 기본 action을 보고 있음
```

### 확인

```bash
ros2 node list | grep bt
ros2 lifecycle get /lee/bt_navigator
ros2 action list | grep navigate
```

### 조치

```bash
ros2 launch lee_robot_description nav2_navigation.launch.py
```

그리고 action 이름은 `/lee/navigate_to_pose`를 사용한다.

---

## 3. No critics defined for FollowPath

### 증상

```text
No critics defined for FollowPath
```

### 의미

DWB controller가 후보 궤적을 평가할 critic 목록을 못 읽은 것이다.

### 원인 후보

```text
nav2_params.yaml의 namespace 구조가 실제 노드 namespace와 안 맞음
FollowPath 설정 indentation이 잘못됨
controller_plugins의 이름과 하위 FollowPath 키가 불일치
nav2_bringup navigation_launch.py를 직접 실행하면서 namespace가 기대대로 적용되지 않음
```


### namespace 불일치 사례

처음에는 공식 Nav2 하위 launch 파일인 `nav2_bringup`의 `navigation_launch.py`를 직접 실행하려고 했다.

```bash
ros2 launch nav2_bringup navigation_launch.py \
  namespace:=lee \
  params_file:=<nav2_params.yaml>
```

하지만 이 방식에서는 `namespace:=lee`를 넘겨도 Nav2 서버 노드가 기대한 것처럼 모두 `/lee` 아래에 생성되지 않을 수 있었다.

그 결과 parameter file은 `lee:` 아래 구조를 기준으로 작성되어 있는데, 실제 노드는 아래처럼 root namespace에 떠서 parameter 구조가 어긋날 수 있다.

```text
/controller_server
/planner_server
/bt_navigator
```

이 상태에서는 `controller_server`가 `FollowPath` 하위의 DWB critic 설정을 제대로 읽지 못하고, `No critics defined for FollowPath` 오류가 발생할 수 있다.

해결은 공식 `navigation_launch.py`를 단독으로 직접 실행하지 않고, 사용자 launch 파일에서 먼저 namespace를 적용한 뒤 그 안에서 include하는 방식이다.

```text
nav2_navigation.launch.py
  -> PushRosNamespace(namespace=lee)
  -> Include nav2_bringup/launch/navigation_launch.py
  -> params_file = nav2_params.yaml
```

수정 후 Nav2 주행 서버들은 아래처럼 `/lee` 아래에 생성된다.

```text
/lee/controller_server
/lee/planner_server
/lee/bt_navigator
/lee/behavior_server
```

이렇게 실제 node namespace와 `nav2_params.yaml`의 parameter namespace 구조가 일치하면, `FollowPath` plugin과 DWB critic 설정도 정상적으로 로드된다.

### 확인

```bash
ros2 node list | grep controller
ros2 param get /lee/controller_server controller_plugins
ros2 param get /lee/controller_server FollowPath.critics
```

노드가 `/controller_server`로 떠 있으면:

```bash
ros2 param get /controller_server controller_plugins
ros2 param get /controller_server FollowPath.critics
```

### 조치

이 저장소에서는 직접 `nav2_bringup navigation_launch.py namespace:=lee`를 실행하는 방식보다 다음 launch 파일을 기준으로 한다.

```bash
ros2 launch lee_robot_description nav2_navigation.launch.py
```

---

## 4. goal accepted인데 `/lee/plan`이 안 생김

### 원인 후보

```text
목표가 벽 또는 inflation 영역 안에 있음
목표가 지도 밖에 있음
global_costmap이 안 만들어짐
planner_server가 active가 아님
AMCL 위치가 틀려 현재 위치가 지도 밖으로 계산됨
```

### 확인

```bash
ros2 lifecycle get /lee/planner_server
ros2 topic echo /lee/global_costmap/costmap --once
ros2 topic echo /lee/map --once
ros2 run tf2_ros tf2_echo map_lee base_footprint --ros-args -r /tf:=/lee/tf -r /tf_static:=/lee/tf_static
```

RViz에서 goal 위치가 자유 공간인지 확인한다.

---

## 5. `/lee/plan`은 있는데 `/lee/cmd_vel`이 없음

### 원인 후보

```text
controller_server가 active가 아님
local_costmap이 안 만들어짐
odom topic이 안 들어옴
DWB 설정 문제
TF transform 불가
```

### 확인

```bash
ros2 lifecycle get /lee/controller_server
ros2 topic echo /lee/local_costmap/costmap --once
ros2 topic echo /lee/odom --once
ros2 run tf2_ros tf2_echo odom_lee base_footprint --ros-args -r /tf:=/lee/tf -r /tf_static:=/lee/tf_static
ros2 param get /lee/controller_server FollowPath.critics
```

---

## 6. `/lee/cmd_vel`은 나오는데 로봇이 안 움직임

### 원인 후보

```text
Gazebo가 pause 상태
Gazebo diff_drive plugin이 /lee/cmd_vel을 구독하지 않음
cmd_vel topic remap 문제
다른 publisher가 반대 명령을 계속 발행
```

### 확인

```bash
ros2 topic info /lee/cmd_vel -v
ros2 topic echo /lee/cmd_vel
```

Gazebo GUI에서 pause 상태도 확인한다.

---

## 7. AMCL이 흔들리고 Nav2도 이상함

### 원인 후보

```text
초기 위치를 잘못 찍음
world와 map이 맞지 않음
/lee/scan frame_id와 TF가 맞지 않음
map_lee -> odom_lee TF가 없음
```

### 확인

```bash
ros2 topic echo /particle_cloud --once
ros2 topic echo /amcl_pose --once
ros2 run tf2_ros tf2_echo map_lee odom_lee --ros-args -r /tf:=/lee/tf -r /tf_static:=/lee/tf_static
ros2 run tf2_ros tf2_echo base_footprint base_scan --ros-args -r /tf:=/lee/tf -r /tf_static:=/lee/tf_static
```

### 조치

RViz에서 `2D Pose Estimate`를 다시 찍는다.
world와 map 조합도 확인한다.

---

## 8. costmap이 비어 있거나 이상함

### 원인 후보

```text
/lee/map이 없음
/lee/scan이 없음
TF가 끊김
costmap frame 설정이 실제 frame과 다름
sensor QoS 문제
```

### 확인

```bash
ros2 topic list | grep costmap
ros2 topic echo /lee/global_costmap/costmap --once
ros2 topic echo /lee/local_costmap/costmap --once
ros2 topic hz /lee/scan
ros2 run tf2_ros tf2_echo map_lee base_footprint --ros-args -r /tf:=/lee/tf -r /tf_static:=/lee/tf_static
```

---

## 9. 디버깅 순서 요약

```text
1. /lee/scan, /lee/odom, /lee/tf 확인
2. /lee/map 확인
3. /amcl_pose, /particle_cloud, map_lee -> odom_lee 확인
4. Nav2 lifecycle active 확인
5. /lee/navigate_to_pose action 확인
6. goal 전송
7. /lee/plan 확인
8. /lee/cmd_vel 확인
9. Gazebo 움직임 확인
```

