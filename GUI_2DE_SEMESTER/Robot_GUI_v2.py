# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Robot_GUI_v2.ui'
#
# Created: Mon Nov 10 13:04:55 2014
#      by: PyQt4 UI code generator 4.11.1
#
# WARNING! All changes made in this file will be lost!

import os
import select
import shutil
import socket
import sys
import threading
import time

from PIL import ImageDraw, ImageFont, Image
from PyQt4 import QtCore, QtGui,Qt

from ImRec import ImRec
from ProcesThread import ProcesThread
from makeMapV2 import makeMap


#zit bij in eclipse pydev dus niet importeren
#import sys
#import matplotlib.pyplot as plt
#import time
#from PIL import *

#defining globals
global s
global t
global imrec
global pic
global Form
global picture
picture = 0
global kaart
kaart = 0
global send
send = 0
global command
global closing
closing = False
global distanceRight
global distanceLeft
global app
global ui
#global save
#save = 0
global xIjzer
xIjzer = 1
global yIjzer
yIjzer = 1
global xMax
xMax = 5
global yMax
yMax = 5
global positionList
positionList = ""
global previous50
global contentLength



try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


class Ui_Form(Qt.QWidget):

    global x_series
    x_series = [255,255,255,255]
    global oldSide
    oldSide = "NA"
    global distanceRight
    global distanceLeft
    distanceRight='NA-ini'
    distanceLeft='NA-ini'
    
    def setupUi(self, Form):
        shutil.copy2(r'mapimages/NOMAP.jpg',r'mapimages/map.jpg')
        
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(955, 755)
        self.gridLayout = QtGui.QGridLayout(Form)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.gridLayout_autonoom = QtGui.QGridLayout()
        self.gridLayout_autonoom.setObjectName(_fromUtf8("gridLayout_autonoom"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_autonoom.addItem(spacerItem, 0, 0, 1, 1)
        self.autonoomRijden = QtGui.QCheckBox(Form)
        self.autonoomRijden.setObjectName(_fromUtf8("autonoomRijden"))
        self.gridLayout_autonoom.addWidget(self.autonoomRijden, 0, 1, 1, 1)

        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_autonoom.addItem(spacerItem, 0, 1, 2, 1)
        self.doelPositie = QtGui.QLineEdit(Form)
        self.doelPositie.setObjectName(_fromUtf8("doelpositie"))
        self.gridLayout_autonoom.addWidget(self.doelPositie, 0, 2, 1, 1)

        self.pushButton_pos = QtGui.QPushButton(Form)
        self.pushButton_pos.setObjectName(_fromUtf8("pushButton_pos"))
        self.gridLayout_autonoom.addWidget(self.pushButton_pos, 0, 3, 1, 1)
        
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_autonoom.addItem(spacerItem1, 0, 2, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_autonoom, 2, 0, 1, 1)
        self.verticalLayout_kaart = QtGui.QVBoxLayout()
        self.verticalLayout_kaart.setObjectName(_fromUtf8("verticalLayout_kaart"))
        self.Kaart = customGraphicsView(Form)
        self.Kaart.setObjectName(_fromUtf8("Kaart"))
        self.verticalLayout_kaart.addWidget(self.Kaart)
        self.gridLayout.addLayout(self.verticalLayout_kaart, 1, 1, 1, 1)
        self.gridLayout_besturing = QtGui.QGridLayout()
        self.gridLayout_besturing.setObjectName(_fromUtf8("gridLayout_besturing"))
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_besturing.addItem(spacerItem2, 1, 0, 1, 1)
        
        self.verticalLayout_forward = QtGui.QVBoxLayout()
        self.verticalLayout_forward.setObjectName(_fromUtf8("verticalLayout_forward"))
        self.pushButton_forward = QtGui.QPushButton(Form)
        self.pushButton_forward.setObjectName(_fromUtf8("pushButton_forward"))
        self.verticalLayout_forward.addWidget(self.pushButton_forward)
        self.gridLayout_besturing.addLayout(self.verticalLayout_forward, 0, 2, 1, 1)

        self.verticalLayout_adjustLeft = QtGui.QVBoxLayout()
        self.verticalLayout_adjustLeft.setObjectName(_fromUtf8("verticalLayout_adjustLeft"))
        self.pushButton_adjustLeft = QtGui.QPushButton(Form)
        self.pushButton_adjustLeft.setObjectName(_fromUtf8("pushButton_adjustLeft"))
        self.verticalLayout_adjustLeft.addWidget(self.pushButton_adjustLeft)
        self.gridLayout_besturing.addLayout(self.verticalLayout_adjustLeft, 0, 1, 1, 1)

        self.verticalLayout_adjustRight = QtGui.QVBoxLayout()
        self.verticalLayout_adjustRight.setObjectName(_fromUtf8("verticalLayout_adjustRight"))
        self.pushButton_adjustRight = QtGui.QPushButton(Form)
        self.pushButton_forward.setObjectName(_fromUtf8("pushButton_adjustRight"))
        self.verticalLayout_adjustRight.addWidget(self.pushButton_adjustRight)
        self.gridLayout_besturing.addLayout(self.verticalLayout_adjustRight, 0, 3, 1, 1)

        self.verticalLayout_backward = QtGui.QVBoxLayout()
        self.verticalLayout_backward.setObjectName(_fromUtf8("verticalLayout_backward"))
        self.pushButton_backward = QtGui.QPushButton(Form)
        self.pushButton_backward.setObjectName(_fromUtf8("pushButton_backward"))
        self.verticalLayout_backward.addWidget(self.pushButton_backward)
        self.gridLayout_besturing.addLayout(self.verticalLayout_backward, 2, 2, 1, 1)
        self.verticalLayout_stop = QtGui.QVBoxLayout()
        self.verticalLayout_stop.setObjectName(_fromUtf8("verticalLayout_stop"))
        self.pushButton_stop = QtGui.QPushButton(Form)
        self.pushButton_stop.setObjectName(_fromUtf8("pushButton_stop"))
        self.verticalLayout_stop.addWidget(self.pushButton_stop)
        self.gridLayout_besturing.addLayout(self.verticalLayout_stop, 1, 2, 1, 1)
        self.verticalLayout_left = QtGui.QVBoxLayout()
        self.verticalLayout_left.setObjectName(_fromUtf8("verticalLayout_left"))
        self.pushButton_left = QtGui.QPushButton(Form)
        self.pushButton_left.setObjectName(_fromUtf8("pushButton_left"))
        self.verticalLayout_left.addWidget(self.pushButton_left)
        self.gridLayout_besturing.addLayout(self.verticalLayout_left, 1, 1, 1, 1)
        self.verticalLayout_right = QtGui.QVBoxLayout()
        self.verticalLayout_right.setObjectName(_fromUtf8("verticalLayout_right"))
        self.pushButton_right = QtGui.QPushButton(Form)
        self.pushButton_right.setObjectName(_fromUtf8("pushButton_right"))
        self.verticalLayout_right.addWidget(self.pushButton_right)
        self.gridLayout_besturing.addLayout(self.verticalLayout_right, 1, 3, 1, 1)
        spacerItem3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_besturing.addItem(spacerItem3, 1, 4, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_besturing, 2, 1, 1, 1)
        self.verticalLayout_camerabeeld = QtGui.QVBoxLayout()
        self.verticalLayout_camerabeeld.setObjectName(_fromUtf8("verticalLayout_camerabeeld"))
        self.Camerabeeld = QtGui.QLabel(Form)
        self.Camerabeeld.setObjectName(_fromUtf8("Camerabeeld"))
        self.Camerabeeld.setFixedHeight(300)
        self.verticalLayout_camerabeeld.addWidget(self.Camerabeeld)
        self.gridLayout.addLayout(self.verticalLayout_camerabeeld, 0, 1, 1, 1)
        self.gridLayout_turnCamera = QtGui.QGridLayout()
        self.gridLayout_turnCamera.setObjectName(_fromUtf8("gridLayout_turnCamera"))
        spacerItem4 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_turnCamera.addItem(spacerItem4, 0, 0, 1, 1)
        self.verticalLayout_turnCameraRight = QtGui.QVBoxLayout()
        self.verticalLayout_turnCameraRight.setObjectName(_fromUtf8("verticalLayout_turnCameraRight"))
        self.pushButton_turnCameraRight = QtGui.QPushButton(Form)
        self.pushButton_turnCameraRight.setObjectName(_fromUtf8("pushButton_turnCameraRight"))
        self.verticalLayout_turnCameraRight.addWidget(self.pushButton_turnCameraRight)
        self.gridLayout_turnCamera.addLayout(self.verticalLayout_turnCameraRight, 0, 3, 1, 1)
        self.verticalLayout_turnCameraLeft = QtGui.QVBoxLayout()
        self.verticalLayout_turnCameraLeft.setObjectName(_fromUtf8("verticalLayout_turnCameraLeft"))
        self.pushButton_turnCameraLeft = QtGui.QPushButton(Form)
        self.pushButton_turnCameraLeft.setObjectName(_fromUtf8("pushButton_turnCameraLeft"))
        self.verticalLayout_turnCameraLeft.addWidget(self.pushButton_turnCameraLeft)
        self.gridLayout_turnCamera.addLayout(self.verticalLayout_turnCameraLeft, 0, 1, 1, 1)

        self.verticalLayout_turnCameraFront = QtGui.QVBoxLayout()
        self.verticalLayout_turnCameraFront.setObjectName(_fromUtf8("verticalLayout_turnCameraFront"))
        self.pushButton_turnCameraFront = QtGui.QPushButton(Form)
        self.pushButton_turnCameraFront.setObjectName(_fromUtf8("pushButton_turnCameraFront"))
        self.verticalLayout_turnCameraFront.addWidget(self.pushButton_turnCameraFront)
        self.gridLayout_turnCamera.addLayout(self.verticalLayout_turnCameraFront, 0, 2, 1, 1)
        
        spacerItem5 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_turnCamera.addItem(spacerItem5, 0, 3, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_turnCamera, 2, 2, 1, 1)
        self.gridLayout_sensorwaarden = QtGui.QGridLayout()
        self.gridLayout_sensorwaarden.setObjectName(_fromUtf8("gridLayout_sensorwaarden"))

        #sensorwaarden
        spacerItem6 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_sensorwaarden.addItem(spacerItem6, 0, 0, 1, 1)
        self.Sensorwaarden = QtGui.QLabel(Form)
        self.Sensorwaarden.setObjectName(_fromUtf8("Sensorwaarden"))
        self.gridLayout_sensorwaarden.addWidget(self.Sensorwaarden, 0, 1, 1, 1)     
        
        spacerItem7 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_sensorwaarden.addItem(spacerItem7, 0, 2, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_sensorwaarden, 0, 2, 1, 1)
        self.gridLayout_commandos = QtGui.QGridLayout()
        self.gridLayout_commandos.setObjectName(_fromUtf8("gridLayout_commandos"))
        self.Commandos = QtGui.QTextBrowser(Form)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Commandos.sizePolicy().hasHeightForWidth())
        self.Commandos.setSizePolicy(sizePolicy)
        self.Commandos.setObjectName(_fromUtf8("Commandos"))
        self.gridLayout_commandos.addWidget(self.Commandos, 0, 1, 1, 1)
        spacerItem8 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_commandos.addItem(spacerItem8, 0, 0, 1, 1)
        spacerItem9 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_commandos.addItem(spacerItem9, 0, 2, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_commandos, 0, 0, 1, 1)
        self.gridLayout_snelheid = QtGui.QGridLayout()
        self.gridLayout_snelheid.setObjectName(_fromUtf8("gridLayout_snelheid"))
        self.snelheid = QtGui.QLCDNumber(Form)
        self.snelheid.setObjectName(_fromUtf8("snelheid"))
        self.gridLayout_snelheid.addWidget(self.snelheid, 0, 1, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_snelheid, 1, 2, 1, 1)
        
        #timer voor refresh-rate van camera afbeeldingen.
        self.ctimer = QtCore.QTimer()

        #timer voor refreshen van kaart
        #self.ktimer = QtCore.QTimer()

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)
        self.Kaart.setStyleSheet("border-image: url(mapImages/map.jpg);")
   
    @QtCore.pyqtSlot()
    def setKaart(self):
        print"kaart gezet"
        self.Kaart.setStyleSheet("border-image: url(mapImages/map.jpg);")
        app.processEvents()
        
    def retranslateUi(self, Form):
        global pic
        Form.setWindowTitle(_translate("Form", "Robot GUI", None))
        self.autonoomRijden.setText(_translate("Form", "Autonomously driving", None))
        
        self.pushButton_adjustRight.setText(_translate("Form", "adjust Right", None))

        self.pushButton_adjustLeft.setText(_translate("Form", "adjust Left", None))

        self.pushButton_forward.setText(_translate("Form", "Forward", None))

        
        self.pushButton_backward.setText(_translate("Form", "Backward", None))
        self.pushButton_stop.setText(_translate("Form", "Stop/Disconnect", None))
        self.pushButton_left.setText(_translate("Form", "Left", None))
        self.pushButton_right.setText(_translate("Form", "Right", None))
        self.pushButton_turnCameraRight.setText(_translate("Form", "Turn camera right", None))
        self.pushButton_turnCameraLeft.setText(_translate("Form", "Turn camera left", None))
        self.pushButton_turnCameraFront.setText(_translate("Form", "Turn camera front", None))
        
        self.pushButton_pos.setText(_translate("Form", "Set goal", None))

        self.pushButton_adjustRight.clicked.connect(self.adjustRight)

        self.pushButton_adjustLeft.clicked.connect(self.adjustLeft)

        self.pushButton_forward.clicked.connect(self.moveForward)


        
        self.pushButton_backward.clicked.connect(self.moveBackwards)
        self.pushButton_stop.clicked.connect(self.stop)
        self.pushButton_left.clicked.connect(self.turnLeft)
        self.pushButton_right.clicked.connect(self.turnRight)
        self.pushButton_turnCameraRight.clicked.connect(self.turnCameraRight)
        self.pushButton_turnCameraLeft.clicked.connect(self.turnCameraLeft)
        self.pushButton_turnCameraFront.clicked.connect(self.turnCameraFront)
        self.autonoomRijden.stateChanged.connect(self.autonomouslyDrivingOrNot)

        

        self.pushButton_pos.clicked.connect(self.setPos)

        self.sb = self.Commandos.verticalScrollBar()
        self.sb.setValue(self.sb.maximum())
        
        
        #self.snelheid.display(self.getSpeed())
        pixmap = QtGui.QPixmap(r'tijdelijk/img1.jpg')
        
        #timer voor refresh-rate van camera afbeeldingen.
        self.Camerabeeld.setPixmap(pixmap)
        self.ctimer.start(1000)
        QtCore.QObject.connect(self.ctimer, QtCore.SIGNAL("timeout()"), self.changeImage)

        #kaart
        #self.Kaart.setStyleSheet("border-image: url(mapimages/map.jpg);")
        #self.ktimer.start(1000)
        #QtCore.QObject.connect(self.ktimer, QtCore.SIGNAL("timeout()"),
        #                      self.callMarkingPointOnMap)
        #QtCore.QObject.connect(self.Kaart, QtCore.SIGNAL("resize()"),
        #                     self.callMarkingPointOnMap)

