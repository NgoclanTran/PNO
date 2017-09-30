import socket
import sys

class Connection:

    def __init__(self):
        'initialize connection'
        HOST = ''                  # Symbolic name meaning all available interfaces
        PORT = 184                          # Arbitrary non-privileged port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print "socket created"
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((HOST, PORT))
        print "socket binded"
        self.socket.listen(1)
        print "listening ..."
        self.conn, self.addr = self.socket.accept()
        print 'Connected by', self.addr

    def send(self, typ, data):
        if typ == "message":
            self.conn.sendall(data)
        if typ == "component":
            self.conn.sendall(data)

    def sendMessage(self, data):
        self.send("message", data)

    def sendData(self, component, data):
        self.send("component", data)

    def sendImage(self):
       # self.sendMessage("afbeelding")
        
        f=open ("img1.jpg", "rb")
        #belangerijk da de afbeelding in de workingdirectory wordt opgeslagen
        #en exact img1.jpg wordt genoemd.
        l = f.read(1024)
        while (l):
            self.conn.send(l)
            l = f.read(1024)      

    def receive(self):
        self.received = self.conn.recv(1024)

    def getReceived(self):
        self.receive()
	print str(self.received)
        return self.received

connectiontest = Connection()
#connectiontest.sendMessage("afbeelding")
connectiontest.sendImage()
