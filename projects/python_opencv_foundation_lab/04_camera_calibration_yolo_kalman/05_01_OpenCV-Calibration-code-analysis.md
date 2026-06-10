# 05_01_OpenCV-Calibration.ipynb 마지막 코드 셀 상세 분석

이 문서는 `05_01_OpenCV-Calibration.ipynb`의 마지막 코드 셀을 처음 보는 사람도 천천히 읽으면 이해할 수 있도록 풀어 쓴 분석 문서다.

이 코드는 한마디로 말하면 다음 일을 한다.

```text
체커보드 이미지 여러 장 준비
        |
        v
이미지마다 체커보드 내부 코너 검출
        |
        v
3D 체커보드 좌표와 2D 이미지 좌표를 OpenCV에 전달
        |
        v
카메라 행렬과 렌즈 왜곡 계수 계산
        |
        v
결과를 YAML로 저장
        |
        v
실시간 보정에 쓸 remap용 map1, map2를 NPZ로 저장
```

---

## 1. 이 코드의 목적

카메라로 촬영한 이미지는 보통 완벽한 직선 세계가 아니다. 렌즈 때문에 가장자리 쪽이 휘어 보일 수 있다.

예를 들어 실제로는 곧은 선인데 이미지에서는 살짝 휘어 보이는 현상이 생긴다.

```text
실제 직선:
--------------------

렌즈 왜곡이 있는 이미지:
)------------------(
```

카메라 캘리브레이션은 이런 렌즈 왜곡을 수학적으로 구해서, 나중에 이미지를 다시 곧게 펴기 위한 준비 과정이다.

이 코드가 최종적으로 만드는 핵심 파일은 두 개다.

| 파일 | 역할 |
|---|---|
| `camera_calibration.yml` | 원본 캘리브레이션 결과. 카메라 행렬과 왜곡 계수가 저장된다. |
| `undistort_maps_640x480_alpha0.npz` | 실시간 보정용 캐시. `cv2.remap()`에 바로 넣을 수 있는 `map1`, `map2`가 저장된다. |

`camera_calibration.yml`은 원본 데이터에 가깝고, `undistort_maps_640x480_alpha0.npz`는 빠른 실행을 위한 캐시에 가깝다.

---

## 2. 먼저 알아야 할 용어

### 2.1 체커보드 내부 코너

OpenCV에서 `CHECKERBOARD = (9, 6)`이라고 쓰면, 이것은 체커보드의 칸 수가 아니다.

의미는 다음과 같다.

```python
CHECKERBOARD = (9, 6)
```

```text
가로 내부 교차점 9개
세로 내부 교차점 6개
```

즉, 검은 칸과 흰 칸이 만나는 안쪽 교차점 개수다.

체커보드가 실제로 `10 x 7`칸이면 내부 코너는 보통 `9 x 6`개다.

```text
칸 수:        10 x 7
내부 코너 수:  9 x 6
```

이 값을 잘못 넣으면 코너 검출이 실패하거나, 운 좋게 검출되더라도 캘리브레이션 결과가 틀어질 수 있다.

### 2.2 Object Points

`object points`는 실제 세계에서 체커보드 코너가 어디에 있는지를 나타내는 3D 좌표다.

체커보드는 평평한 판이므로 보통 `z = 0`으로 둔다.

예를 들어 한 칸 크기가 `0.025m`라면, 첫 줄의 코너 좌표는 이런 식이다.

```text
(0.000, 0.000, 0)
(0.025, 0.000, 0)
(0.050, 0.000, 0)
(0.075, 0.000, 0)
...
```

여기서 단위는 코드에서 정한 `SQUARE_SIZE`에 따라 결정된다.

### 2.3 Image Points

`image points`는 실제 이미지 안에서 검출된 체커보드 코너의 2D 픽셀 좌표다.

예를 들면 이런 값들이다.

```text
(312.4, 228.7)
(345.1, 229.2)
(377.9, 230.0)
...
```

카메라 캘리브레이션은 결국 다음 대응 관계를 이용한다.

```text
실제 체커보드의 3D 좌표  <->  이미지에서 보이는 2D 픽셀 좌표
```

OpenCV는 이 대응 관계를 여러 이미지에서 모아서 카메라의 특성을 추정한다.

### 2.4 Camera Matrix

`camera_matrix`는 카메라 내부 파라미터를 담은 3x3 행렬이다.

형태는 다음과 같다.

```text
[ fx   0  cx ]
[  0  fy  cy ]
[  0   0   1 ]
```

각 값의 의미는 다음과 같다.

| 값 | 의미 |
|---|---|
| `fx` | x 방향 초점 거리. 픽셀 단위다. |
| `fy` | y 방향 초점 거리. 픽셀 단위다. |
| `cx` | 이미지 중심점의 x 좌표에 가까운 값이다. |
| `cy` | 이미지 중심점의 y 좌표에 가까운 값이다. |

현재 실행 결과에서는 다음 값이 나왔다.

```text
fx = 807.8398
fy = 805.7470
cx = 320.0486
cy = 240.2473
```