#GUI GERELATEERDE FUNCTIES
    
    def setPos(self):
        global doelposition
        doelposition = self.doelPositie.text()
        self.doelPositie.clear()
        print doelposition
        self.updateDebug("Executing: Setting goal position")
        self.sendCommand("goal:"+str(doelposition))
        app.processEvents()
    


    def makeDistancePic(self, value, side):
        value = int(float(value))
        if (side == "L"):
            img = Image.open("distance_left.jpg")
            draw = ImageDraw.Draw(img)
            os.environ.get("FONT_PATH", "LucidaSansRegular.ttf" )
            font = ImageFont.truetype("LucidaSansRegular.ttf", 16)
            draw.text((40,30), "distance left: " + str(value),(0,0,0), font = font)

        else:
            img = Image.open("distance_right.jpg")
            draw = ImageDraw.Draw(img)
            os.environ.get("FONT_PATH", "LucidaSansRegular.ttf" )
            font = ImageFont.truetype("LucidaSansRegular.ttf", 16)
            draw.text((120,30), "distance right: " + str(value),(0,0,0), font = font)

        img.save('example.jpg')



    def changeImage(self):
        #change camera image
        path = r'tijdelijk/img1.jpg'
        pixmap = QtGui.QPixmap(path)
        self.Camerabeeld.setPixmap(pixmap)

        #change image of sensor values
        pixmap = QtGui.QPixmap('example.jpg')

        self.Sensorwaarden.setPixmap(pixmap)

    def updateDebug(self,data):
        self.Commandos.insertPlainText(str(data))
        self.Commandos.append('')
        app.processEvents()
        self.sb = self.Commandos.verticalScrollBar()
        self.sb.setValue(self.sb.maximum())
        app.processEvents()  

    def setDistanceLeft(self,distance):
        global distanceLeft
        distanceLeft = distance
        
    def setDistanceRight(self,distance):
        global distanceRight
        distanceRight = distance


