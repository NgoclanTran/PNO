import socket
import sys

def fotoZenden():
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind(("",188))
	s.listen(10)

	conn, address = s.accept()
	while(1):
		f=open ("img1.jpg","rb")
		l = f.read(1024)
		while(l):
			conn.send(l)
			l =f.read(1024)
		