이미지 크기가 `640 x 480`이므로 중심은 대략 `(320, 240)`이다. 따라서 `cx`, `cy`가 이미지 중앙 근처에 있는 것은 자연스럽다.

### 2.5 Distortion Coefficients

`dist_coeffs`는 렌즈 왜곡 계수다.

현재 코드는 OpenCV 기본 모델의 5개 계수를 사용한다.

```text
[k1, k2, p1, p2, k3]
```

각 값은 대략 다음 의미를 가진다.

| 값 | 의미 |
|---|---|
| `k1`, `k2`, `k3` | 방사 왜곡. 중심에서 멀어질수록 생기는 휘어짐과 관련 있다. |
| `p1`, `p2` | 접선 왜곡. 렌즈와 이미지 센서가 완전히 평행하지 않을 때 생기는 왜곡과 관련 있다. |

현재 실행 결과는 다음과 같다.

```text
[-2.23036330, 3.30283911, 0.01283524, 0.00035400, 23.62763735]
```

`k3`가 꽤 큰 편이다. 만약 실습에서 일부러 강한 합성 왜곡을 넣은 이미지를 사용했다면 이상하지 않을 수 있다. 하지만 실제 카메라에서 얻은 값이라면 촬영 이미지 품질, 체커보드 크기 설정, 내부 코너 개수 설정을 다시 확인하는 것이 좋다.

### 2.6 Reprojection Error

재투영 오차는 캘리브레이션 결과가 얼마나 잘 맞는지 확인하는 값이다.

개념은 이렇다.

```text
1. 실제 체커보드의 3D 코너 좌표를 알고 있다.
2. 캘리브레이션 결과로 얻은 camera_matrix와 dist_coeffs도 있다.
3. 이 값들을 이용해서 3D 코너를 다시 이미지 위로 투영한다.
4. 다시 투영한 점과 실제 검출된 이미지 코너 점의 차이를 계산한다.
```

차이가 작을수록 캘리브레이션이 잘 된 것이다.

단, 이 코드의 `Mean reproj error`와 OpenCV의 `RMS error`는 계산 방식이 완전히 같지 않다.

`cv2.calibrateCamera()`가 반환하는 `RMS error`는 OpenCV 내부 기준의 전체 RMS 오차다.

반면 코드의 `compute_reprojection_errors()`에서는 이미지별로 다음처럼 계산한다.

```python
error = cv2.norm(imgpoints[i], projected_points, cv2.NORM_L2) / len(projected_points)
```

이 값은 이미지 하나에 대해 전체 코너 차이의 L2 norm을 코너 개수로 나눈 값이다. 그래서 숫자의 의미는 비슷하지만, OpenCV의 RMS 값과 1:1로 같은 값은 아니다.

---

## 3. 코드 전체 구조

마지막 코드 셀은 크게 16개 구역으로 나뉘어 있다.

| 번호 | 구역 | 역할 |
|---|---|---|
| 1 | 사용자 설정 | 체커보드 크기, 이미지 경로, 저장 파일 경로, alpha 값 설정 |
| 2 | 3D 기준 좌표 생성 | 체커보드의 실제 3D 좌표 생성 |
| 3 | 코너 검출 | 이미지에서 체커보드 내부 코너 찾기 |
| 4 | 점 수집 | 여러 이미지에서 object points와 image points 수집 |
| 5 | 캘리브레이션 수행 | `cv2.calibrateCamera()` 실행 |
| 6 | 재투영 오차 계산 | 이미지별 오차 계산 |
| 7 | outlier 제거 후 재캘리브레이션 | 오차가 큰 이미지 제거 후 다시 보정 |
| 8 | YAML 저장/로드 | 원본 캘리브레이션 결과 저장과 로드 |
| 9 | remap용 map 생성 | `map1`, `map2` 생성 |
| 10 | NPZ 저장/로드 | 실시간 보정용 map 캐시 저장과 로드 |
| 11 | dat 방식 참고 | 예전 방식과 NPZ 방식 비교 설명 |
| 12 | 이미지 보정 | `cv2.remap()`으로 이미지 왜곡 보정 |
| 13 | 전체 캘리브레이션 실행 | 캘리브레이션 전체 흐름 실행 |
| 14 | YAML 기반 테스트 | YAML에서 읽어 테스트 이미지 보정 |
| 15 | NPZ 기반 테스트 | NPZ map 캐시로 테스트 이미지 보정 |
| 16 | main | 실제 실행 순서 지정 |

---

## 4. 사용자 설정 영역 분석

### 4.1 CHECKERBOARD

```python
CHECKERBOARD = (9, 6)
```

이 값은 체커보드 내부 코너 개수다.

주의할 점은 주석에 다음 설명이 있다는 것이다.

```text
실제 보드가 9칸 x 6칸이면 내부 코너는 8 x 5이다.
```

따라서 지금 사용하는 실제 보드가 `10 x 7`칸인지, 내부 코너가 정말 `9 x 6`인지 확인해야 한다.

만약 실제 내부 코너가 `8 x 5`인데 코드가 `(9, 6)`으로 되어 있으면 보정 결과가 맞지 않는다.

### 4.2 SQUARE_SIZE