#CONNECTIE

    def sendCommand(self,commandToSend):
        global send
        global command

        send = True
        command = commandToSend
        

    

    def getPic(self):
        global picture
        picture = 1
        
    def getMap(self):
        global kaart
        kaart = 1

    def setFeedBack(self,result):
        
        if result:
            self.updateDebug("Image recognition recognised: "+str(result))
            
        else:
            self.updateDebug("Image recognition faild due to incorrect received image: trying again ...")
        

#VERWERKING INFO
        
    def autonomouslyDrivingOrNot(self):
        global send
        global command
        
        if (self.autonoomRijden.isChecked()):
            self.Commandos.insertPlainText("Enable autonomously driving")
            self.Commandos.append('')
            self.rijAutonoom()
            print "auto : autonoom gestart"
            
        else:
            self.Commandos.insertPlainText("Disable autonomously driving")
            self.Commandos.append('')
            self.stopRijAutonoom()
            print "auto : autonoom gestopt"
    
    def stop(self):
        
        if not (self.autonoomRijden.isChecked()):
            self.Commandos.insertPlainText("Stop")
            self.Commandos.append('')

    def setSpeed(self, t):
        print 't: ' + str(t)
        y = (12*t + 2.5)/t
        self.snelheid.display(y)
        app.processEvents()
        time.sleep(t/100)
        self.snelheid.display(0)
        app.processEvents()
        
    def connect_slots(self, sender):
        self.connect(sender,QtCore.SIGNAL("setKaart"),self.setKaart)
        
    #catching info en uitsorteren van data.
    def processInfo(self,data):
        global previous50
        global positionList
        global xIjzer
        global yIjzer
        global contentLength
        print "processinfo: " + str(data)
        
        if (data[0:2]=='--'):
            previous50=0
            self.updateDebug(data)
            
        elif (data[0:6] == "teams:"):
            previous50=0
            lijst = data[7:]
            endPos = lijst.index(')')
            positionList = lijst[1:endPos]
            self.updateDebug("Calculating positions ...")
            (xIjzer,yIjzer) = makeMap((xMax,yMax,xIjzer,yIjzer), positionList)
            self.updateDebug("updating positions on map")
            self.emit(QtCore.SIGNAL("setKaart"))
            
        elif (data[0:14] == "distance left:"):
            previous50=0
            self.setDistanceLeft(data[15:18])
            self.makeDistancePic(data[15:18], "L")
            
        elif (data[0:10] == "refreshMap"):
            (xIjzer,yIjzer) = makeMap((xMax,yMax,xIjzer,yIjzer), positionList)
            self.emit(QtCore.SIGNAL("setKaart"))
            
        elif (data[0:15] == "distance right:"):
            previous50=0
            self.setDistanceRight(data[16:19])
            self.makeDistancePic(data[16:19], "R")
            

        elif (data[0:5] == "ImRec"):
            contentLength = data[6:]
            self.updateDebug("Image recognition is processing...")
            self.getPic()
                   
        elif (data[0:7] == "No goal"):
            previous50=0
            self.updateDebug("No goal specified yet!")
            
        elif data=='':
            previous50=1
            pass

        elif (data[0:12] == "resultImrec:"):
            self.setFeedBack(data[12:])

        elif (data[0:12] == "imrecfail"):
            self.setFeedBack(False)
        
        elif (data[0:5] == "World"):
            contentLength = data[6:]
            self.updateDebug("Retrieving map from server...")
            self.getMap()
            
            
            
        
        else:
            if ((previous50==0) and len(data)>10):
                previous50=1
                self.updateDebug("Image receiving failed: trying again ...")
            else:
                pass
            
       
    
