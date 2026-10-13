import RPI.GPIO as GPIO
import sys
'''


Forwards:

IN1 = high
IN2 = low

Backwards:

IN1 = low
IN2 = high

Stop:

IN1 = low
IN2 = low


'''




ENABLEL = 0
IN1L = 0
IN2L = 0

ENABLER = 0
IN1R = 0
IN2R = 0

motorLeft = [IN1L,IN2L]
motorRight = [IN1R,IN2R]

GPIO.setmode(GPIO.BOARD)
GPIO.cleanup()

GPIO.setup(motorLeft,GPIO.OUT)
GPIO.setup(motorRight,GPIO.OUT)
GPIO.setup(ENABLEL,GPIO.OUT)
GPIO.setup(ENABLER,GPIO.OUT)
GPIO.output(motorLeft,GPIO.LOW)
GPIO.output(motorRight,GPIO.LOW)




pL=GPIO.PWM(ENABLEL,1000)
pR=GPIO.PWM(ENABLER,1000)


#pX.ChangeDutyCycle(n)          n is a values from 0 to 100 to control speed. Stick between 25 and 75 for now


GPIO.output(motorLeft, (GPIO.HIGH,GPIO.LOW))

