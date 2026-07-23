import cv2

# ESP32 Cam için kamera yayını URL'si
STREAM_URL = "http://192.168.1.137:81/stream"

def test_camera_stream():
    print("[INFO] Kamera yayınına bağlanılıyor...")
    cap = cv2.VideoCapture(STREAM_URL)

    if not cap.isOpened():
        
        print("[HATA] Kamera yayını açılamadı! IP adresini veya portu kontrol edin.")
        return

    print("[INFO] Yayın başarıyla başlatıldı. Çıkmak için 'q' tuşuna basın.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[UYARI] Kare alınamadı, yayın kesilmiş olabilir.")
            break

        
        cv2.imshow("ESP32 Cam - Smart Parking Stream", frame)

        # 'q' tuşuna basilirsa pencereyi kapat
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    test_camera_stream()