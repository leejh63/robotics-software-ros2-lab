# 06. Robot Camera Practice / Raspberry Pi Environment Note

## 1. 이 문서에서 다루는 것

Day 05의 Robot Camera Practice는 앞에서 배운 내용을 한 번에 묶는 통합 실습에 가깝다.

```text
카메라 입력
  -> calibration 결과 로드
  -> 왜곡 보정
  -> YOLO 추론
  -> bbox 중심점 계산
  -> Kalman Filter 안정화
  -> 거리/경고 판단
  -> 결과 시각화
  -> 로그 저장
```

이 문서는 이 파이프라인의 의미와 Raspberry Pi 환경 메모의 위치를 정리한다.

---

## 2. 관련 원본 파일

```text
day_4/prac/05_03_Robot-Camera-Practice.py
day_5/in_rasp_install.md
day_67/code/05.02.02.Webcam-Kalman.py
day_67/code/05.02.03.Kalman-NIS-Eval.py
```

---

## 3. Robot Camera Practice의 전체 흐름

`05_03_Robot-Camera-Practice.py`는 여러 개념을 합친다.

```text
1. YOLO 모델 로드
2. calibration YAML 탐색/로드
3. camera open
4. frame read
5. undistort 적용
6. YOLO inference
7. detection 결과 파싱
8. target class 선택
9. 중심점 계산
10. Kalman update
11. 거리 추정과 warning 판단
12. detection log 저장
```

이 흐름은 단일 알고리즘이라기보다 perception pipeline이다.

---

## 4. 왜곡 보정의 위치

파이프라인에서 undistort는 YOLO 전에 적용될 수 있다.

```text
camera frame
  -> undistort
  -> YOLO
```

그런데 이것이 항상 정답은 아니다.

| 상황 | 판단 |
|---|---|
| 정확한 위치/거리 추정이 중요 | undistort 고려 |
| 단순 객체 탐지만 필요 | 원본 frame으로도 가능 |
| 실시간성이 부족 | undistort 비용을 줄일 방법 고려 |
| 렌즈 왜곡이 거의 없음 | 효과가 작을 수 있음 |

현재 실습에서는 “보정된 frame을 YOLO 입력으로 넣어볼 수 있다”는 감각이 중요하다.

---

## 5. Target box 선택 정책

YOLO는 여러 객체를 동시에 찾을 수 있다. 그러면 어떤 box를 추적할지 정책이 필요하다.

| 정책 | 설명 |
|---|---|
| class filter | 특정 class만 사용 |
| confidence max | confidence가 가장 높은 box 선택 |
| area max | 가장 큰 box 선택 |
| center nearest | 화면 중앙에 가장 가까운 box 선택 |
| track id | tracker를 이용해 같은 객체 유지 |

초기 실습에서는 단순하게 아래 조합이 적당하다.

```text
target class만 남긴다.
confidence가 기준 이상인 것만 본다.
그중 confidence가 가장 높은 box를 선택한다.
```

객체가 여러 개 있는 상황에서 “person을 추적한다”고만 쓰면 부족하다. 어떤 person을 추적하는지 정책이 있어야 한다.

---

## 6. 거리 추정의 한계

단안 카메라와 YOLO bbox만으로 실제 거리를 정확하게 알기는 어렵다. 객체의 실제 크기를 알고 있다고 가정하면 대략적인 추정은 가능하다.

```text
Z ≈ fy * H / h_px
```

| 값 | 의미 |
|---|---|
| `Z` | 카메라와 객체 사이의 거리 추정값 |
| `fy` | y 방향 focal length |
| `H` | 객체의 실제 높이 |
| `h_px` | 이미지에서 box 높이 |

이 방식은 가정이 강하다.

```text
객체 실제 크기를 알고 있어야 한다.
객체가 정면에 가깝게 보여야 한다.
box가 실제 객체 경계를 잘 잡아야 한다.
카메라 calibration 값이 적절해야 한다.
```

따라서 문서에서는 “정밀 거리 측정”이라고 쓰면 안 된다. “box 크기 기반 단순 거리 추정” 정도가 정확하다.

---

## 7. 경고 판단 로직

경고는 detection 하나만으로 바로 내면 흔들릴 수 있다. 안정적인 판단에는 조건이 필요하다.

```text
target class인가?
confidence가 기준 이상인가?
box 중심이 관심 영역에 들어왔는가?
거리 추정값이 기준 이하인가?
N프레임 이상 지속되었는가?
```

예를 들어 단일 프레임에서 한 번 person이 잡혔다고 바로 경고를 내면 오탐에 약하다. 3~5프레임 이상 연속으로 조건이 만족될 때 경고를 내는 방식이 더 안정적이다.

---

## 8. 로그 저장의 의미

`05_03_Robot-Camera-Practice.py`에는 detection log를 JSON으로 저장하는 흐름이 있다.

로그 저장의 목적은 다음이다.

```text
실행 결과를 나중에 다시 확인한다.
어떤 frame에서 어떤 객체가 잡혔는지 본다.
threshold를 바꾸기 전/후를 비교한다.
실패 사례를 모아서 개선한다.
```

ROS2로 넘어가면 이런 역할을 rosbag이 맡을 수 있다.

```text
JSON log
  -> 내가 정한 데이터 구조만 저장

rosbag
  -> ROS2 topic message를 시간순으로 저장
```

---

## 9. Raspberry Pi 환경 메모의 의미

`day_5/in_rasp_install.md`는 완성된 튜토리얼이라기보다 실습 환경을 만들며 남긴 메모에 가깝다.

주요 주제는 아래다.

```text
Raspberry Pi Imager
SSH 접속
netplan/network 설정
자동 업데이트 비활성화
절전/sleep 비활성화
swap 설정
locale 설정
ROS2/TurtleBot 관련 설치
카메라 장치 확인
```

이 메모는 나중에 실제 보드에서 실습할 때 중요하다. PC에서는 잘 되던 코드가 보드에서는 아래 이유로 실패할 수 있기 때문이다.

```text
카메라 권한 문제
네트워크 문제
메모리 부족
apt lock 문제
locale 문제
CPU 성능 부족
GUI 환경 없음
```

---

## 10. ROS2 실물 환경과 연결

Raspberry Pi/TurtleBot 환경에서는 아래 흐름이 된다.

```text
카메라 장치
  -> camera driver
  -> /image_raw topic
  -> image processing node
  -> YOLO node
  -> detection topic
  -> TF/RViz/제어 node
```

Day 05의 OpenCV 단독 파이프라인은 ROS2에서 여러 node로 쪼개진다. 이것이 다음 단계의 핵심이다.

---

## 11. 현재 단계에서의 결론

Robot Camera Practice에서 가져갈 것은 아래다.

```text
카메라 perception은 여러 단계를 묶은 pipeline이다.
YOLO box를 바로 제어에 쓰기보다 target 선택/필터링/검증이 필요하다.
단안 카메라 거리 추정은 강한 가정이 있으므로 표현을 조심해야 한다.
로그 저장은 실패 사례와 파라미터 비교를 위한 도구다.
Raspberry Pi 환경 메모는 실물 장비 재현성을 위한 기록이다.
```
