import socket

global HOST
HOST = "192.168.43.129"                         # the ip-address of the server
global PORT 
PORT = 9000


'initialize connection'
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST,PORT))
print "connected"
s.sendall("-- werken nondedju")
s.setblocking(0)
isAlive = True
