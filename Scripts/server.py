from functools import partial
import http.server
import json
import multiprocessing
import os
import queue
import threading
import time
import requests

from secret import CALIBRATION_FILE
from dataclass import MesureSimple, MesureVect

class CustomRequestHandler(http.server.BaseHTTPRequestHandler):
	def __init__(self, event, que, gui_data_queue, idMvt, calibration_data, *args, **kwargs):
		self.event = event
		self.que = que
		self.idMvt = idMvt
		self.calibration_data = calibration_data

		self.gui_data_queue = gui_data_queue

		super().__init__(*args, **kwargs)

	def log_message(self, format: str, *args) -> None:
		return # Don't log anything
		return super().log_message(format, *args)

	def do_GET(self):
		# Custom handling for GET requests
		self.send_response(200)
		self.end_headers()
		self.wfile.write(b'Hello, World!')
		print('Received GET')

	def do_POST(self):
		content_length = int(self.headers['Content-Length'])
		post_data = self.rfile.read(content_length)
		post_body = json.loads(post_data.decode('utf-8'))

		self.send_data(post_body)

		start = time.time()
		idPaquet = 1
		try:
			idDonneeMouvement = self.idMvt
		except AttributeError:
			idDonneeMouvement = -1

		simples, vects = [], []
		for packet in post_body:
			date = packet['time']

			if packet['type'] == 'simple':
				for idCapteur, value in packet['data'].items():
					idCapteur = int(idCapteur)+1

					value = self.fix_sensor_value(idCapteur, value)

					simples.append((idCapteur, idDonneeMouvement, date, value))
					mesure = MesureSimple.from_raw((idCapteur, idDonneeMouvement, date, value))

					try:
						self.que.put(mesure)
					except Exception:
						# Program has ended
						break

			elif packet['type'] == 'vector':
				for idCapteur, vec in packet['data'].items():
					vec = self.fix_sensor_value(idCapteur, vec)

					vects.append((int(idCapteur)+1, idDonneeMouvement, date, *vec))
					mesure = MesureVect.from_raw((int(idCapteur)+1, idDonneeMouvement, date, *vec, idPaquet))

					try:
						self.que.put(mesure)
					except Exception:
						# Program has ended
						break

		try:
			is_event_set = self.event.is_set()
		except Exception:
			# Program has ended
			pass
		else:
			if is_event_set:
				print(f'Saving 1 packet, size: {len(post_body)}')

				self.db.add_mesures_multiples(simples, vects)

				print(f'-> Done, took {time.time()-start}sec')

		self.send_response(200)
		self.end_headers()
		self.wfile.write(b'Ok')
		# self.wfile.write(b'Hello, World!')

	def fix_sensor_value(self, idCapteur, value):
		if isinstance(idCapteur, str):
			idCapteur = int(idCapteur)

		if idCapteur <= 10:
			# mesure simple
			if 1 <= idCapteur <= 5:
				# pression
				if not hasattr(self.que, 'pressure_average'):
					pass
					self.que.pressure_average = pressure_average = [[] for _ in range(5)]
				else:
					pressure_average = self.que.pressure_average

				pressure_average[idCapteur-1].append(value)
				samples = 10
				if len(pressure_average[idCapteur-1]) > samples: # 10 samples
					pressure_average[idCapteur-1] = pressure_average[idCapteur-1][-samples:]

				value = sum(pressure_average[idCapteur-1]) / len(pressure_average[idCapteur-1])
			elif 6 <= idCapteur <= 10:
				# flexion

				if len(self.calibration_data) > 0:

					frange = self.calibration_data[str(idCapteur)]

					value = (value-frange[1]) / (frange[0]-frange[1])
	
			value = min(max(value, 0), 1)
		else:
			# vecteur
			norm = sum([v**2 for v in value]) ** 0.5
			if norm != 0 and norm != 1:
				value = [v/norm for v in value]

			# if len(self.calibration_data) > 0:

			# 	ref = (0, 0) # TODO
			# 	ref_angles = self.calibration_data[str(idCapteur)]
			# 	teta = math.atan(value[1] / value[0])
			# 	phi = math.acos(value[2] / (value[0]**2 + value[1]**2 + value[2]**2)**0.5) 
			# 	value = 

		return value

	def send_data(self, packets):
		try:
			if not self.gui_data_queue.empty():
				threading.Thread(target=self.gui_worker, daemon=True).start()
		except Exception as e:
			# Program has ended
			return

		self.gui_data_queue.put(packets)

	def gui_worker(self):
		while True:
			try:
				packets = self.gui_data_queue.get(timeout=5)
			except queue.Empty:
				# Stop the worker
				return
			except EOFError:
				# Pipe has been ended
				return
			except Exception:
				# Whatever, just start a new worker
				return

			out = {}
			# for packet in packets:
			for packet in packets[:2]:
				if packet['type'] == 'simple':
					for idCapteur, value in packet['data'].items():
						if int(idCapteur) <= 4: # Only fingers
							out[idCapteur] = [value, 0, 0]
				elif packet['type'] == 'vector':
					for idCapteur, vec in packet['data'].items():
						if int(idCapteur) >= 17 and int(idCapteur)%3==1:
							out[int(idCapteur)//3 - 1] = vec


			serialized = ';'.join([','.join([str(k), *list(map(str, v))]) for k, v in out.items()])

			URL = 'http://nitro5:13579/data?data=' + serialized
			# URL = "http://localhost:13579/UpdatePos?bone=1&data={%22test%22:{%22bone%22:1,%20%22rotX%22:0.5}}"
			try:
				requests.get(URL)
			except requests.ConnectionError as e:
				# print('Error while sending data to renderer:', e)
				pass


def run_custom_server(*args):
	server_address = ('', 8085)  # Use a custom port if needed
	httpd = http.server.HTTPServer(server_address, partial(CustomRequestHandler, *args))
	print('Starting HTTP server...')
	httpd.serve_forever()

class DataServer:
	def __init__(self) -> None:
		self.start_server()

	def start_server(self):
		self.manager = multiprocessing.Manager()

		# self.server_event = threading.Event()
		# self.dataQueue = queue.Queue()
		# self.gui_data_queue = queue.Queue()

		self.server_event = self.manager.Event()
		self.dataQueue = self.manager.Queue()
		self.gui_data_queue = self.manager.Queue()
		self.idMvt = self.manager.Value('i', 0)
		self.calibration_data = self.manager.dict()

		if os.path.exists(CALIBRATION_FILE):
			with open(CALIBRATION_FILE, 'r') as f:
				self.calibration_data = json.load(f)
		else:
			self.calibration_data = {}

		# self.server_thread = threading.Thread(target=self.run_server, args=(self.server_event,self.dataQueue, self.gui_data_queue), daemon=True)
		self.server_thread = multiprocessing.Process(target=run_custom_server, args=(self.server_event, self.dataQueue, self.gui_data_queue, self.idMvt, self.calibration_data), daemon=True)
		self.server_thread.start()

	def run_server(self, *args):
		run_custom_server(*args)

if __name__ == '__main__':
	# event = threading.Event()
	# run_custom_server(event)
	serv = DataServer()
	serv.server_event.set()
	serv.server_event.idMvt = 2
	moy = serv.dataQueue.get()

	while True:
		data = serv.dataQueue.get()
		if isinstance(data, MesureSimple):
			print(f"Capteur {data.idCapteur} : {data.valeur}")

	import matplotlib.pyplot as plt

	# You probably won't need this if you're embedding things in a tkinter plot...
	plt.ion()
	fig = plt.figure()
	ax = fig.add_subplot(111)

	x, y = [time.time()], [moy]
	lines = []
	for datay in zip(*y):
		line, = ax.plot(x, datay, '-') # Returns a tuple of line objects, thus the comma
		lines.append(line)
  
	while True:
		time.sleep(1)
		while not serv.dataQueue.empty:
			moy = list(map(lambda e: e[0]*0.8+e[1]*0.2, zip(moy, serv.dataQueue.get())))
			y.append(moy)

		x.append(time.time())
		if len(x) > 50:
			x, y = x[-50:], y[-50:]

		for line, datay in zip(lines, zip(*y)):
			line.set_xdata(x)
			line.set_ydata(datay)
		fig.canvas.draw()
		fig.canvas.flush_events()