from gpiozero import Button

button = Button(1)
button.wait_for_press()
print('You pushed me')