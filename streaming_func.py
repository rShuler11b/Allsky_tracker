from picamera2 import Picamera2, Preview
import time

def start_night_sky_capture():
    # Initialize the camera
    picam2 = Picamera2()
    config = picam2.create_still_configuration(main={"size": (1920, 1080), "format": "XBGR8888"})  # Compatible format
    picam2.configure(config)

    # Set controls for preview in low-light mode
    picam2.set_controls({
        "ExposureTime": 500000,           # Half-second exposure for live preview
        "AnalogueGain": 4.0,              # Moderate gain for visibility in preview
        "FrameDurationLimits": (33333, 1000000),  # Range allowing up to ~30 fps
        "AwbEnable": False,
        "AeEnable": False
    })

    # Start the preview
    picam2.start_preview(Preview.QTGL)
    picam2.start()

    print("Capturing the night sky... Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)  # Slow loop for long exposure
    except KeyboardInterrupt:
        print("Stopping the capture.")
    finally:
        picam2.stop()

    # Switch to long exposure for still capture if needed
    picam2.set_controls({
        "ExposureTime": 1000000,  # 1-second exposure
        "AnalogueGain": 8.0       # Higher gain for night visibility
    })


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
    config = picam2.create_preview_configuration(main={"size": (1920, 1080), "format": "XBGR8888"})  # Set resolution and format
    picam2.configure(config)

    # Set controls to reduce motion blur and achieve a high frame rate
    picam2.set_controls({
        "ExposureTime": 5000,             # Shorter exposure to reduce motion blur
        "AnalogueGain": 2.0,              # Lower gain for clarity
        "FrameDurationLimits": (33333, 33333)  # Set frame rate to ~30 fps in microseconds
    })

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