#definities voor key-presses                        
    def moveForward(self):
        self.updateDebug("Executing: moving forward")
        self.sendCommand("forward")

    def adjustRight(self):
        self.updateDebug("Executing: adjusting Right")
        self.sendCommand("adjustRight")

    def adjustLeft(self):
        self.updateDebug("Executing: adjusting Left")
        self.sendCommand("adjustLeft")

    def moveBackwards(self):
        self.updateDebug("Executing: moving backward")
        self.sendCommand("backward")

    def turnLeft(self):
        self.updateDebug("Executing: turning Left")
        self.sendCommand("turnLeft")

    def turnRight(self):
        self.updateDebug("Executing: turning Right")
        self.sendCommand("turnRight")

    def turnCameraLeft(self):
        self.updateDebug("Executing: turning camera left")
        self.sendCommand("turnCameraLeft")
        
    def turnCameraRight(self):
        self.updateDebug("Executing: turning camera right")
        self.sendCommand("turnCameraRight")

    def turnCameraFront(self):
        self.updateDebug("Executing: turning camera front")
        self.sendCommand("turnCameraFront")

    def rijAutonoom(self):
        self.updateDebug("Executing: driving autonomously")
        self.sendCommand("auto")

    def stopRijAutonoom(self):
        self.updateDebug("Executing: stopping autonomously driving")
        self.sendCommand("autoStop")

