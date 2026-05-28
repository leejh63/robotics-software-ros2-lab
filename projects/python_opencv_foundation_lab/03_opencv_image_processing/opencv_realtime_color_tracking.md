# OpenCV Day 3-3 · 웹캠 실시간 색상 추적과 트랙바 실습 정리

대상 자료:
- `parc/04_03_00_OpenCV-Practice.py`

이 문서는 `day_3`의 마지막 축인 **실시간 카메라 입력, 트랙바 UI, HSV 색상 추적, 모폴로지 후처리, 바운딩 박스 시각화**를 정리한다.  
특히 현재 파일은 주석 처리된 `edge_detection_pipeline()` 버전과, 실제 실행되는 `color_detection_pipeline()` 버전이 함께 있어 학습 진화 과정까지 읽을 수 있다.

---

## 1. 파일 구조 해석

`04_03_00_OpenCV-Practice.py`는 크게 3부분이다.

1. 초기 버전
   고정 임계값으로 Canny + Contour를 사용하는 웹캠 엣지 검출
2. 개선 버전
   트랙바로 Canny 임계값, 최소 면적, Gaussian 커널을 조절하는 버전
3. 최종 버전
   HSV 색상 추적 + 모폴로지 + contour 박스 + 텍스트 표시

즉, 이 파일은 단순한 결과 코드가 아니라 **실험하면서 점진적으로 기능을 붙인 실습 기록**에 가깝다.

---

## 2. 카메라 입력 기본

### 2.1 `cv2.VideoCapture(index_or_path)`

웹캠이나 영상 파일을 연다.

```python
cap = cv2.VideoCapture(0)
```

| 인자 | 설명 |
|---|---|
| `0` | 보통 기본 웹캠 |
| `1`, `2` | 추가 카메라일 수 있음 |
| 파일 경로 | 동영상 파일 입력 |

### 2.2 `cap.isOpened()`

카메라가 정상적으로 열렸는지 검사한다.

```python
if not cap.isOpened():
    print("카메라를 열 수 없습니다.")
    return
```

### 2.3 `cap.read()`

프레임을 한 장 읽는다.

```python
ret, frame = cap.read()
```

| 반환값 | 의미 |
|---|---|
| `ret` | 성공 여부 |
| `frame` | 읽은 이미지 프레임 |

### 2.4 `cap.release()`

카메라 리소스를 반드시 해제한다.

---

## 3. 루프 제어와 화면 표시

실시간 비전 기본 루프:

```python
while True:
    ret, frame = cap.read()
    if not ret:
        break

    cv2.imshow("view", frame)

    if cv2.waitKey(25) & 0xFF == ord("q"):
        break
```

중요 표현:

### `cv2.waitKey(25) & 0xFF`

- `waitKey(25)`는 25ms 동안 키 입력을 확인
- `& 0xFF`는 플랫폼 차이를 줄이기 위한 전형적인 패턴
- `ord("q")`와 비교해 종료 키를 만든다

---

## 4. 트랙바 UI

실시간 튜닝에서 가장 중요한 도구다.

### 4.1 `cv2.namedWindow(winname)`

트랙바를 붙일 창을 먼저 만든다.

```python
cv2.namedWindow("Control")
```

### 4.2 `cv2.createTrackbar(trackbarName, windowName, value, count, onChange)`

슬라이더를 만든다.

```python
cv2.createTrackbar("H Min", "Control", 35, 179, nothing)
```

| 인자 | 설명 |
|---|---|
| `trackbarName` | 슬라이더 이름 |
| `windowName` | 붙일 창 이름 |
| `value` | 초기값 |
| `count` | 최댓값 |
| `onChange` | 값이 바뀔 때 호출할 함수 |

### 4.3 `def nothing(x): pass`

현재 코드는 트랙바 변화 시 별도 콜백 동작이 필요 없어서 빈 함수를 넣는다.  
OpenCV 트랙바는 콜백 자리에 `None`이 아니라 함수 레퍼런스를 요구하는 경우가 많아 이 패턴을 자주 쓴다.

### 4.4 `cv2.getTrackbarPos(trackbarName, windowName)`

현재 슬라이더 값을 읽는다.

```python
h_min = cv2.getTrackbarPos("H Min", "Control")
```

이 방식 덕분에 코드를 다시 실행하지 않고도 탐지 범위를 즉석에서 조정할 수 있다.

---

## 5. 보조 함수 `make_odd_kernel(value)`

현재 파일에 직접 추가된 중요한 유틸 함수다.

```python
def make_odd_kernel(value):
    if value < 1:
        value = 1
    if value % 2 == 0:
        value += 1
    return value
```

필요한 이유:

1. `GaussianBlur()`와 많은 모폴로지 커널은 홀수 크기를 요구한다.
2. 트랙바로 받은 값은 짝수일 수도 있다.
3. 따라서 실행 전에 안전한 홀수 커널 값으로 보정해야 한다.

이런 "입력값 방어 로직"은 실시간 프로그램에서 매우 중요하다.

---

## 6. HSV 색상 탐지 파이프라인

최종 실행 함수는 `color_detection_pipeline()`이다.

흐름은 다음과 같다.

```text
웹캠 프레임 읽기
-> BGR -> HSV 변환
-> H/S/V 범위 마스크 생성
-> 빨강처럼 Hue가 끊기는 경우 2개 마스크 OR 결합
-> morphologyEx OPEN/CLOSE
-> findContours
-> contourArea 기준 필터
-> boundingRect + rectangle + putText
-> bitwise_and로 색상만 남긴 결과 시각화
```

---

## 7. 핵심 함수별 상세 설명

### 7.1 `cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)`

프레임을 HSV로 변환한다.

```python
hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
```

트랙바 범위도 이 HSV 스케일에 맞춰져 있다.

