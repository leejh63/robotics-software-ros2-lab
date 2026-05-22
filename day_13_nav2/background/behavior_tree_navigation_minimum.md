# Behavior Tree Navigation 최소 배경지식

Nav2에서 `bt_navigator`는 goal을 받은 뒤 planner, controller, recovery behavior를 어떤 순서로 호출할지 관리한다.

---

## 1. Behavior Tree를 왜 쓰는가?

로봇 주행은 단순한 직선 명령이 아니다.

```text
목표까지 경로 생성
경로 추종
장애물 감지
경로 재계획
막힘 상태 복구
목표 도달 판정
실패 처리
```

이런 절차를 if문만으로 관리하면 복잡해진다.  
Behavior Tree는 행동을 트리 형태로 나눠서 관리한다.

---

## 2. Nav2에서 자주 보는 행동

```text
ComputePathToPose
  planner_server에게 global path 생성을 요청

FollowPath
  controller_server에게 path 추종을 요청

Spin
  제자리 회전 recovery

BackUp
  뒤로 물러나는 recovery

Wait
  잠시 대기

ClearCostmap
  costmap 정보를 비우고 다시 받기
```

---

## 3. goal 처리 흐름

```text
NavigateToPose action goal 수신
        ↓
bt_navigator가 BT 실행
        ↓
ComputePathToPose
        ↓
planner_server가 /robot_ns/plan 생성
        ↓
FollowPath
        ↓
controller_server가 /robot_ns/cmd_vel 생성
        ↓
목표 도달 또는 실패
```

---

## 4. 학습할 때의 핵심

처음부터 BT XML을 전부 외울 필요는 없다.  
먼저 아래만 구분하면 된다.

```text
bt_navigator
  전체 절차를 관리

planner_server
  path 생성

controller_server
  path 추종 속도 생성

behavior_server
  실패 상황의 recovery 동작 제공
```

---

## 5. 디버깅 관점

BT가 실패했다는 말은 너무 넓다.  
로그에서 어느 단계가 실패했는지 봐야 한다.

```text
ComputePathToPose 실패
  planner/global costmap/goal 위치 문제 가능성

FollowPath 실패
  controller/local costmap/odom/DWB 문제 가능성

Recovery 반복
  장애물, TF, localization, goal 위치 문제 가능성
```

