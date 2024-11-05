from db_utils import init_db
from menu import display_menu
from Flask_server import start_flask_server
from threading import Thread
from streaming_func import start_camera_stream, start_night_sky_capture
from camera_utils import continuous_capture
import cv2

if __name__ == '__main__':

    # If it is nighttime activate this code when not actively capturing frames for tracking
    # start_night_sky_capture()

    # If it is daytime activate this code for streaming
    # start_camera_stream()

    # Start continuous capture
    continuous_capture()

    # Initialize the database
    init_db()

    # Start the Flask server in a separate thread
    flask_thread = Thread(target=start_flask_server)
    flask_thread.start()

    # Display the interactive menu
    display_menu()