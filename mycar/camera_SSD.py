import os
import numpy as np
from PIL import Image
import glob
from mvnc import mvncapi as mvnc
import cv2
import time

class BaseCamera:

    def run_threaded(self):
        return self.frame


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

                label = '{}: {:.0f}%'.format(clss, conf * 100)
                image = cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
                y = y1 - 5 if y1 - 15 > 15 else y1 + 18

                image = cv2.putText(image, label, (x1, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 1)
            self.frame = image
            #self.frame = f.array
            #cv2.imshow('frame', self.frame)
            print('FPS = {:.1f}'.format(1 / (time.time() - stime)))
            self.rawCapture.truncate(0)

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
