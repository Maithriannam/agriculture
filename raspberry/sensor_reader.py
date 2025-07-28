import Adafruit_DHT
import RPi.GPIO as GPIO
import time
import csv
import os

DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 4
MOISTURE_PIN = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(MOISTURE_PIN, GPIO.IN)

def read_sensor_data():
    humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)
    if humidity is None or temperature is None:
        return 0.0, 0.0, 0
    moisture = GPIO.input(MOISTURE_PIN)
    return temperature, humidity, moisture

def collect_and_store():
    file_exists = os.path.exists('data/sensor_data.csv')
    with open('data/sensor_data.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['temp', 'humidity', 'moisture'])
        temperature, humidity, moisture = read_sensor_data()
        writer.writerow([temperature, humidity, moisture])
        print("Saved:", temperature, humidity, moisture)

if __name__ == "__main__":
    while True:
        collect_and_store()
        time.sleep(10)
