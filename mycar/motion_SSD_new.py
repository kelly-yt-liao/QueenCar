import os
import numpy as np
import glob
#import RPi.GPIO as GPIO
import cv2
import time
#import serial

class MotDec():
    def __init__(self):
#        #Initialize GIPO for sonar module
#        GPIO.setmode(GPIO.BOARD)
#        self.TRIG = 23
#        self.ECHO = 24
#        GPIO.setup(self.TRIG,GPIO.OUT)
#        GPIO.setup(self.ECHO,GPIO.IN)
#        GPIO.output(self.TRIG, False)
#        print ("Calibrating Sonar Module.....")
#        time.sleep(2)
        #Initialize Motion Detection Function
        self.frame = None
        self.w_center = 0.0
        self.h_max = 0.0
        self.ssd_angle = 0.0
        self.ssd_throttle = 0.0
        self.info_cnt = 0
        self.cnt = 0
        self.psn_det_loss_cnt = 0
        self.mode = 'user'
#        self.ser = serial.Serial('/dev/ttyACM0',115200)
        self.sonar_front_dist = 0
        self.sonar_rear_dist = 0
        self.front_safe_dist = 80 #unit: cm
        self.front_min_safe_dist = 30 #unit: cm
        self.rear_safe_dist = 20  # unit: cm
        # self.rear_min_safe_dist = 30  # unit: cm
        self.person_detected_flag = False
        self.sh_start_time = 0
        self.search_mode_activate = False
        self.backward_mode_activate = False
        self.bw_mode = 'default'
        self.sh_mode = 'default'
        self.bw_start_time = 0
        self.forward_obs_avoid_flag = False
        self.motion_state = 'default'
    
#    def sonar(self):
#        try:
#            while True:
#                GPIO.output(self.TRIG, True)
#                time.sleep(0.00001)
#                GPIO.output(self.TRIG, False)
#            while GPIO.input(self.ECHO)==0:
#                pulse_start = time.time()
#            while GPIO.input(self.ECHO)==1:
#                pulse_end = time.time()
#                pulse_duration = pulse_end - pulse_start
#                distance = pulse_duration * 17150
#                self.sonar_front_dist = round(distance+1.15, 2)
#            print ('Front:',self.sonar_front_dist)    
#        except KeyboardInterrupt:
#            GPIO.cleanup()

    def event_handler(self, mode):
        if mode == 'search_init':
            #time unit is second
            self.ssd_angle = 0
            self.ssd_throttle = 0.0
            if time.time() - self.sh_start_time > 1:
                self.sh_mode = 'search_step_1'
        elif mode == 'search_step_1':   
            if time.time() - self.sh_start_time > 2:
                self.ssd_angle = 0.8
                self.ssd_throttle = 0.35
        elif mode == 'backward_init':
            if time.time() - self.bw_start_time > 1:
                self.ssd_angle = 0.0
                self.ssd_throttle = -0.2
                self.bw_mode = 'backward_step_1'
        elif mode == 'backward_step_1':
            if time.time() - self.bw_start_time > 1:
                self.ssd_angle = 0.0
                self.ssd_throttle = 0.0
                if self.search_mode_activate or self.forward_obs_avoid_flag:
                    self.bw_mode = 'backward_obs_avoid'
                else:
                    self.bw_mode = 'backward_step_2'
        elif mode == 'backward_step_2':
            if time.time() - self.bw_start_time > 2:
                self.ssd_angle = 0.0
                self.ssd_throttle = -0.35
        elif mode == 'backward_obs_avoid':
            if time.time() - self.bw_start_time > 2:
                self.ssd_angle = -0.8
                self.ssd_throttle = -0.35

        print (mode)


    def search_mode(self):
        self.event_handler(self.sh_mode)
#        print ('Entering Search Mode!')

    def backward_mode(self):
        if (self.sonar_rear_dist < self.rear_safe_dist) and (self.sonar_rear_dist > 0):
            self.ssd_angle = 0.0
            self.ssd_throttle = 0.0
            self.cnt += 1
            if self.cnt == 5:
                print('Something is ', self.sonar_rear_dist, '(cm) behind the car!')
                self.cnt = 0
            if self.search_mode_activate:
                self.backward_mode_activate = False
                self.sh_mode = 'search_init'
                self.sh_start_time = time.time()
                self.search_mode()
        else:
            self.event_handler(self.bw_mode)
            print ('Entering Backward Mode!')

    def run(self, img_arr=None, grp_x=None, max_h=None, dtec_flag=None, frt_dis=None, rear_dis=None):
        self.frame = img_arr
        self.w_center = grp_x
        self.h_max = max_h
        self.person_detected_flag = dtec_flag
        self.sonar_front_dist = frt_dis
        self.sonar_rear_dist = rear_dis

        #get sonar distance
#        line = self.ser.readline()
#        print(line)
#        self.sonar()
        if (self.sonar_front_dist < self.front_min_safe_dist) and (self.sonar_front_dist > 0):
            self.motion_state = 'Too Close! Backward Mode'
            self.backward_mode_activate = True
            if self.bw_mode == 'default':
                self.ssd_throttle = 0.0
                self.bw_mode = 'backward_init'
                self.bw_start_time = time.time()
            self.backward_mode()

        elif (self.sonar_front_dist < self.front_safe_dist) and (self.sonar_front_dist > 0):
#        elif (self.sonar_front_dist < self.front_safe_dist) or (self.sonar_rear_dist < self.rear_safe_dist):
            if self.search_mode_activate and self.bw_mode == 'default': #If car encounter obstacle in searching mode.
                self.ssd_throttle = 0.0
                self.backward_mode_activate = True
                self.bw_mode = 'backward_init'
                self.bw_start_time = time.time()
                self.backward_mode()
