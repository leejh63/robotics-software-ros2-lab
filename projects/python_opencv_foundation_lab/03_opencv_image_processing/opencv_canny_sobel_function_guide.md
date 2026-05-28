# OpenCV Day 3-2 · 블러, Sobel, Canny, Contour 정리

대상 자료:
- `parc/04_02_OpenCV-Canny-Sobel.ipynb`
- `parc/baboon.jpg`
- `parc/baboon_gaussian_noise.jpg`
- `parc/fbaboon_sp_noise.jpg`
- `parc/road_image.jpg`

이 문서는 `day_3`의 두 번째 축인 **노이즈 제거 -> 엣지 검출 -> 객체 경계 추출**을 정리한다.  
특히 이 노트북은 OpenCV 함수만 쓰는 것이 아니라, 일부 과정을 NumPy로 직접 구현해 보는 학습형 구조라는 점이 중요하다.

---

## 1. 학습 흐름 요약

`04_02_OpenCV-Canny-Sobel.ipynb`의 구조는 아래처럼 흘러간다.

```text
이미지 로드
-> 노이즈 추가/관찰
-> blur / Gaussian / median / bilateral 비교
-> Sobel X, Sobel Y
-> gradient magnitude 계산
-> Canny 4단계 이해
-> findContours로 덩어리 추출
-> contourArea + boundingRect로 객체화
```

즉, "보이는 선"을 잡는 것이 목표가 아니라, **노이즈 속에서 의미 있는 경계만 안정적으로 꺼내는 과정**을 배우는 문서다.

---

## 2. 필터링과 노이즈 제거

### 2.1 왜 먼저 blur를 하나?

엣지 검출은 밝기 변화에 민감하다.  
노이즈도 밝기 변화이기 때문에, 노이즈를 줄이지 않으면 엣지 검출기가 쓸데없는 선까지 많이 잡는다.

### 2.2 `cv2.blur(src, ksize)`

평균값 블러다.

| 인자 | 설명 |
|---|---|
| `src` | 입력 이미지 |
| `ksize` | 커널 크기 `(w, h)` |

특징:
- 빠르다
- 단순 평균이라 경계가 쉽게 뭉개진다

### 2.3 `cv2.GaussianBlur(src, ksize, sigmaX[, sigmaY])`

가우시안 가중치를 사용해 중심부를 더 강하게 반영한다.

| 인자 | 설명 |
|---|---|
| `ksize` | 홀수 커널 크기, 예: `(3, 3)`, `(5, 5)` |
| `sigmaX` | x축 표준편차 |
| `sigmaY` | 생략 시 `sigmaX` 기반 처리 |

예시:

```python
blurred = cv2.GaussianBlur(gray, (5, 5), 0)
```

실전에서 가장 많이 쓰는 블러다.

### 2.4 `cv2.medianBlur(src, ksize)`

주변 픽셀의 **중간값**을 사용한다.

장점:
- salt-and-pepper 노이즈 제거에 강하다
- 윤곽선 보존이 평균 블러보다 좋은 편이다

### 2.5 `cv2.bilateralFilter(src, d, sigmaColor, sigmaSpace)`

색 차이와 거리 차이를 같이 고려한다.

| 인자 | 설명 |
|---|---|
| `d` | 주변 픽셀 지름 |
| `sigmaColor` | 색 차이 허용 범위 |
| `sigmaSpace` | 거리 허용 범위 |

장점:
- 경계는 살리고 평탄한 영역만 부드럽게

단점:
- 느리다

---

## 3. NumPy로 같이 이해한 필터링 요소

노트북에서는 OpenCV 결과만 보는 것이 아니라 일부를 수식 수준으로 확인한다.