```python
SQUARE_SIZE = 0.025
```

체커보드 한 칸의 실제 크기다.

여기서는 `0.025m`, 즉 `25mm`로 설정되어 있다.

왜 실제 크기가 필요할까?

왜곡 보정만 할 때는 상대적인 크기만 있어도 어느 정도 된다. 하지만 `tvecs`, 즉 카메라와 체커보드 사이의 실제 거리나 위치를 해석하려면 실제 단위가 필요하다.

따라서 실제 체커보드 한 칸이 30mm라면 다음처럼 바꿔야 한다.

```python
SQUARE_SIZE = 0.030
```

### 4.3 CALIB_IMAGE_GLOB

```python
CALIB_IMAGE_GLOB = "/home/jaeholee/work/calib_images/*.*"
```

캘리브레이션 이미지들을 찾는 경로다.

현재는 절대 경로를 사용한다.

장점은 어디서 실행해도 같은 폴더를 바라본다는 점이다.

단점은 다른 컴퓨터나 다른 사용자 계정에서는 경로가 깨질 수 있다는 점이다.

프로젝트 안에서만 돌릴 목적이라면 상대 경로를 쓰는 것도 방법이다.

```python
CALIB_IMAGE_GLOB = "./calib_images/*.*"
```

다만 노트북에서 상대 경로는 노트북 파일 위치가 아니라 Jupyter가 실행된 현재 작업 디렉터리 기준일 수 있으므로 주의해야 한다.

### 4.4 저장 경로

```python
CALIB_YAML_PATH = "camera_calibration.yml"
MAP_CACHE_NPZ_PATH = "undistort_maps_640x480_alpha0.npz"
TEST_IMAGE_PATH = "./test.jpg"
OUTPUT_IMAGE_PATH = "./test_undistorted.jpg"
```

이 경로들은 상대 경로다.

즉, 노트북을 실행하는 현재 작업 디렉터리에 파일이 저장된다.

현재 `prac` 폴더에는 다음 파일들이 있다.

```text
camera_calibration.yml
undistort_maps_640x480_alpha0.npz
test.jpg
test_undistorted.jpg
```

그래서 현재는 `prac` 폴더 기준으로 실행된 것으로 보인다.

### 4.5 ALPHA

```python
ALPHA = 0.0
```

`alpha`는 보정 후 시야를 얼마나 유지할지 정하는 값이다.

| 값 | 결과 |
|---|---|
| `0.0` | 검은 영역을 최대한 제거한다. 대신 가장자리가 조금 잘릴 수 있다. |
| `1.0` | 원래 시야를 최대한 유지한다. 대신 가장자리에 검은 영역이 생길 수 있다. |
| `0.3` | 둘 사이의 절충안이다. |

실시간 마커 인식이나 로봇 비전에서는 검은 영역이 적은 편이 다루기 쉬워서 `0.0`이나 `0.3`을 자주 쓴다.

### 4.6 USE_OUTLIER_FILTER

```python
USE_OUTLIER_FILTER = True
```

재투영 오차가 유난히 큰 이미지를 제거하고 다시 캘리브레이션할지 결정한다.

현재는 `True`이므로 다음 흐름으로 동작한다.

```text
1차 캘리브레이션
        |
        v
이미지별 재투영 오차 계산
        |
        v
평균 + 2 * 표준편차보다 큰 이미지 제거
        |
        v
남은 이미지로 2차 캘리브레이션
```

---

## 5. 3D 기준 좌표 생성 함수

```python
def create_object_points(pattern_size, square_size):
```

이 함수는 체커보드 코너의 실제 3D 좌표를 만든다.

핵심 코드는 다음이다.

```python
cols, rows = pattern_size

objp = np.zeros((cols * rows, 3), np.float32)
objp[:, :2] = np.mgrid[0:cols, 0:rows].T.reshape(-1, 2)
objp *= square_size
```

예를 들어 `pattern_size = (9, 6)`이면 총 코너 수는 `9 * 6 = 54`개다.

처음에는 이런 좌표가 만들어진다.

```text
(0, 0, 0)
(1, 0, 0)
(2, 0, 0)
...
(8, 0, 0)
(0, 1, 0)
(1, 1, 0)
...
```

여기에 `square_size = 0.025`를 곱하면 실제 meter 단위 좌표가 된다.

```text
(0.000, 0.000, 0)
(0.025, 0.000, 0)
(0.050, 0.000, 0)
...
```

중요한 점은 이 좌표가 모든 이미지에서 동일하다는 것이다.

체커보드 자체의 실제 모양은 변하지 않기 때문이다. 이미지마다 달라지는 것은 카메라에서 보이는 위치와 각도다.

---

## 6. 체커보드 코너 검출 함수

```python
def find_chessboard_corners(gray, pattern_size):
```

이 함수는 그레이스케일 이미지에서 체커보드 내부 코너를 찾는다.

### 6.1 먼저 findChessboardCornersSB 사용

```python
if hasattr(cv2, "findChessboardCornersSB"):
    sb_flags = cv2.CALIB_CB_NORMALIZE_IMAGE

    ret, corners = cv2.findChessboardCornersSB(
        gray,
        pattern_size,
        flags=sb_flags
    )

    if ret:
        return True, corners.astype(np.float32)
```

