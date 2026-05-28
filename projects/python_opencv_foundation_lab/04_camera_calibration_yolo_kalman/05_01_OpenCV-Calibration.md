# 05.01 OpenCV Camera Calibration 정리

이 문서는 카메라 캘리브레이션을 처음 배우는 사람도 따라갈 수 있도록, 핀홀 카메라 모델의 수학적 원리부터 OpenCV 실습 코드의 흐름까지 차근차근 설명한다.

---

## 1. 카메라 캘리브레이션이란?

카메라는 실제 3차원 세계를 2차원 이미지로 바꾼다.

예를 들어 실제 공간에 있는 물체의 한 점이 있다고 하자.

```text
실제 세계의 한 점 P = (X, Y, Z)
        |
        | 카메라 렌즈를 통과
        v
이미지 위의 한 점 p = (u, v)
```

여기서 문제는 3D 정보가 2D 이미지로 바뀌는 순간, 깊이 정보가 사라진다는 점이다. 이미지 속 픽셀 하나만 보면 그 점이 카메라에서 1m 떨어져 있는지, 3m 떨어져 있는지 바로 알 수 없다.

그래서 로봇 비전에서는 다음 질문에 답해야 한다.

- 이 카메라는 3D 점을 2D 픽셀로 어떤 방식으로 투영하는가?
- 렌즈 때문에 이미지가 얼마나 휘어지는가?
- 픽셀 좌표 `(u, v)`를 실제 공간의 방향 또는 위치로 어떻게 바꿀 수 있는가?

이 질문에 답하기 위해 카메라의 고유한 수학적 파라미터를 구하는 과정이 **카메라 캘리브레이션(Camera Calibration)** 이다.

캘리브레이션을 하면 다음 값을 얻는다.

| 값 | 의미 |
|---|---|
| 카메라 행렬 `K` | 초점 거리, 주점 등 카메라 내부 특성 |
| 왜곡 계수 `dist` | 렌즈가 이미지를 얼마나 휘게 만드는지 나타내는 값 |
| 외부 파라미터 `rvecs`, `tvecs` | 각 체커보드 이미지에서 카메라와 보드의 상대 자세 |
| 재투영 오차 `ret` | 캘리브레이션 결과가 얼마나 정확한지 나타내는 오차 |

---

## 2. 핀홀 카메라 모델

### 2.1 기본 아이디어

핀홀 카메라는 말 그대로 작은 구멍 하나만 있는 카메라다.

```text
물체에서 나온 빛
      \
       \
        \   작은 구멍
         \    o
          \   |
           \  |
            \ v
           이미지 평면
```

핵심 가정은 다음과 같다.

1. 빛은 직선으로 이동한다.
2. 모든 빛은 크기가 0에 가까운 하나의 구멍을 통과한다.
3. 3D 점 하나는 이미지 평면의 2D 점 하나로 투영된다.

이 모델은 현실 카메라와 완전히 같지는 않지만, 수학적으로 매우 단순하기 때문에 컴퓨터 비전의 기본 모델로 사용된다.

### 2.2 왜 실제 카메라는 렌즈를 사용하는가?

핀홀 구멍이 아주 작으면 이미지가 선명해진다. 하지만 들어오는 빛이 적어서 이미지가 어두워진다.

반대로 구멍을 크게 만들면 빛은 많이 들어오지만, 여러 방향의 빛이 섞여 이미지가 흐릿해진다.

| 구멍 크기 | 장점 | 단점 |
|---|---|---|
| 작음 | 선명함 | 어두움 |
| 큼 | 밝음 | 흐릿함 |

렌즈는 이 문제를 해결한다. 한 점에서 나온 여러 빛줄기를 다시 이미지 평면의 한 점으로 모아 밝고 선명한 이미지를 만든다.

하지만 렌즈는 빛을 굴절시키기 때문에 새로운 문제가 생긴다.

**렌즈 왜곡(Distortion)** 이다.

따라서 실제 카메라는 다음 흐름으로 이해하면 된다.

```text
실제 렌즈 카메라
      |
      | 캘리브레이션으로 왜곡 계수 계산
      v
왜곡 보정된 이미지
      |
      | 핀홀 카메라 모델 적용
      v
수학적으로 다루기 쉬운 카메라
```

---

## 3. 좌표계 정리

카메라 수학에서 헷갈리는 가장 큰 이유는 좌표계가 여러 개이기 때문이다.

### 3.1 3D 월드 좌표계

월드 좌표계는 실제 세계의 기준 좌표계다.

예를 들어 로봇이 있는 방의 한쪽 모서리를 원점으로 잡으면, 물체의 위치를 다음처럼 표현할 수 있다.

```text
P_world = (X_world, Y_world, Z_world)
```

월드 좌표계는 카메라가 아니라 환경 기준이다.

### 3.2 3D 카메라 좌표계

카메라 좌표계는 카메라 렌즈의 중심을 원점으로 잡는다.

OpenCV와 일반적인 카메라 optical frame에서는 보통 다음처럼 축을 둔다.

| 축 | 방향 |
|---|---|
| X | 이미지 오른쪽 |
| Y | 이미지 아래쪽 |
| Z | 카메라가 바라보는 앞쪽 |

카메라 앞에 있는 3D 점은 다음처럼 표현된다.

```text
P_camera = (X, Y, Z)
```

여기서 `Z`는 깊이(depth)다. `Z`가 클수록 카메라에서 멀리 있는 점이다.

### 3.3 이미지 좌표계

이미지 좌표계는 아직 픽셀 단위가 아니라, 핀홀 모델에서 사용하는 정규화된 좌표계다.

3D 점 `(X, Y, Z)`는 깊이 `Z`로 나누어 2D 평면의 점이 된다.

```text
x = X / Z
y = Y / Z
```

이때 `(x, y)`는 길이 단위가 없다. 그냥 비율이다.

예를 들어 `X = 0.3m`, `Z = 2.0m`이면

```text
x = 0.3 / 2.0 = 0.15
```

이는 "카메라 앞 방향으로 2m 떨어진 점이, 오른쪽으로는 깊이의 15%만큼 벗어나 있다"는 의미다.

### 3.4 픽셀 좌표계

픽셀 좌표계는 우리가 이미지에서 실제로 보는 좌표다.

```text
왼쪽 위 모서리 = (0, 0)
오른쪽 방향 = u 증가
아래쪽 방향 = v 증가
```

OpenCV에서 이미지 좌표를 다룰 때는 보통 `(u, v)` 또는 `(x_pixel, y_pixel)` 형태를 사용한다.

---

## 4. 핀홀 투영 수식

### 4.1 닮은 삼각형으로 이해하기

카메라 중심에서 이미지 평면까지의 거리를 초점 거리 `f`라고 하자.

3D 점이 카메라 좌표계에서 `(X, Y, Z)`에 있을 때, 이미지 평면에 맺히는 위치는 닮은 삼각형으로 계산할 수 있다.

```text
x_image / f = X / Z
y_image / f = Y / Z
```

따라서

```text
x_image = f * X / Z
y_image = f * Y / Z
```

여기서 중요한 점은 `Z`로 나누는 것이다.

- `Z`가 커지면 물체가 멀어진다.
- 멀어진 물체는 이미지에서 작게 보인다.
- 그래서 `X / Z`, `Y / Z`가 작아진다.

