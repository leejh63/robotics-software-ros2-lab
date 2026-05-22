# Costmap Layer와 DWB 최소 배경지식

Nav2가 움직이는 핵심은 “어디를 지나가면 위험한지”와 “지금 어떤 속도로 움직이면 좋은지”를 계산하는 것이다.

---

## 1. Costmap은 무엇인가?

Costmap은 지도를 숫자 격자로 바꾼 것이다.

```text
낮은 비용
  지나가기 좋음

높은 비용
  장애물에 가깝거나 위험함

lethal obstacle
  지나가면 안 됨

unknown
  아직 모르는 공간
```

planner와 controller는 이 비용을 보고 판단한다.

---

## 2. Layer 구조

Costmap은 여러 layer를 합쳐 만든다.

```text
static_layer
  저장 지도에서 벽/공간 정보 가져옴

obstacle_layer
  /scan 같은 실시간 센서로 장애물 반영

voxel_layer
  3D 장애물 정보를 쓸 때 사용 가능

inflation_layer
  장애물 주변에 안전 여유 영역 생성
```

현재 실습에서는 static/obstacle/inflation을 중심으로 보면 된다.

---

## 3. Inflation이 왜 필요한가?

로봇은 점이 아니다. 폭이 있다.  
그래서 벽 바로 옆을 지나가면 충돌할 수 있다.

Inflation layer는 장애물 주변에 비용을 퍼뜨린다.

```text
벽 자체
  lethal obstacle

벽 근처
  비용이 높음

벽에서 멀어짐
  비용이 낮아짐
```

이 덕분에 planner가 벽에 너무 붙는 경로를 피한다.

---

## 4. DWB는 무엇인가?

DWB는 local controller다.  
global path를 따라가기 위해 지금 당장 낼 속도 명령을 고른다.

흐름:

```text
여러 속도 후보 생성
  -> 각 후보로 미래 궤적 예측
  -> costmap과 path 기준으로 점수 계산
  -> 가장 좋은 후보 선택
  -> /cmd_vel 발행
```

---

## 5. Critic은 무엇인가?

Critic은 속도 후보를 평가하는 기준이다.

예:

```text
장애물에 가까운가?
path에서 벗어나는가?
goal에 가까워지는가?
방향 정렬이 되는가?
진동하는 움직임인가?
```

Critic이 없으면 DWB는 어떤 후보가 좋은지 평가할 기준이 없다.

그래서 `No critics defined for FollowPath`는 controller가 정상적으로 설정을 못 읽었다는 강한 신호다.

---

## 6. 현재 환경에서 봐야 할 값

```text
global frame: map_robot_ns
local frame: odom_robot_ns
robot base: base_footprint
scan topic: /robot_ns/scan
odom topic: /robot_ns/odom
cmd_vel topic: /robot_ns/cmd_vel
```

DWB 관련 핵심:

```text
controller_plugins: FollowPath
FollowPath.plugin: dwb_core::DWBLocalPlanner
FollowPath.critics: 여러 critic 목록
```

