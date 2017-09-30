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
from patternMatcher import *

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
    turnCameraValueLeft = -80 
    global turnCameraValueRight         # power to turn the camera right
    turnCameraValueRight = 80
    global motorLeftPower               # power on the left motor (forward)
    motorLeftPower = -220
    global motorRightPower              # power on the right motor (forward)
    motorRightPower = -210
    global motorLeftPowerBackward       # power on the left motor (backward)
    motorLeftPowerBackward = 255
    global motorRightPowerBackward      # power on the right motor (backward)
    motorRightPowerBackward = 255
    global medianNumber                 # number of value to calculate median
    medianNumber = 15
    global adjustLeftLeftMotor          # power to adjust to the leftside with left motor
    adjustLeftLeftMotor = 0
    global adjustLeftRightMotor         # power to adjust to the leftside with right motor
    adjustLeftRightMotor = -120
    global adjustRightLeftMotor         # power to adjust to the rightside with the left motor
    adjustRightLeftMotor = -120
    global adjustRightRightMotor        # power to adjust to the rightside with the right motor
    adjustRightRightMotor = 0
    global leftDistanceBoundaryMin      # Minimum distance for the left boundary in adjust(strook)
    leftDistanceBoundaryMin = 25
    global leftDistanceBoundaryMax      # Maximum distance for the left boundary in adjust(strook)
    leftDistanceBoundaryMax = 35
    global distanceToCornerTurn         # Distance needed from sensors to put the pi into cornerturn
    distanceToCornerTurn = 80
    global rightDistanceBoundaryMin     # Minimum distance for the right boundary in adjust(strook)
    rightDistanceBoundaryMin = 25
    global rightDistanceBoundaryMax     # Maximum distance for the right boundary in adjust(strook)
    rightDistanceBoundaryMax = 35
    global distanceOneStepForward       # Distance that the pi covers in the 0.5s steps of moving forward
    distanceOneStepForward = 15
    global degFor90deg                  # Degrees needed for an orthogonal turn
    degFor90deg = 400
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
    global distanceToWallToFollow
    distanceToWallToFollow = 40
    global tries
    tries = 0

    global image

    global leftAdjust
    leftAdjust = 2
    global rightAdjust
    rightAdjust = 2

    def __init__(self, connection=None,ip = None, port = None, wall=None, cameraPosition=0, orientation=None, position=tuple(), path=list(), state = ''):
       	global mapSending
        
	self.connection = connection
        self.client = Client(ip,port)
        self.wall = wall
        self.camera = Camera(cameraPosition)
        self.orientation = orientation
        self.position = position
        self.path = path
        self.state = state
	self.points = 0
	
	if self.connection:
            	self.connection.sendMessage("-- Robot connected")
	self.sendPositions()

 	# Set the world
	self.client.getWorld()
        self.world = World("kaart.txt")
	self.matcher = patternMatcher(self.world)

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

    def setPoints(self,points):
        self.points += points
        if self.connection:
            self.connection.sendMessage('score ' + str(self.points))
            
    def resetPoints(self):
        self.points = 0
        if self.connection:
            self.connection.sendMessage('score 0.0')
        
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
        self.turnCamera(-20)
        self.camera.setPosition(-20)
        
    def turnCameraRightSwing(self):
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
	    self.alignWithWallBeforeTurning()


        motorRotateDegree([200],[degFor90deg],[self.MOTOR_RIGHT.getPort()])
        self.pauseMotors()                          

    def turnRight(self,adjust = True):
        if self.connection:
            self.connection.sendMessage('-- turning right ')
	if (adjust and (self.state == 'T') ):
	    self.alignWithWallBeforeTurning()

        motorRotateDegree([200],[degFor90deg],[self.MOTOR_LEFT.getPort()])
        self.pauseMotors()                           
        
    def turn(self):
        # This function makes the robot turn
    

        if (self.wall == 'left'):
            self.turnRight()
            self.turnCameraLeft()
        else:
            if (self.wall == None):
                self.wall = 'right'
            self.turnLeft()
            self.turnCameraRight()

    def alignWithWallBeforeTurning(self):

	walls = self.world.TILES.get(self.world.map[self.position[0]][self.position[1]])
	orientations = ['N','E','S','W']
	orientation = orientations.index(self.orientation)
	
	# Check if right wall
	if walls[(orientation+1)%4]:
	    self.alignRight(self.checkDistanceRight())
	# Check if left wall
	elif walls[(orientation-1)%4]:
	    self.alignLeft(self.checkDistanceLeft())



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
	
        self.setupBrickPi()
        self.MOTOR_LEFT.setPower(0)
        self.MOTOR_RIGHT.setPower(0)
        
        BrickPiUpdateValues()
	
    def continueDrivingForward(self,c):
        # This function makes the robot drive c x one rotation of its wheels (= c x 19 cm) forward
        
        deg = c*360
        
        # Important: driving forward corresponds with a positive number of degrees!
        motorRotateDegree([motorLeftPower,motorRightPower],[deg,deg],[self.MOTOR_LEFT.getPort(),self.MOTOR_RIGHT.getPort()])
        self.pauseMotors()
 
            
    def continueDrivingBack(self,c):
         # This function makes the robot drive c x one rotation of its wheels (= c x 19 cm) forward

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
		distance = self.SENSOR_ULTRASONIC.getValue()
                dist.append(distance) # BrickPi.Sensor[PORT] stores the value obtained from sensor
                i += 1
            time.sleep(.02) # sleep for 20 ms


        a = np.array(dist)
        a = self.reject_outliers(a)
        result = np.mean(a)
        
        if self.connection:
            self.connection.sendMessage('distance left: '+str(result))
        return result

    def checkDistanceRight(self):
	std = 15
	j = 0
	result = self.checkDistanceRightResultList()	
	mediaan = np.median(result)  

  	time_passed = 0
	begintime = time.time()

	while ((std>(1.5*(mediaan/20))) and (time_passed<3)):
	    if (j > 10):
		result = self.checkDistanceRightResultList()
		j = 0    
	    medresult = result[:]
	    for i in range(0,len(result)):
		medresult[i] = abs(medresult[i]-mediaan)
	    maximum = max(medresult)
	    maximum = medresult.index(maximum)
	    extra_result = self.checkDistanceRightHulp()
	    result[maximum]= extra_result
	    std = np.std(result)
	    j += 1
	    mediaan = np.median(result)
	    print mediaan
	    endtime = time.time()
	    time_passed =  endtime - begintime

	resultaat = np.median(result)
	if self.connection:
            self.connection.sendMessage('distance right: '+str(resultaat))
        
	return 	resultaat

    def checkDistanceRightResultList(self):
	result1 =  self.checkDistanceRightHulp()
        result2 =  self.checkDistanceRightHulp()
	result3 =  self.checkDistanceRightHulp()
	result4 =  self.checkDistanceRightHulp()
        result5 =  self.checkDistanceRightHulp()
	result6 =  self.checkDistanceRightHulp()
	result = [result1,result2,result3,result4,result5,result6]
	return result

    def checkDistanceRightHulp(self):
        dist = []
        i = 0
	nbDiscarded = 0
        while (i < medianNumber) and (nbDiscarded < medianNumber):
            
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
		if distance > 10:
	            dist.append(distance)
                    i += 1
		else:
		    nbDiscarded += 1
                
        a = np.array(dist)
        a = self.reject_outliers(a)
        result = np.mean(a)

	# Handle nan's
	if np.isnan(result):
	    result = self.checkDistanceRightHulp()        

        return result
        
    def adjustLeft(self,t=1): 
        # This method makes the robot turn a little using its left wheel.
        # Make sure that t > 0 in case you want a forward adaption!

        
        motorRotateDegree([adjustRightLeftMotor],[adjustFactor*t],[self.MOTOR_LEFT.getPort()])
        self.pauseMotors()

    def adjustRight(self,t=1): # make the robot turn a little with his right wheel
        # This method makes the robot turn a little using its right wheel.
        # Make sure that t > 0 in case you want a forward adaption!        

        motorRotateDegree([adjustLeftRightMotor],[adjustFactor*t],[self.MOTOR_RIGHT.getPort()])
        self.pauseMotors()

    def alignLeft(self,minDistance):

        if self.connection:
            self.connection.sendMessage('-- aligning left')

	mindistances = []
	mindistances.append(minDistance)
	

        self.wall = 'left'
        
        self.adjustLeft(2)
        adjusting = 'Right'
        
        while self.continueExecuting():
            
            distance = self.checkDistanceLeft()
	    mindistances.append(distance)
	    if (distance <= minDistance) and (adjusting == 'Right'):
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
		self.adjustLeft(0.5)
                break

    def alignRight(self,minDistance):

        if self.connection:
            self.connection.sendMessage('-- aligning right')

        self.wall = 'right'

        self.adjustRight(1)
        adjusting = 'Left'

        while self.continueExecuting():
            distance = self.checkDistanceRight()
	    distance = np.rint(distance)
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
		time.sleep(0.2)
                break

    def determineAdjust(self,distanceToWall,distanceFromLastPosition):
        # Determines the amount of adjust needed when a difference in distance
        # of distanceToWall cm is registered when traversed distanceFromLastPosition cm
            
        if (distanceToWall == 0):
	    return 1.0

        result =  (degFor90deg/(np.pi/2))*np.arctan(distanceToWall/distanceFromLastPosition)/(adjustFactor*1.5)
	if (np.floor(result) == 0.0):
	    result = 1.0
	return min(result,3)
	
    def trackLeft(self):

	if (not self.continueExecuting()):
            return

        if self.connection:
            self.connection.sendMessage('-- Roaming: tracking left wall')
        distance = 0

        while self.continueExecuting():
            
            collision = self.checkTouchSensor()
            if collision:
                self.continueDrivingBack(rotationCst)
                self.turn()
                return 0

            if self.detectImage():
                return 1

            distanceLeft = self.checkDistanceLeft()
            
            if (distanceLeft < leftDistanceBoundaryMin and ((distanceLeft <= distance) or (distance == 0))):
                if (distance == 0):
                    adjust = 1
                else:
                    adjust = self.determineAdjust(distance-distanceLeft,0.5*wheel*rotationCst)
                print "trackLeft: case distanceLeft < leftDistanceBoundaryMin, adjust = ",adjust
                self.adjustLeft(adjust)
                self.continueDrivingForward(0.5*rotationCst)
                distance = distanceLeft
		
            elif (distanceLeft > leftDistanceBoundaryMax and distanceLeft < distanceToCornerTurn and distanceLeft >= distance):
                if (distance == 0):
                    adjust = 1
                else:
                    adjust = self.determineAdjust(distanceLeft-distance,0.5*wheel*rotationCst) 
                print "trackLeft: case distanceLeft > leftDistanceBoundaryMax but no corner turn, adjust = ",adjust               
                self.adjustRight(adjust)
                self.continueDrivingForward(0.5*rotationCst)
                distance = distanceLeft

            elif (distanceLeft >= distanceToCornerTurn):
                print "trackLeft: cornerTurn" 
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

            if (distanceRight < rightDistanceBoundaryMin) and ((distanceRight <= distance) or (distance == 0)): # voor de hindernis met de versmalling
                if (distance == 0):
                    adjust = 1
                else:
                    adjust = self.determineAdjust(distance-distanceRight,0.5*wheel*rotationCst)
                print "trackRight: case distanceRight < rightDistanceBoundaryMin, adjust = ",adjust
                self.adjustRight(adjust)
                self.continueDrivingForward(0.5*rotationCst)
                distance = distanceRight
	
		
            elif (distanceRight > rightDistanceBoundaryMax and distanceRight < distanceToCornerTurn and distanceRight >= distance):
                if (distance == 0):
                    adjust = 1
                else:
                    adjust = self.determineAdjust(distanceRight-distance,0.5*wheel*rotationCst)    
                print "trackRight: case distanceRight > rightDistanceBoundaryMax but no cornerturn, adjust = ",adjust            
                self.adjustLeft(adjust)
                self.continueDrivingForward(0.5*rotationCst)
                distance = distanceRight

            elif (distanceRight >= distanceToCornerTurn):
                print "trackRight: cornerTurn" 
                self.cornerTurn()
                self.wall = None

                return 0

            else: # als die nie in de vorige gaat , rijdt hij gewoon rechtdoor, dit doet hij dus ook als het verschil plots te groot wordt (de inkeping)

                self.continueDrivingForward(0.5*rotationCst)
                

    def trackOneTile(self, side = None, oneTile=distanceOneTile):
        global leftAdjust
        leftAdjust = 2
        global rightAdjust
        rightAdjust = 2

        if (not self.continueExecuting()):
            return

	# To make sure roaming, which uses this method, works well
	if self.state == 'T':
	    self.wall = side
        
        totalDistance = oneTile/wheel
        
        if self.connection:
            self.connection.sendMessage('-- Traveling Blind: tracking one tile')
        
        while totalDistance > 0.0:
            
            
            if (not self.continueExecuting()):
                return 0
            
            collision = self.checkTouchSensor()
            if collision:
                self.continueDrivingBack(rotationCst)
                self.turn()
                return 0
        
            nextDistance = min(0.5*rotationCst,totalDistance) # Maximum 0.2*(perimeter of the Robot's wheel) forward
        
            if(self.wall == "left"):
                print "trackOneTile: case left"
                
                distanceLeftOne = self.checkDistanceLeft()
                self.moveLeft(distanceLeftOne, distanceLeftOne)
                self.continueDrivingForward(nextDistance)
                distanceLeftTwo = self.checkDistanceLeft()
                self.moveLeft(distanceLeftOne, distanceLeftTwo)
    
    
            elif(self.wall == "right"):
                print "trackOneTile: right"
            
                distanceRightOne = self.checkDistanceRight()
                self.moveRight(distanceRightOne, distanceRightOne)
                self.continueDrivingForward(nextDistance)
                distanceRightTwo = self.checkDistanceRight()
                self.moveRight(distanceRightOne, distanceRightTwo)
        
            elif(side == None):
                print "trackOneTile: none"
                self.moveWithoutWall(nextDistance)
            
            totalDistance -= nextDistance
        
        return 1                        ## return 1 omdat anders None hetzelfde is als False
   
    def checkDistances(self, distOne, distTwo):
        #include special start case
        result = (distOne, distTwo)
        return result

	

    def checkWallToTrack(self,old,new):
        
        commonWall = self.world.checkCommonWall(old,new)
        commonWallList = set()

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
        

    def blindMove(self,previousPosition,length = distanceOneTile):
        # the robot travels without an image on the next tile
        
        if (not self.continueExecuting()):
            return

        commonWall = self.checkWallToTrack(previousPosition, self.position)
        if self.connection:
            self.connection.sendMessage('-- Traveling: Blind Move')
            self.connection.sendMessage('-- Traveling: commonwall = ' + str(commonWall))
        
        if commonWall == 'Left':
	    result = self.trackOneTile(None,length)
            #result = self.trackOneTile('left')
            
        elif commonWall == 'Right':
	    result = self.trackOneTile(None,length)
            #result = self.trackOneTile('right')
            
        else:
            result = self.trackOneTile(None, length)

        if not result:
            return 0
        
        return result        

    def deterministicMove(self):
        global leftAdjust
        leftAdjust = 2
        global rightAdjust
        rightAdjust = 2

        
        # the robot travels to the next tile with an image
        if (not self.continueExecuting()):
            return 0

	totalDistance = ((0.3*distanceOneTile)/wheel)
        nextDistance = min(0.5*rotationCst,totalDistance)


        sides = self.world.checkTileForImage(self.orientation,self.position)

	if sides[1]:
	    self.alignRight(self.checkDistanceRight())
	elif sides[3]:
	    self.alignLeft(self.checkDistanceLeft())
        
        

        while (totalDistance >=0):

    	    if (not self.continueExecuting()):
                    return 0
    
    	    collision = self.checkTouchSensor()
            if collision:
                self.continueDrivingBack(rotationCst)
                self.turn()
                return 0

	    distanceLeftOne = self.checkDistanceLeft()
            distanceRightOne = self.checkDistanceRight()
            self.move(distanceLeftOne, distanceLeftOne, distanceRightOne, distanceRightOne)
            self.continueDrivingForward(nextDistance)
            distanceLeftTwo = self.checkDistanceLeft()
            distanceRightTwo = self.checkDistanceRight()
            self.move(distanceLeftOne, distanceLeftTwo, distanceRightOne, distanceRightTwo)

            for i in range(len(sides)):
                # Check if there's a wall on this side
                if sides[i] == 1:
        
                    # Check which wall it is
                    if ((i == 0)):
                        
                        #self.turnCameraLeftSwing()
                        #if self.tryImage(0):
			    #self.turnCameraFront()
                            #return 1
                                
                        #self.turnCameraFront()
                        
                        #self.turnCameraRightSwing()
                        #if self.tryImage(0):
			    #self.turnCameraFront()
                            #return 1
                    
                        self.turnCameraFront()
			if self.tryImage(0):
                            return 1

                        
                    elif i == 1:
                        self.turnCameraRight()
                        if self.tryImage(1):
                            return 1
                        
                    elif i == 2:
                        print "ERROR in deterministic move: Robot should detect an image behind itself!"
                        
                    elif i == 3:
                        self.turnCameraLeft()
                        if self.tryImage(-1):
                            return 1
                    
                    else:
                        print "ERROR in deterministic move: No wall to detect image on!"

            

	    totalDistance -= nextDistance
	    
	return 0
 

    def tryImage(self,side):
	# side = -1,0,1
        print "INTRYIMAGE"
        print "INTRYDETECTIMAGE"
        result = self.tryDetectImage(side)
        print "OUTTRYDETECTIMAGE"

        # If returns 1, the above method returns
        if result == 1:
            return 1
        
        
        elif result == 2:
            # WRONG from server:
            print "INTRYDETECTIMAGE"
            self.tryDetectImage(side)
            print "OUTTRYDETECTIMAGE"
            # If return 0, the above method continues
            return 0
        else:
            return 0


    def move(self, distanceLeftOne, distanceLeftTwo, distanceRightOne, distanceRightTwo):
        global leftAdjust
        global rightAdjust
        
        deltaLeft = distanceLeftTwo - distanceLeftOne
        deltaRight = distanceRightTwo - distanceRightOne
        
        if (not self.continueExecuting()):
            return

        if(distanceLeftTwo <= 20):
            distanceLeftTwo = 20
        if(distanceLeftOne <= 20):
            distanceLeftOne = 20
        elif (distanceLeftTwo >= 35) and (distanceRightTwo >= 40):
            print "move case: (distanceLeftTwo > 35) and (distanceRightTwo > 40)"
            return
        elif (distanceLeftTwo < 35) and (distanceRightTwo >= 40):
            print "move case: (distanceLeftTwo < 35) and (distanceRightTwo >= 40)"
            self.moveLeft(distanceLeftOne,distanceLeftTwo)
            return
            
        elif (distanceLeftTwo >= 35) and (distanceRightTwo < 40):
            print "move case: (distanceLeftTwo > 35) and (distanceRightTwo < 40)"
            self.moveRight(distanceRightOne,distanceRightTwo)
            return
            
            
        #first look if we have to go to our distanceBand
        if distanceLeftTwo < leftDistanceBoundaryMin:
            if (deltaLeft <= 0) and (deltaRight >=0):
                print "move case: distanceLeftTwo < leftDistanceBoundaryMin adjust = ", leftAdjust
                self.adjustLeft(max(1,leftAdjust))
		leftAdjust -= 1
            return
        
        elif distanceLeftTwo > leftDistanceBoundaryMax:
            if (deltaLeft >= 0) and (deltaRight <= 0):
                print "move case: distanceLeftTwo > leftDistanceBoundaryMax adjust =", rightAdjust
                self.adjustRight(max(1,rightAdjust))
		rightAdjust -= 1
            return
        
        elif distanceRightTwo < rightDistanceBoundaryMin:
            if (deltaRight <= 0) and (deltaLeft >= 0):
                print "move case: distanceRightTwo < rightDistanceBoundaryMin adjust = ", rightAdjust
                self.adjustRight(max(1,rightAdjust))
		rightAdjust -= 1
            return
        
        elif distanceRightTwo > rightDistanceBoundaryMax:
            if (deltaRight >= 0)  and (deltaLeft <=0):
                print "move case: distanceRightTwo > rightDistanceBoundaryMax adjust = ", leftAdjust
                self.adjustLeft(max(1,leftAdjust))
		leftAdjust -= 1
            return
        
        #we are in our distanceBand
	rightAdjust = 2
	leftAdjust = 2
        if (deltaLeft > 0) and (deltaRight < 0):
            adjust = self.determineAdjust(distanceLeftTwo, distanceLeftOne)
            print "move case: deltaLeft > 0 adjust = ", adjust
            self.adjustRight(adjust)
            return
        elif (deltaLeft < 0) and (deltaRight > 0):
            adjust = self.determineAdjust(distanceLeftOne, distanceLeftTwo)
            print "move case: deltaLeft < 0 adjust = ", adjust
            self.adjustLeft(adjust)
            return
        elif (deltaRight > 0) and (deltaLeft <0):
            adjust = self.determineAdjust(distanceRightTwo, distanceRightOne)
            print "move case: deltaRight > 0 adjust = ", adjust
            self.adjustLeft(adjust)
            return
        elif (deltaRight < 0) and (deltaLeft >0):
            adjust = self.determineAdjust(distanceRightOne, distanceRightTwo)
            print "move case: deltaRight < 0 adjust = ", adjust
            self.adjustRight(adjust)
            return
        
    def moveLeft(self, distanceLeftOne, distanceLeftTwo):
        
        global leftAdjust
	global rightAdjust
        
        deltaLeft = distanceLeftTwo - distanceLeftOne
        
        if (not self.continueExecuting()):
            return
        
        if(distanceLeftTwo <= 20):
            distanceLeftTwo = 20
        if(distanceLeftOne <= 20):
            distanceLeftTwo = 20

	if (distanceLeftTwo >= 60):
            print "moveLeft case: (distanceLeftTwo > 60)"
            return
           
            
        #first look if we have to go to our distanceBand
        if distanceLeftTwo < leftDistanceBoundaryMin:
            if deltaLeft <= 0:
                print "moveLeft case: distanceLeftTwo < leftDistanceBoundaryMin adjust = ", leftAdjust
                self.adjustLeft(max(1,leftAdjust))
		leftAdjust -= 1
            return
        
        elif distanceLeftTwo > leftDistanceBoundaryMax:
            if deltaLeft >= 0:
		print "moveLeft case: distanceLeftTwo > leftDistanceBoundaryMax adjust =", rightAdjust
                self.adjustRight(max(1,rightAdjust))
		rightAdjust -= 1
            return
    
        
        #we are in our distanceBand
	rightAdjust = 2
	leftAdjust = 2

        if deltaLeft > 0:
            adjust = self.determineAdjust(distanceLeftTwo, distanceLeftOne)
            print "moveLeft case: deltaLeft > 0 adjust = ", adjust
            self.adjustRight(adjust)
            return
        elif deltaLeft < 0:
            adjust = self.determineAdjust(distanceLeftOne, distanceLeftTwo)
            print "moveLeft case: deltaLeft < 0 adjust = ", adjust
            self.adjustLeft(adjust)
            return
        


    def moveRight(self, distanceRightOne, distanceRightTwo):

        global rightAdjust
	global leftAdjust
        
        deltaRight = distanceRightTwo - distanceRightOne
        
        if (not self.continueExecuting()):
            return
        
	if (distanceRightTwo >= 60):
            print "moveRight case: (distanceRightTwo > 60)"
            return

            
        #first look if we have to go to our distanceBand
        if distanceRightTwo < rightDistanceBoundaryMin:
            if deltaRight <= 0:
                print "moveRight case: distanceRightTwo < rightDistanceBoundaryMin adjust = ", rightAdjust
                self.adjustRight(max(1,rightAdjust))
		rightAdjust -= 1
            return
        
        elif distanceRightTwo > rightDistanceBoundaryMax:
            if deltaRight >= 0:
                print "moveRight case: distanceRightTwo > rightDistanceBoundaryMax adjust = ", leftAdjust
                self.adjustLeft(max(1,leftAdjust))
		leftAdjust -= 1
            return
        
        #we are in our distanceBand
        rightAdjust = 2
	leftAdjust = 2
	if deltaRight > 0:
            adjust = self.determineAdjust(distanceRightTwo, distanceRightOne)
            print "moveRight case: deltaRight > 0 adjust = ", adjust
            self.adjustLeft(adjust)
            return
        elif deltaRight < 0:
            adjust = self.determineAdjust(distanceRightOne, distanceRightTwo)
            print "moveRight case: deltaRight < 0 adjust = ", adjust
            self.adjustRight(adjust)
            return



    def moveWithoutWall(self, nextDistance=0.5*rotationCst):
        #the robot has no commonwall
        
        if (not self.continueExecuting()):
            return

        distanceLeftOne = self.checkDistanceLeft()
        distanceRightOne = self.checkDistanceRight()
        self.move(distanceLeftOne, distanceLeftOne, distanceRightOne, distanceRightOne)
        self.continueDrivingForward(nextDistance)
        distanceLeftTwo = self.checkDistanceLeft()
        distanceRightTwo = self.checkDistanceRight()
        self.move(distanceLeftOne, distanceLeftTwo, distanceRightOne, distanceRightTwo)

                        
    def getImRecResult(self):

	if (not self.continueExecuting()):
            return

        global newImRec
	global image
	global imageSending
	newImRec = 0
	
        if self.connection:
	    # 
	    b = str(os.path.getsize('/home/pi/image.jpg'))
            self.connection.sendMessage('ImRec'+':'+b)
            
	    while (not imageSending):
		print "not yet allowed to send picture"
                time.sleep(0.2)

	    imageSending = 0
                
	    print "start sending pic"
            self.connection.sendImage()
            
            while(newImRec == 0):
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


    def tryDetectImage(self,side):
	global tries
	# If already tried twice, return
    	if tries == 2:
	    tries = 0
            return 1
        
    	self.camera.detectImage()
    	self.getImRecResult()
    	if self.connection:
            self.connection.sendMessage('-- Accepted result: '+ image)
        
    	if image != '0':
      	    tries += 1
        
            imageToSend = image.split(".")[0]
            if self.connection:
            	self.connection.sendMessage('-- Posting symbol to server: '+ image)
            respons = self.client.postSymbol(self.getRowMajor(),self.determineImageOrientation(side),imageToSend)
        
            if self.connection:
            	self.connection.sendMessage('-- Answer from server: '+ str(respons))
        
            if respons == "TOOLATE":
            	print "TOOLATE"
            	tries = 0
            	return 1
	    
            elif respons in ["0.0", "1.0", "0.5"]:
            	print "POINTS"
            	self.setPoints(float(respons))
            	tries = 0
            	return 1
	    
            else: # WRONG
            	print respons 
            	return 2
	    
        else:
            return 0
               

    def detectImage(self,position=()):
        
	global newImRec
	global image

        self.camera.detectImage()

	self.getImRecResult()
        
        if image != '0':
            
            result = self.world.getTileFromImage(image)

            if (len(result) == 0):
                 return 0
            else:
                (image,posOr) = result

	    if self.connection:
                self.connection.sendMessage('-- Accepted result :'+ image)
                 
            self.position = posOr[0]
            self.orientation = self.determineOrientation(posOr[1])
            
            rowMajor = self.getRowMajor()
            res = self.client.postPosition(rowMajor,self.orientation)
            while (not res):
                res = self.client.postPosition(rowMajor,self.orientation)
            
	    positions = self.sendPositions()
	    discoveredSymbols = self.client.getAllDiscoveredSymbols()
            self.world.updateSymbols(discoveredSymbols)
            path = self.world.determineNearestGoal(self.position,positions)
            
            self.path = path[1:]
            if len(self.path) == 0:
                # This should be impossible, since no 2 images are located on the same tile.
                self.setStop()
            else:
                if self.connection:
                    self.connection.sendMessage('-- Nearest goal: '+ str(path[-1]))

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

    def determineImageOrientation(self, side):

	orientations = ['N','E','S','W']
        index = orientations.index(self.orientation)
	index = (index+side)%4
	return orientations[index]

    def roaming(self):

        # Kijk of GUI autonoom rijden gestopt heeft
        if (not self.continueExecuting()):
            return

        # Initialisatie in roaming toestand
        self.state = 'R'
        
        self.wall = None
        self.orientation = None


	self.client.postPosition('?','?')
        self.sendPositions()
        
        self.position = tuple()
        self.path = list()

        # Variabelen om het pad te construeren
        self.pattern = list()

	if self.connection:
            self.connection.sendMessage('drawPath: []')
	
        if self.connection:
                self.connection.sendMessage('-- Roaming')
        
        direction = 'f' # One of F = Forward, B = Backward, L = Left, R = Right after turning relatively to the start position
        self.initialOrientation = None # left or right wall that was taken as 1N the first time means E or W
        walls = [0,0,0,0] # Wall F, R, B, L

        knownPosition = False
        
        while(not knownPosition):

            # Kijk of GUI autonoom rijden gestopt heeft
            if (not self.continueExecuting()):
                return
        
            thisType = '0N' # Default: veronderstel 0N
            walls = [0,0,0,0] # Reset walls
            
            distanceLeft = self.checkDistanceLeft()
            distanceRight = self.checkDistanceRight()
            
            if (distanceLeft < distanceToWallToFollow): # distanceToWallToFollow is een global die experimenteel bepaald moet worden

                print '1 wall on left side'
		self.wall = 'left'

                if self.initialOrientation == None: # Only update first time, reference for later use
                    self.initialOrientation = 'E'
                
                walls[3] = 1

		self.alignLeft(distanceLeft)
                self.turnCameraLeft()
                if self.detectImage(): # Kijk eerst voor afbeeldingsherkenning
                    return
                
                if distanceRight < distanceToWallToFollow:
                    self.turnCameraRight()
                    if self.detectImage(): # Kijk eerst voor afbeeldingsherkenning
                        return

                    print '2 wall on right side'

                    walls[1] = 1

               

                result = self.trackOneTile(None)
                if not result:

                    print 'could not drive forward'

                    walls[0] = 1

                    thisType = self.determineTileType(walls,self.determineRelativeOrientation(direction))
                    self.pattern.append((direction,thisType))

                    print 'thisType: ',thisType
                    
                    if thisType[0] == '3': # Type 3
                                                
                        #self.continueDrivingBack()
                        #self.turnRight()

                        self.alignLeft(self.checkDistanceLeft())
			if self.detectImage(): # Kijk eerst voor afbeeldingsherkenning
                    	    return

                        print 'driven backward, turned right, aligned left'
                        
                        result = self.trackOneTile(None)

                        if not result: # We know we are on type 3, so there shouldn't be a wall in front of us after having turned to the right
                            print 'Collision, but there should be no wall in front of the robot!!!'

                        direction = 'r'

                        print 'new direction: ',direction
                        
                        
                    elif thisType[0] == '4':
                        
			if self.detectImage(): # Kijk eerst voor afbeeldingsherkenning
                    	    return
                      
                        self.continueDrivingBack(rotationCst)
                        self.turn()

                        self.continueDrivingForward(1) # HOEVEEL??? TOT HET MIDDEN VAN DE TEGEL

                        self.alignRight(self.checkDistanceRight())

                        print 'driven backward, turned left, driven backward, turned left, driven forward, aligned right'
                        
                        result = self.trackOneTile(None)

                        if not result: # We know there's no wall behind us; if there were a wall, we'd been captured in between 4 walls
                            print 'Robot captured in between 4 walls!!!'
                        
                        direction = 'b'

                        print 'new direction: ',direction

                else:
                    
                    thisType = self.determineTileType(walls,self.determineRelativeOrientation(direction))
                    self.pattern.append((direction,thisType)) # Voeg type 1 of 2 toe aan pattern

                    direction = 'f'

                    print 'new direction: ',direction
                    

            elif (distanceRight < distanceToWallToFollow):

                print '1 wall on right side'
		self.wall = 'right'

                if self.initialOrientation == None: # Only update first time, for later use
                    self.initialOrientation = 'W'

                walls[1] = 1

		self.alignRight(distanceRight)
                self.turnCameraRight()
                if self.detectImage(): # Kijk eerst voor afbeeldingsherkenning
                    return
                
                if distanceLeft < distanceToWallToFollow:

                    print '2 wall on left side'

                    walls[3] = 1
                    self.turnCameraLeft()
                    if self.detectImage(): # Kijk eerst voor afbeeldingsherkenning
                        return

                

                result = self.trackOneTile(None)
                if not result:

                    print 'could not drive forward'

                    walls[0] = 1

                    thisType = self.determineTileType(walls,self.determineRelativeOrientation(direction))
                    self.pattern.append((direction,thisType))

                    print 'thisType: ',thisType
                    
                    if thisType[0] == '3':
                        
                        #self.continueDrivingBack()
                        #self.turnLeft()

                        self.alignRight(self.checkDistanceRight())

			if self.detectImage(): # Kijk eerst voor afbeeldingsherkenning
                    	    return

                        print 'driven backward, turned left, aligned right'
                        
                        result = self.trackOneTile(None)

                        if not result:
                            print 'Collision, but there should be no wall in front of the robot!!!'

                        direction = 'l'

                        printontinue


		self.walirection

                    elif thisType[0] == '4':
                        
			if self.detectImage(): # Kijk eerst voor afbeeldingsherkenning
                    	    return                       

                        self.continueDrivingBack(rotationCst)
                        self.turn()

                        self.continueDrivingForward(1) # HOEVEEL??? TOT HET MIDDEN VAN DE TEGEL

                        print 'driven backward, turned right, driven backward, turned right, driven forward, aligned left'

                        self.alignRight(self.checkDistanceRight())
                        result = self.trackOneTile(None)

                        if not result:
                            print 'Robot captured in between 4 walls!!!'
                        
                        direction = 'b'

                        print 'new direction: ',direction

                else:
                    
                    thisType = self.determineTileType(walls,self.determineRelativeOrientation(direction))
                    self.pattern.append((direction,thisType)) # Voeg type 1 of 2 toe aan pattern

                    direction = 'f'

                    print 'new direction: ',direction

            else: # No wall to the left or to the right

                print 'no wall'
		#if self.initialOrientation == None:
		 #   self.pattern = list()
                  #  direction = 'f'
                   # self.initialOrientation = None
                    #walls = [0,0,0,0]
		    #continue


		self.wall = None
                
                result = self.trackOneTile(None)
                if not result:

                    walls[0] = 1
                    
                    thisType = self.determineTileType(walls,self.determineRelativeOrientation(direction))
                    self.pattern.append((direction,thisType))
                    
                    #self.continueDrivingBack()
                    #self.turnLeft() # Turn to the left and align right, since aligning with the right wall is more precise

                    self.alignRight(self.checkDistanceRight())

                    print 'driven backward, turned left, aligned right'
                    
                    result = self.trackOneTile(None)

                    if not result: # We know we are on type 1, so there shouldn't be a wall in front of us after having turned to the left
                        print 'The robot should begin next to a wall'
                        return

                    direction = 'l'

                    print 'new direction: ',direction

                else:

                    thisType = self.determineTileType(walls,self.determineRelativeOrientation(direction))
                    self.pattern.append((direction,thisType)) # Add type 0

                    direction = 'f'

                    print 'new direction: ',direction
                    

            print 'pattern: ', self.pattern
	    
            (position,initialOrientation) = self.checkPattern() # This should retrun (0,?) when no match was found and ((1,3),'E') if there is a match; initialOrientation can be deduced from the actual map
            
	    possiblePaths = self.matcher.getPaths()
	    pathsToSend = ""
	    for i in range(len(possiblePaths)):
		if (i==0) and (len(possiblePaths[i]) <= 1):
		    break
		else:
		    if (i==len(possiblePaths)-1):
			pathsToSend += str(possiblePaths[i])
		    else:
			pathsToSend += str(possiblePaths[i]) + "$"
	    if len(pathsToSend)==0:
		pathsToSend = "[]"
	    if self.connection:
                # Send current position + remaining path
                self.connection.sendMessage('drawPath: ' + pathsToSend)

            if position:

                print 'patternMachter returned: ' + str(position)

                posOr = self.determinePositionOrientationFromPattern(position,initialOrientation,direction)
                
                self.position = posOr[0]
                self.orientation = posOr[1]

                print 'I found myself on posOr: ', posOr
                
                rowMajor = self.getRowMajor()
                res = self.client.postPosition(rowMajor,self.orientation)
                while (not res):
                    res = self.client.postPosition(rowMajor,self.orientation)
                positions = self.sendPositions()

		discoveredSymbols = self.client.getAllDiscoveredSymbols()
                self.world.updateSymbols(discoveredSymbols)
                
                # Hier een determineNearestGoal
                path = self.world.determineNearestGoal(self.position, positions)
                
                self.path = path[1:]
                if self.connection:
                    self.connection.sendMessage('-- Position and orientation found: '+ str(posOr[0]) + ', ' + posOr[1])
		    self.connection.sendMessage('-- Nearest goal: '+ str(path[-1]))

                return 1

            else:

                if initialOrientation == 'RESET': # Robot has constructed a wrong path, the pattern matcher forces to reset.

                    if self.connection:
                        self.connection.sendMessage('-- The robot has constructed a non-existent path. The current path was reset.')

                    self.pattern = list()
                    direction = 'f'
                    self.initialOrientation = None
                    walls = [0,0,0,0]

	return 0

            
    def checkPattern(self):
        # Methode uit World van Raf en Ngoc-Lan aanroepen met EERSTE ELEMENT uit self.pattern er NIET bij
        # return self.world.checkPattern(self.pattern[1:])
        if len(self.pattern) == 1:
            return (0,0)
        (direction,tile) = self.pattern[-1]
        (position,initialOrientation) = self.matcher.addTile(tile[0],tile[1],direction)
        if (not position) or (len(initialOrientation) == 0):
            return (0,0)
        else:
            return (position,initialOrientation)
        
 

    def determineRelativeOrientation(self,lastMove):

        directions = ['f','r','b','l']
        nbTurns = 0
        
        for tup in self.pattern:

            direction = tup[0]
            nbTurns += directions.index(direction)

        nbTurns += directions.index(lastMove)
        print 'number of turns so far: ', nbTurns
        nbTurns = (nbTurns)%4
        print 'equivalent number of turns so far: ', nbTurns

        orientations = ['N','E','S','W']
        
        return orientations[(orientations.index(self.initialOrientation) + nbTurns)%4]

    def determineTileType(self,walls,orientation):
        # Determine this tile's type, given the robot is oriented in the given orientation and has seen the given walls

        orientations = ['N','E','S','W']

        nbWalls = sum(walls)

        if (nbWalls == 0): # Type 0
            return '0N'
        elif (nbWalls == 1): # Type 1
            return '1' + orientations[(orientations.index(orientation)+walls.index(1))%4]
        elif (nbWalls == 2): # Type 2 or 3
            thisType = ''
            for i in range(len(walls)):
                if walls[i]:
                    if walls[i-1]:
                        thisType = '3' # Two walls next to each other: Type 3
                        break
            if thisType == '3':
                nordWall = (orientations.index(orientation)+i)%4 # Find the orientation of the northern wall
                return '3' + orientations[nordWall]
            else: # Type 2
                eastWall = (orientations.index(orientation)+walls.index(1))%4 # Find the orientation of the eastern wall
                return '2' + orientations[(eastWall-1)%4]
        elif (nbWalls == 3): # Type 4
            noWall = (orientations.index(orientation)+walls.index(0))%4 # Find the orientation of the side with no wall
            return '4' + orientations[(noWall-2)%4] # Type 4 has its side with no wall S
        else:
            print 'Robot has indicated 4 walls in determineTileType'
            return 0 # This should raise an error
        

    def determinePositionOrientationFromPattern(self, position, initialOrientation, currentDirection):

        orientations = ['N','E','S','W']
        orientation = (orientations.index(initialOrientation)+orientations.index(self.determineRelativeOrientation('f'))-orientations.index(self.initialOrientation))%4 # Dummy 'F'; this gives the actual orientation on the last tile of self.pattern

        print 'orientation on one to last tile: ' + orientations[orientation]

        directions = ['f','r','b','l']
        direction = directions.index(currentDirection) # the last direction the robot moved in

        print 'moved to last tile in direction: ' + currentDirection
        
        orientationAfterMoving = (orientation+direction)%4

        print 'so orientation after moving is: ' + orientations[orientationAfterMoving]

        (i,j) = position

        if orientationAfterMoving == 0: # N
            i -= 1
        elif orientationAfterMoving == 1: # E
            j += 1
        elif orientationAfterMoving == 2: # S
            i += 1
        elif orientationAfterMoving == 3: # W
            j -= 1

        position = (i,j)
        orientation = orientations[orientationAfterMoving]

        return (position,orientation)
    


    def adaptOrientation(self, newOrientation):
        
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
		self.continueDrivingBack(0.5)
                self.turnRight(False)
                deltaOrientation = 0

            elif self.wall == 'right':
                self.turnLeft()
		self.continueDrivingBack(0.5)
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
        
        while True:	#(len(self.path) >= 1):
            
            if (not self.continueExecuting()):
                break

            if self.connection:
                # Send current position + remaining path
                self.connection.sendMessage('drawPath: ' + str([self.position]+self.path))

	    if len(self.path)>=1:
		newPosition = self.path[0]
                self.path = self.path[1:]
                deltaY = newPosition[0] - self.position[0]
                deltaX = newPosition[1] - self.position[1]
                delta = (deltaX,deltaY)
                self.adapt(delta)
	        self.wall = None

                # Remember current position for common wall detection
	        previousPosition = self.position
	        # update position
	        self.position = newPosition

                # Already send position to server so that we can detect an image.
	        rowMajor = self.getRowMajor()
                res = self.client.postPosition(rowMajor,self.orientation)
                while (not res):
                    res = self.client.postPosition(rowMajor,self.orientation)

		# Unknown image is coming!
                if newPosition == self.world.goal:

                    move = self.blindMove(previousPosition,0.8*distanceOneTile)
                
                    if not move:
                        break

                    move = self.deterministicMove()
                
                    if not move:
                        break

		    self.world.removeFromUnknownImagePositions(self.position)
            
                else:
                    move = self.blindMove(previousPosition)
                
                    if not move:
                        break
	
	    else:
		newPosition = self.position
		self.continueDrivingBack(0.5)
                move = self.deterministicMove()
                
                if not move:
                    break

		self.world.removeFromUnknownImagePositions(self.position)

            

            # Now, update own and other positions to GUI
            if self.connection:
            	self.connection.sendMessage('position: ' + str(self.position))
            positions = self.sendPositions()

	    discoveredSymbols = self.client.getAllDiscoveredSymbols()
            updatedSymbols = self.world.updateSymbols(discoveredSymbols)          

            if self.connection:
                self.connection.sendMessage('Update World: '+updatedSymbols)

            # If we reached our goal
            if (len(self.path) < 1):
                print "goal reached, so determineNearestGoal()"
		path = self.world.determineNearestGoal(self.position, positions)
		if len(path) != 0:
		    self.path = path[1:]

            # Check if current goal is still a goal and no team has come nearer
	    elif not self.world.checkPathForEnemies(self.path, positions): 
                print "Someone else has come closer to my goal, so determineNearestGoal()"
		path = self.world.determineNearestGoal(self.position, positions)
		if len(path) != 0:
		    self.path = path[1:]

            # No more images to discover.
	    if (len(self.world.unknownimagepositions) == 0):
		self.setStop()
		self.connection.sendMessage('drawPath: ' + str([]))
	        self.connection.sendMessage('finished')
		break                   

    def execute(self):
	global stopp
	
	self.sendMap()

        while True:
            if not self.continueExecuting():
                break
            self.roaming()
            self.traveling()


     	stopp =0

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
        positions = self.client.getAllRobotsPositions()
        self.connection.sendMessage('teams: ' + positions)
	return positions
        
    def sendMap(self):
	global mapSending
	if self.connection:
	    b = str(os.path.getsize('/home/pi/Desktop/peno/Auto_drive/kaart.txt'))
            self.connection.sendMessage('World'+':'+b)
        
        while (not mapSending):
            time.sleep(0.2)

	mapSending = 0
                
        self.connection.sendMap()

    def testDistL(self):
	i = 1
	while(i<20):
	    print self.checkDistanceLeft()
	    i +=1

    def testDistR(self):
	std = 5
	while (std>1.5):
	    result1 =  self.checkDistanceRight()
            result2 =  self.checkDistanceRight()
	    result3 =  self.checkDistanceRight()
	    result4 =  self.checkDistanceRight()
            result5 =  self.checkDistanceRight()
	    result6 =  self.checkDistanceRight()

	    result = [result1,result2,result3,result4,result5,result6]
            std = np.std(result)
	
