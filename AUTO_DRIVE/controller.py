from Connection import * 
from Robot import * 
import threading
from signal import signal, SIGPIPE, SIG_DFL
import time

global httpServerPort
httpServerPort= 4000
global httpServerHost
httpServerHost= '192.168.2.21'
global robot


def auto(connection):
    
    #if (robot.world.goal!= None):
    #	robot.stopStart()
   	exThread = threading.Thread(target=robot.execute)
   	exThread.start()
	signal(SIGPIPE,SIG_DFL)
	
    #else:
#	print 'No goal specified yet!'
#	connection.socket.sendall("--No goal specified yet!/")


def stopAuto():
    robot.setStop()

#aanmaken in robot.py
import sys
def stopExecute(self):
    sys.exit()

def shutdown():
    robot.setStop()
    robot.connection.socket.close()

def forward():
    robot.continueDrivingForward(1)

def alignRight():
    #robot.testDistR()
    robot.alignRight(robot.checkDistanceRight())

def alignLeft():
    #robot.testDistL()
    robot.alignLeft(robot.checkDistanceLeft()) 

def adjustRight():
    #robot.testDistR()
    robot.adjustRight()

def adjustLeft():
    #robot.testDistL()
    robot.adjustLeft() 

       
def backward():
    robot.continueDrivingBack(1)   
            
def stop():
    robot.pauseMotors()
   
def turnLeft():
    robot.turnLeft()
    
def turnRight():
    robot.turnRight()
    
def turnCameraLeft():
    robot.turnCameraLeft()
   
def turnCameraRight():
    robot.turnCameraRight()

def turnCameraFront():
    robot.turnCameraFront()

def sendImage():
    robot.allowSendingImage()

def sendMapAllow():
    robot.allowSena)=="turnCameraRight":
 ():
    print "main controller"
    global robot
    connection = Connection()
    robot = Robot(connection, httpServerHost,httpServerPort)

    while True:
	ready = select.select([connection.socket,],[],[])

        try:
            data = connection.socket.recv(4096)
        except:
            print "No data!"
            continue
        


        #print "data received"
        
        if data:
            
            print "Executing command: " + str(data)
            
            if str(data)=="auto":
                auto(connection)
                
            elif str(data)=="autoStop":
                stopAuto()
                
            elif str(data)=="forward":
                forward()
                
            elif str(data)=="alignRight":
                alignRight()
                
            elif str(data)=="alignLeft":
                alignLeft()

	    elif str(data)=="adjustRight":
                adjustRight()
                
            elif str(data)=="adjustLeft":
                adjustLeft()

                
            elif str(data)=="backward":
                backward()
                
            elif str(data)=="stop":
                stop()
                
            elif str(data)=="turnLeft":
                turnLeft()
                
            elif str(data)=="turnRight":
                turnRight()
                
            elif str(data)=="turnCameraLeft":
                turnCameraLeft()
                
            elif str(data)=="turnCameraRight":
                turnCameraRight()
                
            elif str(data)=="turnCameraFront":
                turnCameraFront()

	    elif str(data)=="shutdown":
		robot.client.postPosition('?','?')
		print "***remove position from server***"

		for i in range(0,10):
		    time.sleep(0.1)
		    print 10-i
		print "*****************KABOOOOOOOOOOM!!!*******************"
                shutdown()
		break

            elif str(data)=="Send Picture":
                sendImage()

	    elif str(data)=="Send Map":
                sendMapAllow()

	 
            elif str(data[0:12])=="resultImRec:":
                robot.setResultImRec(data[12:])
                robot.setNewImRec(1)

            elif str(data[0:12])=="imrecfail":
                robot.connection.isAlive = False
		time.sleep(1)
                connection = Connection()
                robot.connection = connection
                robot.setNewImRec(2)

	    elif str(data[0:12])=="mapfail":
                robot.connection.isAlive = False
		time.sleep(1)
                connection = Connection()
                robot.connection = connection
                robot.setNewImRec(2)


            elif str(data[0:5])=="goal:":
                
                if (data[5]=='('):
                    tup = tuple((int(data[6]),int(data[8])))
                    print str(tup)
                    print tup
                    robot.world = World('kaart.txt')
                    robot.world.setGoal(tup)
		    connection.socket.sendall("-- goal position set./")
                    
                else:
                    robot.world = World('kaart.txt')
		    try:
                        robot.world.setGoal(data[5:]+'.png')
			connection.socket.sendall("-- goal position set./")
		    except:
			connection.socket.sendall("-- ERROR: goal position incorrect./")

                
            
            else:
                data = "FAILED"
            print "Executed command: " + str(data)
            answer = "-- Executed command: " + str(data)
           # connection.socket.sendall(answer+"/")
    #connection.conn.close()

main()