class customGraphicsView(QtGui.QGraphicsView):
    
    def __init__(self, parent=None):
        QtGui.QGraphicsView.__init__(self, parent)

    def resizeEvent(self,evt = None):  # @UnusedVariable
        self.emit(QtCore.SIGNAL("resize()"))

class Server():

    def initConnection(self):
        global s
        global t
        global send
        global picture
        global command
        global kaart
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
        HOST = ""     # The  host of the server
        PORT = 9044                     # The port used by the server
        s.bind((HOST,PORT))
        print "Listening"
        s.listen(5)

        while not closing:
#             try:
            print "accepting"
            self.client = s.accept()[0]
            print "Connected"
            print "***************************************"
            self.client.setblocking(0)
            while not closing:
                
                try:
                    ready = select.select([self.client,],[self.client,],[])
                    if ready[0]:
                        print "receive"
                        data = self.receiveInfo()
                        print "received: " + str(data)
                        t.add(data)
                        
                    else:    
                        if picture:
                            print "send Picture"
                            self.client.sendall("Send Picture")
                            result = self.receivePicture()
                            picture = 0
                            if not result:
                                self.client.close()
                                break
                            
                        elif send:
                            print "command send: ", command
                            self.client.sendall(str(command))
                            send = 0
                            command = ""

                        elif kaart:
                            print "send Map"
                            self.client.sendall("Send Map")
                            result = self.receiveMap()
                            kaart = 0
                            if not result:
                                self.client.close()
                                break
                            
                    
                        
                except socket.error,msg:
                    print "Socketerror %read_socket" % msg
                    break

