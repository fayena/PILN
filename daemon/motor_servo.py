import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)
GPIO.setup(24, GPIO.OUT)

pwm=GPIO.PWM(24, 50)
pwm.start(0)

def motor(pid):
   duty = pid/18 + 2.5
   pwm.ChangeDutyCycle(duty)
   sleep(.2)
   pwm.ChangeDutyCycle(0)
try:
   while True:
      pid = int(input("Enter Angle:"))
      motor(pid)
except KeyboardInterrupt:
    pwm.stop()
    GPIO.cleanup()
