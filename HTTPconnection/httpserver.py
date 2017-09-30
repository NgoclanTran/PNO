from httphandler2 import MyHandler
from BaseHTTPServer import HTTPServer
from SocketServer import ThreadingMixIn



class threadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""
    global acceptableNames
    acceptableNames = ['ijzer', 'blauw', 'koper','paars','rood','groen','brons','geel','indigo','zilver','goud','platinum']
    
def initializeFiles():
    global acceptableNames
    for name in acceptableNames:
        try:
            textFile = open('position/' + name + ".txt", 'w')
            textFile.write("??")
        except:
            textFile = open('position/' + name + ".txt", 'a')
            textFile.write("??")

def parseMap():
    mapFile = open("world.txt",'r')
    mapString = mapFile.read()
    splitMap = mapString.split("\n")

    for line in splitMap:
        if ("images/" in line):
            info = line.split("images/")
            if "#" not in info[0]:
                newName = info[0]
                image = info[1].split(".")
                image = image[0]
                textFile = open("images/" + newName  + ".txt", 'a')
                textFile.write(image + "\n")
                
                
def runServer():
    try:
        server = threadedHTTPServer(('', 8080), MyHandler)
        print 'Starting server, use <Ctrl-C> to stop'
        initializeFiles()
        parseMap()
        server.serve_forever()


    except KeyboardInterrupt:
        print "stopped"
        server.socket.close()
                
            
if __name__ == '__main__':
    runServer()
    
