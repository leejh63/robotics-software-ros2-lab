# Virtual Monster Nav2 Lab

Nav2 costmap에 가상 몬스터를 동적 장애물처럼 주입하고, TurtleBot이 이를 회피하거나 제거하는 실험용 ROS 2 워크스페이스입니다.

이 프로젝트의 핵심은 Gazebo에 실제 몬스터 모델을 추가하는 것이 아니라, **RViz Marker와 가상 LaserScan(`/lee/virtual_scan`)을 이용해 Nav2 costmap에 장애물을 주입하는 것**입니다. Gazebo는 TurtleBot 시뮬레이션 실행 환경으로 그대로 사용합니다.

## 현재 구현 범위

```text
Gazebo TurtleBot 시뮬레이션              유지
AMCL + Nav2 자율주행                    유지
가상 몬스터 Marker 표시                 구현됨
/lee/virtual_scan 장애물 주입            구현됨
local/global costmap 연동                구현됨
근접 몬스터 제거 서비스                  구현됨
맵 기반 랜덤 몬스터 스폰                 구현됨
벽/unknown/로봇 주변 스폰 제한           구현됨
벽을 뚫지 않는 랜덤 waypoint 이동        구현됨
살아있는 몬스터 수 유지                 구현됨
런치 인자/실행 중 파라미터로 스폰 수 조절 구현됨
랜덤 몬스터 리셋 서비스                  구현됨
Gazebo 몬스터 모델 spawn/despawn         나중에 추가 예정
```

## 주요 파일

```text
virtual_monster_nav2_lab/
├── COMMANDS.md
└── src/
    └── lee_robot_description/
        ├── config/
        │   ├── virtual_obstacles.yaml
        │   └── nav2_params_virtual_obstacles.yaml
        ├── launch/
        │   ├── nav2.launch.py
        │   └── virtual_dynamic_obstacles.launch.py
        ├── maps/
        │   ├── slam_map.yaml        # 기본 실행/몬스터 스폰 기준 맵
        │   ├── slam_map.pgm
        │   ├── room_map.yaml        # 작은 방 테스트용 보조 맵
        │   └── room_map.pgm
        └── scripts/
            └── virtual_dynamic_obstacles.py
```

## 동작 구조

```text
virtual_dynamic_obstacles.py
  ├── slam_map.yaml/pgm 로드
  ├── map_lee 기준 free 영역 계산
  ├── 벽/unknown/로봇 주변을 제외하고 target_count만큼 랜덤 몬스터 생성
  ├── 각 몬스터가 유효한 랜덤 target을 선택해 이동
  ├── 이동 중 다음 위치가 벽/unknown 영역이면 target 재선택
  ├── /lee/virtual_obstacle_markers 로 RViz Marker 발행
  ├── /lee/virtual_scan 으로 가상 LaserScan 발행
  ├── Nav2 local/global costmap의 virtual_obstacle_layer가 이를 장애물로 반영
  ├── /lee/clear_nearest_virtual_obstacle 서비스 호출 시 조건을 만족한 몬스터 제거 후 재생성
  ├── /lee/reset_virtual_obstacles 서비스 호출 시 랜덤 몬스터 전체 재생성
  └── target_count 파라미터 변경 시 살아있는 몬스터 수를 즉시 조정
```

## 좌표 프레임 기준

랜덤 스폰과 벽 충돌 검사는 저장된 맵을 기준으로 해야 하므로, 가상 몬스터 좌표는 `map_lee` 기준입니다.

```yaml
obstacle_frame: map_lee
scan_frame: base_scan
```

`random_spawn.require_robot_tf_for_spawn`이 `true`이면 `map_lee -> base_scan` TF가 잡힌 뒤에만 몬스터가 생성됩니다. 따라서 AMCL 초기 위치를 주기 전에는 몬스터가 아직 보이지 않을 수 있습니다.

## 기본 맵 기준

현재 기본 실행 기준은 `slam.world + slam_map.yaml`입니다. 따라서 가상 몬스터의 랜덤 스폰과 벽 충돌 검사도 `slam_map.yaml`을 기준으로 맞춥니다.

```yaml
map_filter:
  enabled: true
  map_yaml: maps/slam_map.yaml
  unknown_is_blocked: true
```

`room_map.yaml`은 작은 방 테스트용 보조 맵으로 남겨두지만, 기본 실행 기준에서는 사용하지 않습니다. 특정 테스트에서 `room_map.yaml`을 쓰려면 Nav2 실행 맵과 `virtual_obstacles.yaml`의 `map_filter.map_yaml`을 함께 바꿔야 합니다.

## 랜덤 스폰 규칙

기본 설정은 `src/lee_robot_description/config/virtual_obstacles.yaml`에서 관리합니다.

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

  radius_min: 0.25
  radius_max: 0.35
  speed_min: 0.12
  speed_max: 0.28

  wall_clearance: 0.25
  robot_spawn_clearance: 1.00
  monster_clearance: 0.60

  target_min_distance: 0.80
  target_max_distance: 2.00
  path_check_step: 0.05
  max_spawn_attempts: 300
  max_target_attempts: 120
  require_robot_tf_for_spawn: true
