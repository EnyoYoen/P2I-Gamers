from functools import partial
import http.server
import json
import math
import multiprocessing
import os
import queue
import threading
import time
import requests

from database import Database
from secret import CALIBRATION_FILE
from dataclass import MesureSimple, MesureVect

class CustomRequestHandler(http.server.BaseHTTPRequestHandler):
	def __init__(self, db, event, que, gui_data_queue, idMvt, calibration_data, *args, **kwargs):
		self.event = event
		self.que = que
		self.idMvt = idMvt
		self.calibration_data = calibration_data

		self.db = db

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
		"""
		Handles the POST request received by the server.

		Parses the request body, sends the data, and saves the measurements to the database.
		"""
		# Get the content length from the request headers
		content_length = int(self.headers['Content-Length'])
		# Read the request body
		post_data = self.rfile.read(content_length)
		# Decode the request body as JSON
		post_body = json.loads(post_data.decode('utf-8'))

		# Initialize packet ID
		idPaquet = 1

		try:
			# Get the ID of the movement data
			idDonneeMouvement = self.idMvt.value
		except AttributeError:
			idDonneeMouvement = 1
		except Exception:
			# Program has ended
			return

		# Initialize lists for simple and vector measurements
		simples, vects = [], []

		# Process each packet in the request body
		for packet in post_body:
			date = packet['time']

			if packet['type'] == 'simple':
				# Process simple measurements
				for idCapteur, value in packet['data'].items():
					idCapteur = int(idCapteur) + 1

					# Fix the sensor value if needed
					value = self.fix_sensor_value(idCapteur, value)

					# Add the measurement to the simples list
					simples.append((idCapteur, idDonneeMouvement, date, value))
					mesure = MesureSimple.from_raw((idCapteur, idDonneeMouvement, date, value))

					try:
						self.que.put(mesure)
					except Exception:
						# Program has ended
						break

			elif packet['type'] == 'vector':
				# Process vector measurements
				for idCapteur, vec in packet['data'].items():
					idCapteur = int(idCapteur) + 1
					vec = self.fix_sensor_value(idCapteur, vec)

					# Add the measurement to the vects list
					vects.append((idCapteur, idDonneeMouvement, date, *vec))
					mesure = MesureVect.from_raw((idCapteur, idDonneeMouvement, date, *vec, idPaquet))

					try:
						self.que.put(mesure)
					except Exception:
						# Program has ended
						break

		# Send the data to the 3D renderer
		self.send_data(simples, vects)

		try:
			is_event_set = self.event.is_set()
		except Exception:
			# Program has ended
			pass
		else:
			if is_event_set and idDonneeMouvement != -1:
				# Save the measurements to the database
				try:
					self.db.add_mesures_multiples(simples, vects)
				except Exception as e:
					print('Erreur durant l\'ajout des mesures:', e)

		# Send the response
		self.send_response(200)
		self.end_headers()
		self.wfile.write(b'Ok')
		# self.wfile.write(b'Hello, World!')

	def fix_sensor_value(self, idCapteur, value):
		"""
		Fixes the sensor value based on the given idCapteur and value.

		Parameters:
		- idCapteur (int or str): The identifier of the sensor.
		- value (float or list): The sensor value to be fixed.

		Returns:
		- float or list: The fixed sensor value.
		"""
		# Convert idCapteur to int if it's a string
		if isinstance(idCapteur, str):
			idCapteur = int(idCapteur)

		if idCapteur <= 10:
			# Simple measurement
			if 1 <= idCapteur <= 5:
				# Pressure sensor
				if not hasattr(self.que, 'pressure_average'):
					pass
					self.que.pressure_average = pressure_average = [[] for _ in range(5)]
				else:
					pressure_average = self.que.pressure_average

				pressure_average[idCapteur-1].append(value)
				samples = 10
				if len(pressure_average[idCapteur-1]) > samples:  # Keep only the last 10 samples
					pressure_average[idCapteur-1] = pressure_average[idCapteur-1][-samples:]

				value = sum(pressure_average[idCapteur-1]) / len(pressure_average[idCapteur-1])
			elif 6 <= idCapteur <= 10:
				# Flexion sensor
				if len(self.calibration_data) > 0:
					frange = self.calibration_data[str(idCapteur)]
					value = (value - frange[1]) / (frange[0] - frange[1])

			# Clamp the value between 0 and 1
			value = min(max(value, 0), 1)
		else:
			# Vector sensor

			# Normalize the vector
			norm = sum([v**2 for v in value]) ** 0.5
			if norm != 0 and norm != 1:
				value = [v / norm for v in value]

			# Calibration
			x, y, z = value
			r = 1

			ref_teta, ref_phi = self.calibration_data.get(str(idCapteur), (None, None))
			if ref_teta is not None:
				teta = math.acos(z/r)
				phi = math.atan2(y, x)

				teta2, phi2 = ref_teta - teta, ref_phi - phi
				x = r * math.sin(teta2) * math.cos(phi2)
				y = r * math.sin(teta2) * math.sin(phi2)
				z = r * math.cos(teta2)
				value = x, y, z

				# # Renormalize the vector -> not needed
				# norm = sum([v**2 for v in value]) ** 0.5
				# if norm != 0 and norm != 1:
				# 	value = [v / norm for v in value]

		return value

	def send_data(self, simple, vect):
		# Add data to be sent to the GUI
		try:
			if not self.gui_data_queue.empty():
				threading.Thread(target=self.gui_worker, daemon=True).start()
		except Exception as e:
			# Program has ended
			return

		self.gui_data_queue.put((simple, vect))

	def gui_worker(self):
		# Send all available data to the GUI
		# This worker is used to avoid blocking the main thread

		while True:
			try:
				simple, vect = self.gui_data_queue.get(timeout=5)
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
			for (idCapteur, idDonneeMouvement, date, value) in simple:
				if 6 <= int(idCapteur) <= 10: # Only fingers
					out[idCapteur-6] = [value, 0, 0]
			for (idCapteur, idDonneeMouvement, date, x, y, z) in vect:
				if int(idCapteur) >= 17 and int(idCapteur)%3==2:
					out[int(idCapteur)//3 - 1] = [x, y, z]

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
	args = [Database()] + list(args)
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
				calibration_data = json.load(f)
				for k, v in calibration_data.items():
					self.calibration_data[k] = v
		# else:
		# 	self.calibration_data = {}

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