`findChessboardCornersSB()`는 비교적 최신 방식이다.

일반적으로 기존 `findChessboardCorners()`보다 조명 변화나 각도 변화에 강한 경우가 있다.

성공하면 바로 코너 좌표를 반환한다.

### 6.2 실패하면 기존 방식 사용

```python
ret, corners = cv2.findChessboardCorners(
    gray,
    pattern_size,
    classic_flags
)
```

`findChessboardCornersSB()`가 실패하면 기존 방식인 `findChessboardCorners()`를 사용한다.

기존 방식이 성공하면 `cornerSubPix()`로 코너 위치를 더 정밀하게 다듬는다.

```python
corners = cv2.cornerSubPix(
    gray,
    corners,
    winSize=(11, 11),
    zeroZone=(-1, -1),
    criteria=criteria
)
```

`cornerSubPix()`는 픽셀보다 더 작은 단위로 코너 위치를 보정한다.

캘리브레이션은 코너 좌표 정확도에 민감하므로 이 단계가 중요하다.

---

## 7. 여러 이미지에서 점 수집

```python
def collect_calibration_points(image_glob, pattern_size, square_size):
```

이 함수는 캘리브레이션 이미지들을 하나씩 읽고, 성공한 이미지에서 다음 값을 모은다.

| 목록 | 들어가는 값 |
|---|---|
| `objpoints` | 실제 체커보드 3D 좌표 |
| `imgpoints` | 이미지에서 검출한 2D 코너 좌표 |
| `valid_image_paths` | 검출에 성공한 이미지 경로 |

### 7.1 이미지 목록 읽기

```python
image_paths = sorted(glob.glob(image_glob))
```

`CALIB_IMAGE_GLOB`에 맞는 모든 파일을 가져온다.

현재 설정에서는 다음 폴더를 본다.

```text
/home/jaeholee/work/calib_images/
```

### 7.2 이미지 크기 검사

```python
current_size = gray.shape[::-1]

if image_size is None:
    image_size = current_size
elif current_size != image_size:
    print(f"[SKIP] 이미지 크기 다름: {path}, size={current_size}, expected={image_size}")
    continue
```

캘리브레이션 이미지는 모두 같은 해상도여야 한다.

예를 들어 어떤 이미지는 `640 x 480`, 다른 이미지는 `1280 x 720`이면 하나의 캘리브레이션에 섞으면 안 된다.

그래서 첫 이미지의 크기를 기준으로 잡고, 이후 이미지가 다르면 건너뛴다.

### 7.3 코너 검출 실패 이미지는 제외

```python
ret, corners = find_chessboard_corners(gray, pattern_size)

if not ret:
    print(f"[SKIP] 체크보드 코너 검출 실패: {os.path.basename(path)}")
    continue
```

체커보드가 흐릿하거나 너무 기울어져 있거나 일부가 잘려 있으면 코너 검출이 실패할 수 있다.

그런 이미지는 캘리브레이션에 넣지 않는다.

### 7.4 성공 이미지가 너무 적으면 중단

```python
if len(objpoints) < 10:
    raise RuntimeError(...)
```

이미지가 너무 적으면 카메라 파라미터를 안정적으로 구하기 어렵다.

코드에서는 최소 10장을 요구한다. 실습에서는 15장 이상, 가능하면 20~30장 정도가 더 좋다.

---

## 8. 카메라 캘리브레이션 수행

```python
def calibrate_camera(objpoints, imgpoints, image_size):
```

핵심은 이 함수 호출이다.

```python
rms, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
    objpoints,
    imgpoints,
    image_size,
    None,
    None
)
```

OpenCV가 `objpoints`와 `imgpoints`의 대응 관계를 보고 다음 값을 계산한다.

| 반환값 | 의미 |
|---|---|
| `rms` | 전체 재투영 RMS 오차 |
| `camera_matrix` | 카메라 내부 파라미터 |
| `dist_coeffs` | 렌즈 왜곡 계수 |
| `rvecs` | 각 이미지에서 체커보드의 회전 정보 |
| `tvecs` | 각 이미지에서 체커보드의 이동 정보 |

`rvecs`, `tvecs`는 이미지마다 하나씩 나온다.

예를 들어 캘리브레이션에 15장을 사용했다면 `rvecs` 15개, `tvecs` 15개가 생긴다.

---

## 9. 재투영 오차 계산

```python
def compute_reprojection_errors(objpoints, imgpoints, rvecs, tvecs, camera_matrix, dist_coeffs):
```

이 함수는 이미지별 오차를 계산한다.

핵심 코드는 다음이다.

```python
projected_points, _ = cv2.projectPoints(
    objpoints[i],
    rvecs[i],
    tvecs[i],
    camera_matrix,
    dist_coeffs
)
```

`cv2.projectPoints()`는 3D 점을 다시 이미지의 2D 픽셀 좌표로 투영한다.

그다음 실제 검출된 코너와 다시 투영된 코너 사이의 차이를 계산한다.

