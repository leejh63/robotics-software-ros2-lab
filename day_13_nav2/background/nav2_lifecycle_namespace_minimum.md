# Nav2 Lifecycle과 Namespace 최소 배경지식

Nav2를 처음 볼 때 가장 헷갈리는 부분은 lifecycle과 namespace다.

---

## 1. Lifecycle node란?

일반 ROS2 node는 실행되면 바로 동작한다고 생각하기 쉽다.  
하지만 Nav2의 주요 서버들은 lifecycle node다.

Lifecycle node는 상태를 가진다.

```text
unconfigured
  아직 설정되지 않음

inactive
  설정은 되었지만 실제 기능 수행 전

active
  실제 동작 가능 상태

finalized
  종료 상태
```

그래서 `ros2 node list`에 보인다고 해서 바로 주행 가능한 것은 아니다.

---

## 2. 왜 lifecycle이 필요한가?

Nav2는 여러 서버가 순서 있게 준비되어야 한다.

```text
map_server가 map을 준비
AMCL이 위치추정을 준비
planner_server가 costmap을 준비
controller_server가 local costmap과 odom을 준비
bt_navigator가 action을 받을 준비
```

아무 노드나 먼저 active가 되면 의존 데이터가 없어서 실패할 수 있다.  
Lifecycle은 이런 초기화 순서를 통제하기 위한 구조다.

---

## 3. Namespace란?

Namespace는 topic/node/action 이름 앞에 붙는 경로 같은 것이다.

```text
navigate_to_pose
  기본 action 이름

/robot_ns/navigate_to_pose
  robot_ns namespace 안의 action 이름
```

현재 환경은 `/robot_ns` namespace를 많이 사용한다.

```text
/robot_ns/map
/robot_ns/scan
/robot_ns/odom
/robot_ns/cmd_vel
/robot_ns/navigate_to_pose
```

---

## 4. Namespace와 frame_id는 다르다

아래 두 개는 완전히 다른 개념이다.

```text
/robot_ns/scan
  topic 이름

base_scan
  LaserScan 메시지 안의 frame_id
```

```text
/robot_ns/navigate_to_pose
  action 이름

map_robot_ns
  goal pose를 해석할 frame_id
```

topic remap을 해도 메시지 안의 frame_id가 자동으로 바뀌지는 않는다.

---

## 5. 현재 환경에서의 핵심

```text
namespace: /robot_ns
map frame: map_robot_ns
odom frame: odom_robot_ns
base frame: base_footprint
scan frame: base_scan
```

이 네 개를 섞어 쓰면 안 된다.

---

## 6. 확인 명령

```bash
ros2 node list | sort
ros2 topic list | grep -E 'robot_ns|scan|odom|cmd_vel|map|amcl|particle|initialpose'
ros2 action list | grep navigate
ros2 lifecycle get /robot_ns/planner_server
ros2 run tf2_ros tf2_echo map_robot_ns odom_robot_ns
```

