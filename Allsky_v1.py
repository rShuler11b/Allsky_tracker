# """
# Satellite Tracking Program
#
# This program is designed to detect and track satellites and meteors using video feed from a camera.
# It processes frames to identify celestial objects, calculates their altitude and azimuth based on
# pixel coordinates, and stores relevant data in a SQLite database. The application integrates
# real-time video streaming, object detection algorithms, and geographical calculations to facilitate
# satellite observation.
#
# Key Features:
# - GPS location retrieval for camera positioning.
# - Calculation of satellite positions using TLE data.
# - Detection of meteors from video frames.
# - Storage of satellite and meteor data in a SQLite database.
# - Real-time video feed streaming via Flask.
#
# Author: Ryan Shuler
# Date: 10.24
#
# Email: Ryan.shuler11b@gmail.com
# GitHub: https://github.com/rShuler11b
# """
#
#
# # Required libraries (same as before)
# # Required libraries
# import cv2
# import numpy as np
# import sqlite3
# import time
# from flask import Flask, Response
# from threading import Thread
# from skyfield.api import load, Topos
# from datetime import datetime
# import gps
# from MetDetPy import MeteorDetection
#
#
# app = Flask(__name__)
#
# # Initialize the IMX462 camera
# camera = cv2.VideoCapture(0)
#
# # Set camera properties
# camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
# camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
# camera.set(cv2.CAP_PROP_FPS, 60)
#
# RESIZE_FACTOR = 0.5  # Adjustable resolution factor
# frame_skip_count = 5  # Frame skipping for processing efficiency
#
# BATCH_SIZE = 10
# satellite_data_batch = []
# meteor_data_batch = []
#
# # Function to get GPS location
# def get_location():
#     """
#     Get the current GPS location (latitude and longitude).
#
#     This function starts a GPS session, reads the GPS data stream, and extracts the latitude and longitude if available.
#
#     :return: A tuple (latitude, longitude) containing the GPS coordinates. Returns (None, None) if the location is unavailable.
#     """
#     try:
#         session = gps.gps()  # Create a new GPS session
#         session.stream(gps.WATCH_ENABLE)  # Enable the GPS data stream
#
#         # Read GPS data
#         report = session.next()
#
#         # Check if report contains latitude and longitude data
#         if report['class'] == 'TPV':
#             latitude = report.lat
#             longitude = report.lon
#             return latitude, longitude
#     except Exception as e:
#         print(f"Error getting GPS location: {e}")
#
#     return None, None  # Return None if unable to get location
#
#
# # Get GPS location
# latitude_degrees, longitude_degrees = get_location()
# if latitude_degrees is None or longitude_degrees is None:
#     print("Failed to get GPS location, using default coordinates.")
#     latitude_degrees, longitude_degrees = 0.0, 0.0  # Set default or prompt user
#
# # Time scale and observer location setup
# ts = load.timescale()
# camera_location = Topos(latitude_degrees, longitude_degrees)
#
# # Same database initialization function
# def init_db():
#     """
#     Initialize the SQLite database for storing satellite and meteor data.
#
#     This function creates two tables if they do not exist: 'satellites' and 'meteors'.
#     - 'satellites' table stores information about satellite observations, including id, name, timestamp, altitude, azimuth, and location.
#     - 'meteors' table stores information about meteor detections, including id, timestamp, altitude, azimuth, and location.
#
#     :return: None
#     """
#     conn = sqlite3.connect('satellite_data.db')
#     cursor = conn.cursor()
#     cursor.execute('''CREATE TABLE IF NOT EXISTS satellites (
#         id INTEGER PRIMARY KEY,
#         name TEXT,
#         time_passed TIMESTAMP,
#         alt REAL,
#         az REAL,
#         location TEXT
#     )''')
#     cursor.execute('''CREATE TABLE IF NOT EXISTS meteors (
#         id INTEGER PRIMARY KEY,
#         time_detected TIMESTAMP,
#         alt REAL,
#         az REAL,
#         location TEXT
#     )''')
#     conn.commit()
#     conn.close()
#
# # Add satellite data to the database with sky coordinates
# def add_satellite_data_batch(data):
#     """
#     Add a batch of satellite data to the database.
#
#     This function appends new satellite data to the global batch. When the batch reaches the defined BATCH_SIZE,
#     it inserts the data into the 'satellites' table in the SQLite database. After insertion, the batch is cleared.
#
#     :param data: A list of tuples, where each tuple contains satellite data (name, time_passed, alt, az, location).
#     :return: None
#     """
#     global satellite_data_batch
#     satellite_data_batch.extend(data)
#
#     if len(satellite_data_batch) >= BATCH_SIZE:
#         conn = sqlite3.connect('satellite_data.db')
#         cursor = conn.cursor()
#         cursor.executemany('''INSERT INTO satellites (name, time_passed, alt, az, location) VALUES (?, ?, ?, ?, ?)''',
#                            satellite_data_batch)
#         conn.commit()
#         conn.close()
#         satellite_data_batch = []
#
# # Add meteor data to the database with sky coordinates
# def add_meteor_data_batch(data):
#     """
#     Add a batch of meteor data to the database.
#
#     This function appends new meteor data to the global batch. When the batch reaches the defined BATCH_SIZE,
#     it inserts the data into the 'meteors' table in the SQLite database. After insertion, the batch is cleared.
#
#     :param data: A list of tuples, where each tuple contains meteor data (time_detected, alt, az, location).
#     :return: None
#     """
#     global meteor_data_batch
#     meteor_data_batch.extend(data)
#
#     if len(meteor_data_batch) >= BATCH_SIZE:
#         conn = sqlite3.connect('satellite_data.db')
#         cursor = conn.cursor()
#         cursor.executemany('''INSERT INTO meteors (time_detected, alt, az, location) VALUES (?, ?, ?, ?)''',
#                            meteor_data_batch)
#         conn.commit()
#         conn.close()
#         meteor_data_batch = []
#
#
# def count_meteors():
#     """
#     Count the total number of meteors detected.
#
#     This function connects to the database, retrieves the total count of meteors from the
#     meteors table, and returns that count.
#
#     :return: The total number of meteors detected.
#     """
#     conn = sqlite3.connect('satellite_data.db')
#     cursor = conn.cursor()
#     cursor.execute('SELECT COUNT(*) FROM meteors')
#     total_count = cursor.fetchone()[0]
#     conn.close()
#     return total_count
#
#
# def count_meteors_last_24():
#     """
#     Count the number of meteors detected in the last 24 hours.
#
#     This function connects to the database, retrieves the count of meteors from the meteors
#     table that were detected in the last 24 hours, and returns that count.
#
#     :return: The number of meteors detected in the last 24 hours.
#     """
#     conn = sqlite3.connect('satellite_data.db')
#     cursor = conn.cursor()
#     cursor.execute('SELECT COUNT(*) FROM meteors WHERE time_detected > datetime("now", "-1 day")')
#     last_24_count = cursor.fetchone()[0]
#     conn.close()
#     return last_24_count
#
#
# def custom_query():
#     """
#     Allow the user to execute a custom SQL query on the database.
#
#     This function prompts the user for an SQL query, executes it against the satellite_data.db
#     database, and displays the results. Error handling is included to manage any SQL errors.
#
#     Note: Remove custom query before submission.
#
#     :return: None
#     """
#     conn = sqlite3.connect('satellite_data.db')
#     cursor = conn.cursor()
#
#     query = input("Enter your SQL query: ")
#
#     try:
#         cursor.execute(query)
#         results = cursor.fetchall()
#
#         if results:
#             for row in results:
#                 print(row)  # Print each result row
#         else:
#             print("No results found.")
#     except sqlite3.Error as e:
#         print(f"An error occurred: {e}")  # Print error message
#
#     conn.close()
#
# # Load TLE data for satellite identification (same as before)
# def load_tle_data():
#     """
#     Load TLE (Two-Line Element) data for satellite identification.
#
#     This function retrieves TLE data from a specified URL, loads it, and creates a dictionary that maps satellite names
#     to their corresponding TLE objects.
#
#     :return: A dictionary where keys are satellite names and values are satellite objects from the TLE data.
#     """
#     print("Loading TLE data...")
#     satellites = load.tle_file('http://celestrak.com/NORAD/elements/stations.txt')
#     satellite_by_name = {sat.name: sat for sat in satellites}
#     return satellite_by_name
#
# # Global variables for satellite tracking and TLE data
# satellite_counter = 0
# satellite_by_name = load_tle_data()
#
# # Define the threshold for satellite identification
# ALTITUDE_THRESHOLD = 10.0  # Allowable deviation in altitude (in degrees)
# AZIMUTH_THRESHOLD = 10.0   # Allowable deviation in azimuth (in degrees)
#
# def within_threshold(track_position, observed_position):
#     """
#     Check if the observed satellite position is within the threshold of the track position.
#
#     :param track_position: A tuple (altitude, azimuth) of the camera's tracking position.
#     :param observed_position: A tuple (altitude, azimuth) of the satellite's observed position.
#     :return: True if the observed position is within the threshold; otherwise, False.
#     """
#     track_alt, track_az = track_position
#     observed_alt, observed_az = observed_position
#
#     alt_diff = abs(track_alt - observed_alt)
#     az_diff = abs(track_az - observed_az)
#
#     return alt_diff <= ALTITUDE_THRESHOLD and az_diff <= AZIMUTH_THRESHOLD
#
# # Function to match satellite track with TLE data and compute sky coordinates
# def identify_satellite(track_position, timestamp, location):
#     """
#     Identify a satellite by matching its track with TLE data and compute its sky coordinates.
#
#     This function takes the camera's tracking position, timestamp, and location, then iterates over the loaded
#     TLE data to find a matching satellite based on its calculated altitude and azimuth at the specified time.
#     If a match is found within a defined threshold, it returns the satellite's name and sky coordinates.
#
#     :param track_position: A tuple (altitude, azimuth) representing the camera's tracking position.
#     :param timestamp: A datetime object representing the time the observation was made.
#     :param location: A tuple (latitude, longitude) representing the camera's GPS location.
#     :return: A tuple (satellite_name, altitude, azimuth) if a match is found. Returns ("Unknown Satellite", None, None) if no match is found.
#     """
#     ts = load.timescale()
#     t = ts.utc(*timestamp.timetuple()[:6])
#
#     # Use location (latitude, longitude) to define the camera's location
#     camera_location = Topos(latitude_degrees=location[0], longitude_degrees=location[1])
#
#     for name, satellite in satellite_by_name.items():
#         difference = satellite - camera_location
#         topocentric = difference.at(t)
#         alt, az, _ = topocentric.altaz()
#
#         if within_threshold(track_position, (alt.degrees, az.degrees)):
#             return name, alt.degrees, az.degrees
#
#     return "Unknown Satellite", None, None
#
# # Detect meteors and calculate sky coordinates
# def detect_meteors(frame):
#     """
#     Detect meteors in a video frame and calculate their sky coordinates.
#
#     This function processes an image frame to detect potential meteors using contour detection.
#     For each detected meteor, it calculates the sky coordinates (altitude and azimuth) and adds the result
#     to the database in batch format.
#
#     :param frame: A single video frame (image) from the camera feed in BGR format.
#     :return: The frame with detected meteor positions marked by red circles.
#     """
#     detected_meteors = []
#     gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#     blurred_frame = cv2.GaussianBlur(gray_frame, (5, 5), 0)
#     _, thresholded_frame = cv2.threshold(blurred_frame, 200, 255, cv2.THRESH_BINARY)
#
#     contours, _ = cv2.findContours(thresholded_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#
#     for contour in contours:
#         if cv2.contourArea(contour) > 100:
#             M = cv2.moments(contour)
#             if M["m00"] != 0:
#                 cX = int(M["m10"] / M["m00"])
#                 cY = int(M["m01"] / M["m00"])
#
#                 timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
#                 alt, az = calculate_alt_az(timestamp, cX, cY)
#                 detected_meteors.append((timestamp, alt, az, f"({cX}, {cY})"))
#                 cv2.circle(frame, (cX, cY), 10, (0, 0, 255), -1)
#
#     add_meteor_data_batch(detected_meteors)
#     return frame
#
# # # Calculate altitude and azimuth from frame coordinates
# # def calculate_alt_az():
# #     t = ts.utc(*datetime.utcnow().timetuple()[:6])
# #     difference = camera_location - Topos(latitude_degrees, longitude_degrees)
# #     topocentric = difference.at(t)
# #     alt, az, _ = topocentric.altaz()
# #     return alt.degrees, az.degrees
#
# """
# Calculate altitude and azimuth from frame coordinates.
#
# This function computes the altitude and azimuth based on the current time and the pixel coordinates
# of the detected meteor in the frame.
#
# :param timestamp: A string representing the current UTC timestamp.
# :param x: The x-coordinate (pixel) of the detected meteor in the frame.
# :param y: The y-coordinate (pixel) of the detected meteor in the frame.
# :param frame_width: The width of the frame (in pixels).
# :param frame_height: The height of the frame (in pixels).
# :param fov: The field of view of the camera (in degrees).
# :return: A tuple containing the altitude and azimuth in degrees.
# """
#
#
# def calculate_alt_az(timestamp, x, y, frame_width, frame_height, fov):
#     """
#     Calculate the altitude and azimuth based on pixel coordinates in the frame.
#
#     This function converts pixel coordinates (x, y) from a video frame into angular coordinates
#     (altitude and azimuth) relative to a defined field of view (FOV). The calculations account for
#     the camera's location and ensure that the resulting values are within valid ranges.
#
#     :param timestamp: The current timestamp (not used in calculations but provided for consistency).
#     :param x: The x-coordinate (horizontal pixel position) in the frame.
#     :param y: The y-coordinate (vertical pixel position) in the frame.
#     :param frame_width: The width of the video frame in pixels.
#     :param frame_height: The height of the video frame in pixels.
#     :param fov: The field of view in degrees, defining the extent of the observable area.
#
#     :return: A tuple (altitude, azimuth) in degrees, representing the calculated angular coordinates.
#     """
#     # Convert the current time to UTC using Skyfield's timescale
#     t = ts.utc(*datetime.utcnow().timetuple()[:6])
#
#     # Calculate the angular coordinates based on the pixel position and FOV
#     az = (x / frame_width) * fov - (fov / 2)  # Convert x to azimuth
#     alt = (1 - (y / frame_height)) * fov - (fov / 2)  # Convert y to altitude
#
#     # Ensure that azimuth and altitude are within valid ranges
#     az = az % 360  # Normalize azimuth to be between 0 and 360 degrees
#     alt = max(0, min(alt, 90))  # Altitude should be between 0 and 90 degrees
#
#     # Define the camera's location in Topos using pre-defined latitude and longitude
#     difference = camera_location - Topos(latitude_degrees, longitude_degrees)
#
#     # Get the topocentric (observer-relative) position of the satellite at the current time
#     topocentric = difference.at(t)
#
#     # Optionally, you can calculate the altitude and azimuth of a satellite here if needed
#     alt, az, _ = topocentric.altaz()
#
#     # Return calculated altitude and azimuth in degrees
#     return alt, az
#
#
# # Process each frame and calculate sky coordinates
# def process_frame(frame):
#     """
#     Process a video frame to detect satellites and meteors.
#
#     This function performs image processing on the provided frame to detect satellite positions based on
#     Hough Line Transform and also detects meteors using a separate detection method. The results are
#     appended to the satellite data for database storage.
#
#     :param frame: The image frame captured from the camera, represented as a NumPy array.
#     :return: The processed frame with detected satellites and meteors marked.
#     """
#     global satellite_counter
#     satellite_data_to_add = []
#
#     gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#     blurred_frame = cv2.GaussianBlur(gray_frame, (5, 5), 0)
#     adaptive_thresh = cv2.adaptiveThreshold(blurred_frame, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
#                                             cv2.THRESH_BINARY, 11, 2)
#
#     lines = cv2.HoughLinesP(adaptive_thresh, 1, np.pi / 180, threshold=100, minLineLength=15, maxLineGap=3)
#
#     if lines is not None:
#         for line in lines:
#             x1, y1, x2, y2 = line[0]
#             cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
#             satellite_counter += 1
#             timestamp = datetime.utcnow()
#             satellite_name, alt, az = identify_satellite((x1, y1), timestamp, f"({x1}, {y1})")
#             satellite_data_to_add.append((satellite_name, time.strftime('%Y-%m-%d %H:%M:%S'), alt, az, f"({x1}, {y1})"))
#
#     frame = detect_meteors(frame)
#     add_satellite_data_batch(satellite_data_to_add)
#     return frame
#
# # Flask video stream
# def generate_frames():
#     """
#     Generate frames for video streaming in a Flask application.
#
#     This function continuously captures frames from the camera, processes them to detect
#     satellites and meteors, resizes the frames for efficient streaming, and encodes them in
#     JPEG format for transmission over HTTP.
#
#     Yields:
#         bytes: A byte stream of the processed frames for video streaming.
#     """
#     frame_count = 0
#     while True:
#         ret, frame = camera.read()
#         if ret:
#             frame_count += 1
#             if frame_count % frame_skip_count == 0:
#                 frame = cv2.resize(frame, None, fx=RESIZE_FACTOR, fy=RESIZE_FACTOR)
#                 processed_frame = process_frame(frame)
#
#                 _, buffer = cv2.imencode('.jpg', processed_frame)
#                 frame = buffer.tobytes()
#
#                 yield (b'--frame\r\n'
#                        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
#
# @app.route('/video_feed')
# def video_feed():
#     """
#      Generate a video feed for streaming.
#
#      This function creates a Flask response that streams video frames using the
#      generate_frames() generator function. The response is set with the appropriate
#      MIME type for streaming video, allowing the client to display the video feed
#      in real-time.
#
#      :return: A Flask Response object containing the video stream.
#      """
#     return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
#
# # Count satellites detected
# def count_satellites():
#     """
#     Count the number of satellites detected from the database.
#
#     This function retrieves the total count of satellites stored in the database and the count of
#     satellites detected in the last 24 hours.
#
#     Returns:
#         tuple: A tuple containing two integers:
#             - total_count: The total number of satellites detected.
#             - last_24_hours_count: The number of satellites detected in the last 24 hours.
#     """
#     conn = sqlite3.connect('satellite_data.db')
#     cursor = conn.cursor()
#     cursor.execute('SELECT COUNT(*) FROM satellites')
#     total_count = cursor.fetchone()[0]
#
#     cursor.execute('SELECT COUNT(*) FROM satellites WHERE time_passed > datetime("now", "-1 day")')
#     last_24_hours_count = cursor.fetchone()[0]
#
#     conn.close()
#     return total_count, last_24_hours_count
#
# # Command-line menu for querying satellites and meteors
# def display_menu():
#     """
#     Display a menu for the satellite tracking system.
#
#     This function presents a command-line menu to the user, allowing them to select options to
#     retrieve counts of satellites and meteors detected, as well as perform custom SQL queries.
#     The menu will continue to display until the user chooses to exit.
#     """
#     while True:
#         print("\n==== Satellite Tracker Menu ====")
#         print("1. Total satellites detected")
#         print("2. Satellites detected in the last 24 hours")
#         print("3. Total meteors detected")
#         print("4. Meteors detected in the last 24 hours")
#         print("5. Custom SQL query")
#         print("6. Exit")
#
#         choice = input("Select an option: ")
#
#         if choice == '1':
#             total, _ = count_satellites()
#             print(f"Total satellites detected: {total}")
#         elif choice == '2':
#             _, last_24 = count_satellites()
#             print(f"Satellites detected in the last 24 hours: {last_24}")
#         elif choice == '3':
#             total_meteors = count_meteors()  # Get total meteors count
#             print(f"Total meteors detected: {total_meteors}")
#         elif choice == '4':
#             last_24_meteors = count_meteors_last_24()  # Get last 24 hours meteors count
#             print(f"Meteors detected in the last 24 hours: {last_24_meteors}")
#         elif choice == '5':
#             custom_query()  # Allow user to perform a custom SQL query
#         elif choice == '6':
#             break  # Exit the menu
#         else:
#             print("Invalid option. Please try again.")
#
# if __name__ == '__main__':
#     init_db()
#
#     # Start the Flask web server in a separate thread
#     flask_thread = Thread(target=lambda: app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False))
#     flask_thread.start()
#
#     # Start the menu for querying satellite data
#     display_menu()
#
#     # Release the camera when done
#     camera.release()
#
