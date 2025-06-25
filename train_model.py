
import sys
import os
import cv2
import random
from ultralytics import YOLO
from tqdm import tqdm
import shutil
from tensorflow import keras
import matplotlib.pyplot as plt
from keras import layers, callbacks
import tensorflow as tf
import pandas as pd
from tensorflow import keras
import os
import json
with open("settings.json", "r") as f:
    data = json.load(f)


data["train_model"] = True


with open("settings.json", "w") as f:
    json.dump(data, f, indent=4)

if len(sys.argv) < 2:
    print("Kein Name übergeben!")
    sys.exit(1)



model = YOLO("yolov8n.pt")
CAT = sys.argv[1]



INPUT_FOLDER = "data/"
OUTPUT_FOLDER = "data/preprocessed/"

CLASS_FOLDER = [CAT, "other_cats"]

for category in CLASS_FOLDER:
    os.makedirs(os.path.join(OUTPUT_FOLDER, category), exist_ok=True)


class_image_files = {}
for class_name in CLASS_FOLDER:
    class_path = os.path.join(INPUT_FOLDER, class_name)
    files = [f for f in os.listdir(class_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif'))]
    class_image_files[class_name] = files

min_count = min(len(files) for files in class_image_files.values())

for class_name, files in class_image_files.items():
    if len(files) > min_count:
        selected_files = random.sample(files, min_count)
    else:
        selected_files = files
    class_image_files[class_name] = selected_files

for class_name in CLASS_FOLDER:
    class_path = os.path.join(INPUT_FOLDER, class_name)
    start_index = 0
    for filename in class_image_files[class_name]:
        img_path = os.path.join(class_path, filename)
        img = cv2.imread(img_path)
        results = model.predict(source=img_path, conf=0.45, classes=[15])

        if results[0].boxes:
            boxes = results[0].boxes.xyxy.tolist()
            for box in boxes:
                x_min, y_min, x_max, y_max = map(int, box)
                cropped_img = img[y_min:y_max, x_min:x_max]
                cropped_img_path = os.path.join(OUTPUT_FOLDER, class_name, f"{class_name}_{start_index}.jpg")
                cv2.imwrite(cropped_img_path, cropped_img)
                start_index += 1
        else:
            os.remove(img_path)

cat_files = [f for f in os.listdir(os.path.join(OUTPUT_FOLDER, CAT)) if f.endswith(".jpg") or f.endswith(".png")]
other_cats_files = [f for f in os.listdir(os.path.join(OUTPUT_FOLDER, "other_cats")) if f.endswith(".jpg") or f.endswith(".png")]

cat_count = len(cat_files)
other_cats_count = len(other_cats_files)

if cat_count != other_cats_count:
    target_count = min(cat_count, other_cats_count)
    if cat_count > target_count:
        excess_files = random.sample(cat_files, cat_count - target_count)
        for file in excess_files:
            os.remove(os.path.join(OUTPUT_FOLDER, CAT, file))
    elif other_cats_count > target_count:
        excess_files = random.sample(other_cats_files, other_cats_count - target_count)
        for file in excess_files:
            os.remove(os.path.join(OUTPUT_FOLDER, "other_cats", file))



shutil.rmtree(f"data/{CAT}")

print("ich fange an zu trainieren")
IMG_SIZE = (180, 180)
IMG_SIZE_ = 180
BATCH_SIZE = 16
dataset_name = f"dataset_{CAT[:3]}_other"
VERSION = "4"

class_0_dir = f"data/preprocessed/{CAT}"
class_1_dir = "data/preprocessed/other_cats"

class_0_images = [os.path.join(class_0_dir, fname) for fname in os.listdir(class_0_dir)]
class_1_images = [os.path.join(class_1_dir, fname) for fname in os.listdir(class_1_dir)]

df = pd.DataFrame({ 
    "filename": class_0_images + class_1_images,
    "class": [0] * len(class_0_images) + [1] * len(class_1_images)
})

df['class'] = df['class'].astype(str)

datagen = keras.preprocessing.image.ImageDataGenerator(
    rescale=1./255,
    validation_split=0.2,
    rotation_range=40,
    width_shift_range=0.26,
    height_shift_range=0.26,
    shear_range=0.17,
    zoom_range=0.26,
    horizontal_flip=True,
    fill_mode="nearest"
)

train_generator = datagen.flow_from_dataframe(
    dataframe=df,
    x_col="filename",
    y_col="class",
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="binary",
    subset="training",
    shuffle=True,
    seed=42,
    validation_split=0.2
)

val_generator = datagen.flow_from_dataframe(
    dataframe=df,
    x_col="filename",
    y_col="class",
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="binary",
    subset="validation",
    shuffle=True,
    seed=42,
    validation_split=0.2
)


base_model = keras.applications.MobileNetV2(input_shape=(IMG_SIZE_, IMG_SIZE_, 3), include_top=False, weights="imagenet")
base_model.trainable = False

x = layers.GlobalAveragePooling2D()(base_model.output)
x = layers.Dense(128, activation="relu")(x)
x = layers.Dense(1, activation="sigmoid")(x)

model = keras.Model(inputs=base_model.input, outputs=x)


model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])

