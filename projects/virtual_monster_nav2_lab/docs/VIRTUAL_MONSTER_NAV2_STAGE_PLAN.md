# Virtual Monster Nav2 Lab 단계별 설계 및 수정 계획

이 문서는 `virtual_monster_nav2_lab`의 수정 순서와 설계 기준을 고정하기 위한 작업 문서이다. 현재 프로젝트는 Gazebo에 실제 몬스터 모델을 spawn/despawn하는 방식이 아니라, RViz Marker와 가상 LaserScan(`/lee/virtual_scan`)을 이용해 Nav2 costmap에 동적 장애물을 주입하는 구조이다.

최종 목표는 다음과 같다.

```text
기존 맵을 기준으로 TurtleBot이 자율적으로 이동한다.
가상 몬스터를 탐색하거나 접근한다.
지정한 수의 몬스터를 제거한다.
목표 제거 수를 달성하면 특정 위치로 이동한다.
```

---

## 1. 핵심 설계 원칙

### 1.1 표시, 회피, 판단을 분리한다

```text
/lee/virtual_obstacle_markers    RViz 표시용
/lee/virtual_scan                Nav2 costmap 주입용
/lee/virtual_monster_states      hunter/mission 판단용
```

MarkerArray는 사람이 보기 위한 표현이고, LaserScan은 costmap 주입용이다. 자율 판단 로직이 MarkerArray나 LaserScan을 억지로 해석하지 않도록, 별도 상태 토픽을 둔다.

### 1.2 Gazebo 모델 몬스터는 후순위로 둔다

현재 목표에서는 Gazebo에 실제 몬스터 모델을 추가하는 것보다 Marker + LaserScan + 상태 토픽 구조가 더 안정적이다. Gazebo 모델은 시각 효과나 카메라 실험 단계에서 추가한다.

### 1.3 최종 미션 로직은 별도 노드로 둔다

`virtual_dynamic_obstacles.py`는 가상 몬스터 환경 생성기 역할로 유지한다. 자율 접근/제거/미션 완료 로직은 이후 `monster_hunter_node.py` 같은 별도 노드에 둔다.

---

## 2. Stage 1 적용 결과: 맵 기준 통일 및 RViz 표시 안정화

Stage 1에서는 새로운 자율 행동 기능을 추가하지 않고, 실행 기준을 안정화하는 변경만 적용했다.

```text
virtual_obstacles.yaml의 map_filter.map_yaml을 maps/slam_map.yaml로 통일
README.md의 기본 맵 설명을 slam_map 기준으로 정리
COMMANDS.md의 기본 맵 설명과 RViz 확인 항목 정리
amcl.rviz에 가상 몬스터 MarkerArray, virtual_scan, local/global costmap Display 추가
```

기본 실행 기준은 다음과 같다.

```text
Gazebo world        : slam.world
Nav2 map            : slam_map.yaml
몬스터 스폰/벽 검사 : slam_map.yaml
```

`room_map.yaml`은 작은 방 테스트용 보조 맵으로만 남긴다. 특정 테스트에서 `room_map.yaml`을 쓰려면 Nav2 map과 `virtual_obstacles.yaml`의 `map_filter.map_yaml`을 함께 바꾼다.

---

## 3. Stage 2 적용 결과: 몬스터 상태 토픽 추가

Stage 2에서는 hunter node를 만들기 전에, hunter가 읽을 수 있는 상태 인터페이스만 추가했다.

```text
/lee/virtual_monster_states
```

메시지 타입은 커스텀 msg가 아니라 `std_msgs/msg/String`이다. data 필드에는 JSON 문자열을 넣는다.

### 3.1 JSON payload 구조

예상 형태는 다음과 같다.

```json
{
  "stamp": {"sec": 0, "nanosec": 0},
  "frame_id": "map_lee",
  "scan_frame": "base_scan",
  "mode": "random-map-spawn",
  "target_count": 3,
  "alive_count": 3,
  "known_count": 3,
  "monsters": [
    {
      "id": 0,
      "name": "random_monster_1",
      "x": 1.2,
      "y": -0.4,
      "radius": 0.3,
      "height": 0.6,
      "speed": 0.2,
      "alive": true,
      "clearable": true,
      "random_motion": true,
      "target": {"x": 1.8, "y": -0.2}
    }
  ]
}
```

