from picamera2 import Picamera2
import time
import cv2
from ultralytics import YOLO

IMG_SIZE = (180, 180)
print("Kamera wird gestartet")
picam2 = Picamera2()
picam2.start()






model = YOLO("yolov8n.pt")

img_array = picam2.capture_array()

img_array = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)
results = model.predict(source=img_array, conf=0.3, classes=[15])

print(results)
        
       
