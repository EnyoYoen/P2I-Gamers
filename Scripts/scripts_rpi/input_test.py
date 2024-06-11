from gpiozero import Button
import time

MAX = 21
btns = [None for _ in range(MAX)]
for pin in range(MAX):
	try:
		btn = Button(pin)
	except Exception:
		pass
	else:
		btns[pin] = btn

top = '|'.join(map(lambda e: str(e).center(5), range(MAX)))
print(top)
while True:
	txt = '|'.join(map(lambda e: str(e.is_pressed if e else None).center(5), btns))
	print(txt + '\r', end ="")
	time.sleep(0.1)