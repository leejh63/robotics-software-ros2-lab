# Virtual Monster Nav2 Lab 실행 명령어

이 문서는 현재 워크스페이스에서 Gazebo, AMCL, Nav2, 랜덤 가상 몬스터, 몬스터 제거 서비스를 확인하기 위한 기본 명령어입니다.

이번 단계에서는 **Gazebo에 실제 몬스터 모델을 spawn/despawn하지 않습니다.** Gazebo는 TurtleBot 시뮬레이션 환경으로 사용하고, 몬스터는 RViz Marker와 `/lee/virtual_scan` 기반 가상 장애물로 처리합니다.

## 0. 워크스페이스 준비

```bash
cd ~/ros2_ws/virtual_monster_nav2_lab
source /opt/ros/humble/setup.bash
colcon build --symlink-install --packages-select lee_robot_description
source install/setup.bash
```

기존 다른 워크스페이스와 섞이지 않도록, 테스트할 때는 현재 워크스페이스의 `install/setup.bash`를 기준으로 source합니다.

## 1. 통합 실행

Gazebo, AMCL, Nav2, RViz, 가상 몬스터 노드를 함께 실행합니다.

```bash
ros2 launch lee_robot_description nav2.launch.py \
  use_rviz:=true \
  use_virtual_obstacles:=true
```

이 실행 흐름에서 가상 몬스터 노드는 다음 기능을 담당합니다.

```text
/lee/virtual_obstacle_markers          RViz 표시용 MarkerArray
/lee/virtual_scan                      Nav2 costmap 주입용 LaserScan
/lee/virtual_monster_states            hunter/mission 판단용 JSON 상태 토픽
/lee/clear_nearest_virtual_obstacle    근접 몬스터 제거 서비스
/lee/reset_virtual_obstacles          랜덤 몬스터 전체 재생성 서비스
```

## 1-1. 기본 맵 기준 확인

현재 기본 실행 기준은 `slam.world + slam_map.yaml`입니다. 가상 몬스터의 스폰/벽 충돌 검사도 같은 맵을 사용해야 합니다.

```yaml
# src/lee_robot_description/config/virtual_obstacles.yaml
map_filter:
  enabled: true
  map_yaml: maps/slam_map.yaml
  unknown_is_blocked: true
```

`room_map.yaml`을 테스트에 사용할 때는 Nav2 실행 맵과 위 `map_filter.map_yaml`을 함께 변경합니다. 둘 중 하나만 바꾸면 몬스터가 벽을 뚫거나 잘못된 위치에 생성되는 것처럼 보일 수 있습니다.

## 2. 초기 위치 지정

Nav2 목표를 보내기 전에 AMCL 초기 위치를 지정합니다.

```bash
ros2 topic pub --once /initialpose geometry_msgs/msg/PoseWithCovarianceStamped \
"{header: {frame_id: map_lee}, pose: {pose: {position: {x: 0.0, y: 0.0, z: 0.0}, orientation: {z: 0.0, w: 1.0}}, covariance: [0.25, 0, 0, 0, 0, 0, 0, 0.25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0685]}}"
```

랜덤 스폰 설정에서 `require_robot_tf_for_spawn: true`를 사용하므로, `map_lee -> base_scan` TF가 연결된 뒤에 몬스터가 생성됩니다. 초기 위치를 주기 전에는 몬스터가 바로 보이지 않을 수 있습니다.

TF 확인:

```bash
ros2 run tf2_ros tf2_echo map_lee base_scan
```

## 3. 스폰 수를 바꿔서 실행하기

기본 스폰 수는 YAML의 `random_spawn.target_count: 3`입니다. YAML을 수정하지 않고 실행할 때만 바꾸려면 `monster_count` 런치 인자를 사용합니다.

예: 몬스터 5개 유지

```bash
ros2 launch lee_robot_description nav2.launch.py \
  use_rviz:=true \
  use_virtual_obstacles:=true \
  monster_count:=5
```

예: 몬스터 1개 유지

```bash
ros2 launch lee_robot_description nav2.launch.py \
  use_rviz:=true \
  use_virtual_obstacles:=true \
  monster_count:=1
```

`monster_count:=-1`은 YAML 값을 그대로 사용한다는 의미입니다.

## 4. 랜덤 몬스터 생성 확인

가상 몬스터 Marker 확인:

```bash
ros2 topic echo /lee/virtual_obstacle_markers --once
```

현재 기본 설정에서는 살아있는 몬스터 3개가 유지됩니다. `monster_count` 런치 인자를 주면 해당 개수로 유지됩니다.

