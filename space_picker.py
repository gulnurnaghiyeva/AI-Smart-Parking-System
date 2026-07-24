import cv2
import pickle
import numpy as np
import urllib.request

# Park yeri kutu boyutları 
WIDTH, HEIGHT = 55, 135

try:
    with open('CarParkPos', 'rb') as f:
        pos_list = pickle.load(f)
except:
    pos_list = []

def mouse_click(event, x, y, flags, params):

    if event == cv2.EVENT_LBUTTONDOWN:
        pos_list.append((x, y))
        
    if event == cv2.EVENT_RBUTTONDOWN:
        for i, pos in enumerate(pos_list):
            px, py = pos
            if px < x < px + WIDTH and py < y < py + HEIGHT:
                pos_list.pop(i)
                break

    with open('CarParkPos', 'wb') as f:
        pickle.dump(pos_list, f)

# ESP32 / Deneyap Cam canlı yayın adresi
URL = "http://192.168.1.137:81/stream"

cv2.namedWindow("Parking Space Picker")
cv2.setMouseCallback("Parking Space Picker", mouse_click)

try:
    stream = urllib.request.urlopen(URL)
    bytes_data = b''

    while True:
        bytes_data += stream.read(1024)
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
                        
                        for pos in pos_list:
                            cv2.rectangle(frame, pos, (pos[0] + WIDTH, pos[1] + HEIGHT), (255, 0, 255), 2)

                        cv2.imshow("Parking Space Picker", frame)

        # Çıkış yapmak için 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except Exception as e:
    print(f"[HATA] Kamera bağlantısı sağlama hatası: {e}")

cv2.destroyAllWindows()