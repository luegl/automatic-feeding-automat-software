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

picam2 = Picamera2()
picam2.start()
picam2.capture_file("/tmp/captured_image.jpg")  
picam2.close()

IMG_SIZE = (180, 180)
model = YOLO("yolov8n.pt")
keras_model_bruno = tf.keras.models.load_model("models/model4_bruno.keras")
keras_model_flaekli = tf.keras.models.load_model("models/model1_flaekli.keras")

img_path = "/tmp/captured_image.jpg"
img = cv2.imread(img_path)
plt.imshow(img)
plt.show()
print(f"Originalbildgröße: {img.shape}")
img_array = np.array(img)
results = model.predict(source=img_path, conf=0.47, classes=[15])

if results[0].boxes:
  cat = 1
  boxes = results[0].boxes.xyxy.tolist()
  for box in boxes:
    x_min, y_min, x_max, y_max = map(int, box)

    cropped_img_array = img_array[y_min:y_max, x_min:x_max]
    if isinstance(cropped_img_array, tf.Tensor):
        cropped_img_array = cropped_img_array.numpy()
    print(f"Zugeschnittene Bildgröße: {cropped_img_array.shape}")

    cropped_img_array_rgb = cv2.cvtColor(cropped_img_array, cv2.COLOR_BGR2RGB)
    cropped_img = Image.fromarray(cropped_img_array_rgb.astype('uint8'))
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    plt.figure(figsize=(10, 5))
    plt.subplot(1, 2, 1)
    plt.imshow(cropped_img)
    plt.axis("off")
    plt.title("Cropped Image")
    plt.subplot(1, 2, 2)
    plt.imshow(img_rgb)
    plt.axis("off")
    plt.title("Original Image")
    plt.show()
    print("Cat in the Picture!")
    cropped_img_resized = cropped_img.resize(IMG_SIZE)
    print(f"Zugeschnittene Bildgröße (nach behandeln): {cropped_img_resized.size}")
    img_array_resized = keras.utils.img_to_array(cropped_img_resized)
    img_array_resized = img_array_resized / 255.0  


    img_array_resized = np.expand_dims(img_array_resized, axis=0)  

   
    predictions_bruno = keras_model_bruno.predict(img_array_resized)
    score_bruno = float(predictions_bruno[0])

    predictions_flaekli = keras_model_flaekli.predict(img_array_resized)
    score_flaekli = float(predictions_flaekli[0])

  
    if 100 * (1 - score_bruno) > 25:
        print(f"Bruno ist im Bild! ({100 * (1 - score_bruno):.2f}%)")

    if 100 * (1 - score_flaekli) > 25:
        print(f"Flaekli ist im Bild! ({100 * (1 - score_flaekli):.2f}%)")
else:
  cat = 0
  print("No cat in the picture!")

