import json
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
import RPi.GPIO as GPIO
from time import sleep
import gpiozero

import collections
import datetime


import time

import sys

from JoyIT_hx711py import HX711
if sys.version_info[0] != 3:

    raise Exception("Python 3 is required.")
hx = HX711(5, 6)
hx.set_offset(8018181.6875)

hx.set_scale(-916.85)


# GPIO Pins (BCM-Nummerierung)
DIR = 10  # Richtung
PUL = 8
ENA = 32     # Gegen den Uhrzeigersinn


GPIO.setmode(GPIO.BOARD)
GPIO.setup(DIR, GPIO.OUT)
GPIO.setup(PUL, GPIO.OUT)

import collections
import datetime

FPS = 2  # anpassen an deine Kamera
PRE_BUFFER_SEC = 5
class VideoRecorder:
    def __init__(self, fps=FPS, pre_buffer_sec=PRE_BUFFER_SEC, out_dir="videos"):
        self.buffer = collections.deque(maxlen=fps*pre_buffer_sec)
        self.is_recording = False
        self.out = None
        self.fps = fps
        self.out_dir = out_dir
        os.makedirs(out_dir, exist_ok=True)

    def add_frame(self, frame):
        self.buffer.append(frame)
        if self.is_recording and self.out is not None:
            self.out.write(frame)

    def start(self, cat_name="unknown"):   # <--- Katzennamen als optionales Argument
        if not self.is_recording:
            filename = f"{cat_name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
            path = os.path.join(self.out_dir, filename)

            h, w, _ = self.buffer[0].shape
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.out = cv2.VideoWriter(path, fourcc, self.fps, (w, h))

            for f in self.buffer:  # Prebuffer reinschreiben
                self.out.write(f)

            self.is_recording = True
            print(f"▶️ Aufnahme gestartet: {path}")

    def stop(self):
        if self.is_recording:
            self.out.release()
            self.out = None
            self.is_recording = False
            print("⏹ Aufnahme gestoppt")


class Food_bowl:
  def __init__(self, name, state, weight, cat):
    self.name = name
    self.state = state
    self.weight = weight
    self.cat = cat

def load_cats(file):
    with open(file, "r") as f:
        return json.load(f)
    
def save_cats():
    with open("cats.json", "w") as f:
        json.dump(cats_json, f, indent=2)

def weigh_bowl_A():
    hx.power_up()
    val = hx.get_grams()





    hx.power_down()



        


    return val



def open_bowl_A(cat):
    delay = 0.001
    GPIO.output(DIR, True)

    for _ in range(900):
        GPIO.output(PUL, True)
        time.sleep(delay)
        GPIO.output(PUL, False)
        time.sleep(delay)
    fA.state="open"
    fA.cat=cat

def close_bowl_A(weight, cat):
    delay = 0.001
    GPIO.output(DIR, False)
    for _ in range(900):
        GPIO.output(PUL, True)
        time.sleep(delay)
        GPIO.output(PUL, False)
        time.sleep(delay)

    cats_json[cat]['ration_left'] = cats_json.get(cat, {}).get("ration_left")-(fA.weight-weight)
    save_cats()
    fA.state="closed"
    fA.cat=""
    fA.weight=weight


def fill_up_bowl_A():
 
    delay = 0.001
    if fA.weight < min_weight:
        GPIO.output(DIR, False)
        
       
        for _ in range(287):
            GPIO.output(PUL, True)
            time.sleep(delay)
            GPIO.output(PUL, False)
            time.sleep(delay)
      
        while int(weigh_bowl_A())<min_weight:
            print("warten")
        GPIO.output(DIR, True)
        for _ in range(287):
            GPIO.output(PUL, True)
            time.sleep(delay)
            GPIO.output(PUL, False)
            time.sleep(delay)
        fA.weight = int((weigh_bowl_A()))
     

def detect_cat_camera_A():
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

            scores = []
            for cat in cats_names:
                prediction = models_dict[cat].predict(img_array_resized)
                score = float(prediction[0])
                if 100 * (1 - score) > 25:
                    scores.append((cat, score))  

            if scores == []:
                cat_detected = ""
            else:
                cat_detected = max(scores, key=lambda x: x[1])[0]  
        


    else:
        cat_detected=""

    return cat_detected

def detect_cat_camera_A_fake():
    a=input("wer: ")
    return a 

def weigh_bowl_A_fake():
    a=input("wie viel: ")
    return int(a)

recorder = VideoRecorder()
NO_CAT_TIMEOUT = 5  # Sekunden bis Aufnahme stoppt, wenn keine Katze mehr da ist
last_cat_seen = time.time()
target_delay = 1.0 / FPS
def food_bowl_A():


    wrong_detection_count = 0 
    global last_modified
    global cats_json
    global cats_names
    global min_weight 
    min_weight = 30
    last_cat_seen = time.time()

    while True:
        start = time.time()
        img_array = picam2.capture_array()
        img_array = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)
        recorder.add_frame(img_array)
             
        current_modified = os.path.getmtime("cats.json")
        if current_modified != last_modified:
            last_modified = current_modified
            cats_json = load_cats("cats.json")
            cats_names = list(cats_json.keys())

        cat = detect_cat_camera_A()
        weight = weigh_bowl_A()
        print(cat)
        print(weight)
        if cat in cats_names:
            if not recorder.is_recording:
                recorder.start(cat)   # Name der erkannten Katze in den Dateinamen
            last_cat_seen = time.time()
        else:
            if recorder.is_recording and (time.time() - last_cat_seen > NO_CAT_TIMEOUT):
                recorder.stop()


        if cat in cats_names and fA.state == "closed" and int(cats_json.get(cat, {}).get("ration_left")) > 0:
            open_bowl_A(cat)
            print("geöffnet für", cat)
        
        if fA.state == "closed" and weight <min_weight:
            fill_up_bowl_A()

        if fA.state == "open":

            if cat != fA.cat:
                wrong_detection_count += 1
                print(f"Andere oder keine Katze erkannt. Zähler: {wrong_detection_count}")
            else:
                wrong_detection_count = 0 

           
            if (fA.weight - weight > cats_json.get(fA.cat, {}).get("ration_left")) or (wrong_detection_count >= 5):
                close_bowl_A(weight, fA.cat)
                print("geschlossen")
                wrong_detection_count = 0
                if weight < min_weight:
                    fill_up_bowl_A()
        
        print(fA.state)
        elapsed = time.time() - start
        if elapsed < target_delay:
            time.sleep(target_delay - elapsed)

def __main__():
   food_bowl_A()


models_dir = 'models'
models_dict = {}


for filename in os.listdir(models_dir):
    if filename.endswith('.keras'):
        cat_name = filename.replace('model_', '').replace('.keras', '')
        models_dict[cat_name] = tf.keras.models.load_model(os.path.join(models_dir, filename))


bruno_model = models_dict['bruno']


model = YOLO("yolov8n.pt")

cat_detected = ""
IMG_SIZE = (180, 180)
picam2 = Picamera2()
picam2.start()
print("gestartet")



fA = Food_bowl("A", "closed", weigh_bowl_A(), "")

last_modified = os.path.getmtime("cats.json")

cats_json = load_cats("cats.json")

cats_names = list(cats_json.keys())
try:
    __main__()


finally:
    GPIO.cleanup()
    