### 4.2 초점 거리 `f`와 픽셀 단위 초점 거리 `fx`, `fy`

물리적인 초점 거리 `f`는 보통 mm 단위다. 하지만 이미지 좌표는 픽셀 단위다.

그래서 실제 코드에서는 `f`를 그대로 쓰지 않고, 픽셀 단위로 바꾼 `fx`, `fy`를 사용한다.

```text
fx = f / dx
fy = f / dy
```

| 기호 | 단위 | 의미 |
|---|---|---|
| `f` | mm | 렌즈 중심에서 센서까지의 물리적 거리 |
| `dx` | mm/pixel | 픽셀 하나의 가로 실제 크기 |
| `dy` | mm/pixel | 픽셀 하나의 세로 실제 크기 |
| `fx` | pixel | 가로 방향 픽셀 단위 초점 거리 |
| `fy` | pixel | 세로 방향 픽셀 단위 초점 거리 |

예를 들어

```text
f = 4.0 mm
dx = 0.004 mm/pixel
dy = 0.004 mm/pixel
```

이면

```text
fx = 4.0 / 0.004 = 1000 pixel
fy = 4.0 / 0.004 = 1000 pixel
```

`fx = 1000`이라는 말은 초점 거리가 픽셀 1000개의 길이에 해당한다는 뜻이다.

### 4.3 주점 `cx`, `cy`

주점(Principal Point)은 카메라의 광축이 이미지 센서와 만나는 점이다.

쉽게 말하면 "렌즈 중심이 이미지 위에 떨어지는 위치"다.

이론적으로는 이미지 정중앙이어야 한다.

예를 들어 640x480 이미지라면 이상적인 주점은 다음과 같다.

```text
cx = 640 / 2 = 320
cy = 480 / 2 = 240
```

하지만 실제 카메라는 제조 오차 때문에 렌즈와 센서가 완벽히 정렬되지 않는다. 그래서 실제 `cx`, `cy`는 중앙에서 조금 벗어날 수 있다.

### 4.4 카메라 행렬 `K`

초점 거리와 주점을 하나로 모은 행렬을 카메라 행렬 또는 내부 파라미터 행렬이라고 한다.

```text
K = [ fx   0  cx ]
    [  0  fy  cy ]
    [  0   0   1 ]
```

이 행렬은 카메라마다 고유하다. 렌즈, 센서, 해상도, 줌 상태가 바뀌면 `K`도 바뀐다.

### 4.5 3D 점을 2D 픽셀로 투영하기

3D 카메라 좌표계의 점을

```text
P = (X, Y, Z)
```

라고 하자.

먼저 정규화 이미지 좌표를 구한다.

```text
x = X / Z
y = Y / Z
```

그 다음 픽셀 좌표로 바꾼다.

```text
u = fx * x + cx
v = fy * y + cy
```

즉 최종 수식은 다음과 같다.

```text
u = fx * X / Z + cx
v = fy * Y / Z + cy
```

예제:

```text
fx = 800
fy = 800
cx = 320
cy = 240

P = (X, Y, Z) = (0.3, 0.2, 2.0)
```

계산:

```text
u = 800 * (0.3 / 2.0) + 320
  = 800 * 0.15 + 320
  = 120 + 320
  = 440

v = 800 * (0.2 / 2.0) + 240
  = 800 * 0.1 + 240
  = 80 + 240
  = 320
```

따라서 3D 점 `(0.3, 0.2, 2.0)`은 이미지 픽셀 `(440, 320)`에 찍힌다.

### 4.6 동차 좌표로 표현하기

컴퓨터 비전에서는 행렬 곱으로 표현하기 위해 동차 좌표를 자주 사용한다.

정규화 좌표를 다음처럼 쓴다.

```text
[x, y, 1]^T = [X/Z, Y/Z, 1]^T
```

픽셀 좌표는 다음과 같다.

```text
[u, v, 1]^T = K [x, y, 1]^T
```

펼쳐 쓰면

```text
[u]   [ fx  0  cx ] [x]
[v] = [  0 fy  cy ] [y]
[1]   [  0  0   1 ] [1]
```

행렬 곱 결과:

```text
u = fx*x + cx
v = fy*y + cy
1 = 1
```

---

## 5. 픽셀에서 3D 방향으로 되돌리기

픽셀 좌표 `(u, v)`와 카메라 행렬 `K`를 알고 있으면, 이 픽셀이 카메라에서 어느 방향을 바라보는지 알 수 있다.

```text
x = (u - cx) / fx
y = (v - cy) / fy
```

이 `(x, y)`는 정규화 이미지 좌표다.

하지만 이것만으로는 3D 위치를 완전히 복원할 수 없다. 이유는 깊이 `Z`가 없기 때문이다.

깊이 `Z`까지 알고 있다면 3D 좌표를 복원할 수 있다.

```text
X = x * Z = (u - cx) / fx * Z
Y = y * Z = (v - cy) / fy * Z
Z = Z
```

예제:

```text
u = 440
v = 320
fx = 800
fy = 800
cx = 320
cy = 240
Z = 2.0m
```

계산:

```text
X = (440 - 320) / 800 * 2.0
  = 120 / 800 * 2.0
  = 0.15 * 2.0
  = 0.3m

Y = (320 - 240) / 800 * 2.0
  = 80 / 800 * 2.0
  = 0.1 * 2.0
  = 0.2m
```

따라서 픽셀 `(440, 320)`과 깊이 `2.0m`를 알면 3D 점 `(0.3, 0.2, 2.0)`을 얻는다.

---

## 6. 렌즈 왜곡

핀홀 모델은 이상적인 모델이다. 실제 렌즈는 이미지를 휘게 만든다.

왜곡이 보정되지 않으면 다음 문제가 생긴다.

- 직선 벽이 곡선처럼 보인다.
- 이미지 가장자리의 물체 위치가 실제보다 다르게 계산된다.
- 픽셀 좌표를 3D 방향으로 바꿀 때 오차가 커진다.
- 로봇이 거리나 방향을 잘못 추정할 수 있다.

렌즈 왜곡은 크게 두 종류로 나눈다.

### 6.1 방사 왜곡

방사 왜곡(Radial Distortion)은 이미지 중심에서 멀어질수록 커지는 왜곡이다.

렌즈 중심 근처는 비교적 정확하지만, 이미지 가장자리로 갈수록 직선이 휘어진다.

대표적인 형태는 두 가지다.

| 종류 | 특징 | 자주 발생하는 렌즈 |
|---|---|---|
| 배럴 왜곡 | 이미지가 바깥으로 볼록하게 부푼 것처럼 보임 | 광각 렌즈 |
| 핀쿠션 왜곡 | 이미지가 안쪽으로 오목하게 들어간 것처럼 보임 | 망원 렌즈 |

정규화 좌표 `(x, y)`에서 중심으로부터의 거리 제곱은 다음과 같다.

```text
r^2 = x^2 + y^2
```

방사 왜곡은 보통 `k1`, `k2`, `k3`로 표현한다.

```text
x_radial = x * (1 + k1*r^2 + k2*r^4 + k3*r^6)
y_radial = y * (1 + k1*r^2 + k2*r^4 + k3*r^6)
```

왜 `r^2`, `r^4`, `r^6`을 쓰는가?

