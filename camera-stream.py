from flask import Flask, Response
from picamzero import Camera
import io

app = Flask(__name__)

# Initialize the Camera
camera = Camera()
camera.resolution = (640, 480)  # Set resolution
camera.framerate = 30  # Set framerate

def generate_frames():
    while True:
        # Capture frame as bytes
        frame = camera.capture()
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