```python
error = cv2.norm(
    imgpoints[i],
    projected_points,
    cv2.NORM_L2
) / len(projected_points)
```

오차가 큰 이미지는 보통 다음 문제가 있을 수 있다.

- 체커보드가 흔들리거나 흐릿하게 찍힘
- 조명 반사가 심함
- 체커보드 일부가 잘림
- 코너 검출이 엉뚱한 위치에 잡힘
- 너무 정면 사진만 있거나, 반대로 너무 극단적인 각도에서 찍힘

---

## 10. Outlier 제거 후 재캘리브레이션

```python
def filter_outliers_and_recalibrate(objpoints, imgpoints, image_paths, image_size):
```

이 함수는 다음 흐름으로 동작한다.

```text
1. 전체 이미지로 1차 캘리브레이션
2. 이미지별 재투영 오차 계산
3. 평균 + 2 * 표준편차를 threshold로 설정
4. threshold보다 큰 이미지를 제거
5. 남은 이미지로 2차 캘리브레이션
```

현재 실행 결과는 다음과 같다.

```text
1차 RMS error         : 0.5157862285898495
1차 Mean reproj error : 0.06463043640727667
1차 Std reproj error  : 0.02737671828722044
Outlier threshold     : 0.11938387298171754
```

이미지별 결과에서는 1장이 제거되었다.

```text
[DROP] calib_20260429_114226_642275.jpg, reproj_error=0.146520
```

나머지 15장으로 다시 캘리브레이션한 결과는 다음과 같다.

```text
2차 RMS error         : 0.5605397140790048
2차 Mean reproj error : 0.070724010183044
2차 Used images       : 15
```

여기서 중요한 점이 있다.

2차 RMS가 1차 RMS보다 커졌다.

```text
1차 RMS: 0.5158
2차 RMS: 0.5605
```

즉, outlier를 제거했는데 OpenCV RMS 기준으로는 결과가 더 좋아지지 않았다.

현재 코드는 이런 경우에도 무조건 2차 결과를 최종 결과로 사용한다. 이 부분은 개선 여지가 있다.

더 안전한 방식은 다음과 같다.

```text
2차 결과가 1차보다 좋아졌을 때만 2차 결과 채택
그렇지 않으면 1차 결과 유지
```

또는 RMS뿐 아니라 평균 재투영 오차, 이미지 구성의 다양성, 실제 undistort 결과를 함께 보고 판단하는 것이 좋다.

---

## 11. YAML 저장과 로드

### 11.1 저장 함수

```python
def save_calibration_to_yaml(path, camera_matrix, dist_coeffs, image_size, square_size, pattern_size, rms):
```

이 함수는 원본 캘리브레이션 결과를 YAML 파일로 저장한다.

저장되는 값은 다음과 같다.

```text
image_width
image_height
checkerboard_cols
checkerboard_rows
square_size
rms
camera_matrix
dist_coeffs
```

현재 `camera_calibration.yml`에는 다음 값이 저장되어 있다.

```text
image_width: 640
image_height: 480
checkerboard_cols: 9
checkerboard_rows: 6
square_size: 0.025
rms: 0.5605397140790048
```

카메라 행렬은 다음과 같다.

```text
[807.83983537,   0.        , 320.04864803]
[  0.        , 805.74702650, 240.24734991]
[  0.        ,   0.        ,   1.        ]
```

왜곡 계수는 다음과 같다.

```text
[-2.23036330, 3.30283911, 0.01283524, 0.00035400, 23.62763735]
```

### 11.2 로드 함수

```python
def load_calibration_from_yaml(path):
```

이 함수는 YAML에서 다음 값을 읽는다.

```text
image_width
image_height
camera_matrix
dist_coeffs
```

이 값만 있으면 나중에 `map1`, `map2`를 다시 만들 수 있다.

즉, YAML 파일은 보정 결과의 원본 저장소 역할을 한다.

---

## 12. remap용 map 생성

```python
def create_undistort_maps(camera_matrix, dist_coeffs, image_size, alpha):
```

이 함수는 왜곡 보정용 `map1`, `map2`를 만든다.

OpenCV에서 이미지를 보정하는 방법은 크게 두 가지로 생각할 수 있다.

### 12.1 cv2.undistort()

```python
undistorted = cv2.undistort(image, camera_matrix, dist_coeffs)
```

간단하다.

하지만 매번 보정 좌표를 계산해야 하므로 실시간 영상 처리에서는 불리할 수 있다.

### 12.2 initUndistortRectifyMap() + remap()

```python
map1, map2 = cv2.initUndistortRectifyMap(...)
undistorted = cv2.remap(frame, map1, map2, cv2.INTER_LINEAR)
```

이 방식은 처음에 보정 좌표표를 미리 계산해 둔다.

그다음 매 프레임에서는 `cv2.remap()`만 수행한다.

라즈베리파이처럼 성능이 제한된 환경에서는 이 방식이 더 적합하다.

### 12.3 getOptimalNewCameraMatrix()

```python
new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(
    camera_matrix,
    dist_coeffs,
    image_size,
    alpha
)
```