렌즈 왜곡은 중심으로부터의 거리와 관련이 있다. 방향이 아니라 중심에서 얼마나 떨어져 있는지가 중요하기 때문에 `r = sqrt(x^2 + y^2)`를 사용한다. 계산에서는 제곱근을 피하고 다항식으로 안정적으로 표현하기 위해 `r^2`, `r^4`, `r^6` 형태를 쓴다.

### 6.2 접선 왜곡

접선 왜곡(Tangential Distortion)은 렌즈와 이미지 센서가 완벽하게 평행하지 않을 때 생긴다.

즉 렌즈가 센서에 대해 아주 살짝 기울어져 있으면, 이미지가 비스듬하게 밀린 것처럼 보일 수 있다.

접선 왜곡은 `p1`, `p2`로 표현한다.

```text
x_tangential = 2*p1*x*y + p2*(r^2 + 2*x^2)
y_tangential = p1*(r^2 + 2*y^2) + 2*p2*x*y
```

### 6.3 전체 왜곡 모델

OpenCV에서 일반적으로 사용하는 왜곡 모델은 방사 왜곡과 접선 왜곡을 합친 형태다.

```text
x' = x * (1 + k1*r^2 + k2*r^4 + k3*r^6)
     + 2*p1*x*y
     + p2*(r^2 + 2*x^2)

y' = y * (1 + k1*r^2 + k2*r^4 + k3*r^6)
     + p1*(r^2 + 2*y^2)
     + 2*p2*x*y
```

여기서

| 기호 | 의미 |
|---|---|
| `(x, y)` | 왜곡 전 또는 이상적인 정규화 좌표 |
| `(x', y')` | 왜곡이 적용된 정규화 좌표 |
| `r^2` | 중심에서 떨어진 거리의 제곱 |
| `k1, k2, k3` | 방사 왜곡 계수 |
| `p1, p2` | 접선 왜곡 계수 |

OpenCV의 `dist` 배열은 보통 다음 순서를 가진다.

```text
dist = [k1, k2, p1, p2, k3]
```

실습 코드에서는 합성 왜곡을 만들기 위해 다음 값을 사용한다.

```python
DIST_COEF = np.array([[-0.40, 0.15, 0.001, -0.001, 0.05]], np.float64)
```

즉

```text
k1 = -0.40
k2 =  0.15
p1 =  0.001
p2 = -0.001
k3 =  0.05
```

---

## 7. 체커보드 캘리브레이션 원리

### 7.1 왜 체커보드를 쓰는가?

카메라 파라미터를 구하려면 다음 두 정보를 많이 모아야 한다.

1. 실제 3D 공간에서 기준점들이 어디에 있는지
2. 그 기준점들이 이미지에서 어떤 픽셀에 찍혔는지

체커보드는 이 조건에 적합하다.

- 검정/흰색 대비가 뚜렷해서 코너 검출이 쉽다.
- 격자 구조가 규칙적이라 실제 좌표를 정의하기 쉽다.
- 교차점을 서브픽셀 단위로 정밀하게 찾을 수 있다.

주의할 점은 OpenCV가 입력받는 체커보드 크기는 칸 수가 아니라 **내부 교차점 수**라는 것이다.

예를 들어 체커보드가 10칸 x 7칸이면 내부 교차점은 다음과 같다.

```text
가로 내부 교차점 = 10 - 1 = 9
세로 내부 교차점 = 7 - 1 = 6
```

따라서 코드에서는 다음처럼 쓴다.

```python
CHECKERBOARD = (9, 6)
```

### 7.2 객체 포인트와 이미지 포인트

캘리브레이션에서 가장 중요한 두 리스트가 있다.

```python
objpoints = []
imgpoints = []
```

#### 객체 포인트

객체 포인트(object points)는 실제 3D 공간에서 체커보드 코너들의 좌표다.

체커보드가 평평한 판 위에 있다고 가정하면 모든 코너는 `Z = 0` 평면 위에 있다.

예를 들어 내부 코너가 9x6개라면 다음 좌표를 만들 수 있다.

```text
(0,0,0), (1,0,0), (2,0,0), ... (8,0,0)
(0,1,0), (1,1,0), (2,1,0), ... (8,1,0)
...
(0,5,0), (1,5,0), (2,5,0), ... (8,5,0)
```

코드에서는 보통 다음처럼 만든다.

```python
objp = np.zeros((pattern[0] * pattern[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:pattern[0], 0:pattern[1]].T.reshape(-1, 2)
```

여기서 좌표 단위는 체커보드 한 칸의 크기다. 실제 한 칸이 25mm라면 `objp[:, :2] *= 25`처럼 곱해주면 mm 단위가 된다.

#### 이미지 포인트

이미지 포인트(image points)는 카메라 이미지에서 검출된 체커보드 코너의 픽셀 좌표다.

```python
ret, corners = cv2.findChessboardCorners(gray, pattern, None)
```

검출된 `corners`는 대략적인 픽셀 좌표다. 더 정확하게 만들기 위해 `cornerSubPix()`를 사용한다.

```python
corners_refined = cv2.cornerSubPix(
    gray,
    corners,
    (11, 11),
    (-1, -1),
    criteria
)
```

`cornerSubPix()`는 코너 위치를 정수 픽셀보다 더 정밀한 소수점 픽셀 좌표로 다듬는다.

예:

```text
정수 픽셀 코너: (231, 145)
서브픽셀 코너: (231.42, 145.87)
```

캘리브레이션은 작은 픽셀 오차에도 영향을 받기 때문에 이 정밀화 과정이 중요하다.

### 7.3 여러 장의 이미지가 필요한 이유

이미지 한 장만으로는 카메라의 초점 거리, 주점, 왜곡 계수를 안정적으로 구하기 어렵다.

좋은 캘리브레이션 이미지는 다음 조건을 만족해야 한다.

- 최소 10~20장 이상
- 체커보드를 다양한 거리에서 촬영
- 체커보드를 다양한 각도로 기울여 촬영
- 이미지 중앙뿐 아니라 가장자리와 모서리까지 골고루 포함
- 촬영 중 해상도, 줌, 초점이 바뀌지 않음

특히 가장자리 데이터가 중요하다. 렌즈 왜곡은 이미지 가장자리에서 크게 나타나기 때문이다.

---

## 8. OpenCV 캘리브레이션 함수 흐름

전체 흐름은 다음 3단계다.

```text
1. findChessboardCorners()
   이미지에서 체커보드 내부 코너 찾기

2. cornerSubPix()
   찾은 코너를 서브픽셀 단위로 정밀화

3. calibrateCamera()
   3D 객체 포인트와 2D 이미지 포인트를 비교해 카메라 파라미터 계산
```

### 8.1 `cv2.findChessboardCorners()`

```python
ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, None)
```

함수 원형을 간단히 쓰면 다음과 같다.

```python
ret, corners = cv2.findChessboardCorners(image, patternSize, flags)
```

인자 설명:

| 인자 | 예시 | 의미 |
|---|---|---|
| `image` | `gray` | 체커보드를 찾을 입력 이미지. 보통 흑백 이미지 사용 |
| `patternSize` | `(9, 6)` | 체커보드 내부 교차점 개수. 칸 수가 아니라 코너 수 |
| `flags` | `None` | 검출 옵션. 기본값으로 충분하면 `None` 사용 |

| 반환값 | 의미 |
|---|---|
| `ret` | 코너 검출 성공 여부 |
| `corners` | 검출된 코너들의 픽셀 좌표 |

