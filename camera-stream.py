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
        # Capture frame as a byte stream
        with io.BytesIO() as stream:
            camera.capture_to_stream(stream, format='jpeg')  # Capture to a byte stream in JPEG format
            frame = stream.getvalue()  # Get byte data from the stream
            yield (b"--frame\r\n"
                   b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
