# import os
# import sys

# if sys.platform == 'win32':
#     os.environ['PIGPIO_ADDR'] = '192.168.3.12'

# from gpiozero import LED
# from time import sleep

# red = LED(17)

# while True:
#     print('ON')
#     red.on()
#     sleep(1)
#     print('OFF')
#     red.off()
#     sleep(1)


import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN)

signal = []
last_signal = time.time()
reset_delay = 1 #sec
while True:
    GPIO.wait_for_edge(17, GPIO.RISING)
    if last_signal + reset_delay <= time.time():
        print(signal)
        signal = []
    else:
        print(last_signal + reset_delay, time.time())

    signal.append(round(time.time()-last_signal, 5))
    last_signal = time.time()

    GPIO.wait_for_edge(17, GPIO.FALLING)
    signal.append(round(time.time()-last_signal, 5))
    last_signal = time.time()