`ret == True`일 때만 해당 이미지를 캘리브레이션에 사용한다.

여기서 `CHECKERBOARD = (9, 6)`은 가로 코너 9개, 세로 코너 6개를 찾겠다는 뜻이다. 만약 실제 체커보드 내부 교차점이 8x5인데 코드에 9x6을 넣으면 OpenCV는 패턴을 찾지 못한다.

`corners`의 모양은 보통 다음과 같다.

```text
(코너 개수, 1, 2)
```

예를 들어 9x6 체커보드라면 코너 개수는 `9 * 6 = 54`개이므로 대략 다음 형태가 된다.

```text
corners.shape = (54, 1, 2)
```

마지막 `2`는 각 코너의 픽셀 좌표 `(x, y)`를 의미한다. OpenCV 이미지 좌표에서는 `x`가 오른쪽 방향, `y`가 아래쪽 방향이다.

### 8.2 `cv2.cornerSubPix()`

```python
criteria = (
    cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,
    30,
    0.001
)
```

이 조건은 반복 계산을 언제 멈출지 정한다.

| 항목 | 의미 |
|---|---|
| `MAX_ITER = 30` | 최대 30번 반복 |
| `EPS = 0.001` | 코너 위치 변화가 0.001픽셀보다 작으면 수렴 |

코너 정밀화:

```python
corners_refined = cv2.cornerSubPix(
    gray,
    corners,
    (11, 11),
    (-1, -1),
    criteria
)
```

함수 원형을 간단히 쓰면 다음과 같다.

```python
corners_refined = cv2.cornerSubPix(
    image,
    corners,
    winSize,
    zeroZone,
    criteria
)
```

인자 설명:

| 인자 | 예시 | 의미 |
|---|---|---|
| `image` | `gray` | 코너를 더 정밀하게 찾을 흑백 이미지 |
| `corners` | `corners` | `findChessboardCorners()`가 찾은 초기 코너 좌표 |
| `winSize` | `(11, 11)` | 각 코너 주변에서 탐색할 창 크기 |
| `zeroZone` | `(-1, -1)` | 탐색 중심 주변에서 제외할 영역. `(-1, -1)`이면 제외 영역 없음 |
| `criteria` | `(type, max_iter, epsilon)` | 반복 계산 종료 조건 |

`(11, 11)`은 코너 주변 11x11 영역을 보고 더 정확한 코너 위치를 찾겠다는 뜻이다.

`criteria`는 "언제까지 반복해서 더 좋은 코너 위치를 찾을 것인가?"를 정한다.

```python
criteria = (
    cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,
    30,
    0.001
)
```

위 코드는 다음 뜻이다.

| 값 | 의미 |
|---|---|
| `cv2.TERM_CRITERIA_EPS` | 변화량이 충분히 작아지면 종료 |
| `cv2.TERM_CRITERIA_MAX_ITER` | 최대 반복 횟수에 도달하면 종료 |
| `30` | 최대 30번 반복 |
| `0.001` | 코너 위치 변화가 0.001픽셀보다 작으면 종료 |

즉 "최대 30번까지만 반복하되, 그 전에 변화량이 0.001픽셀보다 작아지면 멈춘다"는 의미다.

### 8.3 `cv2.calibrateCamera()`

```python
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
    objpoints,
    imgpoints,
    image_size,
    None,
    None
)
```

함수 원형을 간단히 쓰면 다음과 같다.

```python
ret, cameraMatrix, distCoeffs, rvecs, tvecs = cv2.calibrateCamera(
    objectPoints,
    imagePoints,
    imageSize,
    cameraMatrix,
    distCoeffs
)
```

인자 설명:

| 인자 | 예시 | 의미 |
|---|---|---|
| `objectPoints` | `objpoints` | 실제 3D 공간에서의 체커보드 코너 좌표 목록 |
| `imagePoints` | `imgpoints` | 이미지에서 검출한 2D 코너 픽셀 좌표 목록 |
| `imageSize` | `(640, 480)` | 이미지 크기. 순서는 `(width, height)` |
| `cameraMatrix` | `None` | 초기 카메라 행렬. 모르면 `None` |
| `distCoeffs` | `None` | 초기 왜곡 계수. 모르면 `None` |

`objectPoints`와 `imagePoints`는 반드시 서로 대응되어야 한다. 예를 들어 첫 번째 이미지의 3D 코너 목록이 `objpoints[0]`에 들어갔다면, 그 이미지에서 검출한 2D 코너 목록은 `imgpoints[0]`에 들어가야 한다.

`imageSize`에서 주의할 점은 OpenCV 이미지 배열의 모양과 순서가 다르다는 것이다.

```python
gray.shape        # (height, width)
gray.shape[::-1]  # (width, height)
```

그래서 코드에서 다음처럼 쓴다.

```python
image_size = gray.shape[::-1]
```

반환값:

| 반환값 | 의미 |
|---|---|
| `ret` | RMS 재투영 오차 |
| `mtx` | 카메라 행렬 `K` |
| `dist` | 왜곡 계수 `[k1, k2, p1, p2, k3]` |
| `rvecs` | 각 이미지의 회전 벡터 |
| `tvecs` | 각 이미지의 이동 벡터 |

반환값을 조금 더 자세히 보면 다음과 같다.

#### `ret`

`ret`는 RMS 재투영 오차다. 단위는 픽셀이다. 값이 작을수록 캘리브레이션 결과가 좋다.

#### `mtx`

`mtx`는 카메라 행렬이다.

```text
mtx = [ fx   0  cx ]
      [  0  fy  cy ]
      [  0   0   1 ]
```

OpenCV 코드에서는 보통 다음처럼 값을 꺼낸다.

```python
fx = mtx[0, 0]
fy = mtx[1, 1]
cx = mtx[0, 2]
cy = mtx[1, 2]
```

#### `dist`

`dist`는 왜곡 계수다. 일반적인 5개 계수 모델에서는 다음 순서다.

```text
dist = [k1, k2, p1, p2, k3]
```

| 계수 | 의미 |
|---|---|
| `k1`, `k2`, `k3` | 방사 왜곡 계수 |
| `p1`, `p2` | 접선 왜곡 계수 |

#### `rvecs`, `tvecs`

`rvecs`와 `tvecs`는 이미지마다 하나씩 나온다.

예를 들어 캘리브레이션에 성공한 이미지가 20장이라면

```text
len(rvecs) = 20
len(tvecs) = 20
```

`rvecs[i]`와 `tvecs[i]`는 i번째 이미지에서 체커보드가 카메라 기준으로 어떤 회전과 이동을 가지고 있었는지 나타낸다.

`calibrateCamera()`는 다음 최적화 문제를 푼다.

```text
실제 검출된 이미지 코너 좌표
        vs
현재 카메라 모델로 다시 투영한 코너 좌표
```

이 두 좌표의 차이가 최소가 되도록 `K`, `dist`, `rvecs`, `tvecs`를 찾는다.

수식으로 쓰면, 모든 이미지와 모든 코너에 대해 다음 오차를 최소화한다.

```text
error = sum || p_detected - p_projected ||^2
```

여기서

| 기호 | 의미 |
|---|---|
| `p_detected` | 실제 이미지에서 검출한 코너 픽셀 |
| `p_projected` | 추정된 카메라 모델로 3D 코너를 다시 투영한 픽셀 |

