# 08. 실행 관찰 메모

이 문서는 현재 학습 코드 기준으로 실행할 때 헷갈리기 쉬운 점과 확인 기준을 정리한 것이다.

---

## 1. 패키지 위치 주의

현재 `lee_robot_description`은 navigation project 기준으로 다음 위치에 있다.

```text
projects/ros2_navigation_lab/src/lee_robot_description/
```

일반적인 ROS2 워크스페이스 구조에서는 패키지를 보통 `ws/src/` 아래에 둔다.

```text
ws/src/lee_robot_description/
```

현재 project는 일반적인 `src/` 하위 패키지 구조를 이미 사용한다.

---

## 2. `turtlebot_gaze.xacro` 이름

파일명은 `turtlebot_gaze.xacro`다. 역할상으로는 Gazebo plugin 설정 파일이므로 `turtlebot_gazebo.xacro`가 더 직관적일 수 있다.

하지만 현재 코드에서는 아래처럼 include한다.

```xml
<xacro:include filename="turtlebot_gaze.xacro"/>
```

파일명을 바꾸면 include도 함께 바꿔야 하므로 문서에서는 실제 파일명을 기준으로 설명한다.

---

## 3. `/tf`를 `/lee/tf`로 remap하는 구조

현재 launch와 Gazebo plugin은 `/tf`, `/tf_static`을 `/lee/tf`, `/lee/tf_static`으로 remap한다.

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

## 4. `use_avoidance` 기본값이 false

`gazebo.launch.py`에서 `use_avoidance` 기본값은 `false`다.

즉 그냥 실행하면 `lidar_wall_follower.py`가 같이 실행되지 않는다.

회피 노드를 함께 보고 싶을 때만 아래처럼 켠다.

```bash
ros2 launch lee_robot_description gazebo.launch.py use_avoidance:=true
```

---

## 5. teleop과 회피 노드의 `/lee/cmd_vel` 충돌

`teleop_twist_keyboard`와 `lidar_wall_follower.py`가 동시에 실행되면 둘 다 `/lee/cmd_vel`을 발행한다.

증상:

```text
키보드 조작을 했는데 로봇이 다시 회전함
멈추려 했는데 다시 움직임
움직임이 튐
```

확인:

```bash
ros2 topic info /lee/cmd_vel -v
```

Publisher가 2개 이상이면 누가 발행 중인지 확인해야 한다.

---

## 6. LaserScan QoS

`/lee/scan`이 RViz2나 echo에서 안 보일 때는 QoS 문제일 수 있다.

```bash
ros2 topic echo /lee/scan --qos-reliability best_effort --once
ros2 topic hz /lee/scan --qos-reliability best_effort
```

RViz2 LaserScan display에서도 Reliability Policy를 `Best Effort`로 맞춰야 할 수 있다.

---

## 7. Gazebo entity 중복

`spawn_entity.py`는 `turtlebot`라는 entity 이름으로 로봇을 생성한다.

이미 같은 entity가 있으면 spawn 실패가 날 수 있다.

삭제:

```bash
ros2 run gazebo_ros delete_entity.py -entity turtlebot
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
