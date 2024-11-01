import cv2

def configure_camera():
    camera = cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    camera.set(cv2.CAP_PROP_FPS, 60)
    return camera

def process_frame(frame, detect_meteors_func, add_satellite_data_func):
    satellite_data_to_add = []
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred_frame = cv2.GaussianBlur(gray_frame, (5, 5), 0)
    adaptive_thresh = cv2.adaptiveThreshold(blurred_frame, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    lines = cv2.HoughLinesP(adaptive_thresh, 1, np.pi / 180, threshold=100, minLineLength=15, maxLineGap=3)

    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            satellite_data_to_add.append((x1, y1, x2, y2))

    frame, meteors = detect_meteors_func(frame)
    add_satellite_data_func(satellite_data_to_add)
    return frame