---

## 9. 재투영 오차

재투영 오차(Reprojection Error)는 캘리브레이션 품질을 평가하는 핵심 지표다.

과정은 다음과 같다.

1. 캘리브레이션으로 `K`, `dist`, `rvecs`, `tvecs`를 구한다.
2. 체커보드의 3D 객체 포인트를 다시 이미지에 투영한다.
3. 실제 검출된 2D 코너와 다시 투영된 2D 코너의 거리를 계산한다.
4. 전체 평균 오차를 픽셀 단위로 확인한다.

코드에서는 다음 함수를 사용한다.

```python
proj, _ = cv2.projectPoints(op, rvecs[i], tvecs[i], mtx, dist)
err = cv2.norm(ip, proj, cv2.NORM_L2) / len(proj)
```

`cv2.projectPoints()` 인자 설명:

| 인자 | 예시 | 의미 |
|---|---|---|
| `objectPoints` | `op` | 다시 투영할 3D 점들 |
| `rvec` | `rvecs[i]` | 해당 이미지의 회전 벡터 |
| `tvec` | `tvecs[i]` | 해당 이미지의 이동 벡터 |
| `cameraMatrix` | `mtx` | 카메라 행렬 |
| `distCoeffs` | `dist` | 왜곡 계수 |

반환값:

| 반환값 | 의미 |
|---|---|
| `proj` | 3D 점을 다시 이미지에 투영한 2D 픽셀 좌표 |
| `_` | 자코비안 행렬. 여기서는 사용하지 않으므로 `_`로 받음 |

`cv2.norm(ip, proj, cv2.NORM_L2)`는 실제 검출 좌표 `ip`와 다시 투영한 좌표 `proj` 사이의 유클리드 거리 합을 계산한다.

유클리드 거리는 두 점 사이의 직선 거리다.

```text
distance = sqrt((x1 - x2)^2 + (y1 - y2)^2)
```

마지막에 `len(proj)`로 나누는 이유는 코너 개수로 나누어 평균적인 코너 오차를 보기 위해서다.

평가 기준:

| RMS Error | 해석 |
|---|---|
| 0.5px 미만 | 매우 좋음 |
| 1.0px 이하 | 대부분의 용도에서 사용 가능 |
| 1.0px 초과 | 촬영 데이터 또는 체커보드 설정 점검 필요 |

오차가 크다면 다음을 확인한다.

- 체커보드 내부 교차점 수를 잘못 입력하지 않았는가?
- 흔들린 사진이나 흐릿한 사진이 섞여 있지 않은가?
- 체커보드가 휘어져 있지 않은가?
- 중앙 사진만 있고 가장자리 사진이 부족하지 않은가?
- 촬영 중 줌, 초점, 해상도가 바뀌지 않았는가?

---

## 10. 왜곡 보정

캘리브레이션으로 `mtx`와 `dist`를 얻었다면 이미지를 보정할 수 있다.

가장 간단한 방식은 `cv2.undistort()`를 사용하는 것이다.

```python
dst = cv2.undistort(img, mtx, dist, None, mtx)
```

함수 원형을 간단히 쓰면 다음과 같다.

```python
dst = cv2.undistort(src, cameraMatrix, distCoeffs, newCameraMatrix)
```

실습 코드처럼 5개 인자를 쓰면 다음 의미다.

| 인자 | 의미 |
|---|---|
| `img` | 왜곡된 원본 이미지 |
| `mtx` | 입력 카메라 행렬 |
| `dist` | 왜곡 계수 |
| `None` | 출력 배열을 직접 지정하지 않음 |
| `mtx` | 출력 이미지에 사용할 새 카메라 행렬 |

마지막 인자인 새 카메라 행렬을 조정하면 보정 후 이미지의 시야각이나 잘리는 영역을 바꿀 수 있다. 실습에서는 이해를 쉽게 하기 위해 입력 카메라 행렬 `mtx`를 그대로 사용한다.

실시간 영상에서는 매 프레임마다 `undistort()`를 직접 호출할 수도 있지만, 더 효율적인 방법은 보정 맵을 미리 계산하는 것이다.

```python
undist_map1, undist_map2 = cv2.initUndistortRectifyMap(
    mtx,
    dist,
    None,
    mtx,
    (w, h),
    cv2.CV_16SC2
)
```

`cv2.initUndistortRectifyMap()` 인자 설명:

| 인자 | 예시 | 의미 |
|---|---|---|
| `cameraMatrix` | `mtx` | 입력 카메라 행렬 |
| `distCoeffs` | `dist` | 왜곡 계수 |
| `R` | `None` | 추가 회전 보정 행렬. 일반 단일 카메라 보정에서는 `None` |
| `newCameraMatrix` | `mtx` | 보정 후 사용할 카메라 행렬 |
| `size` | `(w, h)` | 출력 이미지 크기. 순서는 `(width, height)` |
| `m1type` | `cv2.CV_16SC2` | 맵의 데이터 타입. 실시간 처리에 효율적인 형식 |

반환값:

| 반환값 | 의미 |
|---|---|
| `undist_map1` | 보정에 필요한 첫 번째 좌표 맵 |
| `undist_map2` | 보정에 필요한 두 번째 좌표 맵 |

그 다음 매 프레임에는 `remap()`만 적용한다.

```python
undistorted = cv2.remap(distorted, undist_map1, undist_map2, cv2.INTER_LINEAR)
```

`cv2.remap()` 인자 설명:

| 인자 | 예시 | 의미 |
|---|---|---|
| `src` | `distorted` | 보정할 입력 이미지 |
| `map1` | `undist_map1` | `initUndistortRectifyMap()`이 만든 좌표 맵 1 |
| `map2` | `undist_map2` | `initUndistortRectifyMap()`이 만든 좌표 맵 2 |
| `interpolation` | `cv2.INTER_LINEAR` | 픽셀 값을 보간하는 방법 |

보간(interpolation)이 필요한 이유는 보정 과정에서 픽셀 좌표가 정수로 딱 떨어지지 않기 때문이다. 예를 들어 어떤 출력 픽셀이 원본 이미지의 `(123.4, 57.8)` 위치에서 값을 가져와야 한다면, 주변 픽셀들을 섞어서 색을 계산해야 한다. `cv2.INTER_LINEAR`는 주변 픽셀을 선형 보간하는 일반적인 방식이다.

이 방식이 실시간 처리에 더 적합하다. 보정 좌표 계산은 한 번만 하고, 프레임마다 픽셀을 재배치하기 때문이다.

---

## 11. 실습 파일별 역할

### 11.1 `05_01_OpenCV-Calibration.ipynb`

이 노트북은 전체 이론과 캘리브레이션 파이프라인을 실습하는 중심 파일이다.

주요 내용:

1. `fx`, `fy` 계산
2. 카메라 행렬 `K` 구성
3. 3D 점을 2D 픽셀로 투영
4. 픽셀 좌표를 깊이와 함께 3D 좌표로 역변환
5. 체커보드 코너 검출
6. `calibrateCamera()` 실행
7. 재투영 오차 계산
8. `undistort()`로 왜곡 보정
9. YAML 파일로 결과 저장 및 불러오기

노트북에서 사용하는 예시 상수:

```python
F_MM       = 4.0
DX         = 0.004
DY         = 0.004
IMG_WIDTH  = 640
IMG_HEIGHT = 480
```

