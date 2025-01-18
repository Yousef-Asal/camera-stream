from picamera2 import Picamera2, Preview
from http.server import BaseHTTPRequestHandler, HTTPServer
import io
from threading import Condition

class StreamingOutput:
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def update_frame():
        buffer = picam2.capture_buffer("main")
        print(f"Captured frame of size: {len(buffer)} bytes")  # Debugging line
        output.update_frame(buffer)

class StreamingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/stream.mjpg':
            self.send_response(200)
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
            except Exception as e:
                print(f"Streaming client disconnected: {e}")
        else:
            self.send_error(404)
            self.end_headers()

# Initialize the camera
picam2 = Picamera2()
config = picam2.create_video_configuration({"size": (640, 480)})
picam2.configure(config)
output = StreamingOutput()

# Callback to update the output frame
def update_frame():
    buffer = picam2.capture_buffer("main")
    output.update_frame(buffer)

picam2.pre_callback = update_frame
picam2.start()

# Start the server
server = HTTPServer(('0.0.0.0', 8000), StreamingHandler)
print("Streaming on port 8000...")
try:
    server.serve_forever()
finally:
    picam2.stop()
