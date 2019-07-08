import os
import numpy as np
from PIL import Image
import glob
from mvnc import mvncapi as mvnc
import cv2
import time



class BaseCamera:

    def run_threaded(self):
#        print('camera thread')
#        return self.frame
#         return self.frame, self.w_center, self.h_center
        return self.frame, self.grp_w_center, self.psn_max_height, self.psn_detected_flag


class PiCamera(BaseCamera):
    def __init__(self, resolution=(480, 640), framerate=20):
        from picamera.array import PiRGBArray
        from picamera import PiCamera
        resolution = (resolution[1], resolution[0])
        # initialize the camera and stream
        self.camera = PiCamera()  # PiCamera gets resolution (height, width)
        self.camera.resolution = resolution
        self.height, self.width = (resolution[1], resolution[0])
        self.camera.framerate = framerate
        self.rawCapture = PiRGBArray(self.camera, size=resolution)
        self.stream = self.camera.capture_continuous(self.rawCapture,
                                                     format="rgb",
                                                     use_video_port=True)

        #Initialize and import MobileNet SSD graph and activate NCS device
        self.GRAPH = 'graph/graph'
        self.CLASSES = ('background',
                   'aeroplane', 'bicycle', 'bird', 'boat',
                   'bottle', 'bus', 'car', 'cat', 'chair',
                   'cow', 'diningtable', 'dog', 'horse',
                   'motorbike', 'person', 'pottedplant',
                   'sheep', 'sofa', 'train', 'tvmonitor')
        self.input_size = (300, 300)
        np.random.seed(3)
        self.colors = 255 * np.random.rand(len(self.CLASSES), 3)
        self.w_center = 0.0
        self.h_center = 0.0
        self.grp_w_center = 0.0
        self.grp_h_center = 0.0
        self.psn_width = 0
        self.psn_height = 0
        self.psn_max_height = 0
        self.psn_cnt_right = 0
        self.psn_cnt_left = 0
        self.right_w_sum = 0.0
        self.left_w_sum = 0.0
        self.psn_detected_flag = False

        # discover our device
        devices = mvnc.enumerate_devices()
        device = mvnc.Device(devices[0])
        device.open()

        # load graph onto device
        with open(self.GRAPH, 'rb') as f:
            graph_file = f.read()

        self.graph = mvnc.Graph('graph1')
        # graph.allocate(device, graph_file)
        self.input_fifo, self.output_fifo = self.graph.allocate_with_fifos(device, graph_file)



        # initialize the frame and the variable used to indicate
        # if the thread should be stopped
        self.frame = None
        self.on = True

        print('PiCamera loaded.. .warming camera')
        time.sleep(2)

    # image preprocessing
    # def preprocess(self):
    #     img = cv2.resize(self, self.input_size)
    #     img = img - 127.5
    #     img = img / 127.5
    #     return img.astype(np.float32)

    def run(self):
        f = next(self.stream)
        frame = f.array
        self.rawCapture.truncate(0)
        return frame

    def update(self):
        
        # keep looping infinitely until the thread is stopped
        for f in self.stream:
            # grab the frame from the stream and clear the stream in
            # preparation for the next frame
            stime = time.time()
            image = f.array
            image_pro = cv2.resize(image, self.input_size)
            image_pro = image_pro - 127.5
            image_pro = image_pro / 127.5
            image_pro = image_pro.astype(np.float32)

            self.graph.queue_inference_with_fifo_elem(self.input_fifo, self.output_fifo, image_pro, None)
            output, _ = self.output_fifo.read_elem()

            valid_boxes = int(output[0])

            self.psn_cnt_right = 0
            self.psn_cnt_left = 0
            self.right_w_sum = 0
            self.left_w_sum = 0
            self.right_h_sum = 0
            self.left_h_sum = 0
            self.psn_max_height = 0
            x1_left_min, y1_left_min, x2_left_max, y2_left_max = (0, 0, 0, 0)
            x1_right_min, y1_right_min, x2_right_max, y2_right_max = (0, 0, 0, 0)
            right_w_center = 0
            left_w_center = 0

            for i in range(7, 7 * (1 + valid_boxes), 7):
                if not np.isfinite(sum(output[i + 1: i + 7])):
                    continue
                clss = self.CLASSES[int(output[i + 1])]
                conf = output[i + 2]
                color = self.colors[int(output[i + 1])]

                x1 = max(0, int(output[i + 3] * self.width))
                y1 = max(0, int(output[i + 4] * self.height))
                x2 = min(self.width, int(output[i + 5] * self.width))
                y2 = min(self.height, int(output[i + 6] * self.height))
                
                if clss == 'person':
                    self.psn_detected_flag = True
                    self.w_center = (x1 + x2)/2
                    self.h_center = (y1 + y2)/2
                    self.psn_width = (x2-x1)
                    self.psn_height = (y2-y1)
                    if self.psn_height > self.psn_max_height:
                        self.psn_max_height = self.psn_height
                    
                    #check left/right side people number and calculate avg width center
                    if self.w_center > 320:
                        self.psn_cnt_right += 1
                        self.right_w_sum += self.w_center
                        self.right_h_sum += self.h_center
                        if ((x1 > 320) and (x1_right_min > x1)) or (x1_right_min == 0):
                            x1_right_min = x1
                        if (y1_right_min > y1) or (y1_right_min == 0):
                            y1_right_min = y1
                        if x2_right_max < x2:
                            x2_right_max = x2
                        if y2_right_max < y2:
                            y2_right_max = y2
                    elif self.w_center < 320:
                        self.psn_cnt_left += 1
                        self.left_w_sum += self.w_center
                        self.left_h_sum += self.h_center
                        if (x1_left_min > x1) or (x1_left_min == 0):
                            x1_left_min = x1
                        if (y1_left_min > y1) or (y1_left_min == 0):
                            y1_left_min = y1
                        if x2_left_max < x2:
                            x2_left_max = x2
                        if y2_left_max < y2:
                            y2_left_max = y2
                        
                    #check which side should go by checking person count.
                    if self.psn_cnt_right != 0:    
                        right_w_center = self.right_w_sum / self.psn_cnt_right
                        right_h_center = self.right_h_sum / self.psn_cnt_right
                    if self.psn_cnt_left != 0:    
                        left_w_center = self.left_w_sum / self.psn_cnt_left
                        left_h_center = self.left_h_sum / self.psn_cnt_left
                    
                    if self.psn_cnt_right > self.psn_cnt_left:
                        self.grp_w_center = right_w_center
                        self.grp_h_center = right_h_center                        
                        label_right = 'Grp_Cen: {:.0f}'.format(self.grp_w_center)
                        image = cv2.rectangle(image, (x1_right_min, y1_right_min), (x2_right_max, y2_right_max), color, 2)
                        image = cv2.putText(image, label_right, ((int(self.grp_w_center)-50), int(self.grp_h_center)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 1)
                    elif self.psn_cnt_right < self.psn_cnt_left:
                        self.grp_w_center = left_w_center
                        self.grp_h_center = left_h_center
                        label_left = 'Grp_Cen: {:.0f}'.format(self.grp_w_center)
                        image = cv2.rectangle(image, (x1_left_min, y1_left_min), (x2_left_max, y2_left_max), color, 2)
                        image = cv2.putText(image, label_left, ((int(self.grp_w_center)-50), int(self.grp_h_center)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 1)
                    else:
                        if abs(right_w_center - 320) <= abs(left_w_center - 320):
                            self.grp_w_center = right_w_center
                        else:
                            self.grp_w_center = left_w_center
                    label = '{}: {:.0f}%'.format(clss, conf * 100)
                    image = cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
                    y = y1 - 5 if y1 - 15 > 15 else y1 + 18
                    image = cv2.putText(image, label, (x1, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 1)
                else:
                    self.psn_detected_flag = False
                    self.grp_w_center = self.width/2

                    
                # label = '{}: ({:.0f},{:.0f})'.format(clss, self.w_center, self.h_center)
                
#                label = '{}: {:.0f}%'.format(clss, conf * 100)
#                image = cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
#                image = cv2.rectangle(image, (x1_min, y1_min), (x2_max, y2_max), color, 2)
#                y = y1 - 5 if y1 - 15 > 15 else y1 + 18
#                image = cv2.putText(image, label, (x1, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 1)
                
            self.frame = image
            
            #self.frame = f.array
            #cv2.imshow('frame', self.frame)
            print('FPS = {:.1f}'.format(1 / (time.time() - stime)))
#            print('({:.1f},{:.1f})/({:.1f},{:.1f})'.format(x1, y1, x2, y2))
#            print('({:.1f},{:.1f})'.format(self.grp_w_center, self.psn_max_height))
#            print('({:.1f},{:.1f})'.format(self.x_center, self.y_center))
            self.rawCapture.truncate(0)
#            return self.x_center, self.y_center

            # if the thread indicator variable is set, stop the thread
            if not self.on:
                break

    def shutdown(self):
        # indicate that the thread should be stopped
        self.on = False
        print('stopping PiCamera')
        time.sleep(.5)
        self.stream.close()
        self.rawCapture.close()
        self.camera.close()
