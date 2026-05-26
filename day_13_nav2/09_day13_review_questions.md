# 09. Day 13 복습 질문

Day 13을 제대로 이해했는지 확인하기 위한 질문이다.  
명령어를 외우는 것보다, 아래 질문에 말로 답할 수 있는지가 더 중요하다.

---

## 1. 전체 흐름

```text
1. Nav2는 왜 Day 10, Day 11, Day 12 결과가 모두 필요할까?
2. SLAM으로 만든 map은 Nav2에서 어디에 쓰일까?
3. AMCL이 만든 map_robot_ns -> odom_robot_ns TF는 왜 중요할까?
4. /robot_ns/navigate_to_pose goal은 어떤 과정을 거쳐 /robot_ns/cmd_vel이 될까?
5. /robot_ns/cmd_vel이 나오면 실제 로봇을 움직이는 주체는 누구인가?
```

---

## 2. Lifecycle

```text
1. node list에 보이는 것과 lifecycle active 상태는 무엇이 다른가?
2. lifecycle_manager_navigation은 어떤 역할을 하는가?
3. autostart:=true와 autostart:=false는 어떤 차이가 있는가?
4. planner_server가 inactive이면 어떤 증상이 나올까?
5. bt_navigator가 active가 아니면 action goal은 어떻게 될까?
```

---

## 3. Behavior Tree

```text
1. bt_navigator는 직접 속도 명령을 만드는가?
2. Behavior Tree는 왜 필요한가?
3. ComputePathToPose와 FollowPath는 각각 어떤 서버와 연결될까?
4. recovery behavior는 어떤 상황에서 의미가 있을까?
```

---

## 4. Costmap

```text
1. global costmap과 local costmap은 무엇이 다른가?
2. global costmap의 기준 frame은 왜 map_robot_ns인가?
3. local costmap의 기준 frame은 왜 odom_robot_ns인가?
4. static layer, obstacle layer, inflation layer는 각각 무엇을 하는가?
5. goal이 벽이나 inflation 영역 안에 있으면 어떤 일이 생길까?
```

---

## 5. Planner / Controller

```text
1. planner_server와 controller_server는 무엇이 다른가?
2. /robot_ns/plan이 있다는 것은 무엇을 의미하는가?
3. /robot_ns/plan은 있는데 /robot_ns/cmd_vel이 없으면 어디를 의심해야 하는가?
4. DWB controller는 왜 여러 속도 후보를 평가하는가?
5. critic은 무엇을 평가하는 기준인가?
```

---

## 6. Debug

```text
1. RViz Goal 버튼이 안 되는데 CLI action goal은 된다면 무엇을 의미할까?
2. action server not available이면 어떤 노드를 봐야 할까?
3. No critics defined for FollowPath가 나오면 어떤 설정을 봐야 할까?
4. /robot_ns/cmd_vel에 publisher가 여러 개 있으면 어떤 문제가 생길까?
5. map/world 조합이 틀리면 AMCL과 Nav2에 어떤 영향이 있을까?
```

---

## 7. 예시 환경 기준

```text
1. 내 workspace 경로는 어디인가?
2. Nav2 localization launch와 navigation launch는 각각 무엇인가?
3. 예시 환경의 map frame, odom frame, base frame은 무엇인가?
4. 예시 환경의 navigate action 이름은 무엇인가?
5. 예시 환경에서 goal을 CLI로 보내는 명령어를 직접 작성할 수 있는가?
```

