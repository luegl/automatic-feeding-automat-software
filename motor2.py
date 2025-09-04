import RPi.GPIO as GPIO
from time import sleep

# Richtungspin (DIR) und Schritte-Pin (STEP) definieren
DIR = 10      # Pin 10 (GPIO15)
STEP = 8      # Pin 8  (GPIO14)
ENA = 12      # Schritt-Pin (BOARD Pin 8)
CW = 1       # Umdrehung im Uhrzeigersinn
CCW = 0      # Gegen den Uhrzeigersinn

# GPIO-Modus auf BOARD setzen
GPIO.setmode(GPIO.BOARD)

# Pins als Ausgänge definieren
GPIO.setup(DIR, GPIO.OUT)
GPIO.setup(STEP, GPIO.OUT)

def move_motor(direction, steps=200, delay=0.005):

    GPIO.output(DIR, direction)
    for _ in range(steps):
        GPIO.output(STEP, GPIO.HIGH)
        sleep(delay)
        GPIO.output(STEP, GPIO.LOW)
        sleep(delay)

try:
    # Schrittbewegung im Uhrzeigersinn
    print("Motor dreht im Uhrzeigersinn")
    move_motor(CW, steps=200, delay=0.005)

    # Warten, dann Richtung wechseln
    sleep(1.0)

    # Schrittbewegung gegen den Uhrzeigersinn
    print("Motor dreht gegen den Uhrzeigersinn")
    move_motor(CCW, steps=200, delay=0.005)

except KeyboardInterrupt:
    print("Bewegung durch Benutzer abgebrochen")

finally:
    print("GPIO wird zurückgesetzt")
    GPIO.cleanup()
