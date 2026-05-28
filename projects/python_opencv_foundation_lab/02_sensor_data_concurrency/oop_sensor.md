# OOP · 센서 데이터 시뮬레이션

---

### 라이브러리 설치

```bash
python -m venv .venv
source .venv/bin/activate     # macOS / Linux
.venv\Scripts\activate        # Windows

pip install numpy matplotlib
```

---

## 목차

1. [OOP 세 가지 핵심 개념](#1-oop-세-가지-핵심-개념)
2. [추상 클래스 — abc 모듈](#2-추상-클래스--abc-모듈)
3. [상속 — super()와 __init__](#3-상속--super와-__init__)
4. [LidarSensor 구현](#4-lidarsensor-구현)
5. [ImuSensor 구현](#5-imusensor-구현)
6. [다형성으로 센서 통합 관리](#6-다형성으로-센서-통합-관리)
7. [극좌표 → 직교좌표 변환과 시각화](#7-극좌표--직교좌표-변환과-시각화)
8. [이동 평균 필터](#8-이동-평균-필터)
9. [JSON으로 데이터 저장과 로드](#9-json으로-데이터-저장과-로드)
10. [실시간 시각화](#10-실시간-시각화)
11. [자주 발생하는 오류](#11-자주-발생하는-오류)

---

## 1. OOP 세 가지 핵심 개념

이 실습 전체는 OOP 세 가지 기둥 위에 세워져 있습니다.

### 추상화 (Abstraction)

"무엇을 할 수 있는가"만 드러내고 "어떻게 하는가"는 감춥니다.  
`Sensor` 추상 클래스는 `get_data()`라는 인터페이스만 정의합니다.  
사용하는 쪽은 LiDAR인지 IMU인지 몰라도 `get_data()`를 호출하면 됩니다.

### 상속 (Inheritance)

공통 속성과 동작을 부모 클래스에 두고, 자식 클래스는 차이점만 구현합니다.  
`LidarSensor`와 `ImuSensor` 모두 `Sensor`를 상속해서 `name` 속성과 인터페이스를 물려받습니다.

### 다형성 (Polymorphism)

같은 메서드 이름이 타입마다 다르게 동작합니다.  
`sensor.get_data()`를 호출할 때 `sensor`가 LiDAR이면 각도·거리 배열을, IMU이면 시간·가속도 배열을 반환합니다.

```
클래스 다이어그램

[ Abstract Class: Sensor ]      ← 인터페이스 정의
          ▲
          │ (Inheritance)
   ┌──────┴──────────────┐
[ LidarSensor ]   [ ImuSensor ]  ← 구현체
  get_data()         get_data()
  → (angles,         → (t,
     distances)         accel)
```

---

## 2. 추상 클래스 — abc 모듈

### 왜 추상 클래스가 필요한가

`Sensor` 클래스를 일반 클래스로 만들면 `get_data()`를 구현하지 않은 자식 클래스도 인스턴스를 만들 수 있습니다.  
추상 클래스를 쓰면 **`get_data()`를 구현하지 않은 자식 클래스는 인스턴스 생성 시점에 즉시 `TypeError`**가 납니다.  
버그를 런타임 깊은 곳에서가 아니라, 가장 빠른 시점에 잡을 수 있습니다.

### 구현

```python
from abc import ABC, abstractmethod

class Sensor(ABC):
    def __init__(self, name):
        self.name = name        # 모든 센서에 공통인 이름

    @abstractmethod
    def get_data(self):         # 반드시 구현해야 하는 메서드 선언
        pass
```

- `ABC`: `Abstract Base Class`의 약자. 이걸 상속하면 추상 클래스가 됩니다.
- `@abstractmethod`: 이 데코레이터가 붙은 메서드를 구현하지 않으면 자식 클래스의 인스턴스 생성이 막힙니다.

```python
# 직접 인스턴스화 시 즉시 오류
try:
    s = Sensor("test")
except TypeError as e:
    print(e)   # Can't instantiate abstract class Sensor with abstract method get_data
```

---

## 3. 상속 — super()와 __init__

### super().__init__()을 반드시 호출해야 하는 이유

부모 클래스의 `__init__`을 호출해야 `self.name`이 초기화됩니다.  
`super().__init__(name)`을 빠뜨리면 `self.name`이 없어서 `AttributeError`가 납니다.

```python
class LidarSensor(Sensor):
    def __init__(self, name, scan_range=5.0, num_samples=360):
        super().__init__(name)       # Sensor.__init__ 호출 → self.name 초기화
        self.scan_range = scan_range # 자식 클래스만의 속성
        self.num_samples = num_samples
```

### 초기화 순서

```
LidarSensor("Hokuyo_LiDAR") 호출
    → LidarSensor.__init__ 실행
        → super().__init__("Hokuyo_LiDAR") 호출
            → Sensor.__init__ 실행
            → self.name = "Hokuyo_LiDAR"  ← 여기서 설정됨
        → self.scan_range = 5.0
        → self.num_samples = 360
```

---

## 4. LidarSensor 구현

LiDAR는 로봇 주변 360도 방향의 거리를 측정합니다.  
각도 배열과 거리 배열, 두 개의 NumPy 1D 배열로 한 번의 스캔을 표현합니다.

```python
class LidarSensor(Sensor):
    def __init__(self, name, scan_range=5.0, num_samples=360):
        super().__init__(name)
        self.scan_range = scan_range   # 기본 측정 거리 (m)
        self.num_samples = num_samples # 스캔 포인트 수

    def get_data(self):
        # 0~2π까지 균등 간격으로 각도 생성
        angles = np.linspace(0, 2 * np.pi, self.num_samples)

        # 기본 거리에 가우시안 노이즈 추가
        distances = self.scan_range + np.random.normal(0, 0.1, self.num_samples)

        return angles, distances
```

### 핵심 NumPy 함수

| 함수 | 역할 |
|------|------|
| `np.linspace(0, 2π, 360)` | 0~2π를 360등분 → 각도 배열 |
| `np.random.normal(0, 0.1, 360)` | 평균 0, 표준편차 0.1의 가우시안 노이즈 |

실제 LiDAR 센서는 측정값 주변에 가우시안 오차가 붙습니다.  
`scan_range + noise` 형태가 "이상적인 거리 + 현실 오차"를 모사합니다.

```python
lidar = LidarSensor("Hokuyo_LiDAR")
angles, distances = lidar.get_data()

print(angles.shape)     # (360,)
print(distances.shape)  # (360,)
print(distances.mean()) # 약 5.0m
```

---

## 5. ImuSensor 구현

IMU는 3축(X/Y/Z) 가속도를 시간에 따라 측정합니다.  
시간 배열(1D)과 가속도 배열(2D), 두 개로 데이터를 표현합니다.

```python
class ImuSensor(Sensor):
    def __init__(self, name, axis=3, duration=100):
        super().__init__(name)
        self.axis = axis         # 축 수 (X/Y/Z = 3)
        self.duration = duration # 측정 시간 스텝 수

    def get_data(self):
        t = np.arange(self.duration)                            # [0, 1, 2, ..., 99]
        accel = np.random.randn(self.duration, self.axis) * 0.5 # shape (100, 3)
        return t, accel
```

### 2D 배열 구조 이해

`np.random.randn(duration, axis)` → shape `(100, 3)`:

```
accel 배열 (100행 × 3열)

       X축    Y축    Z축
t=0  [ 0.12, -0.34,  9.81 ]   ← 0번째 시간
t=1  [-0.05,  0.21, -0.11 ]   ← 1번째 시간
t=2  [ 0.33, -0.09,  0.44 ]   ← 2번째 시간
...
t=99 [ 0.01,  0.08, -0.23 ]   ← 99번째 시간
```

```python
imu = ImuSensor("InvenSense_IMU")
t, accel = imu.get_data()

print(t.shape)       # (100,)
print(accel.shape)   # (100, 3)
print(accel[:, 0])   # X축 전체 (0번째 열)
print(accel[:, 1])   # Y축 전체 (1번째 열)
print(accel[:, 2])   # Z축 전체 (2번째 열)
```

`accel[:, 0]`의 의미: "모든 행에서(=시간 전체에서) 0번째 열(X축)만 선택"

---

## 6. 다형성으로 센서 통합 관리

### 핵심 아이디어

서로 타입이 다른 센서를 **하나의 리스트에 넣고 같은 코드로 처리**합니다.  
이게 가능한 이유는 두 클래스가 같은 인터페이스(`get_data()`)를 구현했기 때문입니다.

```python
lidar = LidarSensor("Hokuyo_LiDAR")
imu   = ImuSensor("InvenSense_IMU")

sensors = [lidar, imu]   # 다른 타입이지만 같은 인터페이스

for sensor in sensors:
    data = sensor.get_data()   # 타입 관계없이 동일하게 호출 ← 다형성 핵심
    print(sensor.name)
```

### isinstance — 타입별 분기 처리

데이터를 어떻게 시각화할지는 타입마다 다릅니다.  
`isinstance()`로 타입을 확인해서 분기합니다.

```python
for sensor in sensors:
    data = sensor.get_data()

    if isinstance(sensor, LidarSensor):
        angles, dists = data
        # LiDAR 전용 시각화

    elif isinstance(sensor, ImuSensor):
        t, accel = data
        # IMU 전용 시각화
```

`isinstance(sensor, LidarSensor)`:
- `sensor`가 `LidarSensor`의 인스턴스이면 `True`
- `LidarSensor`를 상속한 자식 클래스의 인스턴스도 `True`

---

## 7. 극좌표 → 직교좌표 변환과 시각화

### 극좌표 변환이 필요한 이유

LiDAR는 `(각도, 거리)` 형태인 **극좌표**로 데이터를 냅니다.  
2D 지도에 표시하려면 `(x, y)` 형태인 **직교좌표**로 변환해야 합니다.

```
극좌표 (r, θ) → 직교좌표 (x, y)

x = r × cos(θ)
y = r × sin(θ)
```

```python
angles, dists = lidar.get_data()

x = dists * np.cos(angles)   # shape (360,)
y = dists * np.sin(angles)   # shape (360,)
```

NumPy 브로드캐스팅 덕분에 360개 포인트 전체를 루프 없이 한 줄로 변환합니다.

### 두 센서 동시 시각화

```python
def main():
    lidar = LidarSensor("Hokuyo_LiDAR")
    imu   = ImuSensor("InvenSense_IMU")
    sensors = [lidar, imu]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    for sensor in sensors:
        data = sensor.get_data()

        if isinstance(sensor, LidarSensor):
            angles, dists = data
            x = dists * np.cos(angles)
            y = dists * np.sin(angles)
            ax1.scatter(x, y, s=5, c='blue')
            ax1.set_title(f"{sensor.name} — 2D 스캔")
            ax1.set_aspect('equal')   # 가로세로 비율 1:1 필수
            ax1.set_xlabel("X (m)")
            ax1.set_ylabel("Y (m)")

        elif isinstance(sensor, ImuSensor):
            t, accel = data
            ax2.plot(t, accel[:, 0], label='X축')
            ax2.plot(t, accel[:, 1], label='Y축')
            ax2.plot(t, accel[:, 2], label='Z축')
            ax2.set_title(f"{sensor.name} — 3축 가속도")
            ax2.set_xlabel("Time (samples)")
            ax2.set_ylabel("Acceleration (m/s²)")
            ax2.legend()

    plt.tight_layout()   # 서브플롯 간 여백 자동 조정
    plt.show()
```

`set_aspect('equal')`을 빠뜨리면 LiDAR 원형 스캔이 타원으로 찌그러집니다.

---

## 8. 이동 평균 필터

### 왜 필터가 필요한가

센서 데이터에는 노이즈가 섞입니다. 이동 평균 필터는 인접한 여러 값의 평균을 내서 노이즈를 줄입니다.  
`window_size`가 클수록 더 매끄럽지만, 빠른 변화도 같이 흐려집니다.

### np.convolve로 구현

```python
def moving_average(data, window_size=5):
    kernel = np.ones(window_size) / window_size   # 균등 가중치 커널
    return np.convolve(data, kernel, mode='valid')
```

`mode='valid'`: 경계 효과가 없는 구간만 반환합니다.  
결과 길이 = `len(data) - window_size + 1` (원래보다 짧아집니다)

```python
imu = ImuSensor("InvenSense_IMU", duration=200)
t, accel = imu.get_data()

filtered = moving_average(accel[:, 0], window_size=10)

plt.figure(figsize=(10, 4))
plt.plot(t, accel[:, 0], label='Raw (X축)', alpha=0.5)
plt.plot(t[:len(filtered)], filtered, label='Filtered', linewidth=2)
# t[:len(filtered)] — filtered가 짧아졌으므로 시간 배열도 맞춰 자름
plt.legend()
plt.show()
```

### mode별 동작 비교

| mode | 출력 길이 | 특징 |
|------|-----------|------|
| `'valid'` | `len(data) - window + 1` | 경계 효과 없음. 필터링에 권장 |
| `'same'` | `len(data)` | 원래 길이 유지. 경계 처리 있음 |
| `'full'` | `len(data) + window - 1` | 전체 합성곱 결과 |

---

## 9. JSON으로 데이터 저장과 로드

### ndarray는 직접 JSON 저장 불가

NumPy 배열은 Python 기본 타입이 아니라 JSON 직렬화가 안 됩니다.  
`.tolist()`로 Python 리스트로 변환한 뒤 저장해야 합니다.

### 저장

```python
import json

imu = ImuSensor("InvenSense_IMU")
t, accel = imu.get_data()

log = {
    "sensor": imu.name,
    "time":   t.tolist(),       # ndarray → list 변환 필수
    "accel":  accel.tolist()    # (100, 3) ndarray → 중첩 list
}

with open("sensor_log.json", "w") as f:
    json.dump(log, f, indent=2)
```

저장된 JSON 구조:

```json
{
  "sensor": "InvenSense_IMU",
  "time": [0, 1, 2, ...],
  "accel": [
    [0.12, -0.34, 0.11],
    [-0.05, 0.21, 0.44],
    ...
  ]
}
```

### 로드

```python
with open("sensor_log.json", "r") as f:
    loaded = json.load(f)

print(loaded["sensor"])                    # "InvenSense_IMU"

t_loaded     = np.array(loaded["time"])   # list → ndarray 복원
accel_loaded = np.array(loaded["accel"])  # shape (100, 3) 복원

print(t_loaded.shape)      # (100,)
print(accel_loaded.shape)  # (100, 3)
```

| 작업 | 코드 |
|------|------|
| ndarray → JSON | `.tolist()` |
| JSON → ndarray | `np.array(loaded_list)` |

---

## 10. 실시간 시각화

### plt.ion() / plt.ioff()

인터랙티브 모드를 켜면 `plt.show()` 없이도 화면이 즉시 갱신됩니다.  
`plt.pause()`가 화면 갱신과 대기를 함께 처리합니다.

```python
lidar = LidarSensor("Hokuyo_LiDAR")

plt.ion()                           # 인터랙티브 모드 ON
fig, ax = plt.subplots(figsize=(6, 6))

for frame in range(10):
    ax.clear()                      # 이전 프레임 지우기

    angles, dists = lidar.get_data()
    x = dists * np.cos(angles)
    y = dists * np.sin(angles)

    ax.scatter(x, y, s=5, c='blue')
    ax.set_title(f"LiDAR Real-time Scan (frame {frame + 1}/10)")
    ax.set_aspect('equal')
    ax.set_xlim(-7, 7)              # 축 범위 고정 필수 — 없으면 매 프레임 축이 바뀜
    ax.set_ylim(-7, 7)

    plt.pause(0.1)                  # 0.1초 대기 + 화면 갱신

plt.ioff()   # 인터랙티브 모드 OFF
plt.show()
```

### 실시간 시각화 주의사항

| 주의 | 이유 |
|------|------|
| Figure는 루프 밖에서 한 번만 | 루프 안에서 생성하면 매 프레임 새 창이 열려 메모리 누수 발생 |
| `ax.clear()` 호출 필수 | 없으면 이전 프레임 위에 계속 덧그려짐 |
| 축 범위 `set_xlim`/`set_ylim` 고정 | 없으면 매 프레임 축이 자동 조정되어 상대적 변화 파악 불가 |
| `plt.ioff()` 후 `plt.show()` | 루프 종료 후 화면을 유지하려면 필요 |

---

## 11. 자주 발생하는 오류

| 오류 | 원인 | 해결 |
|------|------|------|
| `TypeError: Can't instantiate abstract class` | 자식 클래스에서 `get_data()` 구현 안 함 | 메서드 이름 확인 후 구현 |
| `AttributeError: 'LidarSensor' object has no attribute 'name'` | `super().__init__(name)` 빠뜨림 | 자식 클래스 `__init__` 첫 줄에 추가 |
| `ValueError: operands could not be broadcast` | 배열 shape 불일치 | `.shape` 출력해서 확인 |
| 그래프가 안 뜨거나 바로 닫힘 | `plt.show()` 누락 | 마지막에 `plt.show()` 추가 |
| LiDAR 스캔이 타원으로 찌그러짐 | `ax.set_aspect('equal')` 누락 | scatter 그린 후 추가 |
| JSON 저장 시 `TypeError: Object of type ndarray is not JSON serializable` | ndarray를 그대로 저장 시도 | `.tolist()` 로 변환 후 저장 |
| 이동 평균 길이 불일치 | `mode='valid'`로 출력이 짧아짐 | `t[:len(filtered)]`로 시간 배열 맞춤 |

---

*이 문서는 day2 · 02.03 센서 데이터 시뮬레이션 실습 내용을 기반으로 작성되었습니다.*
