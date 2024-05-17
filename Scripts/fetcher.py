import json
import math
import random
import time
import requests

# LORA_URL = "https://eu1.cloud.thethings.network/api/v3/as/applications/projet-2024-224b/packages/storage/uplink_message" # ??

DEVICE_ID = "eui-a8610a33301b7302"
LORA_URL = f"https://eu1.cloud.thethings.network/api/v3/as/applications/projet-2024-224b/devices/{DEVICE_ID}/packages/storage/uplink_message"
KEY = "NNSXS.S473SKFIKNWPGK2OHRTWEU3BRBKHGAN4NSZE5SQ.U7FLEVGXRVOHDCFKH7PVKIQJEMZHJVM77P57Y5K42UZLB3LKIA2A"

RENDER_URL = "http://localhost:13579/data"

def send_data(data):
	out = json.dumps({"rotations": data})
	try:
		requests.get(f"{RENDER_URL}?data={out}")
	except requests.ConnectionError:
		pass
	except Exception as e:
		print(e)
		pass

def get_data():
	try:
		headers = {"Authorization": f"Bearer {KEY}"}
		data = requests.get(LORA_URL, headers=headers)
	except requests.ConnectionError:
		pass
	except Exception as e:
		print(e)
		pass
	else:
		out = []
		if len(data.text) == 0:
			print('No data available!')
			return False
		for entry in data.text.strip().split('\n'):
			entry = json.loads(entry)
			try:
				data = entry['result']['uplink_message']['decoded_payload']
			except KeyError:
				pass
			except Exception as e:
				pass
			else:
				out.append((data, entry['result']['received_at']))
		return out

def get_parsed_data():
	global tmp
	joints = {
		"arm": [
			"shoulder",
			"arm",
			"forearm",
			"hand"], 
		"hand":[
			"finger1",
			"finger2",
			"finger3",
			"finger4",
			"thumb"
		]
	}
	data = get_data()
	if data is False:
		return False

	for entry, received_at in data:
		if not 'joint_id' in entry:
			continue
		name = joints[("hand" if entry['is_hand'] else "arm")][int(f"0x{entry['joint_id']}", 0)]
		if name not in tmp or received_at > tmp[name][1]:
			tmp[name] = [entry['angle'], received_at]
		else:
			tmp[name][0] = 0

	out = {}
	for k, (v, t) in tmp.items():
		out[k] = v

	return out


tmp = {}

while True:
	out = get_parsed_data()
	if out is False:
		print('Stopping...')
		break

	data = []
	# for name in [
	# 	"shoulder",
	# 	"arm",
	# 	"forearm",
	# 	"hand",
	# 	"finger1",
	# 	"finger2",
	# 	"finger3",
	# 	"finger4",
	# 	"thumb",
	# ]:
	# 	data.append(
	# 		{
	# 			"name": name,
	# 			"x": random.random() * 360,
	# 			"y": random.random() * 360,
	# 			"z": random.random() * 360,
	# 		}
	# 	)
	has_data = any(map(lambda e: e[1] != 0, out.items()))
	if has_data:
		for name, value in out.items():
			data.append(
				{
					"name": name,
					"x": 0,
					"y": 0,
					"z": value
				}
			)

		send_data(data)
		print('Sent:', data)
	time.sleep(2)