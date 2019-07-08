import RPi.GPIO as GPIO
import time

class Sonar_GPIO():
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        self.F_TRIG = 23 #16 #23
        self.F_ECHO = 24 #20 #24
        GPIO.setup(self.F_TRIG,GPIO.OUT)
        GPIO.setup(self.F_ECHO,GPIO.IN)
        self.R_TRIG = 16 #19
        self.R_ECHO = 20 #26
        GPIO.setup(self.R_TRIG,GPIO.OUT)
        GPIO.setup(self.R_ECHO,GPIO.IN)
        
        self.sonar_front_dist = 0
        self.sonar_rear_dist = 0
        
#        GPIO.output(self.TRIG, False)
        print ("Calibrating.....")
        time.sleep(2)
    def send_f_trigger_pulse(self):
        GPIO.output(self.F_TRIG, True)
        time.sleep(0.00001)
        GPIO.output(self.F_TRIG, False)
        
    def send_r_trigger_pulse(self):
        GPIO.output(self.R_TRIG, True)
        time.sleep(0.00001)
        GPIO.output(self.R_TRIG, False)

    def wait_for_f_echo(self, value, timeout):
        count = timeout
        while GPIO.input(self.F_ECHO) != value and count > 0:
            count = count - 1

    def wait_for_r_echo(self, value, timeout):
        count = timeout
        while GPIO.input(self.R_ECHO) != value and count > 0:
            count = count - 1

    def run(self):
#        print('Into thread')
        self.send_f_trigger_pulse()
        self.wait_for_f_echo(True, 5000)
        start = time.time()
        self.wait_for_f_echo(False, 5000)
        finish = time.time()
        f_pulse_len = finish - start
        f_distance = f_pulse_len * 17150
        self.sonar_front_dist = round(f_distance+1.15, 2)

        self.send_r_trigger_pulse()
        self.wait_for_r_echo(True, 5000)
        start = time.time()
        self.wait_for_r_echo(False, 5000)
        finish = time.time()
        r_pulse_len = finish - start
        r_distance = r_pulse_len * 17150
        self.sonar_rear_dist = round(r_distance + 1.15, 2)

#        print ('Run_Front:',self.sonar_front_dist, '/ Run_Rear:', self.sonar_rear_dist)

        return self.sonar_front_dist, self.sonar_rear_dist


    def run_threaded(self):
#        try:
#        while True:
#        print('Into thread')
        self.send_trigger_pulse()
        self.wait_for_echo(True, 5000)
        start = time.time()
        self.wait_for_echo(False, 5000)
        finish = time.time()
        pulse_len = finish - start
        distance = pulse_len * 17150
        self.sonar_front_dist = round(distance+1.15, 2)
#        self.sonar_front_dist = distance
        print ('Thread_Front:',self.sonar_front_dist)
        return self.sonar_front_dist
#        except KeyboardInterrupt:
#            GPIO.cleanup()

    def update(self):
#        try:
#        while True:
        print('Into update')
        self.send_trigger_pulse()
        self.wait_for_echo(True, 5000)
        start = time.time()
        self.wait_for_echo(False, 5000)
        finish = time.time()
        pulse_len = finish - start
        distance = pulse_len * 17150
        self.sonar_front_dist = round(distance+1.15, 2)
#        self.sonar_front_dist = distance
        print ('Update sonar dist:',self.sonar_front_dist)



