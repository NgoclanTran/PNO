# -*- coding: cp1252 -*-
from BaseHTTPServer import BaseHTTPRequestHandler
from cgi import parse_header, parse_multipart
from urlparse import parse_qs
import time

#TODO
# --> save score
# --> when server close -> delete file of shapes
class MyHandler(BaseHTTPRequestHandler):
    print "connected"
    global acceptableNames
    acceptableNames = ['ijzer', 'blauw', 'koper','paars','rood','groen','brons','geel','indigo','zilver','goud','platinum']

    
    def do_GET(self):
  
        try:
            request = self.path[1:].split("/")
            command = request[0]
            message = ""
            if(len(request) == 1):
                
                if(command == "name"):
                    self.send_response(200)
                    self.end_headers()
                    file = command
                    textFile = open(file + ".txt",'r')
                    message = textFile.read().replace('\n', '')
                    self.wfile.write("Your name is " + message + "\n")
                                
                elif(command == "world"):
                    self.send_response(200)
                    self.end_headers()
                    file = command
                    textFile = open(file + ".txt", 'r')
                    message = textFile.read()
                    self.wfile.write(message + "\n")
                    
                else:
                    self.send_response(400)
                    self.end_headers()  
                    self.wfile.write("The given command is incorrect" + "\n")


            elif(len(request) == 2):               
                                
                if(command =="position"):
                    file = self.path[1:]
                    # /position/<team>
                    if(request[1] != "all" and request[1] in acceptableNames):
                        self.send_response(200)
                        self.end_headers()
                        textFile = open(file + ".txt", 'r')
                        text = textFile.read().replace('\n', '')
                        
                        self.wfile.write(text + "\n")
                    
                                        
                    elif(request[1] == "all"):
                        self.send_response(200)
                        self.end_headers()               
                        allpositions = ""
                        for team in acceptableNames:
                            textFile = open('position/' + team + ".txt", 'r')
                            text = textFile.read().replace('\n', '')
                            if( text != "??"):
                                allpositions = allpositions + team + text + " "     
                        print allpositions  
                        self.wfile.write(allpositions + "\n")
                    else:
                        #print 'in invalid team'
                        self.send_response(400)
                        self.end_headers()  
                        self.wfile.write("Invalid team: " + request[1] + "\n")
                   
                else:
                    self.send_response(400)
                    self.end_headers()  
                    self.wfile.write("The given command is incorrect" + "\n")
            else:
                self.send_response(400)
                self.end_headers()  
                self.wfile.write("The given command is incorrect" + "\n")

        except:
            self.send_response(500)
            self.end_headers()
            self.wfile.write("Server Error" + "\n")
            
            
    def do_POST(self):
        try:
            global acceptableNames
            request = self.path[1:].split("/")
            command = request[0]
            
            if(len(request) == 1):
                
                if(command == "name"):

                    self.send_response(200)
                    self.end_headers()
                    file = command
                    postvars = self.parse_POST()
                    parameters = postvars.keys()
                        
                    textFile = open(file + ".txt", 'w')
                    textFile.write(parameters[0])
                                
                    self.wfile.write("Your new name is " + parameters[0] + "\n")

                else:
                    self.send_response(400)
                    self.end_headers()  
                    self.wfile.write("The given command is incorrect" + "\n")

            elif(len(request) == 2):  
                
                if(command == "position"):
                    postvars = self.parse_POST()
                    parameters = postvars.keys()

                    try:
                        file = self.path[1:]
                        if(request[1] in acceptableNames):

                            orientation = self.get_Orientation(parameters[0])
                            position = self.get_Position(parameters[0])
                        
                            ValidOrientations = ['N','E','S','W','?']
                            if(orientation in ValidOrientations):
                            
                                if((position == "?")  or (int(self.get_maxPosition()) > int(position))):
                                    self.send_response(200)
                                    self.end_headers()
                                    
                                    textFile = open(file  + ".txt", 'w')
                                    textFile.write(parameters[0])
                                    
                                    self.wfile.write("OK" + "\n")
                                else:
                                    self.send_response(400)
                                    self.end_headers()
                                    self.wfile.write("Invalid position: " + position + "\n")
                            else:
                                self.send_response(400)
                                self.end_headers()
                                self.wfile.write("Invalid orientation: " + orientation + "\n")
                        else:
                            self.send_response(400)
                            self.end_headers()
                            self.wfile.write("Invalid team: " + request[1] + "\n")
                    except:
                        self.send_response(400)
                        self.end_headers()
                        self.wfile.write("The given command is incorrect" + "\n")

                if (command == "symbol"):
                    agent = self.parse_USER_AGENT()
                    postvars = self.parse_POST()
                    parameters = postvars.keys()

                    try:
                        if (agent in acceptableNames):
                            
                            orientation = self.get_Orientation(request[1])
                            ValidOrientations = ['N','E','S','W']
                            
                            if(orientation in ValidOrientations):

                                position = self.get_Position(request[1])

                                if (position in range(0,self.get_MaxPosition-1)):

                                    lastPosition = open("position/" + agent + ".txt", 'r')
                                    lastPosition = lastPosition.read()

                                    if (lastPosition == request[1]):

                                        os.chdir("/images")
                                        lijst = glob.glob('*.txt')
                                        os.chdir("..")

                                        if (request[1] in lijst):
                                            
                                            imageFile = open("/images/" + request + ".txt", 'r')
                                            imageFile1 = imageFile.read()
                                            imageFileList = imageFile1.split("\n")
                                            image = imageFileList[0].split("_")
                                            if(len(image) == 2 and image[1] == "finished"):
                                                self.send_response(200)
                                                self.end_headers()
                                                self.send_response("TOOLATE")

                                            guess = parameters[0].split("_")

                                            if (guess[0] == image[0]):

                                                if (guess[1] == image[1]):
                                                    self.send_response(200)
                                                    self.end_headers()
                                                    index = 0
                                                    score = 0
                                                    #TODO : add score to a file
                                                    index = get_IndexOfTeamInList(imageFileList,agent)
                                                    if(index < 0):
                                                        score = 1
                                                        imageFileList = imageFileList[0] + "\n" + "finished"
                                                        imageFile.write(imageFileList)
                                                        self.wfile.write("1.0")
                                                    else:

                                                        nmbrTry = int(imageFileList[index].split(":")[-1])
                                                        if(nmbrTry == 1):
                                                            scoree = 0.5
                                                            imageFileList = imageFileList[0] + "\n" + "finished"
                                                            imageFile.write(imageFileList)
                                                            self.wfile.write("0.5")
                                                        else:
                                                            scoree = 0
                                                            imageFileList = imageFileList[0] + "\n" + "finished"
                                                            imageFile.write(imageFileList)
                                                            self.wfile.write("0.0")
                                                        
                                                else:
                                                    self.send_response(400)
                                                    self.end_headers()

                                                    index = get_IndexOfTeamInList(imageFileList,agent)
                                                    if(index  < 0):
                                                        imageFile1 = imageFile1 + agent + ":1\n"
                                                        imageFile.write(imageFile1)
                                                    else:
                                                        nmbrTry = int(imageFileList[index].split(":")[-1])
                                                        content = agent + ":" + nmbrTry + "\n"
                                                        imageFileList.insert(index, content)
                                                        text = listToString(imageFileList)
                                                        imageFile.write(text)

                                                    self.wfile.write("WRONG")
                                            else:
                                                self.send_response(400)
                                                self.end_headers()

                                                index = get_IndexOfTeamInList(imageFileList,agent)
                                                if(index  < 0):
                                                    imageFile1 = imageFile1 + agent + ":1\n"
                                                    imageFile.write(imageFile1)
                                                else:
                                                    nmbrTry = int(imageFileList[index].split(":")[-1])
                                                    content = agent + ":" + nmbrTry + "\n"
                                                    imageFileList.insert(index, content)
                                                    text = listToString(imageFileList)
                                                    imageFile.write(text)

                                                self.wfile.write("WRONG")
                                        else:
                                            self.send_response(400)
                                            self.end_headers()
                                            self.wfile.write("No symbol at: " + request[1]
                                                             
                                    else:
                                        self.send_response(400)
                                        self.end_headers()
                                        self.wfile.write("Robot not on tile: " + request[1]
                                else:

                                    self.send_response(400)
                                    self.end_headers()
                                    self.wfile.write("Invalid position: " + position
                            else
                                self.send_response(400)
                                self.end_headers()
                                self.wfile.write("Invalid orientation :" + orientation
                        else:
                            self.send_response(400)
                            self.end_headers()
                            self.wfile.write("Invalid team :" + agent
                                
                else:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write("The given command is incorrect" + "\n")

            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write("The given command is incorrect" + "\n")

                
        except:
            self.send_response(500)
            self.end_headers()
            self.wfile.write("Server Error" + "\n")
    def listToString(self, array):
        string = ""
        for i in array :
            string = string + i + "\n"

        return string
            
    def get_IndexOfTeamInList(self, textList , agent):
        index = 0
        for row in textList:
            if(agent in row):
                return index
            index = index + 1
        return -1

    def get_Orientation(self, parameter):
        return parameter[-1]

    def get_Position(self, parameter):
        return parameter[:-1]
    
    def get_maxPosition(self):
        textFile = open("world.txt", 'r')
        temp = textFile.readlines()
        for line in temp:
            if (line[0].isdigit()):
                dimensions = line
                array = dimensions.split(" ")
                maxPosition = int(array[0]) * int(array[1])
                return maxPosition
        return 0

    def parse_POST(self):
       # print "headers",self.headers
        length = int(self.headers['content-length'])
        postvars = parse_qs(self.rfile.read(length), keep_blank_values=1)
        return postvars

    def parse_USER_AGENT(self):
        agent = str(self.headers['user-agent'])
        return agent
    
    def send_response(self, code, message=None):
        """Send the response header and log the response code.
        """

        self.log_request(code) # rode tekst bij de server
        if message is None:
            if self.responses.has_key(code):
                message = self.responses[code][0]
            else:
                message = ''
        if self.request_version != 'HTTP/0.9':

            self.wfile.write("%s %s %s \n" %
                             (self.protocol_version, str(code), message))

