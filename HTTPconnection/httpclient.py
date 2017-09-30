# -*- coding: utf-8 -*-
import httplib
import re
from urllib import *



class Client:

    def __init__(self, ip="192.168.43.197", port=8080):
        self.ip = ip
        print "ip: " + ip
        self.port = port
        print "port: " + str(port)
        self.setConnection()
        self.postPosition('?','?')
        

    # OK
    def setConnection(self):
        print "Connecting ..."
        self.conn = httplib.HTTPConnection(self.ip,self.port)
        print "Connected to server"

    # TODO

    def getName(self):
        self.conn.request("GET","/name","")
        response = self.conn.getresponse()
        data = response.read()
        print(data)

    # OK  
    def getWorld(self):
        self.conn.request("GET","/world","")
        response = self.conn.getresponse()
        data = response.read()
        kaart = open("kaart.txt","w")
        kaart.write(data)
        kaart.close()
        print data

    # OK
    def getPositionOfGivenTeam(self,Team):
        self.conn.request("GET","/position/" + Team,"")
        response = self.conn.getresponse()
        data = response.read()
        data = data.split()
        print data
        if (data[0] == "Invalid")or (data[0] == "??"):
            return ""
        else:
            print data[0]
            return data[0]
        
       
        
    # OK
    # Hier steken wij zelfs al in se 
    def getAllRobotsPositions(self):
        self.conn.request("GET","/position/all","")
        response = self.conn.getresponse()
        data = response.read()
        data = self.splitData(data)
        if len(data) == 0:
            return "()"
        else:
            print data
            newData = str()
            r = re.compile("([a-z]+)([A-Z0-9]+)")
            for i in data:
                m = r.match(i)
                newData += m.group(1) + " " + m.group(2) + " "
            print newData
            if (len(newData) == 0):
                return "()"
            
            return '('+newData+')'
        

    # OK 
    def postName(self,Name):
        head = {"Content-Type" : "application/x-www-form-urlencoded", "Accept" : "text/plain"}
        params = urlencode({Name:""})
        #print str(params)
        self.conn.request("POST", "/name", params, head)
        response = self.conn.getresponse()
        data = response.read()
        print data
       

    def postPosition(self,Position,Orientation, Team = "ijzer"):
        head = {"Content-Type" : "application/x-www-form-urlencoded", "Accept" : "text/plain"}
        PosOr = str(Position) + str(Orientation)
        params = urlencode({PosOr:""})
        #print str(params)
        self.conn.request("POST","/position/" + Team,params,head)
        response = self.conn.getresponse()
        data = response.read()
        data = data.split()
        if data[0] == "OK":
            return True;
        else:
            return False;

    def postSymbol(self,Position,Orientation,image, Team = "ijzer"):
        head = {"Content-Type" : "application/x-www-form-urlencoded", "Accept" : "text/plain", "User-Agent" : Team}
        PosOr = str(Position) + str(Orientation)
        params = urlencode({image:""})
        self.conn.request("POST","/symbol/"+ PosOr,params,head)
        response = self.conn.getresponse()
        data = response.read()
        data = self.split(data)
        if data[0] == "OK":
            return data[1]
            # 1.0,0.5,0.0,WRONG,TOOLATE
            # If TOOLATE, a "GET /symbol/all" request should be done here.
        else:
            return False

    def getAllDiscoveredSymbols(self):
        # Undiscovered symbols and symbols that were known upfront aren’t listed
        self.conn.request("GET","/symbol/all","")
        response = self.conn.getresponse()
        data = response.read()
        data = self.splitData(data)
        return data

    def getAllScores(self):
        self.conn.request("GET","/score/all","")
        response = self.conn.getresponse()
        data = response.read()
        data = self.splitData(data)
        if len(data) == 0:
            return []
        else:
            print data
            newData = str()
            r = re.compile("([a-z]+)([0-9.]+)")
            for i in data:
                m = r.match(i)
                newData[m.group(1)] = float(m.group(2))
            print newData
            if (len(newData) == 0):
                return []
            
            return newData 


    def splitData(self,data):
        # separated by a space, tab or newline
        data = data.splitlines()
        result = list()
        for el in data:
            d = [splits for splits in el.split("\t") if splits is not ""]
            for da in d:
                result += da.split()
        return result
                
    
    def closeConnection(self):
        self.conn.close()
