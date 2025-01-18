from picamera2 import Picamera2
import time
from http.server import SimpleHTTPRequestHandler, HTTPServer
import io
import threading

# Initialize the Picamera2 object
picam2 = Picamera2()

# Set the resolution and framerate directly (this is the minimal configuration)
picam2.configure(picam2.create_preview_configuration(main={"size": (640, 480)}, lores={"size": (320, 240)}))

# Start the camera preview
picam2.start_preview()

# Function to handle MJPEG stream
def stream_mjpeg():
    with HTTPServer(('', 8000), SimpleHTTPRequestHandler) as server:
        print("Serving MJPEG stream on http://localhost:8000/stream.mjpg")
        server.serve_forever()

# Function to capture frames and send them as MJPEG
def capture_frames():
    while True:
        # Capture a frame from the camera
        frame = picam2.capture_array()
        # Encode the frame as JPEG
        with io.BytesIO() as output:
            picam2.encode_image(frame, 'jpeg', output)
            frame_data = output.getvalue()
        
        # Send the frame data as MJPEG (you can adapt this to your needs)
        # For now, this is the placeholder for the MJPEG loop
        
        time.sleep(1/24)  # 24 fps (adjust as necessary)

# Start the MJPEG stream in a separate thread
stream_thread = threading.Thread(target=stream_mjpeg)
stream_thread.daemon = True
stream_thread.start()

# Capture frames in the main thread
capture_frames()
