import cv2
import numpy as np
from flask import Flask, render_template, Response
import threading
import time

app = Flask(__name__)

# Global variables for the video stream
output_frame = None
lock = threading.Lock()

# Initialize the camera
cap = cv2.VideoCapture(0)

# Set the resolution to 640x480
cap.set(3, 640)
cap.set(4, 480)

def capture_frame():
    global output_frame, lock
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        # Convert frame to RGB (Flask's render_template expects RGB)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Lock the frame variable so that it can be updated safely
        with lock:
            output_frame = frame

        # Print statement indicating that a new frame is captured
        print("New frame captured")

        # Sleep to reduce CPU load
        time.sleep(0.1)

def generate():
    global output_frame, lock
    while True:
        if output_frame is not None:
            # Ensure that the frame is locked before sending it to the client
            with lock:
                # Encode the frame as JPEG
                ret, jpeg = cv2.imencode('.jpg', output_frame)
                if ret:
                    # Convert the encoded frame to bytes
                    frame = jpeg.tobytes()

                    # Print statement indicating the frame is being sent
                    print("Sending frame to client")

                    # Yield the frame as a multipart HTTP response
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stream')
def stream():
    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    # Start the capture frame thread
    capture_thread = threading.Thread(target=capture_frame)
    capture_thread.daemon = True
    capture_thread.start()

    # Start the Flask app
    app.run(host='0.0.0.0', port=8080, debug=False)
