from LT.centroidtracker import CentroidTracker
import picamera.array
import cv2
import time
import imutils
import numpy as np
import pandas as pd
import os

# ct = CentroidTracker()


class AnalysisClass(picamera.array.PiRGBAnalysis):
    def __init__(self,camera):
        super(AnalysisClass, self).__init__(camera)
        self.frames = 0
        self.ct = CentroidTracker()
        grid_string = input("assign values for x1, x2 and y1 separated by comma: ")
        self.grid_list = grid_string.split(",")
        self.default = [255,495,315]
        try:
            for i in range(3):
                self.default[i] = int(self.grid_list[i])
        except ValueError:
            print("default values")
            pass
        print(self.default)
            
    def nothing(self,j):
        pass

    def analyse(self, array):
        cv2.namedWindow("Trackbars")
        cv2.namedWindow("Edges")
        cv2.createTrackbar("intensity L", "Trackbars", 14, 255, self.nothing)
        cv2.createTrackbar("intensity U", "Trackbars", 255, 255, self.nothing)
        cv2.createTrackbar("size L", "Trackbars", 234, 500, self.nothing)
        cv2.createTrackbar("size U", "Trackbars", 1800, 2000, self.nothing)
          
        cv2.createTrackbar("AR", "Trackbars", 1, 1, self.nothing)
        cv2.createTrackbar("Show values", "Trackbars", 1, 1, self.nothing)
        cv2.createTrackbar("Show mask", "Trackbars", 0, 1, self.nothing)
        cv2.createTrackbar("Gamma", "Trackbars", 30,30, self.nothing)
        cv2.createTrackbar("Top", "Edges", 0,600, self.nothing)
        cv2.createTrackbar("Bottom", "Edges", 580,600, self.nothing)
        cv2.createTrackbar("Left", "Edges", 0,800, self.nothing)
        cv2.createTrackbar("Right", "Edges", 780,800, self.nothing)
#         cv2.imshow("Live", array)

        self.frames += 1
#         print(self.frames)
        if self.frames == 10:
            array = imutils.resize(array, width=800)
            w,h,c = array.shape
            mask1 = np.zeros([w,h,1],dtype=np.uint8)
            Sx = cv2.getTrackbarPos("Left", "Edges")
            Sy = cv2.getTrackbarPos("Top", "Edges")
            Ix = cv2.getTrackbarPos("Right", "Edges")
            Iy = cv2.getTrackbarPos("Bottom", "Edges")
        
            mask1[Sy:Iy,Sx:Ix]=255
#             cv2.imshow("firulai", mask1)
            stamp = time.time()
            rects = []
#             time1 = time.time() 

            self.frames = 0
            B,G,R =cv2.split(array)
                        
            colorLower = cv2.getTrackbarPos("intensity L", "Trackbars")
            colorUpper = cv2.getTrackbarPos("intensity U", "Trackbars")   
            sizeL = cv2.getTrackbarPos("size L", "Trackbars")
            sizeU = cv2.getTrackbarPos("size U", "Trackbars")
            x1,x2,y1 = self.default
            gamma = cv2.getTrackbarPos("Gamma", "Trackbars")
            if gamma != 10:
                gamma = float(gamma)/10
                invGamma= 1.0/gamma
                table = np.array([((i / 255.0) ** invGamma) * 255 for i in np.arange(0,256)]).astype("uint8")
                Gcorr = cv2.LUT(G, table)
            else:
                Gcorr = G
#             Gcorr = cv2.equalizeHist(G)
#             clahe = cv2.createCLAHE(clipLimit=5 , tileGridSize=(3,3))
#             Gcorr = clahe.apply(G)
            cv2.line(array, (x1,0), (x1,608),(50,50,50), 1)
            cv2.line(array, (x2,0), (x2,608),(50,50,50), 1)
            cv2.line(array, (0,y1), (800,y1), (50,50,50),1)
#            cv2.circle(array, (x1, y1), 4, (255, 250, 255), -1)
#            cv2.circle(array, (x2, y1), 4, (255, 250, 255), -1)
#             gray = cv2.cvtColor(array, cv2.COLOR_BGR2GRAY)

            mask = cv2.inRange(Gcorr, colorLower, colorUpper)
            mask = cv2.erode(mask, None, iterations=2)
            mask = cv2.dilate(mask, None, iterations=2)
            mask = cv2.bitwise_and(mask,mask,mask=mask1)
        
            cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
            center = None
                
            if len(cnts) > 0:
                indice = 0
                for i in cnts:
                    sup = cv2.contourArea(i)
                    rect = cv2.minAreaRect(i)
                    (x,y), (width,height), angle =rect
                    ancho = width
                    largo = height
                    
                    if width > height:
                        (ancho, largo) = (height,width)
                        
