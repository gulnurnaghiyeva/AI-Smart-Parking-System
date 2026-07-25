import cv2
import pickle
import numpy as np
import urllib.request
import http.client
from flask import Flask, Response, render_template

WIDTH, HEIGHT = 55, 135


try:
    with open('CarParkPos', 'rb') as f:
        pos_list = pickle.load(f)
except Exception as e:
    print(f"[UYARI] 'CarParkPos' dosyası yüklenemedi: {e}")
    pos_list = []

app = Flask(__name__)

URL = "http://192.168.1.137:81/stream"

def check_parking_spaces(img_pro, img_frame):
    space_counter = 0

    for pos in pos_list:
        x, y = pos
        img_crop = img_pro[y:y + HEIGHT, x:x + WIDTH]
        count = cv2.countNonZero(img_crop)

        if count < 2000:
            color = (0, 255, 0)
            space_counter += 1
        else:
            color = (0, 0, 255)

        cv2.rectangle(img_frame, pos, (pos[0] + WIDTH, pos[1] + HEIGHT), color, 2)

  
    cv2.rectangle(img_frame, (20, 20), (320, 70), (0, 0, 0), -1)
    cv2.putText(img_frame, f'BOS ALAN: {space_counter}/{len(pos_list)}', (30, 55),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

def generate_frames():
    while True:
        try:
            req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
            stream = urllib.request.urlopen(req, timeout=5)
            bytes_data = b''

            while True:
                try:
                    chunk = stream.read(4096)
                    if not chunk:
                        break
                    bytes_data += chunk

                    a = bytes_data.find(b'\xff\xd8')
                    b = bytes_data.find(b'\xff\xd9')

                    if a != -1 and b != -1:
                        jpg = bytes_data[a:b+2]
                        bytes_data = bytes_data[b+2:]

                        if len(jpg) > 0:
                            img_np = np.frombuffer(jpg, dtype=np.uint8)
                            if img_np.size > 0:
                                frame = cv2.imdecode(img_np, cv2.IMREAD_COLOR)

                                if frame is not None:
                                    # Adaptive Thresholding
                                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                                    blur = cv2.GaussianBlur(gray, (3, 3), 1)
                                    img_threshold = cv2.adaptiveThreshold(
                                        blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                        cv2.THRESH_BINARY_INV, 25, 16
                                    )
                                    img_median = cv2.medianBlur(img_threshold, 5)
                                    kernel = np.ones((3, 3), np.uint8)
                                    img_dilate = cv2.dilate(img_median, kernel, iterations=1)                        
                                    check_parking_spaces(img_dilate, frame)
                                    ret, buffer = cv2.imencode('.jpg', frame)
                                    frame_bytes = buffer.tobytes()

                                    yield (b'--frame\r\n'
                                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

                except (http.client.IncompleteRead, urllib.error.URLError):
                    break

        except Exception as e:
            print(f"[YAYIN UYARISI] Kamera akışı yeniden bağlanıyor... ({e})")
            cv2.waitKey(1000)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    print("\n[INFO] Flask Web Sunucusu Başlatılıyor...")
    print("[INFO] Web Paneli Adresi: http://127.0.0.1:5000\n")
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)