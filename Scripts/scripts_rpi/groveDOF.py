import json
import os
import time
from mpu9250_jmdev.registers import *
from mpu9250_jmdev.mpu_9250 import MPU9250

SETTINGS_PATH = 'MPU9250_settings.json'

class MPUWrapper:
	def __init__(self, buses):
		self.buses = buses
		self.initialize_mpus()

	def initialize_mpus(self, buses=None):
		self.mpus = {}
		if buses is None:
			buses = self.buses

		for bus in buses: #[3, 4, 5]:
			loop = True
			while loop:
				loop = False
				mpu = MPU9250(
					address_ak=AK8963_ADDRESS, 
					address_mpu_master=MPU9050_ADDRESS_68, # In 0x68 Address
					address_mpu_slave=None, 
					bus=bus,
					gfs=GFS_1000, 
					afs=AFS_8G, 
					mfs=AK8963_BIT_16, 
					mode=AK8963_MODE_C100HZ)

				try:
					mpu.configure() # Apply the settings to the registers.
				except OSError as e:
					if e.errno == 6:
						# The device isn't connected
						print(f'MPU9250 not found on bus {bus}')
						# loop = True
					else:
						raise
				else:
					self.mpus[bus] = mpu

		# self.load_config()

	def configure_mpus(self, buses=None):
		if buses is None:
			buses = self.buses

		settings = {}
		for bus, mpu in self.mpus.items():
			print(f'Calibrating MPU9250 on bus {bus}')
			try:
				mpu.calibrate()

				settings[bus] = {
					'abias': mpu.abias, # Get the master accelerometer biases
					'gbias': mpu.gbias, # Get the master gyroscope biases

					'magScale': mpu.magScale, # Get magnetometer soft iron distortion
					'mbias': mpu.mbias # Get magnetometer hard iron distortion
				}

				mpu.configure()
			except OSError as e:
				if e.errno == 6:
					# The device isn't connected
					print(f'MPU9250 not found on bus {bus} during calibration')
					# loop = True
				else:
					raise

		with open(SETTINGS_PATH, 'w') as f:
			json.dump(settings, f)

	def load_config(self):
		# Tries to load saved config from a file
		if not os.path.exists(SETTINGS_PATH):
			print(f'Not settings file, recalibrating {len(self.mpus)} sensors')
			return self.configure_mpus()

		with open(SETTINGS_PATH, 'r') as f:
			settings = json.load(f)

		if len(settings) != len(self.mpus):
			# There are/were missing sensors, so just try to configure what you can
			print('MPU9250 settings are invalid!')

		for bus, data in settings.items():
			mpu = self.mpus.get(int(bus), None)
			if mpu is not None:
				for attr, value in data.items():
					setattr(mpu, attr, value)

	def get_data(self):
		out = {}
		for bus, mpu in self.mpus.items():
			data = {
				'acc': [0]*3,
				'gyro': [0]*3,
				'mag': [0]*3
			}
			for key, value in zip(mpu.getAllDataLabels(), mpu.getAllData()):
				key = key.split('_')
				if key[0] == 'slave': continue # We won't use slaves

				if key[0] == 'master':
					key = key[1:]

				if key and key[0] in data:
					name, axis = key
					axis_ind = list('xyz').index(axis)
					data[name][axis_ind] = value

			out[bus] = data

		return out

if __name__ == "__main__":
	mpu = MPU9250(
		address_ak=AK8963_ADDRESS, 
		address_mpu_master=MPU9050_ADDRESS_68, # In 0x68 Address
		address_mpu_slave=None, 
		bus=3,
		gfs=GFS_1000, 
		afs=AFS_8G, 
		mfs=AK8963_BIT_16, 
		mode=AK8963_MODE_C100HZ)

	if True:
		# For the magnetometer
		mpu.calibrateAK8963() # Calibrate sensors
		mpu.configure() # The calibration function resets the sensors, so you need to reconfigure them

		magScale = mpu.magScale # Get magnetometer soft iron distortion
		mbias = mpu.mbias # Get magnetometer hard iron distortion

		pass

	if False:
		# For all sensors
		mpu.calibrate()


	mpu.configure() # Apply the settings to the registers.

	while True:

		print("|.....MPU9250 in 0x68 Address.....|")
		print("Accelerometer", mpu.readAccelerometerMaster())
		print("Gyroscope", mpu.readGyroscopeMaster())
		print("Magnetometer", mpu.readMagnetometerMaster())
		print("Temperature", mpu.readTemperatureMaster())
		print("\n")

		time.sleep(1)