#!/usr/bin/env python3
import serial
import time

if __name__ == '__main__':
	ser = serial.Serial('/dev/ttyACM0', 9600, timeout=5)
	ser.reset_input_buffer()

	while True:
		ser.write(str(time.time()).encode() + b" Hello from Raspberry Pi!\n")
		raw = ser.readline()
		line = raw.decode('utf-8', errors="ignore").rstrip()
		print(line)
		time.sleep(1)