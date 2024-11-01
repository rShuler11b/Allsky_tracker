from picamera2 import Picamera2, Preview
import time

def start_night_sky_capture():
    # Initialize the camera
    picam2 = Picamera2()
    config = picam2.create_still_configuration(main={"size": (1920, 1080), "format": "RGB888"})  # Max resolution
    picam2.configure(config)

    # Set controls for low-light night sky capture
    picam2.set_controls({
        "ExposureTime": 1000000,  # 1-second exposure, adjust based on sky brightness
        "AnalogueGain": 8.0,      # Higher ISO for star visibility
        "FrameRate": 1,           # Set low frame rate or disable it
        "AwbEnable": False,       # Disable auto white balance for consistency
        "AeEnable": False         # Disable auto exposure to allow manual control
    })

    # Start the preview in a window
    picam2.start_preview(Preview.QTGL)
    picam2.start()

    print("Capturing the night sky... Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)  # Maintain a slow loop for long exposure
    except KeyboardInterrupt:
        print("Stopping the capture.")
    finally:
        picam2.stop()


def start_camera_stream():
    # Initialize the camera
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"size": (1920, 1080), "format": "RGB888", "fps": 30})  # Set higher FPS
    picam2.configure(config)

    # Set controls to reduce motion blur
    picam2.set_controls({"ExposureTime": 5000, "AnalogueGain": 2.0})  # Adjust as needed

    # Start the preview in its own window
    picam2.start_preview(Preview.QTGL)
    picam2.start()

    print("Streaming... Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping the stream.")
    finally:
        picam2.stop()