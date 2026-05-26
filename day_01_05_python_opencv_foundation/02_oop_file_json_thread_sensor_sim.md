# 02. OOP / 파일 / JSON / Thread / 센서 시뮬레이션

## 1. 이 문서에서 다루는 것

Day 02의 핵심은 Python 문법을 “로봇 프로그램 구조”처럼 바꾸는 것이다.

```text
단순 함수 실행
  -> 센서 class
  -> 파일/JSON 설정 저장
  -> 로그 파싱
  -> thread/process/queue로 동시 작업 구성
```

ROS2를 쓰면 직접 thread를 많이 만들지 않아도 된다. 하지만 sensor callback, timer callback, executor, queue 개념을 이해하려면 이 파트가 필요하다.

---

## 2. 관련 실습 파일

```text
day_2/ioff.py
day_2/calib.json
day_2/03_01_Python-File-JSON.ipynb
day_2/03_02_01_Python-Thread-Daemon.py
day_2/03_02_02_Python-Multi-Thread.py
day_2/03_02_02_02_Python-Multi-Thread..py
day_2/03_02_03_Python-Process-Pool.py
day_2/03_02_04_Python-Process-Queue.py
day_2/03_02_05_Python-Thread-Practice.py
day_2/file_json_regex.md
day_2/oop_sensor.md
day_2/threading_process.md
```

---

## 3. OOP를 쓰는 이유

로봇에는 상태를 가진 구성요소가 많다.

```text
카메라
LiDAR
IMU
필터
로거
제어기
추론기
```

함수만으로 만들면 매번 인자로 상태를 넘겨야 하고, 어떤 값이 어디에 속하는지 흐려진다. class는 관련된 데이터와 함수를 하나의 역할 단위로 묶는다.

```python
class LidarSensor:
    def __init__(self, name, max_range):
        self.name = name
        self.max_range = max_range

    def read(self):
        ...
```

핵심은 문법이 아니라 역할 분리다.

```text
Sensor class
  -> 센서 데이터를 만든다.

Filter class
  -> 센서 데이터를 보정한다.

Logger class
  -> 데이터를 파일로 저장한다.

Node class
  -> ROS2에서 topic/service/timer를 묶는다.
```

---

## 4. 추상 클래스와 인터페이스

`ioff.py`와 기존 OOP 정리에서는 `Sensor` 추상 클래스를 만들고, 구체 센서가 이를 구현하는 형태를 다룬다.

```python
from abc import ABC, abstractmethod

class Sensor(ABC):
    @abstractmethod
    def get_data(self):
        pass
```

이런 구조의 의미는 다음이다.

```text
센서 종류는 다를 수 있다.
하지만 외부에서는 get_data()라는 같은 방식으로 읽고 싶다.
```

이것이 인터페이스 감각이다. ROS2에서도 node가 내부적으로 무엇을 하든, 외부에서는 topic/service/action이라는 약속된 인터페이스로 통신한다.

---

## 5. 파일 I/O와 JSON

센서값, 설정값, 보정값은 프로그램을 종료해도 남아야 한다.

```python
import json

config = {
    "camera_index": 0,
    "width": 640,
    "height": 480,
}

with open("config.json", "w", encoding="utf-8") as f:
    json.dump(config, f, indent=2)
```

NumPy 배열은 JSON으로 바로 저장할 수 없다. JSON은 Python list, dict, str, int, float, bool, null 같은 기본 구조만 직접 저장한다.

```python
ranges = np.array([1.0, 2.0, 3.0])
json_ready = ranges.tolist()
```

이 감각은 이후 아래 파일들을 이해할 때 도움이 된다.

```text
camera calibration yaml
map yaml
nav2_params.yaml
ROS2 parameter yaml
```

JSON과 YAML은 형식은 다르지만 “구조화된 설정/데이터 파일”이라는 점에서 같은 방향으로 이해하면 된다.

---

## 6. 정규표현식과 로그 파싱

정규표현식은 문자열에서 필요한 값을 뽑아내는 도구다.

```python
import re

line = "[INFO] battery=12.4V temp=36.2C"
match = re.search(r"battery=([0-9.]+)V", line)

if match:
    battery = float(match.group(1))
```

로봇 실습에서는 터미널 로그, 센서 로그, build log에서 필요한 값을 빠르게 뽑을 때 유용하다.

---

## 7. Thread가 필요한 상황

로봇 프로그램은 여러 일이 동시에 진행되는 것처럼 보여야 한다.

