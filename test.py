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
        'ffmpeg', '-re', '-i', '-', '-vcodec', 'copy', '-an', '-f', 'mpegts', 'http://localhost:8000/stream'
    ]

    # Run libcamera-vid and ffmpeg in subprocesses
    libcamera_process = subprocess.Popen(libcamera_cmd, stdout=subprocess.PIPE)
    ffmpeg_process = subprocess.Popen(ffmpeg_cmd, stdin=libcamera_process.stdout)

    # Wait for the processes to finish
    libcamera_process.wait()
    ffmpeg_process.wait()

# Function to handle HTTP server (for MJPEG or raw streams)
def run_http_server():
    with HTTPServer(('', 8000), SimpleHTTPRequestHandler) as server:
        print("Serving video stream on http://localhost:8000/stream")
        server.serve_forever()

# Start the video stream in a separate thread
video_thread = threading.Thread(target=start_video_stream)
video_thread.daemon = True
video_thread.start()

# Start the HTTP server to serve the video stream
run_http_server()
