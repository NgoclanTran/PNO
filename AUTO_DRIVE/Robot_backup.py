#!/usr/bin/env python

# Initial Date: Oktober 13, 2014
# Last Updated: March 17, 2015

'''
This is a file containing the class Robot and some of its additional helper classes.
The robot respresents a real-world Brick Pi driven autonomously driving robot.
'''

# Import BrickPi.py file to use BrickPi operations
from BrickPi import *

# Import RPi.GPIO module to access GPIO pins
import RPi.GPIO as GPIO

# Import all necessary classes
import os
import time
import numpy as np
from Camera import *
from World import *
#import math
from httpclient import *

# Some globals used for communication with a GUI
global stopp
stopp = 0
global newImRec
newImRec = 0
global resultImRec
global imageSending
imageSending = 0
global mapSending
mapSending = 0

class Sensor:
    'Sensor class, representing a sensor attached to one of the BrickPi ports.'

    def __init__(self,port=PORT_1):
        self.port = port

    def getPort(self):
        return self.port

    def getValue(self):
        return BrickPi.Sensor[self.port]

class Motor:
    'Motor class, representing a motor attached to one of the BrickPi ports.'

    def __init__(self,port=PORT_A):
        self.port = port
        self.setPower(0)

    def getPort(self):
        return self.port

    def getPosition(self):
        encoderValue = int(BrickPi.Encoder[self.getPort()])
        result = (encoderValue % 720)/2.0
        return result
    
    def getPower(self):
        return self.power

    def setPower(self,power):
        self.power = power
        BrickPi.MotorSpeed[self.port] = self.power

    def moveTo(self,degrees):
        motorRotateDegree([30],[degrees],[self.getPort()])
            
    def getAverageSpeed(self,currentTime,currentPosition,previousTime,previousPosition):
        return float(currentPosition - previousPosition) / float(currentTime - previousTime)
        
