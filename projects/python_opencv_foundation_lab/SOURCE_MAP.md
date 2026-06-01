# Source Map

이 문서는 원본 Day 01~05 자료를 현재 구조에 어떻게 배치했는지 정리한다.

---

## 1. 직접 실습 코드

| 원본 범위 | 정리 후 경로 | 역할 |
|---|---|---|
| `day_1/*` | `projects/python_opencv_foundation_lab/01_python_basics/` | Python, NumPy, Matplotlib 기초 실습 |
| `day_2/*` | `projects/python_opencv_foundation_lab/02_sensor_data_concurrency/` | 파일/JSON, sensor class, thread/process 실습 |
| `day_3/*.md` | `projects/python_opencv_foundation_lab/03_opencv_image_processing/` | OpenCV 개념 노트 |
| `day_3/parc/*` | `projects/python_opencv_foundation_lab/03_opencv_image_processing/parc/` | OpenCV notebook, script, sample image |
| `day_4/*.md` | `projects/python_opencv_foundation_lab/04_camera_calibration_yolo_kalman/` | Calibration, YOLO, Kalman 분석 노트 |
| `day_4/prac/*` | `projects/python_opencv_foundation_lab/04_camera_calibration_yolo_kalman/prac/` | Calibration, YOLO, Kalman 실행 코드 |
| `day_5/in_rasp_install.md` | `projects/python_opencv_foundation_lab/05_raspberry_pi_turtlebot_camera_setup/` | Raspberry Pi/TurtleBot3 환경 메모 |

---

## 2. 문서화 기준

| 목적 | 위치 |
|---|---|
| 학습 흐름 설명 | `day_01_05_python_opencv_foundation/` |
| 실제 코드/노트북/이미지 샘플 | `projects/python_opencv_foundation_lab/` |
| YOLO fine-tuning 참고 문서 | `appendix/yolo_finetuning_pipeline/` |
| asset/notebook 유지 기준 | `projects/python_opencv_foundation_lab/ASSET_AND_NOTEBOOK_POLICY.md` |
| Stage 6 asset/notebook 정리 결과 | `projects/python_opencv_foundation_lab/ASSET_NOTEBOOK_INVENTORY_STAGE06.md` |
| 내부 작업 로그 | `__revision_worklog_do_not_commit/` |

---

## 3. 원본 참고 자료 처리 기준

원본 `tranning/` 폴더에는 Day 01~05와 직접 관련 없는 Day 09, Day 11, Day 12, Day 14 자료도 섞여 있었다.

현재 정리본에서는 `projects/python_opencv_foundation_lab/`를 직접 실습 코드 중심으로 유지하기 위해 원본 참고 자료 중복본은 제외했다. 포트폴리오 설명에서는 `day_1`~`day_5` 직접 실습 자료를 우선 기준으로 삼는다.

---

## 4. 제외한 자료

| 제외 항목 | 이유 |
|---|---|
| `reference_training_materials/` | 직접 실습 코드가 아니라 원본 참고자료 중복본이라 제외 |
| `03.02.02.02.Python-Multi-Thread.py` | re import 누락, 파일 생성 순서 문제, top-level 실행 문제 |
| `03_02_02_02_Python-Multi-Thread..py` | race condition 관찰용 중간 코드이고 파일명이 부적절함 |
| `ioff.py` | matplotlib 실시간 시각화 중간 코드이며 top-level 실행 구조 |
| `pickle.plk` | 실습 중 생성된 데이터 파일 성격 |
| `output_gray.png` | 실행 결과물 성격의 대용량 이미지 |
| `day_4/pdf/` PDF 원본 | 수업 자료 성격이 강하므로 직접 작성 정리문서와 실행 코드로 대체 |
