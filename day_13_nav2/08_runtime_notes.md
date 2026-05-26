# 08. Nav2 실행 관찰 메모

이 문서는 현재 구조를 기준으로 Nav2 실행 중 주의할 점과 확인 기준을 정리한다.

---

## 1. `nav2.launch.py`와 `nav2_navigation.launch.py`가 분리되어 있음

현재 구조는 아래처럼 나뉜다.

```text
nav2.launch.py
  simulation + localization

nav2_navigation.launch.py
  navigation stack
```

이 구조는 학습/디버깅에는 좋다.  
하지만 실행할 때 두 터미널을 모두 띄워야 한다.

---

## 2. map_server/amcl 노드 이름과 topic namespace가 다를 수 있음

`nav2.launch.py`에서는 `map_server`, `amcl` 노드 이름에 `/robot_ns` namespace를 직접 붙이지 않는다.

하지만 topic remap은 `/robot_ns/map`, `/robot_ns/tf`, `/robot_ns/tf_static` 쪽으로 걸려 있다.

그래서 아래 두 상황이 동시에 가능하다.

```text
node: /amcl
topic: /robot_ns/map, /robot_ns/scan, /robot_ns/tf
```

노드 이름과 topic 이름을 같은 기준으로 보면 안 된다.

---

## 3. `map_yaml` 기본 경로는 workspace root를 추정함

`nav2.launch.py`는 기본 map 경로를 package share directory에서 위로 올라가 workspace root를 추정한 뒤 `slam_map.yaml`을 찾는 구조다.

학습 환경에서는 동작할 수 있지만, 패키지 설치 구조나 위치가 달라지면 깨질 수 있다.

패키지 설치 구조나 위치가 달라질 수 있으므로 실행 시 경로를 명시하는 편이 안전하다.

---

## 4. RViz Nav2 Goal 버튼과 CLI goal은 다르게 봐야 함

현재 기록 기준:

```text
CLI /robot_ns/navigate_to_pose action goal은 주행 확인됨
RViz Nav2 Goal 버튼은 namespace/action 연결 문제가 있을 수 있음
```

따라서 RViz 버튼이 안 된다고 바로 Nav2 서버 전체 문제로 판단하면 안 된다.

---

## 5. `/robot_ns/cmd_vel` publisher 충돌 가능성

Day 10의 wall follower, teleop, 직접 만든 test publisher, Nav2 controller가 동시에 `/robot_ns/cmd_vel`에 publish하면 충돌할 수 있다.

확인:

```bash
ros2 topic info /robot_ns/cmd_vel -v
```

자율주행 테스트 중에는 teleop이나 wall follower를 꺼두는 것이 좋다.

---

## 6. local_costmap에 static_layer가 없음

현재 `nav2_params.yaml` 기준으로 local costmap은 아래 구조다.

```text
local_costmap
  obstacle_layer
  inflation_layer
```

이건 이상한 설정이 아니다.  
local costmap은 `odom_robot_ns` 기준 rolling window로 주변 장애물을 보는 것이 핵심이기 때문이다.

---

## 7. DWB critic 설정은 namespace/parameter 구조에 민감함

`No critics defined for FollowPath`가 나오면 대부분 아래를 의심해야 한다.

```text
controller_server가 기대한 namespace로 떠 있지 않음
params_file이 잘못 들어감
FollowPath 하위 critics indentation 문제
controller_plugins 이름과 FollowPath 키 불일치
```

확인:

```bash
ros2 param get /robot_ns/controller_server controller_plugins
ros2 param get /robot_ns/controller_server FollowPath.critics
```

---

## 8. map/world 불일치 문제

world와 map이 다르면 AMCL이 수렴하지 않는다.  
AMCL이 흔들리면 Nav2가 경로를 만들어도 주행이 이상해진다.

현재 문서 기준 권장 조합:

```text
slam.world       <-> slam_map.yaml
lee_world.world  <-> room_map.yaml
```

---

## 9. 현재 구조에서 주의할 점

이 문서의 목적은 코드 개선이 아니라 학습 정리다.

```text
현재 코드가 어떤 구조인지 이해
실행 중 주의점을 문서화
프로젝트화할 때 고칠 후보만 분리
```

따라서 현재 문서에서는 실행 전 확인 기준을 먼저 분리해서 정리한다.
