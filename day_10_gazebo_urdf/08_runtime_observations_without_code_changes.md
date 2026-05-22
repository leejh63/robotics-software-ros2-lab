# 08. Runtime Observations Without Code Changes

이 문서는 코드를 수정하지 않고, 현재 학습 코드 기준으로 실행할 때 주의해야 할 점을 기록한 것이다.

---

## 1. 패키지 위치 주의

현재 `lee_robot_description`은 압축본 기준으로 다음 위치에 있다.

```text
day_67/ws/lee_robot_description/
```

일반적인 ROS2 워크스페이스 구조에서는 패키지를 보통 `ws/src/` 아래에 둔다.

```text
ws/src/lee_robot_description/
```

현재 구조에서도 colcon이 패키지를 발견할 수는 있지만, 나중에 정식 프로젝트로 정리할 때는 `src/` 아래로 옮기는 편이 일반적이다. 다만 이번 문서 정리에서는 코드/구조를 수정하지 않았다.

---

## 2. `turtlebot_gaze.xacro` 이름

파일명은 `turtlebot_gaze.xacro`다. 역할상으로는 Gazebo plugin 설정 파일이므로 `turtlebot_gazebo.xacro`가 더 직관적일 수 있다.

하지만 현재 코드에서는 아래처럼 include한다.

```xml
<xacro:include filename="turtlebot_gaze.xacro"/>
```

파일명을 바꾸면 include도 함께 바꿔야 하므로 이번 정리에서는 실제 파일명을 그대로 사용한다.

---

## 3. `/tf`를 `/robot_ns/tf`로 remap하는 구조

현재 launch와 Gazebo plugin은 `/tf`, `/tf_static`을 `/robot_ns/tf`, `/robot_ns/tf_static`으로 remap한다.

장점:

```text
다른 사람 또는 다른 로봇과 topic 충돌을 줄일 수 있다.
```

주의점:

```text
RViz2, tf2_tools, SLAM Toolbox, AMCL, Nav2도 같은 TF remap을 받아야 한다.
기본 /tf를 기대하는 설정과 섞이면 TF가 없는 것처럼 보일 수 있다.
```

이 문제는 Day 11~13에서 특히 중요하다.

---

## 4. `use_avoidance` 기본값이 true

`gaze.launch.py`에서 `use_avoidance` 기본값은 `true`다.

즉 그냥 실행하면 `lidar_wall_follower.py`가 같이 실행되어 `/robot_ns/cmd_vel`을 발행할 수 있다.

수동 teleop을 테스트할 때는 아래처럼 끄는 것이 안전하다.

```bash
ros2 launch lee_robot_description gaze.launch.py use_avoidance:=false
```

---

## 5. teleop과 회피 노드의 `/robot_ns/cmd_vel` 충돌

`teleop_twist_keyboard`와 `lidar_wall_follower.py`가 동시에 실행되면 둘 다 `/robot_ns/cmd_vel`을 발행한다.

증상:

```text
키보드 조작을 했는데 로봇이 다시 회전함
멈추려 했는데 다시 움직임
움직임이 튐
```

확인:

```bash
ros2 topic info /robot_ns/cmd_vel -v
```

Publisher가 2개 이상이면 누가 발행 중인지 확인해야 한다.

---

## 6. LaserScan QoS

`/robot_ns/scan`이 RViz2나 echo에서 안 보일 때는 QoS 문제일 수 있다.

```bash
ros2 topic echo /robot_ns/scan --qos-reliability best_effort --once
ros2 topic hz /robot_ns/scan --qos-reliability best_effort
```

RViz2 LaserScan display에서도 Reliability Policy를 `Best Effort`로 맞춰야 할 수 있다.

---

## 7. Gazebo entity 중복

`spawn_entity.py`는 `turtlebot_lee`라는 entity 이름으로 로봇을 생성한다.

이미 같은 entity가 있으면 spawn 실패가 날 수 있다.

삭제:

```bash
ros2 run gazebo_ros delete_entity.py -entity turtlebot_lee
```

또는 Gazebo를 완전히 종료한 뒤 다시 실행한다.

```bash
pkill -f gzserver
pkill -f gzclient
pkill -f gazebo
```

---

## 8. `/clock` publisher 중복

Gazebo나 rosbag이 여러 개 켜져 있으면 `/clock`이 여러 곳에서 발행될 수 있다.

증상:

```text
Detected jump back in time
Moved backwards in time
Message Filter dropping message
```

확인:

```bash
ros2 topic info /clock -v
```

Gazebo/rosbag/RViz를 정리하고 하나만 남기는 것이 좋다.

---

## 9. world 파일명 주의

현재 실제 world 파일은 다음이다.

```text
lee_world.world
simple_maze.world
slam.world
```

기존 일부 설명에서 `obstacle_world.world` 같은 이름이 섞일 수 있는데, 현재 압축본 기준 실제 파일 목록에는 없다. 문서에서는 실제 파일명을 기준으로 정리했다.

---

## 10. 코드 수정 여부

이번 문서 정리에서는 위 항목을 코드 수정으로 해결하지 않았다.

```text
현재 목적: 학습 문서화
아직 목적이 아닌 것: 패키지 구조 정리, 파일명 변경, launch 리팩토링, topic/frame 설계 변경
```