#                         largo = width
#                         ancho = height    
                    if (sup > sizeL and sup < sizeU and largo < 150 and ancho > 4) :
                    
                        box= cv2.boxPoints(rect)
                        box = np.int0(box)
                        M = cv2.moments(i)
                        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                        
                        cv2.drawContours(array,cnts,int(indice),(255,0,255),1)
                        
                        black = np.zeros([w,h,1],dtype=np.uint8)
                        black = cv2.drawContours(black,cnts,int(indice),(255),-1)
                        intensidad = cv2.mean(G,mask=black)[0]
                        intensidad = int(intensidad*sup)
                  
                        arBar = cv2.getTrackbarPos("AR", "Trackbars")
                        AR = float(largo/ancho)
                        if arBar == 1:
                            superficie = "AREA: " + str(sup)
                            cv2.putText(array, superficie,(center[0] +10,center[1]-25), cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,70,255),1)
                            ARprint = int(AR*100)
                            ARprint = float(ARprint/100)
                            ARprint = "AR: " + str(ARprint)
                            cv2.putText(array, ARprint, (center[0] +10,center[1]-10), cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,255,255),1)
                            cv2.drawContours(array, [box],0,(0,255,255),1)
                    
                        points = (x1,x2,y1)
                        center=(center,intensidad,AR,points)
                        
                        rects.append(center)
                    indice = indice + 1
                   
            objects = self.ct.update(rects)
            
            # loop over the tracked objects
            for (objectID, variables) in objects.items():
                showBar = cv2.getTrackbarPos("Show values", "Trackbars")
                try:
                    for (well, centroid, intensidad, AR, speed, threshold, triggered) in [variables]:
                        text = "ID {}".format(objectID)
                        cv2.putText(array, text, (centroid[0] + 10, centroid[1] + 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                        
                        cv2.circle(array, (centroid[0], centroid[1]), 2, (255, 0, 255), -1)
                        speed = int(speed*10)
                        speed = float(speed/10)
                        if showBar == 1:
                            text2 = "speed: {}".format(speed)
                            cv2.putText(array, text2, (centroid[0] + 10, centroid[1] + 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                            text3 = "thr: {}".format(threshold)
                            cv2.putText(array, text3, (centroid[0] + 10, centroid[1] + 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                            intTotal = "Int: {}".format(str(intensidad)[1:-1])
                            cv2.putText(array, intTotal,(centroid[0] + 10, centroid[1]-45),
                            cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,70,255),1)
                        
                except ValueError:
                    print("value error")
   
            for objectID in list(objects.keys()):
                objects[objectID].append(stamp)
#             
            df = pd.DataFrame.from_dict(objects)
            df = df.T
            
            if not os.path.isfile("output.csv"):
                df.to_csv("output.csv")
            else:
                df.to_csv("output.csv",mode="a", header=False)
                    
                # draw both the ID of the object and the centroid of the
                # object on the output frame
               
            
#             result = cv2.bitwise_and(array,array,mask=mask)
    #             array = cv2.bitwise_and(array,array,mask=mask)
#             final = cv2.hconcat([array,result])
            showMask = cv2.getTrackbarPos("Show mask", "Trackbars")
            if showMask == 1: 
                result = cv2.bitwise_and(array,array,mask=mask)
                cv2.imshow("Mask", result)
                cv2.imshow("Gcorr", Gcorr)
            else:
                cv2.destroyWindow("Mask")
                cv2.destroyWindow("Gcorr")
    
            array = cv2.bitwise_and(array,array,mask=mask1)
            cv2.imshow("Frame2",array)
#             cv2.imshow("G",G)
#             cv2.imshow("Gcorr",Gcorr)
#             cv2.imshow("B",B)
        
    #             mask = cv2.bitwise_and(mask,mask,mask=mask)
    #             cv2.imshow("F",final)

        cv2.waitKey(1) & 0xFF
           
#             cv2.destroyAllWindows()
