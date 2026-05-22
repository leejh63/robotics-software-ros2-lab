# 01. Python 환경 / NumPy / Matplotlib

## 1. 이 문서에서 다루는 것

이 문서는 Day 01에서 다룬 Python 기본기, NumPy 배열 처리, Matplotlib 시각화를 ROS2 학습의 기반 관점에서 다시 정리한다.

Day 01의 목적은 Python 문법 전체를 외우는 것이 아니다. 핵심은 아래다.

```text
코드를 실행할 환경을 만든다.
함수와 모듈을 나누어 실행한다.
숫자 데이터를 배열로 처리한다.
계산 결과를 그래프로 확인한다.
뒤에서 ROS2 Python node를 읽을 수 있는 기본기를 만든다.
```

---

## 2. 관련 원본 파일

```text
day_1/hello.py
day_1/test_1.py
day_1/01_03_Python_Practice.ipynb
day_1/02_01_Python-Class.ipynb
day_1/02_02_Python-NumPy.ipynb
day_1/02_03_Python-Data-Simulation.ipynb
day_1/python.md
day_1/numpy.md
day_1/matplotlib.md
```

`hello.py`는 NumPy 설치 확인과 다른 파일의 함수 호출을 보여준다.

```python
import numpy as np
import test_1 as c

print(np.__version__)
c.calculator_with_history()
```

이 작은 예제는 뒤에서 ROS2 package 안의 module/executable을 이해하는 데도 연결된다. Python 파일 하나가 독립 실행될 수도 있고, 다른 파일에서 import되어 사용될 수도 있다.

---

## 3. Python 실행 환경

실습 코드는 환경이 맞지 않으면 같은 코드여도 동작하지 않는다. 그래서 Python 학습의 첫 단계는 “내가 어떤 Python으로 실행하고 있는지” 확인하는 것이다.

```bash
python --version
which python
python -m pip --version
```

가상환경은 프로젝트마다 패키지 버전을 분리하기 위한 장치다.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install numpy matplotlib opencv-python ultralytics
pip freeze > requirements.txt
```

중요한 점은 `pip` 대신 가능하면 `python -m pip`를 쓰는 것이다. 이렇게 하면 현재 실행 중인 Python과 pip가 같은 환경에 있는지 확인하기 쉽다.

---

## 4. 함수, 모듈, `if __name__ == "__main__"`

`day_1/test_1.py`에는 계산 기록을 저장하는 함수가 있다.

```python
history = []

def calculator_with_history():
    ...

if __name__ == "__main__":
    calculator_with_history()
```

여기서 중요한 구조는 다음이다.

```text
직접 실행할 때:
    python test_1.py
    -> __name__ == "__main__" 이므로 함수 실행

다른 파일에서 import할 때:
    import test_1
    -> 함수 정의와 전역 변수는 로드되지만, main 블록은 자동 실행되지 않음
```

ROS2 Python package에서도 이 감각이 필요하다. `setup.py`의 entry point는 특정 `main()` 함수를 실행 대상으로 지정한다.

---

## 5. Python 자료형이 중요한 이유

ROS2로 넘어가면 message field마다 타입이 정해져 있다.

```text
string
int32
float64
bool
int32[4]
custom message array
```

Python에서 list, tuple, dict, int, float, str, bool의 차이를 알아야 message를 제대로 채울 수 있다.

| Python 개념 | 뒤에서 연결되는 부분 |
|---|---|
| `list` | detection 배열, bbox 좌표, LaserScan ranges |
| `dict` | class id-name mapping, parameter 묶음 |
| `float` | confidence, distance, velocity |
| `str` | topic name, frame_id, class_name |
| `bool` | success flag, condition check |
| exception | camera open failure, file not found, invalid parameter |

---

## 6. mutable / immutable

Python에서 변수는 값 자체가 아니라 객체를 가리키는 이름에 가깝다.

```python
a = [1, 2, 3]
b = a
b.append(4)
print(a)  # [1, 2, 3, 4]
```

이것이 중요한 이유는 센서 데이터나 detection list를 함수에 넘길 때 원본이 바뀔 수 있기 때문이다.

```text
원본 frame을 직접 수정해서 box를 그림
  -> 이후 단계에서도 box가 그려진 frame을 보게 됨

