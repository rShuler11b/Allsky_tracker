from flask import Flask, Response
from camera_utils import process_frame, capture_frame  # Only need capture_frame and process_frame

app = Flask(__name__)


def start_flask_server():
    from threading import Thread
    flask_thread = Thread(target=lambda: app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False))
    flask_thread.start()


def generate_frames():
    frame_skip_count = 5
    RESIZE_FACTOR = 0.5
    frame_count = 0

    while True:
        # Use capture_frame() to get the frame directly
        frame = capture_frame()  # No need for camera object since we're using libcamera directly

        # Resize and process the frame if needed
        frame_count += 1
        if frame_count % frame_skip_count == 0:
            frame = cv2.resize(frame, None, fx=RESIZE_FACTOR, fy=RESIZE_FACTOR)
            processed_frame = process_frame(frame)

            _, buffer = cv2.imencode('.jpg', processed_frame)  # Encode for streaming
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')



