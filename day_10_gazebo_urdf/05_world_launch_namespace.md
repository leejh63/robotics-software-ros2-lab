# 05. Gazebo World / Launch / Namespace 정리

## 1. World 파일의 역할

로봇 모델이 있어도 로봇이 놓일 환경이 없으면 시뮬레이션을 구성할 수 없다. Gazebo world 파일은 로봇이 돌아다닐 공간을 정의한다.

현재 패키지에는 다음 world 파일이 있다.

| 파일 | 역할 |
|---|---|
| `worlds/lee_world.world` | Day 10 Gazebo 기본 실행 world |
| `worlds/simple_maze.world` | 미로/장애물 형태의 world |
| `worlds/slam.world` | SLAM 실습에 적합한 벽/장애물 world |

World 파일은 대략 다음을 정의한다.

```text
physics
  시간 간격, 물리 엔진 설정

ground_plane / sun
  바닥과 조명

static model
  벽, 박스, 원통, 장애물
```

로봇은 world 파일 안에 미리 넣을 수도 있고, 이번 실습처럼 `spawn_entity.py`로 이후 넣을 수도 있다.

---

## 2. Gazebo 실행에 필요한 ROS plugin

`gazebo.launch.py`는 Gazebo를 실행할 때 아래 plugin을 로드한다.

```text
-s libgazebo_ros_init.so
-s libgazebo_ros_factory.so
```

| plugin | 역할 |
|---|---|
| `libgazebo_ros_init.so` | Gazebo 안에서 ROS2 초기화 |
| `libgazebo_ros_factory.so` | ROS2 명령으로 Gazebo에 entity를 spawn/delete할 수 있게 함 |

`spawn_entity.py`를 쓰려면 `libgazebo_ros_factory.so`가 필요하다.

---

## 3. spawn_entity.py의 역할

`spawn_entity.py`는 Gazebo 안에 로봇 모델을 생성하는 도구다.

현재 `gazebo.launch.py`에서는 다음과 같은 의미로 실행된다.

```text
-topic /lee/robot_description
-entity turtlebot
-z 0.1
```

해석:

```text
/lee/robot_description topic에서 URDF XML을 읽는다.
Gazebo 안에 turtlebot라는 entity 이름으로 로봇을 생성한다.
처음 z 위치는 0.1m로 둔다.
```

구분해야 할 이름:

```text
Gazebo entity name: turtlebot
URDF robot name:    turtlebot
ROS namespace:      /lee
base frame:         base_footprint 또는 base_link
```

이 네 개는 같은 개념이 아니다.

---

## 4. launch 파일의 역할

Launch 파일은 단순히 여러 명령어를 순서대로 실행하는 쉘 스크립트가 아니다. ROS graph 구성을 선언하는 파일이다.

`gazebo.launch.py`가 묶는 요소:

```text
1. xacro 변환
2. robot_state_publisher 실행
3. Gazebo 실행
4. spawn_entity.py 실행
5. RViz2 실행
6. lidar_wall_follower.py 조건부 실행
7. remap과 parameter 설정
```

주요 launch argument:

| argument | 기본값 | 의미 |
|---|---:|---|
| `use_sim_time` | `true` | Gazebo `/clock` 사용 |
| `use_rviz` | `true` | RViz2 실행 여부 |
| `use_avoidance` | `false` | LiDAR 회피 노드 실행 여부 |
| `namespace` | `lee` | robot topic namespace |
| `odom_frame` | `odom_lee` | Gazebo odometry frame |
| `entity_name` | `turtlebot` | Gazebo entity 이름 |
| `spawn_z` | `0.1` | Gazebo spawn 높이 |

확인:

```bash
ros2 launch lee_robot_description gazebo.launch.py --show-args
```

---

## 5. Namespace와 remap

현재 실습은 기본값으로 `/lee` namespace를 사용한다. `gazebo.launch.py`에서는 `namespace:=...` 인자로 이 값을 바꿀 수 있다.

Gazebo plugin 내부:

```xml
<ros>
  <namespace>/lee</namespace>
</ros>
```

이렇게 되어 있으면 상대 topic은 `/lee` 아래로 들어간다.

```text
cmd_vel -> /lee/cmd_vel
odom    -> /lee/odom
scan    -> /lee/scan
imu     -> /lee/imu
```

Launch의 remap:

```text
/robot_description -> /lee/robot_description
/tf                -> /lee/tf
/tf_static         -> /lee/tf_static
/joint_states      -> /lee/joint_states
```

---

## 6. Namespace와 frame_id는 다르다

가장 중요한 구분이다.

```text
namespace
  ROS topic/service/action 이름을 나누는 용도
  예: /lee/scan, /lee/odom, /lee/cmd_vel

frame_id
  좌표계 이름
  예: base_scan, base_link, odom_lee, camera_link
```

`/lee/scan`이라는 topic으로 LaserScan이 발행되더라도, 메시지 내부의 `header.frame_id`는 `base_scan`일 수 있다.

```text
Topic: /lee/scan
Message header.frame_id: base_scan
```

SLAM/AMCL/Nav2는 topic 이름뿐 아니라 frame 이름도 함께 본다. 그래서 둘을 분리해서 이해해야 한다.

---

## 7. /clock과 use_sim_time

Gazebo를 실행하면 `/clock` topic이 발행된다. ROS2 노드가 Gazebo 시간을 사용하려면 `use_sim_time`이 `true`여야 한다.

```text
Gazebo
  -> /clock

ROS2 node with use_sim_time:=true
  -> wall time 대신 /clock 기준 시간 사용
```

SLAM/AMCL/Nav2에서는 시간 동기화가 매우 중요하다. sensor message의 timestamp와 TF timestamp가 맞지 않으면 아래 같은 문제가 생길 수 있다.

```text
Extrapolation into the future
Lookup would require extrapolation
Message Filter dropping message
```

---

## 8. 핵심 결론

```text
world는 환경을 정의한다.
launch는 world, robot model, Gazebo, spawn, RViz, remap을 하나로 묶는다.
namespace는 topic 충돌을 줄이지만 frame 이름까지 자동으로 바꾸지는 않는다.
```
