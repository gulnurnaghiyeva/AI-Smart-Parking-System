import cv2
import pickle
import numpy as np
import urllib.request

WIDTH, HEIGHT = 55, 135

try:
    with open('CarParkPos', 'rb') as f:
        pos_list = pickle.load(f)
except Exception as e:
    print(f"[UYARI] 'CarParkPos' dosyası okunamadı veya bulunamadı: {e}")
    pos_list = []

def check_parking_space(img_pro, img):
    space_counter = 0

    for pos in pos_list:
        x, y = pos

       
        img_crop = img_pro[y:y + HEIGHT, x:x + WIDTH]
        
       
        count = cv2.countNonZero(img_crop)

        
        if count < 2000:
            color = (0, 255, 0) # Yeşil (Boş)
            thickness = 2
            space_counter += 1
        else:
            color = (0, 0, 255) # Kırmızı (Dolu)
            thickness = 2

        # Park alanını çerçevele
        cv2.rectangle(img, pos, (pos[0] + WIDTH, pos[1] + HEIGHT), color, thickness)
        
        cv2.putText(img, str(count), (x, y + HEIGHT - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)

    # genel durum bilgi kutusu
    cv2.rectangle(img, (20, 20), (300, 70), (0, 0, 0), -1)
    cv2.putText(img, f'BOS ALAN: {space_counter}/{len(pos_list)}', (30, 55),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

# ESP32 / Deneyap Cam canlı yayın adresi
URL = "http://192.168.1.137:81/stream"

cv2.namedWindow("ESP32 Cam - Smart Parking Stream")

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
                        # Görüntü İşleme Adımları
                        img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        img_blur = cv2.GaussianBlur(img_gray, (3, 3), 1)
                        img_threshold = cv2.adaptiveThreshold(img_blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                                             cv2.THRESH_BINARY_INV, 25, 16)
                        img_median = cv2.medianBlur(img_threshold, 5)
                        kernel = np.ones((3, 3), np.uint8)
                        img_dilated = cv2.dilate(img_median, kernel, iterations=1)

                        check_parking_space(img_dilated, frame)

                        cv2.imshow("ESP32 Cam - Smart Parking Stream", frame)

        # Çıkış yapmak için 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except Exception as e:
    print(f"[HATA] Bağlantı veya analiz hatası: {e}")

cv2.destroyAllWindows()