from picamera2 import Picamera2
from picamera2.previews import MjpgServer
import time
from http.server import SimpleHTTPRequestHandler, HTTPServer

# Initialize the Picamera2 object
picam2 = Picamera2()

# Set the resolution and framerate directly (this is the minimal configuration)
picam2.configure(picam2.create_preview_configuration(main={"size": (640, 480)}, lores={"size": (320, 240)}))

# Start the camera preview
picam2.start_preview()

# Start the MJPEG stream (you can display this in a browser)
server = MjpgServer(picam2, port=8000)
server.start()

# Set up the HTTP server for serving the page
address = ('', 8000)
httpd = HTTPServer(address, SimpleHTTPRequestHandler)

print("Serving on port 8000...")

# Keep the script running to serve both the MJPEG stream and the HTTP server
try:
    while True:
        httpd.handle_request()
        time.sleep(1)
except KeyboardInterrupt:
    picam2.stop_preview()
    server.stop()
    print("Server stopped.")