```yaml
random_spawn:
  enabled: true
  target_count: 3
```

가상 LaserScan 확인:

```bash
ros2 topic echo /lee/virtual_scan --once --qos-reliability best_effort
ros2 topic info /lee/virtual_scan -v
```

몬스터 상태 토픽 확인:

```bash
ros2 topic echo /lee/virtual_monster_states --once
```

예상 형태:

```text
data: '{"frame_id":"map_lee","target_count":3,"alive_count":3,"monsters":[...]}'
```

`amcl.rviz`에는 아래 Display가 기본 포함되어 있습니다. 보이지 않을 때만 수동으로 다시 추가합니다.

```text
/lee/virtual_obstacle_markers  MarkerArray
/lee/virtual_scan              LaserScan
/lee/local_costmap/costmap     Map
/lee/global_costmap/costmap    Map
```

## 5. Nav2 목표 전송

예시 목표입니다. 실제 맵 상황에 맞게 좌표는 조정합니다.

```bash
ros2 action send_goal /lee/navigate_to_pose nav2_msgs/action/NavigateToPose \
"{pose: {header: {frame_id: map_lee}, pose: {position: {x: 0.6, y: 0.0, z: 0.0}, orientation: {z: 0.0, w: 1.0}}}}" \
--feedback
```

## 6. 가상 몬스터 제거 테스트

로봇이 몬스터 가까이에 있고, 몬스터가 로봇 정면 범위 안에 있을 때 아래 서비스를 호출합니다.

```bash
ros2 service call /lee/clear_nearest_virtual_obstacle std_srvs/srv/Trigger "{}"
```

성공 예시는 다음과 같습니다.

```text
success: true
message: cleared random_monster_1
```

조건을 만족하지 못하면 다음과 비슷하게 실패합니다.

```text
success: false
message: no clearable virtual obstacle in front of the robot (...)
```

기본 제거 조건은 다음 파일에서 조정합니다.

```bash
src/lee_robot_description/config/virtual_obstacles.yaml
```

```yaml
clear_rule:
  enabled: true
  service_name: /lee/clear_nearest_virtual_obstacle
  attack_range: 0.70
  attack_fov_deg: 60.0
  attack_cooldown: 1.0
```

제거 후 살아있는 몬스터 수가 현재 `target_count`보다 작아지면 새 몬스터가 유효 위치에 다시 생성됩니다.

## 7. 실행 중 스폰 수 변경

가상 몬스터 노드는 `target_count` 파라미터를 제공합니다. 실행 중에도 유지 개수를 바꿀 수 있습니다.

현재 파라미터 확인:

```bash
ros2 param get /virtual_dynamic_obstacles target_count
```

5개로 늘리기:

```bash
ros2 param set /virtual_dynamic_obstacles target_count 5
```

2개로 줄이기:

```bash
ros2 param set /virtual_dynamic_obstacles target_count 2
```

동작 의미:

```text
target_count 증가  새 몬스터가 유효 위치에 추가 생성됨
target_count 감소  초과 몬스터가 Marker와 /lee/virtual_scan에서 제거됨
target_count 0     랜덤 몬스터를 모두 제거한 상태로 유지함
```

## 8. 랜덤 몬스터 전체 리셋

현재 랜덤 몬스터 배치를 전부 다시 뽑고 싶을 때 사용합니다.

```bash
ros2 service call /lee/reset_virtual_obstacles std_srvs/srv/Trigger "{}"
```

성공 예시:

```text
success: true
message: reset random monsters: removed=3, alive=3
```

## 9. 랜덤 스폰 설정 수정

현재 시나리오 파일:

```bash
src/lee_robot_description/config/virtual_obstacles.yaml
```

핵심 설정:

```yaml
map_filter:
  enabled: true
  map_yaml: maps/slam_map.yaml
  unknown_is_blocked: true

marker_style:
  body_type: sphere
  body_radius_scale: 0.55
  show_collision_radius: true
  show_target_line: false

random_spawn:
  enabled: true
  target_count: 3
  respawn_delay: 0.0
  wall_clearance: 0.25
  robot_spawn_clearance: 1.00
  monster_clearance: 0.60
  target_min_distance: 0.80
  target_max_distance: 2.00
  path_check_step: 0.05
```

설정 의미:

```text
body_type             RViz에 표시할 몬스터 몸체 모양
body_radius_scale     화면에 보이는 몸체 크기 비율
show_collision_radius 실제 /lee/virtual_scan 주입 반경을 바닥 원판으로 표시
show_target_line      랜덤 이동 목표선을 RViz에 표시
wall_clearance        벽/unknown 주변 생성 및 이동 금지 여유 거리
robot_spawn_clearance TurtleBot 주변 생성 금지 거리
monster_clearance     몬스터끼리 너무 가까운 생성 방지 거리
path_check_step       이동 target까지의 선분 검사 간격
```

