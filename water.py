
import RPi.GPIO as GPIO
import datetime
import time
import Adafruit_DHT
import sys
import os
import glob
from time import sleep

''' 
'A': auto
'M': manual
'O': on
'F': off
'''
init = False
global count
global flowRate
global old_time
old_time = 0
flowRate = 0
count = 0


GPIO.setmode(GPIO.BOARD) 
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

def read_temp_raw():

   f = open(device_file, 'r')
   lines = f.readlines()
   f.close()
   return lines

def current_milli_time():
   return int(time.time() * 1000)

def get_water_temperature():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c
      
def get_soil_status(pin = 8):
    GPIO.setmode(GPIO.BOARD) 
    GPIO.setup(pin, GPIO.IN) 
    return GPIO.input(pin)

def get_air_temperature(gpiopin = 6):
    humidity, temperature = Adafruit_DHT.read_retry(11, gpiopin)
    return temperature

def get_air_humidity(gpiopin = 6):
    humidity, temperature = Adafruit_DHT.read_retry(11, gpiopin)
    return humidity

GPIO.setup(29, GPIO.IN, pull_up_down = GPIO.PUD_UP)


def countPulse(channel):
   global count
   count = count+1
   

GPIO.add_event_detect(29, GPIO.FALLING, callback=countPulse)

def reset_count_water(): 
    global count
    global flowRate
    try:
        print(count)
        flowRate = 0
        count = 0
    except KeyboardInterrupt:
        GPIO.cleanup()

def return_FlowRate():
    global flowRate 
    global old_time
    current_time = current_milli_time()
    flowRate = round(((1000/ (int)(current_time - old_time)) * count) / 90,3)
    flowRate = round((flowRate / 60 ),3)
    old_time = current_milli_time()
    return flowRate

def init_output(pin):
    GPIO.setmode(GPIO.BOARD) 
    GPIO.setup(pin, GPIO.OUT)

    
def auto_water(delay = 10, pump_pin = 7, water_sensor_pin = 8):
    init_output(pump_pin)
    print("Press CTRL+C to interrupt.")
    try:
        if get_soil_status() == 1 and get_air_temperature() >= 15 and get_air_temperature() <= 30 and get_air_humidity() != 100 and get_water_temperature() >= 15 and get_water_temperature() <= 30:
            pump_on_auto(pump_pin, 10)
        elif get_soil_status() == 1 and get_air_temperature() >= 30 and get_water_temperature() >= 15 and get_water_temperature() <= 30:
            pump_on_auto(pump_pin, 30)
    except KeyboardInterrupt: 
        GPIO.cleanup() 

def pump_on_auto(pump_pin = 7, delay = 3):
    init_output(pump_pin)
    GPIO.output(pump_pin, GPIO.LOW)
    time.sleep(delay)
    GPIO.output(pump_pin, GPIO.HIGH)

def pump_on_manual(pump_pin = 7):
    init_output(pump_pin)
    GPIO.output(pump_pin, GPIO.LOW)
    
def pump_off(pump_pin = 7):
    init_output(pump_pin)
    GPIO.output(pump_pin, GPIO.HIGH)