import cv2
import subprocess
from flask import Flask, Response

app = Flask(__name__)

# Open the camera using OpenCV (you can change this to your camera source)
cap = cv2.VideoCapture(0)

# Check if the camera opened successfully
if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

# FFmpeg command for streaming
ffmpeg_command = [
    "ffmpeg",
    "-y",  # Overwrite output file if it exists
    "-f", "rawvideo",  # Input format
    "-vcodec", "rawvideo",  # Input codec
    "-pix_fmt", "bgr24",  # Pixel format
    "-s", "640x480",  # Resolution
    "-r", "24",  # Frames per second
    "-i", "-",  # Input from stdin
    "-c:v", "libx264",  # Video codec
    "-f", "mpegts",  # Output format
    "http://127.0.0.1:8080/stream"  # Output stream URL
]

# Start the FFmpeg process
ffmpeg_process = subprocess.Popen(ffmpeg_command, stdin=subprocess.PIPE)

def generate_video():
    while True:
        # Capture frame-by-frame from the camera
        ret, frame = cap.read()
        if not ret:
            break

        # Write the frame to FFmpeg's stdin
        ffmpeg_process.stdin.write(frame.tobytes())

        # Yield the frame for streaming via Flask
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + cv2.imencode('.jpg', frame)[1].tobytes() + b'\r\n')

@app.route('/stream')
def stream_video():
    return Response(generate_video(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return "Streaming video at <a href='/stream'>/stream</a>"

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)
