from picamera2 import Picamera2
import time
import os
import sys


if len(sys.argv) < 2:
    sys.exit(1)

variabel_cat = sys.argv[1]

save_path = f"data/{variabel_cat}"
os.makedirs(save_path, exist_ok=True)

picam2 = Picamera2()
picam2.configure(picam2.create_still_configuration())
picam2.start()

# Funktion, um die nächste freie Bildnummer zu finden
def get_next_filename(save_path, cat_name):
    files = os.listdir(save_path)
    image_files = [f for f in files if f.startswith(f"{cat_name}_") and f.endswith(".jpg")]
    
    # Falls keine Bilder existieren, starten wir mit 1
    if not image_files:
        return 1
    
    # Extrahiere die Bildnummern und finde die höchste
    numbers = [int(f.split('_')[1].split('.')[0]) for f in image_files]
    return max(numbers) + 1

# Setze den maximalen Bildzähler auf 500
max_images = 500
count = get_next_filename(save_path, variabel_cat)

try:
    while count <= max_images:
        filename = f"{save_path}/{variabel_cat}_{count}.jpg"
        picam2.capture_file(filename)
        print(f"Bild gespeichert: {filename}")
        count += 1
        time.sleep(0.5)

    print("Maximale Bildanzahl erreicht. Aufnahme gestoppt.")

except KeyboardInterrupt:
    print("\nAufnahme gestoppt.")

finally:
    picam2.close()
