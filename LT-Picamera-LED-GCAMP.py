from LT.analysisclass import AnalysisClass 
import picamera
import time
import argparse
from LT.controlLED import ControlLED 

# ap = argparse.ArgumentParser()
# ap.add_argument("-ir", "--infrared", help="settings adjusted for IR video", action ="store_true")
# ap.add_argument("-l", "--long", help="record 24 hr video", action ="store_true" )
# 
# args = ap.parse_args()
# if args.infrared:
#     print("[INFO] working with IR settings...")
#     
# else:
#     print("[INFO]  working with GCaMP settings...")

input("\nRemember to delete or rename output.csv\nThen press Enter to continue...\n")

with picamera.PiCamera() as camera:
    camera.resolution = (1280,960)
    camera.framerate = 10
    camera.vflip = True
    camera.hflip = True
    camera.led = False
    camera.brightness = 51
    camera.exposure_mode = "snow"
    camera.awb_mode = "off"
    camera.awb_gains = (0.1,2.0) #red,blue
    
    output = AnalysisClass(camera)
    video = 1
    camera.start_recording(output, splitter_port=2, format='bgr')
    time1=time.time()
    for filename in camera.record_sequence(( 
        "%05d.h264" % i for i in range(1,289)), bitrate = 1000000 ):
        camera.wait_recording(300)
        print("video" + str(video))
        video += 1
    camera.stop_recording(splitter_port=2)
    x=ControlLED()
    x.GPIO_clean()
    
#         camera.stop_recording()
# fin = np.full((38,50,3),200,dtype=np.uint8)
# output.analyse(fin)      


t = time.time()-time1
if t < 60:
    print("tiempo total: " + str(t) + " seg.")
elif t >= 60 and t < 3600:
    print("tiempo total: " + str(t/60) + " min")
elif t >= 3600:
    print("tiempo total: " + str(t//3600) + " hr " + str((t%3600//60)) + " min")      
        
