# Background - Simulation Time과 /clock

## 1. wall time과 simulation time

ROS2 노드는 기본적으로 컴퓨터 실제 시간을 사용한다. 이를 wall time이라고 볼 수 있다.

Gazebo나 rosbag을 사용할 때는 시뮬레이션 시간이 따로 흐른다. 이 시간은 `/clock` topic으로 발행된다.

```text
Gazebo or rosbag --clock
        ↓
/clock
        ↓
use_sim_time:=true인 ROS2 노드
```

---

## 2. use_sim_time

`use_sim_time:=true`로 설정된 노드는 실제 시간이 아니라 `/clock`을 기준으로 동작한다.

SLAM/AMCL/Nav2에서는 센서 메시지 timestamp와 TF timestamp가 중요하기 때문에, 같은 시간 기준을 써야 한다.

---

## 3. 문제가 생기는 경우

```text
Gazebo는 simulation time 사용
RViz2는 wall time 사용
SLAM은 simulation time 사용 안 함
rosbag은 --clock 없이 재생
/clock publisher가 여러 개
```

이런 경우 아래 문제가 나올 수 있다.

```text
Message Filter dropping message
Extrapolation into the future
Detected jump back in time
Moved backwards in time
```

---

## 4. 확인 명령

```bash
ros2 topic echo /clock --once
ros2 topic info /clock -v
ros2 param get /robot_ns_robot_state_publisher use_sim_time
ros2 param get /rviz use_sim_time
```

노드 이름은 실제 실행 상태에 따라 다를 수 있다.
