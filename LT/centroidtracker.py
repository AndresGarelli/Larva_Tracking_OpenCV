# import the necessary packages
from scipy.spatial import distance as dist
from collections import OrderedDict
from LT.controlLED import ControlLED
import threading
import numpy as np

class CentroidTracker():
    def __init__(self, maxDisappeared=180, thresholdValue=1200):
        # initialize the next unique object ID along with two ordered
        # dictionaries used to keep track of mapping a given object
        # ID to its centroid and number of consecutive frames it has
        # been marked as "disappeared", respectively
        self.nextObjectID = 0
        self.objects = OrderedDict()
        self.disappeared = OrderedDict()
        self.speed = OrderedDict()
        self.threshold = OrderedDict()
        self.triggered = OrderedDict()
        self.AR = OrderedDict()
        self.intensidad =OrderedDict()
        self.well = OrderedDict()
        # store the number of maximum consecutive frames a given
        # object is allowed to be marked as "disappeared" until we
        # need to deregister the object from tracking
        self.maxDisappeared = maxDisappeared
        self.thresholdValue = thresholdValue
        
    def register(self, centroid, area):
        # when registering an object we use the next available object
        # ID to store the centroid
        self.objects[self.nextObjectID] = centroid
        self.disappeared[self.nextObjectID] = 0
        self.speed[self.nextObjectID] = 0
        self.threshold[self.nextObjectID] = 0
        self.triggered[self.nextObjectID]= 0
        self.AR[self.nextObjectID]= 0
        self.intensidad[self.nextObjectID]= 0
        self.well[self.nextObjectID] = area
        
        self.nextObjectID += 1
        
    def deregister(self, objectID):
        # to deregister an object ID we delete the object ID from
        # both of our respective dictionaries
        del self.objects[objectID]
        del self.disappeared[objectID]
        del self.speed[objectID]
        del self.threshold[objectID]
        del self.triggered[objectID]
        del self.intensidad[objectID]
        del self.AR[objectID]
        del self.well[objectID]
        
    def createList(self, well, objects, intensidad, AR,speed,threshold,triggered):
        list_tracking = [well, objects, intensidad, AR,speed, threshold, triggered]
        self.final = {}
        for i in list_tracking:
            for k in i:
                if not k in self.final:
                    self.final[k]=[]
                self.final[k].append(i[k])
        return self.final
    
    def trigger(self,led):
        cL = ControlLED()
        led = led
        startLED = threading.Thread(target = cL.turnONled, args=(led,))
        startLED.start()
        
    def defineWell(self,centroid,points):

        Ax, Bx, y = points
        
        if centroid[1] < y:
            if centroid[0] < Ax:
                self.area = 1
                
            elif centroid[0] > Bx:
                self.area = 3
                
            else:
                self.area = 2
                
        if centroid[1] > y:
            if centroid[0] < Ax:
                self.area = 4

            elif centroid[0] > Bx:
                self.area = 6
            
            else:
                self.area = 5
            
         
        return self.area
    
    def update(self, rects):
        # check to see if the list of input bounding box rectangles
        # is empty
        if len(rects) == 0:
            # loop over any existing tracked objects and mark them
            # as disappeared
            for objectID in list(self.disappeared.keys()):
                self.disappeared[objectID] += 1

                # if we have reached a maximum number of consecutive
                # frames where a given object has been marked as
                # missing, deregister it
                if self.disappeared[objectID] > self.maxDisappeared:
                    self.deregister(objectID)

            # return early as there are no centroids or tracking info
            # to update
            self.createList(self.well, self.objects, self.intensidad, self.AR, self.speed, self.threshold, self.triggered)
            return self.final

        # initialize an array of input centroids for the current frame
        inputCentroids = np.zeros((len(rects), 2), dtype="int")
        inputIntensidad = np.zeros((len(rects), 1), dtype="int")
        inputAR = np.zeros((len(rects), 1), dtype="float")
        # loop over the bounding box rectangles
        for (i, ((cX, cY),intensidad,AR,(x1,x2,y))) in enumerate(rects):
            # use the bounding box coordinates to derive the centroid
