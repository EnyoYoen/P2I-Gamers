import asyncio
import io
import json
import logging
import math
import os
import queue
import threading
from tkinter import *
from PIL import ImageTk, Image
import uuid
import numpy as np

import cv2
import numpy
from aiortc import (
	RTCIceCandidate,
	RTCPeerConnection,
	RTCSessionDescription,
	VideoStreamTrack,
	MediaStreamTrack,
)
from aiortc.contrib.signaling import BYE, candidate_from_sdp
from aiortc.contrib.media import MediaRecorder, MediaRelay, MediaBlackhole, MediaStreamError
from websockets.server import serve
from websockets.exceptions import ConnectionClosedOK
from av import VideoFrame

def object_from_string(message_str):
	message = json.loads(message_str)
	if message["type"] in ["answer", "offer"]:
		return RTCSessionDescription(sdp=message['data']['sdp'], type=message['type'])
	elif message["type"] == "candidate" and message["data"]["candidate"]:
		candidate = candidate_from_sdp(message["data"]["candidate"].split(":", 1)[1])
		candidate.sdpMid = message["data"]["sdpMid"]
		candidate.sdpMLineIndex = message["data"]["sdpMLineIndex"]
		return candidate
	elif message["type"] == "bye":
		return None


def object_to_string(obj, from_):
	if isinstance(obj, RTCSessionDescription):
		message = {
			"from": from_,
			"type": obj.type,
			"data": {
				"sdp": obj.sdp,
			}
		}
	else:
		assert obj is BYE
		message = {"type": "bye"}
	return json.dumps(message, sort_keys=True)


async def receive(ws):
	try:
		data = await ws.recv()
	except asyncio.IncompleteReadError: #TODO: replace to occur from websocket connection
		print("IncompleteReadError")
		ret = None
	except ConnectionClosedOK:
		ret = None
	else:
		ret = object_from_string(data)

	if ret == None:
		print("remote host says good bye!")
		ret = BYE

	return ret

async def send(ws, descr, from_):
	data = object_to_string(descr, from_)
	
	# data["from"] = pc._RTCPeerConnection__stream_id, #_RTCPeerConnection__cname
	# data["to"]: ""
	await ws.send(data + '\n')

class FlagVideoStreamTrack(VideoStreamTrack):
	"""
	A video track that returns an animated flag.
	"""

	def __init__(self):
		super().__init__()  # don't forget this!
		self.counter = 0
		height, width = 480, 640

		# generate flag
		data_bgr = numpy.hstack(
			[
				self._create_rectangle(
					width=213, height=480, color=(255, 0, 0)
				),  # blue
				self._create_rectangle(
					width=214, height=480, color=(255, 255, 255)
				),  # white
				self._create_rectangle(width=213, height=480, color=(0, 0, 255)),  # red
			]
		)

		# shrink and center it
		M = numpy.float32([[0.5, 0, width / 4], [0, 0.5, height / 4]])
		data_bgr = cv2.warpAffine(data_bgr, M, (width, height))

		# compute animation
		omega = 2 * math.pi / height
		id_x = numpy.tile(numpy.array(range(width), dtype=numpy.float32), (height, 1))
		id_y = numpy.tile(
			numpy.array(range(height), dtype=numpy.float32), (width, 1)
		).transpose()

		self.frames = []
		for k in range(30):
			phase = 2 * k * math.pi / 30
			map_x = id_x + 10 * numpy.cos(omega * id_x + phase)
			map_y = id_y + 10 * numpy.sin(omega * id_x + phase)
			self.frames.append(
				VideoFrame.from_ndarray(
					cv2.remap(data_bgr, map_x, map_y, cv2.INTER_LINEAR), format="bgr24"
				)
			)

	async def recv(self):
		return None
		pts, time_base = await self.next_timestamp()

		frame = self.frames[self.counter % 30]
		frame.pts = pts
		frame.time_base = time_base
		self.counter += 1
		return frame

	def _create_rectangle(self, width, height, color):
		data_bgr = numpy.zeros((height, width, 3), numpy.uint8)
		data_bgr[:, :] = color
		return data_bgr


