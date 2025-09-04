import RPi.GPIO as GPIO
import time

# GPIO Pins (BCM-Nummerierung)
DIR = 10  # Richtung
PUL = 8
ENA = 32   # Puls

# Setup
GPIO.setmode(GPIO.BOARD)
GPIO.setup(DIR, GPIO.OUT)
GPIO.setup(PUL, GPIO.OUT)

# Richtung setzen (True = eine Richtung, False = andere)
GPIO.output(DIR, True)

# Anzahl Schritte
steps = 115

# Schrittgeschwindigkeit (Zeit zwischen Pulsen)
delay = 0.001 # 1 ms = 1000 Schritte pro Sekunde

GPIO.output(DIR, False)
for _ in range(steps):
    GPIO.output(PUL, True)
    time.sleep(delay)
    GPIO.output(PUL, False)
    time.sleep(delay)

# Aufräumen
GPIO.cleanup()