```

의미는 다음과 같습니다.

```text
body_type                : RViz에 표시할 몬스터 몸체 모양, 기본값은 sphere
body_radius_scale        : 화면에 보이는 몸체 크기 비율, 실제 충돌 반경은 radius 유지
show_collision_radius    : 실제 /lee/virtual_scan 주입 반경을 바닥 원판으로 표시
target_count             : 살아있는 몬스터 유지 개수
respawn_delay            : 제거 후 재생성 지연 시간
wall_clearance           : 벽/unknown 영역과의 최소 여유 거리
robot_spawn_clearance    : TurtleBot 주변 스폰 금지 거리
monster_clearance        : 몬스터끼리 너무 가깝게 생성되는 것을 막는 거리
target_min/max_distance  : 랜덤 이동 목표점 선택 거리
path_check_step          : 이동 경로가 벽을 통과하는지 검사하는 간격
require_robot_tf_for_spawn: 로봇 위치를 확인한 뒤 스폰할지 여부
```


## RViz 표시 방식

`amcl.rviz`에는 가상 몬스터 확인에 필요한 기본 Display를 포함해 두었습니다. 실행 후 별도 수동 추가 없이 `/lee/virtual_obstacle_markers`, `/lee/virtual_scan`, `/lee/local_costmap/costmap`, `/lee/global_costmap/costmap`을 확인할 수 있습니다.

기본 표시 방식은 원기둥 하나가 아니라, 작은 구체와 바닥 원판을 함께 사용합니다.

```text
구체        : 화면에 보이는 몬스터 몸체
바닥 원판   : Nav2 costmap에 주입되는 실제 LaserScan 반경
```

이렇게 분리한 이유는 단순 원기둥만 표시하면 실제 충돌 반경과 시각적 몸체가 섞여서 벽을 뚫는 것처럼 보일 수 있기 때문입니다. 바닥 원판이 벽을 넘지 않는데 구체만 근처에 보이면 시각 표시 문제에 가깝고, 바닥 원판 자체가 벽을 넘으면 맵 좌표/충돌 검사 쪽을 조정해야 합니다.

```yaml
marker_style:
  body_type: sphere
  body_radius_scale: 0.55
  show_collision_radius: true
  collision_radius_alpha: 0.18
  show_target_line: false
```

이동 목표선을 확인하고 싶으면 `show_target_line: true`로 바꿉니다.


## 몬스터 상태 토픽

Stage 2부터는 자율 hunter node가 사용할 수 있도록 상태 토픽도 함께 발행합니다.

```text
/lee/virtual_monster_states  std_msgs/String JSON
```

이 토픽은 MarkerArray나 LaserScan을 해석하지 않고도 살아있는 몬스터의 위치, 반경, 속도, clear 가능 여부를 확인하기 위한 인터페이스입니다.

예상 JSON payload의 핵심 필드는 다음과 같습니다.

```text
frame_id       몬스터 좌표 기준 frame
scan_frame     virtual_scan 기준 frame
mode           random-map-spawn 또는 fixed-path
target_count   유지하려는 몬스터 수
alive_count    현재 살아있는 몬스터 수
known_count    내부 리스트에 남아있는 전체 몬스터 객체 수
monsters       살아있는 몬스터 상태 배열
```

확인 명령:

```bash
ros2 topic echo /lee/virtual_monster_states --once
```

## 스폰 수 조절 방법

기본 스폰 수는 `virtual_obstacles.yaml`의 `random_spawn.target_count`에서 관리합니다.

```yaml
random_spawn:
  enabled: true
  target_count: 3
```

YAML을 수정하지 않고 실행할 때만 바꾸고 싶으면 `monster_count` 런치 인자를 사용합니다.

```bash
ros2 launch lee_robot_description nav2.launch.py \
  use_rviz:=true \
  use_virtual_obstacles:=true \
  monster_count:=5
```

실행 중에도 아래처럼 바꿀 수 있습니다. 값이 줄어들면 초과 몬스터는 Marker와 `virtual_scan`에서 제거되고, 값이 늘어나면 유효 위치에 새 몬스터가 생성됩니다.

```bash
ros2 param set /virtual_dynamic_obstacles target_count 5
ros2 param set /virtual_dynamic_obstacles target_count 2
```

랜덤 몬스터 배치를 다시 뽑고 싶으면 리셋 서비스를 호출합니다.

```bash
ros2 service call /lee/reset_virtual_obstacles std_srvs/srv/Trigger "{}"
```

## 몬스터 제거 규칙

기본 제거 조건은 `clear_rule`에서 관리합니다.

```yaml
clear_rule:
  enabled: true
  service_name: /lee/clear_nearest_virtual_obstacle
  attack_range: 0.70
  attack_fov_deg: 60.0
  attack_cooldown: 1.0
```

의미는 다음과 같습니다.

```text
attack_range   : 로봇 기준 제거 가능 거리
attack_fov_deg : 로봇 정면 기준 제거 가능 각도
attack_cooldown: 제거 서비스 재사용 대기 시간
```

현재 방식에서는 몬스터가 제거되면 Gazebo 객체가 삭제되는 것이 아니라, 해당 가상 몬스터가 `virtual_scan`과 Marker 발행 대상에서 제외됩니다. `random_spawn.target_count` 또는 `monster_count`로 지정한 유지 개수보다 살아있는 몬스터가 적어지면 새 몬스터가 맵의 유효 위치에 다시 생성됩니다.

## 고정 path 모드로 되돌리는 방법

기본값은 랜덤 스폰입니다. 기존 고정 path 테스트가 필요하면 아래처럼 바꿉니다.

```yaml
random_spawn:
  enabled: false
```

이 경우 `obstacles:`에 정의된 `crossing_1`, `crossing_2` 경로를 사용합니다.

## 실행 명령

자세한 실행 순서는 `COMMANDS.md`를 기준으로 사용합니다.