초점 거리를 픽셀 단위로 바꾸면 다음과 같다.

```python
fx = F_MM / DX
fy = F_MM / DY
```

카메라 행렬:

```python
K = np.array([
    [fx,  0,  cx],
    [ 0, fy,  cy],
    [ 0,  0,   1]
], dtype=np.float64)
```

### 11.2 `05_01_01_OpenCV-Calib-Capture.py`

이 파일은 캘리브레이션용 체커보드 이미지를 촬영하고 저장한다.

핵심 설정:

```python
CHECKERBOARD = (9, 6)
SAVE_DIR = "calib_images"
CAMERA_INDEX = 0
```

동작:

1. 웹캠을 연다.
2. 매 프레임을 읽는다.
3. 필요하면 합성 렌즈 왜곡을 적용한다.
4. 체커보드 코너를 찾는다.
5. 코너가 발견되면 화면에 표시한다.
6. `SPACE` 또는 `c`를 누르면 이미지를 저장한다.
7. `q` 또는 `ESC`를 누르면 종료한다.

실습에서는 왜곡 보정 효과를 눈으로 확인하기 위해 합성 왜곡을 추가한다.

```python
USE_DISTORTION = True
DIST_COEF = np.array([[-0.40, 0.15, 0.001, -0.001, 0.05]], np.float64)
```

이 코드는 실제 카메라가 완벽히 왜곡되어 있다는 뜻이 아니라, 학습용으로 일부러 왜곡을 만들어 저장하는 구조다.

저장 파일명은 현재 시간을 이용해 만든다.

```python
filename = os.path.join(SAVE_DIR, f"calib_{timestamp}.jpg")
cv2.imwrite(filename, distorted)
```

### 11.3 `05_01_02_OpenCV-Calib-Undistort.py`

이 파일은 저장된 `camera_info.yaml`을 읽어서 실시간 영상에 왜곡 보정을 적용한다.

사전 조건:

```text
camera_info.yaml 파일이 있어야 한다.
```

이 파일은 캘리브레이션 노트북에서 다음처럼 저장한다.

```python
data = {
    'camera_matrix': mtx.tolist(),
    'dist_coeff': dist.tolist()
}
```

실시간 보정 코드의 핵심:

```python
with open(YAML_PATH, 'r') as f:
    data = yaml.safe_load(f)

mtx  = np.array(data['camera_matrix'], np.float64)
dist = np.array(data['dist_coeff'], np.float64)
```

그 다음 보정 맵을 미리 만든다.

```python
undist_map1, undist_map2 = cv2.initUndistortRectifyMap(
    mtx, dist, None, mtx, (w, h), cv2.CV_16SC2
)
```

매 프레임에서는 다음처럼 보정한다.

```python
undistorted = cv2.remap(distorted, undist_map1, undist_map2, cv2.INTER_LINEAR)
```

화면에는 왜곡된 영상과 보정된 영상을 나란히 보여준다.

```python
cv2.imshow("Live Undistort", np.hstack([distorted, undistorted]))
```

---

## 12. YAML 저장과 재사용

캘리브레이션은 매번 다시 할 필요가 없다. 카메라, 렌즈, 해상도, 줌, 초점이 그대로라면 한 번 구한 파라미터를 저장해서 재사용하면 된다.

저장:

```python
def save_calibration_yaml(mtx, dist, filepath="camera_info.yaml"):
    data = {
        'camera_matrix': mtx.tolist(),
        'dist_coeff': dist.tolist()
    }
    with open(filepath, 'w') as f:
        yaml.dump(data, f)
```

불러오기:

```python
def load_calibration_yaml(filepath="camera_info.yaml"):
    with open(filepath, 'r') as f:
        data = yaml.safe_load(f)
    mtx  = np.array(data['camera_matrix'], np.float64)
    dist = np.array(data['dist_coeff'], np.float64)
    return mtx, dist
```

주의:

- 해상도가 바뀌면 `fx`, `fy`, `cx`, `cy`도 달라질 수 있다.
- 줌이 바뀌면 초점 거리가 바뀐다.
- 자동 초점이 움직이면 내부 파라미터가 미세하게 바뀔 수 있다.
- 따라서 촬영과 실제 사용 환경의 카메라 설정을 동일하게 유지해야 한다.

---

## 13. 전체 좌표 변환 흐름

로봇이 이미지 속 픽셀을 실제 위치로 이해하는 흐름은 다음과 같다.

```text
픽셀 좌표 (u, v)
      |
      | K^-1 적용
      v
정규화 이미지 좌표 (x, y)
      |
      | 깊이 Z 곱하기
      v
카메라 좌표 (X, Y, Z)
      |
      | 외부 파라미터 R, t 적용
      v
월드 좌표 (Xw, Yw, Zw)
```

픽셀에서 정규화 좌표:

```text
x = (u - cx) / fx
y = (v - cy) / fy
```

정규화 좌표에서 카메라 좌표:

```text
X = x * Z
Y = y * Z
Z = Z
```

카메라 좌표에서 월드 좌표:

```text
P_camera = R * P_world + t
```

따라서 반대로 월드 좌표를 구하려면

```text
P_world = R^-1 * (P_camera - t)
```

여기서

| 기호 | 의미 |
|---|---|
| `R` | 회전 행렬 |
| `t` | 이동 벡터 |
| `R^-1` | 회전 행렬의 역행렬 |

회전 행렬은 직교 행렬이므로 보통 다음 성질을 가진다.

```text
R^-1 = R^T
```

즉 회전 행렬의 역행렬은 전치 행렬과 같다.

---

## 14. 초보자가 자주 헷갈리는 부분

### 14.1 이미지가 실제로는 거꾸로 맺히지 않나?

물리적인 핀홀 카메라에서는 이미지가 센서에 거꾸로 맺힌다.

하지만 컴퓨터 비전 수학에서는 계산을 편하게 하기 위해 이미지 평면을 카메라 앞쪽에 둔다고 가정한다. 그래서 수식에서는 이미지가 똑바로 선 것처럼 다룬다.

### 14.2 `f`와 `fx`는 같은가?

같지 않다.

| 값 | 단위 | 의미 |
|---|---|---|
| `f` | mm | 실제 렌즈 초점 거리 |
| `fx`, `fy` | pixel | 픽셀 단위로 환산된 초점 거리 |

OpenCV의 카메라 행렬에 들어가는 값은 `f`가 아니라 `fx`, `fy`다.

### 14.3 픽셀 좌표만으로 3D 위치를 알 수 있는가?

아니다.

픽셀 좌표만으로 알 수 있는 것은 "방향"이다. 실제 3D 위치를 알기 위해서는 깊이 `Z`가 추가로 필요하다.

깊이는 다음 방법으로 얻을 수 있다.

- RGB-D 카메라
- 스테레오 카메라
- LiDAR
- 물체의 실제 크기를 알고 있을 때의 기하 계산
- 다른 센서와의 융합

### 14.4 체커보드 크기는 칸 수인가?

OpenCV에 넣는 값은 칸 수가 아니라 내부 교차점 수다.

```text
10 x 7 칸 체커보드 -> 내부 교차점 9 x 6
8 x 6 칸 체커보드 -> 내부 교차점 7 x 5
```

### 14.5 왜 가장자리 사진이 중요한가?

