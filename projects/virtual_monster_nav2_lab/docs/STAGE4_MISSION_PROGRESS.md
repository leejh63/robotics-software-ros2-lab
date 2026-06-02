# Stage 4 Mission Progress

## 목표

Stage 3 hunter를 보존한 상태에서, TurtleBot이 몬스터의 실제 위치를 직접 알지 않는 탐색형 미션 구조를 추가한다.

핵심 목표는 다음과 같다.

```text
알고 있는 정적 맵 사용
몬스터 위치는 mission/hunter가 직접 모름
waypoint 순찰 중 scan 기반 후보 감지
static map에는 free인데 scan에 잡힌 장애물을 몬스터 후보로 판단
접근 가능한 후보를 Nav2로 추적
clear service로 제거
목표 kill_count 달성 후 exit_pose로 이동
ESCAPE_TO_EXIT 상태는 예약만 하고 실제 탈출 로직은 추후 구현
```

## 보존 원칙

```text
기존 Stage 3 파일은 삭제하지 않는다.
monster_hunter_node.py는 좌표를 알고 사냥하는 테스트 노드로 유지한다.
/lee/virtual_monster_states는 디버그/검증용으로 유지한다.
Stage 4 mission 로직은 /lee/virtual_monster_states에 직접 의존하지 않는다.
```

## 현재 반영된 작업

- [x] `config/monster_mission.yaml` 추가
- [x] `scripts/monster_detector_node.py` 추가
- [x] `scripts/monster_mission_node.py` 추가
- [x] `launch/monster_mission.launch.py` 추가
- [x] `CMakeLists.txt` install 대상에 새 노드 추가
- [x] `package.xml`에 `action_msgs` 실행 의존성 추가
- [x] `virtual_dynamic_obstacles.py`의 unknown PGM cell 처리 보정
- [x] `ESCAPE_TO_EXIT` 상태를 mission state에 예약
- [ ] 실제 ESCAPE_TO_EXIT 탈출 로직 연결
- [ ] hunt 실패 누적/timeout/blacklist 정책 추가
- [ ] virtual_scan 생성 시 벽 뒤 몬스터 occlusion raycast 추가
- [ ] search_waypoints와 exit_pose를 실제 맵 기준 좌표로 조정

## Stage 4 현재 동작 경로

```text
INIT
  ↓
PATROL_SEARCH
  ↓
MONSTER_DETECTED
  ↓
APPROACH_MONSTER
  ↓
ATTACK_MONSTER
  ↓
CHECK_KILL_COUNT
  ├─ 목표 수 미달 → PATROL_SEARCH
  └─ 목표 수 달성 → GO_TO_EXIT
  ↓
MISSION_DONE
```

## 예약 상태

```text
ESCAPE_TO_EXIT
```

이 상태는 enum/state로 존재하지만 현재 단계에서는 실제 전환 조건을 만들지 않는다. 나중에 다음 조건을 붙일 수 있다.

```text
hunt timeout 초과
clear 실패 횟수 초과
Nav2 접근 실패 횟수 초과
몬스터 후보 blacklist가 꽉 참
mission timeout 초과
```

## 새 토픽

```text
/lee/detected_monster_candidates   detector가 발행하는 후보 JSON
/lee/monster_mission_status        mission manager 상태 JSON
```

## 새 실행 명령

Nav2/가상 몬스터 통합 실행 후 별도 터미널에서 실행한다.

```bash
ros2 launch lee_robot_description monster_mission.launch.py \
  target_kill_count:=3 \
  exit_pose:="0.0,0.0,0.0"
```

`exit_pose`와 `search_waypoints`는 현재 placeholder이다. 실제 맵/RViz에서 안전한 좌표를 확인한 뒤 조정해야 한다.

## 다음 수정 우선순위

1. RViz에서 실제 `search_waypoints`와 `exit_pose` 좌표 확정
2. detector 후보 토픽이 정상 발행되는지 확인
3. mission status 흐름 확인
4. target_kill_count 달성 후 exit_pose 이동 검증
5. 실패 조건과 ESCAPE_TO_EXIT 연결


## Detector local-range tuning

Stage 4 초기 동작 확인 결과, 장애물 제거는 동작하지만 detector 감지 거리가 넓어 mission이 너무 이른 시점에 후보를 잡을 수 있다.

적용한 보정:

```text
max_range: 3.5 -> 1.40
detection_fov_deg: 120.0 추가
cluster_distance: 0.45 -> 0.30
min_cluster_points: 2 -> 3
max_candidates: 5 -> 3
max_candidate_distance: 1.60 mission-side filter 추가
```

실행 중 조절 인자:

```bash
ros2 launch lee_robot_description monster_mission.launch.py   detection_max_range:=1.0   detection_fov_deg:=90.0   max_candidate_distance:=1.2
```


## Runtime Fix Notes

- fix2: detector range was reduced to keep detection local.
- fix3 clear tuning: clear range/FOV were widened and mission clear retries were added because removal felt unreliable with the original short attack rule.

## Map-wide patrol update

The old `search_waypoints` loop was intentionally simple, but it looked unnatural because the robot stayed inside a small square.
The mission node now supports a map-generated coverage patrol:

```text
patrol_mode: map_grid
map_yaml: maps/slam_map.yaml
patrol_grid_spacing: 0.80
patrol_wall_clearance: 0.28
patrol_max_waypoints: 80
```

Behavior:

```text
known static map free-space
  -> sample safe patrol points
  -> order them in serpentine grid order
  -> start from nearest point to robot
  -> continue around the map
  -> interrupt immediately when a monster candidate is detected
```

RViz check:

```text
MarkerArray: /lee/patrol_waypoint_markers
```

Use `patrol_mode:=manual` only when testing a hand-authored route.