원본 frame.copy()에 box를 그림
  -> 원본 영상과 표시용 영상을 분리할 수 있음
```

OpenCV에서는 이 차이가 자주 중요해진다.

---

## 7. NumPy가 필요한 이유

로봇에서 다루는 데이터는 대부분 숫자 배열이다.

```text
LiDAR ranges
IMU x/y/z acceleration
camera image pixel
YOLO bbox coordinates
Kalman state vector
```

Python list로 반복문을 돌려도 가능하지만, NumPy는 배열 단위 연산을 간결하고 빠르게 처리한다.

```python
import numpy as np

ranges = np.array([2.5, 3.1, 1.8, 0.9])
near_mask = ranges < 1.0
print(ranges[near_mask])
```

여기서 `near_mask`는 bool 배열이다. 이 감각은 나중에 AMCL 실습에서 `valid = ...`로 유효한 LaserScan 값만 골라 계산하는 코드와도 연결된다.

---

## 8. shape, dtype, axis

NumPy에서 가장 자주 헷갈리는 것은 값 자체보다 배열의 모양이다.

```python
arr = np.array([[1, 2, 3], [4, 5, 6]])
print(arr.shape)  # (2, 3)
print(arr.dtype)  # int64
```

| 개념 | 의미 | 예시 |
|---|---|---|
| dimension | 몇 차원 배열인가 | 1D, 2D, 3D |
| shape | 각 차원의 크기 | image: `(480, 640, 3)` |
| dtype | 원소 타입 | `uint8`, `float32`, `float64` |
| axis | 연산 방향 | `axis=0`, `axis=1` |

OpenCV 이미지의 shape는 보통 다음과 같다.

```text
(height, width, channel)
```

그래서 배열 인덱싱은 아래처럼 해석해야 한다.

```python
pixel = img[y, x]
```

좌표를 말할 때는 보통 `(x, y)`라고 하지만, 배열로 접근할 때는 `[y, x]`다. 이 차이는 이미지 처리에서 매우 자주 실수하는 부분이다.

---

## 9. 극좌표와 직교좌표

LiDAR는 보통 각도별 거리값처럼 볼 수 있다. 이를 2D 점으로 바꾸려면 삼각함수를 쓴다.

```python
angles = np.linspace(-np.pi, np.pi, 360)
ranges = np.random.uniform(0.5, 5.0, 360)

x = ranges * np.cos(angles)
y = ranges * np.sin(angles)
```

이 코드는 SLAM을 직접 구현하는 것은 아니지만, `LaserScan.ranges`가 결국 공간상의 점으로 해석될 수 있다는 감각을 만든다.

나중에 `/scan`을 RViz에서 보면 점들이 퍼져 보이는데, 내부적으로는 이런 “각도 + 거리 -> 위치”의 해석이 깔려 있다.

---

## 10. Matplotlib의 위치

Matplotlib은 결과물을 예쁘게 만드는 도구라기보다, 계산이 말이 되는지 확인하는 디버깅 도구다.

| 그래프 | 쓰는 상황 |
|---|---|
| line plot | 센서값, error, FPS, NIS 시계열 |
| scatter | LiDAR point, feature point |
| histogram | noise 분포 |
| image display | OpenCV 결과 비교 |

Kalman Filter의 NIS 평가에서도 Matplotlib이 다시 등장한다.

```text
raw measurement가 얼마나 튀는지
filter output이 얼마나 부드러워졌는지
NIS가 기준 범위 안에 있는지
```

숫자만 보는 것보다 그래프로 보는 쪽이 훨씬 빠르게 판단할 수 있다.

---

## 11. 현재 단계에서의 결론

Day 01에서 가져가야 할 것은 아래다.

```text
Python 파일은 직접 실행될 수도 있고 import될 수도 있다.
함수와 class는 뒤에서 ROS2 node/callback 구조로 이어진다.
NumPy 배열의 shape/dtype/axis를 알아야 sensor/image/bbox 데이터를 해석할 수 있다.
Matplotlib은 센서 데이터와 필터 결과를 확인하는 디버깅 도구다.
```

다음 단계에서는 이 기본기를 센서 객체, 파일 저장, thread/process 구조로 확장한다.
