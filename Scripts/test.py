import json
import random
import time
import requests
import math

URL = "http://localhost:13579/data"
amplitude = 0.2

while True:
	data = []
	reset = []
	for name in [
		"shoulder",
		"arm",
		"forearm",
		"hand",
		"finger1",
		"finger2",
		"finger3",
		"finger4",
		"thumb",
	]:
		x, y, z = [(random.random()-0.5) * 2 * 360 * amplitude for _ in range(3)]
		data.append(
			{
				"name": name,
				"x": x,
				"y": y,
				"z": z,
			}
		)
		reset.append(
			{
				"name": name,
				"x": -x,
				"y": -y,
				"z": -z,
			}
		)

	for d in [data, reset]:
		out = json.dumps({"rotations": d})
		try:
			requests.get(f"{URL}?data={out}")
		except requests.ConnectionError:
			pass
		except Exception as e:
			print(e)
			pass
		time.sleep(2)
