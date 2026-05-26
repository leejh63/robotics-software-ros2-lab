# 01. rosbag topic remap vs frame_id

이 문서는 rosbag을 재생할 때 자주 생기는 혼동을 정리한다.

핵심은 하나다.

```text
ros2 bag play --remap은 topic 이름을 바꾼다.
하지만 message 안의 header.frame_id, child_frame_id는 자동으로 바꾸지 않는다.
```

이 차이를 모르면 `/scan`을 `/robot_ns/scan`으로 remap했는데도 SLAM/AMCL/Nav2가 실패하는 이유를 이해하기 어렵다.

---

## 1. 먼저 구분해야 하는 4가지 이름

ROS2 Navigation에서 이름은 크게 네 종류가 섞여 나온다.

| 종류 | 예시 | 의미 |
|---|---|---|
| topic 이름 | `/robot_ns/scan`, `/robot_ns/odom`, `/robot_ns/tf` | 노드들이 데이터를 주고받는 통신 채널 이름 |
| namespace | `/robot_ns` | 노드/topic/action 이름 앞에 붙는 이름 공간 |
| frame 이름 | `map_robot_ns`, `odom_robot_ns`, `base_footprint`, `base_scan` | 좌표계 이름 |
| message 내부 필드 | `header.frame_id`, `child_frame_id` | 이 데이터가 어느 좌표계 기준인지 알려주는 값 |

중요한 점:

```text
/robot_ns/scan은 topic 이름이다.
base_scan은 frame 이름이다.
/robot_ns/tf는 topic 이름이다.
map_robot_ns, odom_robot_ns, base_footprint는 TF message 안에 들어 있는 frame 이름이다.
```

---

## 2. topic remap이 실제로 바꾸는 것

예를 들어 rosbag 안에 이런 LaserScan이 있다고 하자.

```text
topic: /scan
message type: sensor_msgs/msg/LaserScan
header.frame_id: laser
```

이걸 아래처럼 재생한다.

```bash
ros2 bag play rosbag2_xxx --remap /scan:=/robot_ns/scan
```

그러면 바뀌는 것은 topic 이름이다.

```text
topic: /robot_ns/scan
header.frame_id: laser
```

`header.frame_id`는 그대로 `laser`다.

즉, `/robot_ns/scan`으로 들어온 scan이라고 해서 자동으로 `base_scan` 기준의 scan이 되는 것이 아니다.

---

## 3. TF topic remap도 frame 이름을 바꾸지 않는다

TF도 마찬가지다.

rosbag 안의 TF message가 다음 관계를 담고 있다고 하자.

```text
odom -> base_link
base_link -> laser
```

이걸 아래처럼 remap한다.

```bash
ros2 bag play rosbag2_xxx \
  --remap /tf:=/robot_ns/tf \
  --remap /tf_static:=/robot_ns/tf_static
```

그러면 TF가 발행되는 topic은 바뀐다.

```text
/tf        -> /robot_ns/tf
/tf_static -> /robot_ns/tf_static
```

하지만 TF message 내부의 frame 이름은 그대로다.

```text
odom -> base_link
base_link -> laser
```

이름이 자동으로 아래처럼 바뀌지 않는다.

```text
odom_robot_ns -> base_footprint
base_footprint -> base_scan
```

따라서 topic remap과 frame rename은 완전히 다른 문제다.

---

## 4. 예시 환경 기준으로 필요한 frame chain

현재 정리본에서 기준으로 삼는 네 환경은 대략 다음 구조다.

```text
map_robot_ns
  -> odom_robot_ns
      -> base_footprint
          -> base_link
              -> base_scan
```

SLAM/AMCL/Nav2는 상황에 따라 이 관계를 사용한다.

```text
SLAM Toolbox
  /robot_ns/scan을 받음
  scan의 header.frame_id를 확인함
  base_scan에서 odom_robot_ns 또는 base_footprint로 가는 TF를 찾음
  map_robot_ns를 생성함

AMCL
  /robot_ns/scan을 받음
  scan과 저장된 map을 비교함
  map_robot_ns -> odom_robot_ns TF를 추정함

Nav2
  map_robot_ns, odom_robot_ns, base_footprint 관계를 사용함
  costmap에서 /robot_ns/scan을 장애물로 반영함
  controller가 /robot_ns/cmd_vel을 생성함
```

