# -*- coding: cp1252 -*-

from BaseHTTPServer import BaseHTTPRequestHandler
from urlparse import parse_qs


# TODO  updateWorld() test
#       Get request : voorhand gekende figuren horen hier niet bij
class MyHandler(BaseHTTPRequestHandler):
    print "connected"
    global acceptableNames
    global acceptableShapes
    global acceptableColors
    acceptableNames = ['ijzer', 'blauw', 'koper','paars','rood','groen','brons','geel','indigo','zilver','goud','platinum']
    acceptableShapes = ['circle', 'star', 'triangle', 'square']
    acceptableColors = ['green','red','yellow','purple','blue']
    global shapes
    shapes = []

    
    def do_GET(self):
  
        try:
            request = self.path[1:].split("/")
            command = request[0]
            message = ""
            if(len(request) == 1):
                
                if(command == "name"):
                    self.send_response(200)
                    self.end_headers()
                    fileName = command
                    textFile = open(fileName + ".txt",'r')
                    message = textFile.read().replace('\n', '')
                    self.wfile.write("Your name is " + message + "\n")
                                
                elif(command == "world"):
                    self.send_response(200)
                    self.end_headers()
                    fileName = command
                    textFile = open(fileName + ".txt", 'r')
                    message = textFile.read()
                    self.wfile.write(message + "\n")
                    
                else:
                    self.send_response(400)
                    self.end_headers()  
                    self.wfile.write("The given command is incorrect" + "\n")


            elif(len(request) == 2):               
                                
                if(command =="position"):
                    fileName = self.path[1:]
                    # /position/<team>
                    if(request[1] != "all" and request[1] in acceptableNames):
                        self.send_response(200)
                        self.end_headers()
                        textFile = open(fileName + ".txt", 'r')
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
                        self.wfile.write(allpositions + "\n")
                    else:
                        #print 'in invalid team'
                        self.send_response(400)
                        self.end_headers()  
                        self.wfile.write("Invalid team: " + request[1] + "\n")
                elif(command == "symbol"):
                    self.send_response(200)
                    self.end_headers()
                    global shapes
                    text =""
                    for x in shapes:
                        if(x['finished'] == 1):
                            text = text + x['position'] + x['orientation'] + x['color'] + "_" + x['shape'] + " "

                    self.wfile.write(text)
                elif(command == "score"):
                    stringToPrint = ""
                    for x in acceptableNames:
                        if(int(tryDictionary[x]) > 0):
                            stringToPrint = stringToPrint + x + str(scoreDictionary[x]) + " "
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(stringToPrint)
                    
                else:
                    self.send_response(400)
                    self.end_headers()  
                    self.wfile.write("The given command is incorrect" + "\n")
            else:
                self.send_response(400)
                self.end_headers()  
                self.wfile.write("The given command is incorrect" + "\n")

        except IndexError:
            self.send_response(500)
            self.end_headers()
            self.wfile.write("Server Error" + "\n")
            
            
    def do_POST(self):
        try:
            global acceptableNames
            request = self.path[1:].split("/")
            command = request[0]
            #print request
            #print command    
            
            if(len(request) == 1):
                
                if(command == "name"):

                    self.send_response(200)
                    self.end_headers()
                    fileName = command
                    postvars = self.parse_POST()
                    parameters = postvars.keys()
                        
                    textFile = open(fileName + ".txt", 'w')
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
                    #print parameters

                    try:
                        fileName = self.path[1:]
                        #print 'check team'
                        if(request[1] in acceptableNames):

                            orientation = self.get_Orientation(parameters[0])
                            position = self.get_Position(parameters[0])
                        
                            ValidOrientations = ['N','E','S','W','?']
                            # print 'check orientation'
                            if(orientation in ValidOrientations):
                                #print 'check position'
                                #print position =="?"
                                #print (int(self.get_maxPosition()) > int(position))
                                if((position == "?")  or (int(self.get_maxPosition()) > int(position))):
                                    #print 'check position'

                                    self.send_response(200)
                                    self.end_headers()
                                    textFile = open(fileName  + ".txt", 'w')
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
                    except IndexError:
                        self.send_response(400)
                        self.end_headers()
                        self.wfile.write("The given command is incorrect" + "\n")

                elif (command == "symbol"):
                    self.postSymbol(request)
                else:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write("The given command is incorrect" + "\n")

            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write("The given command is incorrect" + "\n")
    
                
        except IndexError:
                self.send_response(500)
                self.end_headers()
                self.wfile.write("Server Error" + "\n")

    def postSymbol(self, request):
        global acceptableShapes
        global acceptableColors
        agent = self.parse_USER_AGENT()
        postvars = self.parse_POST()
        parameters = postvars.keys()
        # Correct team?
        if (agent in acceptableNames):
            orientation = self.get_Orientation(request[1])
            ValidOrientations = ['N','E','S','W']
            
            # Correct orientation?
            tryDictionary[agent] = int(tryDictionary[agent]) + 1
            if(orientation in ValidOrientations):   
                position = int(self.get_Position(request[1]))

                # Correct position?
                if (position >= 0 and position < self.get_maxPosition() - 1):
                        
                    lastPosition = open("position/" + agent + ".txt", 'r')
                    lastPosition = lastPosition.read()
                    lastposition = lastPosition[:-1]
                    
                    # Given position is last posted positoin?
                    if (lastposition == (request[1])[:-1]):
                        # list of all shapes with color in format color_shape
                        listImages = []
                        for elem in shapes:
                            image = elem['color'] + "_" + elem['shape']
                            listImages.append(image)
 
                        # does the given image exist?
                        if (self.isSymbolOnTile(position)):
                        
                            index = 0
                            for x in shapes:
                                if (str(position) == x['position']):
                                    break
                                else:
                                    index += 1
                            color = parameters[0].split("_")[0]
                            shape = parameters[0].split("_")[1]
                            if(not(color in acceptableColors)):
                                self.send_response(400)
                                self.end_headers()
                                self.wfile.write("Invalid Color: " + color)
                                return
                            
                            if(not(shape in acceptableShapes)):
                                self.send_response(400)
                                self.end_headers()
                                self.wfile.write("Invalid Shape: " + shape)
                                return

                            # TOOLATE?
                            if((shapes[index])['finished'] == 1):
                                self.send_response(200)
                                print "TOOLATE"
                                self.end_headers()
                                self.wfile.write("TOOLATE")
                            else:
                                guess = parameters[0].split("_")
                            
                                if (guess[0] == (shapes[index])['color'] and guess[1] == (shapes[index])['shape']):
                                    self.send_response(200)
                                    self.end_headers()
                                    tries = (shapes[index])[agent]
                                    print "POINTS"
                                    if(tries == 0):
                                        scoreDictionary[agent] += 1
                                        self.wfile.write("1.0")
                                    elif(tries == 1):
                                        scoreDictionary[agent] += 0.5
                                        self.wfile.write("0.5")
                                    else:
                                        self.wfile.write("0.0")
                                    (shapes[index])['finished'] = 1
                                    self.updateWorld(position, orientation, color, shape)
                  
                                else:
                                    self.send_response(200)
                                    self.end_headers()
                                    print "WRONG"
                                    shapes[index][agent] = int((shapes[index])[agent]) + 1
                                    self.wfile.write("WRONG")   
                        else:
                            self.send_response(400)
                            self.end_headers()
                            self.wfile.write("No symbol at: " + request[1])
                                                             
                    else:
                        self.send_response(400)
                        self.end_headers()
                        self.wfile.write("Robot not on tile: " + request[1])
                else:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write("Invalid position: " + str(position))
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write("Invalid orientation: " + str(orientation))
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write("Invalid team :" + agent)

    def updateWorld(self, position, orientation, color, shape):
        worldFile = open("world.txt", 'r')
        oldWorld = worldFile.read()
        worldFile.close()
        listLines = oldWorld.split("\n")
        print listLines
        newWorld = ""
        newShape = color + "_" + shape
        for line in listLines:
            if(newShape in line):
                newWorld = newWorld + "\n" + str(position) + orientation +"image/" + newShape 
            else:
                newWorld = newWorld + "\n" + line
        worldFile = open("world.txt", 'w')
        worldFile.write(newWorld)
        worldFile.close()
            
        
    def listToString(self, array):
        string = ""
        for i in array :
            string = string + i + "\n"

        return string[:-1]
    def isSymbolOnTile(self, position):
        global shapes
        for x in shapes:
            if(x['position'] == str(position)):
                return True

        return False
    
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

