from functools import partial
import http.server
import json
import queue
import threading
import time
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

		if self.event.is_set():
			print(f'Saving 1 packet, size: {len(post_body)}')
			start = time.time()
			idPaquet = 1
			idDonneeMouvement = self.event.idMvt
			if False:
				for packet in post_body:
					date = packet['time']

					if packet['type'] == 'simple':
						for idCapteur, value in packet['data'].items():
							db.add_mesure_simple(int(idCapteur)+1, idPaquet, idDonneeMouvement, date, value, save=False)

					elif packet['type'] == 'vector':
						for idCapteur, vec in packet['data'].items():
							db.add_mesure_vect(int(idCapteur)+1, idPaquet, idDonneeMouvement, date, *vec, save=False)

				db.save()

			simples, vects = [], []
			for packet in post_body:
				date = packet['time']

				if packet['type'] == 'simple':
					for idCapteur, value in packet['data'].items():
						simples.append((int(idCapteur)+1, idPaquet, idDonneeMouvement, date, value))
						mesure = MesureSimple.from_raw((int(idCapteur)+1, date, value, idPaquet, idDonneeMouvement))

				elif packet['type'] == 'vector':
					for idCapteur, vec in packet['data'].items():
						vects.append((int(idCapteur)+1, idPaquet, idDonneeMouvement, date, *vec))
						mesure = MesureVect.from_raw((int(idCapteur)+1, date, *vec, idPaquet, idDonneeMouvement))

				self.que.put(mesure)

			db.add_mesures_multiples(simples, vects)

			print(f'-> Done, took {time.time()-start}sec')

		self.send_response(200)
		self.end_headers()
		self.wfile.write(b'Ok')
		# self.wfile.write(b'Hello, World!')

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
	event = threading.Event()
	run_custom_server(event)