| 채널 | OpenCV 범위 |
|---|---|
| `H` | `0 ~ 179` |
| `S` | `0 ~ 255` |
| `V` | `0 ~ 255` |

### 7.2 `np.array([h_min, s_min, v_min])`

하한/상한 범위를 배열로 만든다.

```python
lower = np.array([h_min, s_min, v_min])
upper = np.array([h_max, s_max, v_max])
```

### 7.3 `cv2.inRange(hsv, lower, upper)`

범위 안의 픽셀만 흰색으로 남긴 1채널 마스크를 만든다.

### 7.4 Hue wrap-around 처리

현재 코드의 추가 내용 중 가장 좋은 부분 중 하나다.

```python
if h_min <= h_max:
    mask = cv2.inRange(hsv, lower, upper)
else:
    ...
    mask = cv2.bitwise_or(mask1, mask2)
```

이 처리가 필요한 대표 색상은 빨강이다.  
예를 들어 `170 -> 10` 범위는 단순 비교로는 표현이 안 되므로 두 구간으로 나눠야 한다.

### 7.5 `kernel = np.ones((morph_k, morph_k), np.uint8)`

모폴로지 연산용 커널 생성이다.

### 7.6 `cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)`

작은 흰 점 노이즈를 제거한다.

의미:

```text
OPEN = erosion 후 dilation
```

### 7.7 `cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)`

끊긴 영역을 조금 메우고 연결하는 데 사용한다.

의미:

```text
CLOSE = dilation 후 erosion
```

이 두 줄 덕분에 마스크 품질이 크게 안정된다.

### 7.8 `cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)`

가장 바깥쪽 색상 덩어리 contour만 찾는다.

### 7.9 `cv2.contourArea(cnt)`

너무 작은 검출 결과를 버린다.

```python
if area < min_area:
    continue
```

### 7.10 `cv2.boundingRect(cnt)`

검출된 색상 영역을 둘러싸는 사각형을 만든다.

### 7.11 `cv2.rectangle(...)`

탐지 결과 박스를 그린다.

현재 코드는 빨간색 박스를 사용한다.

```python
cv2.rectangle(result, (x, y), (x + w, y + h), (0, 0, 255), 2)
```

### 7.12 `cv2.putText(...)`

객체 위에 `"target color"`라는 라벨을 쓴다.

| 인자 | 설명 |
|---|---|
| 문자열 | 표시할 텍스트 |
| `(x, y - 5)` | 텍스트 시작 위치 |
| `cv2.FONT_HERSHEY_SIMPLEX` | 폰트 |
| `0.6` | 폰트 크기 |
| `(0, 0, 255)` | BGR 글자색 |
| `2` | 두께 |

### 7.13 `cv2.bitwise_and(frame, frame, mask=mask)`

현재 선택한 색상만 실제 영상에서 남긴다.

```python
color_only = cv2.bitwise_and(frame, frame, mask=mask)
```

이 코드는 박스 시각화와 별개로, **마스크가 실제로 원하는 색을 얼마나 정확히 자르고 있는지 디버깅하는 데 매우 유용**하다.

---

## 8. 이전 Canny 버전과의 연결점

파일 상단의 주석 처리된 `edge_detection_pipeline()`은 다음 학습 연결을 보여 준다.

```text
gray
-> GaussianBlur
-> Canny
-> findContours
-> contourArea
-> boundingRect
-> rectangle
```

최종 색상 추적 버전도 사실 구조가 거의 같다.

```text
HSV
-> inRange
-> morphologyEx
-> findContours
-> contourArea
-> boundingRect
-> rectangle
```

차이는 "엣지 기반 분할"이냐 "색상 기반 분할"이냐에 있다.

---

## 9. 실무에서 바로 같이 쓰이는 추가 기능

### 9.1 `cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)`

카메라 해상도 조절에 자주 쓴다.

함께 많이 쓰는 속성:

| 속성 | 의미 |
|---|---|
| `cv2.CAP_PROP_FRAME_WIDTH` | 프레임 너비 |
| `cv2.CAP_PROP_FRAME_HEIGHT` | 프레임 높이 |
| `cv2.CAP_PROP_FPS` | 초당 프레임 수 |

### 9.2 `cv2.flip(frame, 1)`

좌우 반전 셀피 화면을 만들 때 많이 사용한다.

### 9.3 `cv2.resize(frame, (w, h))`

처리 속도 향상용으로 프레임을 줄일 때 효과적이다.

### 9.4 `cv2.moments(cnt)`

객체 중심점 계산에 자주 쓴다.  
박스만이 아니라 중심 추적이 필요할 때 유용하다.

### 9.5 `cv2.minEnclosingCircle(cnt)`

원형 물체 추적에서 자주 쓴다.

### 9.6 `cv2.connectedComponentsWithStats()`

Contour 대신 연결요소 기반으로 물체를 분석할 때 강력하다.

---

## 10. 튜닝 팁

1. `S`, `V` 하한을 너무 낮게 두면 배경까지 많이 잡힌다.
2. 조명 변화가 심하면 `H`만 믿지 말고 `S`, `V` 범위도 같이 조절해야 한다.
3. `Min Area`가 너무 작으면 작은 반사광도 객체로 잡힌다.
4. `Morph K`가 너무 크면 작은 물체가 사라질 수 있다.
5. 디버깅은 항상 `Original`, `Mask`, `Color Only` 세 창을 같이 보는 것이 좋다.

---

## 11. 한 줄 정리

이 문서의 핵심은 다음이다.

> 실시간 비전 프로그램은 "카메라 입력 -> 분할 마스크 -> 후처리 -> contour 분석 -> 시각화" 파이프라인으로 생각하면 구조가 훨씬 선명해진다.
