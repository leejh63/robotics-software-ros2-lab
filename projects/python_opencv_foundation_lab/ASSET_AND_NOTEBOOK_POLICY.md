# Asset and Notebook Policy

이 문서는 `projects/python_opencv_foundation_lab/`의 이미지, GIF, notebook을 공개 수정본에서 어떻게 판단할지 정리한다. Stage 4에서는 파일을 삭제하지 않고 기준만 정했고, Stage 6에서는 참조되는 이미지/GIF asset은 유지하면서 notebook output만 제거했다.

---

## 1. 기본 원칙

- 학습 흐름을 설명하는 데 필요한 샘플 이미지는 유지한다.
- notebook output은 commit 기준에서 제거한다. 학습자는 notebook을 실행해 결과를 재생성한다.
- 대용량 파일은 크기만 보고 즉시 삭제하지 않는다. 문서나 notebook에서 참조되는지 먼저 확인한다.
- YOLO weight, rosbag, calibration output, 실행 로그 같은 재생성 가능한 파일은 Git 대상에서 제외한다.

---

## 2. 현재 보이는 주요 asset

| 파일 | 크기 기준 | 판단 |
|---|---:|---|
| `01_python_basics/sphere_rotation.gif` | 약 4.6 MB | Python/Matplotlib animation 학습 자료로 유지하되, 포트폴리오 zip 크기를 줄여야 하면 첫 번째 검토 후보 |
| `03_opencv_image_processing/parc/sample.jpg` | 약 11 MB | OpenCV 기본/edge 실습에서 참조되는 샘플 이미지라 현재 유지 |
| `03_opencv_image_processing/parc/baboon.jpg` | 소형 | 필터/노이즈 실습 샘플로 유지 |
| `03_opencv_image_processing/parc/*noise*.jpg` | 소형 | 이미지 필터 실습 샘플로 유지 |
| `04_camera_calibration_yolo_kalman/prac/bus.jpg` | 소형 | YOLO smoke test 샘플로 유지 |
| `04_camera_calibration_yolo_kalman/prac/test.jpg` | 소형 | calibration/undistort 예제 확인용으로 유지 |

---

## 3. Notebook output 기준

Stage 6 기준으로 commit 대상 notebook은 output이 비어 있어야 한다. 아래 notebook들은 Stage 5에서 output이 남아 있었고 Stage 6에서 정리했다.

```text
03_opencv_image_processing/parc/04_01_OpenCV-Basic.ipynb
03_opencv_image_processing/parc/04_02_OpenCV-Canny-Sobel.ipynb
04_camera_calibration_yolo_kalman/prac/05_01_OpenCV-Calibration.ipynb
04_camera_calibration_yolo_kalman/prac/05_02_YOLO-Kalman.ipynb
```

판단 기준:

| 상태 | 처리 |
|---|---|
| 설명 이해에 필요한 이미지 output | commit에는 저장하지 않고 실행 재생성 기준으로 둠 |
| 반복 실행 로그 output | 제거 |
| 개인 경로가 포함된 output | 제거 또는 placeholder 처리 |
| 대용량 base64 image output | 제거 |

Stage 6에서 저장된 output과 execution count를 제거했다. 이후 commit 전에는 `python3 tools/notebook_output_audit.py` 또는 `python3 tools/static_repo_check.py`로 notebook output이 다시 들어오지 않았는지 확인한다.

---

## 4. Git ignore 기준

이 프로젝트의 `.gitignore`는 다음 생성물을 제외한다.

```text
calib_images/
output_gray.png
runs/
*.pt
*.onnx
*.engine
camera_info.yaml
camera_calibration.yaml
nis_log.csv
detection_log.json
```

따라서 calibration 결과, YOLO 실행 결과, 모델 weight는 재생성 가능한 로컬 산출물로 보고 공개 commit에 넣지 않는다.

---

## 5. Stage 6 실제 적용 결과

```text
이미지/GIF asset: 유지
notebook output: 제거
execution_count: 제거
코드 셀/markdown 셀: 유지
```

세부 판단은 [ASSET_NOTEBOOK_INVENTORY_STAGE06.md](ASSET_NOTEBOOK_INVENTORY_STAGE06.md)에 남긴다.

---

## 6. 다음 단계에서 실제로 할 수 있는 작업

필요할 때만 아래 순서로 진행한다.

```text
1. zip 크기 제한이 필요하면 sphere_rotation.gif와 sample.jpg를 우선 검토
2. 대체 asset을 만들 경우 README/SOURCE_MAP/RUN_COMMANDS에서 참조를 함께 수정
3. 대체 전/후 OpenCV 실습 notebook이 그대로 실행되는지 확인
4. output이 다시 생기면 commit 전에 제거
```