| NumPy 함수 | 역할 |
|---|---|
| `np.pad()` | 가장자리에 패딩 추가 |
| `np.array()` | 커널 행렬 정의 |
| `np.ones()` | 평균 커널 생성 |
| `np.exp()` | 가우시안 가중치 계산 |
| `np.meshgrid()` | 좌표 격자 생성 |
| `np.median()` | 미디안 계산 |
| `np.clip()` | 범위 제한 |
| `np.uint8()` | 결과를 이미지 타입으로 변환 |

학습 포인트:

1. 필터는 결국 커널과 주변 픽셀의 연산이다.
2. OpenCV 함수 한 줄 뒤에는 대부분 convolution 개념이 숨어 있다.
3. 커널 크기가 커질수록 노이즈 억제는 강해지지만 디테일은 사라진다.

---

## 4. Sobel 엣지 검출

### 4.1 `cv2.Sobel(src, ddepth, dx, dy, ksize=3)`

밝기 변화율을 x축, y축 방향으로 계산한다.

| 인자 | 설명 |
|---|---|
| `src` | 보통 grayscale 입력 |
| `ddepth` | 출력 타입, 보통 `cv2.CV_64F` |
| `dx` | x 방향 미분 차수 |
| `dy` | y 방향 미분 차수 |
| `ksize` | Sobel 커널 크기 |

예시:

```python
sobelx = cv2.Sobel(blurred, cv2.CV_64F, 1, 0, ksize=3)
sobely = cv2.Sobel(blurred, cv2.CV_64F, 0, 1, ksize=3)
```

해석:

| 코드 | 의미 |
|---|---|
| `(dx=1, dy=0)` | 세로 경계에 민감한 x 방향 변화 |
| `(dx=0, dy=1)` | 가로 경계에 민감한 y 방향 변화 |

### 4.2 왜 `CV_64F`를 쓰나?

미분 결과는 음수가 나올 수 있다.  
`uint8`로 바로 계산하면 음수 정보가 깨지므로, 먼저 실수형이나 signed 타입으로 계산하고 나중에 시각화용으로 바꾼다.

```python
abs_sobelx = np.uint8(np.absolute(sobelx))
```

관련 NumPy 함수:

| 함수 | 역할 |
|---|---|
| `np.absolute()` | 절댓값 |
| `np.sqrt()` | 크기 계산 |
| `np.max()` | 오차 비교, 최대값 확인 |

### 4.3 그래디언트 크기

노트북에서는 두 방향 미분을 합쳐 전체 edge strength를 계산했다.

```python
magnitude = cv2.magnitude(sobelx, sobely)
magnitude = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX)
magnitude = np.uint8(magnitude)
```

#### `cv2.magnitude(x, y)`

2차원 벡터 크기를 계산한다.

#### `cv2.normalize(src, dst, alpha, beta, norm_type)`

값 범위를 보기 좋게 조정한다.

| 인자 | 설명 |
|---|---|
| `alpha`, `beta` | 목표 범위 |
| `norm_type` | 여기서는 `cv2.NORM_MINMAX` |

---

## 5. Canny 엣지 검출

### 5.1 `cv2.Canny(image, threshold1, threshold2, L2gradient=False)`

OpenCV에서 가장 대표적인 엣지 검출 함수다.

| 인자 | 설명 |
|---|---|
| `image` | 보통 blur된 grayscale |
| `threshold1` | 낮은 임계값 |
| `threshold2` | 높은 임계값 |
| `L2gradient` | `True`면 더 정확한 gradient magnitude 사용 |

예시:

```python
edges = cv2.Canny(blurred, 50, 150, L2gradient=True)
```

### 5.2 Canny 4단계

노트북에서 특히 강조한 부분이다.

1. Gaussian Blur
2. Gradient 계산
3. Non-Maximum Suppression
4. Double Threshold + Hysteresis

NumPy 직접 구현에 쓰인 함수:

| 함수 | 역할 |
|---|---|
| `np.arctan2()` | gradient 방향 계산 |
| `np.round()` | 방향 양자화 보조 |
| `np.zeros_like()` | NMS 결과 배열 생성 |
| `np.clip()` | 범위 제한 |

