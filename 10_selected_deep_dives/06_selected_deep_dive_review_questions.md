# Selected Deep Dive Review Questions

이 문서는 선별 심화 문서를 읽은 뒤 스스로 점검하기 위한 질문 모음이다.

---

## 1. TF / Topic / Namespace / Frame ID

```text
1. /robot_ns/scan과 base_scan은 각각 무엇인가?
2. /robot_ns/tf와 map_robot_ns는 각각 무엇인가?
3. topic remap을 하면 header.frame_id도 자동으로 바뀌는가?
4. namespace는 topic/node/action 이름에 주로 적용되는가, frame_id에 적용되는가?
5. RViz Fixed Frame이 map인데 실제 frame이 map_robot_ns라면 어떤 문제가 생길 수 있는가?
```

---

## 2. LaserScan / Odometry / TF / SLAM

```text
1. LaserScan의 ranges[index] 방향은 어떻게 계산하는가?
2. LaserScan 하나만으로는 왜 map을 만들 수 없는가?
3. /robot_ns/odom은 SLAM에서 어떤 역할을 하는가?
4. SLAM Toolbox가 map_robot_ns -> odom_robot_ns TF를 발행하는 이유는 무엇인가?
5. rosbag replay에서 topic remap과 frame_id 불일치는 왜 별개 문제인가?
```

---

## 3. SLAM vs AMCL

```text
1. SLAM과 AMCL의 목적 차이는 무엇인가?
2. AMCL은 map을 새로 만드는가?
3. SLAM과 AMCL을 동시에 켰을 때 map_robot_ns -> odom_robot_ns TF가 충돌할 수 있는 이유는 무엇인가?
4. Gazebo diff_drive는 보통 map->odom과 odom->base 중 어느 쪽을 담당하는가?
5. Nav2 주행 전에 AMCL이 준비되어야 하는 이유는 무엇인가?
```

---

## 4. AMCL 파라미터

```text
1. min_particles와 max_particles는 무엇을 조절하는가?
2. alpha 값이 커지면 particle 분포는 어떤 경향을 가지는가?
3. likelihood_field 방식은 beam endpoint를 무엇과 비교하는가?
4. max_beams는 계산량과 어떤 관계가 있는가?
5. update_min_d와 update_min_a는 AMCL update 빈도와 어떤 관계가 있는가?
6. initialpose가 실제 위치와 크게 다르면 어떤 일이 생길 수 있는가?
```

---

## 5. Nav2 goal -> cmd_vel

```text
1. NavigateToPose action goal은 바로 /robot_ns/cmd_vel로 바뀌는가?
2. bt_navigator, planner_server, controller_server의 역할은 각각 무엇인가?
3. global costmap과 local costmap의 frame은 내 환경에서 각각 무엇인가?
4. DWB controller는 속도 후보를 어떻게 고르는가?
5. /robot_ns/cmd_vel은 나오는데 로봇이 안 움직이면 어느 쪽을 의심해야 하는가?
6. RViz Goal 실패와 CLI action goal 성공은 무엇을 의미할 수 있는가?
```

---

## 6. 최소 자기 설명 목표

선별 심화 문서를 끝낸 뒤에는 아래 내용을 말로 설명할 수 있으면 충분하다.

```text
내 Gazebo 로봇은 /robot_ns/scan, /robot_ns/odom, /robot_ns/tf를 낸다.
SLAM은 이 데이터를 이용해 /robot_ns/map과 map_robot_ns->odom_robot_ns를 만든다.
AMCL은 저장된 map과 현재 scan을 비교해 현재 pose를 찾고 map_robot_ns->odom_robot_ns를 발행한다.
Nav2는 AMCL pose, costmap, goal을 이용해 path와 velocity command를 만들고 /robot_ns/cmd_vel로 내보낸다.
이 과정에서 topic 이름과 frame 이름은 다르며, topic remap은 frame_id를 자동으로 바꾸지 않는다.
```
