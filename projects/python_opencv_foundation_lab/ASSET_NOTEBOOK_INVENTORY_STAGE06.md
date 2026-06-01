# Stage 6 Asset and Notebook Inventory

이 문서는 Stage 6에서 실제 asset/notebook 정리 여부를 판단한 결과를 남긴다. 원본 zip은 수정하지 않았고, Stage 5 수정본을 기준으로 별도 Stage 6 수정본에서만 반영했다.

## 1. 결정 요약

| 항목 | 결정 | 이유 |
|---|---|---|
| 이미지/GIF asset | 유지 | 문서 또는 notebook에서 실제 참조된다. 크기만 보고 삭제하지 않는다. |
| notebook output | 제거 | 실행하면 재생성 가능한 산출물이고, 일부 notebook에서 base64 output이 zip 크기를 크게 키웠다. |
| execution_count | 제거 | source notebook을 깨끗한 실행 전 상태로 유지한다. |
| 대용량 `sample.jpg` | 유지 | OpenCV 기본 실습에서 직접 참조된다. |
| `sphere_rotation.gif` | 유지 | NumPy/Matplotlib animation 학습 자료로 참조된다. |

## 2. Notebook output 정리 결과

| Notebook | Stage 5 크기 | Stage 6 크기 | 결과 |
|---|---:|---:|---|
| `projects/python_opencv_foundation_lab/03_opencv_image_processing/parc/04_01_OpenCV-Basic.ipynb` | 1.27 MB | 0.03 MB | output/execution count 제거 |
| `projects/python_opencv_foundation_lab/03_opencv_image_processing/parc/04_02_OpenCV-Canny-Sobel.ipynb` | 4.35 MB | 0.04 MB | output/execution count 제거 |
| `projects/python_opencv_foundation_lab/04_camera_calibration_yolo_kalman/prac/05_01_OpenCV-Calibration.ipynb` | 0.07 MB | 0.07 MB | output/execution count 제거 |
| `projects/python_opencv_foundation_lab/04_camera_calibration_yolo_kalman/prac/05_02_YOLO-Kalman.ipynb` | 0.09 MB | 0.02 MB | output/execution count 제거 |

Stage 6 이후 모든 `.ipynb` 파일은 `outputs: []`, `execution_count: null` 기준을 만족한다.

## 3. 주요 asset 참조 현황

| Asset | 크기 | 참조 수 | Stage 6 판단 |
|---|---:|---:|---|
| `projects/python_opencv_foundation_lab/03_opencv_image_processing/parc/sample.jpg` | 11.00 MB | 6 | 유지 |
| `projects/python_opencv_foundation_lab/01_python_basics/sphere_rotation.gif` | 4.56 MB | 4 | 유지 |
| `projects/python_opencv_foundation_lab/03_opencv_image_processing/parc/fbaboon_sp_noise.jpg` | 0.26 MB | 2 | 유지 |
| `projects/python_opencv_foundation_lab/03_opencv_image_processing/parc/baboon_gaussian_noise.jpg` | 0.24 MB | 2 | 유지 |
| `projects/python_opencv_foundation_lab/03_opencv_image_processing/parc/road_image.jpg` | 0.22 MB | 4 | 유지 |
| `projects/python_opencv_foundation_lab/03_opencv_image_processing/parc/baboon.jpg` | 0.17 MB | 4 | 유지 |
| `projects/python_opencv_foundation_lab/04_camera_calibration_yolo_kalman/prac/bus.jpg` | 0.13 MB | 6 | 유지 |
| `projects/python_opencv_foundation_lab/01_python_basics/sensor_diagnostic.png` | 0.06 MB | 3 | 유지 |
| `projects/python_opencv_foundation_lab/04_camera_calibration_yolo_kalman/prac/test.jpg` | 0.06 MB | 5 | 유지 |
| `projects/python_opencv_foundation_lab/01_python_basics/battery_monitor.png` | 0.04 MB | 1 | 유지 |

## 4. 다음에 줄일 수 있는 후보

현재 Stage 6에서는 이미지를 삭제하지 않았다. zip 크기를 더 줄여야 할 때만 아래 순서로 검토한다.

```text
1. sample.jpg를 교육용 축소 이미지로 대체할 수 있는지 확인
2. sphere_rotation.gif를 더 작은 mp4/gif 또는 정적 이미지로 대체할지 확인
3. 대체하면 notebook과 markdown 참조를 동시에 수정
4. 대체 전/후 OpenCV 실습이 그대로 실행되는지 확인
```

## 5. 금지한 처리

- 참조되는 이미지를 크기만 보고 삭제하지 않는다.
- notebook 코드 셀은 삭제하지 않는다.
- ROS2/Gazebo/Nav2 runtime 성공 문구를 notebook 정리와 함께 추가하지 않는다.

