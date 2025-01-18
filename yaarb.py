import cv2
from flask import Flask, send_file
import io

app = Flask(__name__)

# Initialize the camera
cap = cv2.VideoCapture(0)  # 0 is the default camera

@app.route('/image')
def get_image():
    # Capture a frame from the camera
    ret, frame = cap.read()
    if not ret:
        return "Failed to capture image", 500

    # Convert the frame to JPEG
    _, jpeg = cv2.imencode('.jpg', frame)
    if not _:
        return "Failed to encode image", 500

    # Convert the JPEG to a byte stream
    img_bytes = jpeg.tobytes()

    # Send the image back as a response
    return send_file(io.BytesIO(img_bytes), mimetype='image/jpeg')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
