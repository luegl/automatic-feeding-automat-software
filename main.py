import json
import threading
import time
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




class Food_bowl:
  def __init__(self, name, state, weight, cat):
    self.name = name
    self.state = state
    self.weight = weight
    self.cat = cat


class Cat:
  def __init__(self, name, ratio_per_day):
    self.name = name
    self.ratio_per_day = ratio_per_day

def load_cats():
    with open("cats.json", "r") as f:
        return json.load(f)
    
def save_cats():
    with open("cats.json", "w") as f:
        json.dump(cats_json, f, indent=2)

def weigh_bowl_A():
    a = 0
    weights = [200, 180, 160, 140, 120, 100, 80,60, 40, 20, 10, 0]
    weight_bowl_A = weights[a%12]
    a += 1
    return weight_bowl_A

def open_bowl_A(cat):
   fA.state="open"
   fA.cat=cat

def close_bowl_A(weight, cat):
   cats_json[cat]['ration_left'] = cats_json.get(cat, {}).get("ration_left")-(fA.weight-weight)
   save_cats()
   fA.state="closed"
   fA.cat=""
   fA.weight=weight

def fill_up_bowl_A():
    if fA.weight < 200:
       fA.weight = int(input("Wie schwer nach dem Auffüllen? "))

def detect_cat_camera_A():
    bruno = False
    flaekli = False
    
    img_array = picam2.capture_array()
    img_array = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)
    
    try:
        results = model.predict(source=img_array, conf=0.3, classes=[15])   
    except:
        print("Fehler bei erkennung")
    
    if results and results[0].boxes is not None and len(results[0].boxes) > 0:
        boxes = results[0].boxes.xyxy.tolist()
        for box in boxes:
            x_min, y_min, x_max, y_max = map(int, box)

            cropped_img_array = img_array[y_min:y_max, x_min:x_max]
            if isinstance(cropped_img_array, tf.Tensor):
                cropped_img_array = cropped_img_array.numpy()
        

            cropped_img_array_rgb = cv2.cvtColor(cropped_img_array, cv2.COLOR_BGR2RGB)
            cropped_img = Image.fromarray(cropped_img_array_rgb.astype('uint8'))
            cropped_img_resized = cropped_img.resize(IMG_SIZE)
            img_array_resized = keras.utils.img_to_array(cropped_img_resized)
            img_array_resized = img_array_resized / 255.0  
            img_array_resized = np.expand_dims(img_array_resized, axis=0)  
            predictions_bruno = keras_model_bruno.predict(img_array_resized)
            score_bruno = float(predictions_bruno[0])
            predictions_flaekli = keras_model_flaekli.predict(img_array_resized)
            score_flaekli = float(predictions_flaekli[0])
        
            if 100 * (1 - score_bruno) > 25:
                bruno = True
                print("bruno")

            if 100 * (1 - score_flaekli) > 25:
                flaekli = True
                print("flaekli")
                
            if bruno and not flaekli:
                cat_detected = "bruno"

            if flaekli and not bruno:
                cat_detected = "flaekli"

            if bruno and flaekli:
                if 100 * (1 - score_bruno) > 100 * (1 - score_flaekli):
                   cat_detected = "bruno"
                else:
                    cat_detected = "flaekli"

    else:
        cat_detected=""

    return cat_detected

def detect_cat_camera_A_fake():
    a=input("wer: ")
    return a 

def weigh_bowl_A_fake():
    a=input("wie viel: ")
    return int(a)

def food_bowl_A():
    wrong_detection_count = 0 

    while True:
        cat = detect_cat_camera_A_fake()
        weight = weigh_bowl_A_fake()

        if cat in cats_names and fA.state == "closed" and int(cats_json.get(cat, {}).get("ration_left")) > 0:
            open_bowl_A(cat)
            print("geöffnet für", cat)

        if fA.state == "open":
            if cat != fA.cat:
                wrong_detection_count += 1
                print(f"Andere oder keine Katze erkannt. Zähler: {wrong_detection_count}")
            else:
                wrong_detection_count = 0 

           
            if (fA.weight - weight > cats_json.get(fA.cat, {}).get("ration_left")) or (wrong_detection_count >= 3):
                close_bowl_A(weight, fA.cat)
                print("geschlossen")
                wrong_detection_count = 0
                fill_up_bowl_A()
        
        print(fA.state)

def __main__():
   food_bowl_A()
   
"""      
keras_model_bruno = tf.keras.models.load_model("models/model4_bruno.keras")
keras_model_flaekli = tf.keras.models.load_model("models/model1_flaekli.keras")
model = YOLO("yolov8n.pt")

cat_detected = ""
IMG_SIZE = (180, 180)
picam2 = Picamera2()
picam2.start()
print("gestartet")
"""


fA = Food_bowl("A", "closed", 200, "")

bruno = Cat("Bruno", 200)
flaekli = Cat("Flaekli", 200)

cats_json = load_cats()

cats_names = list(cats_json.keys())


__main__()





