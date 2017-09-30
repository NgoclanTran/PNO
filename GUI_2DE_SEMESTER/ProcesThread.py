import Queue
from PyQt4 import QtCore

class ProcesThread(QtCore.QThread):

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

    def message(self):
        pass

    def clear(self):
        pass

    def run(self):
        q = self.Q

        while self.running:
            
            try:
                value = q.get(block = True,timeout = 1)
                #self.emit(QtCore.SIGNAL("setKaart"))
                self.ui.processInfo(value)
                
            except Queue.Empty:
                pass

        #info of what is left in the queue when stopped               
        if not q.empty():
            print "elements left in the queue:"
            
            while not q.empty():
                print q.get()
                
