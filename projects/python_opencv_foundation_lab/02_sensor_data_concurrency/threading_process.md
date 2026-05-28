# 멀티스레딩 · 멀티프로세스

---

## 목차

1. [왜 멀티태스킹이 필요한가](#1-왜-멀티태스킹이-필요한가)
2. [프로세스 vs 스레드](#2-프로세스-vs-스레드)
3. [Python GIL](#3-python-gil)
4. [멀티스레딩 vs 멀티프로세싱 선택 기준](#4-멀티스레딩-vs-멀티프로세싱-선택-기준)
5. [Thread 생성 · start() · join()](#5-thread-생성--start--join)
6. [Daemon(데몬) 스레드](#6-daemon데몬-스레드)
7. [Race Condition과 Lock](#7-race-condition과-lock)
8. [Thread-safe 코드 작성 패턴](#8-thread-safe-코드-작성-패턴)
9. [threading.Event — 스레드 종료 신호](#9-threadingevent--스레드-종료-신호)
10. [queue.Queue — 스레드 간 안전한 데이터 전달](#10-queuequeue--스레드-간-안전한-데이터-전달)
11. [멀티프로세싱 기본](#11-멀티프로세싱-기본)
12. [Pool을 이용한 병렬 처리](#12-pool을-이용한-병렬-처리)
13. [자주 하는 실수](#13-자주-하는-실수)

---

## 1. 왜 멀티태스킹이 필요한가

로봇은 여러 작업을 **동시에** 처리해야 합니다.

```
싱글 스레드 방식 (문제 상황)

카메라 처리 ━━━━━━━━━━━━━━━━━━━━━━ (100~200ms)
                                          ↑ 이 사이에 초음파 센서를 전혀 못 읽음
초음파 센서   ████░░░░░░░░░░░░░░░░░████
              읽음  기다리는 중...     다시 읽음
```

```
멀티스레드 방식 (해결)

카메라 스레드   ━━━━━━━━━━━━━━━━━━━━━━
초음파 스레드   ██░██░██░██░██░██░██░██
               동시에 독립적으로 실행
```

- **I/O 바운드 작업**: 센서 통신, 네트워크 → 대기 시간이 많아 멀티스레딩이 효과적
- **CPU 바운드 작업**: 이미지 처리, 경로 계획 → GIL 때문에 멀티프로세싱 필요 (3번 참고)

---

## 2. 프로세스 vs 스레드

"주방의 요리사" 비유로 이해합니다.

```
프로세스 (Process)                 스레드 (Thread)

[ 주방 A ]    [ 주방 B ]          [ 주방 하나 ]
  요리사1       요리사2              요리사1  요리사2
  냄비, 칼       냄비, 칼            └──공용 냄비, 칼──┘
  독립 공간       독립 공간               공유 공간
```

| 비교 항목 | 프로세스 | 스레드 |
|-----------|----------|--------|
| 메모리 | 독립된 공간 | 프로세스 내 공유 |
| 격리 | 한쪽 크래시가 다른 쪽에 영향 없음 | 한 스레드가 죽으면 프로세스 전체 위험 |
| 생성 비용 | 높음 | 낮음 |
| 데이터 공유 | Queue/Pipe 필요 | 변수 직접 공유 가능 (Lock 필요) |

---

## 3. Python GIL

**GIL(Global Interpreter Lock)**: 한 번에 하나의 스레드만 Python 바이트코드를 실행하도록 거는 잠금장치.

```
GIL 동작 흐름

시간 →     0ms      10ms     20ms     30ms
Thread A   ██실행██  ░대기░   ██실행██  ░대기░
Thread B   ░대기░   ██실행██  ░대기░   ██실행██
            ↑GIL 넘김  ↑GIL 넘김  ↑GIL 넘김
```

- **CPU 바운드**: 스레드 A가 계산하는 동안 스레드 B는 무조건 대기 → 코어가 여러 개여도 실제로는 하나만 씀
- **I/O 바운드**: 스레드 A가 센서 응답을 기다리는 동안 GIL을 자동으로 해제 → 스레드 B가 바로 실행됨

이것이 "I/O 바운드엔 멀티스레딩, CPU 바운드엔 멀티프로세싱"인 이유입니다.  
`multiprocessing`은 프로세스마다 독립된 Python 인터프리터를 가지므로 GIL의 영향을 받지 않습니다.

---

## 4. 멀티스레딩 vs 멀티프로세싱 선택 기준

| 구분 | 멀티스레딩 | 멀티프로세싱 |
|------|-----------|------------|
| GIL 영향 | 받음 | 받지 않음 |
| 적합한 작업 | I/O 바운드 | CPU 바운드 |
| 메모리 | 프로세스 내 공유 | 각 프로세스 독립 |
| 생성 비용 | 낮음 | 높음 |
| 데이터 공유 | 쉬움 (Lock 필요) | Queue/Pipe 필요 |
| 사용 예시 | 시리얼 포트, 네트워크, 하트비트 | 이미지 처리, AI 추론, 경로 계획 |

---

## 5. Thread 생성 · start() · join()

스레드를 만들고 실행하는 기본 흐름 세 단계입니다.

```python
import threading
import time

def sensor_reader(name):
    print(f"{name} 읽기 시작")
    time.sleep(2)          # 센서 응답 대기 시뮬레이션
    print(f"{name} 읽기 완료")

# 1. Thread 객체 생성 (target=실행할 함수, args=인수 튜플)
t = threading.Thread(target=sensor_reader, args=("Lidar",))

# 2. 스레드 시작
t.start()

# 3. 스레드가 끝날 때까지 메인 프로그램 대기
t.join()
print("모든 센서 작업 완료")
```

### join()을 쓰는 이유

`join()`이 없으면 메인 스레드가 스레드 완료를 기다리지 않고 바로 다음 줄을 실행합니다.

```
join() 있을 때               join() 없을 때

main ━━━━━━━━┓ join ─── 대기 ── 완료    main ━━━━━━━━━━━━━━━━━━━ 완료
             ↓                           ↓ (바로 다음으로 진행)
thread       ━━━━━━━━━━━━━━━━━━━━         thread ━━━━━━━━━━━━━━━━━━━━
```

여러 스레드를 순서대로 시작하고 모두 끝날 때까지 기다리는 패턴:

```python
threads = [
    threading.Thread(target=sensor_reader, args=("Lidar",)),
    threading.Thread(target=sensor_reader, args=("Ultrasonic",)),
]

for t in threads:
    t.start()   # 모든 스레드 먼저 시작

for t in threads:
    t.join()    # 그 다음 모두 완료 대기

print("전체 완료")
```

`start()` 루프와 `join()` 루프를 분리하는 게 핵심입니다.  
`start()`와 `join()`을 같은 루프에 넣으면 스레드를 하나씩 순서대로 실행하는 것과 다름없습니다.

---

## 6. Daemon(데몬) 스레드

**메인 프로그램이 종료될 때 함께 강제 종료되는 스레드**입니다.

```python
import threading
import time

def heartbeat():
    while True:               # 무한 루프
        print("Robot alive...")
        time.sleep(1.1)

# daemon=True 설정
t = threading.Thread(target=heartbeat, daemon=True)
t.start()

time.sleep(0.35)              # 메인 프로그램이 0.35초 후 종료
print("메인 프로그램 종료 → 데몬 스레드 자동 종료")
# heartbeat()의 while True 루프가 살아있어도 여기서 프로그램 전체 종료
```

```
실행 타임라인

0ms   ─ 데몬 스레드 시작 (heartbeat 무한 루프)
350ms ─ 메인 종료 신호 → 데몬 스레드 강제 종료
        "Robot alive..."는 한 번도 출력 안 됨 (sleep(1.1) > sleep(0.35))
```

| 설정 | 동작 |
|------|------|
| `daemon=True` | 메인 종료 시 함께 종료. 종료 처리가 필요 없는 백그라운드 작업에 적합 |
| `daemon=False` (기본값) | 스레드가 끝날 때까지 메인도 대기. `join()` 없이도 프로그램이 종료되지 않음 |

**용도**: 로봇 상태 로깅, 하트비트 신호 전송처럼 메인이 꺼지면 같이 꺼져야 하는 작업.

---

## 7. Race Condition과 Lock

### Race Condition (경쟁 상태)

두 스레드가 하나의 변수에 동시에 접근하면 데이터가 꼬입니다.

```python
# Lock 없는 경우 — 결과가 매번 달라짐 (Race Condition)
import threading, time

robot_telemetry = {"counter": 0}

def read_sensor():
    for _ in range(1000):
        counter = robot_telemetry["counter"]   # 1. 값 읽기
        counter += 1                           # 2. 계산
        time.sleep(0.01)                       # ← 이 사이에 다른 스레드가 끼어들 수 있음
        robot_telemetry["counter"] = counter   # 3. 값 쓰기

t1 = threading.Thread(target=read_sensor)
t2 = threading.Thread(target=read_sensor)
t1.start(); t2.start()
t1.join();  t2.join()

print(robot_telemetry)  # {"counter": 1274} ← 2000이어야 하는데 엉뚱한 값
```

왜 꼬이는지:

```
시간 →        t=0            t=1            t=2
Thread A   counter=10 읽기    계산중...      counter=11 씀
Thread B          counter=10 읽기    계산중...      counter=11 씀
                                                    ↑ A가 쓴 값 덮어씀!
결과: counter가 11 (실제로는 12가 되어야 함)
```

### Lock으로 해결

```python
import threading, time

robot_telemetry = {"counter": 0}
data_lock = threading.Lock()   # Lock 객체 생성

def read_sensor():
    for _ in range(1000):
        with data_lock:                            # 자물쇠 잠금
            counter = robot_telemetry["counter"]
            counter += 1
            time.sleep(0.01)
            robot_telemetry["counter"] = counter
            # with 블록 종료 시 자동으로 자물쇠 해제

t1 = threading.Thread(target=read_sensor)
t2 = threading.Thread(target=read_sensor)
t1.start(); t2.start()
t1.join();  t2.join()

print(robot_telemetry)  # {"counter": 2000} ← 정확한 값
```

`with lock:` 을 쓰면 블록이 끝날 때 예외가 발생해도 Lock이 자동으로 풀립니다.  
`lock.acquire()` / `lock.release()`를 직접 쓰면 예외 발생 시 `release()`를 빠뜨려 데드락이 날 수 있습니다.

### 종합 예제 — Lidar · Ultrasonic 동시 읽기

```python
import threading, time, random

robot_telemetry = {"lidar": 0, "ultrasonic": 0}
data_lock = threading.Lock()

def read_lidar():
    while True:
        distance = random.uniform(0.1, 10.0)
        with data_lock:
            robot_telemetry["lidar"] = distance
        time.sleep(0.1)   # 10Hz

def read_ultrasonic():
    while True:
        distance = random.uniform(20, 400)
        with data_lock:
            robot_telemetry["ultrasonic"] = distance
        time.sleep(0.5)   # 2Hz

if __name__ == "__main__":
    t1 = threading.Thread(target=read_lidar,      daemon=True)
    t2 = threading.Thread(target=read_ultrasonic, daemon=True)
    t1.start()
    t2.start()

    try:
        for _ in range(3):
            with data_lock:
                print(f"Lidar: {robot_telemetry['lidar']:.2f}m  "
                      f"Ultrasonic: {robot_telemetry['ultrasonic']:.2f}cm")
            time.sleep(1.0)
    except KeyboardInterrupt:
        print("\n종료합니다.")
```

---

## 8. Thread-safe 코드 작성 패턴

세 가지 원칙입니다.

### 원칙 1 — Lock 사용

공유 변수에 읽기/쓰기를 할 때 반드시 `Lock`으로 감쌉니다.

```python
lock = threading.Lock()
shared = 0

def safe_update():
    global shared
    with lock:
        shared += 1
```

### 원칙 2 — queue.Queue 활용

내부적으로 Lock이 구현되어 있어 별도 Lock 없이 스레드 간 데이터를 주고받을 수 있습니다.  
(다음 섹션에서 자세히 다룹니다)

### 원칙 3 — 공유 상태 최소화

스레드끼리 데이터를 최대한 공유하지 않도록 설계합니다.  
각 스레드가 독립적인 결과만 내놓고, 결과를 Queue로 한 곳에 모으는 구조가 가장 안전합니다.

### 데드락 (Deadlock)

Lock을 여러 개 쓸 때 발생할 수 있는 무한 대기 상태입니다.

```
A 스레드: lock1 보유 → lock2 대기
B 스레드: lock2 보유 → lock1 대기
→ 서로 상대방의 Lock이 풀리기만 기다리며 영원히 멈춤
```

예방법: **항상 같은 순서로 Lock을 획득합니다.** A, B 스레드 모두 `lock1 → lock2` 순서를 지키면 데드락이 발생하지 않습니다.

---

## 9. threading.Event — 스레드 종료 신호

`Event`는 모든 스레드가 공유하는 "신호 깃발"입니다.  
무한 루프를 돌고 있는 스레드를 안전하게 종료할 때 사용합니다.

```python
import threading, time

stop_event = threading.Event()

def worker():
    while not stop_event.is_set():   # 신호가 오기 전까지 반복
        print("작업 중...")
        time.sleep(0.5)
    print("종료 신호 수신 → 정리 후 종료")

t = threading.Thread(target=worker)
t.start()

time.sleep(2)
stop_event.set()   # 신호 발송 → is_set()이 True가 됨

t.join()
print("완료")
```

| 메서드 | 동작 |
|--------|------|
| `event.set()` | 깃발 올리기. `is_set()` → True |
| `event.is_set()` | 깃발 상태 확인 |
| `event.clear()` | 깃발 내리기. `is_set()` → False |
| `event.wait(timeout)` | 깃발이 올려질 때까지 대기 (timeout 초 후 자동 해제) |

### Event vs daemon=True 비교

| 방법 | 스레드 종료 시 | 정리 코드 실행 가능 여부 |
|------|--------------|------------------------|
| `daemon=True` | 메인 종료 시 즉시 강제 종료 | 불가 |
| `Event.set()` | 루프 조건 확인 후 정상 종료 | 가능 |

자원을 정리해야 하는 스레드라면 `Event`를 씁니다.  
백그라운드 하트비트처럼 정리가 필요 없으면 `daemon=True`가 더 간단합니다.

---

## 10. queue.Queue — 스레드 간 안전한 데이터 전달

`queue.Queue`는 내부적으로 Lock을 구현하고 있어 별도 Lock 없이 스레드 간 데이터를 안전하게 주고받을 수 있습니다.

```
생산자(Producer) 스레드          소비자(Consumer) 스레드
   센서 데이터 생성                  데이터 꺼내서 처리
       │                                   ↑
       └─── q.put(data) ──► [ Queue ] ──► q.get() ───┘
                             (내부 Lock으로 보호)
```

```python
import threading, queue, time, random

def producer(q, stop_event):
    while not stop_event.is_set():
        value = round(random.uniform(0, 100), 2)
        q.put(value)
        print(f"[Producer] 생성: {value}")
        time.sleep(0.1)

def consumer(q, stop_event):
    # stop_event가 세팅됐어도 큐에 남은 데이터까지 모두 처리
    while not stop_event.is_set() or not q.empty():
        try:
            value = q.get(timeout=0.2)   # 0.2초 안에 데이터 없으면 Empty 예외
            label = "HIGH" if value >= 50 else "LOW"
            print(f"[Consumer] 처리: {value:.2f} → {label} (잔량: {q.qsize()})")
            q.task_done()               # get()한 항목 처리 완료 알림
        except queue.Empty:
            continue

if __name__ == "__main__":
    sensor_queue = queue.Queue()
    stop_event   = threading.Event()

    t_producer = threading.Thread(target=producer, args=(sensor_queue, stop_event), daemon=True)
    t_consumer = threading.Thread(target=consumer, args=(sensor_queue, stop_event), daemon=True)

    t_producer.start()
    t_consumer.start()

    time.sleep(3)        # 3초 실행 후 종료
    stop_event.set()

    t_producer.join()
    t_consumer.join()
    print("파이프라인 종료")
```

### 핵심 메서드

| 메서드 | 동작 |
|--------|------|
| `q.put(item)` | 데이터 넣기. 큐가 가득 차면 대기 |
| `q.get(timeout=N)` | 데이터 꺼내기. N초 안에 없으면 `queue.Empty` 예외 |
| `q.empty()` | 큐가 비어 있으면 True |
| `q.qsize()` | 현재 큐에 있는 항목 수 |
| `q.task_done()` | `get()` 후 처리 완료 알림 (`join()` 과 쌍으로 사용) |

`threading.Lock`과의 차이: Lock은 공유 변수를 직접 보호할 때, `queue.Queue`는 스레드 간에 데이터를 **전달**할 때 씁니다.

---

## 11. 멀티프로세싱 기본

### Process 생성 · start() · join()

`threading.Thread`와 인터페이스가 같습니다. `Process`만 바꿔 사용합니다.

```python
from multiprocessing import Process

def task(name):
    print(f"{name} 작업 완료")

if __name__ == "__main__":           # 반드시 필요! (아래 실수 섹션 참고)
    p = Process(target=task, args=("Worker-1",))
    p.start()
    p.join()
```

### Queue — 프로세스 간 데이터 전달

프로세스는 메모리를 공유하지 않으므로 전역 변수를 수정해도 다른 프로세스에 반영되지 않습니다.  
`multiprocessing.Queue`로 데이터를 주고받아야 합니다.

```python
from multiprocessing import Process, Queue

def worker(q):
    q.put("결과 데이터")

if __name__ == "__main__":
    q = Queue()
    p = Process(target=worker, args=(q,))
    p.start()
    print(q.get())    # "결과 데이터"
    p.join()
```

### Event — 프로세스 간 종료 신호

`threading.Event`와 같은 인터페이스입니다. `multiprocessing.Event`를 씁니다.

```python
import multiprocessing, time, random

def sensor_worker(sensor_queue, stop_event):
    print("센서 프로세스 시작")
    while not stop_event.is_set():
        data = random.uniform(0, 100)
        sensor_queue.put(data)
        time.sleep(0.01)   # 100Hz
    print("센서 프로세스 종료")

def ai_inference_worker(sensor_queue, stop_event):
    print("AI 추론 프로세스 시작")
    while not stop_event.is_set():
        try:
            data = sensor_queue.get(timeout=1)
            print(f"[AI] {data:.2f} 분석 중... → 장애물 없음")
            time.sleep(0.2)   # 무거운 AI 연산 시뮬레이션
        except:
            continue
    print("AI 추론 프로세스 종료")

if __name__ == "__main__":
    sensor_q = multiprocessing.Queue()
    stop_sig  = multiprocessing.Event()

    p_sensor = multiprocessing.Process(
        target=sensor_worker, args=(sensor_q, stop_sig))
    p_ai = multiprocessing.Process(
        target=ai_inference_worker, args=(sensor_q, stop_sig))

    p_sensor.start()
    p_ai.start()

    try:
        time.sleep(2)
    except KeyboardInterrupt:
        pass
    finally:
        stop_sig.set()   # 두 프로세스에 동시에 종료 신호
        p_sensor.join()
        p_ai.join()
        print("모든 시스템이 안전하게 종료되었습니다.")
```

### 로봇 개발의 3-프로세스 패턴

```
[ 센서 프로세스 ]  ──put()──► [ Queue ]  ──get()──► [ AI 추론 프로세스 ]
  60 FPS로 읽기                                        10 FPS로 처리 (느려도 OK)
                                                              │
                                              [ 제어 프로세스 ]
                                               독립적으로 동작
                                               하드웨어와 주기적 통신
```

각 프로세스는 독립적이므로 AI 추론이 느려져도 센서 읽기와 모터 제어에 영향을 주지 않습니다.

---

## 12. Pool을 이용한 병렬 처리

**같은 함수를 여러 입력값에 대해 병렬로 실행**할 때 씁니다.

```python
from multiprocessing import Pool

def process_sensor_data(data):
    return data * 2   # 복잡한 필터링·계산 수행

if __name__ == "__main__":
    sensor_readings = [1.2, 3.4, 5.6, 7.8, 9.0]

    with Pool(processes=4) as pool:
        results = pool.map(process_sensor_data, sensor_readings)

    print(results)   # [2.4, 6.8, 11.2, 15.6, 18.0]
```

```
Pool(processes=4)

sensor_readings → [1.2,  3.4,  5.6,  7.8,  9.0]
                     ↓     ↓     ↓     ↓     ↓
Worker 1:         1.2 → 2.4
Worker 2:               3.4 → 6.8
Worker 3:                     5.6 → 11.2
Worker 4:                           7.8 → 15.6
Worker 1 (재사용):                        9.0 → 18.0
                                                ↓
results:                              [2.4, 6.8, 11.2, 15.6, 18.0]
```

`pool.map()`은 입력 순서를 보장하여 결과를 반환합니다.  
대량의 센서 데이터 필터링, 행렬 연산, 이미지 배치 처리에 효율적입니다.

---

## 13. 자주 하는 실수

### 멀티스레딩

| 실수 | 원인 | 해결 |
|------|------|------|
| 결과가 매번 달라짐 (Race Condition) | Lock 없이 공유 변수에 여러 스레드가 접근 | `with lock:` 블록으로 감싸기 |
| 프로그램이 종료되지 않음 | `daemon=False` 스레드가 무한 루프 중 | `Event`로 루프 종료하거나 `daemon=True` 설정 |
| `start()`와 `join()`이 같은 루프에 있음 | 순차 실행과 다를 바 없음 | `start()` 루프와 `join()` 루프 분리 |
| 데드락 | 여러 Lock을 다른 순서로 획득 | 모든 스레드에서 Lock 획득 순서를 동일하게 고정 |

### 멀티프로세싱

| 실수 | 원인 | 해결 |
|------|------|------|
| 프로세스가 무한 복제됨 | `if __name__ == '__main__':` 누락 | 프로세스 생성 코드를 해당 블록 안에 넣기 |
| 전역 변수를 수정해도 반영 안 됨 | 프로세스마다 독립된 메모리 | `Queue`나 `Pipe`로 데이터 전달 |
| `terminate()` 후 데드락 | 강제 종료로 Lock·Queue가 깨짐 | `Event.set()` → `join()` 순서로 정상 종료 |
| `queue.Queue`를 프로세스 간에 사용 | `threading`용 Queue는 프로세스 간 공유 불가 | `multiprocessing.Queue` 사용 |

### threading.Queue vs multiprocessing.Queue

```python
import queue               # 스레드 간 전용
import multiprocessing     # 프로세스 간 전용

q1 = queue.Queue()                   # ← 스레드에서 사용
q2 = multiprocessing.Queue()         # ← 프로세스에서 사용
```

---

*이 문서는 day2 · 03.02 Python 멀티스레딩 · 멀티프로세스 실습 내용을 기반으로 작성되었습니다.*
