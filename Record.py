from flask import Flask, Response
import cv2
import numpy as np
from mss import mss

app = Flask(__name__)

def generate():
    with mss() as sct:
        while True:
            frame = np.array(sct.grab(sct.monitors[1]))
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=5000)
