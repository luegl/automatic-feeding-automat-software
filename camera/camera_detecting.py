
from picamera2 import Picamera2
import os
import cv2
import random
from ultralytics import YOLO
from tqdm import tqdm
import shutil
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
from ultralytics import YOLO
import time



IMG_SIZE = (180, 180)
model = YOLO("yolov8n.pt")
keras_model_bruno = tf.keras.models.load_model("models/model4_bruno.keras")
keras_model_flaekli = tf.keras.models.load_model("models/model1_flaekli.keras")
picam2 = Picamera2()
picam2.start()


while True:

    start_camera = time.time()
    img_array = picam2.capture_array()
    end_camera = time.time()
   
  


    img_array = cv2.cvtColor(img_array, cv2.COLOR_BGRA2BGR) if img_array.shape[2] == 4 else img_array
    cv2.imwrite('debug_image.jpg', img_array)

    start_yolo = time.time()
    try:
        results = model.predict(source=img_array, conf=0.47, classes=[15])
    except IndexError:
        print("Fehler bei leerer Erkennung - überspringe Frame")

    end_yolo = time.time()


    print(f"YOLO-Erkennung dauerte: {end_yolo - start_yolo:.3f} Sekunden")




    if results[0].boxes is not None and len(results[0].boxes) > 0:

        boxes = results[0].boxes.xyxy.tolist()
        for box in boxes:
            x_min, y_min, x_max, y_max = map(int, box)

            cropped_img_array = img_array[y_min:y_max, x_min:x_max]
            if isinstance(cropped_img_array, tf.Tensor):
                cropped_img_array = cropped_img_array.numpy()
            print(f"Zugeschnittene Bildgröße: {cropped_img_array.shape}")

            cropped_img_array_rgb = cv2.cvtColor(cropped_img_array, cv2.COLOR_BGR2RGB)
            cropped_img = Image.fromarray(cropped_img_array_rgb.astype('uint8'))

            cropped_img_resized = cropped_img.resize(IMG_SIZE)
            print(f"Zugeschnittene Bildgröße (nach behandeln): {cropped_img_resized.size}")
            img_array_resized = keras.utils.img_to_array(cropped_img_resized)
            img_array_resized = img_array_resized / 255.0  


            img_array_resized = np.expand_dims(img_array_resized, axis=0)  

            start_keras = time.time()
            predictions_bruno = keras_model_bruno.predict(img_array_resized)
            score_bruno = float(predictions_bruno[0])

            predictions_flaekli = keras_model_flaekli.predict(img_array_resized)
            score_flaekli = float(predictions_flaekli[0])
            end_keras = time.time()
            print(f"Bruno_Flaekli-Erkennung dauerte: {end_keras - start_keras:.3f} Sekunden")

        
            if 100 * (1 - score_bruno) > 25:
                print(f"Bruno ist im Bild! ({100 * (1 - score_bruno):.2f}%)")

            if 100 * (1 - score_flaekli) > 25:
                print(f"Flaekli ist im Bild! ({100 * (1 - score_flaekli):.2f}%)")
    else:
    
        print("No cat in the picture!")

    time.sleep(1)


picam2.close()

