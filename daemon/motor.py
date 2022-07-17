import RPi.GPIO as GPIO
import time

servoPIN =18 
GPIO.setmode(GPIO.BCM)
GPIO.setup(servoPIN, GPIO.OUT)

p = GPIO.PWM(servoPIN, 50) # GPIO 17 for PWM with 50Hz
p.start(4.3) # Initialization
def motor (duty):
        #pwm=GPIO.PWM(24,50)
        #pwm.start(0)
        duty = duty*0.029 + 4.3
        p.ChangeDutyCycle(duty)
        time.sleep(1)
        #p.ChangeDutyCycle(0)
        #print("pid:",pid)
        #print("duty:",duty)

 
try:
    while True:
        value = input("Please enter the PID:\n")
        value = int(value)
        motor(value)

except KeyboardInterrupt:
  p.stop()
  GPIO.cleanup()