설정 수정 후에는 가상 몬스터 노드를 재실행합니다.

## 10. 벽을 뚫는 것처럼 보일 때 확인

먼저 표시 문제인지 실제 이동 문제인지 분리합니다.

```text
구체만 벽과 겹쳐 보임       시각 표시 문제일 가능성이 큼
바닥 원판도 벽을 넘어감      맵 좌표/충돌 검사 문제일 가능성이 큼
목표선이 벽을 통과함         target 선분 검사 조건을 조정해야 함
```

목표선까지 확인하려면 아래 값을 켭니다.

```yaml
marker_style:
  show_target_line: true
```

벽과 더 떨어지게 하고 싶으면 아래 값을 키웁니다.

```yaml
random_spawn:
  wall_clearance: 0.35
  path_check_step: 0.03
```

설정 수정 후에는 다시 빌드할 필요는 없고, 노드만 재실행하면 됩니다.

## 11. 고정 path 모드로 되돌리기

랜덤 스폰을 끄면 `obstacles:`에 정의된 고정 path 몬스터를 사용합니다.

```yaml
random_spawn:
  enabled: false
```

고정 path 예시:

```yaml
obstacles:
  - name: crossing_1
    shape: circle
    radius: 0.35
    speed: 0.25
    loop: ping_pong
    clearable: true
    path:
      - [0.8, -1.0]
      - [0.8, 1.0]
```

## 12. 서비스 및 Nav2 상태 확인

서비스 확인:

```bash
ros2 service list | grep virtual
```

예상 서비스:

```text
/lee/clear_nearest_virtual_obstacle
/lee/reset_virtual_obstacles
```

Nav2 lifecycle 상태 확인:

```bash
ros2 lifecycle get /lee/controller_server
ros2 lifecycle get /lee/planner_server
ros2 lifecycle get /lee/bt_navigator
```

예상 상태:

```text
active [3]
```

## 13. 모듈 단위 실행

Nav2와 가상 몬스터 노드를 분리해서 확인하고 싶을 때 사용합니다.

Terminal 1, Nav2 실행:

```bash
cd ~/ros2_ws/virtual_monster_nav2_lab
source /opt/ros/humble/setup.bash
source install/setup.bash

VIRTUAL_PARAMS="$(ros2 pkg prefix lee_robot_description)/share/lee_robot_description/config/nav2_params_virtual_obstacles.yaml"

ros2 launch lee_robot_description nav2.launch.py \
  use_rviz:=true \
  use_virtual_obstacles:=false \
  params_file:="${VIRTUAL_PARAMS}"
```

Terminal 2, 가상 몬스터 노드만 별도 실행:

```bash
cd ~/ros2_ws/virtual_monster_nav2_lab
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 launch lee_robot_description virtual_dynamic_obstacles.launch.py \
  monster_count:=3
```

이 방식은 Nav2 costmap에는 `virtual_obstacle_layer`를 적용하되, 가상 몬스터 노드는 별도 터미널에서 관리하고 싶을 때 사용합니다. 통합 실행에서 이미 `use_virtual_obstacles:=true`로 실행 중이면 Terminal 2를 중복 실행하지 않습니다.

## 14. 현재 범위와 나중에 추가할 범위

현재 범위:

```text
맵 기반 랜덤 몬스터 스폰
살아있는 몬스터 수 유지
런치 인자/실행 중 파라미터로 스폰 수 조절
랜덤 몬스터 전체 리셋 서비스
벽/unknown/로봇 주변 스폰 제한
벽을 뚫지 않는 랜덤 waypoint 이동
RViz Marker 표시
/lee/virtual_scan 발행
/lee/virtual_monster_states 발행
Nav2 costmap 장애물 반영
근접 제거 서비스
```

나중에 추가할 수 있는 범위:

```text
Gazebo 몬스터 모델 spawn/despawn
카메라 이미지 위 몬스터 overlay
키보드/버튼 기반 attack command
자동 추적 후 제거하는 monster_hunter_node
Nav2 Behavior Tree와 제거 행동 연동
```

## 15. 종료 및 정리 확인

```bash
pgrep -af 'gazebo|gzserver|gzclient|ros2 launch|spawn_entity|nav2|amcl|map_server|virtual_dynamic_obstacles'
```

필요한 경우 현재 테스트 세션에서 실행한 프로세스만 종료합니다.
