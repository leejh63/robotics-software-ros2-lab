# Day 13에서 나중 프로젝트로 이어지는 연결

이 문서는 포트폴리오 문서가 아니다.  
Day 13에서 배운 내용을 나중에 2주짜리 개인/팀 프로젝트로 확장할 때 어떤 방향이 가능한지 정리한 참고 자료다.

---

## 1. 현재 Day 13의 성격

현재 Day 13은 아래에 가깝다.

```text
Nav2 bringup 구조 학습
Gazebo 기반 navigation 실습
SLAM -> AMCL -> Nav2 연결 확인
namespace/frame/topic 디버깅 연습
```

이것만으로 “완성 프로젝트”라고 말하기에는 부족하다.  
하지만 나중 프로젝트의 기반 지식으로는 매우 중요하다.

---

## 2. 나중 프로젝트로 확장 가능한 주제

```text
1. 커스텀 월드에서 autonomous patrol 구현
2. 특정 waypoint 순회 + 장애물 회피 데모
3. YOLO detection과 Nav2 goal 연동
4. rosbag 기반 offline debugging pipeline 구축
5. SLAM/AMCL/Nav2 파라미터 튜닝 비교 실험
6. RViz panel 없이 CLI/launch로 재현 가능한 navigation demo 정리
```

---

## 3. 프로젝트화할 때 추가로 필요한 것

```text
명확한 목표
  예: 지정된 waypoint를 순회한다.

재현 가능한 실행 명령
  한 번에 실행 가능한 launch 구성

측정 기준
  goal 성공률, 평균 도달 시간, path length, 실패 케이스

데모 자료
  화면 녹화, RViz/Gazebo 캡처, topic echo 로그

한계 명시
  simulation 기준인지, real robot 기준인지 구분
```

---

## 4. 지금 문서에서 유지할 태도

현재는 포장보다 이해가 먼저다.

```text
현재는 학습 정리
나중에 별도 프로젝트에서 문제 정의
그 프로젝트 결과를 README/포트폴리오로 정리
```

지금 문서를 억지로 포트폴리오처럼 만들 필요는 없다.

