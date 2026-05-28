import cv2
import numpy as np
from ultralytics import YOLO


# ============================================================
# YOLOv8 실시간 웹캠 테스트 코드
# ============================================================
# 이 파일은 TASK 변수 하나만 바꿔서 YOLO의 3가지 기능을 실험합니다.
#
# TASK = "detect"
#   일반 객체 탐지입니다.
#   사람, 자동차, 컵 같은 물체를 사각형 박스로 찾아줍니다.
#
# TASK = "segment"
#   세그멘테이션입니다.
#   물체를 사각형 박스뿐 아니라 물체 모양의 마스크로 따줍니다.
#
# TASK = "pose"
#   사람 자세 추정입니다.
#   사람의 눈, 코, 어깨, 팔꿈치, 손목, 무릎 같은 keypoint를 찾습니다.
# ============================================================


# 여기만 바꾸면 됩니다: "detect", "segment", "pose"
# 예:
#   TASK = "detect"   -> yolov8n.pt 사용
#   TASK = "segment"  -> yolov8n-seg.pt 사용
#   TASK = "pose"     -> yolov8n-pose.pt 사용
TASK = "detect"

# 사용할 YOLO 모델 크기입니다.
# n: nano  - 가장 작고 빠름. 실습, 웹캠, CPU 환경에 추천
# s: small - n보다 정확하지만 조금 느림
# m: medium
# l: large
# x: x-large - 가장 크고 느리지만 정확도는 높은 편
MODEL_SIZE = "n"

# OpenCV에서 열 카메라 번호입니다.
# 노트북 기본 웹캠은 보통 0번입니다.
# USB 카메라가 여러 개면 1, 2번일 수도 있습니다.
CAMERA_INDEX = 0

# YOLO 탐지 신뢰도 기준입니다.
# 0.5는 50% 이상 확신하는 결과만 화면에 표시한다는 뜻입니다.
# 값을 낮추면 더 많이 잡지만 오탐이 늘 수 있습니다.
# 값을 높이면 확실한 것만 잡지만 실제 물체를 놓칠 수 있습니다.
CONF_THRESHOLD = 0.5

# pose 모드에서 YOLO가 기본으로 그려주는 사람 skeleton을 표시할지 정합니다.
# True:
#   YOLO가 기본 뼈대, 관절점, 사람 박스를 자동으로 그립니다.
# False:
#   기본 skeleton을 끄고, 이 코드에서 원하는 keypoint만 직접 그립니다.
SHOW_POSE_DEFAULT_SKELETON = True

# pose 모드에서 keypoint 이름을 글자로 표시할지 정합니다.
# 예: left_eye, right_wrist 같은 글자를 화면에 표시합니다.
SHOW_POSE_KEYPOINT_LABELS = True

# pose keypoint에도 신뢰도가 있습니다.
# 이 값보다 낮은 keypoint는 부정확하다고 보고 표시하지 않습니다.
KEYPOINT_CONF_THRESHOLD = 0.5

# pose 모드에서 이름을 표시하고 싶은 keypoint 목록입니다.
# 주의:
#   yolov8n-pose.pt는 COCO 17개 keypoint만 지원합니다.
#   입, 손가락 마디는 이 모델에 포함되어 있지 않습니다.
POSE_LABELS_TO_SHOW = {
    "left_eye",
    "right_eye",
    "left_ear",
    "right_ear",
    "left_shoulder",
    "right_shoulder",
    "left_elbow",
    "right_elbow",
    "left_wrist",
    "right_wrist",
    "left_hip",
    "right_hip",
    "left_knee",
    "right_knee",
    "left_ankle",
    "right_ankle",
}


