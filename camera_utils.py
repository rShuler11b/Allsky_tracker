import subprocess
from PIL import Image
import cv2
import numpy as np

def capture_frame():
    # Capture an image using libcamera-still and load it into OpenCV
    subprocess.run(["libcamera-still", "-o", "/tmp/libcamera_frame.jpg", "--width", "1920", "--height", "1080", "--timeout", "1", "-n"])
    pil_image = Image.open("/tmp/libcamera_frame.jpg")
    frame = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)  # Convert to OpenCV format
    return frame

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
