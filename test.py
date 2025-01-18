from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import io
import picamera

class MJPEGStreamHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            with picamera.PiCamera(resolution='640x480', framerate=24) as camera:
                stream = io.BytesIO()
                for _ in camera.capture_continuous(stream, format='jpeg', use_video_port=True):
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(stream.getvalue()))
                    self.end_headers()
                    self.wfile.write(stream.getvalue())
                    stream.seek(0)
                    stream.truncate()
        else:
            self.send_error(404)
            self.end_headers()

address = ('', 8000)
server = HTTPServer(address, MJPEGStreamHandler)
print("Streaming on port 8000...")
server.serve_forever()
