from gpiozero import Button
from time import sleep
button = Button(5)

while True:
    if button.is_pressed:
        print("Button is pressed")
    else:
        print(" ")
    sleep(0.1)