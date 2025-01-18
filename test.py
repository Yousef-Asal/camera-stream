from flask import Flask, Response
import cv2

app = Flask(__name__)

def generate_frames():
    cap = cv2.VideoCapture(0)  # or the video stream source you are using
    
    while True:
        # Read frame-by-frame from the camera
        success, frame = cap.read()
        if not success:
            break
        
        # Encode frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        # Yield the frame to Flask in the correct MIME type for streaming
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()

@app.route('/stream')
def stream():
    return Response(generate_frames(), 
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
