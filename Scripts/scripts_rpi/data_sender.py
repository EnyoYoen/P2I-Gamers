import queue
import threading
import time
from gpiozero import MCP3008
from mpu9250_jmdev.registers import *
from mpu9250_jmdev.mpu_9250 import MPU9250
import requests
from datetime import datetime

from CAN2 import MAX127
from gpiozero import Button

from groveDOF import MPUWrapper

PIN = 18
btn = Button(PIN)

# URL = 'http://laptop-gia:8085'
# URL = 'http://desktop-lucie:8085'
URL = 'http://nitro5:8085'

mcp3008_channels = list(range(2, 7))
mcp3008 = [MCP3008(channel=c) for c in mcp3008_channels]

max127_channels = list(range(5))
max127 = MAX127(i2c_address=0x28, i2c_busnum=4)

mpus = MPUWrapper(buses=[3, 4, 5])

def get_can_data():
	mcp_data = {i: pot.value for i, pot in enumerate(mcp3008)}
	mpu_data = {i+len(mcp3008_channels): value for i, value in enumerate(max127.get_all_values(max127_channels))}

	return mcp_data | mpu_data

def get_mpu_data():
	out = {}
	for bus, data in mpus.get_data().items():
		fdata = {
			# 8+3*bus: mpu.readAccelerometerMaster(),
			# 8+3*bus+1: mpu.readGyroscopeMaster(),
			8+3*bus+2: data['mag'],
			# "Temperature": mpu.readTemperatureMaster() # Tf?
		}
		# out[bus] = data
		out |= fdata

	for k, v in out.items():
		if all(map(lambda e: e==0, v)):
			print(f'No data from MPU on bus {(k-10)//3}\n')
	# 		mpus = initialize_mpus()
	return out

def send_data(data):
	try:
		r = requests.post(URL, json=data, timeout=10)
		r.raise_for_status()
	except Exception as e:
		print(f'Error: {e}') # TODO
		return False
	else:
		return True

def get_now():
	return datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

def client(que: queue.Queue):
	while True:
		packets = [que.get()] # Will block until some data is available
		while not que.empty():
			try:
				packet = que.get_nowait()
			except queue.Empty:
				break
			else:
				packets.append(packet)

		if len(packets) > 0:
			print(f'Sending packet, size: {len(packets)}', packets[0]['time'] + '\r', end='')
			send_data(packets)

if __name__ == '__main__':

	que = queue.Queue()
	threading.Thread(target=client, args=(que, ), daemon=True).start()

	while True:
		now = get_now()
		packet = {
			'type': 'simple',
			'data': get_can_data(),
			'time': now
		}
		que.put(packet)

		packet = {
			'type': 'vector',
			'data': get_mpu_data(),
			'time': now
		}
		que.put(packet)

		time.sleep(0.1)

		if not btn.is_pressed:
			print(f"Pin {PIN} isn't connected, stopping data fetcher")
			raise SystemExit()