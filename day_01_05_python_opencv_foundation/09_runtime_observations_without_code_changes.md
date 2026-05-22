# 09. Runtime Observations Without Code Changes

이 문서는 Day 01~05 관련 코드에서 정적 확인 중 발견한 실행상 주의점을 정리한다. 현재 단계에서는 코드를 수정하지 않고, 학습 문서에 관찰 사항으로만 남긴다.

---

## 1. 이 문서의 기준

```text
코드 수정 X
실행 중 문제가 될 수 있는 지점 기록 O
왜 문제가 될 수 있는지 설명 O
나중에 수정할 때 확인할 체크리스트 제공 O
```

---

## 2. Day 02 thread/process 실습 코드

### 2.1 `03.02.02.02.Python-Multi-Thread.py`

관찰 사항:

```text
extract_error_logs() 안에서 re.search()를 사용하지만 import re가 보이지 않는다.
live_tail()이 error_data.txt를 열려고 할 때 파일이 아직 없으면 FileNotFoundError가 날 수 있다.
live_tail()의 `for line in f:`는 일반 파일 반복이라 tail -f처럼 새로 추가되는 줄을 계속 따라가지 못할 수 있다.
```

학습 포인트:

```text
thread를 여러 개 시작하면 실행 순서가 항상 기대한 순서대로 보장되지 않는다.
파일 생산자와 소비자가 동시에 움직일 때는 파일 존재 여부, flush, polling, EOF 처리를 고려해야 한다.
```

---

### 2.2 `03_02_02_02_Python-Multi-Thread..py`

관찰 사항:

```text
counter를 두 thread가 동시에 증가시키는 구조다.
Lock 코드가 주석 처리되어 있다.
```

이것은 실수라기보다 race condition을 관찰하기 좋은 코드다.

```text
읽기
계산
쓰기
```

이 세 단계 사이에 다른 thread가 끼어들면 증가 횟수가 누락될 수 있다.

---

### 2.3 `03_02_05_Python-Thread-Practice.py`

관찰 사항:

```text
producer() 내부의 time.sleep(0.1)이 주석 처리되어 있다.
```

요구사항에는 0.1초마다 센서 값을 생성한다고 되어 있지만, sleep이 없으면 producer가 매우 빠르게 queue를 채울 수 있다.

학습 포인트:

```text
producer 속도 > consumer 속도
  -> queue backlog 증가
  -> 메모리 사용량 증가
  -> 출력 폭주
```

ROS2에서도 publisher가 너무 빠르고 subscriber 처리가 느리면 queue가 밀리거나 message drop이 생길 수 있다.

---

### 2.4 `03_02_04_Python-Process-Queue.py`

관찰 사항:

```text
AI worker process를 19개 만든다.
finally에서 p2.join()은 반복문 마지막 p2만 기다릴 가능성이 있다.
```

학습 포인트:

```text
여러 process를 만들었다면 리스트 전체를 순회하며 join하는 구조가 필요하다.
worker 수는 CPU core, 작업량, queue 처리 속도를 고려해야 한다.
```

지금은 코드 수정이 아니라 process/queue 구조를 이해하기 위한 관찰로 남긴다.

---

## 3. Day 04 / Day 67 YOLO-Kalman 코드

### 3.1 `05.02.02.Webcam-Kalman.py`

관찰 사항:

```text
YOLO 모델 경로가 'yolov8n.pt'로 상대경로다.
실행 위치에 따라 모델 파일을 찾지 못할 수 있다.
카메라 index가 0으로 고정되어 있다.
GUI 창과 trackbar는 headless/SSH/WSL 환경에서 실패할 수 있다.
```

학습 포인트:

```text
실시간 vision 코드는 working directory, camera device, GUI 환경에 영향을 많이 받는다.
나중에 ROS2 패키지로 정리할 때는 model_path를 parameter로 빼는 것이 좋다.
```

---

### 3.2 `05.02.03.Kalman-NIS-Eval.py`

관찰 사항:

```text
nis_log.csv가 없으면 실행할 수 없다.
scipy가 설치되어 있어야 한다.
중간에 print(ci_low, ci_low)가 있어 ci_high 확인용 출력 의도라면 오타 가능성이 있다.
```

학습 포인트:

```text
평가 스크립트는 입력 로그 파일 존재 여부를 먼저 확인해야 한다.
분석용 dependency는 requirements에 분리해두는 것이 좋다.
```

---

## 4. OpenCV / YOLO 공통 실행 환경 주의

```text
cv2.imshow()는 GUI 환경이 필요하다.
Docker/WSL/SSH에서는 창이 안 뜰 수 있다.
카메라 장치가 /dev/video0이 아닐 수 있다.
OpenCV와 ultralytics를 설치한 Python 환경이 다를 수 있다.
YOLO 첫 실행 시 모델 다운로드 또는 로드 시간이 걸릴 수 있다.
```

확인 명령은 `commands/python_opencv_yolo_commands.md`에 정리했다.

---

## 5. 나중에 코드 정리 단계에서 볼 후보

현재는 수정하지 않지만, 나중에 코드 정리 단계로 넘어가면 아래 항목을 볼 수 있다.

```text
- thread 실습 코드의 import re 추가 여부
- live_tail을 tail -f 방식으로 바꿀지 여부
- producer sleep 복구 여부
- process join 구조 정리 여부
- YOLO model_path를 parameter 또는 절대/패키지 경로로 바꿀지 여부
- camera index를 CLI argument 또는 parameter로 뺄지 여부
- headless 환경에서는 imshow 대신 image 저장/ROS topic 확인 방식 제공
- NIS eval script의 입력 파일 존재 확인 추가
```

하지만 이 작업은 현재 문서 정리 범위가 아니다. 여기서는 학습 문서 정리와 배경지식 보강까지만 다룬다.
