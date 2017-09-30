import thread
from threading import Thread
import time
import os
import Queue
import socket
import random
import select

global s
global t

global send
send = 0
global command
command = ''
global picture
picture = 0
global contentLength



class Server():

    def initConnection(self):
        global s
        global t
        global send
        global command
        global picture
        
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        host = ''     # The hostname of the server
        port = 2000                     # The random port used by the server
        s.bind((host,port))
        print "Listening as " + host + " on port " + str(port)
        s.listen(2)

        while True:
            
            try:
                self.client,self.addr = s.accept()
                self.client.setblocking(0)
                # Hier een andere zend socket maken?
                print "Connected"
                
                while True:

                    ready = select.select([self.client,],[self.client,],[])

                    if ready[0]:

                        #print "ready[0]" 
                        data = self.receiveInfo()
                        t.add(data)

                    else:

                        #print "ready[1]"
                        if picture:
                            print "Send Picture"
                            self.client.sendall("Send Picture")
                            result = self.receivePicture()
                            picture = 0
                            if not result:
                                self.client.close() # Misschien meer doen hier?
                                break
                            
                        elif send:
                            print "Send Command: " + command
                            self.client.sendall(str(command))
                            send = 0
                            command = ""

            except KeyboardInterrupt:
                
                print "Stop"
                break

##            except:
##
##                print "Stop"
##                break
                
        self.cleanup()

    def receiveInfo(self):
    
        try:
            data = self.client.recv(4096)
#            print "data received: " + data
        except:
            print "No data!"
            data = ''
        return data


    def receivePicture(self):

        client,addr = s.accept()
        client.setblocking(0)

 #       client = self.client

        time.sleep(0.2)

        print "in receivePicture"
        print "contentLength: " + contentLength
        
        ready = select.select([client,],[],[])

        print "client is ready to read from: "+str(ready)

        data = ''
        
        timeOut = 5
        currentTime = time.time()

        with open(r'img1TEST.jpg', 'wb') as file_to_write:

            bytesReadUpToNow = 0
            
            while bytesReadUpToNow < int(contentLength):
                #try:
                received = client.recv(1)
                data += received
                bytesReadUpToNow += len(received)
                #print "bytesReadUpToNow: " + str(bytesReadUpToNow)
                #except:
#                    print "except"
#                    ready = select.select([],[self.client,],[])
#                    self.client.sendall('imrecfail')
#                    return 0

            
                if time.time() - currentTime > timeOut:
                    print "timeOut"
                    ready = select.select([],[client,],[])
                    client.sendall('imrecfail')
                    return 0

            print "bytesReadUpToNow" + str(bytesReadUpToNow)

            file_to_write.write(data)
            print 'data weg geschreven'

            file_to_write.close()
    
        os.remove(r'img1ontvangen.jpg')
        os.rename(r'img1TEST.jpg',r'img1ontvangen.jpg')


        client.close()
        
        ready = select.select([],[self.client,],[])
        self.client.sendall('imRecResult')
        
        return 1

##        try:
##            result = imrec.detectImage(r'tijdelijk/img1.jpg')
##            ready = select.select([],[self.client,],[])
##            self.client.sendall(result)
##            return 1
## 
##        except:
##            ready = select.select([],[self.client,],[])
##            self.client.sendall('imrecfail')
##            return 0
        

    def cleanup(self):
        global s
        global t

        if self.client:
            self.client.close()
            
        t.stop()
        t.join()
        
        s.close()



class ProcesThread(Thread):

    def __init__(self,ui):
        super(ProcesThread,self).__init__()
        self.running = True
        self.Q = Queue.Queue()
        self.ui = ui

    def add(self,data):
        newData = data.split("/")
        for d in newData:
            self.Q.put(d)

    def stop(self):
        self.running = False

    def run(self):
        q = self.Q

        while self.running:
            
            try:
                value = q.get(block = True,timeout = 1)
                ui.processInfo(value)
                
            except Queue.Empty:
                print "."

        # Info of what is left in the queue when stopped               
        if not q.empty():
            print "Elements left in the queue:"
            
            while not q.empty():
                print q.get()

class UI:

    def processInfo(self, value):
        global picture
        global contentLength

        print "processInfo"
        
        if value[0:5] == 'imrec':
            print value
            picture = 1
            contentLength = value[6:]
            return
        
        time.sleep(random.randint(1,9)/10.0)
        print value


ui = UI()
t = ProcesThread(ui)
t.start()
server = Server()
thread.start_new_thread(server.initConnection,())
inp = raw_input()
send = 1
command = 'auto'
