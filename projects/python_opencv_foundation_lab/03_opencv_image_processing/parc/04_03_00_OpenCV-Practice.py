import cv2
import numpy as np


def nothing(_):
    pass


def make_odd_kernel(value):
    value = max(1, value)
    return value if value % 2 == 1 else value + 1


def color_detection_pipeline(camera_index=0):
    """웹캠 영상에서 HSV 범위에 맞는 색 영역을 추출한다."""
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print(f"카메라를 열 수 없습니다. camera_index={camera_index}")
        return

    cv2.namedWindow("Control")

    # OpenCV HSV 범위: H 0~179, S/V 0~255
    # 초기값은 초록색 계열 예시다.
    cv2.createTrackbar("H Min", "Control", 35, 179, nothing)
    cv2.createTrackbar("H Max", "Control", 85, 179, nothing)
    cv2.createTrackbar("S Min", "Control", 50, 255, nothing)
    cv2.createTrackbar("S Max", "Control", 255, 255, nothing)
    cv2.createTrackbar("V Min", "Control", 50, 255, nothing)
    cv2.createTrackbar("V Max", "Control", 255, 255, nothing)
    cv2.createTrackbar("Min Area", "Control", 900, 10000, nothing)
    cv2.createTrackbar("Morph K", "Control", 3, 31, nothing)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("프레임을 읽지 못했습니다.")
                break

            h_min = cv2.getTrackbarPos("H Min", "Control")
            h_max = cv2.getTrackbarPos("H Max", "Control")
            s_min = cv2.getTrackbarPos("S Min", "Control")
            s_max = cv2.getTrackbarPos("S Max", "Control")
            v_min = cv2.getTrackbarPos("V Min", "Control")
            v_max = cv2.getTrackbarPos("V Max", "Control")
            min_area = cv2.getTrackbarPos("Min Area", "Control")
            morph_k = make_odd_kernel(cv2.getTrackbarPos("Morph K", "Control"))

            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            if h_min <= h_max:
                lower = np.array([h_min, s_min, v_min])
                upper = np.array([h_max, s_max, v_max])
                mask = cv2.inRange(hsv, lower, upper)
            else:
                # 빨간색처럼 H 범위가 179 -> 0을 넘어가는 경우 처리한다.
                mask1 = cv2.inRange(
                    hsv,
                    np.array([h_min, s_min, v_min]),
                    np.array([179, s_max, v_max]),
                )
                mask2 = cv2.inRange(
                    hsv,
                    np.array([0, s_min, v_min]),
                    np.array([h_max, s_max, v_max]),
                )
                mask = cv2.bitwise_or(mask1, mask2)

            kernel = np.ones((morph_k, morph_k), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            result = frame.copy()

            for contour in contours:
                area = cv2.contourArea(contour)
                if area < min_area:
                    continue

                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(result, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.putText(
                    result,
                    "target color",
                    (x, y - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 0, 255),
                    2,
                )

            color_only = cv2.bitwise_and(frame, frame, mask=mask)

            cv2.imshow("Original Video", result)
            cv2.imshow("Mask", mask)
            cv2.imshow("Color Only", color_only)

            if cv2.waitKey(25) & 0xFF == ord("q"):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    color_detection_pipeline()
