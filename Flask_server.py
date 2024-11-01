from flask import Flask, Response
from camera_utils import process_frame, configure_camera

app = Flask(__name__)
camera = configure_camera()

def start_flask_server():
    from threading import Thread
    flask_thread = Thread(target=lambda: app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False))
    flask_thread.start()

def generate_frames():
    frame_skip_count = 5
    RESIZE_FACTOR = 0.5
    frame_count = 0

    while True:
        ret, frame = camera.read()
        if ret:
            frame_count += 1
            if frame_count % frame_skip_count == 0:
                frame = cv2.resize(frame, None, fx=RESIZE_FACTOR, fy=RESIZE_FACTOR)
                processed_frame = process_frame(frame)
                _, buffer = cv2.imencode('.jpg', processed_frame)
                frame = buffer.tobytes()

                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