# TASK 값에 따라 어떤 YOLO 모델 파일을 사용할지 정하는 딕셔너리입니다.
# f-string을 사용해서 MODEL_SIZE 값이 자동으로 들어갑니다.
#
# MODEL_SIZE = "n"일 때:
#   detect  -> yolov8n.pt
#   segment -> yolov8n-seg.pt
#   pose    -> yolov8n-pose.pt
MODEL_BY_TASK = {
    "detect": f"yolov8{MODEL_SIZE}.pt",
    "segment": f"yolov8{MODEL_SIZE}-seg.pt",
    "pose": f"yolov8{MODEL_SIZE}-pose.pt",
}

# OpenCV 창 제목을 TASK별로 다르게 보여주기 위한 딕셔너리입니다.
WINDOW_BY_TASK = {
    "detect": "YOLOv8 Detection",
    "segment": "YOLOv8 Segmentation",
    "pose": "YOLOv8 Pose",
}

# YOLO pose 모델이 사용하는 COCO keypoint 17개 이름입니다.
# result.keypoints.xy에서 0번 좌표는 nose, 1번 좌표는 left_eye처럼
# 이 리스트의 순서와 keypoint 좌표 순서가 서로 대응됩니다.
COCO_KEYPOINTS = [
    "nose",
    "left_eye",
    "right_eye",
    "left_ear",
    "right_ear",
    "left_shoulder",
    "right_shoulder",
    "left_elbow",
    "right_elbow",
    "left_wrist",
    "right_wrist",
    "left_hip",
    "right_hip",
    "left_knee",
    "right_knee",
    "left_ankle",
    "right_ankle",
]


def draw_segmentation_contours(frame, result):
    """
    세그멘테이션 결과의 마스크 외곽선을 frame 위에 그립니다.

    Args:
        frame:
            OpenCV 이미지 배열입니다.
            보통 shape은 (높이, 너비, 3)입니다.
            OpenCV는 BGR 색상 순서를 사용합니다.
            이 함수는 frame을 직접 수정합니다.

        result:
            YOLO 추론 결과 하나입니다.
            model.predict(...) 결과에서 for문으로 꺼낸 객체입니다.
            segment 모델을 사용하면 result.masks 안에 마스크 정보가 들어 있습니다.

    Returns:
        int:
            화면에 그릴 수 있는 segmentation mask 개수입니다.
            마스크가 없으면 0을 반환합니다.
    """
    # result.masks가 None이면 현재 프레임에서 segmentation mask가 없다는 뜻입니다.
    if result.masks is None:
        return 0

    # result.masks.xy:
    #   각 마스크의 외곽선을 polygon 좌표로 담고 있습니다.
    #   polygon은 [[x1, y1], [x2, y2], ...] 형태의 점 목록입니다.
    for polygon in result.masks.xy:
        # OpenCV의 polylines 함수는 int32 좌표 배열을 기대하므로 변환합니다.
        contour = np.array(polygon, dtype=np.int32)

        # 점이 3개 미만이면 닫힌 도형을 만들 수 없으므로 건너뜁니다.
        if len(contour) < 3:
            continue

        # cv2.polylines:
        #   여러 점을 이어서 선을 그리는 OpenCV 함수입니다.
        #
        # frame:
        #   선을 그릴 이미지
        # [contour]:
        #   그릴 외곽선 좌표 목록입니다.
        #   OpenCV는 contour들을 리스트로 받기 때문에 [contour] 형태로 넣습니다.
        # isClosed=True:
        #   마지막 점과 첫 점을 연결해서 닫힌 도형으로 만듭니다.
        # color=(0, 255, 0):
        #   BGR 기준 초록색입니다.
        # thickness=2:
        #   선 두께입니다.
        cv2.polylines(
            frame,
            [contour],
            isClosed=True,
            color=(0, 255, 0),
            thickness=2,
        )

    return len(result.masks.xy)


