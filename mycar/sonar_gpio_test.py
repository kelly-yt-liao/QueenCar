import RPi.GPIO as GPIO
import time

TRIG = 23
ECHO = 24

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG,GPIO.OUT)
GPIO.setup(ECHO,GPIO.IN)
GPIO.output(TRIG, False)
print ("Calibrating.....")
time.sleep(2)
print ("Place the object......")

def send_trigger_pulse():
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)    

def wait_for_echo(value, timeout):
    count = timeout
    while GPIO.input(ECHO) != value and count > 0:
        count = count - 1
        
def get_distance():
    send_trigger_pulse()
    wait_for_echo(True, 5000)
    start = time.time()
    wait_for_echo(False, 5000)
    finish = time.time()
    pulse_len = finish - start
    distance_cm = pulse_len * 17150
    return (distance_cm)

while True:
    print("cm=%f" % get_distance())
    time.sleep(0.5)

#try:
#    while True:
#        GPIO.output(TRIG, True)
#        time.sleep(0.00001)
#        GPIO.output(TRIG, False)
##        print('While True')
#    while GPIO.input(ECHO)==0:
#        pulse_start = time.time()
#        print('Echo 0')
#    while GPIO.input(ECHO)==1:
#        print('Echo 1')
#        pulse_end = time.time()
#        pulse_duration = pulse_end - pulse_start
#        distance = pulse_duration * 17150
#        distance = round(distance+1.15, 2)
#    if distance<=200 and distance>=0:
#        print ("distance:",distance,"cm")
#        i=1
#    if distance>20 and i==1:
#        print ("place the object....")
#        i=0
#        time.sleep(0.5)
#except KeyboardInterrupt:
#    GPIO.cleanup()