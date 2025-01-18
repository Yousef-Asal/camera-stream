import io
import logging
import socketserver
from threading import Condition
from http import server
from picamera2 import Picamera2, Preview
import numpy as np
import time

PAGE = """\
<html>
<head>
<title>Raspberry Pi - Surveillance Camera</title>
</head>
<body>
<center><h1>Raspberry Pi - Surveillance Camera</h1></center>
<center><img src="stream.mjpg" width="640" height="480"></center>
</body>
</html>
"""

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def update_frame(self, frame):
        """Update the frame when a new one is captured"""
        self.frame = frame
        with self.condition:
            self.condition.notify_all()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):  # New frame, notify clients
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

with Picamera2() as picam2:
    output = StreamingOutput()

    # Set the update_frame callback to handle the frames
    picam2.pre_callback = output.update_frame

    # Configure the camera with resolution, framerate, colour_space, and transform
    camera_config = {
        "resolution": (640, 480),
        "framerate": 24,
        "colour_space": 'YUV420',  # Added colour_space configuration
        "transform": 0  # No rotation or flip
    }
    
    picam2.configure(camera_config)

    # Start the camera preview
    picam2.start_preview(Preview.NULL)

    # Start capturing video
    picam2.start_recording(output, format="mjpeg")

    try:
        # Start the HTTP server for streaming
        address = ('', 8000)
        server = StreamingServer(address, StreamingHandler)
        print("Serving on http://0.0.0.0:8000")
        server.serve_forever()
    finally:
        picam2.stop_recording()
