# Python / OpenCV / YOLO 빠른 참조

## 1. Python

| 개념 | 의미 | 연결 |
|---|---|---|
| function | 반복 동작 묶기 | ROS2 callback/helper |
| class | 상태와 동작 묶기 | ROS2 Node class |
| list | 순서 있는 값 묶음 | detection list, bbox |
| dict | key-value mapping | class id-name, config |
| exception | 실패 처리 | camera/file/model load failure |
| `__main__` | 직접 실행 진입점 | ROS2 entry point 이해 |

## 2. NumPy

| 개념 | 의미 |
|---|---|
| ndarray | 숫자 배열 |
| shape | 배열 모양 |
| dtype | 원소 타입 |
| axis | 연산 방향 |
| boolean mask | 조건에 맞는 원소 선택 |

## 3. OpenCV

| 개념 | 의미 |
|---|---|
| BGR | OpenCV 기본 컬러 순서 |
| RGB | Matplotlib 표시에서 자주 쓰는 순서 |
| Gray | edge/threshold 전처리 |
| HSV | 색상 추적에 유리 |
| mask | 남길 픽셀 영역 |
| contour | 연결된 영역 윤곽 |
| bbox | 객체 후보를 감싸는 사각형 |

주의:

```text
이미지 배열 접근: img[y, x]
좌표 표기: (x, y)
```

## 4. Camera Calibration

| 값 | 의미 |
|---|---|
| `fx`, `fy` | 초점거리, 픽셀 단위 |
| `cx`, `cy` | 주점 |
| `K` | camera matrix |
| `dist` | 렌즈 왜곡 계수 |
| object points | 실제 체커보드 점 |
| image points | 이미지에서 검출된 점 |
| reprojection error | 추정 파라미터의 설명 오차 |

## 5. YOLO / Kalman

| 값 | 의미 |
|---|---|
| `xyxy` | `[x1, y1, x2, y2]` |
| `xywh` | `[cx, cy, w, h]` |
| `conf` | confidence |
| `cls` | class id |
| NMS | 중복 box 제거 |
| `P` | 추정 불확실성 |
| `Q` | 모델 불확실성 |
| `R` | 관측 불확실성 |
| NIS | 관측 오차 일관성 평가 |

## 6. ROS2 연결

| Day 01~05 | ROS2 연결 |
|---|---|
| OpenCV frame | `sensor_msgs/Image` + `cv_bridge` |
| YOLO bbox | custom message field |
| class/confidence | detection topic |
| camera calibration | `CameraInfo` |
| JSON log | rosbag과 비교되는 기록 방식 |
| thread/queue | callback/queue/executor 이해 |