렌즈 왜곡은 이미지 중심보다 가장자리에서 훨씬 크게 나타난다.

체커보드를 중앙에서만 찍으면 OpenCV는 가장자리 왜곡을 제대로 학습할 수 없다.

따라서 체커보드를 화면의 왼쪽, 오른쪽, 위쪽, 아래쪽, 네 모서리 근처까지 골고루 배치해야 한다.

---

## 15. 실습 순서

### Step 1. 체커보드 준비

- 고해상도 체커보드 패턴을 출력한다.
- 종이가 휘지 않도록 단단하고 평평한 판에 붙인다.
- 내부 교차점 수를 정확히 센다.

### Step 2. 이미지 수집

`prac` 폴더에서 이미지 수집 스크립트를 실행한다.

```bash
python3 05_01_01_OpenCV-Calib-Capture.py
```

촬영 중:

- 체커보드가 검출되면 초록색 코너 표시가 나타난다.
- `SPACE` 또는 `c`를 누르면 이미지가 저장된다.
- 최소 10~20장 이상 저장한다.
- 다양한 각도와 거리를 포함한다.
- 가장자리와 모서리 영역도 충분히 촬영한다.

### Step 3. 캘리브레이션 실행

노트북 `05_01_OpenCV-Calibration.ipynb`에서 `run_calibration("./calib_images/")`를 실행한다.

결과로 다음 값이 출력된다.

```text
RMS Error
camera matrix mtx
distortion coefficients dist
```

### Step 4. 재투영 오차 확인

재투영 오차가 너무 크면 이미지를 다시 점검한다.

```text
0.5px 미만: 매우 좋음
1.0px 이하: 보통 사용 가능
1.0px 초과: 재촬영 권장
```

### Step 5. YAML 저장

노트북에서 `camera_info.yaml`을 저장한다.

```python
save_calibration_yaml(mtx, dist)
```

### Step 6. 실시간 왜곡 보정 확인

```bash
python3 05_01_02_OpenCV-Calib-Undistort.py
```

화면에서 왼쪽은 왜곡된 영상, 오른쪽은 보정된 영상이다.

---

## 16. 실습 코드 핵심 요약

### 이미지 수집 코드 핵심

```python
cap = cv2.VideoCapture(CAMERA_INDEX)
```

카메라를 연다.

```python
ret, frame = cap.read()
```

프레임을 한 장 읽는다.

```python
gray = cv2.cvtColor(distorted, cv2.COLOR_BGR2GRAY)
```

체커보드 검출을 위해 흑백 이미지로 변환한다.

```python
found, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, None)
```

체커보드 내부 코너를 찾는다.

```python
corners_refined = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
```

코너 위치를 더 정확하게 만든다.

```python
cv2.drawChessboardCorners(display, CHECKERBOARD, corners_refined, found)
```

찾은 코너를 화면에 그린다.

```python
cv2.imwrite(filename, distorted)
```

검출에 성공한 프레임을 저장한다.

### 캘리브레이션 코드 핵심

```python
objpoints.append(objp)
imgpoints.append(corners_refined)
```

실제 3D 기준점과 이미지 2D 검출점을 짝지어 저장한다.

```python
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
    objpoints, imgpoints, image_size, None, None
)
```

카메라 내부 파라미터와 왜곡 계수를 계산한다.

### 실시간 보정 코드 핵심

```python
mtx  = np.array(data['camera_matrix'], np.float64)
dist = np.array(data['dist_coeff'], np.float64)
```

YAML에서 파라미터를 읽는다.

```python
undist_map1, undist_map2 = cv2.initUndistortRectifyMap(
    mtx, dist, None, mtx, (w, h), cv2.CV_16SC2
)
```

왜곡 보정용 좌표 맵을 미리 계산한다.

```python
undistorted = cv2.remap(distorted, undist_map1, undist_map2, cv2.INTER_LINEAR)
```

매 프레임을 보정한다.

### 자주 나오는 함수 인자 추가 설명

#### `cv2.VideoCapture()`

```python
cap = cv2.VideoCapture(CAMERA_INDEX)
```

| 인자 | 예시 | 의미 |
|---|---|---|
| `CAMERA_INDEX` | `0` | 사용할 카메라 번호. 보통 노트북 내장/기본 웹캠은 `0` |

`cv2.VideoCapture(0)`은 0번 카메라 장치를 열겠다는 뜻이다. 카메라가 여러 개 연결되어 있으면 `1`, `2`처럼 번호를 바꿔 테스트할 수 있다.

```python
if not cap.isOpened():
    raise RuntimeError("카메라를 열 수 없습니다.")
```

`cap.isOpened()`는 카메라가 정상적으로 열렸는지 확인한다.

#### `cap.read()`

```python
ret, frame = cap.read()
```

| 반환값 | 의미 |
|---|---|
| `ret` | 프레임 읽기 성공 여부. 성공하면 `True` |
| `frame` | 카메라에서 읽어온 한 장의 이미지 |

`frame`은 NumPy 배열이다. 컬러 이미지라면 보통 다음 형태다.

```text
frame.shape = (height, width, 3)
```

마지막 `3`은 BGR 색상 채널을 의미한다. OpenCV는 기본 색상 순서가 RGB가 아니라 BGR이다.

#### `cv2.cvtColor()`

```python
gray = cv2.cvtColor(distorted, cv2.COLOR_BGR2GRAY)
```

| 인자 | 예시 | 의미 |
|---|---|---|
| `src` | `distorted` | 변환할 입력 이미지 |
| `code` | `cv2.COLOR_BGR2GRAY` | 색상 변환 방식 |

`cv2.COLOR_BGR2GRAY`는 BGR 컬러 이미지를 흑백 이미지로 바꾸겠다는 뜻이다. 체커보드 코너 검출은 색상보다 명암 차이가 중요하므로 흑백으로 바꿔서 처리한다.

#### `cv2.drawChessboardCorners()`

```python
cv2.drawChessboardCorners(display, CHECKERBOARD, corners_refined, found)
```

| 인자 | 예시 | 의미 |
|---|---|---|
| `image` | `display` | 코너를 그릴 이미지 |
| `patternSize` | `CHECKERBOARD` | 내부 교차점 개수 |
| `corners` | `corners_refined` | 그릴 코너 좌표들 |
| `patternWasFound` | `found` | 코너 검출 성공 여부 |

이 함수는 계산 결과를 바꾸는 함수가 아니라, 사람이 확인할 수 있도록 이미지 위에 코너 표시를 그려주는 시각화 함수다.

#### `cv2.putText()`

```python
cv2.putText(display, status_text, (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
```

| 인자 | 예시 | 의미 |
|---|---|---|
| `img` | `display` | 글자를 넣을 이미지 |
| `text` | `status_text` | 표시할 문자열 |
| `org` | `(10, 30)` | 글자가 시작될 위치 `(x, y)` |
| `fontFace` | `cv2.FONT_HERSHEY_SIMPLEX` | 글꼴 |
| `fontScale` | `0.7` | 글자 크기 |
| `color` | `(0, 255, 0)` | 글자 색상. OpenCV는 BGR 순서 |
| `thickness` | `2` | 글자 두께 |

색상 `(0, 255, 0)`은 RGB가 아니라 BGR 기준이므로 초록색이다.

#### `cv2.imshow()`와 `cv2.waitKey()`

```python
cv2.imshow("Calibration Image Capture", show)
key = cv2.waitKey(1) & 0xFF
```

