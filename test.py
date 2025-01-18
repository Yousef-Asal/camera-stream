import subprocess
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer

# Function to start libcamera-vid and stream via HTTP
def start_video_stream():
    # Start libcamera-vid to capture video stream and pipe it to ffmpeg for HTTP serving
    libcamera_cmd = [
        'libcamera-vid', '--width', '640', '--height', '480', '--framerate', '24', '--inline',
        '--output', '-'
    ]
    
    # Using ffmpeg to stream the output as H.264 over HTTP
    ffmpeg_cmd = [
        'ffmpeg', '-re', '-i', '-', '-vcodec', 'copy', '-an', '-f', 'mpegts', 'http://127.0.0.1:8080/stream'
    ]

    # Run libcamera-vid and ffmpeg in subprocesses
    libcamera_process = subprocess.Popen(libcamera_cmd, stdout=subprocess.PIPE)
    ffmpeg_process = subprocess.Popen(ffmpeg_cmd, stdin=libcamera_process.stdout)

    # Wait for the processes to finish
    libcamera_process.wait()
    ffmpeg_process.wait()

# Function to handle HTTP server (for MJPEG or raw streams)
def run_http_server():
    # This handler serves the video stream as it is
    class VideoStreamHandler(SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/stream':
                self.send_response(200)
                self.send_header('Content-type', 'video/mp2t')
                self.end_headers()
                with open('/dev/null', 'rb') as f:
                    while True:
                        data = f.read(1024)
                        if not data:
                            break
                        self.wfile.write(data)
            else:
                super().do_GET()

    with HTTPServer(('', 8080), VideoStreamHandler) as server:
        print("Serving video stream on http://localhost:8080/stream")
        server.serve_forever()

# Start the video stream in a separate thread
video_thread = threading.Thread(target=start_video_stream)
video_thread.daemon = True
video_thread.start()

# Start the HTTP server to serve the video stream
run_http_server()
