from adafruit_servokit import ServoKit
kit = ServoKit(channels=16)
while True:
	angle = int(input('Angle: '))
	kit.servo[0].angle = angle