`cv2.imshow()`:

| 인자 | 예시 | 의미 |
|---|---|---|
| `winname` | `"Calibration Image Capture"` | 창 이름 |
| `mat` | `show` | 화면에 보여줄 이미지 |

`cv2.waitKey()`:

| 인자 | 예시 | 의미 |
|---|---|---|
| `delay` | `1` | 키 입력을 기다릴 시간. 단위는 ms |

`cv2.waitKey(1)`은 1ms 동안 키 입력을 확인하고 넘어간다. 실시간 영상 루프에서는 이 값이 너무 크면 화면이 느려질 수 있다.

```python
key = cv2.waitKey(1) & 0xFF
```

`& 0xFF`는 키 코드의 하위 8비트만 남기는 처리다. 운영체제나 OpenCV 버전에 따라 키 코드에 추가 비트가 붙을 수 있어서, `ord('q')` 같은 값과 안정적으로 비교하려고 사용한다.

#### `cv2.imwrite()`

```python
cv2.imwrite(filename, distorted)
```

| 인자 | 예시 | 의미 |
|---|---|---|
| `filename` | `"calib_images/calib_001.jpg"` | 저장할 파일 경로 |
| `img` | `distorted` | 저장할 이미지 배열 |

반환값은 저장 성공 여부다.

```python
ok = cv2.imwrite(filename, distorted)
```

`ok == True`이면 저장 성공, `False`이면 저장 실패다. 실습 코드에서는 간단히 저장만 하지만, 실제 프로젝트에서는 반환값을 확인하는 것이 좋다.

#### `cv2.remap()`에서 `borderMode`와 `borderValue`

이미지 수집 코드의 합성 왜곡 부분에는 다음 코드가 나온다.

```python
distorted = cv2.remap(
    frame,
    dist_map_x,
    dist_map_y,
    cv2.INTER_LINEAR,
    borderMode=cv2.BORDER_CONSTANT,
    borderValue=0
)
```

| 인자 | 의미 |
|---|---|
| `frame` | 원본 프레임 |
| `dist_map_x` | x 방향 좌표 맵 |
| `dist_map_y` | y 방향 좌표 맵 |
| `cv2.INTER_LINEAR` | 선형 보간 |
| `borderMode=cv2.BORDER_CONSTANT` | 이미지 밖 영역을 고정 색으로 채움 |
| `borderValue=0` | 이미지 밖 영역을 검정색으로 채움 |

왜곡을 적용하거나 보정하면 어떤 픽셀은 원본 이미지 바깥 좌표를 참조하게 된다. 이때 바깥 영역을 어떻게 처리할지 정하는 옵션이 `borderMode`다.

#### `np.meshgrid()`

합성 왜곡 맵을 만들 때 다음 코드가 나온다.

```python
_ug, _vg = np.meshgrid(
    np.arange(_fw, dtype=np.float64),
    np.arange(_fh, dtype=np.float64)
)
```

| 인자 | 의미 |
|---|---|
| `np.arange(_fw)` | x 좌표 0부터 width-1까지 생성 |
| `np.arange(_fh)` | y 좌표 0부터 height-1까지 생성 |

`np.meshgrid()`는 이미지의 모든 픽셀 좌표 격자를 만든다.

예를 들어 이미지가 3x2라면 개념적으로 다음과 같다.

```text
u 좌표:
0 1 2
0 1 2

v 좌표:
0 0 0
1 1 1
```

이렇게 모든 픽셀 위치에 대해 왜곡 전/후 좌표를 계산하기 위해 사용한다.

#### `np.hstack()`

```python
show = np.hstack([label_orig, display])
```

| 인자 | 의미 |
|---|---|
| `[label_orig, display]` | 가로로 이어 붙일 이미지 목록 |

`np.hstack()`은 이미지를 좌우로 붙인다. 단, 두 이미지의 높이와 채널 수가 같아야 한다.

```text
[원본 이미지] [왜곡 이미지]
```

실시간 보정 코드에서도 왜곡 전/후 비교를 위해 사용한다.

```python
cv2.imshow("Live Undistort", np.hstack([distorted, undistorted]))
```

#### `yaml.safe_load()`와 `yaml.dump()`

저장:

```python
yaml.dump(data, f)
```

| 인자 | 의미 |
|---|---|
| `data` | 저장할 Python 딕셔너리 |
| `f` | 열린 파일 객체 |

불러오기:

```python
data = yaml.safe_load(f)
```

| 인자 | 의미 |
|---|---|
| `f` | 읽을 YAML 파일 객체 |

`safe_load()`는 YAML 파일을 Python 딕셔너리로 읽는다. 일반적인 설정 파일을 읽을 때는 `yaml.load()`보다 `safe_load()`를 사용하는 것이 안전하다.

#### 직접 만든 함수 `save_calibration_yaml()`

```python
def save_calibration_yaml(mtx, dist, filepath="camera_info.yaml"):
```

| 인자 | 의미 |
|---|---|
| `mtx` | `cv2.calibrateCamera()`로 구한 카메라 행렬 |
| `dist` | `cv2.calibrateCamera()`로 구한 왜곡 계수 |
| `filepath` | 저장할 YAML 파일 경로. 기본값은 `camera_info.yaml` |

`mtx`와 `dist`는 NumPy 배열이므로 YAML에 바로 저장하기 불편하다. 그래서 `.tolist()`로 Python 리스트로 바꿔 저장한다.

```python
'camera_matrix': mtx.tolist()
'dist_coeff': dist.tolist()
```

#### 직접 만든 함수 `load_calibration_yaml()`

```python
def load_calibration_yaml(filepath="camera_info.yaml"):
```

| 인자 | 의미 |
|---|---|
| `filepath` | 읽어올 YAML 파일 경로 |

YAML에서 읽어온 리스트는 다시 NumPy 배열로 바꿔야 OpenCV 함수에 넣기 좋다.

```python
mtx  = np.array(data['camera_matrix'], np.float64)
dist = np.array(data['dist_coeff'], np.float64)
```

---

## 17. 좋은 캘리브레이션을 위한 체크리스트

- [ ] 체커보드를 평평하고 단단한 판에 붙였는가?
- [ ] 조명이 균일하고 그림자나 반사가 심하지 않은가?
- [ ] 체커보드 내부 교차점 수를 정확히 입력했는가?
- [ ] 촬영 중 해상도, 줌, 초점이 바뀌지 않았는가?
- [ ] 최소 10~20장 이상 촬영했는가?
- [ ] 체커보드를 다양한 각도로 기울였는가?
- [ ] 가까운 거리와 먼 거리를 모두 포함했는가?
- [ ] 이미지 중앙뿐 아니라 가장자리와 모서리도 촬영했는가?
- [ ] 흐릿하거나 흔들린 이미지를 제거했는가?
- [ ] 재투영 오차가 1px 이하인지 확인했는가?

---

## 18. 한 줄 요약

카메라 캘리브레이션은 **실제 렌즈 카메라를 수학적으로 다루기 쉬운 핀홀 카메라 모델에 맞추기 위해, 카메라 행렬 `K`와 왜곡 계수 `dist`를 구하는 과정**이다.

캘리브레이션을 잘해야 이미지 속 픽셀을 실제 3D 공간의 방향과 위치로 신뢰성 있게 연결할 수 있다.
