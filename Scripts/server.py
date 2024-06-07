from functools import partial
import http.server
import json
import queue
import threading
import time

import requests
from database import db
from dataclass import MesureSimple, MesureVect

class CustomRequestHandler(http.server.BaseHTTPRequestHandler):
	def __init__(self, event, que, *args, **kwargs):
		self.event = event
		self.que = que

		super().__init__(*args, **kwargs)

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
			idDonneeMouvement = self.event.idMvt
		except AttributeError:
			idDonneeMouvement = -1

		fingers_ranges = {
			1:[0.2, 0],
			2:[0.37, 0.2],
			3:[0.25, 0.17],
			4:[0.2, 0],
			5:[0.33, 0.2],
		}

		simples, vects = [], []
		for packet in post_body:
			date = packet['time']

			if packet['type'] == 'simple':
				for idCapteur, value in packet['data'].items():
					idCapteur = int(idCapteur)+1
					if idCapteur > 5:
						frange = fingers_ranges[idCapteur-5]
						value = (value-frange[1]) / (frange[0]-frange[1])

						value = min(max(value, 0), 1)

					simples.append((idCapteur, idDonneeMouvement, date, value))
					mesure = MesureSimple.from_raw((idCapteur, idDonneeMouvement, date, value))

					self.que.put(mesure)

			elif packet['type'] == 'vector':
				for idCapteur, vec in packet['data'].items():
					vects.append((int(idCapteur)+1, idDonneeMouvement, date, *vec))
					mesure = MesureVect.from_raw((int(idCapteur)+1, idDonneeMouvement, date, *vec, idPaquet))

					self.que.put(mesure)

		if self.event.is_set():
			print(f'Saving 1 packet, size: {len(post_body)}')

			db.add_mesures_multiples(simples, vects)

			print(f'-> Done, took {time.time()-start}sec')

		self.send_response(200)
		self.end_headers()
		self.wfile.write(b'Ok')
		# self.wfile.write(b'Hello, World!')

	def send_data(self, packets, thread=False):
		if not thread:
			threading.Thread(target=self.send_data, args=(packets, True)).start()
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
					if int(idCapteur) in (21, 24, 27):
						out[int(idCapteur)//3 -2] = vec


		serialized = ';'.join([','.join([str(k), *list(map(str, v))]) for k, v in out.items()])

		URL = 'http://nitro5:13579/data?data=' + serialized
		# URL = "http://localhost:13579/UpdatePos?bone=1&data={%22test%22:{%22bone%22:1,%20%22rotX%22:0.5}}"
		try:
			requests.get(URL)
		except requests.ConnectionError as e:
			# print('Error while sending data to renderer:', e)
			pass



def run_custom_server(event, que):
	server_address = ('', 8085)  # Use a custom port if needed
	httpd = http.server.HTTPServer(server_address, partial(CustomRequestHandler, event, que))
	print('Starting HTTP server...')
	httpd.serve_forever()

class DataServer:
	def __init__(self) -> None:
		self.start_server()

	def start_server(self):
		self.server_event = threading.Event()
		self.dataQueue = queue.Queue()
		self.server_thread = threading.Thread(target=self.run_server, args=(self.server_event,self.dataQueue), daemon=True)
		self.server_thread.start()

	def run_server(self, event, que):
		run_custom_server(event, que)

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