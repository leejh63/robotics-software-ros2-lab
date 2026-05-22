# 05. Navigation Debug Review Questions

이 문서는 Navigation Debug Deep Dive 내용을 제대로 이해했는지 점검하기 위한 질문 모음이다.

---

## 1. rosbag / frame

```text
1. ros2 bag play --remap /scan:=/robot_ns/scan은 정확히 무엇을 바꾸는가?
2. 위 remap을 해도 header.frame_id가 자동으로 base_scan이 되지 않는 이유는 무엇인가?
3. /robot_ns/tf라는 topic 이름과 map_robot_ns라는 frame 이름은 무엇이 다른가?
4. rosbag 안의 /odom message에서 header.frame_id와 child_frame_id는 각각 무엇을 의미하는가?
5. /robot_ns/scan topic이 보이는데 SLAM이 실패한다면 가장 먼저 어떤 값을 확인해야 하는가?
6. namespace 없는 bag을 robot_ns namespace 구조에 맞추려면 어떤 topic들을 remap할 가능성이 높은가?
7. frame 이름이 다른 bag을 억지로 static_transform_publisher로 연결할 때 왜 조심해야 하는가?
```

---

## 2. DWB

```text
1. planner_server와 controller_server의 역할 차이는 무엇인가?
2. DWB는 왜 여러 velocity 후보를 만든 뒤 평가하는가?
3. critic은 무엇을 평가하는 기준인가?
4. BaseObstacle critic은 어떤 상황에서 중요해지는가?
5. /robot_ns/plan은 보이는데 /robot_ns/cmd_vel이 안 보이면 어느 쪽을 의심해야 하는가?
6. /robot_ns/cmd_vel은 보이는데 Gazebo 로봇이 움직이지 않으면 어느 쪽을 의심해야 하는가?
7. DWB 문제를 확인할 때 odom_robot_ns -> base_footprint TF를 보는 이유는 무엇인가?
```

---

## 3. Behavior Tree

```text
1. bt_navigator는 직접 path와 velocity를 만드는가?
2. ComputePathToPose와 FollowPath는 각각 어떤 서버와 연결되는가?
3. Behavior Tree가 recovery behavior를 실행하는 상황은 언제인가?
4. RViz Goal은 실패하는데 CLI action goal이 성공한다면 무엇을 의심해야 하는가?
5. action goal은 들어가는데 path가 안 생기면 어디를 확인해야 하는가?
6. path는 있는데 cmd_vel이 안 나오면 BT 관점에서 어느 단계가 실패한 것인가?
7. lifecycle node가 active 상태인지 확인해야 하는 이유는 무엇인가?
```

---

## 4. 종합 판단

아래 상황을 보고 원인을 분류해보자.

```text
상황 A:
/robot_ns/scan은 보인다.
SLAM Toolbox는 scan을 drop한다.
TF 에러가 나온다.

우선 의심:
- scan header.frame_id
- /robot_ns/tf, /robot_ns/tf_static
- odom_robot_ns/base_scan transform
```

```text
상황 B:
NavigateToPose goal을 보냈다.
/robot_ns/plan은 보인다.
하지만 /robot_ns/cmd_vel이 안 나온다.

우선 의심:
- controller_server
- DWB plugin/critics
- local costmap
- odom_robot_ns -> base_footprint TF
```

```text
상황 C:
/robot_ns/cmd_vel은 나온다.
그런데 Gazebo 로봇이 움직이지 않는다.

우선 의심:
- Gazebo diff drive plugin
- /robot_ns/cmd_vel 구독 여부
- cmd_vel topic 이름 불일치
- robot spawn/plugin 문제
```

```text
상황 D:
RViz Goal 버튼으로는 실패한다.
CLI action goal은 성공한다.

우선 의심:
- RViz fixed frame
- RViz Nav2 goal action namespace
- RViz plugin 설정
- goal frame 설정
```