def draw_pose_keypoint_labels(frame, result):
    """
    pose 결과에서 원하는 keypoint에 점과 이름을 표시합니다.

    Args:
        frame:
            OpenCV 이미지 배열입니다.
            이 함수 안에서 cv2.circle, cv2.putText로 직접 그림을 추가합니다.

        result:
            YOLO pose 추론 결과 하나입니다.
            pose 모델을 사용하면 result.keypoints 안에 사람별 keypoint 좌표가 들어 있습니다.

    Returns:
        int:
            keypoint가 검출된 사람 수입니다.
            keypoint가 없거나 표시 옵션이 꺼져 있으면 0을 반환합니다.
    """
    # keypoints가 없으면 pose 결과가 없는 것입니다.
    # SHOW_POSE_KEYPOINT_LABELS가 False이면 일부러 이름 표시를 끈 상태입니다.
    if result.keypoints is None or not SHOW_POSE_KEYPOINT_LABELS:
        return 0

    # result.keypoints.conf:
    #   각 keypoint의 신뢰도입니다.
    #   낮은 신뢰도 점은 잘못 찍힌 점일 수 있으므로 필터링합니다.
    keypoints_conf = result.keypoints.conf

    # result.keypoints.xy:
    #   사람별 keypoint 좌표입니다.
    #
    # 구조 예시:
    #   [
    #       사람 0의 17개 keypoint 좌표,
    #       사람 1의 17개 keypoint 좌표,
    #       ...
    #   ]
    #
    # enumerate를 쓰면:
    #   person_index에는 사람 번호,
    #   person_keypoints에는 그 사람의 17개 좌표가 들어갑니다.
    for person_index, person_keypoints in enumerate(result.keypoints.xy):
        # index:
        #   0이면 nose, 1이면 left_eye처럼 COCO_KEYPOINTS 순서와 맞습니다.
        #
        # point:
        #   keypoint의 좌표입니다. 보통 [x, y] 형태입니다.
        for index, point in enumerate(person_keypoints):
            # keypoint confidence가 기준값보다 낮으면 화면에 표시하지 않습니다.
            if keypoints_conf is not None and keypoints_conf[person_index][index] < KEYPOINT_CONF_THRESHOLD:
                continue

            # PyTorch tensor 형태의 좌표를 OpenCV에서 쓸 수 있는 int 좌표로 바꿉니다.
            x, y = int(point[0]), int(point[1])

            # 좌표가 (0, 0)에 가까우면 검출 실패처럼 취급하고 건너뜁니다.
            if x <= 0 and y <= 0:
                continue

            # POSE_LABELS_TO_SHOW에 들어 있는 keypoint만 표시합니다.
            # 예를 들어 "left_eye"가 들어 있으면 왼쪽 눈만 표시 대상입니다.
            if COCO_KEYPOINTS[index] in POSE_LABELS_TO_SHOW:
                # keypoint 위치에 노란 점을 찍습니다.
                cv2.circle(frame, (x, y), 4, (0, 255, 255), -1)

                # keypoint 이름을 점 옆에 글자로 표시합니다.
                cv2.putText(
                    frame,
                    COCO_KEYPOINTS[index],
                    (x + 5, y - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.4,
                    (0, 255, 255),
                    1,
                )

    return len(result.keypoints.xy)


def draw_task_info(frame, task, count):
    """
    화면 왼쪽 위에 현재 결과 개수를 표시합니다.

    Args:
        frame:
            OpenCV 이미지 배열입니다.
            이 함수는 frame 위에 텍스트를 직접 그립니다.

        task:
            현재 실행 중인 작업 이름입니다.
            "detect", "segment", "pose" 중 하나입니다.

        count:
            화면에 표시할 결과 개수입니다.
            detect에서는 박스 개수,
            segment에서는 마스크 개수,
            pose에서는 사람 수를 의미합니다.

    Returns:
        None:
            이 함수는 값을 반환하지 않고 frame에 글자만 그립니다.
    """
    # task별로 화면에 표시할 단어를 고릅니다.
    label = {
        "detect": "Detections",
        "segment": "Segmentation masks",
        "pose": "Pose persons",
    }[task]

    # cv2.putText:
    #   이미지 위에 텍스트를 쓰는 OpenCV 함수입니다.
    #
    # 주요 인자:
    #   frame              텍스트를 쓸 이미지
    #   f"{label}: {count}" 실제로 표시할 문자열
    #   (10, 30)           텍스트 시작 위치
    #   FONT_HERSHEY...    글꼴 종류
    #   0.8                글자 크기
    #   (0, 255, 255)      BGR 기준 노란색
    #   2                  글자 두께
    cv2.putText(
        frame,
        f"{label}: {count}",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 255),
        2,
    )


