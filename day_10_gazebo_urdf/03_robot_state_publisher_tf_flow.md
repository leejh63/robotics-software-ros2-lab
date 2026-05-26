# 03. robot_state_publisher / robot_description / TF 흐름

## 1. robot_state_publisher가 필요한 이유

URDF/Xacro 파일은 그 자체로는 파일일 뿐이다. ROS2의 다른 노드들이 로봇의 link/joint 구조를 알게 하려면 이 구조를 ROS graph에 올려야 한다.

그 역할을 하는 대표 노드가 `robot_state_publisher`다.

```text
URDF XML 문자열
        ↓
robot_description parameter
        ↓
robot_state_publisher
        ↓
/tf, /tf_static
```

---

## 2. robot_description은 무엇인가

`robot_description`은 보통 URDF XML 문자열을 담는 파라미터다.

`display.launch.py`와 `gazebo.launch.py`에서는 아래 흐름으로 만들어진다.

```text
xacro executable
  + urdf/turtlebot.xacro
        ↓
URDF XML 문자열
        ↓
robot_description parameter
```

launch 코드 관점에서는 대략 아래 구조다.

```python
robot_description = ParameterValue(
    Command([
        FindExecutable(name='xacro'),
        ' ',
        xacro_file,
    ]),
    value_type=str,
)
```

즉 launch가 실행될 때 xacro를 직접 실행해서 URDF 문자열을 만든 뒤, `robot_state_publisher`에 넘긴다.

---

## 3. /tf와 /tf_static의 차이

TF는 좌표계 사이의 관계를 나타낸다.

| topic | 의미 | 예시 |
|---|---|---|
| `/tf_static` | 시간이 지나도 변하지 않는 고정 관계 | `base_link -> camera_link`, `base_link -> base_scan` |
| `/tf` | 시간이 지나면서 바뀌는 관계 | `odom_lee -> base_footprint`, wheel 회전 관련 동적 TF |

고정 joint는 한 번 알려주면 되므로 `/tf_static`에 가깝고, 움직이는 joint나 로봇 위치는 계속 바뀌므로 `/tf`에 가깝다.

---

## 4. joint_states가 필요한 이유

URDF에는 joint 구조가 있지만, 움직이는 joint의 현재 값은 들어 있지 않다.

예를 들어 바퀴 joint는 `continuous` joint다. 현재 바퀴가 몇 rad 회전했는지는 Gazebo가 계산해서 `/lee/joint_states`로 발행한다.

```text
Gazebo joint_state plugin
        ↓
/lee/joint_states
        ↓
robot_state_publisher
        ↓
/lee/tf
```

즉 `robot_state_publisher`는 다음 두 정보를 함께 사용한다.

```text
robot_description
  로봇의 구조

joint_states
  움직이는 joint의 현재 상태
```

---

## 5. display.launch.py와 gazebo.launch.py의 차이

### 5.1 display.launch.py

`display.launch.py`는 Gazebo 없이 RViz2에서 모델과 TF를 확인하는 용도다.

```text
xacro -> robot_description
robot_state_publisher 실행
joint_state_publisher_gui 또는 joint_state_publisher 실행
RViz2 실행
```

이 모드에서는 사용자가 GUI로 joint 값을 바꾸거나, non-GUI publisher로 기본 joint state를 공급한다.

### 5.2 gazebo.launch.py

`gazebo.launch.py`는 Gazebo와 연결되는 통합 실행이다.

```text
xacro -> robot_description
robot_state_publisher 실행
Gazebo 실행
spawn_entity.py 실행
Gazebo joint_state plugin이 /lee/joint_states 발행
RViz2 실행
```

이 모드에서는 Gazebo가 실제 바퀴 joint 상태를 계산하므로, `joint_state_publisher_gui`를 같이 띄우는 것은 피하는 것이 좋다.

---

## 6. 현재 remap 구조

현재 launch 파일은 isolation을 위해 아래 remap을 사용한다.

```text
/robot_description -> /lee/robot_description
/tf                -> /lee/tf
/tf_static         -> /lee/tf_static
/joint_states      -> /lee/joint_states
```

이 구조의 장점:

```text
여러 사람이 같은 ROS_DOMAIN_ID에서 작업할 때 topic 충돌을 줄일 수 있다.
/lee 아래로 로봇 관련 topic을 모을 수 있다.
```

주의점:

```text
ROS2의 많은 도구는 기본적으로 /tf, /tf_static을 본다.
따라서 /lee/tf, /lee/tf_static을 쓸 경우 RViz2, tf2_tools, SLAM, AMCL, Nav2 쪽에서도 remap이 맞아야 한다.
```

---

## 7. frame 이름은 remap되지 않는다

중요한 점은 topic remap과 frame 이름 변경은 다르다는 것이다.

```text
/tf -> /lee/tf
  topic 이름 remap

base_link -> lee/base_link
  이런 frame 이름 변경은 자동으로 일어나지 않음
```

현재 frame 이름은 URDF와 plugin 설정에 의해 결정된다.

```text
base_footprint
base_link
base_scan
camera_link
imu_link
odom_lee
```

따라서 namespace `/lee`를 쓴다고 해서 frame 이름이 자동으로 `/lee/base_link`가 되는 것은 아니다.

---

## 8. 확인 명령

```bash
# robot_description 확인
ros2 param get /robot_state_publisher robot_description

# TF topic 확인
ros2 topic echo /lee/tf --once
ros2 topic echo /lee/tf_static --once

# joint state 확인
ros2 topic echo /lee/joint_states --once

# TF tree PDF 생성
ros2 run tf2_tools view_frames --ros-args \
  -r /tf:=/lee/tf \
  -r /tf_static:=/lee/tf_static
```

---

## 9. 핵심 결론

```text
robot_state_publisher는 로봇을 움직이는 노드가 아니다.
URDF 구조와 joint state를 이용해 좌표계 관계를 TF로 알려주는 노드다.
```

로봇이 움직이는 것은 Gazebo diff drive plugin 또는 실제 로봇 드라이버의 역할이다.