왜곡을 보정하면 이미지 가장자리에 검은 영역이 생길 수 있다.

`getOptimalNewCameraMatrix()`는 이 문제를 어떻게 처리할지 정하는 새 카메라 행렬을 만든다.

`alpha = 0.0`이면 검은 영역을 줄이고, `alpha = 1.0`이면 원래 시야를 더 많이 유지한다.

현재 NPZ 안의 ROI는 다음과 같다.

```text
roi = (0, 0, 639, 479)
```

거의 전체 이미지 영역을 사용할 수 있다는 뜻이다.

---

## 13. NPZ map 캐시 저장과 로드

### 13.1 저장 함수

```python
def save_undistort_maps_to_npz(path, map1, map2, image_size, alpha, new_camera_matrix, roi):
```

이 함수는 다음 데이터를 `.npz` 파일에 저장한다.

```text
map1
map2
image_width
image_height
alpha
new_camera_matrix
roi
```

현재 파일명은 다음이다.

```text
undistort_maps_640x480_alpha0.npz
```

파일명에서 알 수 있듯이 이 map은 `640 x 480` 해상도와 `alpha = 0.0` 조건에 묶여 있다.

즉, 카메라 해상도를 `1280 x 720`으로 바꾸면 이 파일을 그대로 쓰면 안 된다.

### 13.2 로드 함수

```python
def load_undistort_maps_from_npz(path):
```

NPZ 파일에서 `map1`, `map2`를 읽는다.

라즈베리파이 실시간 코드에서는 보통 다음처럼 사용한다.

```python
data = np.load("undistort_maps_640x480_alpha0.npz")
map1 = data["map1"]
map2 = data["map2"]

frame_undistorted = cv2.remap(frame, map1, map2, cv2.INTER_LINEAR)
```

이 방식의 장점은 실행 중에 `camera_matrix`에서 map을 다시 계산하지 않아도 된다는 것이다.

---

## 14. dat 방식과 NPZ 방식

코드에는 `save_undistort_maps_dat_style_example_comment_only()`라는 함수가 있다.

이 함수는 실제 저장을 하지 않고 설명만 담고 있다.

예전 예제에서는 이런 방식을 볼 수 있다.

```python
f = open("calib.dat", "wb")
np.save(f, map1)
np.save(f, map2)
f.close()
```

읽을 때도 같은 순서를 지켜야 한다.

```python
f = open("calib.dat", "rb")
map1 = np.load(f)
map2 = np.load(f)
f.close()
```

이 방식은 동작하지만 순서에 의존한다.

반면 `np.savez()`는 이름을 붙여 저장한다.

```python
np.savez(
    path,
    map1=map1,
    map2=map2,
    image_width=...,
    image_height=...,
    alpha=...
)
```

그래서 `map1`, `map2`, `alpha`, `image_width` 같은 값을 이름으로 꺼낼 수 있다.

이 코드에서는 NPZ 방식이 더 안전하고 관리하기 쉽기 때문에 NPZ를 사용한다.

---

## 15. 이미지 보정 함수

```python
def undistort_image_with_remap(image, map1, map2, roi=None):
```

이 함수는 `cv2.remap()`을 이용해 이미지를 보정한다.

```python
undistorted = cv2.remap(
    image,
    map1,
    map2,
    interpolation=cv2.INTER_LINEAR
)
```

`map1`, `map2`는 출력 이미지의 각 픽셀이 원본 이미지의 어느 위치에서 값을 가져와야 하는지를 알려주는 지도 같은 것이다.

`INTER_LINEAR`는 보간 방식이다.

원본 좌표가 정확히 정수 픽셀이 아닐 수 있으므로 주변 픽셀을 섞어서 값을 만든다.

### ROI 처리

함수에는 `roi` 인자가 있다.

```python
if roi is not None:
    x, y, w, h = roi

    if w > 0 and h > 0:
        undistorted = undistorted[y:y + h, x:x + w]
```

ROI는 보정 후 유효한 이미지 영역이다.

`roi`를 넣으면 검은 영역을 잘라낼 수 있다.

하지만 현재 테스트 함수에서는 `roi=None`으로 호출하고 있다.

```python
undistorted = undistort_image_with_remap(
    image,
    map1,
    map2,
    roi=None
)
```

즉, 현재 코드는 보정된 전체 이미지를 저장하고, ROI로 자르지는 않는다.

---

## 16. 전체 캘리브레이션 실행 함수

```python
def run_calibration():
```

이 함수가 전체 파이프라인의 중심이다.

흐름은 다음과 같다.

```text
1. 캘리브레이션 이미지에서 코너 수집
2. 캘리브레이션 실행
3. 필요하면 outlier 제거 후 재캘리브레이션
4. 최종 결과 출력
5. YAML 저장
6. remap용 map1, map2 생성
7. NPZ 저장
```

핵심 부분은 다음이다.

```python
objpoints, imgpoints, valid_image_paths, image_size = collect_calibration_points(
    CALIB_IMAGE_GLOB,
    CHECKERBOARD,
    SQUARE_SIZE
)
```

이 단계에서 이미지별 코너 검출이 이루어진다.