핵심 이해:

- Sobel만 쓰면 엣지가 두껍고 노이즈가 남기 쉽다
- Canny는 후처리까지 포함해서 **얇고 안정적인 edge map**을 만든다

---

## 6. Laplacian

### `cv2.Laplacian(src, ddepth[, ksize])`

2차 미분 기반 엣지 검출이다.

```python
laplacian = cv2.Laplacian(blurred, cv2.CV_64F, ksize=3)
lap_vis = cv2.convertScaleAbs(laplacian)
```

관련 함수:

### `cv2.convertScaleAbs(src)`

음수/실수 값을 화면에 보기 좋은 8비트 절댓값 이미지로 바꿔 준다.

Laplacian은 모든 방향 변화에 반응하지만 노이즈에도 민감해서, 단독 실전 사용보다는 비교 학습용이나 특수 상황에서 더 많이 쓰인다.

---

## 7. Contour로 객체화

엣지를 구한 다음, 실제로는 "선"보다 "물체 후보"가 필요할 때가 많다.  
이때 Contour 단계로 넘어간다.

### 7.1 `cv2.findContours(image, mode, method)`

흰색 덩어리의 외곽선을 찾는다.

```python
contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
```

| 인자 | 설명 |
|---|---|
| `image` | 보통 이진 이미지나 edge map |
| `mode` | 어떤 contour를 찾을지 |
| `method` | 점 저장 방식 |

주요 옵션:

| 값 | 의미 |
|---|---|
| `cv2.RETR_EXTERNAL` | 가장 바깥 contour만 |
| `cv2.CHAIN_APPROX_SIMPLE` | 직선 구간 점을 압축 저장 |

### 7.2 `cv2.contourArea(contour)`

면적이 너무 작은 contour를 버리는 데 사용한다.

```python
if cv2.contourArea(cnt) > 900:
    ...
```

### 7.3 `cv2.boundingRect(contour)`

contour를 감싸는 축 정렬 박스를 계산한다.

반환값:

```python
x, y, w, h = cv2.boundingRect(cnt)
```

### 7.4 `cv2.rectangle(img, pt1, pt2, color, thickness)`

계산한 박스를 화면에 그린다.

```python
cv2.rectangle(result, (x, y), (x + w, y + h), (0, 255, 0), 2)
```

이 조합은 이후 웹캠 실습 코드에서도 거의 그대로 재사용된다.

---

## 8. 이 노트북에서 배운 튜닝 감각

### 커널 크기

- 작으면 디테일 유지, 노이즈도 남음
- 크면 깨끗해지지만 작은 물체가 사라질 수 있음

### Canny 임계값

- 너무 낮으면 잡음까지 edge로 인식
- 너무 높으면 중요한 경계도 놓침

### contour 면적 기준

- 너무 작으면 노이즈 박스가 많이 생김
- 너무 크면 작은 장애물을 놓칠 수 있음

---

## 9. 실무에서 자주 붙는 추가 함수

### 9.1 `cv2.threshold()`

밝기 기준으로 이진화할 때 자주 쓴다.

```python
_, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
```

### 9.2 `cv2.adaptiveThreshold()`

조명이 고르지 않을 때 유리하다.

### 9.3 `cv2.erode()`, `cv2.dilate()`, `cv2.morphologyEx()`

엣지 후처리, 마스크 정리에 매우 자주 쓰인다.  
이 함수는 다음 문서의 실시간 색상 추적 파트와 직접 연결된다.

### 9.4 `cv2.approxPolyDP()` / `cv2.arcLength()`

사각형, 삼각형 같은 도형 판별을 하고 싶을 때 자주 붙는다.

---

## 10. 한 줄 정리

이 문서의 핵심은 다음이다.

> 좋은 엣지 검출은 단일 함수 한 번보다, "전처리 -> 미분 -> 후처리 -> contour 필터링" 파이프라인으로 이해해야 한다.