#             cX = int((startX + endX) / 2.0)
#             cY = int((startY + endY) / 2.0)
            inputCentroids[i] = (cX, cY)
            inputIntensidad[i] = intensidad
            inputAR[i] = AR
            points = (x1,x2,y)
        # if we are currently not tracking any objects take the input
        # centroids and register each of them
        if len(self.objects) == 0:
            for i in range(0, len(inputCentroids)):
                area1 = self.defineWell(inputCentroids[i],points)
                self.register(inputCentroids[i],area1)

        # otherwise, are are currently tracking objects so we need to
        # try to match the input centroids to existing object
        # centroids
        else:
            # grab the set of object IDs and corresponding centroids
            objectIDs = list(self.objects.keys())
            objectCentroids = list(self.objects.values())

            # compute the distance between each pair of object
            # centroids and input centroids, respectively -- our
            # goal will be to match an input centroid to an existing
            # object centroid
            D = dist.cdist(np.array(objectCentroids), inputCentroids)

            # in order to perform this matching we must (1) find the
            # smallest value in each row and then (2) sort the row
            # indexes based on their minimum values so that the row
            # with the smallest value as at the *front* of the index
            # list
            rows = D.min(axis=1).argsort()

            # next, we perform a similar process on the columns by
            # finding the smallest value in each column and then
            # sorting using the previously computed row index list
            cols = D.argmin(axis=1)[rows]

            # in order to determine if we need to update, register,
            # or deregister an object we need to keep track of which
            # of the rows and column indexes we have already examined
            usedRows = set()
            usedCols = set()

            # loop over the combination of the (row, column) index
            # tuples
            for (row, col) in zip(rows, cols):
                # if we have already examined either the row or
                # column value before, ignore it
                # val
                if row in usedRows or col in usedCols:
                    continue

                # otherwise, grab the object ID for the current row,
                # set its new centroid, and reset the disappeared
                # counter
                objectID = objectIDs[row]
                self.objects[objectID] = inputCentroids[col]
                self.disappeared[objectID] = 0
                self.speed[objectID] = D[row,col]
                self.intensidad[objectID] = inputIntensidad[col]
                self.AR[objectID] = inputAR[col]
                area2 = self.defineWell(inputCentroids[col],points)
                self.well[objectID] = area2
                if D[row,col] < 4:
                    self.threshold[objectID] += 1
                    if self.threshold[objectID] >= self.thresholdValue:
                        if self.triggered[objectID] == 0:
                            print("disparo " + str(objectID))
                            self.trigger(area2) #manda el centroide
                            self.triggered[objectID] =  1
                else:
                    self.threshold[objectID] = 0
                    
                
#                 print ("object: " + str(objectID) + " speed: " + str(D[row,col]) + " threshold: " + str(self.threshold[objectID]))
                # indicate that we have examined each of the row and
                # column indexes, respectively
                usedRows.add(row)
                usedCols.add(col)

            # compute both the row and column index we have NOT yet
            # examined
            unusedRows = set(range(0, D.shape[0])).difference(usedRows)
            unusedCols = set(range(0, D.shape[1])).difference(usedCols)

            # in the event that the number of object centroids is
            # equal or greater than the number of input centroids
            # we need to check and see if some of these objects have
            # potentially disappeared
            
            if D.shape[0] >= D.shape[1]:
                # loop over the unused row indexes
                for row in unusedRows:
                    # grab the object ID for the corresponding row
                    # index and increment the disappeared counter
                    objectID = objectIDs[row]
                    self.disappeared[objectID] += 1
                    self.speed[objectID] = 0
                    self.threshold[objectID] += 1
                    self.intensidad[objectID] = 0
                    self.AR[objectID] = 0

                    # check to see if the number of consecutive
                    # frames the object has been marked "disappeared"
                    # for warrants deregistering the object
                    if self.disappeared[objectID] > self.maxDisappeared:
                        self.deregister(objectID)

            # otherwise, if the number of input centroids is greater
            # than the number of existing object centroids we need to
            # register each new input centroid as a trackable object
            else:
                for col in unusedCols:
                    area3 = self.defineWell(inputCentroids[col],points)
                    self.register(inputCentroids[col],area3)
                    

        # return the set of trackable objects
        self.createList(self.well, self.objects, self.intensidad, self.AR, self.speed, self.threshold, self.triggered)
        return self.final