따라서 `/robot_ns/scan` topic이 보인다는 것만으로는 충분하지 않다.

아래도 맞아야 한다.

```text
/robot_ns/scan의 header.frame_id가 TF tree 안에 존재해야 한다.
그 frame에서 base_footprint, odom_robot_ns 등으로 변환 가능해야 한다.
SLAM/AMCL/Nav2 parameter의 frame 이름과 실제 TF frame 이름이 맞아야 한다.
```

---

## 5. rosbag 재생 시 자주 생기는 실패 패턴

### 패턴 A. `/scan`만 remap하고 `/tf`를 remap하지 않음

명령:

```bash
ros2 bag play rosbag2_xxx --remap /scan:=/robot_ns/scan
```

증상:

```text
/robot_ns/scan은 보인다.
하지만 /robot_ns/tf에는 필요한 transform이 없다.
SLAM/AMCL이 scan frame을 해석하지 못한다.
```

의심:

```text
/tf, /tf_static도 현재 launch 구조와 맞게 remap해야 할 수 있다.
```

예:

```bash
ros2 bag play rosbag2_xxx \
  --clock \
  --remap /scan:=/robot_ns/scan \
  --remap /odom:=/robot_ns/odom \
  --remap /tf:=/robot_ns/tf \
  --remap /tf_static:=/robot_ns/tf_static
```

단, 이렇게 해도 frame 이름 자체가 바뀌는 것은 아니다.

---

### 패턴 B. topic은 맞는데 scan frame이 다름

예:

```text
/robot_ns/scan
  header.frame_id: laser
```

하지만 현재 로봇 TF는 다음을 기대한다.

```text
base_scan
```

증상:

```text
Frame laser does not exist
Could not transform from laser to base_footprint
Message Filter dropping message
```

의심:

```text
bag이 현재 로봇 모델의 frame 체계와 다르다.
```

---

### 패턴 C. `/odom` topic은 맞는데 frame이 다름

예:

```text
/robot_ns/odom
  header.frame_id: odom
  child_frame_id: base_link
```

현재 Nav2 설정:

```text
odom frame: odom_robot_ns
base frame: base_footprint
```

증상:

```text
Nav2가 robot pose를 못 찾는다.
local costmap이 robot pose를 가져오지 못한다.
controller_server가 path는 받아도 cmd_vel을 못 낸다.
```

의심:

```text
odom message 내부 frame과 nav2_params.yaml의 frame 설정이 맞지 않는다.
```

---

### 패턴 D. `/clock` 없이 use_sim_time만 켬

rosbag, Gazebo, SLAM/AMCL/Nav2를 사용할 때 `use_sim_time`이 켜져 있으면 `/clock`이 필요하다.

증상:

```text
노드는 떠 있는데 시간이 흐르지 않는 것처럼 보인다.
message timestamp가 맞지 않는다.
TF extrapolation 에러가 난다.
```

rosbag 재생 시:

```bash
ros2 bag play rosbag2_xxx --clock
```

그리고 노드들이 `use_sim_time:=true`를 사용하고 있는지 확인한다.

---

## 6. 확인 명령어

### bag 안에 어떤 topic이 있는지 확인

```bash
ros2 bag info rosbag2_xxx
```

확인할 것:

```text
/scan인지 /robot_ns/scan인지
/odom인지 /robot_ns/odom인지
/tf, /tf_static이 들어 있는지
/clock이 있는지
```

---

### scan message의 frame_id 확인

```bash
ros2 topic echo /robot_ns/scan --once --field header.frame_id
```

또는 전체 header 확인:

```bash
ros2 topic echo /robot_ns/scan --once --field header
```

확인할 것:

```text
base_scan인가?
laser인가?
다른 이름인가?
```

---

### odom message의 frame 확인

```bash
ros2 topic echo /robot_ns/odom --once --field header.frame_id
ros2 topic echo /robot_ns/odom --once --field child_frame_id
```

확인할 것:

```text
header.frame_id가 odom_robot_ns인가?
child_frame_id가 base_footprint 또는 base_link인가?
```

