#!/usr/bin/env python

# Initial Date: Oktober 22, 2014
# Last Updated: Oktober 22, 2014
# Team Ijzer 

#import ImRec.py file to use ImRec operations
from ImRec import *

import os

class Camera:
    'Camera class, representing a camera attached to the BrickPi, and including image recognition methods.'

    def __init__(self,position=0):
        self.position = position
        self.imRec = ImRec()

    def getPosition(self):
        return self.position

    def setPosition(self,position):
        self.position = position

    def detectImage(self):
        filename = "/home/pi/image.jpg"
        cmd = "raspistill -w 640 -h 480 -n -t 100 -q 10 -e jpg -th none -o "+filename
        os.system(cmd)
        # add a line of code here to send the picture to the GUI
        #return self.ImRec.detectImage(filename)
	return filename
	
   # def takePic(self):#
#	filename = self.takePicture()
#	return self.imRec.detectImage(filename)
        
        
#camera = Camera()
#camera.takePicture()
