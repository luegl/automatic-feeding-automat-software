from picamera2 import Picamera2
import cv2

def main():
    # Kamera initialisieren
    picam2 = Picamera2()
    config = picam2.create_preview_configuration()
    picam2.configure(config)
    picam2.start()

    print("Kamera gestartet. Drücke 'q' zum Beenden.")

    while True:
        # Frame holen
        frame = picam2.capture_array()

        # Frame anzeigen
        cv2.imshow("Raspberry Pi Camera Test", frame)

        # Mit 'q' beenden
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    picam2.stop()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