---

### TF tree 확인

```bash
ros2 run tf2_tools view_frames
```

또는 특정 transform 확인:

```bash
ros2 run tf2_ros tf2_echo odom_robot_ns base_footprint
ros2 run tf2_ros tf2_echo base_footprint base_scan
ros2 run tf2_ros tf2_echo map_robot_ns base_footprint
```

SLAM 전에는 `map_robot_ns -> odom_robot_ns`가 없을 수 있다. SLAM 또는 AMCL이 올라온 뒤 확인해야 한다.

---

### 현재 topic 목록 확인

```bash
ros2 topic list | sort
```

확인할 것:

```text
/robot_ns/scan
/robot_ns/odom
/robot_ns/tf
/robot_ns/tf_static
/robot_ns/map
/clock
```

---

## 7. 예시 환경 기준 재생 예시

현재 `/robot_ns` namespace 구조에 맞추려면, namespace 없는 bag은 보통 아래처럼 재생을 시도할 수 있다.

```bash
ros2 bag play rosbag2_2026_05_13-16_27_44 \
  --clock \
  --remap /scan:=/robot_ns/scan \
  --remap /odom:=/robot_ns/odom \
  --remap /tf:=/robot_ns/tf \
  --remap /tf_static:=/robot_ns/tf_static
```

하지만 이 명령이 항상 성공을 보장하지 않는다.

이유:

```text
토픽 이름은 /robot_ns 구조로 바뀐다.
하지만 message 내부 frame_id는 bag에 기록된 원래 값 그대로다.
```

그래서 반드시 아래를 확인해야 한다.

```bash
ros2 topic echo /robot_ns/scan --once --field header.frame_id
ros2 topic echo /robot_ns/odom --once --field header.frame_id
ros2 topic echo /robot_ns/odom --once --field child_frame_id
ros2 run tf2_tools view_frames
```

---

## 8. 해결 방향

문제가 생겼을 때 해결 방향은 세 가지다.

### 방향 1. 현재 frame 구조와 맞는 bag 사용

가장 안전하다.

```text
현재 로봇이 발행한 /robot_ns/scan, /robot_ns/odom, /robot_ns/tf, /robot_ns/tf_static을 그대로 녹화한 bag을 사용한다.
```

---

### 방향 2. launch/config의 frame 설정을 bag에 맞춤

예를 들어 bag의 frame이 다음과 같다면:

```text
odom -> base_link -> laser
```

SLAM/AMCL/Nav2 설정도 그 frame 이름을 기준으로 맞춰야 한다.

단, 이건 현재 정리본의 코드 수정/재현성 개선 범위는 아니다.

---

### 방향 3. frame 변환을 추가로 제공

예를 들어 scan frame이 `laser`인데 실제 로봇의 LiDAR frame처럼 쓰려면 static transform을 추가할 수 있다.

```bash
ros2 run tf2_ros static_transform_publisher \
  0 0 0 0 0 0 \
  base_footprint laser
```

하지만 이건 조심해야 한다.

```text
실제로 물리적 관계가 맞을 때만 써야 한다.
이름만 억지로 맞추려고 잘못된 static TF를 넣으면 map/localization이 틀어진다.
```

---

## 9. 핵심 결론

```text
rosbag replay 문제는 topic 이름 문제와 frame 이름 문제가 섞여 있다.
--remap은 topic 이름만 바꾼다.
header.frame_id와 child_frame_id는 자동으로 바뀌지 않는다.
SLAM/AMCL/Nav2는 topic을 받는 것뿐 아니라, 그 message의 frame을 TF tree에서 해석할 수 있어야 한다.
```

따라서 bag을 재생할 때는 항상 아래 순서로 확인한다.

```text
1. ros2 bag info로 topic 목록 확인
2. --remap으로 현재 topic 구조에 맞춤
3. /robot_ns/scan header.frame_id 확인
4. /robot_ns/odom header.frame_id / child_frame_id 확인
5. /robot_ns/tf, /robot_ns/tf_static 확인
6. view_frames로 TF tree 확인
7. SLAM/AMCL/Nav2 parameter의 frame 이름과 비교
```
