# %%
import json
import cv2
import numpy as np
import yaml
import os
from pathlib import Path
from ultralytics import YOLO


BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent


def first_existing_path(candidates):
    for path in candidates:
        path = Path(path)
        if path.exists():
            return path
    return None


def load_calibration_yaml(candidates):
    yaml_path = first_existing_path(candidates)
    if yaml_path is None:
        print("[WARN] 캘리브레이션 YAML 파일을 찾지 못했습니다. 왜곡 보정을 건너뜁니다.")
        return None, None

    try:
        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError:
        data = None

    if data is None:
        fs = cv2.FileStorage(str(yaml_path), cv2.FILE_STORAGE_READ)
        if fs.isOpened():
            matrix_node = fs.getNode("camera_matrix")
            dist_node = fs.getNode("dist_coeffs")
            if dist_node.empty():
                dist_node = fs.getNode("dist_coeff")

            camera_matrix = matrix_node.mat() if not matrix_node.empty() else None
            dist_coeffs = dist_node.mat() if not dist_node.empty() else None
            fs.release()

            if camera_matrix is not None and dist_coeffs is not None:
                camera_matrix = np.array(camera_matrix, dtype=np.float64).reshape(3, 3)
                dist_coeffs = np.array(dist_coeffs, dtype=np.float64).reshape(1, -1)
                print(f"[INFO] 캘리브레이션 파라미터 로드: {yaml_path}")
                return camera_matrix, dist_coeffs

        print(f"[WARN] {yaml_path} 파일을 읽지 못했습니다. 왜곡 보정을 건너뜁니다.")
        return None, None

    if not data:
        print(f"[WARN] {yaml_path} 파일이 비어 있습니다. 왜곡 보정을 건너뜁니다.")
        return None, None

    matrix_data = data.get("camera_matrix")
    dist_data = (
        data.get("dist_coeff")
        or data.get("dist_coeffs")
        or data.get("distortion_coefficients")
    )

    if isinstance(matrix_data, dict):
        matrix_data = matrix_data.get("data")
    if isinstance(dist_data, dict):
        dist_data = dist_data.get("data")

    if matrix_data is None or dist_data is None:
        print(f"[WARN] {yaml_path}에 camera_matrix/dist_coeff 정보가 없습니다. 왜곡 보정을 건너뜁니다.")
        return None, None

    camera_matrix = np.array(matrix_data, dtype=np.float64).reshape(3, 3)
    dist_coeffs = np.array(dist_data, dtype=np.float64).reshape(1, -1)

    print(f"[INFO] 캘리브레이션 파라미터 로드: {yaml_path}")
    return camera_matrix, dist_coeffs


def undistort_if_ready(frame, camera_matrix, dist_coeffs):
    if camera_matrix is None or dist_coeffs is None:
        return frame.copy()
    return cv2.undistort(frame, camera_matrix, dist_coeffs)

# 칼만 필터 기초 클래스 (단순화 버전)
class SimpleKalman:
    def __init__(self):
        self.kf = cv2.KalmanFilter(4, 2)
        self.kf.measurementMatrix = np.array(
            [[1, 0, 0, 0],
             [0, 1, 0, 0]], dtype=np.float32)
        self.kf.transitionMatrix = np.array(
            [[1, 0, 1, 0],
             [0, 1, 0, 1],
             [0, 0, 1, 0],
             [0, 0, 0, 1]], dtype=np.float32)
        self.kf.processNoiseCov = np.eye(4, dtype=np.float32) * 0.03
        self.kf.measurementNoiseCov = np.eye(2, dtype=np.float32) * 1.0
        self.kf.errorCovPost = np.eye(4, dtype=np.float32)
        self.initialized = False

    def predict(self, coord_x, coord_y):
        measurement = np.array([[np.float32(coord_x)], [np.float32(coord_y)]])

        if not self.initialized:
            self.kf.statePost = np.array(
                [[np.float32(coord_x)],
                 [np.float32(coord_y)],
                 [0],
                 [0]], dtype=np.float32)
            self.initialized = True

        self.kf.predict()
        corrected = self.kf.correct(measurement)
        return int(corrected[0, 0]), int(corrected[1, 0])

# %%
# 1. YOLO 모델 로드 (초경량 Nano 모델)
MODEL_PATH = first_existing_path([
    Path.cwd() / "yolov8n.pt",
    BASE_DIR / "yolov8n.pt",
    PROJECT_DIR / "yolov8n.pt",
    PROJECT_DIR / "day_4" / "prac" / "yolov8n.pt",
])
model = YOLO(str(MODEL_PATH if MODEL_PATH else "yolov8n.pt"))

