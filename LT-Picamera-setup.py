from LT.analysisclass import AnalysisClass
import picamera
import picamera.array
import time
import argparse
from LT.controlLED import ControlLED 
import cv2
import os

def nothing(x):
    pass
    
print("Set grid with sliders and press Enter")
name = "Press Enter when values are set"
cv2.namedWindow(name)
cv2.createTrackbar("x1", name, 255,800,nothing)
cv2.createTrackbar("x2", name, 485,800,nothing)
cv2.createTrackbar("y", name, 315,600,nothing)
        
camera = picamera.PiCamera()
camera.resolution = (800,608)
camera.vflip = True
camera.hflip = True
camera.framerate = 10
rawCapture = picamera.array.PiRGBArray(camera, size=(800,608))
time.sleep(0.1)


for cuadro in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    frame = cuadro.array
    
    x1 = cv2.getTrackbarPos("x1", name)
    x2 = cv2.getTrackbarPos("x2", name)
    y1 = cv2.getTrackbarPos("y", name)    
    cv2.line(frame, (x1,0), (x1,608),(50,50,50), 1)
    cv2.line(frame, (x2,0), (x2,608),(50,50,50), 1)
    cv2.line(frame, (0,y1), (800,y1), (50,50,50),1)
    cv2.imshow(name, frame)
    key = cv2.waitKey(1) & 0xFF
    rawCapture.truncate(0)
    if key == 13:
        break
camera.close()
cv2.destroyWindow(name)

a=(x1,x2,y1)

print("valores x1, x2, y1: " + str(a)[1:-1] )
