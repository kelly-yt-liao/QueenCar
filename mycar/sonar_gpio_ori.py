import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BOARD)
TRIG = 23
ECHO = 24
i=0
GPIO.setup(TRIG,GPIO.OUT)
GPIO.setup(ECHO,GPIO.IN)
GPIO.output(TRIG, False)
print ("Calibrating.....")
time.sleep(2)
print ("Place the object......")
try:
    while True:
        GPIO.output(TRIG, True)
        time.sleep(0.00001)
        GPIO.output(TRIG, False)
#        print('While True')
        while GPIO.input(ECHO)==0:
            pulse_start = time.time()
            print('Echo 0')
        while GPIO.input(ECHO)==1:
            print('Echo 1')
            pulse_end = time.time()
            pulse_duration = pulse_end - pulse_start
            distance = pulse_duration * 17150
            distance = round(distance+1.15, 2)
        if distance<=200 and distance>=0:
            print ("distance:",distance,"cm")
            i=1
        if distance>20 and i==1:
            print ("place the object....")
            i=0
            time.sleep(0.5)
except KeyboardInterrupt:
    GPIO.cleanup()