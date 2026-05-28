# OpenCV Day 3-1 · 기초 이미지 처리와 색공간 정리

대상 자료:
- `parc/04_01_OpenCV-Basic.ipynb`
- `parc/sample.jpg`
- `parc/output_gray.png`는 notebook 실행 시 생성되는 결과 파일이므로 정리본에는 포함하지 않음

이 문서는 `day_3`의 첫 번째 축인 **이미지 입출력, 배열 구조 이해, 색공간 변환, HSV 마스크 처리**를 정리한다.  
기존 실습에서 직접 사용한 함수는 물론, 이어서 자주 쓰이는 함수도 같이 묶어 둔다.

---

## 1. day_3 폴더 흐름

`day_3`는 크게 3단계로 학습이 이어진다.

1. `04_01_OpenCV-Basic.ipynb`
   이미지가 배열이라는 감각, `imread`, `cvtColor`, HSV 마스크, 비트연산을 익히는 단계
2. `04_02_OpenCV-Canny-Sobel.ipynb`
   블러, Sobel, Canny, Contour로 넘어가는 단계
3. `04_03_00_OpenCV-Practice.py`
   웹캠 입력과 트랙바를 이용해 실시간 색상 추적을 만드는 단계

즉, Day 3는 `정적 이미지 이해 -> 엣지/객체화 -> 실시간 비전` 순서로 설계되어 있다.

---

## 2. OpenCV 이미지는 결국 NumPy 배열

OpenCV에서 읽은 이미지는 대부분 `numpy.ndarray`이다.

```python
img = cv2.imread("sample.jpg")
print(type(img))
print(img.shape)
print(img.dtype)
```

핵심 개념:

| 항목 | 의미 |
|---|---|
| `shape == (H, W, 3)` | 컬러 이미지 |
| `shape == (H, W)` | 그레이스케일 이미지 |
| `dtype == uint8` | 픽셀 값이 0~255 정수 |
| `img[y, x]` | `(x, y)`가 아니라 `[행, 열]` 접근 |

실습에서 자주 나온 NumPy 함수:

| 함수 | 역할 |
|---|---|
| `np.zeros()` | 검정 배경 만들기 |
| `np.full()` | 단색 이미지 만들기 |
| `np.array()` | 색상 범위, 좌표 배열 생성 |
| `np.full_like()` | 원본과 같은 크기의 흰 배경 만들기 |
| `np.uint8()` | 픽셀 타입 맞추기 |
| `np.sum(mask > 0)` | 마스크 픽셀 개수 세기 |

예시:

```python
black = np.zeros((300, 400, 3), dtype=np.uint8)
white = np.full((300, 400, 3), 255, dtype=np.uint8)
red_bgr = np.full((100, 100, 3), [0, 0, 255], dtype=np.uint8)
```

---

## 3. 이미지 입출력 핵심 함수

### 3.1 `cv2.imread(filename, flags=cv2.IMREAD_COLOR)`

이미지를 파일에서 읽는다.

주요 인자:

| 인자 | 설명 |
|---|---|
| `filename` | 읽을 파일 경로 |
| `flags` | 읽기 방식 |

대표 `flags`:

| 값 | 의미 |
|---|---|
| `cv2.IMREAD_COLOR` | BGR 3채널 |
| `cv2.IMREAD_GRAYSCALE` | 1채널 grayscale |
| `cv2.IMREAD_UNCHANGED` | 알파 포함 원본 유지 |

중요:

```python
img = cv2.imread("sample.jpg")
if img is None:
    raise FileNotFoundError("이미지를 읽지 못했습니다.")
```

`imread()`는 실패해도 예외 대신 `None`을 반환하므로, 경로 검사는 거의 습관처럼 넣는 편이 좋다.

### 3.2 `cv2.imwrite(filename, img, params=None)`

배열을 이미지 파일로 저장한다.

| 인자 | 설명 |
|---|---|
| `filename` | 저장 경로 |
| `img` | 저장할 배열 |
| `params` | 압축률, 품질 등 추가 옵션 |

예시:

```python
success = cv2.imwrite("output_gray.png", gray)
```

### 3.3 `cv2.imshow()`, `cv2.waitKey()`, `cv2.destroyAllWindows()`

스크립트 환경에서 창을 띄울 때 사용한다.

```python
cv2.imshow("view", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
```

| 함수 | 역할 |
|---|---|
| `imshow(window_name, image)` | 창에 이미지 표시 |
| `waitKey(delay)` | 키 입력 대기 |
| `destroyAllWindows()` | 열린 창 종료 |

`waitKey(0)`은 무한 대기, `waitKey(25)`는 25ms마다 키 입력을 확인한다.

---

## 4. BGR, RGB, Gray, HSV

### 4.1 `cv2.cvtColor(src, code)`

색공간 변환 함수다.

| `code` | 의미 | 용도 |
|---|---|---|
| `cv2.COLOR_BGR2RGB` | BGR -> RGB | Matplotlib 출력 |
| `cv2.COLOR_BGR2GRAY` | BGR -> Gray | 엣지, threshold 전처리 |
| `cv2.COLOR_BGR2HSV` | BGR -> HSV | 색상 탐지 |
| `cv2.COLOR_HSV2RGB` | HSV -> RGB | HSV 결과를 시각화할 때 |

예시:

```python
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
```

실수 포인트:

1. OpenCV는 기본이 `BGR`이다.
2. `plt.imshow(image)`를 그대로 하면 색이 뒤집혀 보일 수 있다.
3. 그레이 변환 뒤에는 `shape`가 2차원으로 바뀐다.

Matplotlib 출력:

```python
plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
plt.axis("off")
```

