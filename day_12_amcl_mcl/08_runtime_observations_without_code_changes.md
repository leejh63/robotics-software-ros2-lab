# 08. Runtime Observations Without Code Changes

이 문서는 코드 수정 없이 문서화만 해둔 실행상 관찰 사항이다. 지금 단계에서는 코드를 고치지 않고, 나중에 실제 프로젝트 정리나 재현성 개선 시 참고한다.

---

## 1. `lee_robot_description` 패키지 위치

현재 패키지가 일반적인 `ws/src/lee_robot_description` 구조가 아니라 아래에 있다.

```text
$ROS2_WS/lee_robot_description
```

현재 환경에서는 빌드/실행이 가능할 수 있지만, 일반적인 ROS2 workspace 구조와는 다르다.

학습 정리에서는 그대로 기록한다. 코드 구조 수정은 하지 않는다.

---

## 2. `amcl_full.launch.py`의 map 기본 경로

`amcl_full.launch.py`는 package share 경로에서 여러 단계 위로 올라가 workspace root를 추정한 뒤 `slam_map.yaml`을 찾는다.

```text
default_map_yaml = workspace_dir + /slam_map.yaml
```

현재 환경에서는 맞을 수 있지만, 다른 workspace나 install 구조에서는 깨질 수 있다.

지금은 코드 수정하지 않고, 실행 문서에서 `map_yaml:=...` 인자를 명시하는 방법을 같이 적어둔다.

---

## 3. topic remap과 frame 이름은 별개

`amcl_full.launch.py`에서 `/map`은 `/robot_ns/map`으로 remap된다.

하지만 이것은 topic 이름만 바꾸는 것이다.

```text
/scan -> /robot_ns/scan remap
  topic 이름 변경

header.frame_id: base_scan
  메시지 내부 frame 이름
```

AMCL 파라미터의 frame 값이 따로 맞아야 한다.

```yaml
global_frame_id: map_robot_ns
odom_frame_id: odom_robot_ns
base_frame_id: base_footprint
```

---

## 4. `/initialpose`는 namespace가 없는 상태로 쓰일 수 있음

현재 AMCL node가 별도 namespace 없이 `/amcl`로 뜨는 구조라면 `/initialpose`도 일반적으로 namespace 없이 사용된다.

```text
/initialpose
```

반면 map/scan/cmd_vel은 `/robot_ns/...`를 쓴다.

```text
/robot_ns/map
/robot_ns/scan
/robot_ns/cmd_vel
```

이 혼합 구조가 처음에는 헷갈릴 수 있다. 문서에서는 “AMCL 노드 자체 namespace와 topic remap은 별개”로 기록한다.

---

## 5. SLAM과 AMCL을 동시에 켜면 TF 발행 주체가 겹칠 수 있음

SLAM 중에는 SLAM Toolbox가 `map_robot_ns -> odom_robot_ns` 성격의 TF를 만든다.

AMCL 중에는 AMCL이 `map_robot_ns -> odom_robot_ns` TF를 만든다.

따라서 아래를 동시에 켜지 않는다.

```text
slam_toolbox mapping/localization
nav2_amcl
static map_robot_ns -> odom_robot_ns publisher
```

중복 발행되면 RViz에서 위치가 튀거나 TF tree가 불안정해질 수 있다.

---

## 6. world-map 짝 문제

현재 환경에는 적어도 두 조합이 존재한다.

```text
slam.world       <-> slam_map.yaml
lee_world.world  <-> room_map.yaml
```

잘못된 조합도 명령상으로는 실행될 수 있다.

```text
map은 보임
scan도 보임
하지만 벽과 scan 점이 맞지 않음
AMCL이 수렴하지 않음
```

따라서 AMCL 문제가 생기면 파라미터보다 world-map 짝을 먼저 확인한다.

---

## 7. RViz 표시가 실제 node 문제와 다를 수 있음

기록상 RViz Map display가 가끔 꺼졌다 켜야 살아나는 경우가 있었다.

이런 경우 바로 AMCL 문제로 판단하지 않는다.

먼저 CLI로 확인한다.

```bash
ros2 topic echo /robot_ns/map --once
ros2 lifecycle get /map_server
ros2 lifecycle get /amcl
```

CLI는 정상인데 RViz만 이상하면 display 설정 문제일 가능성이 크다.

---

## 8. ParticleCloud display

`/particle_cloud`는 일반 PointCloud가 아니라 Nav2 AMCL의 particle message다.

RViz에서 보려면 Nav2 관련 RViz plugin이 필요할 수 있다.

```bash
sudo apt install ros-humble-nav2-rviz-plugins
```

---

## 9. 코드 수정 후보로만 남겨둘 것

현재는 수정하지 않지만, 나중에 재현 가능한 프로젝트로 정리할 때 고려할 만한 항목:

```text
1. lee_robot_description을 ws/src 아래로 정리
2. map 파일을 package share의 maps/ 폴더로 이동
3. launch에서 workspace root 추정 대신 package share 기반 map 경로 사용
4. robot_ns namespace를 launch namespace로 일관되게 적용
5. initialpose, amcl_pose, particle_cloud도 namespace 정책을 명확히 결정
6. RViz config를 최종 실행 구조와 맞춰 정리
```

지금은 학습 기록 보존이 우선이므로 코드 변경하지 않는다.
