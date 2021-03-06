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
host = '192.168.43.129'
global port
port = 2000


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
                continue

            if data == 'auto':
                thread.start_new_thread(self.robot.execute,())

            elif data == 'stopAuto':
                self.robot.setStop()
            
            elif data == 'Send Picture':
                self.connection.sendImage()

            elif data == 'imrecfail':
                self.connection.isAlive = False
                time.sleep(1)
                self.connection = Connection()
                self.connection.send('imrec')

            elif data == "imRecResult":
                cont = 1
                
            else:
                print data


class Robot:

    def __init__(self,connection):
        self.connection = connection

    def execute(self):
        global cont
        

        while not stopp:

            x = random.randint(1,10)
            if x == 1:
                self.connection.send('imrec:'+str(os.path.getsize('img1.jpg')))
                while not cont:
                    time.sleep(0.2)
                cont = 0
            else:
                time.sleep(random.randint(1,9)/10.0)
                self.connection.send("Random number: "+str(random.randint(1000,2000)))

    def setStop(self):
        global stopp
        stopp = 1


class Connection:



    def __init__(self):
        print 'initialize connection'
        global host
        global port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host,port))
        print "connected"
        self.socket.setblocking(0)
        self.isAlive = True

    def send(self,data):

        ready = select.select([],[self.socket,],[])
        self.socket.sendall(data)

    def sendImage(self):
        sk = self.socket

        sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sk.connect((host,port))
        print "image socket connected"
        self.socket.setblocking(0)
        
        ready = select.select([],[sk,],[])
        with open('img1.jpg', 'rb') as file_to_send:
            for data in file_to_send:
                if self.isAlive:
                    sk.sendall(data)
                else:
                    print 'img fail'
                    return 
    
        print 'img sent'
        
c = Controller()
c.main()