#                time.sleep(2)
            elif self.search_mode_activate and self.backward_mode_activate:
                self.backward_mode()
            else:
                self.motion_state = 'Front obstacle avoid! Backward Mode'
                if not self.forward_obs_avoid_flag:
                    self.ssd_throttle = 0.0
                    self.bw_start_time = time.time()
                    self.forward_obs_avoid_flag = True
                    
                
                if (time.time()-self.bw_start_time) > 3 and not self.backward_mode_activate:
                    self.backward_mode_activate = True
                    self.bw_mode = 'backward_init'
                    self.bw_start_time = time.time()
                
                self.backward_mode()
                
#                self.ssd_throttle = 0.0
                
            self.cnt += 1

            if self.cnt == 5:
                print ('Something is ', self.sonar_front_dist, '(cm) in front of car!')
                self.cnt = 0

        else:

                
            if self.forward_obs_avoid_flag:
                self.bw_mode = 'default'
                self.backward_mode_activate = False
                self.forward_obs_avoid_flag = False
                print ('forward_obs_avoid_flag = False')
            
            if self.person_detected_flag:
                self.motion_state = 'Chasing Mode'
                if self.backward_mode_activate:
                    self.ssd_angle = 0
                    self.ssd_throttle = 0.0
                    self.bw_mode = 'default'
                    self.backward_mode_activate = False
                    print ('Backward Finish!')
#                    time.sleep(2)
                elif self.search_mode_activate:
                    self.ssd_angle = 0
                    self.ssd_throttle = 0.0
                    self.sh_mode = 'default'
                    self.search_mode_activate = False
                    print ('Searching Finish!')
#                    time.sleep(2)
                                        
                # when people detected, calculate target steering angle
                if (self.w_center -320) >= 0:
                    self.ssd_angle = min(int((self.w_center - 320)/32)*0.2 , 1)
                else:
                    self.ssd_angle = max(-1, int((self.w_center - 320)/32)*0.2)

                if self.h_max >= 450:
                    self.ssd_throttle = 0.0
                elif self.h_max >= 180:
                    self.ssd_throttle = 0.3
                else:
                    self.ssd_throttle = 0.4
                self.psn_det_loss_cnt = 0
                
                if (self.sonar_front_dist < self.front_safe_dist) and (self.sonar_front_dist > 0):
                    self.ssd_throttle = 0.0
                
#                print ('Chasing Mode')    
            elif not self.person_detected_flag and self.psn_det_loss_cnt == 100:
                          
                self.motion_state = 'Nobody detected! Searching Mode'
                if self.backward_mode_activate:
                    self.bw_mode = 'default'
                    self.backward_mode_activate = False
                    print ('Backward Finish!')
                # activate search mode when system can't detect people
                self.search_mode_activate = True
                
                if self.sh_mode == 'default':
                    self.sh_mode = 'search_init'
                    self.sh_start_time = time.time()
                self.search_mode()
            else:
                if (self.sonar_front_dist < self.front_safe_dist) and (self.sonar_front_dist > 0):
                    self.ssd_throttle = 0.0
                self.psn_det_loss_cnt += 1
                
        self.info_cnt += 1
        if self.info_cnt == 10:
            print ('Run_Cor: ({:.1f},{:.1f})'.format(self.w_center, self.h_max))
            print ('Steering/Throttle: {:.1f}/{:.1f}'.format(self.ssd_angle, self.ssd_throttle))
            print ('Front Dis:', self.sonar_front_dist, '/ Rear Dis:',self.sonar_rear_dist)
            print ('People Loss Cnt: ', self.psn_det_loss_cnt)
            print (self.motion_state)
            self.info_cnt = 0
#        print ('Run_Cor: ({:.1f},{:.1f})'.format(self.x_center, self.y_center))
#        return self.frame
#        return self.frame, self.ssd_angle
        return self.frame, self.ssd_angle, self.ssd_throttle
    
    def update(self, img_arr=None, grp_x=None, max_h=None):
#        self.frame = img_arr
#        self.angle = int((str_ang - 320)/32)*0.2
#        self.x_center = psn_x
#        self.y_center = psn_y
#        print ('Update_Cor: ({:.1f},{:.1f})'.format(self.x_center, self.y_center))
#        return self.frame
        self.w_center = grp_x
        self.h_max = max_h
        if (self.x_center -320) >= 0:
            self.ssd_angle = min(int((self.w_center - 320)/32)*0.2 , 1)
        else:
            self.ssd_angle = max(-1, int((self.w_center - 320)/32)*0.2)
        
        self.cnt += 1
        if self.cnt == 5:
            print ('Update_Cor: ({:.1f},{:.1f})'.format(self.w_center, self.h_max))
            print ('Steering: {:.1f}'.format(self.ssd_angle))
            self.cnt = 0
    def run_threaded(self, img_arr=None, grp_x=None, max_h=None):
#        self.x_center = psn_x
#        self.y_center = psn_y
#        print ('Thread_Cor: ({:.1f},{:.1f})'.format(self.x_center, self.y_center))
#        return self.frame
        self.w_center = grp_x
        self.h_max = max_h
        if (self.x_center -320) >= 0:
            self.ssd_angle = min(int((self.w_center - 320)/32)*0.2 , 1)
        else:
            self.ssd_angle = max(-1, int((self.w_center - 320)/32)*0.2)
        
        self.cnt += 1
        if self.cnt == 5:
            print ('Thread_Cor: ({:.1f},{:.1f})'.format(self.w_center, self.h_max))
            print ('Steering: {:.1f}'.format(self.ssd_angle))
            self.cnt = 0
#        return self.frame