class VideoTransformTrack(MediaStreamTrack):
	"""
	A video stream track that transforms frames from an another track.
	"""

	kind = "video"

	def __init__(self, track, que):
		super().__init__()  # don't forget this!
		self.track = track
		self.video_que = que

	async def recv(self):
		try:
			frame = await self.track.recv()
			img = frame.to_ndarray(format="bgr24")

			await self.video_que.put(img)

			return frame
		except MediaStreamError:
			pass
		except Exception as e:
			pass

logger = logging.getLogger("pc")
# logging.basicConfig(level=logging.INFO)
pcs = set()
# relay = MediaRelay()

async def callback(ws, video_queue):
	pc = RTCPeerConnection()
	pc_id = "PeerConnection(%s)" % uuid.uuid4()
	pcs.add(pc)

	def log_info(msg, *args):
		logger.info(pc_id + " " + msg, *args)

	log_info("Created for %s", ws.remote_address)

	if not os.path.exists("vid"):
		os.makedirs("vid")
	# recorder = MediaRecorder('images/%3d.png')
	recorder = MediaBlackhole()

	# data_channel = pc.createDataChannel("data")
	pc.addTrack(FlagVideoStreamTrack())
	# send offer
	# pc.addTrack(data_channel)
	await pc.setLocalDescription(await pc.createOffer())
	await send(ws, pc.localDescription, pc._RTCPeerConnection__stream_id)

	@pc.on("connectionstatechange")
	async def on_connectionstatechange():
		log_info("Connection state is %s", pc.connectionState)
		if pc.connectionState == "failed":
			await pc.close()
			pcs.discard(pc)

	@pc.on("track")
	def on_track(track):
		log_info("Track %s received", track.kind)

		if track.kind == "video":
			# recorder.addTrack(relay.subscribe(track))
			# recorder.addTrack(track)
			recorder.addTrack(VideoTransformTrack(track, video_queue))

		@track.on("ended")
		async def on_ended():
			log_info("Track %s ended", track.kind)
			await recorder.stop()

	while True:
		obj = await receive(ws)

		if isinstance(obj, RTCSessionDescription):
			await pc.setRemoteDescription(obj)
			await recorder.start()

			if obj.type == "offer":
				# send answer
				pc.addTrack(FlagVideoStreamTrack())
				# data_channel = pc.createDataChannel("data")

				await pc.setLocalDescription(await pc.createAnswer())

				answer = pc.localDescription
				await send(ws, answer, pc._RTCPeerConnection__stream_id)

		elif isinstance(obj, RTCIceCandidate):
			await pc.addIceCandidate(obj)

		elif obj is BYE:
			print("Exiting")
			await recorder.stop()
			break


async def on_shutdown():
	# close peer connections
	coros = [pc.close() for pc in pcs]
	await asyncio.gather(*coros)
	pcs.clear()


async def run(host=None, port=None, video_queue=None):
	# connect signaling
	host = host or '127.0.0.1'
	port = port or 80
	async with serve(lambda ws, v=video_queue: callback(ws, v), host, port):
		await asyncio.Future()


def start_stream_client(video_que=None, thread=False):
	if thread is False:
		video_que = asyncio.Queue()
		threading.Thread(target=start_stream_client, args=(video_que, True), daemon=True).start()
		return video_que

	# run event loop
	loop = asyncio.new_event_loop()
	asyncio.set_event_loop(loop)
	try:
		loop.run_until_complete(
			run(video_queue=video_que)
		)
	except KeyboardInterrupt:
		pass
	except Exception as e:
		print(e)
	finally:
		# cleanup
		loop.run_until_complete(on_shutdown())


def start_tkinter(video_que):
	
	root = Tk()
	# Create a frame
	app = Frame(root, bg="white")
	app.grid()
	# Create a label in the frame
	lmain = Label(app)
	lmain.grid()
 
	display_stream(lmain, video_que)
	root.mainloop()

def display_stream(tk_label, video_que):
	tk_label.after(10, display_stream, tk_label, video_que)
	try:
		frame = video_que.get_nowait()

		cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
		img = Image.fromarray(cv2image)
		imgtk = ImageTk.PhotoImage(image=img)
		tk_label.imgtk = imgtk
		tk_label.configure(image=imgtk)
	except queue.Empty:
		pass
	except asyncio.QueueEmpty:
		pass
	except Exception as e:
		pass

if __name__ == "__main__":
	# video_que = io.BytesIO()
	video_que = start_stream_client()
	start_tkinter(video_que)
	# Closes all the frames 
	cv2.destroyAllWindows() 