### 3.2 Stage 2 수정 대상

```text
src/lee_robot_description/scripts/virtual_dynamic_obstacles.py
src/lee_robot_description/config/virtual_obstacles.yaml
src/lee_robot_description/launch/virtual_dynamic_obstacles.launch.py
src/lee_robot_description/package.xml
README.md
COMMANDS.md
docs/VIRTUAL_MONSTER_NAV2_STAGE_PLAN.md
```

### 3.3 Stage 2에서 하지 않은 작업

```text
monster_hunter_node.py 추가 안 함
kill_count mission state machine 추가 안 함
Nav2 NavigateToPose action client 추가 안 함
patrol/exploration fallback 추가 안 함
Gazebo 몬스터 모델 추가 안 함
커스텀 msg 패키지 추가 안 함
```

### 3.4 검증 명령

```bash
ros2 topic echo /lee/virtual_monster_states --once
```

clear/reset 이후 상태 갱신은 다음으로 확인한다.

```bash
ros2 service call /lee/clear_nearest_virtual_obstacle std_srvs/srv/Trigger "{}"
ros2 topic echo /lee/virtual_monster_states --once

ros2 service call /lee/reset_virtual_obstacles std_srvs/srv/Trigger "{}"
ros2 topic echo /lee/virtual_monster_states --once
```

---

## 4. 다음 단계: Stage 3 단일 몬스터 접근/제거 hunter node

다음 단계에서는 완전한 미션 상태 머신이 아니라, 한 마리 몬스터를 선택해 접근하고 제거하는 최소 hunter node를 추가한다.

신규 파일 후보는 다음과 같다.

```text
src/lee_robot_description/scripts/monster_hunter_node.py
```

Stage 3의 1차 기능은 다음이다.

```text
/lee/virtual_monster_states 구독
현재 로봇 위치 확인
가장 가까운 몬스터 선택
몬스터 중심이 아닌 주변 approach pose 계산
/lee/navigate_to_pose 액션 goal 전송
근접 시 /lee/clear_nearest_virtual_obstacle 서비스 호출
성공/실패 로그 출력
```

Stage 3에서는 최소 테스트용 `target_kill_count`만 사용한다. 아직 다음 작업은 하지 않는다.

```text
목표 수 달성 후 exit pose 이동
복잡한 미션 상태 머신 고도화
frontier exploration 연동
복잡한 behavior tree 구성
```

---

## 5. 이후 단계 요약

```text
Stage 3: 단일 몬스터 접근/제거 hunter node 추가
Stage 4: kill_count + exit pose 미션 상태 머신 고도화
Stage 5: patrol/exploration fallback 추가
Stage 6: Gazebo/카메라/시각 효과 확장
```


## Stage 2/3 적용 결과

Stage 2에서는 hunter가 직접 읽을 수 있는 상태 토픽을 추가했다.

```text
/lee/virtual_monster_states
std_msgs/msg/String JSON payload
```

Stage 2 보정으로 `clear_nearest_virtual_obstacle` 이후의 보충 정책을 명확히 했다.

```text
처리한 몬스터 슬롯만 새 랜덤 몬스터로 교체
처리하지 않은 살아있는 몬스터는 유지
known_count가 clear마다 계속 증가하지 않도록 dead random slot 재사용
```

Stage 3에서는 완전 미션이 아니라 단일 hunter 테스트 노드만 추가했다.

```text
monster_hunter_node.py
monster_hunter.launch.py
```

Stage 3의 범위는 다음으로 제한한다.

```text
상태 토픽 구독
가장 가까운 몬스터 선택
approach pose 계산
Nav2 NavigateToPose goal 전송
기존 clear service 호출
kill_count가 target_kill_count에 도달하면 종료
```

아직 추가하지 않은 항목은 다음과 같다.

```text
exit pose 이동
미션 상태 머신 고도화
patrol/exploration fallback
Gazebo 몬스터 모델
카메라 overlay
```

---

