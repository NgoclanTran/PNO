# Dexter Industries
# Initial Date: June 24, 2013
# Last Updated: August 13, 2014
#
# These files have been made available online through a Creative Commons Attribution-ShareAlike 3.0  license.
# (http://creativecommons.org/licenses/by-sa/3.0/)
#
# http://www.dexterindustries.com/BrickPi
# This code is for testing the BrickPi with a Lego Motor.

from BrickPi import *   #import BrickPi.py file to use BrickPi operations
import cv2
import numpy as np


BrickPiSetup()  # setup the serial port for communication

BrickPi.MotorEnable[PORT_A] = 1 #Enable the Motor A

BrickPiSetupSensors()   #Send the properties of sensors to BrickPi

global imN
imN = 0

def takePicture():
    self.imN += 1
    filename = "image"+str(self.imN)+".jpg"
    cmd = "raspistill -o "+filename
    os.system(cmd)
    return filename

def detectColor(filename):
    
    # load the image
    image = cv2.imread(filename)

    # define the boundaries
    lower = [0, 0, 100]
    upper = [50, 56, 255]

    # create NumPy arrays from the boundaries
    lower = np.array(lower, dtype = "uint8")
    upper = np.array(upper, dtype = "uint8")
     
    # find the colors within the specified boundaries and apply
    # the mask
    mask = cv2.inRange(image, lower, upper)

    return [float(np.count_nonzero(mask))/float(np.size(mask))]

while True:
    filename = takePicture()
    result = detectColor(filename)
    if (result > 0.5)
        print 'Red color detected'
        break
    print "Running Forward"
    power = 200
    BrickPi.MotorSpeed[PORT_A] = power

    ot = time.time()
    while(time.time() - ot < 1):    #running while loop for 3 seconds
        BrickPiUpdateValues()       # Ask BrickPi to update values for sensors/motors
	time.sleep(.1)

BrickPi.MotorSpeed[PORT_A] = 0
BrickPiUpdateValues()