```text
카메라 프레임 읽기
YOLO 추론
결과 화면 표시
키 입력 처리
로그 저장
ROS2 message publish
```

thread는 특히 I/O 대기 작업에 많이 맞는다.

```python
import threading

t = threading.Thread(target=worker, daemon=True)
t.start()
```

`daemon=True`는 메인 프로그램이 끝나면 thread도 같이 종료될 수 있다는 뜻이다. 반대로 안전하게 종료해야 하는 작업이라면 `Event`를 통해 종료 신호를 보내고 `join()`으로 기다리는 구조가 낫다.

---

## 8. Lock이 필요한 이유

두 thread가 같은 데이터를 동시에 수정하면 예상과 다른 결과가 생길 수 있다.

```python
robot_telemetry = {"counter": 0}
```

두 thread가 동시에 아래 순서를 수행한다고 생각하면 문제가 생긴다.

```text
1. counter를 읽음
2. counter + 1 계산
3. 다시 저장
```

중간에 다른 thread가 끼어들면 증가가 누락될 수 있다. 이런 문제를 race condition이라고 한다.

```python
with data_lock:
    robot_telemetry["lidar"] = distance
```

Lock은 공유 데이터를 동시에 건드리지 못하게 막는 장치다.

---

## 9. Queue가 좋은 이유

공유 변수를 직접 만지는 대신 queue를 쓰면 생산자와 소비자를 분리할 수 있다.

```text
producer thread
  -> sensor_queue.put(data)

consumer thread
  -> sensor_queue.get()
```

이 구조는 ROS2 topic과 사고방식이 비슷하다.

```text
Publisher
  -> topic
  -> Subscriber
```

둘은 같은 것은 아니지만, “한쪽은 데이터를 만들고 다른 쪽은 받아 처리한다”는 구조를 이해하는 데 도움이 된다.

---

## 10. Process와 Thread의 차이

| 구분 | 특징 | 적합한 작업 |
|---|---|---|
| thread | 같은 process 안에서 메모리 공유 | I/O, 카메라 읽기, 네트워크, 파일 저장 |
| process | 별도 process로 실행 | CPU가 무거운 계산, 병렬 작업 |
| queue | 데이터 전달 | producer-consumer 구조 |
| event | 종료 신호 | 안전한 종료 |
| lock | 공유 데이터 보호 | race condition 방지 |

Python에는 GIL이 있어서 CPU 연산 병렬화에는 process가 더 적합한 경우가 많다. 다만 OpenCV/NumPy/딥러닝 라이브러리는 내부적으로 C/CUDA를 쓰므로 상황에 따라 다르게 봐야 한다.

---

## 11. ROS2와 연결해서 이해하기

ROS2에서는 직접 thread를 만들지 않아도 아래처럼 여러 callback이 동작한다.

```text
image subscription callback
parameter callback
timer callback
service callback
```

그래서 Day 02의 thread/process 실습은 이런 질문을 이해하는 데 도움이 된다.

```text
callback이 오래 걸리면 다른 callback은 어떻게 되는가?
이미지 처리가 느리면 message가 밀릴 수 있는가?
queue size 10은 어떤 의미인가?
카메라 프레임을 읽는 주기와 YOLO 처리 속도가 다르면 어떻게 되는가?
```

---

## 12. 현재 코드에서 학습적으로 볼 점

Day 02의 일부 파일은 완성 코드라기보다 실습 중간 상태에 가깝다. 그래서 실행 시 문제가 생길 수 있는 부분도 있다.

예를 들면 다음과 같다.

```text
- Lock을 일부러 주석 처리해서 race condition을 관찰하는 코드
- 미완성 상태를 관찰하기 위한 live_tail 실습 코드
- producer의 sleep이 주석 처리되어 매우 빠르게 queue를 채울 수 있는 코드
- process join이 일부 worker에만 적용될 수 있는 코드
```

이것들은 지금 당장 수정 대상이 아니라, 동시성 실습에서 왜 문제가 생기는지 관찰하기 위한 재료로 보는 것이 맞다.

자세한 내용은 `09_runtime_notes.md`에 분리했다.

---

## 13. 정리

Day 02에서 가져갈 것은 아래다.

```text
class는 상태와 동작을 역할 단위로 묶는다.
file/json/yaml은 설정과 결과를 재현 가능하게 만든다.
thread/process는 동시에 여러 흐름을 돌리기 위한 도구다.
공유 변수는 Lock이 필요하고, 데이터 전달은 Queue가 더 안전한 경우가 많다.
이 감각은 ROS2 topic/callback/timer/executor 이해로 이어진다.
```