# %%
# TODO: camera_info.yaml 에서 캘리브레이션 파라미터를 로드하고
#       camera_matrix, dist_coeffs 를 numpy 배열로 만드세요.
YAML_PATH = "camera_info.yaml"
camera_matrix, dist_coeffs = load_calibration_yaml([
    Path.cwd() / YAML_PATH,
    Path.cwd() / "camera_calibration.yml",
    BASE_DIR / YAML_PATH,
    BASE_DIR / "camera_calibration.yml",
    PROJECT_DIR / YAML_PATH,
    PROJECT_DIR / "camera_calibration.yml",
    PROJECT_DIR / "day_4" / "prac" / YAML_PATH,
    PROJECT_DIR / "day_4" / "prac" / "camera_calibration.yml",
])

# %%

# 미션 1 — 탐지된 객체까지의 거리 추정
REAL_HEIGHT  = 1.7           # 사람의 평균 키 (미터)
def estimate_distance(frame, x1, y1, x2, y2):
    pixel_height = max(y2 - y1, 1)
    if camera_matrix is None:
        cv2.putText(frame, "Distance: N/A",
                    (x1, min(y2 + 20, frame.shape[0] - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
        return None

    focal_length = camera_matrix[1, 1]
    distance = (REAL_HEIGHT * focal_length) / pixel_height
    cv2.putText(frame, f"Distance: {distance:.2f}m",
                (x1, min(y2 + 20, frame.shape[0] - 10)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
    return distance

# 미션 2 — 특정 클래스 탐지 시 경고 출력
TARGET_LABEL = "cell phone"  # 경고를 발생시킬 클래스 이름
def check_warning(frame, label):
    if label == TARGET_LABEL:
        cv2.putText(frame, "WARNING: cell phone detected!",
                    (20, 40), cv2.FONT_HERSHEY_SIMPLEX,
                    0.8, (0, 0, 255), 2)

# 미션 3 — 탐지 결과를 JSON 파일로 저장
detection_data = []
def save_detection(label, x1, y1, x2, y2, cx, cy):
    detection_data.append({
        "label": label,
        "bbox": {
            "x1": int(x1),
            "y1": int(y1),
            "x2": int(x2),
            "y2": int(y2),
        },
        "center": {
            "x": int(cx),
            "y": int(cy),
        },
    })

def save_detection_log(path="detection_log.json"):
    output_path = Path(path)
    if not output_path.is_absolute():
        output_path = BASE_DIR / output_path

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(detection_data, f, ensure_ascii=False, indent=2)
    print(f"[INFO] 탐지 로그 저장: {output_path}")

# %%
# 웹캠 연결 (0번: 내장 웹캠)
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
if not cap.isOpened():
    raise RuntimeError("카메라(인덱스 0)를 열 수 없습니다. /dev/video0 연결과 권한을 확인하세요.")

# 칼만 필터 추적기 생성
tracker = SimpleKalman()

try:
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        # 왜곡 보정 적용 (Undistort)
        undistorted_frame = undistort_if_ready(frame, camera_matrix, dist_coeffs)

        # YOLOv8 객체 탐지
        results = model(undistorted_frame, stream=True, verbose=False)

        for r in results:
            boxes = r.boxes
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])

                cx = (x1 + x2) // 2
                cy = (y1 + y2) // 2

                # 칼만 필터 추적
                px, py = tracker.predict(cx, cy)

                cls = int(box.cls[0])
                label = model.names[cls]

                # 탐지 박스 (파란색)
                cv2.rectangle(undistorted_frame,
                              (x1, y1), (x2, y2), (255, 0, 0), 2)
                # 칼만 필터 예측 점 (빨간색)
                cv2.circle(undistorted_frame, (px, py), 5, (0, 0, 255), -1)
                cv2.putText(undistorted_frame, f"{label} (Tracked)",
                            (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX,
                            0.5, (255, 255, 255), 2)

                estimate_distance(undistorted_frame, x1, y1, x2, y2)
                check_warning(undistorted_frame, label)
                save_detection(label, x1, y1, x2, y2, cx, cy)

        cv2.imshow("Robot Vision Pipeline", undistorted_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    cap.release()
    cv2.destroyAllWindows()
    save_detection_log()