# TODO enkel figuren  die nog niet gekend zjn
mapFile = open("correctWorld.txt",'r')
mapString = mapFile.read()
splitMap = mapString.split("\n")

for line in splitMap:
    if ("images/" in line):
        info = line.split("images/")
        if "#" not in info[0]:
            dictionair ={}
            
            posAndOr = info[0]
            image = info[1].split(".")
            image = image[0]

            position = posAndOr[:-1]
            orientation = posAndOr[-1]

            color = image.split("_")[0]
            shape = image.split("_")[1]

            dictionair = {'color' : color, 'shape' : shape, 'position' : position, 'orientation':orientation, 'finished' : 0}

            for team in acceptableNames:
                dictionair.update({team: 0})
                
            global shapes
            shapes.append(dictionair)

shapesAlreadyKnown = []
mapFile = open("world.txt",'r')
mapString = mapFile.read()
splitMap = splitMap = mapString.split("\n")
for line in splitMap:
    if("images/" in line and "?" not in line):
        info = line.split("images/")
        if "#" not in info[0]:
            tmp = {}
            posAndOr = info[0]
            image = info[1].split(".")
            image = image[0]

            position = posAndOr[:-1]
            orientation = posAndOr[-1]

            color = image.split("_")[0]
            shape = image.split("_")[1]

            tmp = {'color' : color, 'shape':shape}

            shapesAlreadyKnown.append(tmp)

print shapesAlreadyKnown

for tmp in shapesAlreadyKnown:
    for fig in shapes:
        if( fig['color'] == tmp['color'] and fig['shape'] == tmp['shape']):
            fig['finished'] = 1

print shapes

global scoreDictionary
scoreDictionary = {}
for team in acceptableNames:
    scoreDictionary.update({team: 0})

global tryDictionary
tryDictionary = {}
for team in acceptableNames:
    tryDictionary.update({team: 0})

        

