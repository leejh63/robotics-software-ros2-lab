# Matplotlib — 센서 데이터 시각화

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

1. [Matplotlib이 왜 필요한가](#1-matplotlib이-왜-필요한가)
2. [구조 이해 — Figure, Axes, Artist](#2-구조-이해--figure-axes-artist)
3. [기본 그래프 작성](#3-기본-그래프-작성)
4. [로봇 개발에서 자주 쓰이는 그래프 유형](#4-로봇-개발에서-자주-쓰이는-그래프-유형)
5. [서브플롯 (Subplot)](#5-서브플롯-subplot)
6. [그래프 꾸미기](#6-그래프-꾸미기)
7. [파일 저장](#7-파일-저장)
8. [실시간(동적) 시각화](#8-실시간동적-시각화)
9. [센서 데이터 시뮬레이션 통합 실습 — OOP + NumPy + Matplotlib](#9-센서-데이터-시뮬레이션-통합-실습--oop--numpy--matplotlib)
10. [Matplotlib 입문자가 자주 하는 실수](#10-matplotlib-입문자가-자주-하는-실수)

---

## 1. Matplotlib이 왜 필요한가

### 숫자만으로는 부족하다

로봇 센서에서 수집된 데이터는 숫자 배열입니다.  
LiDAR가 360개 거리를 반환하고, IMU가 3축 가속도를 반환해도, **그 숫자만 보면 무슨 일이 일어나는지 알기 어렵습니다.**

```python
# 이 숫자만 보고 무엇을 알 수 있나?
distances = [4.97, 5.03, 4.88, 5.12, 0.42, 0.38, 4.95, ...]
```

숫자를 그림으로 바꾸면 즉시 보입니다.

- 전방에 갑자기 0.4m 장애물이 있다
- IMU 신호에 특정 주파수의 진동이 섞여 있다
- PID 제어기의 오차가 수렴하고 있는지 발산하고 있는지

### 로봇 개발에서 시각화의 역할

| 상황 | Matplotlib 활용 |
|------|-----------------|
| 센서 캘리브레이션 | 보정 전후 데이터를 겹쳐서 비교 |
| PID 튜닝 | 오차 신호의 수렴/발산 확인 |
| 노이즈 분석 | 히스토그램으로 분포 확인 |
| LiDAR 스캔 | 극좌표 → 직교좌표 변환 후 2D 지도 표시 |
| 디버깅 | 의도치 않은 값 스파이크 탐지 |

```python
import numpy as np
import matplotlib.pyplot as plt

# 시각화 전 — 숫자만 보임
distances = np.random.uniform(0.5, 5.0, 360)
print(distances[:5])   # [2.31 4.72 1.09 3.88 0.47]

# 시각화 후 — 장애물 위치가 한눈에 보임
angles = np.linspace(0, 2 * np.pi, 360)
x = distances * np.cos(angles)
y = distances * np.sin(angles)

fig, ax = plt.subplots()
ax.scatter(x, y, s=5, c='blue')
ax.set_aspect('equal')
plt.show()
```

---

## 2. 구조 이해 — Figure, Axes, Artist

### 세 계층

Matplotlib 코드를 처음 보면 `plt`, `fig`, `ax`가 섞여서 혼란스럽습니다.  
구조를 한 번 이해하면 어떤 코드든 읽기 쉬워집니다.

```
Figure (캔버스 전체)
  └── Axes (좌표계 — "그래프 하나")
        ├── 제목, 축 레이블, 눈금
        └── Artist (선, 점, 텍스트 등 모든 그림 요소)
```

**Figure**: 가장 바깥쪽 창 또는 페이지. 하나 이상의 Axes를 포함합니다.  
**Axes**: 실제 데이터가 그려지는 구역. "그래프 하나"에 해당합니다. 제목, 축 레이블, 눈금을 포함합니다.  
**Artist**: Figure에 보이는 모든 것(선, 점, 텍스트, 범례 등). Axes에 데이터를 그리면 자동으로 Artist 객체가 생성됩니다.

### plt vs ax — 혼용하면 헷갈리는 이유

Matplotlib에는 두 가지 인터페이스가 있습니다.

```python
# pyplot 방식 (간단한 그래프에 적합)
plt.plot(x, y)
plt.title("제목")
plt.show()

# 객체지향 방식 (권장 — 여러 Axes를 다룰 때 명확)
fig, ax = plt.subplots()
ax.plot(x, y)
ax.set_title("제목")
plt.show()
```

서브플롯이 하나일 때는 두 방식이 같아 보이지만, **서브플롯이 여러 개일 때는 pyplot 방식이 어느 Axes에 그리는지 모호해집니다.**  
로봇 개발에서는 거의 항상 여러 센서 데이터를 함께 표시하므로 **객체지향 방식(`fig, ax`)을 기본으로 씁니다.**

### Figure와 Axes 생성

```python
import matplotlib.pyplot as plt

# 1개 Axes
fig, ax = plt.subplots()

# 크기 지정 (인치 단위)
fig, ax = plt.subplots(figsize=(10, 4))

# 여러 개 Axes
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))   # 1행 2열
fig, axes       = plt.subplots(2, 2, figsize=(10, 8))   # 2행 2열
```

---

## 3. 기본 그래프 작성

### 라인 그래프 — ax.plot()

```python
import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(0, 2 * np.pi, 200)
y = np.sin(x)

fig, ax = plt.subplots(figsize=(10, 4))

ax.plot(x, y)

ax.set_title("sin(x)")
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.grid(True)

plt.tight_layout()
plt.show()
```

### 주요 스타일 옵션

```python
ax.plot(x, y,
        label="sin",           # 범례에 표시될 이름
        color="steelblue",     # 색상 (이름, hex 모두 가능)
        linewidth=2,           # 선 두께
        linestyle="--",        # 선 스타일: "-", "--", "-.", ":"
        marker="o",            # 점 마커: "o", "^", "s", "x" 등
        markersize=4,          # 마커 크기
        alpha=0.7)             # 투명도 (0~1)
```

### 범례 표시

```python
ax.plot(x, np.sin(x), label="sin")
ax.plot(x, np.cos(x), label="cos")
ax.legend()                    # label= 값이 자동으로 범례에 표시됨

# 위치 지정
ax.legend(loc="upper right")   # 'upper left', 'lower right', 'best' 등
```

### 빠른 미리보기 — plt.show() 전 흐름

```python
fig, ax = plt.subplots()

# 데이터를 그리는 모든 호출이 여기에 들어감
ax.plot(...)
ax.scatter(...)

plt.tight_layout()   # 여백 자동 조정 — show() 직전에 호출
plt.show()           # 반드시 마지막에 호출
```

`plt.tight_layout()`을 빠뜨리면 제목이나 레이블이 잘리는 경우가 생깁니다.

---

## 4. 로봇 개발에서 자주 쓰이는 그래프 유형

### ① 시계열 라인 그래프 — IMU, 엔코더, 배터리

시간에 따른 변화를 볼 때 씁니다. PID 제어기 튜닝에서 오차 신호가 수렴하는지 확인하거나, 배터리 전압 강하를 모니터링할 때 필수입니다.

```python
import numpy as np
import matplotlib.pyplot as plt

time = np.linspace(0, 10, 100)
imu_accel = np.sin(time) + 0.1 * np.random.randn(100)

fig, ax = plt.subplots(figsize=(10, 4))

ax.plot(time, imu_accel, label="Accel Z-axis", color="steelblue")

ax.set_title("IMU Telemetry")
ax.set_xlabel("Time (s)")
ax.set_ylabel("Acceleration (m/s²)")
ax.grid(True, alpha=0.3)
ax.legend()

plt.tight_layout()
plt.show()
```

3축 IMU 데이터를 한 그래프에 표시할 때:

```python
# accel_data: shape (100, 3) — 행: 타임스텝, 열: x/y/z
t = np.arange(100)
accel_data = np.random.randn(100, 3) * 0.5

fig, ax = plt.subplots(figsize=(10, 4))

ax.plot(t, accel_data[:, 0], label='X-axis')
ax.plot(t, accel_data[:, 1], label='Y-axis')
ax.plot(t, accel_data[:, 2], label='Z-axis')

ax.set_title("IMU 3-axis Acceleration")
ax.set_xlabel("Time step")
ax.set_ylabel("Acceleration")
ax.legend()
ax.grid(True)

plt.show()
```

`accel_data[:, 0]`은 "모든 행에서 0번째 열(X축) 전체"를 의미합니다.

### ② 산점도 — LiDAR 포인트 클라우드

극좌표(거리 + 각도)를 직교좌표(x, y)로 변환한 뒤 점으로 찍어 2D 환경 지도를 만듭니다.

```python
import numpy as np
import matplotlib.pyplot as plt

angles    = np.linspace(0, 2 * np.pi, 360)
distances = 2 + 0.5 * np.random.randn(360)   # 평균 2m, 노이즈 포함

# 극좌표 → 직교좌표 변환
x = distances * np.cos(angles)
y = distances * np.sin(angles)

fig, ax = plt.subplots(figsize=(6, 6))

ax.scatter(x, y, s=5, c='blue', label='LiDAR Scan')

ax.set_title("LiDAR Obstacle Detection")
ax.set_xlabel("X distance (m)")
ax.set_ylabel("Y distance (m)")
ax.grid(True)
ax.legend()
ax.set_aspect('equal')   # 반드시 1:1 비율 — 없으면 원이 타원으로 찌그러짐

plt.show()
```

`ax.scatter()`의 주요 파라미터:

| 파라미터 | 설명 | 예시 |
|----------|------|------|
| `s` | 점 크기 | `s=5` |
| `c` | 점 색상 (이름, 배열 모두 가능) | `c='red'`, `c=distances` |
| `cmap` | `c`가 숫자 배열일 때 색상 지도 | `cmap='viridis'` |
| `alpha` | 투명도 | `alpha=0.5` |

거리에 따라 색을 다르게 표시하면 장애물까지의 거리를 직관적으로 볼 수 있습니다:

```python
sc = ax.scatter(x, y, s=5, c=distances, cmap='coolwarm')
plt.colorbar(sc, ax=ax, label='Distance (m)')
```

### ③ 히스토그램 — 노이즈 분포 분석

센서 노이즈가 어떻게 분포하는지 확인합니다.  
가우시안인지, 편향이 있는지, 이상값이 있는지를 한눈에 파악합니다.

```python
import numpy as np
import matplotlib.pyplot as plt

noise_data = np.random.normal(0, 0.05, 1000)   # 5cm 노이즈 시뮬레이션

fig, ax = plt.subplots()

ax.hist(noise_data, bins=30, color='mediumseagreen', edgecolor='black', alpha=0.7)

ax.set_title("Sensor Noise Distribution")
ax.set_xlabel("Error (m)")
ax.set_ylabel("Count")

plt.tight_layout()
plt.show()
```

`bins`는 구간 수입니다. 너무 적으면 분포가 뭉개지고, 너무 많으면 개별 노이즈가 다 보여서 분포를 파악하기 어렵습니다. 데이터 수의 제곱근이 경험적 기준입니다.

### ④ 막대 그래프 — 비교

여러 센서의 평균 오차나 각 방향의 장애물 수를 비교할 때 씁니다.

```python
sensors = ['LiDAR', 'IMU', 'Camera', 'Ultrasonic']
errors  = [0.05, 0.02, 0.10, 0.15]

fig, ax = plt.subplots()

ax.bar(sensors, errors, color=['steelblue', 'tomato', 'gold', 'mediumseagreen'])

ax.set_title("Sensor Measurement Errors")
ax.set_xlabel("Sensor")
ax.set_ylabel("Mean Error (m)")

plt.tight_layout()
plt.show()
```

---

## 5. 서브플롯 (Subplot)

여러 센서 데이터를 한 화면에 비교할 때 씁니다.  
로봇 진단 대시보드처럼 쓸 수 있습니다.

### 1행 2열 서브플롯

```python
import numpy as np
import matplotlib.pyplot as plt

# 데이터 생성
angles    = np.linspace(0, 2 * np.pi, 360)
distances = 2 + 0.5 * np.random.randn(360)
x = distances * np.cos(angles)
y = distances * np.sin(angles)

time      = np.linspace(0, 10, 100)
imu_accel = np.sin(time) + 0.1 * np.random.randn(100)

# 서브플롯 생성
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# 왼쪽: LiDAR 산점도
ax1.scatter(x, y, s=5, c='red', label='LiDAR Scan')
ax1.set_title("LiDAR Obstacle Detection")
ax1.set_xlabel("X distance (m)")
ax1.set_ylabel("Y distance (m)")
ax1.grid(True)
ax1.legend()
ax1.set_aspect('equal')

# 오른쪽: IMU 시계열
ax2.plot(time, imu_accel, label='Accel Z-axis')
ax2.set_title("IMU Telemetry")
ax2.set_xlabel("Time (s)")
ax2.set_ylabel("Acceleration (m/s²)")
ax2.grid(True)
ax2.legend()

plt.tight_layout()
plt.savefig("sensor_diagnostic.png")
plt.show()
```

### 2행 2열 서브플롯

```python
fig, axes = plt.subplots(2, 2, figsize=(12, 8))

axes[0, 0].plot(time, imu_accel[:, 0], label='X')
axes[0, 0].set_title("IMU X-axis")

axes[0, 1].plot(time, imu_accel[:, 1], label='Y')
axes[0, 1].set_title("IMU Y-axis")

axes[1, 0].scatter(x, y, s=3)
axes[1, 0].set_title("LiDAR Scan")
axes[1, 0].set_aspect('equal')

axes[1, 1].hist(distances, bins=20)
axes[1, 1].set_title("Distance Distribution")

plt.tight_layout()
plt.show()
```

### 크기가 다른 서브플롯 — GridSpec

```python
import matplotlib.gridspec as gridspec

fig = plt.figure(figsize=(12, 8))
gs  = gridspec.GridSpec(2, 2)

ax_big  = fig.add_subplot(gs[:, 0])   # 왼쪽 전체 (2행 높이)
ax_top  = fig.add_subplot(gs[0, 1])   # 오른쪽 위
ax_bot  = fig.add_subplot(gs[1, 1])   # 오른쪽 아래

ax_big.scatter(x, y, s=3)
ax_big.set_title("LiDAR Scan")
ax_big.set_aspect('equal')

ax_top.plot(time, imu_accel)
ax_top.set_title("IMU Accel")

ax_bot.hist(distances, bins=20)
ax_bot.set_title("Distance Dist.")

plt.tight_layout()
plt.show()
```

---

## 6. 그래프 꾸미기

### 축 범위 고정

실시간 플롯에서 데이터가 바뀔 때마다 축이 자동으로 맞춰지면 상대적 변화를 보기 어렵습니다.  
로봇 위치 추적처럼 공간 범위가 정해진 경우에는 항상 고정합니다.

```python
ax.set_xlim(-6, 6)     # x축 -6 ~ 6m
ax.set_ylim(-6, 6)     # y축 -6 ~ 6m
ax.set_ylim(-2, 2)     # IMU 가속도 범위
```

### 격자(Grid)

```python
ax.grid(True)                    # 기본 격자
ax.grid(True, alpha=0.3)         # 투명도 조절
ax.grid(True, linestyle='--')    # 점선 격자
ax.grid(axis='y')                # y축 격자만
```

### 컬러바 — 색으로 값 표현

```python
sc = ax.scatter(x, y, s=5, c=distances, cmap='viridis')
cb = plt.colorbar(sc, ax=ax)
cb.set_label("Distance (m)")
```

자주 쓰이는 colormap:

| cmap | 특징 |
|------|------|
| `viridis` | 균일한 밝기 변화, 기본 권장 |
| `coolwarm` | 파란(낮음) → 빨강(높음), 편차 표현 |
| `RdBu` | 빨강 → 파랑, 양/음 데이터 |
| `gray` | 흑백, 이미지 |

### 텍스트와 주석

```python
ax.text(2, 0.5, "장애물 감지", fontsize=10, color='red')

ax.annotate("최솟값",
            xy=(min_idx, min_val),       # 화살표 끝 (가리키는 점)
            xytext=(min_idx + 5, 1.0),   # 텍스트 위치
            arrowprops=dict(arrowstyle="->", color='black'))
```

### 한글 폰트 설정 (Linux / macOS)

Matplotlib 기본 설정에서는 한글이 깨집니다.

```python
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# Linux — 나눔 폰트 설치 후
plt.rcParams['font.family'] = 'NanumGothic'

# macOS
plt.rcParams['font.family'] = 'AppleGothic'

# 마이너스 기호 깨짐 방지
plt.rcParams['axes.unicode_minus'] = False
```

---

## 7. 파일 저장

### plt.savefig()

```python
plt.tight_layout()
plt.savefig("sensor_diagnostic.png")       # PNG (기본)
plt.savefig("sensor_diagnostic.pdf")       # PDF — 벡터 형식, 확대해도 안 깨짐
plt.savefig("sensor_diagnostic.png", dpi=150)  # 해상도 지정 (기본 100)
plt.savefig("sensor_diagnostic.png", bbox_inches='tight')  # 여백 자동 자름
plt.show()
```

`plt.savefig()`는 반드시 `plt.show()` **전에** 호출해야 합니다.  
`plt.show()`를 먼저 호출하면 Figure가 초기화되어 빈 파일이 저장됩니다.

### 저장 형식 비교

| 형식 | 특징 | 추천 용도 |
|------|------|-----------|
| PNG | 무손실 비트맵 | 보고서 삽입, 슬랙 공유 |
| PDF | 벡터 형식 | 논문, 확대해도 선명 |
| SVG | 벡터, 웹 호환 | 웹 페이지 |

---

## 8. 실시간(동적) 시각화

로봇의 Sense-Think-Act 루프를 코드로 모사합니다.  
`plt.show()`는 화면을 블로킹하기 때문에 실시간 업데이트에는 `plt.ion()`을 씁니다.

### plt.ion() — 인터랙티브 모드

```python
import numpy as np
import matplotlib.pyplot as plt

plt.ion()                          # 인터랙티브 모드 ON — plt.show() 없이 즉시 갱신
fig, ax = plt.subplots(figsize=(6, 6))

while True:
    ax.clear()                     # 이전 프레임 지우기

    # 새 데이터 생성 (실제 로봇에서는 센서에서 읽어옴)
    angles    = np.linspace(0, 2 * np.pi, 360)
    distances = 2 + 0.5 * np.random.randn(360)
    x = distances * np.cos(angles)
    y = distances * np.sin(angles)

    ax.scatter(x, y, s=5, c='blue')
    ax.set_title("LiDAR Real-time Scan")
    ax.set_xlabel("X distance (m)")
    ax.set_ylabel("Y distance (m)")
    ax.set_aspect('equal')
    ax.set_xlim(-6, 6)             # 축 범위 고정 — 없으면 매 프레임 축이 바뀜
    ax.set_ylim(-6, 6)

    plt.pause(0.1)                 # 0.1초 대기 + 화면 갱신 (핵심 함수)
```

`plt.pause(0.1)`: 0.1초 동안 이벤트 루프를 돌리면서 화면을 갱신합니다.  
`ax.clear()`: 이전 프레임의 데이터를 지워서 새 데이터만 보이게 합니다.

### 키보드 인터럽트로 종료

```python
plt.ion()
fig, ax = plt.subplots()

try:
    while True:
        ax.clear()
        # ... 데이터 업데이트 ...
        plt.pause(0.1)
except KeyboardInterrupt:
    plt.close()
    print("시각화 종료")
```

### set_data() — 더 빠른 업데이트

`ax.clear()` 후 다시 그리는 방법은 간단하지만, **Artist 객체를 매 프레임 새로 만들기 때문에 느립니다.**  
많은 점이나 긴 시계열을 고속으로 업데이트할 때는 `set_data()`로 데이터만 교체합니다.

```python
plt.ion()
fig, ax = plt.subplots()

t_data = []
y_data = []

# 초기 선 객체 생성 (한 번만)
line, = ax.plot([], [], color='steelblue')
ax.set_xlim(0, 100)
ax.set_ylim(-2, 2)
ax.set_title("IMU Real-time")

for i in range(200):
    t_data.append(i)
    y_data.append(np.sin(i * 0.1) + 0.1 * np.random.randn())

    # 데이터만 교체 — Figure 구조는 그대로
    line.set_data(t_data, y_data)
    ax.set_xlim(max(0, i - 100), i + 10)  # 슬라이딩 윈도우

    plt.pause(0.05)
```

---

## 9. 센서 데이터 시뮬레이션 통합 실습 — OOP + NumPy + Matplotlib

OOP로 설계한 센서 클래스에 NumPy 연산과 Matplotlib 시각화를 통합한 예제입니다.  
실제 로봇 소프트웨어의 구조와 거의 같습니다.

### 전체 구조

```
추상 클래스 Sensor
    ├── LidarSensor  → get_data() → (angles, distances) NumPy 배열
    └── ImuSensor    → get_data() → (time, accel_data)  NumPy 배열

main()
    → 센서 리스트에서 다형성으로 데이터 수집
    → isinstance()로 분기
    → Matplotlib으로 시각화
```

### 추상 클래스 정의

```python
import numpy as np
import matplotlib.pyplot as plt
from abc import ABC, abstractmethod

class Sensor(ABC):
    def __init__(self, name):
        self.name = name

    @abstractmethod
    def get_data(self):
        pass
```

`@abstractmethod`: 자식 클래스에서 `get_data()`를 구현하지 않으면 인스턴스 생성 시 즉시 `TypeError`가 납니다.  
센서 종류가 바뀌어도 상위 코드를 수정할 필요 없는 **하드웨어 추상화 계층(HAL)**의 역할을 합니다.

### LiDAR 센서 클래스

```python
class LidarSensor(Sensor):
    def __init__(self, name, num_samples=360):
        super().__init__(name)
        self.num_samples = num_samples

    def get_data(self):
        angles    = np.linspace(0, 2 * np.pi, self.num_samples)
        distances = 5.0 + np.random.normal(0, 0.1, self.num_samples)
        return angles, distances
```

`np.random.normal(0, 0.1, ...)`: 평균 0, 표준편차 0.1m의 가우시안 노이즈.  
실제 LiDAR 센서는 측정값 주변에 이런 오차가 붙습니다.

### IMU 센서 클래스

```python
class ImuSensor(Sensor):
    def __init__(self, name, duration=100):
        super().__init__(name)
        self.duration = duration

    def get_data(self):
        t          = np.arange(self.duration)                    # 시간 인덱스 0~99
        accel_data = np.random.randn(self.duration, 3) * 0.5    # shape (100, 3)
        return t, accel_data
```

`np.random.randn(duration, 3)` → shape `(100, 3)` 2D 배열.  
`accel_data[:, 0]`는 X축 전체, `accel_data[:, 1]`는 Y축 전체입니다.

### 다형성으로 통합 처리 + 시각화

```python
def main():
    lidar = LidarSensor("Hokuyo_LiDAR")
    imu   = ImuSensor("InvenSense_IMU")

    sensors = [lidar, imu]   # 다른 타입이지만 같은 인터페이스

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    for sensor in sensors:
        data = sensor.get_data()   # 타입에 관계없이 동일하게 호출 — 다형성 핵심

        if isinstance(sensor, LidarSensor):
            angles, dists = data
            x = dists * np.cos(angles)   # 극좌표 → 직교좌표
            y = dists * np.sin(angles)
            ax1.scatter(x, y, s=5, c='blue', label=sensor.name)
            ax1.set_title("LiDAR Scan (2D)")
            ax1.set_xlabel("X distance (m)")
            ax1.set_ylabel("Y distance (m)")
            ax1.grid(True)
            ax1.legend()
            ax1.set_aspect('equal')

        elif isinstance(sensor, ImuSensor):
            time, accel = data
            ax2.plot(time, accel[:, 0], label='X-axis')
            ax2.plot(time, accel[:, 1], label='Y-axis')
            ax2.plot(time, accel[:, 2], label='Z-axis')
            ax2.set_title("IMU Acceleration")
            ax2.set_xlabel("Time step")
            ax2.set_ylabel("Acceleration")
            ax2.grid(True)
            ax2.legend()

    plt.tight_layout()
    plt.savefig("sensor_diagnostic.png")
    plt.show()

if __name__ == "__main__":
    main()
```

`for sensor in sensors:` 루프가 로봇의 **Sense 루틴**입니다.  
실제 로봇은 이 루틴을 수백 ms 단위로 반복해서 환경을 인식합니다.

### 심화 — 이동 평균 필터 시각화

IMU 노이즈를 NumPy로 줄이고 필터링 전후를 비교 시각화합니다.

```python
def moving_average(data, window_size=5):
    kernel = np.ones(window_size) / window_size
    return np.convolve(data, kernel, mode='valid')
    # mode='valid': 경계 효과 없이 완전히 겹치는 구간만 반환

imu  = ImuSensor("IMU")
t, accel = imu.get_data()

filtered = moving_average(accel[:, 0], window_size=10)

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(t,              accel[:, 0],  label='Raw',      alpha=0.5, color='gray')
ax.plot(t[:len(filtered)], filtered, label='Filtered',             color='steelblue')
ax.legend()
ax.set_title("IMU X-axis: Raw vs Filtered")
ax.set_xlabel("Time step")
ax.set_ylabel("Acceleration")
ax.grid(True)
plt.show()
```

`mode='valid'`를 쓰면 출력 길이가 `len(data) - window_size + 1`이라서 원래 시간 배열보다 짧아집니다.  
`t[:len(filtered)]`로 길이를 맞춰줘야 합니다.

### 심화 — 실시간 LiDAR 시각화

```python
lidar = LidarSensor("LiDAR")

plt.ion()
fig, ax = plt.subplots(figsize=(6, 6))

try:
    while True:
        ax.clear()

        angles, dists = lidar.get_data()
        x = dists * np.cos(angles)
        y = dists * np.sin(angles)

        ax.scatter(x, y, s=5, c='blue')
        ax.set_title("LiDAR Real-time Scan")
        ax.set_aspect('equal')
        ax.set_xlim(-7, 7)
        ax.set_ylim(-7, 7)

        plt.pause(0.1)
except KeyboardInterrupt:
    plt.close()
```

### 자주 발생하는 오류와 원인

| 오류 | 원인 | 해결 |
|------|------|------|
| 그래프가 안 뜨거나 바로 닫힘 | `plt.show()` 누락 | `plt.show()` 추가 |
| 저장된 파일이 빈 그래프 | `plt.show()` 후에 `plt.savefig()` 호출 | `savefig()` 먼저, `show()` 나중 |
| LiDAR 산점도가 찌그러짐 | `set_aspect('equal')` 누락 | `ax.set_aspect('equal')` 추가 |
| 실시간 루프에서 메모리 누수 | 루프 안에서 매번 `plt.figure()` 생성 | Figure는 루프 밖에서 한 번만 생성 |
| `TypeError: Can't instantiate abstract class` | `get_data()` 미구현 | 자식 클래스에서 메서드 이름 확인 후 구현 |

---

## 10. Matplotlib 입문자가 자주 하는 실수

### ① plt.show() 누락 또는 순서 오류

```python
# 나쁜 예 — 저장 후 show()로 초기화되면 빈 파일이 저장됨
ax.plot(x, y)
plt.show()                # 이 시점에 Figure가 초기화됨
plt.savefig("out.png")    # 빈 그래프 저장!

# 좋은 예 — savefig()는 항상 show() 전에
ax.plot(x, y)
plt.tight_layout()
plt.savefig("out.png")    # 먼저 저장
plt.show()                # 그 다음 표시
```

### ② 실시간 루프 안에서 Figure 생성

```python
# 나쁜 예 — 매 루프마다 새 Figure → 메모리 부족으로 시스템 중단
while True:
    plt.figure()       # 매번 새로 만들면 안 됨
    plt.scatter(x, y)
    plt.show()

# 좋은 예 — Figure는 루프 밖에서 한 번만
fig, ax = plt.subplots()
while True:
    ax.clear()
    ax.scatter(x, y)
    plt.pause(0.1)
```

### ③ 축 범위 미설정 — 실시간 플롯에서 특히 주의

```python
# 나쁜 예 — 매 프레임 축이 자동으로 바뀌어 상대적 변화 파악 불가
while True:
    ax.clear()
    ax.scatter(x, y)    # xlim, ylim이 매 프레임 자동 조정됨
    plt.pause(0.1)

# 좋은 예 — 범위를 고정하여 일관된 시야 확보
while True:
    ax.clear()
    ax.scatter(x, y)
    ax.set_xlim(-6, 6)
    ax.set_ylim(-6, 6)
    plt.pause(0.1)
```

### ④ LiDAR 산점도에서 set_aspect 누락

```python
# 나쁜 예 — 가로세로 비율이 달라 원이 타원으로 찌그러짐
ax.scatter(x, y, s=5)

# 좋은 예
ax.scatter(x, y, s=5)
ax.set_aspect('equal')   # 반드시 추가
```

### ⑤ plt.ion() 없이 while 루프에 plt.show() 사용

```python
# 나쁜 예 — plt.show()가 블로킹되어 루프가 멈춤
while True:
    ax.clear()
    ax.scatter(x, y)
    plt.show()   # 창을 닫기 전까지 여기서 멈춤!

# 좋은 예 — plt.ion() + plt.pause()
plt.ion()
while True:
    ax.clear()
    ax.scatter(x, y)
    plt.pause(0.1)   # 비블로킹 갱신
```

### ⑥ NumPy 미사용 — 대용량 데이터를 Python 리스트로 플롯

```python
# 나쁜 예 — 리스트로 플롯하면 대용량에서 매우 느림
x_list = [i * 0.01 for i in range(10000)]
y_list = [math.sin(v) for v in x_list]
ax.plot(x_list, y_list)

# 좋은 예 — NumPy 배열로 빠르게 처리 후 플롯
x_arr = np.linspace(0, 100, 10000)
y_arr = np.sin(x_arr)
ax.plot(x_arr, y_arr)
```

---

## 실습 체크리스트

복습 시 다음 항목들을 제대로 수행했는지 점검하세요.

- [ ] `fig, ax = plt.subplots()`로 객체지향 방식을 사용했는가?
- [ ] `plt.savefig()`를 `plt.show()` **전에** 호출했는가?
- [ ] LiDAR 산점도에 `ax.set_aspect('equal')`을 추가했는가?
- [ ] 실시간 루프에서 Figure를 루프 밖에서 한 번만 생성했는가?
- [ ] 실시간 플롯에 `ax.set_xlim()`, `ax.set_ylim()`으로 고정 범위를 설정했는가?
- [ ] 그래프에 제목(`set_title`)과 축 이름(`set_xlabel`, `set_ylabel`)을 작성했는가?
- [ ] 여러 선을 그릴 때 `label=`과 `ax.legend()`로 범례를 표시했는가?

---

*이 문서는 02.02 NumPy 배열 연산 & Matplotlib, 02.03 센서 데이터 시뮬레이션 실습 내용을 기반으로 작성되었습니다.*
