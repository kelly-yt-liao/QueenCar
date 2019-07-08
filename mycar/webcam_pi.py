#!/usr/bin/env python
# coding: utf-8

from picamera.array import PiRGBArray
from picamera import PiCamera
from mvnc import mvncapi as mvnc
import numpy as np
import cv2
import time

GRAPH = 'graph/graph'
IMAGE = 'images/000542.jpg'
CLASSES = ('background',
           'aeroplane', 'bicycle', 'bird', 'boat',
           'bottle', 'bus', 'car', 'cat', 'chair',
           'cow', 'diningtable', 'dog', 'horse',
           'motorbike', 'person', 'pottedplant',
           'sheep', 'sofa', 'train', 'tvmonitor')
#input_size = (300, 300)
input_size = (300, 300)
np.random.seed(3)
colors = 255 * np.random.rand(len(CLASSES), 3)


#discover our device
devices = mvnc.enumerate_devices()
device  = mvnc.Device(devices[0])
device.open()

#load graph onto device
with open(GRAPH, 'rb') as f:
    graph_file = f.read()

graph = mvnc.Graph('graph1')
#graph.allocate(device, graph_file)
input_fifo, output_fifo = graph.allocate_with_fifos(device, graph_file)

#image preprocessing
def preprocess(src):
    img = cv2.resize(src, input_size)
    img = img - 127.5
    img = img / 127.5
    return img.astype(np.float32)

#video image capture
#capture = cv2.VideoCapture(0)
#print (capture.isOpened())
#_, image = capture.read()
#height, width = image.shape[:2]

camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 20
rawCapture = PiRGBArray(camera, size=(640,480))
height, width = (480, 640)

time.sleep(2)

#while True:
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):    
    stime = time.time()
    #_, image = capture.read()
    image = frame.array
    image_pro = preprocess(image)
    graph.queue_inference_with_fifo_elem(input_fifo, output_fifo, image_pro, None)
    output, _ = output_fifo.read_elem()

    valid_boxes = int(output[0])

    for i in range(7, 7 * (1 + valid_boxes), 7):
        if not np.isfinite(sum(output[i + 1: i + 7])):
            continue
        clss = CLASSES[int(output[i + 1])]
        conf = output[i + 2]
        color = colors[int(output[i + 1])]

        x1 = max(0, int(output[i + 3] * width))
        y1 = max(0, int(output[i + 4] * height))
        x2 = min(width, int(output[i + 5] * width))
        y2 = min(height, int(output[i + 6] * height))

        label = '{}: {:.0f}%'.format(clss, conf * 100)
        image = cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
        y = y1 -5 if y1 - 15 > 15 else y1 + 18

        image = cv2.putText(image, label, (x1, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
    cv2.imshow('frame', image)
    print('FPS = {:.1f}'.format(1 / (time.time() - stime)))
    
    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.close()
cv2.destroyAllWindows()
device.close()
