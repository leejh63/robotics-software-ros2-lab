# Stage 4 Handoff Notes

## 현재 목표

Stage 3 hunter를 보존하면서 Stage 4 탐색형 미션을 추가한다.

```text
몬스터 좌표 직접 사용 X
scan/static map 비교로 후보 감지
waypoint 순찰
후보 접근 및 clear
목표 수 달성 후 exit_pose 이동
ESCAPE_TO_EXIT는 상태만 예약
```

## 절대 삭제하지 말 것

```text
src/lee_robot_description/scripts/monster_hunter_node.py
src/lee_robot_description/launch/monster_hunter.launch.py
/lee/virtual_monster_states
```

Stage 3 hunter는 비교 테스트용으로 계속 필요하다.

## 새로 추가된 파일

```text
src/lee_robot_description/config/monster_mission.yaml
src/lee_robot_description/scripts/monster_detector_node.py
src/lee_robot_description/scripts/monster_mission_node.py
src/lee_robot_description/launch/monster_mission.launch.py
docs/STAGE4_MISSION_PROGRESS.md
docs/STAGE4_CHANGELOG.md
docs/STAGE4_HANDOFF_NOTES.md
```

## 현재 실행 방식

Terminal 1:

```bash
ros2 launch lee_robot_description nav2.launch.py \
  use_rviz:=true \
  use_virtual_obstacles:=true
```

초기 위치 지정 후 Terminal 2:

```bash
ros2 launch lee_robot_description monster_mission.launch.py \
  target_kill_count:=3 \
  exit_pose:="0.0,0.0,0.0"
```

## 확인 토픽

```bash
ros2 topic echo /lee/detected_monster_candidates --once
ros2 topic echo /lee/monster_mission_status --once
```

## 중요한 설계 제한

`monster_mission_node.py`는 `/lee/virtual_monster_states`를 구독하면 안 된다. 해당 토픽은 디버그/RViz/검증용이다.

## 현재 남은 작업

1. `search_waypoints`를 실제 맵 기준으로 조정
2. `exit_pose`를 실제 출구 좌표로 조정
3. detector 후보가 너무 많이/적게 잡히는 경우 `detection_max_range`, `max_candidate_distance`, `detection_fov_deg`, `cluster_distance`, `min_cluster_points` 조정
4. hunt 실패 누적 로직 추가
5. ESCAPE_TO_EXIT 실제 로직 연결
6. 벽 뒤 몬스터가 virtual_scan에 찍히지 않도록 occlusion raycast 추가

## Known Runtime Fix Applied

- Do not explicitly declare `use_sim_time` inside Python nodes. Pass it from launch/config only.
- This prevents `rclpy.exceptions.ParameterAlreadyDeclaredException` on ROS 2 Humble.



## Detector range tuning

Stage 4 detector는 너무 먼 몬스터까지 바로 반응하지 않도록 기본값을 좁혔다.

```text
detection_max_range: 1.40
max_candidate_distance: 1.60
detection_fov_deg: 120.0
```

튜닝 기준:
- 너무 멀리서 반응하면 `detection_max_range`와 `max_candidate_distance`를 줄인다.
- 너무 가까이 가야 반응하면 두 값을 조금 늘린다.
- 뒤쪽/옆쪽 후보까지 잡히면 `detection_fov_deg`를 줄인다.
- 후보가 너무 잘게 쪼개지면 `cluster_distance`를 조금 늘린다.


## Clear Tuning Notes

Current fix3 defaults are intentionally wider than the initial Stage 4 clear rule:

```yaml
clear_rule:
  attack_range: 1.20
  attack_fov_deg: 140.0
  attack_cooldown: 0.4

monster_mission_node:
  approach_distance: 0.85
  clear_distance: 1.10
  max_clear_attempts: 3
  clear_retry_delay_sec: 0.5
```

Important relation:

```text
clear_distance < attack_range
approach_distance < attack_range
```

If clear still fails often, increase `attack_range` to `1.25~1.40` or `attack_fov_deg` to `160~180`. If monsters are removed too easily from awkward angles, reduce `attack_fov_deg` back toward `100~120`.
