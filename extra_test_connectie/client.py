import select
import thread
import socket
import random
import time
import os

global stopp
stopp = 0
global cont
cont = 0
global host
host = ''
global port
port = 9200


class Controller:

    def __init__(self):

        self.connection = Connection()
        self.robot = Robot(self.connection)

    def main(self):
        global cont
        
        while True:

            conn = self.connection.socket
            
            ready = select.select([conn,],[],[])

            print ready

            try:
                data = conn.recv(4096)
            except:
                print "No data!"
                continue

            if data == 'auto':
                "auto"
                thread.start_new_thread(self.robot.execute,())

            elif data == 'autoStop':
                "stopAuto"
                print "instopauto"
                self.robot.setStop()
            
            elif data == 'Send Picture':
                "Send Picture"
                self.connection.sendImage()
                
            elif data == 'Send Map':
                "Send Picture"
                self.connection.sendMap()
                
            elif data[0:5]=="goal:":
                self.connection.send("-- goal position set./")
                #self.connection.send("refreshMap")

            elif data == 'imrecfail':
                "imrecfail"
                self.connection.isAlive = False
                time.sleep(1)
                self.connection = Connection()
                self.connection.send('ImRec')
                
            elif data == 'mapfail':
                "mapfail"
                self.connection.isAlive = False
                time.sleep(1)
                self.connection = Connection()
                self.connection.send('World')

            elif data == "resultImRec:0":
                cont = 1
                
            else:
                print data


class Robot:

    def __init__(self,connection):
        self.connection = connection
        self.connection.send("-- robot connected")

    def execute(self):
        global cont
        global stopp
        
        print 'Robot executing'
        self.connection.send("-- Roaming")
        self.connection.send('World:'+str(os.path.getsize('kaart.txt'))+'/')

        while not stopp:
            print stopp
            x = random.randint(1,10)
#             if x == 1:
#                 self.connection.send('ImRec:'+str(os.path.getsize('img1.jpg'))+"/")
#                 self.connection.send("-- Traveling")
#                 while not cont:
#                     time.sleep(0.2)
#                 cont = 0
                
            if x == 2:
                position1 = random.randint(1,15)
                position2 = random.randint(1,15)
                self.connection.send("teams: blauw "+str(position1)+"N ijzer "+str(position2)+"N/")
                
            elif x == 3:
                position1 = random.randint(1,24)
                position2 = random.randint(1,24)
                self.connection.send("drawPath: [(1, 2), (1, 3)]$[(2, 1), (2, 2)]$[(4, 1), (4, 2)]/")
                
            elif x == 4:
                score = random.randint(1,10)
                self.connection.send("score "+str(score)+"/")
            
            else:
                time.sleep(random.randint(1,9)/10.0)
                self.connection.send("refreshMap/")
                distance = random.randint(20,100)
                if x > 6:
                    self.connection.send("distance left: "+str(distance)+"/")
                else:
                    self.connection.send("distance right: "+str(distance)+"/")

        print 'Stop executing'

    def setStop(self):
        global stopp
        stopp = 1


class Connection:

    def __init__(self):
        print 'initialize connection'
        global host
        global port
        print host,port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host,port))
        print "connected"
        self.socket.setblocking(0)
        self.isAlive = True

    def send(self,data):

        select.select([],[self.socket,],[])

        print 'Send data: '+data
        self.socket.sendall(data)

    def sendImage(self):
        print "inSendImage"


        sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sk.connect((host,port))
        print "image socket connected"
        self.socket.setblocking(0)
        
        select.select([],[sk,],[])
        with open('img1.jpg', 'rb') as file_to_send:
            for data in file_to_send:
                if self.isAlive:
                    sk.sendall(data)
                else:
                    print 'img fail'
                    return 
    
        print 'img sent'
        
    def sendMap(self):
        print "inSendMap"


        sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sk.connect((host,port))
        print "map socket connected"
        self.socket.setblocking(0)
        
        select.select([],[sk,],[])
        with open('kaart.txt', 'rb') as file_to_send:
            for data in file_to_send:
                if self.isAlive:
                    sk.sendall(data)
                else:
                    print 'map fail'
                    return 
    
        print 'map sent'
        
c = Controller()
c.main()
