import http.server
import json
import database

db = database.Database()

class CustomRequestHandler(http.server.BaseHTTPRequestHandler):
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

		date = post_body['time']
		idPaquet = 1
		idDonneeMouvement = 2
		if post_body['type'] == 'simple':
			for idCapteur, value in post_body['data'].items():
				db.add_mesure_simple(int(idCapteur)+1, idPaquet, idDonneeMouvement, date, value)

		elif post_body['type'] == 'vector':
			for idCapteur, vec in post_body['data'].items():
				db.add_mesure_vect(int(idCapteur)+1, idPaquet, idDonneeMouvement, date, *vec)

		self.send_response(200)
		self.end_headers()
		self.wfile.write(b'Ok')
		# self.wfile.write(b'Hello, World!')

def run_custom_server():
	server_address = ('', 8085)  # Use a custom port if needed
	httpd = http.server.HTTPServer(server_address, CustomRequestHandler)
	print('Starting HTTP server...')
	httpd.serve_forever()

if __name__ == '__main__':
	run_custom_server()