model.fit(train_generator, validation_data=val_generator, epochs=5)

model_path = f"models/model_{CAT}.keras"

model.save(model_path, save_format="keras")

model = tf.keras.models.load_model(model_path)

loss, accuracy = model.evaluate(val_generator)

with open("cats.json", "r") as f:
    cats_data = json.load(f)

cats_data[CAT]["model_accuracy"] = accuracy * 100



with open("settings.json", "w") as f:
    json.dump(cats_data, f, indent=4)


shutil.rmtree(f"data/preprocessed")

data["train_model"] = False


with open("settings.json", "w") as f:
    json.dump(data, f, indent=4)



"""

for category in CLASS_FOLDER:
os.makedirs(os.path.join(OUTPUT_FOLDER, category), exist_ok=True)


for class_name in CLASS_FOLDER:
class_path = os.path.join(INPUT_FOLDER, class_name)
start_index = 0
for filename in os.listdir(class_path):
if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):

img_path = os.path.join(class_path, filename)

img = cv2.imread(img_path)

results = model.predict(source=img_path, conf=0.45, classes=[15])


if results[0].boxes:
boxes = results[0].boxes.xyxy.tolist()
for box in boxes:
x_min, y_min, x_max, y_max = map(int, box)
cropped_img = img[y_min:y_max, x_min:x_max]

os.path.join(class_path, filename)
cropped_img_path = os.path.join(os.path.join(OUTPUT_FOLDER, class_name), f"{class_name}_{start_index}.jpg")
cv2.imwrite(cropped_img_path, cropped_img)
start_index += 1
else:
os.remove(img_path)



cat_files = [f for f in os.listdir(os.path.join(OUTPUT_FOLDER, CAT)) if f.endswith(".jpg") or f.endswith(".png")]
other_cats_files = [f for f in os.listdir(os.path.join(OUTPUT_FOLDER, "other_cats")) if f.endswith(".jpg") or f.endswith(".png")]


cat_count = len(cat_files)
other_cats_count = len(other_cats_files)

if cat_count != other_cats_count:
target_count = min(cat_count, other_cats_count)

if cat_count > target_count:
excess_files = random.sample(cat_files, cat_count - target_count)
for file in excess_files:
os.remove(os.path.join(OUTPUT_FOLDER, CAT, file))

elif other_cats_count > target_count:
excess_files = random.sample(other_cats_files, other_cats_count - target_count)
for file in excess_files:
os.remove(os.path.join(OUTPUT_FOLDER, "other_cats", file))


cat_files = [f for f in os.listdir(os.path.join(OUTPUT_FOLDER, CAT)) if f.endswith(".jpg") or f.endswith(".png")]
other_cats_files = [f for f in os.listdir(os.path.join(OUTPUT_FOLDER, "other_cats")) if f.endswith(".jpg") or f.endswith(".png")]

cat_count = len(cat_files)
other_cats_count = len(other_cats_files)


if cat_count < other_cats_count:
for i in range(other_cats_count - cat_count):
file_to_copy = random.choice(other_cats_files)
shutil.copy(os.path.join(OUTPUT_FOLDER, "other_cats", file_to_copy),
os.path.join(OUTPUT_FOLDER, CAT, file_to_copy))

elif other_cats_count < cat_count:
for i in range(cat_count - other_cats_count):
file_to_copy = random.choice(cat_files)
shutil.copy(os.path.join(OUTPUT_FOLDER, CAT, file_to_copy),
os.path.join(OUTPUT_FOLDER, "other_cats", file_to_copy))
"""