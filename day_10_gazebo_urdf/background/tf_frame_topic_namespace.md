# Background - TF frame, Topic, Namespace 구분

## 1. Topic

Topic은 ROS2 메시지가 흐르는 통신 채널이다.

```text
/robot_ns/scan
/robot_ns/odom
/robot_ns/cmd_vel
/robot_ns/image_raw
```

Topic 이름은 remap이나 namespace로 바꿀 수 있다.

---

## 2. Frame

Frame은 좌표계 이름이다.

```text
base_link
base_footprint
base_scan
camera_link
odom_robot_ns
map
```

Frame 이름은 메시지의 `header.frame_id`, URDF link 이름, plugin 설정 등으로 결정된다.

---

## 3. Namespace

Namespace는 topic/service/action/node 이름을 묶는 이름공간이다.

```text
/scan -> /robot_ns/scan
/odom -> /robot_ns/odom
/cmd_vel -> /robot_ns/cmd_vel
```

하지만 namespace를 쓴다고 frame 이름이 자동으로 바뀌지는 않는다.

```text
Topic: /robot_ns/scan
Frame: base_scan
```

이 둘은 동시에 존재할 수 있으며 전혀 모순이 아니다.

---

## 4. 왜 이 구분이 중요한가

SLAM/AMCL/Nav2는 topic과 frame을 모두 본다.

```text
어떤 topic에서 LaserScan을 받을 것인가?
그 LaserScan은 어느 frame 기준인가?
그 frame은 TF tree에서 map/odom/base와 연결되는가?
```

따라서 topic 이름만 맞추고 frame 연결이 틀리면 동작하지 않을 수 있다.
