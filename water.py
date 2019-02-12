# External module imp
import RPi.GPIO as GPIO
import datetime
import time
import sqlite3
import json
import logging
import Adafruit_ADS1x15

with open('config.json', 'r') as f:
    SETTINGS = json.load(f)

GPIO.setmode(GPIO.BOARD) # Broadcom pin-numbering scheme
conn = sqlite3.connect('water_stats.db')

# Create an ADS1115 ADC (16-bit) instance.
adc = Adafruit_ADS1x15.ADS1115()
ADS_GAIN = 1

def init_output():
    GPIO.setup(SETTINGS["MOISTURE_POWER_GPIO"], GPIO.OUT)
    GPIO.output(SETTINGS["MOISTURE_POWER_GPIO"], GPIO.HIGH)

    for plantObject in SETTINGS["PLANTS"]:
        GPIO.setup(plantObject["WATER_PUMP_GPIO"], GPIO.OUT)
        GPIO.output(plantObject["WATER_PUMP_GPIO"], GPIO.HIGH)


def get_status(plantObject):
    moisture_measurement = adc.read_adc(plantObject["MOISTURE_SENSOR_CHANNEL"], gain=ADS_GAIN)

    conn.execute('insert into moisture (datetime, plantid, measurement) values(datetime(\'now\'),?,?)', (plantObject["PLANT_ID"], moisture_measurement))
    conn.commit()

    return moisture_measurement

def auto_water():
    create_db()
    init_output()

    try:
        # power on sensors
        GPIO.output(SETTINGS["MOISTURE_POWER_GPIO"], GPIO.LOW)
        # let sensors start up before reading them
        time.sleep(1)

        for plantObject in SETTINGS["PLANTS"]:
            moisture_measurement = get_status(plantObject)
            if SETTINGS["MIN_VALID_MOISTURE"] > moisture_measurement or moisture_measurement > SETTINGS["MAX_VALID_MOISTURE"]:
                logging.warning('AutoWaterer: Moisture for %s reported (%s) is outside valid range, ignoring', plantObject["PLANT_NAME"], moisture_measurement)
                continue
            wet = moisture_measurement < plantObject["MOISTURE_THRESHOLD"]
            if not wet:
                logging.info("AutoWaterer: Pump for %s (id: %s) triggered", plantObject["PLANT_NAME"], plantObject["PLANT_ID"])
                pump_on(plantObject)
    except Exception as e:
        logging.warning('AutoWaterer: Exception triggered: ' + str(e))
    finally:
        GPIO.output(SETTINGS["MOISTURE_POWER_GPIO"], GPIO.HIGH)
        GPIO.cleanup() # cleanup all GPI
        conn.close()

def pump_on(plantObject):
    GPIO.output(plantObject["WATER_PUMP_GPIO"], GPIO.LOW)
    conn.execute('insert into waterings (datetime, plantid, status) values(datetime(\'now\'),?,?)', (plantObject["PLANT_ID"], 1))
    time.sleep(plantObject["WATERING_DURATION"])
    GPIO.output(plantObject["WATER_PUMP_GPIO"], GPIO.HIGH)
    conn.execute('insert into waterings (datetime, plantid, status) values(datetime(\'now\'),?,?)', (plantObject["PLANT_ID"], 0))
    conn.commit()

    # let water soak
    time.sleep(SETTINGS["SOAKING_DELAY"])
    # measure and record fresh moisture level
    get_status(plantObject)

def create_db():
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS moisture(id integer primary key, datetime text, plantid integer, measurement integer)''')
    c.execute('''CREATE TABLE IF NOT EXISTS waterings(id integer primary key, datetime text, plantid integer, status integer)''')
    conn.commit()
