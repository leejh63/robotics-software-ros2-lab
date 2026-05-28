# Day 01~05 Source / Split Index

이 문서는 Day 01~05 자료를 전체 저장소 구조에 맞춰 분리한 기준을 기록한다.

---

## 1. 최종 판단

`day_5.zip`은 이름만 보면 Day 05 단일 자료처럼 보이지만, 실제로는 다음이 함께 들어 있다.

```text
day_1/
day_2/
day_3/
day_4/
day_5/
tranning/
```

따라서 이번 정리는 “Day 05 하나 추가”가 아니라 “Day 01~05 Python/OpenCV foundation 정리”로 보는 것이 맞다.

---

## 2. 중요도 판단

우선순위는 다음이다.

```text
1순위: OpenCV basic / edge / color tracking
2순위: Camera calibration / undistort
3순위: YOLO / Kalman / robot camera practice
4순위: Raspberry Pi / TurtleBot3 camera setup memo
5순위: Python / NumPy / thread 기본기
```

Python 기본기는 필요하지만, 포트폴리오에서 핵심으로 강조할 부분은 아니다. 핵심은 카메라 frame을 읽고, 처리하고, detection/tracking으로 확장한 흐름이다.

---

## 3. 저장소 구조 기준

```text
day_* 폴더
  -> 학습 흐름 정리 문서

10_selected_deep_dives/
11_navigation_debug_deep_dives/
appendix/
  -> 개념 심화, 표, 디버깅 기준, 명령어 참조

projects/
  -> 실제 실행 가능한 코드 / workspace / notebook
```

이번 패치는 이 기준에 맞춰 `projects/python_opencv_foundation_lab/`를 추가한다.

---

## 4. GitHub에 올릴 때 주의

대형 모델 파일과 실행 결과는 커밋하지 않는 편이 좋다.

```text
*.pt
runs/
nis_log.csv
detection_log.json
camera_calibration.yml
camera_info.yaml
.venv/
__pycache__/
```

프로젝트 폴더 내부 `.gitignore`에 위 항목을 추가했다. 저장소 루트 `.gitignore`에도 같은 규칙이 있다면 중복되어도 문제 없다.
