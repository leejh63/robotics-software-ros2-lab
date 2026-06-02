# Stage 4 Changelog

## 2026-06-02

### Added

- `config/monster_mission.yaml`
  - Stage 4 detector/mission parameter file.
  - `target_kill_count`, `search_waypoints`, `exit_pose`를 별도 관리.
- `scripts/monster_detector_node.py`
  - `/lee/virtual_scan`을 보고 scan hit를 `map_lee` 좌표로 변환.
  - static map에서는 free인데 scan에 잡힌 hit를 몬스터 후보로 분류.
  - `/lee/detected_monster_candidates` JSON 발행.
- `scripts/monster_mission_node.py`
  - `/lee/detected_monster_candidates`만 사용해 patrol → hunt → exit 성공 루트 수행.
  - `/lee/virtual_monster_states`는 사용하지 않음.
  - `ESCAPE_TO_EXIT` 상태를 예약 상태로 추가.
- `launch/monster_mission.launch.py`
  - detector와 mission manager를 함께 실행.

### Changed

- `CMakeLists.txt`
  - `monster_detector_node.py`, `monster_mission_node.py` 설치 대상 추가.
- `package.xml`
  - `action_msgs` 실행 의존성 추가.
- `scripts/virtual_dynamic_obstacles.py`
  - PGM unknown pixel 값 205를 명시적으로 unknown으로 처리.
  - `unknown_is_blocked=true`일 때 unknown cell이 free로 오분류되지 않도록 보정.

### Preserved

- `scripts/monster_hunter_node.py`
- `launch/monster_hunter.launch.py`
- `/lee/virtual_monster_states` 디버그 토픽

### Deferred

- ESCAPE_TO_EXIT 실제 탈출 로직
- 사냥 실패 횟수/timeout 기반 탈출 전환
- 후보 blacklist
- virtual_scan occlusion raycast
- 자동 waypoint 생성

## Runtime Fix - use_sim_time duplicate declaration

### Fixed
- Removed explicit `declare_parameter('use_sim_time', True)` from Stage 4 detector and mission nodes because ROS 2 Humble can already declare `use_sim_time` through the node time source / launch parameter handling.
- Applied the same defensive cleanup to the preserved Stage 3 hunter node so it does not crash if launched with `use_sim_time` overrides later.

### Reason
- Launching Stage 4 failed with `ParameterAlreadyDeclaredException: ['use_sim_time']` before node initialization completed.



## Runtime Tuning Fix - Detector range too wide

### Changed
- Reduced detector default `max_range` from `3.5m` to `1.40m`.
- Reduced detector default `cluster_distance` from `0.45m` to `0.30m`.
- Increased detector default `min_cluster_points` from `2` to `3` to reduce noisy candidates.
- Reduced detector default `max_candidates` from `5` to `3`.
- Added `detection_fov_deg` with a default front-facing FOV of `120.0` degrees.
- Added mission-side `max_candidate_distance` with a default of `1.60m`.
- Added launch overrides: `detection_max_range`, `detection_fov_deg`, `cluster_distance`, `min_cluster_points`, `max_candidate_distance`.

### Reason
- Stage 4 worked, but the detector reacted to monsters from too far away. The mission should initially behave like local patrol/search, not global monster targeting.

## Runtime Tuning Fix - Clear range too strict

### Changed
- Increased virtual clear default `attack_range` from `0.70m` to `1.20m`.
- Increased virtual clear default `attack_fov_deg` from `60.0` to `140.0`.
- Reduced virtual clear default `attack_cooldown` from `1.0s` to `0.4s`.
- Increased mission default `approach_distance` from `0.65m` to `0.85m`, so Nav2 does not need to drive too close to the virtual obstacle.
- Increased mission default `clear_distance` from `0.75m` to `1.10m`.
- Added mission clear retry controls: `max_clear_attempts`, `clear_retry_delay_sec`.
- Added launch overrides for virtual clear tuning: `attack_range`, `attack_fov_deg`, `attack_cooldown`.
- Added launch overrides for mission clear behavior: `approach_distance`, `clear_distance`, `max_clear_attempts`, `clear_retry_delay_sec`.

### Reason
- The detector could find monsters, but clear/attack was too strict. The robot had to be very close and well aligned, so removal felt unreliable.
- The revised defaults allow the robot to clear from a safer standoff distance while still requiring local detection.

## Runtime Fix - Map-wide coverage patrol

### Changed
- `monster_mission_node.py`
  - Adds `patrol_mode=map_grid` for automatic free-space patrol waypoint generation from `map_yaml`.
  - Keeps `patrol_mode=manual` for explicitly supplied `search_waypoints`.
  - Adds `patrol_grid_spacing`, `patrol_wall_clearance`, `patrol_max_waypoints`, `patrol_start_nearest`, and `patrol_unknown_is_blocked` parameters.
  - Starts patrol from the generated waypoint nearest to the robot.
  - Skips failed patrol waypoints instead of retrying the same unreachable point forever.
  - Publishes `/lee/patrol_waypoint_markers` so generated patrol coverage can be checked in RViz.
- `monster_mission.launch.py`
  - Exposes map-grid patrol arguments through launch parameters.
- `monster_mission.yaml`
  - Sets default patrol strategy to `map_grid` instead of the old four-point square patrol.

### Reason
- The previous Stage 4 patrol used four fixed waypoints, so the robot repeatedly moved inside one small square.
- For monster search, the patrol should cover the known free-space map continuously and interrupt patrol whenever detector candidates appear.