def get_result_count(task, result):
    """
    현재 TASK에 맞는 결과 개수를 계산합니다.

    Args:
        task:
            "detect", "segment", "pose" 중 하나입니다.

        result:
            YOLO 추론 결과 하나입니다.

    Returns:
        int:
            task가 detect이면 bounding box 개수,
            task가 segment이면 mask 개수,
            task가 pose이면 pose가 검출된 사람 수를 반환합니다.
    """
    # detect 모델 결과는 result.boxes에 들어 있습니다.
    if task == "detect":
        return 0 if result.boxes is None else len(result.boxes)

    # segment 모델 결과는 result.masks에 들어 있습니다.
    # result.masks.xy는 마스크 외곽선 좌표 목록입니다.
    if task == "segment":
        return 0 if result.masks is None else len(result.masks.xy)

    # pose 모델 결과는 result.keypoints에 들어 있습니다.
    # result.keypoints.xy는 사람별 keypoint 좌표 목록입니다.
    if task == "pose":
        return 0 if result.keypoints is None else len(result.keypoints.xy)

    # 혹시 모르는 task가 들어오면 안전하게 0을 반환합니다.
    return 0


def yolo_pipeline():
    """
    전체 YOLO 웹캠 파이프라인을 실행합니다.

    실행 순서:
        1. TASK 값이 올바른지 확인합니다.
        2. TASK에 맞는 YOLO 모델 파일명을 고릅니다.
        3. YOLO 모델을 로드합니다.
        4. 웹캠을 엽니다.
        5. 프레임을 계속 읽습니다.
        6. 프레임마다 YOLO 추론을 실행합니다.
        7. TASK에 맞게 결과를 시각화합니다.
        8. q 키를 누르면 종료합니다.

    Args:
        없음

    Returns:
        None:
            이 함수는 화면을 띄우고 루프를 실행하는 함수라 별도 값을 반환하지 않습니다.
    """
    # TASK가 MODEL_BY_TASK 딕셔너리에 없는 값이면 실행할 수 없습니다.
    # 예: TASK = "face"라고 쓰면 어떤 모델을 써야 할지 모르므로 에러를 냅니다.
    if TASK not in MODEL_BY_TASK:
        valid_tasks = ", ".join(MODEL_BY_TASK)
        raise ValueError(f"TASK는 {valid_tasks} 중 하나여야 합니다.")

    # TASK에 맞는 모델 파일명을 가져옵니다.
    # 예: TASK="pose"이면 model_path는 "yolov8n-pose.pt"가 됩니다.
    model_path = MODEL_BY_TASK[TASK]

    # YOLO(model_path):
    #   Ultralytics YOLO 모델을 불러옵니다.
    #   모델 파일이 현재 폴더에 없으면 자동 다운로드를 시도할 수 있습니다.
    model = YOLO(model_path)

    print(f"[INFO] TASK={TASK}")
    print(f"[INFO] MODEL={model_path}")

    # cv2.VideoCapture:
    #   카메라나 영상 파일을 여는 OpenCV 객체입니다.
    #   CAMERA_INDEX=0이면 기본 웹캠을 엽니다.
    cap = cv2.VideoCapture(CAMERA_INDEX)

    # 카메라가 정상적으로 열렸는지 확인합니다.
    # 열리지 않았는데 계속 진행하면 frame을 읽을 수 없습니다.
    if not cap.isOpened():
        raise RuntimeError(f"카메라 {CAMERA_INDEX}번을 열 수 없습니다.")

    # 카메라가 열려 있는 동안 계속 반복합니다.
    while cap.isOpened():
        # cap.read():
        #   카메라에서 프레임 한 장을 읽습니다.
        #
        # success:
        #   프레임을 잘 읽었으면 True, 실패하면 False
        #
        # frame:
        #   실제 카메라 이미지입니다.
        #   OpenCV 이미지이므로 NumPy 배열이고 BGR 순서입니다.
        success, frame = cap.read()
        if not success:
            break

        # model.predict:
        #   YOLO 추론을 실행합니다.
        #
        # frame:
        #   추론할 이미지입니다.
        #
        # stream=True:
        #   결과를 generator처럼 하나씩 처리합니다.
        #   웹캠/영상처럼 계속 들어오는 입력에서 메모리 효율이 좋습니다.
        #
        # conf=CONF_THRESHOLD:
        #   confidence가 기준보다 낮은 결과를 제거합니다.
        #
        # verbose=False:
        #   매 프레임마다 나오는 긴 로그를 줄입니다.
        #
        # results:
        #   YOLO 추론 결과입니다.
        #   stream=True라서 for문으로 하나씩 꺼내 사용합니다.
        results = model.predict(
            frame,
            stream=True,
            conf=CONF_THRESHOLD,
            verbose=False,
        )

        # results 안에는 현재 프레임의 추론 결과가 들어 있습니다.
        # 보통 웹캠 프레임 하나라 result도 하나씩 나옵니다.
        for result in results:
            # pose에서 기본 skeleton을 끄면 원하는 keypoint만 직접 그림
            if TASK == "pose" and not SHOW_POSE_DEFAULT_SKELETON:
                # frame.copy():
                #   원본 frame을 복사합니다.
                #   원본을 직접 수정하지 않고 복사본 위에 그림을 그리기 위해 사용합니다.
                annotated_frame = frame.copy()
            else:
                # result.plot():
                #   YOLO 결과를 이미지 위에 자동으로 그려줍니다.
                #
                # detect:
                #   bounding box와 label을 그립니다.
                #
                # segment:
                #   box, label, segmentation mask를 그립니다.
                #
                # pose:
                #   사람 box, skeleton, keypoint를 그립니다.
                annotated_frame = result.plot()

            # 현재 task에 맞는 결과 개수를 구합니다.
            count = get_result_count(TASK, result)

            # segment 모드에서는 마스크 외곽선을 초록색으로 한 번 더 그립니다.
            if TASK == "segment":
                count = draw_segmentation_contours(annotated_frame, result)

            # pose 모드에서는 원하는 keypoint 이름을 직접 표시합니다.
            elif TASK == "pose":
                draw_pose_keypoint_labels(annotated_frame, result)

            # 화면 왼쪽 위에 결과 개수를 표시합니다.
            draw_task_info(annotated_frame, TASK, count)

            # OpenCV 창에 최종 이미지를 보여줍니다.
            cv2.imshow(WINDOW_BY_TASK[TASK], annotated_frame)

        # cv2.waitKey(1):
        #   키 입력을 1ms 기다립니다.
        #
        # & 0xFF:
        #   OpenCV 키값 처리에서 자주 쓰는 안전 처리입니다.
        #
        # ord("q"):
        #   문자 q의 ASCII 코드입니다.
        #
        # 즉, q 키를 누르면 루프를 종료합니다.
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # 카메라 장치를 해제합니다.
    cap.release()

    # OpenCV로 띄운 모든 창을 닫습니다.
    cv2.destroyAllWindows()


if __name__ == "__main__":
    # 이 파일을 직접 실행했을 때만 yolo_pipeline()을 실행합니다.
    # 다른 파일에서 import할 때는 자동 실행되지 않게 막는 Python 관용구입니다.
    yolo_pipeline()