그다음 outlier 필터를 사용할지 결정한다.

```python
if USE_OUTLIER_FILTER:
    rms, camera_matrix, dist_coeffs, rvecs, tvecs, errors, used_image_paths = filter_outliers_and_recalibrate(...)
else:
    rms, camera_matrix, dist_coeffs, rvecs, tvecs = calibrate_camera(...)
```

마지막으로 결과를 저장한다.

```python
save_calibration_to_yaml(...)
save_undistort_maps_to_npz(...)
```

---

## 17. YAML 기반 테스트 이미지 보정

```python
def run_undistort_test_from_yaml():
```

이 함수는 다음 흐름으로 동작한다.

```text
1. camera_calibration.yml 로드
2. test.jpg 로드
3. 테스트 이미지 해상도와 캘리브레이션 해상도 비교
4. YAML 값으로 map1, map2 새로 생성
5. test_undistorted.jpg 저장
```

이 방식의 장점은 `ALPHA` 값을 바꿔가며 테스트하기 쉽다는 점이다.

단점은 실행할 때마다 `map1`, `map2`를 다시 만든다는 점이다.

하지만 시작할 때 한 번만 만든다면 큰 문제는 아니다.

---

## 18. NPZ 기반 테스트 이미지 보정

```python
def run_undistort_test_from_npz():
```

이 함수는 다음 흐름으로 동작한다.

```text
1. undistort_maps_640x480_alpha0.npz 로드
2. test.jpg 로드
3. 테스트 이미지 해상도와 map 해상도 비교
4. cv2.remap()으로 보정
5. test_undistorted.jpg 저장
```

이 방식은 라즈베리파이 실시간 실행 구조와 가장 비슷하다.

실시간 카메라 코드에서는 매 프레임마다 다음 한 줄을 수행한다고 보면 된다.

```python
frame_undistorted = cv2.remap(frame, map1, map2, cv2.INTER_LINEAR)
```

---

## 19. main 실행부

마지막 부분은 다음과 같다.

```python
if __name__ == "__main__":
    run_calibration()

    # run_undistort_test_from_yaml()
    # run_undistort_test_from_npz()
```

현재 실제로 실행되는 것은 `run_calibration()`뿐이다.

테스트 이미지 보정 함수 두 개는 주석 처리되어 있다.

```python
# run_undistort_test_from_yaml()
# run_undistort_test_from_npz()
```

따라서 현재 코드 그대로 다시 실행하면 다음 파일은 갱신된다.

```text
camera_calibration.yml
undistort_maps_640x480_alpha0.npz
```

하지만 `test_undistorted.jpg`는 갱신되지 않는다.

노트북 출력에는 예전에 다음 메시지가 남아 있다.

```text
[SAVE] YAML 기반 보정 이미지 저장 완료: ./test_undistorted.jpg
```

하지만 현재 코드상으로는 해당 줄이 주석 처리되어 있으므로, 이것은 이전 실행 결과가 노트북에 남아 있는 것으로 보는 것이 맞다.

---

## 20. 현재 실행 결과 해석

현재 노트북 출력 기준으로 검출 결과는 다음과 같다.

```text
체커보드 검출 성공: 16장
outlier 제거: 1장
최종 사용 이미지: 15장
이미지 크기: 640 x 480
```

제거된 이미지는 다음이다.

```text
calib_20260429_114226_642275.jpg
```

최종 저장된 값은 다음과 같다.

```text
RMS error       : 0.5605397140790048
Mean reproj err : 0.070724010183044
```

카메라 행렬은 다음과 같다.

```text
[[807.83983537   0.         320.04864803]
 [  0.         805.7470265  240.24734991]
 [  0.           0.           1.        ]]
```

왜곡 계수는 다음과 같다.

```text
[-2.23036330e+00  3.30283911e+00  1.28352426e-02  3.54004916e-04
  2.36276374e+01]
```

### 20.1 좋은 점

- 이미지 16장에서 모두 체커보드 검출에 성공했다.
- 최종 이미지 수가 15장이므로 최소 기준은 넘는다.
- `cx`, `cy`가 이미지 중심 근처라서 카메라 행렬의 중심점은 자연스럽다.
- YAML과 NPZ를 둘 다 저장하므로, 원본 보정값과 실시간 캐시를 분리해 관리할 수 있다.

### 20.2 주의할 점

가장 중요한 주의점은 outlier 제거 후 RMS가 더 커졌다는 것이다.

```text
1차 RMS: 0.5158
2차 RMS: 0.5605
```

일반적으로 outlier 제거를 하는 이유는 결과를 더 좋게 만들기 위해서다.

그런데 현재 결과만 보면 RMS 기준으로는 더 좋아지지 않았다.

가능한 원인은 다음과 같다.

- 제거된 이미지가 실제로는 유용한 시야 정보를 갖고 있었을 수 있다.
- 전체 이미지 수가 많지 않아 1장을 제거한 영향이 컸을 수 있다.
- 평균 + 2표준편차 기준이 현재 데이터에는 적절하지 않았을 수 있다.
- RMS와 코드에서 계산한 이미지별 평균 reprojection error가 완전히 같은 기준이 아니기 때문에 판단이 엇갈릴 수 있다.

