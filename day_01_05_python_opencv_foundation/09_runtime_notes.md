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

현재 정리본에서는 문제 관찰용 중간 파일을 실행 코드 목록에서 제외했다. 남긴 파일은 아래 기준으로 본다.

| 파일 | 현재 기준 | 주의할 점 |
|---|---|---|
| `03_02_01_Python-Thread-Daemon.py` | daemon thread 종료 동작 확인 | 메인 스레드가 끝나면 daemon thread도 함께 종료됨 |
| `03_02_02_Python-Multi-Thread.py` | Lock으로 공유 telemetry를 보호하는 예제 | ROS2 callback에서 공유 상태를 다룰 때의 감각과 연결 |
| `03_02_03_Python-Process-Pool.py` | 독립 데이터 병렬 처리 예제 | 작업 간 공유 상태가 거의 없을 때 적합 |
| `03_02_04_Python-Process-Queue.py` | process-safe Queue와 Event 기반 종료 예제 | worker 수를 과하게 늘리지 않고 전체 process를 join해야 함 |
| `03_02_05_Python-Thread-Practice.py` | Thread + Queue 기반 producer/consumer 예제 | producer 주기를 명시적으로 제한해야 queue backlog를 피할 수 있음 |

정리하면서 제외한 중간 파일은 `projects/python_opencv_foundation_lab/SOURCE_MAP.md`에 따로 기록했다.

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