#             except:
#                 print "Stop"
#                 break

    
        self.cleanup()

    def receiveInfo(self):
        try:
            data = self.client.recv(4096)
             
        except:
            print "No data available in receive info"
            data = ""
            
        return data

    def receivePicture(self):
        global command
        global contentLength

        client = s.accept()[0]
        client.setblocking(1)

        time.sleep(0.2)
        
        select.select([client,],[],[])

        data = ''
        
        timeOut = 5
        currentTime = time.time()
        
        with open(r'tijdelijk/img1TEST.jpg', 'wb') as file_to_write:
           
            bytesReadUpToNow = 0
            
            while bytesReadUpToNow < int(contentLength):
                data += client.recv(1)
                bytesReadUpToNow += 1
            
                if time.time() - currentTime > timeOut:
                    print "timeOut"
                    select.select([],[client,],[])
                    client.sendall('imrecfail')
                    return 0

            file_to_write.write(data)
            file_to_write.close()
            
        os.remove(r'tijdelijk/img1.jpg')
        os.rename(r'tijdelijk/img1Test.jpg',r'tijdelijk/img1.jpg')

        client.close()
    
        #doing imrec
        try:
            result = imrec.detectImage(r'tijdelijk/img1.jpg')
            command = 'resultImRec:'+str(result)
            select.select([],[self.client,],[])
            self.client.sendall(command)
            t.add("resultImrec: " + str(result))
            return 1
            
        except:
            t.add("imrecfail")
            select.select([],[client,],[])
            self.client.sendall("imrecfail")
            return 0
    
    def receiveMap(self):
        global kaart
        global contentLength
        
        client = s.accept()[0]
        client.setblocking(0)

        time.sleep(0.2)
        select.select([client,],[],[])
        data = ''
        
        timeOut = 5
        currentTime = time.time()
        
        with open(r'mapimages/kaarttest.txt', 'wb') as file_to_write:
            bytesReadUpToNow = 0
            
            while bytesReadUpToNow < int(contentLength):
                data += client.recv(1)
                bytesReadUpToNow += 1
            
                if time.time() - currentTime > timeOut:
                    print "timeOut"
                    select.select([],[client,],[])
                    client.sendall('mapfail')
                    return 0

            file_to_write.write(data)
            file_to_write.close()
        if os.path.exists("mapimages/kaart.txt"):
            os.remove(r'mapimages/kaart.txt')
        os.rename(r'mapimages/kaarttest.txt',r'mapImages/kaart.txt')
        
        #refresh the map
        t.add("refreshMap")
        
        client.close()
        return 1

    def cleanup(self):
        print "cleanup"
        global s
        global t
        
        time.sleep(1)
        if self.client:
            self.client.sendall("shutdown")
            self.client.close()
        t.stop()
        t.terminate()
        time.sleep(1)
        s.close()

class MyQWidget(QtGui.QWidget): 
    
    def __init__(self):
        super(MyQWidget,self).__init__()
    
    def closeEvent(self, event):
        global closing
        quit_msg = "Are you sure you want to quit the program?"
        reply = QtGui.QMessageBox.question(self, 'Message', quit_msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        
        if reply == QtGui.QMessageBox.Yes:
            closing = True
            event.accept()
        
        else:
            event.ignore()
            

        
if __name__ == "__main__":
    global app
    global Form
    global ui
    global t
    global imrec
    if os.path.exists("mapimages/kaart.txt"):
        os.remove(r'mapimages/kaart.txt')
    (x,y) = makeMap()
    app = QtGui.QApplication(sys.argv)
    Form = MyQWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    
    imrec = ImRec()
    Form.show()
    t = ProcesThread(ui)
    ui.connect_slots(t)
    t.start()
    server = Server()
    serverThread = threading.Thread(target = server.initConnection)
    serverThread.start()
    
    sys.exit(app.exec_())
