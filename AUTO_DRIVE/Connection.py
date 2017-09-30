
import socket
import time
import select

global HOST
HOST = "192.168.2.26"                         # the ip-address of the server
global PORT 
PORT = 9200

class Connection:

    def __init__(self):
	global HOST
	global PORT
        'initialize connection'
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((HOST,PORT))
        print "connected"
	self.socket.setblocking(0)
	self.isAlive = True

    def send(self, data):
	ready = select.select([],[self.socket,],[])
        self.socket.sendall(data+"/")
	#time.sleep(1)

    def sendMessage(self, data):
        self.send(data)

    def sendData(self, component, data):
        self.send(data)
        

    def receive(self):
        self.received = self.socket.recv(4096)

    def getReceived(self):
        self.receive()
        return self.received
	
    def sendImage(self):
	sk = self.socket

        sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sk.connect((HOST,PORT))
        print "image socket connected"
        self.socket.setblocking(0)
        
        ready = select.select([],[sk,],[])

        with open('/home/pi/image.jpg', 'rb') as file_to_send:
            for data in file_to_send:
                if self.isAlive:
                    sk.sendall(data)
                else:
                    print 'img fail: not alive'
                    return 
    
        print 'img sent'

    def sendMap(self):
	sk = self.socket

        sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sk.connect((HOST,PORT))
        print "map socket connected"
        self.socket.setblocking(0)
        
        ready = select.select([],[sk,],[])

        with open('/home/pi/Desktop/peno/Auto_drive/kaart.txt', 'rb') as file_to_send:
            for data in file_to_send:
                if self.isAlive:
                    sk.sendall(data)
                else:
                    print 'img fail: not alive'
                    return 
      
        print 'map sent'

        


