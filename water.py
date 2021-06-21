
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

def countPulse(channel):
   global count
   count = count+1

def get_used_water(pin = 29):
    flowRate = 0
    try:
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(pin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        GPIO.add_event_detect(pin, GPIO.FALLING, callback=countPulse)
        flowRate = (count * 2.25)        #Take counted pulses in the last second and multiply by 2.25mL 
        flowRate = flowRate * 60         #Convert seconds to minutes, giving you mL / Minute
        flowRate = flowRate / 1000       #Convert mL to Liters, giving you Liters / Minute
    finally:
        GPIO.cleanup()
    return flowRate

def init_output(pin):
    GPIO.setmode(GPIO.BOARD) 
    GPIO.setup(pin, GPIO.OUT)

    
def auto_water(delay = 10, pump_pin = 7, water_sensor_pin = 8):
    init_output(pump_pin)
    print("Press CTRL+C to interrupt.")
    try:
        if get_soil_status() == 1:
            time.sleep(delay)
            pump_on_auto(pump_pin, 5)
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