따라서 이 코드는 outlier 제거 결과를 무조건 채택하기보다, 개선 여부를 확인한 뒤 채택하도록 바꾸는 것이 좋다.

---

## 21. 실무적으로 개선하면 좋은 부분

### 21.1 2차 결과가 더 좋을 때만 채택

현재는 outlier 제거 후 이미지가 10장 이상이면 무조건 2차 결과를 사용한다.

더 안전한 로직은 다음과 같다.

```text
if rms2 <= rms:
    2차 결과 사용
else:
    1차 결과 유지
```

또는 `Mean reproj error`도 함께 비교할 수 있다.

```text
if rms2 <= rms and mean_error2 <= mean_error:
    2차 결과 사용
else:
    1차 결과 유지
```

### 21.2 체커보드 설정 재확인

현재 코드에는 다음 설정이 있다.

```python
CHECKERBOARD = (9, 6)
SQUARE_SIZE = 0.025
```

반드시 실제 보드가 다음 조건과 맞아야 한다.

```text
내부 코너: 9 x 6
한 칸 크기: 25mm
```

실제 보드가 다르면 결과는 신뢰하기 어렵다.

### 21.3 촬영 이미지 다양성 확보

캘리브레이션 이미지는 단순히 많이 찍는 것보다 다양하게 찍는 것이 중요하다.

좋은 촬영 조건은 다음과 같다.

- 체커보드가 이미지 중앙뿐 아니라 네 모서리 근처에도 나오게 찍기
- 정면 사진만 찍지 말고 약간씩 기울여 찍기
- 너무 멀리서 작게 찍지 않기
- 너무 가까워서 체커보드가 잘리지 않게 하기
- 흔들림과 반사를 피하기
- 같은 자세의 사진을 여러 장 반복해서 넣지 않기

### 21.4 경로 관리

현재 캘리브레이션 이미지 경로는 절대 경로다.

```python
CALIB_IMAGE_GLOB = "/home/jaeholee/work/calib_images/*.*"
```

혼자 쓰는 실습 환경에서는 괜찮다.

하지만 다른 컴퓨터에서 실행하거나 Git으로 공유할 코드라면 상대 경로 또는 `pathlib.Path`를 쓰는 편이 관리하기 쉽다.

### 21.5 YAML과 camera_info.yaml 혼동 주의

현재 폴더에는 `camera_calibration.yml`과 `camera_info.yaml`이 함께 있다.

두 파일의 값은 서로 다르다.

`camera_calibration.yml`의 초점 거리는 대략 다음이다.

```text
fx = 807.84
fy = 805.75
```

`camera_info.yaml`의 초점 거리는 대략 다음이다.

```text
fx = 710.28
fy = 710.40
```

왜곡 계수도 서로 다르다.

따라서 어느 파일을 실제 런타임 코드에서 사용할지 명확히 해야 한다.

같은 카메라, 같은 해상도, 같은 캘리브레이션 조건에서 나온 파일만 섞어 써야 한다.

---

## 22. 이 코드를 실행할 때의 권장 순서

처음부터 다시 실행한다면 다음 순서가 좋다.

### 22.1 이미지 수집

`05_01_01_OpenCV-Calib-Capture.py`로 체커보드 이미지를 수집한다.

확인할 것:

```text
내부 코너 수가 코드와 맞는가?
이미지 해상도가 모두 같은가?
흔들린 사진이 너무 많지 않은가?
체커보드가 화면 여러 위치에 다양하게 나오는가?
```

### 22.2 캘리브레이션 실행

노트북 마지막 셀에서 다음 설정을 확인한다.

```python
CHECKERBOARD = (9, 6)
SQUARE_SIZE = 0.025
CALIB_IMAGE_GLOB = "/home/jaeholee/work/calib_images/*.*"
ALPHA = 0.0
```

그다음 `run_calibration()`을 실행한다.

### 22.3 결과 확인

확인할 항목은 다음이다.

```text
검출 성공 이미지 수
drop된 이미지 목록
1차 RMS와 2차 RMS 비교
camera_matrix의 cx, cy가 이미지 중앙 근처인지
dist_coeffs가 지나치게 비정상적으로 보이지 않는지
```

### 22.4 테스트 이미지 보정

테스트 이미지를 보정하려면 둘 중 하나의 주석을 해제한다.

```python
run_undistort_test_from_yaml()
```

또는

```python
run_undistort_test_from_npz()
```

처음 테스트할 때는 YAML 기반이 이해하기 쉽다.

실시간 구조를 확인할 때는 NPZ 기반이 더 적합하다.

---

## 23. 한 줄 요약

이 코드는 체커보드 이미지로 카메라의 렌즈 왜곡을 추정하고, 그 결과를 `camera_calibration.yml`과 `undistort_maps_640x480_alpha0.npz`로 저장하는 코드다.

전체 구조는 잘 잡혀 있지만, 현재 실행 결과에서는 outlier 제거 후 RMS가 오히려 커졌기 때문에 2차 결과를 무조건 채택하는 부분은 개선하는 것이 좋다.

