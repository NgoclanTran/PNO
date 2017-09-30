import unittest
import httpserver
import threading
import httplib
from urllib import urlencode
import subprocess


#import re


class httpServerTest(unittest.TestCase):

    def setUp(self):
        
        self.conn = httplib.HTTPConnection('localhost',8102)
        

    def testGETName(self):
        # Before send request
        textFile = open("name.txt",'r')
        message = textFile.read().replace('\n', '')
        
        # Send response
        self.conn.request("GET","/name","")
        response = self.conn.getresponse()
        data = response.read()
        self.assertEquals(data, "Your name is ijzer\n")

        # Test if content has changed, after request
        textFile1 = open("name.txt",'r')
        message1 = textFile1.read().replace('\n', '')
        self.assertEquals(message1,message)


    def testGETWorld(self):
        # Before send request
        textFile = open("world.txt",'r')
        message = textFile.read()

        # Send request
        self.conn.request("GET","/world","")
        response = self.conn.getresponse()
        data = response.read()

        # Test if content has changed, after request
        textFile1 = open("world.txt",'r')
        message1 = textFile1.read()
        self.assertEquals(message1,message)

        # Test
        self.assertEquals(message1+"\n", data)
        
           

    def testGETPositionTeam(self):
        
        # Before send request
        textFile = open("position/ijzer.txt",'r')
        message = textFile.read().replace('\n', '')

        # Send request
        self.conn.request("GET","/position/ijzer","")
        response = self.conn.getresponse()
        data = response.read()

        # Test if content has changed, after request
        textFile1 = open("position/ijzer.txt",'r')
        message1 = textFile1.read().replace('\n', '')
        self.assertEquals(message1,message)

        # Test
        self.assertEquals(data, "??\n")

    def testGETPositionTeam_FALSE(self):
        # Before send request
        textFile = open("position/ijzer.txt",'r')
        message = textFile.read().replace('\n', '')

        # Send request
        self.conn.request("GET","/position/foo","")
        response = self.conn.getresponse()
        data = response.read()

        # Test if content has changed, after request
        textFile1 = open("position/ijzer.txt",'r')
        message1 = textFile1.read().replace('\n', '')
        self.assertEquals(message1,message)

        # Test
        self.assertEquals(data, "Invalid team: foo\n")
        

    def testGETPositionALL(self):

        # Send request
        self.conn.request("GET","/position/all","")
        response = self.conn.getresponse()
        data = response.read()
        
        self.assertEquals(data,'\n')

    def testPOSTName(self):
        
        # Before send request
        textFile = open("name.txt",'r')
        message = textFile.read().replace('\n', '')
    
        # Send request
        Name = "newName"
        head = {"Content-Type" : "application/x-www-form-urlencoded", "Accept" : "text/plain"}
        params = urlencode({Name:""})
        self.conn.request("POST", "/name", params, head)
        response = self.conn.getresponse()
        data = response.read()

        # After request
        textFile1 = open("name.txt",'r')
        message1 = textFile1.read().replace('\n', '')
        self.assertNotEqual(message, message1)

        # Test
        self.assertEqual(data, "Your new name is "+ Name+"\n")

    def testPOSTPositionTeam(self):
        # Before send request
        textFile = open("position/ijzer.txt",'r')
        message = textFile.read().replace('\n', '')

        # Send request
        head = {"Content-Type" : "application/x-www-form-urlencoded", "Accept" : "text/plain"}
        Team = "ijzer"
        PosOr = "1N"
        params = urlencode({PosOr:""})
        #print str(params)
        self.conn.request("POST","/position/" + Team,params,head)
        response = self.conn.getresponse()
        data = response.read()

        # Test if content has changed, after request
        textFile1 = open("position/ijzer.txt",'r')
        message1 = textFile1.read().replace('\n', '')
        self.assertNotEquals(message1,message)

        # Test
        self.assertEquals(data, "OK\n")


    def testPOSTPositionTeam_FALSE_Position(self):
        # Before send request
        textFile = open("position/ijzer.txt",'r')
        message = textFile.read().replace('\n', '')

        # Send request
        head = {"Content-Type" : "application/x-www-form-urlencoded", "Accept" : "text/plain"}
        Team = "ijzer"
        PosOr = "1000N"
        params = urlencode({PosOr:""})
        #print str(params)
        self.conn.request("POST","/position/" + Team,params,head)
        response = self.conn.getresponse()
        data = response.read()

        # Test if content has changed, after request
        textFile1 = open("position/ijzer.txt",'r')
        message1 = textFile1.read().replace('\n', '')
        self.assertEquals(message1,message)

        # Test
        self.assertEquals(data, "Invalid position: 1000\n")

    def testPOSTPositionTeam_FALSE_Orientation(self):
        # Before send request
        textFile = open("position/ijzer.txt",'r')
        message = textFile.read().replace('\n', '')

        # Send request
        head = {"Content-Type" : "application/x-www-form-urlencoded", "Accept" : "text/plain"}
        Team = "ijzer"
        PosOr = "0P"
        params = urlencode({PosOr:""})
        #print str(params)
        self.conn.request("POST","/position/" + Team,params,head)
        response = self.conn.getresponse()
        data = response.read()

        # Test if content has changed, after request
        textFile1 = open("position/ijzer.txt",'r')
        message1 = textFile1.read().replace('\n', '')
        self.assertEquals(message1,message)

        # Test
        self.assertEquals(data, "Invalid orientation: " + "P"+"\n")

    def testPOSTWrongCommand(self):

        # Send request
        head = {"Content-Type" : "application/x-www-form-urlencoded", "Accept" : "text/plain"}
        Team = "ijzer"
        PosOr = "0P"
        params = urlencode({PosOr:""})
        #print str(params)
        self.conn.request("POST","/wrongcommand" + Team,params,head)
        response = self.conn.getresponse()
        data = response.read()

        # Test
        self.assertEquals(data, "The given command is incorrect\n")

    
        
        
        
        
        
        
def main():
    
    unittest.main()

if __name__ == '__main__':
    serverThread = threading.Thread(target = httpserver.runServer())
    serverThread.start()
    main()


        
        
        