### 4.2 HSV가 중요한 이유

RGB/BGR에서는 "밝은 빨강", "어두운 빨강"을 한 번에 잡기 어렵다.  
HSV는 색상(H), 채도(S), 명도(V)를 분리해서 다루므로 색상 기반 탐지에 유리하다.

OpenCV HSV 범위:

| 채널 | 범위 |
|---|---|
| `H` | `0 ~ 179` |
| `S` | `0 ~ 255` |
| `V` | `0 ~ 255` |

---

## 5. 도형 그리기와 테스트 이미지 만들기

실습에서는 탐지 테스트용으로 직접 도형을 그렸다.

### 5.1 `cv2.circle(img, center, radius, color, thickness)`

| 인자 | 설명 |
|---|---|
| `center` | 중심 좌표 `(x, y)` |
| `radius` | 반지름 |
| `color` | BGR 색상 |
| `thickness` | 선 두께, `-1`이면 채우기 |

### 5.2 `cv2.rectangle(img, pt1, pt2, color, thickness)`

직사각형을 그린다.

### 5.3 `cv2.fillPoly(img, pts, color)`

다각형 내부를 채울 때 사용한다.

예시:

```python
test = np.zeros((300, 400, 3), dtype=np.uint8)
cv2.circle(test, (200, 150), 80, (0, 0, 220), -1)
cv2.rectangle(test, (10, 10), (100, 100), (255, 0, 0), -1)
```

---

## 6. HSV 마스크 처리 핵심

### 6.1 `cv2.inRange(src, lowerb, upperb)`

특정 범위에 들어오는 픽셀만 흰색(`255`)으로 두고, 나머지는 검정(`0`)으로 만든다.

```python
lower_blue = np.array([100, 120, 70])
upper_blue = np.array([130, 255, 255])
mask = cv2.inRange(hsv, lower_blue, upper_blue)
```

| 인자 | 설명 |
|---|---|
| `src` | 보통 HSV 이미지 |
| `lowerb` | 하한 배열 |
| `upperb` | 상한 배열 |

### 6.2 빨간색이 두 범위가 필요한 이유

빨강은 Hue가 원형으로 이어져 있기 때문에 `0` 근처와 `179` 근처를 동시에 잡아야 할 때가 많다.

```python
mask1 = cv2.inRange(hsv, np.array([0, 120, 70]), np.array([10, 255, 255]))
mask2 = cv2.inRange(hsv, np.array([170, 120, 70]), np.array([179, 255, 255]))
mask = cv2.bitwise_or(mask1, mask2)
```

### 6.3 `cv2.bitwise_and(src1, src2, mask=None)`

마스크가 흰색인 부분만 원본에서 남긴다.

```python
detected = cv2.bitwise_and(image, image, mask=mask)
```

### 6.4 `cv2.bitwise_not(src)` / `cv2.bitwise_or(src1, src2)` / `cv2.add(src1, src2)`

| 함수 | 역할 |
|---|---|
| `bitwise_not()` | 마스크 반전 |
| `bitwise_or()` | 두 마스크 합치기 |
| `add()` | 두 결과 이미지를 합성 |

실습에서는 "초록색 제거 후 흰 배경 합성", "검정/흰색 동시 탐지" 같은 확장 예제를 만들 때 이 조합을 사용했다.

---

## 7. 이 파트에서 특히 잘 이해해야 하는 흐름

기본 색상 탐지 파이프라인:

```text
BGR 이미지 읽기
-> HSV 변환
-> inRange로 마스크 생성
-> bitwise_and로 원하는 색만 추출
-> 필요하면 not/or/add로 배경 합성
```

이 흐름이 익숙해지면 뒤의 실시간 웹캠 추적도 거의 같은 구조로 이해할 수 있다.

---

## 8. 실무에서 자주 같이 쓰는 추가 함수

Day 3 코드에는 직접 많이 안 나왔지만 곧바로 같이 배우면 좋은 것들이다.

### 8.1 `cv2.split()` / `cv2.merge()`

채널 분리와 병합에 사용한다.

```python
b, g, r = cv2.split(image)
merged = cv2.merge([b, g, r])
```

### 8.2 `cv2.resize(src, dsize, fx=0, fy=0, interpolation=...)`

카메라 프레임 크기 조절, 학습용 이미지 축소에 자주 쓴다.

자주 쓰는 보간:

| 값 | 상황 |
|---|---|
| `cv2.INTER_LINEAR` | 일반 확대/축소 |
| `cv2.INTER_AREA` | 축소할 때 품질 좋음 |
| `cv2.INTER_CUBIC` | 확대 품질 좋지만 느림 |

### 8.3 ROI 슬라이싱

```python
roi = image[100:200, 150:300]
```

특정 영역만 잘라서 처리하거나 속도를 줄이는 데 매우 자주 쓰인다.

---

## 9. 자주 하는 실수

1. `cv2.imread()` 결과가 `None`인데 바로 `cvtColor()`를 호출함
2. BGR 이미지를 RGB로 바꾸지 않고 `plt.imshow()`에 넣음
3. HSV 범위를 RGB처럼 생각함
4. 빨강 탐지에서 Hue wrap-around를 빼먹음
5. `mask`는 1채널인데 컬러 이미지처럼 다룸
6. `dtype`가 달라져 저장/연산 결과가 이상해짐

---

## 10. 한 줄 정리

이 문서의 핵심은 다음 한 문장으로 정리된다.

> OpenCV의 기초는 "이미지를 배열로 읽고, 색공간을 바꾸고, 범위 마스크를 만든 뒤, 필요한 픽셀만 남기는 것"이다.
