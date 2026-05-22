# Day 12 AMCL에서 Day 13 Nav2로 이어지는 연결

Day 12는 저장된 지도 위에서 현재 위치를 추정하는 단계다.  
Day 13은 그 위치 추정 결과를 사용해 목표 지점까지 이동하는 단계다.

---

## 1. Day 12의 출력

AMCL이 만들어주는 핵심 출력은 아래다.

```text
/amcl_pose
  지도 기준 현재 pose 추정 결과

/particle_cloud
  여러 pose 후보의 분포

map_robot_ns -> odom_robot_ns TF
  지도 좌표계와 odom 좌표계를 연결하는 transform
```

---

## 2. Day 13에서 이 출력이 필요한 이유

Nav2는 목표 지점까지 가려면 현재 위치를 알아야 한다.

```text
현재 위치 + 목표 위치 + 지도/costmap -> path
```

현재 위치를 모르면 path를 만들 수 없다.  
또 path를 만들더라도 controller가 로봇 기준으로 추종할 수 없다.

---

## 3. 연결 흐름

```text
map_server
  -> /robot_ns/map

AMCL
  /robot_ns/map + /robot_ns/scan + odom TF
  -> /amcl_pose
  -> map_robot_ns -> odom_robot_ns

Nav2 planner_server
  map_robot_ns 기준 현재 위치 + goal
  -> /robot_ns/plan

Nav2 controller_server
  /robot_ns/plan + odom_robot_ns/base_footprint + local_costmap
  -> /robot_ns/cmd_vel
```

---

## 4. 실패가 전파되는 방식

```text
AMCL 초기 위치가 틀림
  -> 현재 위치가 지도에서 틀어짐
  -> planner가 이상한 path 생성
  -> controller가 이상한 방향으로 이동

map_robot_ns -> odom_robot_ns TF 없음
  -> Nav2가 현재 위치를 계산하지 못함
  -> action goal 실패 또는 costmap transform 오류

/robot_ns/scan 없음
  -> AMCL 위치 보정 실패
  -> local/global obstacle layer도 제대로 동작하지 않음
```

---

## 5. 확인 명령

Day 13에 들어가기 전 Day 12 출력이 살아 있는지 확인한다.

```bash
ros2 topic echo /robot_ns/map --once
ros2 topic hz /robot_ns/scan
ros2 topic echo /amcl_pose --once
ros2 topic echo /particle_cloud --once
ros2 run tf2_ros tf2_echo map_robot_ns odom_robot_ns
ros2 run tf2_ros tf2_echo odom_robot_ns base_footprint
```

이게 안 되면 Nav2를 먼저 고치면 안 된다.  
AMCL/localization부터 정상화해야 한다.