class Robot:
    'A class of Robot vehicles that autonomously find their way towards a goal.'

    global ECHO_GPIO 
    ECHO_GPIO = 17
    global TRIG_GPIO 
    TRIG_GPIO = 4
    global TRIG_DURATION                # Trigger duration
    TRIG_DURATION = 0.0001
    global INTTIMEOUT                   # Timeout on echo signal
    INTTIMEOUT = 2100
    global V_SND                        # Speed of sound in m/s
    V_SND = 340.29
    global turnCameraValueLeft          # ower to turn the camera left
    turnCameraValueLeft = -83 
    global turnCameraValueRight         # power to turn the camera right
    turnCameraValueRight = 90
    global motorLeftPower               # power on the left motor (forward)
    motorLeftPower = -255
    global motorRightPower              # power on the right motor (forward)
    motorRightPower = -245
    global motorLeftPowerBackward       # power on the left motor (backward)
    motorLeftPowerBackward = 255
    global motorRightPowerBackward      # power on the right motor (backward)
    motorRightPowerBackward = 255
    global medianNumber                 # number of value to calculate median
    medianNumber = 30
    global adjustLeftLeftMotor          # power to adjust to the leftside with left motor
    adjustLeftLeftMotor = 0
    global adjustLeftRightMotor         # power to adjust to the leftside with right motor
    adjustLeftRightMotor = -120
    global adjustRightLeftMotor         # power to adjust to the rightside with the left motor
    adjustRightLeftMotor = -120
    global adjustRightRightMotor        # power to adjust to the rightside with the right motor
    adjustRightRightMotor = 0
    global leftDistanceBoundaryMin      # Minimum distance for the left boundary in adjust(strook)
    leftDistanceBoundaryMin = 26
    global leftDistanceBoundaryMax      # Maximum distance for the left boundary in adjust(strook)
    leftDistanceBoundaryMax = 28
    global distanceToCornerTurn         # Distance needed from sensors to put the pi into cornerturn
    distanceToCornerTurn = 80
    global rightDistanceBoundaryMin     # Minimum distance for the right boundary in adjust(strook)
    rightDistanceBoundaryMin = 26
    global rightDistanceBoundaryMax     # Maximum distance for the right boundary in adjust(strook)
    rightDistanceBoundaryMax = 30
    global distanceOneStepForward       # Distance that the pi covers in the 0.5s steps of moving forward
    distanceOneStepForward = 15
    global degFor90deg                  # Degrees needed for an orthogonal turn
    degFor90deg = 425
    global outlierDst                   # Outliers are outlierDst away from the median
    outlierDst = 5
    global wheel
    wheel = 19.0
    global rotationCst                  # Number of wheel rotations needed for 24 cm forward
    rotationCst = 24.0/wheel
    global adjust                       # Number of times to adjust when tracking a wall
    adjust = 2
    global adjustFactor
    adjustFactor = 10.0
    global adjustDistance
    adjustDistance = 0.22*degFor90deg
    global rightDistanceBoundaryClose
    rightDistanceBoundaryClose = 15
    global leftDistanceBoundaryClose
    leftDistanceBoundaryClose = 15
    global leftSensorCorr
    leftSensorCorr = 10
    global distanceOneTile
    distanceOneTile = 65

    global image

    def __init__(self, connection=None,ip = None, port = None, wall=None, cameraPosition=0, orientation=None, position=tuple(), path=list(), state = ''):
       	global mapSending
	print "init robot"
        
	self.connection = connection
        self.client = Client(ip,port)
        self.wall = wall
        self.camera = Camera(cameraPosition)
        self.orientation = orientation
        self.position = position
        self.path = path
        self.state = state
	
	if self.connection:
            	self.connection.sendMessage("-- Robot connected")
	self.sendPositions()

 	# Set the world
	self.client.getWorld()
        self.world = World("kaart.txt")

        # Set the sensors used
        self.SENSOR_ULTRASONIC = Sensor(PORT_1)
        self.SENSOR_TOUCH = Sensor(PORT_4)
        self.SENSOR_TOUCH2 = Sensor(PORT_2)

        # Set the motors used
        self.MOTOR_LEFT = Motor(PORT_A)
        self.MOTOR_RIGHT = Motor(PORT_C)
        self.MOTOR_ROOF = Motor(PORT_D)

        # Overall setup
        self.setupBrickPi()
        self.setupRoofMotor()
        self.setupGPIO()

        print "init robot finished"



    def setupRoofMotor(self):

        BrickPi.MotorEnable[self.MOTOR_ROOF.getPort()]=1
        BrickPiSetupSensors()

    def setupBrickPi(self):

        BrickPiSetup()  # setup the serial port for communication
        
        BrickPi.SensorType[self.SENSOR_ULTRASONIC.getPort()] = TYPE_SENSOR_ULTRASONIC_CONT    #Set the type of sensor
        BrickPi.SensorType[self.SENSOR_TOUCH.getPort()] = TYPE_SENSOR_TOUCH                   #Set the type of sensor
        BrickPi.SensorType[self.SENSOR_TOUCH2.getPort()] = TYPE_SENSOR_TOUCH

        BrickPi.MotorEnable[self.MOTOR_LEFT.getPort()] = 1                                    #Enable the Left Motor
        BrickPi.MotorEnable[self.MOTOR_RIGHT.getPort()] = 1                                   #Enable the Right Motor

        BrickPiSetupSensors()                                                                 #Send the properties of sensors to BrickPi

    def setupGPIO(self):

        GPIO.cleanup()
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(ECHO_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(TRIG_GPIO, GPIO.OUT)
        GPIO.output(TRIG_GPIO, False)

        # Wait for 2 seconds for the ultrasonics to settle
        time.sleep(2)
        
    def turnCameraFront(self):
        if self.connection:
            self.connection.sendMessage('-- turning camera front')
        self.turnCamera(0)
        self.camera.setPosition(0)
        
    def turnCameraLeft(self):
        if self.connection:
            self.connection.sendMessage('-- turning camera left')
        self.turnCamera(turnCameraValueLeft)
        self.camera.setPosition(turnCameraValueLeft)
        
    def turnCameraRight(self):
        if self.connection:
            self.connection.sendMessage('-- turning camera right ')
        self.turnCamera(turnCameraValueRight)
        self.camera.setPosition(turnCameraValueRight)

    def turnCameraLeftSwing(self):
        #if self.connection:
        #    self.connection.sendMessage('-- turning camera left swing')
        self.turnCamera(-20)
        self.camera.setPosition(-20)
        
    def turnCameraRightSwing(self):
        #if self.connection:
        #    self.connection.sendMessage('-- turning camera right swing')
        self.turnCamera(20)
        self.camera.setPosition(20)

    def turnCamera(self,newCameraPosition):
        cameraPosition = self.camera.getPosition()
        degrees = newCameraPosition - cameraPosition
        self.MOTOR_ROOF.moveTo(degrees)

    def adaptCameraPosition(self,pictureOrientation):
        
        orientations = ['N','E','S','W']
        indexOld = orientations.index(self.orientation)
        indexNew = orientations.index(pictureOrientation)
        deltaOrientation = indexNew - indexOld

        if abs(deltaOrientation) == 2:
            print "Error in adaptCameraPosition: the camera should turn to the back."
        
        if deltaOrientation == 3:
            deltaOrientation = -1

        if deltaOrientation == -3:
            deltaOrientation = 1
            
        if deltaOrientation == 3 or deltaOrientation == -1:
            self.turnCameraLeft()
            
        elif deltaOrientation == -3 or deltaOrientation == 1:
            self.turnCameraRight()
            
        else:
            self.turnCameraFront()

    def turnLeft(self,adjust = True):
        if self.connection:
            self.connection.sendMessage( '-- turning left ')
	if (adjust and (self.state == 'T') ):
	    if self.wall == 'left':
		self.alignLeft(self.checkDistanceLeft())
	    elif self.wall == 'right':
		self.alignRight(self.checkDistanceRight())


        motorRotateDegree([220],[degFor90deg],[self.MOTOR_RIGHT.getPort()])
        self.pauseMotors()                          

    def turnRight(self,adjust = True):
        if self.connection:
            self.connection.sendMessage('-- turning right ')
	if (adjust and (self.state == 'T') ):
	    if self.wall == 'left':
		self.alignLeft(self.checkDistanceLeft())
	    elif self.wall == 'right':
		self.alignRight(self.checkDistanceRight())

        motorRotateDegree([190],[degFor90deg],[self.MOTOR_LEFT.getPort()])
        self.pauseMotors()                           
        
    def turn(self):
        # This function makes the robot turn
        
        #if self.connection:
        #    self.connection.sendMessage('-- turning ')        

        if (self.wall == 'left'):
            self.turnRight()
            self.turnCameraLeft()
        else:
            if (self.wall == None):
                self.wall = 'right'
            self.turnLeft()
            self.turnCameraRight()


    def cornerTurn(self):
        # This function makes the robot turn when there's no longer a wall to track
        
        if self.connection:
            self.connection.sendMessage('-- turning around the corner ')

        self.continueDrivingForward(1*rotationCst)

        if (self.wall == "left"):
            self.turnLeft()
        elif (self.wall == "right"):
            self.turnRight()
        else:
            return

        self.continueDrivingForward(1*rotationCst)

    def pauseMotors(self):
	#if self.connection:
        #    self.connection.sendMessage('-- pause motors ')


        self.setupBrickPi()
        self.MOTOR_LEFT.setPower(0)
        self.MOTOR_RIGHT.setPower(0)
        
        BrickPiUpdateValues()
	
    def continueDrivingForward(self,c):
        # This function makes the robot drive c x one rotation of its wheels (= c x 19 cm) forward
        
        #if self.connection:
        #    self.connection.sendMessage('-- driving forward ' + str(c*18.0) + 'cm')

        deg = c*360
        
        # Important: driving forward corresponds with a positive number of degrees!
        motorRotateDegree([motorLeftPower,motorRightPower],[deg,deg],[self.MOTOR_LEFT.getPort(),self.MOTOR_RIGHT.getPort()])
        self.pauseMotors()
 
            
    def continueDrivingBack(self,c):
         # This function makes the robot drive c x one rotation of its wheels (= c x 19 cm) forward
        
        #if self.connection:
        #    self.connection.sendMessage('-- driving backward '+ str(c*18.0) + 'cm')

        deg = c*360
        
        motorRotateDegree([motorLeftPowerBackward, motorRightPowerBackward],[-deg,-deg],[self.MOTOR_LEFT.getPort(),self.MOTOR_RIGHT.getPort()])
        self.pauseMotors()
                
    def checkTouchSensor(self):
        result = BrickPiUpdateValues()      # Ask BrickPi to update values for sensors/motors 
        if not result:
            return (self.SENSOR_TOUCH.getValue() or self.SENSOR_TOUCH2.getValue())
        else:
            return self.checkTouchSensor()

    def reject_outliers(self,data):
        # Reject sensor values that are more than outlierDst away from the overall median
        return data[abs(data - np.median(data)) < outlierDst]

    def checkDistanceLeft(self):
        dist = []
        i = 0
        while i < medianNumber:
            result = BrickPiUpdateValues()  # Ask BrickPi to update values for sensors/motors 
            if not result :
                dist.append(self.SENSOR_ULTRASONIC.getValue()) # BrickPi.Sensor[PORT] stores the value obtained from sensor
                i += 1
            time.sleep(.02) # sleep for 20 ms


        a = np.array(dist)
        a = self.reject_outliers(a)
        result = np.mean(a)
        
        print 'distanceLeft:', result
        if self.connection:
            self.connection.sendMessage('distance left: '+str(result))
        return result

    def checkDistanceRight(self):
        dist = []
        i = 0
        while i < medianNumber:
            
            # Trigger trig_gpio for trig_duration
            GPIO.output( TRIG_GPIO, True )
            time.sleep( TRIG_DURATION )
            GPIO.output( TRIG_GPIO, False )

            # Wait for the echo signal (or timeout)
            countdown_high = INTTIMEOUT
            while ( GPIO.input( ECHO_GPIO ) == 0 and countdown_high > 0 ):
                countdown_high -= 1

            # If we've gotten a signal
            if countdown_high > 0:
                echo_start = time.time()

                countdown_low = INTTIMEOUT
                while( GPIO.input( ECHO_GPIO ) == 1 and countdown_low > 0 ):
                    countdown_low -= 1
                echo_end = time.time()

                echo_duration = echo_end - echo_start
            
            # Display the distance, unless there was a timeout on 
            # the echo signal
            if countdown_high > 0 and countdown_low > 0:
                # echo_duration is in seconds, so multiply by speed
                # of sound.  Divide by 2 because of rounttrip and 
                # multiply by 100 to get cm instead of m.
                distance = echo_duration * V_SND * 100 / 2
                dist.append(distance)
                i += 1
                
        a = np.array(dist)
        a = self.reject_outliers(a)
        result = np.mean(a)

	# Handle nan's
	if np.isnan(result):
	    result = self.checkDistanceRight()        

        print 'distanceRight:', result
        
        if self.connection:
            self.connection.sendMessage('distance right: '+str(result))
        return result
        
    def adjustLeft(self,t=1): 
        # This method makes the robot turn a little using its left wheel.
        # Make sure that t > 0 in case you want a forward adaption!

	#if self.connection:
        #    self.connection.sendMessage('-- adjust left ')

        
        motorRotateDegree([adjustRightLeftMotor],[adjustFactor*t],[self.MOTOR_LEFT.getPort()])
        self.pauseMotors()

    def adjustRight(self,t=1): # make the robot turn a little with his right wheel
        # This method makes the robot turn a little using its right wheel.
        # Make sure that t > 0 in case you want a forward adaption!        
        
	#if self.connection:
        #    self.connection.sendMessage('-- adjust right ')

        print "Reporting: adjustRight"
        motorRotateDegree([adjustLeftRightMotor],[adjustFactor*t],[self.MOTOR_RIGHT.getPort()])
        self.pauseMotors()

    def alignLeft(self,minDistance):

        if self.connection:
            self.connection.sendMessage('-- aligning left')

        self.wall = 'left'
        
        self.adjustLeft(1)
        adjusting = 'Right'
        
        while True:
            
            distance = self.checkDistanceLeft()
	    if (distance < minDistance) and (adjusting == 'Right'):
                # Turning back with the same wheel (not driving forward)
                self.adjustLeft(1)
                minDistance = distance		
            elif (distance > minDistance) and (adjusting == 'Right'):
                adjusting ='Left'
                self.adjustLeft(-1)
                minDistance = distance
            elif (distance <= minDistance) and (adjusting == 'Left'):
                self.adjustLeft(-1)
                minDistance = distance
            else:
		self.adjustLeft(1)
                break

    def alignRight(self,minDistance):

        if self.connection:
            self.connection.sendMessage('-- aligning right')

        self.wall = 'right'

        self.adjustRight(1)
        adjusting = 'Left'

        while True:
            distance = self.checkDistanceRight()
	    distance = np.rint(distance)
	    print "Distance: " + str(distance)
	    if (distance < minDistance) and (adjusting == 'Left'):
                self.adjustRight(1)
                minDistance = distance
            elif (distance > minDistance) and (adjusting == 'Left'):
                minDistance = distance
                self.adjustRight(-1)
                adjusting = 'Right'
            elif (distance <= minDistance) and (adjusting == 'Right'):
                self.adjustRight(-1)
                minDistance = distance
            else:
                # since we've gone one too far
		self.adjustRight(1)
                break

    def determineAdjust(self,distanceToWall,distanceFromLastPosition):
        # Determines the amount of adjust needed when a difference in distance
        # of distanceToWall cm is registered when traversed distanceFromLastPosition cm


	#if self.connection:
        #    self.connection.sendMessage('-- calculating dynamic adjust ')
            
        if (distanceToWall == 0):
	    return 1.0

	print str(distanceToWall)
	print str(distanceFromLastPosition)
        result =  (degFor90deg/(np.pi/2))*np.arctan(distanceToWall/distanceFromLastPosition)/(adjustFactor*1.5)
	print "determine adjust: "+ str(result)
	if (np.floor(result) == 0.0):
	    result = 1.0
	print "determine adjust: " + str(result)
	return min(result,8)

    def trackLeft(self):

	if (not self.continueExecuting()):
            return

        if self.connection:
            self.connection.sendMessage('-- Roaming: tracking left wall')
        distance = 0

        while True:
            
            collision = self.checkTouchSensor()
            if collision:
                self.continueDrivingBack(rotationCst)
                self.turn()
                return 0

            if self.detectImage():
                return 1

            distanceLeft = self.checkDistanceLeft()
            
	    if (distanceLeft < leftDistanceBoundaryClose):
		self.adjustLeft(5)
            elif (distanceLeft < leftDistanceBoundaryMin and ((distanceLeft <= distance) or (distance == 0))):
                if (distance == 0):
                    adjust = 1
                else:
                    adjust = self.determineAdjust(distance-distanceLeft,0.5*wheel*rotationCst)
                self.adjustLeft(adjust)
                self.continueDrivingForward(0.5*rotationCst)
                distance = distanceLeft
		
            elif (distanceLeft > leftDistanceBoundaryMax and distanceLeft < distanceToCornerTurn and distanceLeft >= distance):
                if (distance == 0):
                    adjust = 1
                else:
                    adjust = self.determineAdjust(distanceLeft-distance,0.5*wheel*rotationCst)                
                self.adjustRight(adjust)
                self.continueDrivingForward(0.5*rotationCst)
                distance = distanceLeft

            elif (distanceLeft >= distanceToCornerTurn):
                self.cornerTurn()
                self.wall = None

                return 0
	    
            else:

                self.continueDrivingForward(0.5*rotationCst)

    def trackRight(self):

	if (not self.continueExecuting()):
            return

        if self.connection:
            self.connection.sendMessage('-- Roaming: tracking right wall')

        distance = 0

        while True:


            collision = self.checkTouchSensor()
            if collision:
                self.continueDrivingBack(rotationCst)
                self.turn()
                return 0

            if self.detectImage():
                return 1

            distanceRight = self.checkDistanceRight()

	    if (distanceRight < rightDistanceBoundaryClose):
		self.adjustRight(5)

            elif (distanceRight < rightDistanceBoundaryMin) and ((distanceRight <= distance) or (distance == 0)): # voor de hindernis met de versmalling
                if (distance == 0):
                    adjust = 1
                else:
                    adjust = self.determineAdjust(distance-distanceRight,0.5*wheel*rotationCst)
                self.adjustRight(adjust)
                self.continueDrivingForward(0.5*rotationCst)
                distance = distanceRight
	
		
            elif (distanceRight > rightDistanceBoundaryMax and distanceRight < distanceToCornerTurn and distanceRight >= distance):
                if (distance == 0):
                    adjust = 1
                else:
                    adjust = self.determineAdjust(distanceRight-distance,0.5*wheel*rotationCst)                
                self.adjustLeft(adjust)
                self.continueDrivingForward(0.5*rotationCst)
                distance = distanceRight

            elif (distanceRight >= distanceToCornerTurn):
                self.cornerTurn()
                self.wall = None

                return 0

            else: # als die nie in de vorige gaat , rijdt hij gewoon rechtdoor, dit doet hij dus ook als het verschil plots te groot wordt (de inkeping)

                self.continueDrivingForward(0.5*rotationCst)

    def trackOneStep(self):

	if (not self.continueExecuting()):
            return


        side = self.wall


        collision = self.checkTouchSensor()
        if collision:
            self.continueDrivingBack(rotationCst)
            return 0
        
        elif (side == "left"):
            
            if self.connection:
                self.connection.sendMessage('-- Traveling: tracking left wall one step')

            distanceLeftOne = self.checkDistanceLeft()
            self.continueDrivingForward(0.5*rotationCst)
            distanceLeftTwo = self.checkDistanceLeft()

            (distanceLeftOne , distanceLeftTwo) = self.checkDistances(distanceLeftOne,distanceLeftTwo)

            delta = (distanceLeftOne - distanceLeftTwo)
            
            print "delta", delta
            
	    if (distanceLeftTwo<leftDistanceBoundaryMin) and (delta>0):
		self.adjustLeft(2)
	    elif (distanceLeftTwo>leftDistanceBoundaryMax) and (delta<0):
	        self.adjustRight(2)
	    else:
                if delta > 0:
                    self.adjustLeft(self.determineAdjust(delta,0.5*rotationCst*wheel))
                
                elif delta < 0:
                    self.adjustRight(self.determineAdjust(-delta,0.5*rotationCst*wheel))
                
                else:
                    # in case delta == 0, collision with wall, 2x correction to zero, robot adjusting right
                    self.adjustLeft(self.determineAdjust(0,0))
                
        elif (side == "right"):
            
            if self.connection:
                self.connection.sendMessage('-- Traveling: tracking right wall one step')

            distanceRightOne = self.checkDistanceRight()
            self.continueDrivingForward(0.5*rotationCst)
            distanceRightTwo = self.checkDistanceRight()

            (distanceRightOne , distanceRightTwo) = self.checkDistances(distanceRightOne,distanceRightTwo)

            delta = (distanceRightOne - distanceRightTwo)
	    print "delta", delta

	    if (distanceRightTwo<rightDistanceBoundaryMin)  and (delta>0):
		self.adjustRight(2)
	    elif (distanceRightTwo>rightDistanceBoundaryMax) and (delta<0):
	        self.adjustLeft(2)
	    else:

                if delta > 0:
                    self.adjustRight(self.determineAdjust(delta,0.5*rotationCst*wheel))
                
                elif delta < 0:
                    self.adjustLeft(self.determineAdjust(-delta,0.5*rotationCst*wheel))
                    
                else:
                    #if delta == 0, collision with wall, 2x correction to zero, robot adjusting left
                    self.adjustRight(self.determineAdjust(0,0))
                

    def trackOneTile(self, side = None,oneTile=distanceOneTile):

	if (not self.continueExecuting()):
            return
    
        self.wall = side
        
        totalDistance = oneTile/wheel
        
        if self.connection:
            self.connection.sendMessage('-- Traveling Blind: tracking one tile')
        
        while totalDistance > 0.0:
            
            collision = self.checkTouchSensor()
            if collision:
                self.continueDrivingBack(rotationCst)
                self.turn()
                return 0
        
            nextDistance = min(0.5*rotationCst,totalDistance) # Maximum 0.2*(perimeter of the Robot's wheestanceRightOne , distanceRightTwo) =elf.wall == "left"):
                print "trackOneTile: left"
                
                distanceLeftOne = self.checkDistanceLeft()
                self.continueDrivingForward(nextDistance)
                distanceLeftTwo = self.checkDistanceLeft()
                
                (distanceLeftOne , distanceLeftTwo) = self.checkDistances(distanceLeftOne,distanceLeftTwo)
                
                delta = (distanceLeftOne - distanceLeftTwo)
		print "delta", delta
                
		if (distanceLeftTwo<leftDistanceBoundaryMin) and (delta>0):
		    self.adjustLeft(2)
		elif (distanceLeftTwo>leftDistanceBoundaryMax) and (delta<0):
	            self.adjustRight(2)
		else:
                    if delta > 0:
                        self.adjustLeft(self.determineAdjust(delta,nextDistance*wheel))
                
                    elif delta < 0:
                        self.adjustRight(self.determineAdjust(-delta,nextDistance*wheel))
                
                    else:
                        # in case delta == 0, collision with wall, 2x correction to zero, robot adjusting right
                        self.adjustLeft(self.determineAdjust(0,0))
    
    
            elif(self.wall == "right"):
                print "trackOneTile: right"
            
                distanceRightOne = self.checkDistanceRight()
                self.continueDrivingForward(nextDistance)
                distanceRightTwo = self.checkDistanceRight()
                
                (distanceRightOne , distanceRightTwo) = self.checkDistances(distanceRightOne,distanceRightTwo)
                
                delta = (distanceRightOne - distanceRightTwo)
		print "delta", delta

      		if (distanceRightTwo<rightDistanceBoundaryMin) and (delta>0):
		    self.adjustRight(2)
		elif (distanceRightTwo>rightDistanceBoundaryMax) and (delta<0):
	            self.adjustLeft(2)
		else:

                    if delta > 0:
                        self.adjustRight(self.determineAdjust(delta,nextDistance*wheel))
                
                    elif delta < 0:
                        self.adjustLeft(self.determineAdjust(-delta,nextDistance*wheel))
                        
                    else:
                        #if delta == 0, collision with wall, 2x correction to zero, robot adjusting left
                        self.adjustRight(self.determineAdjust(0,0))
        
            elif(side == None):
                print "trackOneTile: none"
                self.moveWithoutWall(nextDistance)
            
            totalDistance -= nextDistance
        
        return 1                        ## return 1 omdat anders None hetzelfde is als False
   
    def checkDistances(self, distOne, distTwo):
	#include special start case
        
        result = (distOne, distTwo)
	return result


	
	if (distOne == distTwo == 0) or ((distOne >80) and ( distTwo >80)):
	    print "case 00"
	    
	    result = (0,0)
	
	elif distOne>80:
	    print "case 1"
	    
	    if distTwo > min(rightDistanceBoundaryMax,leftDistanceBoundaryMax):
		result = (distTwo-adjustDistance,distTwo)
	    
	    else:
		result = (distTwo + adjustDistance,distTwo)
	    
	elif distTwo>80:
	    print "case 2"
	    
	    if distOne > min(rightDistanceBoundaryMax,leftDistanceBoundaryMax):
		result = (distOne,distOne+adjustDistance)
	    
	    else:
		result = (distOne,distOne - adjustDistance)
        else:
            result = (distOne, distTwo)

        print "checkDResult" , result
	return result
	

    def checkWallToTrack(self,old,new):
        
        commonWall = self.world.checkCommonWall(old,new)
        commonWallList = set()

	print "commonWall: " + str(commonWall)

        if len(commonWall)>0:
            if ('N' in commonWall):
                if self.orientation == 'E':
		    commonWallList.add('Left')
		    
                elif self.orientation == 'W':
		    commonWallList.add('Right')

            if ('S' in commonWall):
                if self.orientation == 'E':
		    commonWallList.add('Right')
		    
                elif self.orientation == 'W':
		    commonWallList.add('Left')

            if ( 'E' in commonWall):
                if self.orientation == 'N':
		    commonWallList.add('Right')
		    
                elif self.orientation == 'S':
		    commonWallList.add('Left')

            if ('W' in commonWall):
                if self.orientation == 'N':
		    commonWallList.add('Left')

                elif self.orientation == 'S':
		    commonWallList.add('Right')

	    if len(commonWallList)>1:
		if self.checkDistanceRight() > (self.checkDistanceLeft()-leftSensorCorr) :
		    return 'Left'
		else:
		    return 'Right'
	    else:
		return list(commonWallList)[0]


        else:
            return 0
        

    def blindMove(self,newPosition,length = distanceOneTile):
        # the robot travels without an image on the next tile
        
	if (not self.continueExecuting()):
            return

        commonWall = self.checkWallToTrack(self.position,newPosition)
        if self.connection:
            self.connection.sendMessage('-- Traveling: Blind Move')
            self.connection.sendMessage('-- Traveling: commonwall = ' + str(commonWall))
        
        if commonWall == 'Left':
            result = self.trackOneTile('left')
            
        elif commonWall == 'Right':
            result = self.trackOneTile('right')
            
        else:
            result = self.trackOneTile(None, length)

        if not result:
            return 0
        
        return result        

    def deterministicMove(self,newPosition):
        # the robot travels to the next tile with an image

	if (not self.continueExecuting()):
            return
        
        oldTime = time.time()
        commonWall = self.checkWallToTrack(self.position,newPosition)
        if self.connection:
            self.connection.sendMessage('-- Traveling: deterministic Move')
            self.connection.sendMessage('-- Traveling: commonwall = ' + str(commonWall))

        if commonWall == 'Left':
            self.alignLeft(self.checkDistanceLeft())
            self.wall = 'left'
        elif commonWall == 'Right':
            self.alignRight(self.checkDistanceRight())
            self.wall = 'right'
        else:
            self.wall = None

        while True:

                collision = self.checkTouchSensor()
                if collision:
                    self.continueDrivingBack(rotationCst)
                    return 0

		if abs(self.camera.getPosition()) < 50:
		    
		    self.turnCameraLeftSwing()

                    if self.detectImage(newPosition):
		        return 1
		    self.turnCameraFront()
		    self.turnCameraRightSwing()

                    if self.detectImage(newPosition):
                        return 1
		    self.turnCameraFront()
		else:
		    if self.detectImage(newPosition):
                        return 1



                newTime = time.time()

                #jump out of the function when no image is detected after a curtain time
                if ((newTime - oldTime) > 60):
                    return 0
                
                
                if self.wall:
                    result = self.trackOneStep()
                    if result:
                        return 1
                        
                else:
                    self.moveWithoutWall()
 



    def moveWithoutWall(self, nextDistance=0.5*rotationCst):
        #the robot has no commonwall

	    if (not self.continueExecuting()):
                return

            distanceLeftOne = self.checkDistanceLeft()
            distanceRightOne = self.checkDistanceRight()
            
            self.continueDrivingForward(nextDistance)


            #0 is a default value
            # Not correcting sensor-values but just not adjusting when there is no wall
            if (distanceLeftOne > 40):
                distanceLeftOne = 0

            if distanceRightOne > 45:
                distanceRightOne = 0

            if (distanceLeftOne == 0) and (distanceRightOne == 0):
                return

            distanceLeftTwo = self.checkDistanceLeft()
            if distanceLeftOne == 0:
                distanceLeftTwo = 0
            if distanceLeftTwo > 40:
                distanceLeftOne = 0
                distanceLeftTwo = 0


            distanceRightTwo = self.checkDistanceRight()
            if distanceRightOne == 0:
                distanceRightTwo = 0
            if distanceRightTwo > 45:
                distanceRightOne = 0
                distanceRightTwo = 0

            if ((distanceLeftOne > distanceLeftTwo) or (distanceLeftOne == 0)) and (distanceRightOne < distanceRightTwo):

                adjust = self.determineAdjust(distanceRightTwo-distanceRightOne,nextDistance*wheel)
                self.adjustLeft(adjust)
                
            elif ((distanceLeftOne < distanceLeftTwo) or (distanceLeftOne == 0)) and (distanceRightOne > distanceRightTwo):

                adjust = self.determineAdjust(distanceRightOne-distanceRightTwo,nextDistance*wheel)
                self.adjustRight(adjust)
                
            elif (distanceLeftOne > distanceLeftTwo) and ((distanceRightOne < distanceRightTwo) or (distanceRightOne == 0)):

                adjust = self.determineAdjust(distanceLeftOne-distanceLeftTwo,nextDistance*wheel)
                self.adjustLeft(adjust)
                
            elif (distanceLeftOne < distanceLeftTwo)  and ((distanceRightOne > distanceRightTwo) or (distanceRightOne == 0)):

                adjust = self.determineAdjust(distanceLeftTwo-distanceLeftOne,nextDistance*wheel)
                self.adjustRight(adjust)                    
                        
    def getImRecResult(self):

	if (not self.continueExecuting()):
            return

	print "start imrecresult"
        global newImRec
	global image
	global imageSending
	newImRec = 0
	
        if self.connection:
	    # 
	    b = str(os.path.getsize('/home/pi/image.jpg'))
            self.connection.sendMessage('ImRec'+':'+b)
	    print "imrec sent to server"
            
	    while (not imageSending):
		print "not yet allowed to send picture"
                time.sleep(0.2)

	    imageSending = 0
                
	    print "start sending pic"
            self.connection.sendImage()
            
            while(newImRec == 0):
		print "waiting for imrec result"
                time.sleep(0.2)

        else:
            image = "0"
            return


        if newImRec == 2:
	    print "timeout receiving or damaged file, trying agian"
            return self.getImRecResult()
        
        elif newImRec == 1:
	    "imrec worked, result received"
            image = resultImRec
               

    def detectImage(self,position=()):
	global newImRec
	global image
        self.camera.detectImage()

	print "start getImrecResult"
	self.getImRecResult()
        
        if image != '0':
	 
            print 'image detected: ',image
	    
            if(self.state == 'R'):
                result = self.world.getTileFromImage(image)
            if(self.state == 'T'):
                result = self.world.getTileFromImageTrav(image,position)

            if (len(result) == 0):
                 return 0
            else:
                (image,posOr) = result
                 
            print 'on posOr: ',posOr
            self.position = posOr[0]
            
            self.orientation = self.determineOrientation(posOr[1])
            print 'so orientation is: ', self.orientation
            
            rowMajor = self.getRowMajor()
            res = self.client.postPosition(rowMajor,self.orientation)
            while (not res):
                res = self.client.postPosition(rowMajor,self.orientation)
            self.sendPositions()
            
            path = self.world.doGreedySearch(self.position)
            
            self.path = path[1:]
            if len(self.path) == 0:
                self.setStop()

            if self.connection:
                self.connection.sendMessage('-- Accepted result:'+ image)

	    self.adjustAfterImRec()
            return image
	    
        
        else:
            return 0
        

    def adjustAfterImRec(self):
	# 50 ipv 0 omwille van het lichtjes draaien van de camera 
	# als er vooraan afbeeldingen herkent moeten worden.
	camPos = self.camera.getPosition()
	if camPos > 50:
	    self.alignRight(self.checkDistanceRight())
	elif camPos < -50:
	    self.alignLeft(self.checkDistanceLeft())

    def determineOrientation(self, imageOrientation):

        orientations = ['N','E','S','W']
        index = orientations.index(imageOrientation)
	cameraPosition = self.camera.getPosition()
        
        if (cameraPosition < -50):
            index = (index+1)%4
        elif (cameraPosition  > 50):
            index = (index-1)%4

        return orientations[index]

    def roaming(self):

	if (not self.continueExecuting()):
            return

        self.state = 'R'
        
        self.wall = None
        self.orientation = None

        self.sendPositions()
        
        self.position = tuple()
        self.path = list()
        
        while True:

            if (not self.continueExecuting()):
                break

            if self.connection:
                self.connection.sendMessage('-- Roaming')
    
            collision = self.checkTouchSensor()
            if collision:
                self.continueDrivingBack(1*rotationCst)
                self.turn()
        
            distanceLeft = self.checkDistanceLeft()
            distanceRight = self.checkDistanceRight()
        
            if (distanceLeft < 30) or (self.wall == 'left'): # second is result of turn

                self.turnCameraLeft()
                self.alignLeft(distanceLeft)
                result = self.trackLeft()
                if result:
                    break

            elif (distanceRight < 30) or (self.wall == 'right'):

                self.turnCameraRight()
                self.alignRight(distanceRight)
                result = self.trackRight()
                if result:
                    break
            
            else:
                self.continueDrivingForward(rotationCst)

    def adaptOrientation(self, newOrientation):

        print "Reporting: adaptOrientation"        
        
        print 'oldor: ', self.orientation, ' to newor: ', newOrientation
        
        orientations = ['N','E','S','W']
        indexOld = orientations.index(self.orientation)
        indexNew = orientations.index(newOrientation)
        deltaOrientation = indexNew - indexOld
        
        if deltaOrientation == 3:
            deltaOrientation = -1

        if deltaOrientation == -3:
            deltaOrientation = 1

        if (deltaOrientation == 2) or (deltaOrientation == -2):

            if self.wall == 'left':
                self.turnRight()
                self.turnRight(False)
                deltaOrientation = 0

            elif self.wall == 'right':
                self.turnLeft()
                self.turnLeft(False)
                deltaOrientation = 0
            
        if deltaOrientation > 0:

            
            for i in range(deltaOrientation):
                #no wall to align with
                adjust = (i == 0)
                self.turnRight(adjust)

        else:
            

            for i in range(abs(deltaOrientation)):
                #no wall to align with
                adjust = (i == 0)
                self.turnLeft(adjust)
                
        self.orientation = newOrientation

        rowMajor = self.getRowMajor()
        res = self.client.postPosition(rowMajor,self.orientation)
        while (not res):
            res = self.client.postPosition(rowMajor,self.orientation)
        self.sendPositions()
                

    def adapt(self, delta):
        
        if delta[0] > 0:
            self.adaptOrientation('E')
        elif delta[0] < 0:
            self.adaptOrientation('W')
        elif delta[1] > 0:
            self.adaptOrientation('S')
        elif delta[1] < 0:
            self.adaptOrientation('N')


            
    def traveling(self):
        
        self.state ='T'
        
        if (not self.continueExecuting()):
            return

        if self.connection:
            self.connection.sendMessage('-- Traveling')
        
        while (len(self.path) >= 1):
            if (not self.continueExecuting()):
                break

            newPosition = self.path[0]
            self.path = self.path[1:]
            deltaY = newPosition[0] - self.position[0]
            deltaX = newPosition[1] - self.position[1]
            delta = (deltaX,deltaY)
            self.adapt(delta)
	    self.wall = None

            if self.connection:
            	self.connection.sendMessage('position: ' + str(self.position))

            imageOrientation = self.world.checkImagePosition(newPosition)
            print 'image on next tile?: ',imageOrientation
            if imageOrientation:
                self.adaptCameraPosition(imageOrientation)
                move = self.blindMove(newPosition,40)
                
                if not move:
                    break
                move = self.deterministicMove(newPosition)
                
                if not move:
                    break
            
            else:
                move = self.blindMove(newPosition)
                if not move:
                    break


            self.position = newPosition

            rowMajor = self.getRowMajor()
            res = self.client.postPosition(rowMajor,self.orientation)
            while (not res):
                res = self.client.postPosition(rowMajor,self.orientation)
            self.sendPositions()
        

    def execute(self):
	print "robot: execute"
	self.sendMap()
        while True:
            if not self.continueExecuting():
                break
            self.roaming()
            self.traveling()

    def getRowMajor(self):
        return int((self.position[0]*self.world.breadth) + (self.position[1]))
	
    def setStop(self):
	global stopp
	stopp = 1

    def stopStart(self):
	global stopp
	stopp=0

    def continueExecuting(self):
	if stopp==0:
 	     return True
	elif stopp==1:
	     return False

    def setNewImRec(self, val):
	global newImRec
	newImRec = val

    def setResultImRec(self, res):
	global resultImRec
	resultImRec = res

    def allowSendingImage(self):
        global imageSending
        imageSending = 1

    def disableSendingImage(self):
        global imageSending
        imageSending = 0

    def allowSendingMap(self):
        global mapSending
        mapSending = 1

    def disableSendingMap(self):
        global mapSending
        mapSending = 0

    def sendPositions(self):
	print "robot: send positions"
        positions = self.client.getAllRobotsPositions()
	print "robot: send positions 2"
        self.connection.sendMessage('teams: ' + positions)
	print "robot: send positions 3"
        
    def sendMap(self):
	global mapSending
	if self.connection:
	    b = str(os.path.getsize('/home/pi/Desktop/peno/Auto_drive/kaart.txt'))
	    print "CL:" + b
            self.connection.sendMessage('World'+':'+b)
	    print "World sent to server"
            
	    while (not mapSending):
		print "not yet allowed to send map"
                time.sleep(0.2)

	    mapSending = 0
                
	    print "start sending map"
            self.connection.sendMap()
            print "map sent"

