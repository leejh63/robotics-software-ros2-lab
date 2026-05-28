# NumPy · Matplotlib · 센서 데이터 시뮬레이션

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

1. [NumPy가 왜 필요한가](#1-numpy가-왜-필요한가)
2. [ndarray 구조 — Dimension, Shape, Dtype](#2-ndarray-구조--dimension-shape-dtype)
3. [배열 생성](#3-배열-생성)
4. [인덱싱과 슬라이싱](#4-인덱싱과-슬라이싱)
5. [브로드캐스팅](#5-브로드캐스팅)
6. [수학 연산](#6-수학-연산)
7. [배열 변형과 결합](#7-배열-변형과-결합)
8. [NumPy 입문자가 자주 하는 실수](#8-numpy-입문자가-자주-하는-실수)
9. [Matplotlib 기초 — 구조 이해](#9-matplotlib-기초--구조-이해)
10. [차트 유형별 사용법](#10-차트-유형별-사용법)
11. [Matplotlib 입문자가 자주 하는 실수](#11-matplotlib-입문자가-자주-하는-실수)
12. [센서 데이터 시뮬레이션 — OOP + NumPy + Matplotlib](#12-센서-데이터-시뮬레이션--oop--numpy--matplotlib)
13. [불리언 배열 연산](#13-불리언-배열-연산)
14. [정렬과 탐색](#14-정렬과-탐색)
15. [NaN 처리](#15-nan-처리)
16. [값 변환 함수](#16-값-변환-함수)
17. [배열 반복과 패딩](#17-배열-반복과-패딩)
18. [meshgrid — 2D 격자 생성](#18-meshgrid--2d-격자-생성)
19. [신호 처리 기초](#19-신호-처리-기초)
20. [통계 심화](#20-통계-심화)
21. [선형대수 심화](#21-선형대수-심화)
22. [벡터화 함수](#22-벡터화-함수)
23. [구조화 배열](#23-구조화-배열)

---

## 1. NumPy가 왜 필요한가

### Python 리스트의 한계

Python 리스트는 어떤 타입의 값이든 담을 수 있어서 유연하지만, 그 유연함이 수치 연산에서는 **치명적인 느림**으로 돌아옵니다.

리스트의 각 원소는 독립적인 Python 객체입니다. 덧셈 하나에도 타입 확인, 메모리 추적, 참조 카운트 관리 같은 오버헤드가 붙습니다. 원소가 수천 개만 넘어도 이 오버헤드가 쌓여서 느려집니다.

```python
# 360개 거리 데이터에 보정치를 더하는 경우

# 리스트 방식 — 원소 하나씩 순차 계산
distances = [2.5, 3.1, 1.8, ...]   # 360개
corrected = []
for d in distances:
    corrected.append(d + 0.1)       # Python 루프는 느리다
```

### NumPy의 해결책 — 벡터화(Vectorization)

NumPy는 **모든 원소가 같은 타입인 연속 메모리 배열**(`ndarray`)을 씁니다.  
C로 구현된 최적화 루프를 내부에서 돌리기 때문에, 같은 연산이 수십~수백 배 빠릅니다.

```python
import numpy as np

# NumPy 방식 — 배열 전체에 한 번에 적용
distances = np.array([2.5, 3.1, 1.8, ...])   # ndarray
corrected = distances + 0.1                   # 루프 없음, C 수준 속도
```

### 로봇과 실시간 연산

로봇은 Sense-Think-Act 루프를 수백 ms 단위로 반복합니다.  
LiDAR 360개 포인트, IMU 3축 가속도, 카메라 이미지 픽셀 등 **대량 숫자 데이터를 매우 짧은 시간 안에 처리**해야 합니다.  
Python 리스트로는 이 속도를 맞추기 어렵습니다. NumPy가 사실상 로봇 소프트웨어의 기본 도구인 이유입니다.

---

## 2. ndarray 구조 — Dimension, Shape, Dtype

NumPy 코드를 읽을 때 **항상 이 세 가지를 머릿속에 추적**하세요.  
shape 오류의 99%는 이 세 개념을 혼동해서 생깁니다.

### Dimension (차원)

데이터가 뻗어 나가는 방향의 수입니다.

| 차원 | 이름 | 예시 |
|------|------|------|
| 1D | 벡터 | 시간에 따른 IMU 가속도 값 `[x, y, z]` |
| 2D | 행렬 | LiDAR 스캔 데이터 세트, 로봇 격자 지도 |
| 3D+ | 텐서 | 카메라 이미지 (높이 × 너비 × 채널) |

### Shape (형태)

각 차원의 크기를 **튜플**로 표현합니다.

```python
import numpy as np

accel = np.array([0.02, -0.01, 9.81])   # shape: (3,)
                                          # 1D, 원소 3개

lidar_map = np.zeros((360, 2))           # shape: (360, 2)
                                          # 2D, 360행 × 2열
```

`(3,)` 처럼 쉼표가 있는 이유는 Python 튜플이기 때문입니다. `(3)`은 숫자 3과 같지만 `(3,)`은 원소 1개짜리 튜플입니다.

### Dtype (데이터 타입)

배열의 모든 원소는 **같은 타입**이어야 합니다. 이게 리스트와 가장 큰 차이입니다.

```python
np.array([1.0, 2.0, 3.0]).dtype     # float64 (기본)
np.array([1, 2, 3]).dtype            # int64
np.array([True, False]).dtype        # bool
```

로봇 데이터에서 dtype은 중요합니다.

| 데이터 종류 | 권장 dtype |
|-------------|------------|
| 좌표, 속도, 전압 | `float64` |
| 엔코더 틱, 센서 코드 | `int32` / `int64` |
| 활성화 여부 플래그 | `bool` |

정수형 배열에 실수값을 넣으면 소수점이 잘려 데이터가 왜곡됩니다. 센서 데이터는 **되도록 float64**를 씁니다.

### 세 속성을 수시로 확인하는 습관

```python
a = np.zeros((360, 2))

print(a.ndim)    # 2
print(a.shape)   # (360, 2)
print(a.dtype)   # float64
print(a.size)    # 720  (전체 원소 수)
```

코드가 예상대로 안 돌아갈 때 제일 먼저 이걸 출력해서 확인하세요.

---

## 3. 배열 생성

### np.array — 직접 생성

```python
import numpy as np

# 1D
a = np.array([1, 2, 3])

# 2D
b = np.array([[1, 2, 3],
              [4, 5, 6]])

# dtype 지정
c = np.array([1, 2, 3], dtype=np.float64)
```

### 초기화 배열

```python
np.zeros(100)           # 0으로 채운 1D 배열 (데이터 버퍼 사전 할당)
np.zeros((3, 4))        # 0으로 채운 3×4 2D 배열
np.ones((2, 3))         # 1로 채운 2×3
np.full((3, 3), 7)      # 7로 채운 3×3
np.eye(4)               # 4×4 단위행렬
```

`np.zeros`가 자주 쓰이는 이유: 로봇 소프트웨어에서 센서 버퍼나 제어 출력 배열을 미리 메모리에 잡아두는 용도로 씁니다.

### 수열 생성

```python
np.arange(0, 10, 2)              # [0, 2, 4, 6, 8]
np.arange(5)                     # [0, 1, 2, 3, 4]

np.linspace(0, 2 * np.pi, 360)  # 0~2π 구간을 360개로 균등 분할
                                  # LiDAR 각도 배열 생성에 필수
```

`arange`는 step 크기로, `linspace`는 개수로 배열을 만듭니다.  
끝값 포함 여부가 다릅니다. `linspace`는 끝값을 포함하고, `arange`는 포함하지 않습니다.

### 난수 생성

```python
np.random.rand(3, 3)                        # 0~1 균등분포
np.random.randn(3, 3)                       # 표준정규분포 (평균 0, 표준편차 1)
np.random.uniform(0.5, 5.0, 360)           # 0.5~5.0 균등분포 360개
np.random.normal(0, 0.05, 360)             # 평균 0, 표준편차 0.05, 가우시안
np.random.randint(0, 10, (3, 3))           # 정수 난수
```

센서 노이즈 시뮬레이션에는 `np.random.normal`을 씁니다.  
실제 센서는 측정값 주변에 가우시안(정규분포) 오차가 붙기 때문입니다.

```python
# LiDAR 시뮬레이션 — 실제 거리 5m에 5cm 수준 노이즈 추가
ideal_distance = 5.0
noise = np.random.normal(0, 0.05, 360)   # 평균 0, 표준편차 5cm
noisy_lidar = ideal_distance + noise
```

---

## 4. 인덱싱과 슬라이싱

### 1D 슬라이싱 — 리스트와 동일

```python
arr = np.array([10, 20, 30, 40, 50])

arr[2]          # 30
arr[-1]         # 50
arr[1:4]        # [20, 30, 40]
arr[::2]        # [10, 30, 50]  (2칸씩 건너뜀)
arr[::-1]       # [50, 40, 30, 20, 10]  (역순)
```

### 2D 인덱싱 — [행, 열]

```python
mat = np.array([[1, 2, 3],
                [4, 5, 6],
                [7, 8, 9]])

mat[1, 2]           # 6         (1행 2열)
mat[0]              # [1, 2, 3] (0번째 행 전체)
mat[:, 1]           # [2, 5, 8] (1번째 열 전체)
mat[0:2, 1:3]       # [[2,3],[5,6]]  (0~1행, 1~2열)
```

슬라이싱에서 `:`의 의미: "이 축의 전체"입니다.  
`mat[:, 1]`은 "모든 행에서 1번째 열만"이고,  
`mat[0, :]`는 "0번째 행에서 모든 열"입니다.

### 불리언 인덱싱 — 조건을 배열로 표현

가장 강력하고 자주 쓰이는 기능입니다.  
조건식이 boolean 배열을 반환하고, 그 배열로 원소를 필터링합니다.

```python
lidar_data = np.array([2.5, 0.5, 1.8, 0.9, 3.0])

# 1m 미만의 장애물만 추출
obstacles = lidar_data[lidar_data < 1.0]
print(obstacles)   # [0.5 0.9]

# 조건 여러 개 — &(AND), |(OR), ~(NOT)
safe = lidar_data[(lidar_data >= 1.0) & (lidar_data < 2.5)]
print(safe)        # [1.8]
```

for 루프로 조건 검사하는 코드를 불리언 인덱싱 한 줄로 바꿀 수 있으면 항상 바꾸세요. 훨씬 빠르고 읽기도 쉽습니다.

### np.where — 조건에 따라 값 선택

```python
arr = np.array([10, 20, 30, 40, 50])

# 조건이 True면 arr 값, False면 0
np.where(arr > 25, arr, 0)     # [ 0,  0, 30, 40, 50]

# 임계값 기반 클리핑
np.where(arr > 35, 35, arr)    # [10, 20, 30, 35, 35]
```

### 팬시 인덱싱 — 인덱스 배열로 선택

```python
arr = np.array([10, 20, 30, 40, 50])

indices = [0, 2, 4]
arr[indices]       # [10, 30, 50]

# 2D에서 특정 행만 뽑기
mat = np.array([[1,2,3],[4,5,6],[7,8,9]])
mat[[0, 2]]        # [[1,2,3],[7,8,9]]  (0번째, 2번째 행)
```

### View vs Copy — 매우 중요

슬라이싱은 복사가 아니라 **같은 메모리를 가리키는 뷰(view)**를 반환합니다.  
뷰를 수정하면 원본도 바뀝니다.

```python
a = np.array([1, 2, 3, 4, 5])
b = a[1:4]      # view — 복사 아님

b[0] = 99
print(a)        # [ 1, 99,  3,  4,  5]  ← 원본이 바뀜!

# 진짜 복사가 필요하면 .copy()
b = a[1:4].copy()
b[0] = 99
print(a)        # [1, 2, 3, 4, 5]  ← 원본 안 바뀜
```

불리언 인덱싱과 팬시 인덱싱은 항상 복사를 반환합니다.

---

## 5. 브로드캐스팅

### 브로드캐스팅이란

shape가 다른 배열끼리 연산할 때 NumPy가 **작은 배열을 자동으로 확장해서 계산**하는 규칙입니다.  
루프 없이 고차원 연산을 한 줄로 쓸 수 있게 해줍니다.

```python
# 스칼라 브로드캐스팅 — 가장 단순한 형태
arr = np.array([1, 2, 3, 4, 5])
arr * 2             # [2, 4, 6, 8, 10]  스칼라가 배열 크기로 확장됨
arr + 10            # [11, 12, 13, 14, 15]
```

```python
# 로봇 팔 3축 가속도 보정 예시
accel_data        = np.array([0.02, -0.01, 9.81])   # shape: (3,)
calibration_offset = np.array([0.01,  0.01, 0.00])  # shape: (3,)

calibrated = accel_data - calibration_offset         # 각 축에 개별 오프셋 적용
print(calibrated)   # [0.01 -0.02  9.81]
```

### 브로드캐스팅 규칙

두 배열의 shape를 **오른쪽부터 정렬**해서 비교합니다.

```
a shape:   (2, 3)
b shape:      (3,)
         ↑
       (1, 3)으로 해석 → (2, 3)으로 확장
```

1. 차원 수가 다르면 앞에 1을 채운다: `(3,)` → `(1, 3)`
2. 크기가 1인 축은 상대 배열의 크기에 맞게 복사된다: `(1, 3)` → `(2, 3)`
3. 크기가 다르고 둘 다 1이 아니면 `ValueError`

```python
a = np.array([[1, 2, 3],   # shape (2, 3)
              [4, 5, 6]])

b = np.array([10, 20, 30]) # shape (3,) → (1,3) → (2,3)으로 확장

a + b
# [[11, 22, 33],
#  [14, 25, 36]]

# 열 방향으로 브로드캐스팅
c = np.array([[100],       # shape (2,1) → (2,3)으로 확장
              [200]])

a + c
# [[101, 102, 103],
#  [204, 205, 206]]
```

### 의도치 않은 브로드캐스팅 주의

```python
a = np.array([1, 2, 3])    # shape (3,)
b = np.array([[1],         # shape (3, 1)
              [2],
              [3]])

a + b   # shape (3,3) — 내적이 아니라 3×3 행렬이 됨!
```

shape를 수시로 출력해서 확인하는 습관이 이런 버그를 막습니다.

---

## 6. 수학 연산

### 기본 통계

```python
lidar_data = np.array([4.2, 3.5, 1.1, 2.8, 0.8])

np.mean(lidar_data)      # 2.48  평균
np.std(lidar_data)       # 1.27  표준편차
np.var(lidar_data)       # 분산
np.min(lidar_data)       # 0.8   최솟값
np.max(lidar_data)       # 4.2   최댓값
np.median(lidar_data)    # 중앙값
np.sum(lidar_data)       # 합계
np.cumsum(lidar_data)    # 누적 합
```

### argmin / argmax — 인덱스(방향) 탐색

센서 데이터에서 최솟값이나 최댓값의 **위치**가 중요할 때 씁니다.

```python
lidar_data = np.array([4.2, 3.5, 1.1, 2.8, 0.8])

min_idx = np.argmin(lidar_data)   # 4  (가장 가까운 장애물의 방향 인덱스)
max_idx = np.argmax(lidar_data)   # 0

print(f"가장 가까운 장애물: {lidar_data[min_idx]:.2f}m, 방향: {min_idx}")
```

LiDAR 처리에서 `argmin`은 "어느 방향에 장애물이 있는가"를 찾는 핵심 함수입니다.

### axis — 어느 방향으로 연산할지

2D 이상의 배열에서 방향을 지정해야 할 때 씁니다.  
`axis=0`은 **행 방향(세로, 열 단위 결과)**, `axis=1`은 **열 방향(가로, 행 단위 결과)**입니다.

```python
mat = np.array([[1, 2, 3],
                [4, 5, 6]])

np.sum(mat)           # 21    전체 합
np.sum(mat, axis=0)   # [5, 7, 9]   각 열의 합 (행을 압축)
np.sum(mat, axis=1)   # [6, 15]     각 행의 합 (열을 압축)

np.mean(mat, axis=0)  # [2.5, 3.5, 4.5]
np.max(mat, axis=1)   # [3, 6]
```

"axis=0은 세로 방향을 압축"이라고 외우면 됩니다.

### 벡터/행렬 연산

```python
# L2 노름 (크기 계산) — IMU 총 가속도
accel = np.array([0.02, -0.01, 9.81])
total = np.linalg.norm(accel)
print(f"총 가속도: {total:.2f} m/s²")   # 9.81 정도

# 행렬 곱
A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])

A @ B               # 행렬 곱 (권장)
np.dot(A, B)        # 동일

np.linalg.det(A)    # 행렬식
np.linalg.inv(A)    # 역행렬
```

### 삼각함수 — 극좌표 변환

LiDAR 데이터를 2D 지도로 변환할 때 씁니다.

```python
# 극좌표 (r, θ) → 직교좌표 (x, y) 변환
angles    = np.linspace(0, 2 * np.pi, 360)   # 각도 배열
distances = np.random.uniform(0.5, 5.0, 360)  # 거리 배열

x = distances * np.cos(angles)
y = distances * np.sin(angles)
# x, y 각각 shape (360,) — 이게 2D 포인트 클라우드
```

---

## 7. 배열 변형과 결합

### reshape

원소 수가 같다면 shape를 자유롭게 바꿉니다.

```python
a = np.arange(12)   # [0, 1, 2, ..., 11]

a.reshape(3, 4)     # (3, 4)
a.reshape(2, 6)     # (2, 6)
a.reshape(-1, 3)    # -1은 자동 계산 → (4, 3)
a.reshape(-1)       # 1D로 펼치기 → (12,)
```

### flatten vs reshape(-1)

```python
mat = np.arange(12).reshape(3, 4)

flat1 = mat.reshape(-1)   # 가능하면 view (원본 공유 가능)
flat2 = mat.flatten()     # 항상 복사본

flat1[0] = 999
print(mat[0, 0])   # 999 ← reshape(-1)이 view면 원본도 바뀜

flat2[0] = 999
print(mat[0, 0])   # 999 ← flatten은 복사본이므로 불변
```

독립 복사본이 필요하면 `flatten()` 또는 `.copy()`를 씁니다.

### 전치

```python
mat = np.array([[1, 2, 3],
                [4, 5, 6]])   # shape (2, 3)

mat.T                          # shape (3, 2)
```

### 배열 합치기

```python
a = np.array([[1, 2], [3, 4]])
b = np.array([[5, 6], [7, 8]])

np.vstack([a, b])              # 세로로 쌓기 → (4, 2)
np.hstack([a, b])              # 가로로 붙이기 → (2, 4)

np.concatenate([a, b], axis=0) # vstack과 같음
np.concatenate([a, b], axis=1) # hstack과 같음
```

### 차원 추가

```python
a = np.array([1, 2, 3])   # shape (3,)

a[np.newaxis, :]           # shape (1, 3) 행벡터
a[:, np.newaxis]           # shape (3, 1) 열벡터

# 브로드캐스팅 방향을 맞출 때 자주 씁니다
```

---

## 8. NumPy 입문자가 자주 하는 실수

### ① 배열 연산에 for 루프 사용

NumPy 배열에 습관적으로 for 루프를 쓰면 성능 장점이 전혀 없습니다.

```python
# 나쁜 예
result = []
for x in arr:
    result.append(x * 2)

# 좋은 예
result = arr * 2
```

for 루프가 필요하다고 느껴지면 불리언 인덱싱, 브로드캐스팅, np.where 중 하나로 대체할 수 있는지 먼저 고민하세요.

### ② Shape 불일치

```python
a = np.array([1, 2, 3])     # shape (3,)
b = np.array([[1], [2], [3]])  # shape (3, 1)

a + b   # (3, 3) 브로드캐스팅 — 의도한 연산이 맞는지 확인 필요
```

연산 결과가 이상하면 `print(a.shape, b.shape)`을 먼저 출력하세요.

### ③ 얕은 복사 실수

```python
a = np.array([1, 2, 3])
b = a                  # 복사가 아님, 같은 객체를 가리킴

b[0] = 99
print(a)               # [99,  2,  3]  ← 원본도 바뀜!

# 독립 복사가 필요하면
b = a.copy()
```

### ④ Dtype 무시

```python
arr = np.array([1, 2, 3])      # dtype int64

arr[0] = 1.7
print(arr)                     # [1, 2, 3]  ← 소수점 잘림!

# 센서 데이터는 float로 만들거나 명시적으로 지정
arr = np.array([1, 2, 3], dtype=np.float64)
arr[0] = 1.7
print(arr)                     # [1.7, 2. , 3. ]
```

---

## 9. Matplotlib 기초 — 구조 이해

### 세 계층 구조

Matplotlib을 처음 쓰면 `plt.plot()` 한 줄로 그리다가, 서브플롯이 생기거나 세밀한 제어가 필요할 때 혼란이 생깁니다. 구조를 알면 혼란이 없어집니다.

```
Figure (캔버스 전체)
  └── Axes (좌표계 — "그래프 하나")
        ├── 제목, 축 레이블, 눈금
        └── Artist (선, 점, 텍스트 등 모든 그림 요소)
```

- **Figure**: 가장 바깥쪽 창 또는 페이지. 하나 이상의 Axes를 포함합니다.
- **Axes**: 실제 데이터가 그려지는 구역. 우리가 보통 "그래프 하나"라고 부르는 단위입니다.
- **Artist**: Figure에 보이는 모든 것. Axes에 데이터를 그리면 자동으로 생성됩니다.

### 기본 그래프

```python
import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(0, 2 * np.pi, 200)

# 객체지향 방식 (권장 — 여러 Axes 다룰 때 명확)
fig, ax = plt.subplots(figsize=(10, 4))

ax.plot(x, np.sin(x), label="sin", color="steelblue", linewidth=2)
ax.plot(x, np.cos(x), label="cos", color="tomato", linestyle="--")

ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_title("삼각함수")
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("trig.png", dpi=150)   # PNG 또는 PDF로 저장
plt.show()                          # 반드시 마지막에 호출
```

### 서브플롯

```python
# 1행 2열 서브플롯
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

ax1.plot(...)
ax2.scatter(...)

plt.tight_layout()   # 서브플롯 간 여백 자동 조정
plt.show()

# 2행 2열
fig, axes = plt.subplots(2, 2, figsize=(12, 8))
axes[0, 0].plot(...)
axes[0, 1].scatter(...)
axes[1, 0].hist(...)
axes[1, 1].boxplot(...)
```

### 자주 쓰는 꾸미기 옵션

```python
ax.set_title("제목")
ax.set_xlabel("x축 레이블")
ax.set_ylabel("y축 레이블")
ax.legend()                    # plot의 label= 값으로 범례 표시
ax.grid(True, alpha=0.3)       # 격자 (alpha로 투명도 조절)
ax.set_xlim(0, 10)             # x축 범위 고정
ax.set_ylim(-2, 2)             # y축 범위 고정
ax.set_aspect('equal')         # 가로세로 비율 1:1
```

---

## 10. 차트 유형별 사용법

### 라인 그래프 — 시계열 데이터

IMU, 엔코더, 배터리 전압 등 시간에 따른 변화를 볼 때 씁니다.

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
ax.grid(True)
ax.legend()
plt.show()
```

### 산점도 — LiDAR 포인트 클라우드

극좌표를 직교좌표로 변환한 뒤 점으로 찍어서 로봇 주변 환경을 시각화합니다.

```python
angles    = np.linspace(0, 2 * np.pi, 360)
distances = 2 + 0.5 * np.random.randn(360)   # 평균 2m, 노이즈 포함

# 극좌표 → 직교좌표
x = distances * np.cos(angles)
y = distances * np.sin(angles)

fig, ax = plt.subplots(figsize=(6, 6))
ax.scatter(x, y, s=5, c='blue', label='LiDAR Scan')
ax.set_title("LiDAR Obstacle Detection")
ax.set_xlabel("X distance (m)")
ax.set_ylabel("Y distance (m)")
ax.grid(True)
ax.legend()
ax.set_aspect('equal')   # LiDAR는 가로세로 비율이 반드시 1:1이어야 함
plt.show()
```

### 히스토그램 — 노이즈 분포 분석

센서 데이터의 노이즈가 어떻게 분포하는지 확인합니다.  
필터 알고리즘 설계 전에 먼저 분포를 보는 게 좋습니다.

```python
noise_data = np.random.normal(0, 0.05, 1000)   # 5cm 노이즈 시뮬레이션

fig, ax = plt.subplots()
ax.hist(noise_data, bins=30, color='mediumseagreen', edgecolor='black', alpha=0.7)
ax.set_title("Sensor Noise Distribution")
ax.set_xlabel("Error (m)")
ax.set_ylabel("Count")
plt.show()
```

### 두 센서 동시 시각화 — subplot 활용

```python
import numpy as np
import matplotlib.pyplot as plt

angles    = np.linspace(0, 2 * np.pi, 360)
distances = 2 + 0.5 * np.random.randn(360)
x = distances * np.cos(angles)
y = distances * np.sin(angles)

time     = np.linspace(0, 10, 100)
imu_accel = np.sin(time) + 0.1 * np.random.randn(100)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

ax1.scatter(x, y, s=5, c='red', label='LiDAR Scan')
ax1.set_title("LiDAR Obstacle Detection")
ax1.set_xlabel("X distance (m)")
ax1.set_ylabel("Y distance (m)")
ax1.grid(True)
ax1.legend()
ax1.set_aspect('equal')

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

### 실시간(동적) 시각화

로봇의 Sense-Think-Act 루프를 코드로 모사합니다.  
`plt.ion()`으로 인터랙티브 모드를 켜고, `plt.pause()`로 화면을 갱신합니다.

```python
import numpy as np
import matplotlib.pyplot as plt

plt.ion()                      # 인터랙티브 모드 — plt.show() 없이 즉시 갱신
fig, ax = plt.subplots()

while True:                    # 실제 로봇에서는 종료 조건 추가
    ax.clear()

    angles    = np.linspace(0, 2 * np.pi, 360)
    distances = 2 + 0.5 * np.random.randn(360)
    x = distances * np.cos(angles)
    y = distances * np.sin(angles)

    ax.scatter(x, y, s=5, c='blue')
    ax.set_title("LiDAR Real-time Scan")
    ax.set_aspect('equal')
    ax.set_xlim(-6, 6)
    ax.set_ylim(-6, 6)         # 축 범위 고정 — 안 하면 매 프레임 축이 바뀜

    plt.pause(0.1)             # 0.1초 대기 + 화면 갱신
```

---

## 11. Matplotlib 입문자가 자주 하는 실수

### ① plt.show() 누락

```python
ax.plot(x, y)
# plt.show() 없으면 Jupyter 이외 환경에서 그래프가 안 뜸
plt.show()   # 반드시 마지막에 호출
```

### ② 실시간 루프 안에서 Figure 생성

```python
# 나쁜 예 — 매 루프마다 새 Figure 생성 → 메모리 누수
while True:
    plt.figure()         # 매번 새로 만들면 안 됨
    plt.plot(data)
    plt.show()

# 좋은 예 — Figure는 루프 밖에서 한 번만
fig, ax = plt.subplots()
while True:
    ax.clear()
    ax.plot(data)
    plt.pause(0.1)
```

### ③ 축 범위 미설정

실시간 플롯에서 데이터가 바뀔 때마다 축이 자동으로 맞춰지면 상대적 변화를 관찰하기 어렵습니다.

```python
ax.set_xlim(0, 10)
ax.set_ylim(-3, 3)    # 고정 범위로 전체 흐름 파악
```

### ④ LiDAR 산점도에서 set_aspect 누락

```python
ax.scatter(x, y, s=5)
ax.set_aspect('equal')   # 이게 없으면 원이 타원으로 찌그러짐
```

---

## 12. 센서 데이터 시뮬레이션 — OOP + NumPy + Matplotlib

OOP로 설계한 센서 클래스에 NumPy 연산과 Matplotlib 시각화를 붙인 통합 예제입니다.  
실제 로봇 소프트웨어의 구조와 거의 같습니다.

### 전체 구조

```
추상 클래스 Sensor
    ├── LidarSensor  → get_data() → (angles, distances) NumPy 배열
    └── ImuSensor    → get_data() → (time, accel_data)  NumPy 배열

main()
    → 센서 리스트에서 다형성으로 데이터 수집
    → Matplotlib으로 시각화
```

### Step 1 — 추상 클래스 정의

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

# Sensor("test")  → TypeError: Can't instantiate abstract class
# — abstractmethod를 구현하지 않은 채 인스턴스 생성 시 즉시 오류 발생
```

`@abstractmethod`를 쓰는 이유:  
자식 클래스에서 `get_data()`를 구현하지 않고 인스턴스를 만들면 **즉시 TypeError**가 납니다.  
런타임에 "없는 메서드를 호출했을 때" 오류가 나는 것보다 훨씬 빨리 버그를 잡을 수 있습니다.

### Step 2 — LiDAR 센서 클래스

```python
class LidarSensor(Sensor):
    def __init__(self, name, num_samples=360):
        super().__init__(name)
        self.num_samples = num_samples

    def get_data(self):
        # 0~360도 각도 생성
        angles = np.linspace(0, 2 * np.pi, self.num_samples)

        # 기본 거리 5m에 가우시안 노이즈(표준편차 0.1m) 추가
        distances = 5.0 + np.random.normal(0, 0.1, self.num_samples)

        return angles, distances
```

`np.random.normal(0, 0.1, ...)` — 평균 0, 표준편차 0.1의 가우시안 노이즈.  
실제 LiDAR 센서는 측정값 주변에 이런 오차가 붙습니다.

### Step 3 — IMU 센서 클래스

```python
class ImuSensor(Sensor):
    def __init__(self, name, duration=100):
        super().__init__(name)
        self.duration = duration

    def get_data(self):
        t = np.arange(self.duration)                          # 시간 인덱스 0~99

        # shape (duration, 3) — 행: 시간, 열: x/y/z 축
        accel_data = np.random.randn(self.duration, 3) * 0.5

        return t, accel_data
```

`np.random.randn(duration, 3)` → shape `(100, 3)` 2D 배열.  
`accel_data[:, 0]`은 X축 전체, `accel_data[:, 1]`은 Y축 전체입니다.

### Step 4 — 다형성으로 통합 처리

```python
def main():
    lidar = LidarSensor("Hokuyo_LiDAR")
    imu   = ImuSensor("InvenSense_IMU")

    sensors = [lidar, imu]   # 다른 타입이지만 같은 인터페이스를 가짐

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    for sensor in sensors:
        data = sensor.get_data()   # 타입에 관계없이 동일하게 호출 — 다형성 핵심

        if isinstance(sensor, LidarSensor):
            angles, dists = data
            x = dists * np.cos(angles)
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
    plt.show()

if __name__ == "__main__":
    main()
```

`for sensor in sensors:` 루프가 로봇의 **Sense 루틴**입니다.  
실제 로봇은 이 루틴을 수백 ms 단위로 반복해서 환경을 인식합니다.

### 심화 — 이동 평균 필터

IMU 데이터의 노이즈를 NumPy로 줄이는 간단한 필터입니다.

```python
def moving_average(data, window_size=5):
    kernel = np.ones(window_size) / window_size
    return np.convolve(data, kernel, mode='valid')
    # mode='valid' — 경계 효과 없이 완전히 겹치는 구간만 반환

imu = ImuSensor("IMU")
t, accel = imu.get_data()

filtered = moving_average(accel[:, 0], window_size=10)

plt.figure()
plt.plot(t, accel[:, 0], label='Raw', alpha=0.5, color='gray')
plt.plot(t[:len(filtered)], filtered, label='Filtered', color='steelblue')
plt.legend()
plt.title("IMU X-axis: Raw vs Filtered")
plt.xlabel("Time step")
plt.ylabel("Acceleration")
plt.grid(True)
plt.show()
```

`mode='valid'`를 쓰면 출력 길이가 `len(data) - window_size + 1`이라서 원래 시간 배열보다 짧아집니다.  
그래서 `t[:len(filtered)]`로 맞춰줘야 합니다.

### 심화 — JSON으로 데이터 저장

수집한 센서 데이터를 파일로 저장하고 나중에 다시 불러올 수 있습니다.

```python
import json

imu = ImuSensor("InvenSense_IMU")
t, accel = imu.get_data()

log = {
    "sensor": imu.name,
    "time": t.tolist(),          # ndarray는 JSON 직렬화 불가 → list로 변환
    "accel": accel.tolist()
}

with open("sensor_log.json", "w") as f:
    json.dump(log, f, indent=2)

# 불러오기
with open("sensor_log.json", "r") as f:
    loaded = json.load(f)

print(loaded["sensor"])          # InvenSense_IMU
t_loaded = np.array(loaded["time"])
accel_loaded = np.array(loaded["accel"])
```

`ndarray.tolist()`로 Python 리스트로 변환해야 JSON 저장이 됩니다.  
불러올 때는 `np.array()`로 다시 ndarray로 만들면 됩니다.

### 자주 발생하는 오류와 원인

| 오류 | 원인 | 해결 |
|------|------|------|
| `TypeError: Can't instantiate abstract class` | `get_data()`를 자식 클래스에서 구현 안 함 | 메서드 이름 확인 후 구현 |
| `ValueError: operands could not be broadcast` | 배열 shape 불일치 | `.shape` 출력해서 확인 |
| 그래프가 안 뜨거나 바로 닫힘 | `plt.show()` 누락 또는 IDE 환경 문제 | `plt.show()` 추가, 환경 확인 |
| `NameError: name 'ABC' is not defined` | `from abc import ABC, abstractmethod` 누락 | 임포트 추가 |
| ndarray를 JSON으로 저장 시 오류 | ndarray는 JSON 직렬화 불가 | `.tolist()` 변환 후 저장 |

---

---

## 13. 불리언 배열 연산

### np.any / np.all

배열 전체 또는 특정 축에서 조건을 만족하는지 확인합니다.

```python
import numpy as np

arr = np.array([1, -2, 3, -4, 5])

np.any(arr < 0)         # True  — 하나라도 음수이면 True
np.all(arr > 0)         # False — 모두 양수여야 True
np.all(arr != 0)        # True  — 0이 없으면 True

# 2D에서 axis 지정
mat = np.array([[1, -1, 2],
                [3,  4, 5]])

np.any(mat < 0, axis=0)  # [False, True, False]  각 열에서 음수가 있는지
np.all(mat > 0, axis=1)  # [False, True]          각 행이 모두 양수인지
```

### np.count_nonzero

조건을 만족하는 원소 개수를 셉니다.

```python
lidar = np.array([2.5, 0.5, 1.8, 0.9, 3.0])

np.count_nonzero(lidar < 1.0)    # 2 — 1m 미만 장애물 개수

# 비율 계산
ratio = np.count_nonzero(lidar < 1.0) / len(lidar)
print(f"위험 구역 비율: {ratio:.0%}")   # 40%
```

### 불리언 배열 자체를 숫자로 쓰기

Python에서 `True == 1`, `False == 0`이므로 불리언 배열을 수치 연산에 직접 쓸 수 있습니다.

```python
flags = np.array([True, False, True, True, False])

np.sum(flags)    # 3  — True의 개수
np.mean(flags)   # 0.6 — True의 비율

# 센서 활성화 비율 계산
sensors_active = np.array([True, True, False, True, True, False, True])
print(f"가동률: {np.mean(sensors_active):.0%}")   # 71%
```

### np.logical_and / np.logical_or / np.logical_not

불리언 배열 연산의 함수형 버전입니다. `&`, `|`, `~` 연산자와 결과는 같지만 함수로 전달할 때 유용합니다.

```python
a = np.array([True, True, False, False])
b = np.array([True, False, True, False])

np.logical_and(a, b)    # [True, False, False, False]
np.logical_or(a, b)     # [True, True, True, False]
np.logical_not(a)       # [False, False, True, True]
np.logical_xor(a, b)    # [False, True, True, False]
```

---

## 14. 정렬과 탐색

### 정렬

```python
arr = np.array([3, 1, 4, 1, 5, 9, 2, 6])

np.sort(arr)             # [1, 1, 2, 3, 4, 5, 6, 9]  새 배열 반환
arr.sort()               # 원본을 직접 정렬 (반환값 없음)

np.sort(arr)[::-1]       # 내림차순 (sort 후 역순)

# 2D 정렬
mat = np.array([[3, 1, 2],
                [6, 4, 5]])

np.sort(mat, axis=1)     # 각 행을 정렬 → [[1,2,3],[4,5,6]]
np.sort(mat, axis=0)     # 각 열을 정렬 → [[3,1,2],[6,4,5]]
```

### argsort — 정렬 시 원래 인덱스

값이 아닌 **정렬 순서의 인덱스**를 반환합니다.  
"몇 번째 센서가 가장 가까운가"를 알고 싶을 때 씁니다.

```python
distances = np.array([4.2, 1.1, 3.5, 0.8, 2.9])

order = np.argsort(distances)
print(order)               # [3, 1, 4, 2, 0]  — 가까운 것부터 인덱스

# 가장 가까운 3개의 거리와 방향
print(distances[order[:3]])   # [0.8, 1.1, 2.9]
print(order[:3])              # [3, 1, 4]
```

### np.unique — 중복 제거와 빈도 계산

```python
arr = np.array([3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5])

np.unique(arr)                           # [1, 2, 3, 4, 5, 6, 9]

# 각 값의 첫 번째 인덱스도 반환
values, indices = np.unique(arr, return_index=True)
print(values)    # [1, 2, 3, 4, 5, 6, 9]
print(indices)   # [1, 6, 0, 2, 4, 7, 5]  (처음 등장한 위치)

# 등장 횟수도 반환
values, counts = np.unique(arr, return_counts=True)
for v, c in zip(values, counts):
    print(f"{v}: {c}번")
```

### np.searchsorted — 이진 탐색

정렬된 배열에서 값을 삽입할 위치를 찾습니다.  
임계값 구간 판별에 자주 씁니다.

```python
thresholds = np.array([1.0, 2.0, 3.0, 4.0, 5.0])   # 정렬된 구간 경계

distances = np.array([0.5, 1.5, 2.8, 3.2, 6.0])

levels = np.searchsorted(thresholds, distances)
# 각 거리가 어느 구간에 속하는지 (0=가장 가까운, 5=가장 먼)
print(levels)   # [0, 1, 2, 3, 5]
```

---

## 15. NaN 처리

### NaN이란

`np.nan`은 "Not a Number"입니다. 센서 오류, 누락 데이터, 0/0 같은 정의 불가 연산 결과에 씁니다.

```python
import numpy as np

x = np.array([1.0, 2.0, np.nan, 4.0, np.nan])

np.isnan(x)              # [False, False, True, False, True]
np.isfinite(x)           # [True, True, False, True, False]
~np.isnan(x)             # [True, True, False, True, False]  — 유효한 값만

# NaN이 있으면 일반 연산 결과도 NaN
np.mean(x)               # nan
np.sum(x)                # nan
```

### nan-safe 함수

NaN을 무시하고 계산하는 함수들입니다.

```python
np.nanmean(x)            # 2.333...  (NaN 제외한 평균)
np.nansum(x)             # 7.0
np.nanmin(x)             # 1.0
np.nanmax(x)             # 4.0
np.nanstd(x)             # 표준편차
np.nanmedian(x)          # 중앙값
```

### NaN 제거와 대체

```python
x = np.array([1.0, np.nan, 3.0, np.nan, 5.0])

# NaN 제거
clean = x[~np.isnan(x)]
print(clean)             # [1. 3. 5.]

# NaN을 특정 값으로 대체 (imputation)
filled = np.where(np.isnan(x), 0, x)         # 0으로 대체
print(filled)            # [1. 0. 3. 0. 5.]

filled_mean = np.where(np.isnan(x), np.nanmean(x), x)   # 평균으로 대체
print(filled_mean)       # [1. 3. 3. 3. 5.]
```

### 무한대(inf)

```python
np.isinf(np.array([1.0, np.inf, -np.inf, np.nan]))
# [False, True, True, False]

np.isfinite(np.array([1.0, np.inf, np.nan]))
# [True, False, False]
```

---

## 16. 값 변환 함수

### np.clip — 값 범위 제한

최솟값과 최댓값을 벗어나는 값을 경계값으로 고정합니다.  
제어 출력값을 하드웨어 한계 내로 제한하거나, 센서 이상값을 처리할 때 자주 씁니다.

```python
arr = np.array([-3, -1, 0, 2, 5, 10])

np.clip(arr, 0, 5)        # [0, 0, 0, 2, 5, 5]

# 모터 출력 -100~100 제한
motor_cmd = np.array([-150, -80, 0, 90, 120])
safe_cmd = np.clip(motor_cmd, -100, 100)
print(safe_cmd)           # [-100,  -80,    0,   90,  100]
```

### np.round / np.floor / np.ceil

```python
arr = np.array([1.2, 2.5, 3.7, -1.2, -2.8])

np.round(arr)             # [ 1.,  2.,  4., -1., -3.]  (반올림, 0.5는 짝수 방향)
np.round(arr, decimals=1) # 소수점 1자리
np.floor(arr)             # [ 1.,  2.,  3., -2., -3.]  (내림)
np.ceil(arr)              # [ 2.,  3.,  4., -1., -2.]  (올림)
np.trunc(arr)             # [ 1.,  2.,  3., -1., -2.]  (0 방향 버림)
```

### np.abs / np.sign

```python
arr = np.array([-3, -1, 0, 2, 5])

np.abs(arr)               # [3, 1, 0, 2, 5]
np.sign(arr)              # [-1, -1, 0, 1, 1]  — 부호만 추출
```

### np.diff — 연속 원소 간 차이

시계열 데이터에서 변화량(속도, 가속도)을 계산할 때 씁니다.

```python
position = np.array([0, 1, 3, 6, 10, 15])   # 로봇 위치

velocity = np.diff(position)                  # [1, 2, 3, 4, 5]  1차 차분
accel    = np.diff(position, n=2)             # [1, 1, 1, 1]     2차 차분

# 주의: diff는 길이가 n만큼 줄어듦
# len(position) = 6 → len(velocity) = 5 → len(accel) = 4
```

### np.cumsum / np.cumprod

```python
arr = np.array([1, 2, 3, 4, 5])

np.cumsum(arr)            # [ 1,  3,  6, 10, 15]  누적 합
np.cumprod(arr)           # [ 1,  2,  6, 24, 120] 누적 곱

# 속도 → 위치 변환 (수치 적분 근사)
dt = 0.1
velocity = np.array([1.0, 1.5, 2.0, 1.8, 1.2])
position = np.cumsum(velocity) * dt
```

### 타입 변환

```python
arr = np.array([1.7, 2.3, 3.9])

arr.astype(int)           # [1, 2, 3]  — int로 변환 (소수점 버림)
arr.astype(np.float32)    # float32로 변환 (메모리 절약)
arr.astype(str)           # ['1.7' '2.3' '3.9']
```

---

## 17. 배열 반복과 패딩

### np.tile — 배열을 타일처럼 반복

```python
arr = np.array([1, 2, 3])

np.tile(arr, 3)           # [1, 2, 3, 1, 2, 3, 1, 2, 3]
np.tile(arr, (2, 3))      # [[1,2,3,1,2,3,1,2,3],
                           #  [1,2,3,1,2,3,1,2,3]]

# 보정 오프셋을 여러 타임스텝에 적용
offset = np.array([0.01, 0.01, 0.00])   # IMU 보정값
offsets_100 = np.tile(offset, (100, 1)) # (100, 3) — 100 타임스텝 모두
```

### np.repeat — 각 원소를 개별 반복

```python
arr = np.array([1, 2, 3])

np.repeat(arr, 3)          # [1, 1, 1, 2, 2, 2, 3, 3, 3]
np.repeat(arr, [1, 2, 3])  # [1, 2, 2, 3, 3, 3]  — 각 원소 다른 횟수

mat = np.array([[1, 2], [3, 4]])
np.repeat(mat, 2, axis=0)  # 각 행을 2번 반복
```

### np.pad — 배열 주변에 패딩

이미지 처리, 합성곱 연산 전처리 등에 씁니다.

```python
arr = np.array([1, 2, 3, 4, 5])

np.pad(arr, 2)                        # [0, 0, 1, 2, 3, 4, 5, 0, 0]  (0으로 패딩)
np.pad(arr, 2, constant_values=99)    # [99, 99, 1, 2, 3, 4, 5, 99, 99]
np.pad(arr, 2, mode='edge')           # [ 1,  1, 1, 2, 3, 4, 5,  5,  5]  (경계값 반복)
np.pad(arr, 2, mode='reflect')        # [ 3,  2, 1, 2, 3, 4, 5,  4,  3]  (반사)

# 2D 패딩 — (위, 아래), (왼쪽, 오른쪽)
mat = np.ones((3, 3))
np.pad(mat, ((1, 1), (2, 2)))   # 위아래 1줄, 좌우 2줄 패딩
```

---

## 18. meshgrid — 2D 격자 생성

### meshgrid란

두 1D 배열을 받아서 2D 격자(grid)의 좌표 배열을 만듭니다.  
2D 함수를 시각화하거나, 로봇 격자 지도에서 모든 좌표를 한번에 처리할 때 씁니다.

```python
import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(-3, 3, 100)
y = np.linspace(-3, 3, 100)

X, Y = np.meshgrid(x, y)
# X: 각 행이 같은 x 좌표, shape (100, 100)
# Y: 각 열이 같은 y 좌표, shape (100, 100)

# 2D 함수 계산 — for 루프 없이
Z = np.sin(np.sqrt(X**2 + Y**2))   # shape (100, 100)

fig, ax = plt.subplots()
ax.contourf(X, Y, Z, levels=20, cmap='RdBu')
ax.set_title("2D sin 함수")
plt.colorbar(ax.contourf(X, Y, Z, levels=20, cmap='RdBu'))
plt.show()
```

### 로봇 격자 지도에 적용

```python
# 5×5m 공간을 0.1m 해상도로 격자화
x_grid = np.arange(-2.5, 2.5, 0.1)   # (50,)
y_grid = np.arange(-2.5, 2.5, 0.1)   # (50,)

X, Y = np.meshgrid(x_grid, y_grid)    # X, Y 각각 (50, 50)

# 원점으로부터 거리 계산 — 모든 격자점을 한번에
dist_from_origin = np.sqrt(X**2 + Y**2)   # (50, 50)

# 1m 이내 영역 마스크
near_origin = dist_from_origin < 1.0      # (50, 50) bool 배열
```

---

## 19. 신호 처리 기초

### np.convolve — 1D 합성곱

신호 필터링에 씁니다. 이동 평균 필터가 대표적입니다.

```python
import numpy as np

signal = np.array([1, 2, 3, 4, 5, 4, 3, 2, 1], dtype=float)
kernel = np.array([1/3, 1/3, 1/3])   # 3점 이동 평균 커널

# mode 옵션
np.convolve(signal, kernel, mode='full')   # 길이 len(signal)+len(kernel)-1, 경계 포함
np.convolve(signal, kernel, mode='same')   # 길이 len(signal), 가운데 정렬
np.convolve(signal, kernel, mode='valid')  # 경계 효과 없는 부분만, 길이 len(signal)-len(kernel)+1
```

mode 선택 기준:
- `'valid'`: 경계 효과가 없어야 하는 필터링 (일반적 권장)
- `'same'`: 원래 길이를 유지해야 할 때
- `'full'`: 전체 합성곱 결과가 필요할 때

### 이동 평균 필터 비교

```python
def moving_avg(data, n):
    return np.convolve(data, np.ones(n)/n, mode='valid')

noisy = np.random.randn(100) + np.sin(np.linspace(0, 4*np.pi, 100))

avg_5  = moving_avg(noisy, 5)
avg_10 = moving_avg(noisy, 10)
avg_20 = moving_avg(noisy, 20)
# window가 클수록 더 부드럽지만 길이가 더 많이 줄어듦
```

### np.correlate — 상호 상관

두 신호의 유사도를 시간 지연별로 측정합니다.  
신호 동기화, 패턴 탐지에 씁니다.

```python
a = np.array([0, 0, 1, 1, 0, 0])
b = np.array([1, 1, 0, 0])

np.correlate(a, b, mode='full')
# 두 신호가 가장 잘 겹치는 시간 오프셋을 찾음
```

### np.fft — 고속 푸리에 변환

신호의 주파수 성분을 분석합니다.  
진동 센서나 오디오 처리에 씁니다.

```python
import numpy as np

# 신호 생성 — 10Hz와 25Hz 사인파 합성
fs = 1000           # 샘플링 주파수 (Hz)
t = np.arange(0, 1, 1/fs)
signal = np.sin(2 * np.pi * 10 * t) + 0.5 * np.sin(2 * np.pi * 25 * t)

# FFT
fft_result = np.fft.fft(signal)
frequencies = np.fft.fftfreq(len(signal), d=1/fs)

# 진폭 스펙트럼 (양의 주파수만)
amplitude = np.abs(fft_result[:len(signal)//2]) * 2 / len(signal)
freq_positive = frequencies[:len(signal)//2]

# 피크 주파수 찾기
peak_freqs = freq_positive[np.argsort(amplitude)[-3:]]
print(f"주요 주파수: {peak_freqs}")   # 10Hz, 25Hz 부근
```

---

## 20. 통계 심화

### 백분위수와 분위수

```python
import numpy as np

data = np.random.normal(50, 10, 1000)

np.percentile(data, 25)          # 1사분위수 (Q1)
np.percentile(data, 50)          # 중앙값 (Q2)
np.percentile(data, 75)          # 3사분위수 (Q3)
np.percentile(data, [25, 50, 75])# 한 번에 여러 개

# IQR 이상값 탐지
q1 = np.percentile(data, 25)
q3 = np.percentile(data, 75)
iqr = q3 - q1
lower = q1 - 1.5 * iqr
upper = q3 + 1.5 * iqr

outliers = data[(data < lower) | (data > upper)]
print(f"이상값 수: {len(outliers)}")
```

### np.histogram — 분포 계산

`plt.hist()`는 그리기용이고, `np.histogram()`은 계산만 합니다.  
히스토그램 데이터를 직접 처리해야 할 때 씁니다.

```python
data = np.random.normal(0, 1, 10000)

counts, bin_edges = np.histogram(data, bins=20)
# counts: 각 구간의 빈도수
# bin_edges: 구간 경계값 (len = bins + 1)

# 정규화 (밀도 추정)
counts_density, _ = np.histogram(data, bins=20, density=True)
bin_width = bin_edges[1] - bin_edges[0]
print(np.sum(counts_density * bin_width))   # 약 1.0 — 전체 면적이 1
```

### 가중 평균과 가중 표준편차

```python
values  = np.array([10.0, 20.0, 30.0])
weights = np.array([1.0,  2.0,  3.0])   # 더 신뢰할 수 있는 측정에 높은 가중치

weighted_mean = np.average(values, weights=weights)
# (10*1 + 20*2 + 30*3) / (1+2+3) = 23.33

# 가중 표준편차
variance = np.average((values - weighted_mean)**2, weights=weights)
weighted_std = np.sqrt(variance)
```

### 2D 통계 — 공분산과 상관계수

```python
# 두 센서의 측정값 관계 분석
sensor_a = np.random.randn(100)
sensor_b = 0.8 * sensor_a + 0.2 * np.random.randn(100)  # a와 상관관계 있음

# 공분산 행렬
cov = np.cov(sensor_a, sensor_b)
print(cov)
# [[var_a,  cov],
#  [cov,   var_b]]

# 상관계수 행렬 (공분산을 표준편차로 정규화)
corr = np.corrcoef(sensor_a, sensor_b)
print(corr[0, 1])   # 약 0.8 — 강한 양의 상관관계
```

---

## 21. 선형대수 심화

### 연립방정식 풀기

로봇 캘리브레이션, 센서 퓨전 등에 씁니다.

```python
import numpy as np

# Ax = b 형태의 연립방정식
# 2x + y = 5
# x + 3y = 10

A = np.array([[2, 1],
              [1, 3]], dtype=float)
b = np.array([5, 10], dtype=float)

x = np.linalg.solve(A, b)
print(x)   # [1. 3.]

# 검증
print(np.allclose(A @ x, b))   # True
```

### 최소제곱법 — 과결정 시스템

측정값이 방정식보다 많을 때(센서 퓨전, 회귀 분석) 씁니다.

```python
# y = ax + b 직선 피팅
x = np.array([0, 1, 2, 3, 4], dtype=float)
y = np.array([1.1, 2.9, 5.1, 7.0, 9.1])   # 노이즈 포함

# 설계 행렬 만들기
A = np.column_stack([x, np.ones_like(x)])  # (5, 2)

# 최소제곱 해
coeffs, residuals, rank, sv = np.linalg.lstsq(A, y, rcond=None)
a, b = coeffs
print(f"y = {a:.2f}x + {b:.2f}")   # y = 2.00x + 1.06

# np.polyfit으로도 가능
coeffs_poly = np.polyfit(x, y, deg=1)   # [a, b]
print(np.polyval(coeffs_poly, 5))       # x=5일 때 예측값
```

### 고유값 분해 (Eigendecomposition)

PCA(주성분 분석), 안정성 분석 등에 씁니다.

```python
A = np.array([[4, 2],
              [1, 3]], dtype=float)

eigenvalues, eigenvectors = np.linalg.eig(A)
print("고유값:", eigenvalues)      # [5. 2.]
print("고유벡터:\n", eigenvectors) # 열 벡터가 고유벡터

# 검증: Av = λv
v = eigenvectors[:, 0]   # 첫 번째 고유벡터
lam = eigenvalues[0]
print(np.allclose(A @ v, lam * v))   # True
```

### 특이값 분해 (SVD)

데이터 압축, 노이즈 제거, 의사역행렬 계산에 씁니다.

```python
M = np.array([[1, 2, 3],
              [4, 5, 6],
              [7, 8, 9]], dtype=float)

U, S, Vt = np.linalg.svd(M)
# U: (3,3), S: (3,) 특이값, Vt: (3,3)

# 랭크-1 근사 (특이값 1개만 사용)
M_approx = S[0] * np.outer(U[:, 0], Vt[0, :])

# 의사역행렬 (역행렬이 없는 행렬에 사용)
M_pinv = np.linalg.pinv(M)
```

### 조건수 — 행렬의 수치 안정성

조건수가 크면 역행렬 계산 시 수치 오차가 커집니다.

```python
A_good = np.array([[2, 1], [1, 3]], dtype=float)
A_bad  = np.array([[1, 1], [1, 1.0001]])    # 거의 특이 행렬

print(np.linalg.cond(A_good))   # 작은 값 → 안정적
print(np.linalg.cond(A_bad))    # 매우 큰 값 → 불안정, 역행렬 신뢰 불가
```

---

## 22. 벡터화 함수

### np.vectorize — Python 함수를 배열에 적용

복잡한 조건 분기가 있는 Python 함수를 배열 연산처럼 쓸 수 있게 합니다.  
단, 내부적으로는 for 루프와 비슷해서 **진짜 NumPy 벡터화보다 느립니다.**  
브로드캐스팅으로 표현하기 어려운 복잡한 함수에만 씁니다.

```python
import numpy as np

def classify_distance(d):
    if d < 0.5:
        return "danger"
    elif d < 2.0:
        return "caution"
    else:
        return "safe"

vfunc = np.vectorize(classify_distance)

distances = np.array([0.3, 1.5, 0.8, 3.0, 0.4])
labels = vfunc(distances)
print(labels)   # ['danger' 'caution' 'caution' 'safe' 'danger']
```

같은 결과를 `np.select`로 훨씬 빠르게 구현할 수 있습니다.

```python
conditions = [distances < 0.5, distances < 2.0]
choices    = ["danger", "caution"]
labels = np.select(conditions, choices, default="safe")
```

### np.apply_along_axis — 축 방향으로 함수 적용

각 행이나 열에 함수를 적용합니다.

```python
data = np.array([[1, 2, 3, 4, 5],
                 [6, 7, 8, 9, 10],
                 [11, 12, 13, 14, 15]])

# 각 행에서 중앙값 계산
row_medians = np.apply_along_axis(np.median, axis=1, arr=data)
print(row_medians)   # [3. 8. 13.]

# 각 열의 피크-투-피크(max-min)
col_pp = np.apply_along_axis(np.ptp, axis=0, arr=data)
print(col_pp)        # [10. 10. 10. 10. 10.]
```

### np.frompyfunc — ufunc 직접 만들기

결과 dtype을 세밀하게 제어해야 할 때 씁니다.

```python
add_with_offset = np.frompyfunc(lambda x, y: x + y + 0.5, 2, 1)
result = add_with_offset(np.array([1, 2, 3]), np.array([4, 5, 6]))
print(result)   # [5.5 7.5 9.5]  (dtype=object, astype으로 변환 필요)
```

---

## 23. 구조화 배열

### 구조화 배열이란

서로 다른 타입의 필드를 하나의 배열로 묶습니다.  
C의 struct, 데이터베이스 레코드와 유사합니다.  
센서 로그처럼 timestamp + 여러 측정값을 하나로 관리할 때 씁니다.

```python
import numpy as np

# dtype 정의
sensor_dtype = np.dtype([
    ('timestamp', np.float64),   # 초 단위 시간
    ('x',         np.float32),   # x축 가속도
    ('y',         np.float32),   # y축 가속도
    ('z',         np.float32),   # z축 가속도
    ('valid',     np.bool_)      # 유효 여부
])

# 배열 생성
log = np.zeros(5, dtype=sensor_dtype)

# 데이터 삽입
log['timestamp'] = np.arange(5) * 0.1
log['x']         = np.random.randn(5) * 0.1
log['y']         = np.random.randn(5) * 0.1
log['z']         = 9.81 + np.random.randn(5) * 0.05
log['valid']     = True

# 필드별 접근
print(log['timestamp'])   # 각 레코드의 timestamp만
print(log[2])             # 3번째 레코드 전체

# 조건 필터링
valid_log = log[log['valid']]
high_z    = log[log['z'] > 9.85]
```

### 구조화 배열과 일반 2D 배열 비교

| | 구조화 배열 | 2D float 배열 |
|---|---|---|
| 필드 이름으로 접근 | ✓ `log['z']` | ✗ `arr[:, 2]` |
| 혼합 타입 | ✓ | ✗ |
| 수치 연산 속도 | 느림 | 빠름 |
| 가독성 | 높음 | 낮음 |

실전에서는 pandas DataFrame이 구조화 배열의 역할을 대신하는 경우가 많습니다.  
NumPy만 쓰는 환경(임베디드, 실시간 제어)이나 pandas가 과한 간단한 로그 처리에 구조화 배열을 씁니다.

---

*이 문서는 02.02 NumPy 배열 연산 & Matplotlib, 02.03 센서 데이터 시뮬레이션 실습 내용을 기반으로 작성되었습니다.*
