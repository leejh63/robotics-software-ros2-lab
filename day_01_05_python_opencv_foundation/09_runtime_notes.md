# 09. 실행 시 주의할 점

이 문서는 Day 01~05 관련 코드에서 실행 중 헷갈리기 쉬운 부분을 정리한다. 코드의 의도와 실행 환경 차이를 분리해서 보는 것이 목적이다.

---

## 1. 이 문서의 기준

```text
실행 중 문제가 될 수 있는 지점
왜 문제가 될 수 있는지
나중에 코드 정리 시 확인할 항목
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

---

## 3. Day 04 / 별도 작업공간 YOLO-Kalman 코드

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
ROS2 패키지로 정리할 때는 model_path를 parameter로 빼는 것이 좋다.
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

## 5. 나중에 코드 정리 시 볼 후보

```text
- 누락된 import 확인
- thread/process join 구조 확인
- producer-consumer 속도 조절
- YOLO model_path parameter화
- camera index parameter화
- GUI 환경이 없는 경우 저장/토픽 발행 방식 분리
- 평가 스크립트 입력 파일 존재 여부 확인
```
