from __future__ import division
from bluepy.btle import Scanner, DefaultDelegate, Peripheral
import numpy as np
import threading
import time


class MyDelegate(DefaultDelegate):
    def __init__(self, number):
        DefaultDelegate.__init__(self)
        self.number = number

    def handleNotification(self, cHandle, data):
        global sampleCount
        global sampleCount2

        tempX = ((ord(data[1])<<8) + ord(data[0])) / 100
        tempY = ((ord(data[3])<<8) + ord(data[2])) / 100
        tempZ = ((ord(data[5])<<8) + ord(data[4])) / 100

        if tempX > 327.67:
            tempX = (655.35 - tempX)
        if tempY > 327.67:
            tempY = (655.35 - tempY)
        if tempZ > 327.67:
            tempZ = (655.35 - tempZ)
            
        if str(self.number) == "0":
            sampleCount += 1
            if sampleCount > 300:
                text_file.truncate(0)
                text_file.seek(0)
                sampleCount = 0
            text_file.write("%f," % tempX)
            text_file.write("%f," % tempY)
            text_file.write("%f\n" % tempZ)
            text_file.flush()
        else:
            sampleCount2 += 1
            if sampleCount2 > 300:
                text_file2.truncate(0)
                text_file2.seek(0)
                sampleCount2 = 0
            text_file2.write("%f," % tempX)
            text_file2.write("%f," % tempY)
            text_file2.write("%f\n" % tempZ)
            text_file2.flush()
        print("Thread:" + str(self.number) + " " + str(sampleCount))
        print tempX
        print tempY
        print tempZ  

bt_addresses = ['00:0b:57:51:bd:7e', '00:0b:57:51:c0:a9']
connections = []
connection_threads = []
scanner = Scanner(0)

class ListenerThread(threading.Thread):
    def __init__(self, connection_index):
        threading.Thread.__init__(self)
        self.connection_index = connection_index
        
    def run(self):
        connection = connections[self.connection_index]
        connection.setDelegate(MyDelegate(self.connection_index))
        connection.writeCharacteristic(79, "\x01\x00")
        
        while True:
            if connection.waitForNotifications(1):
                continue
            

text_file = open("Acc_Data.txt", "w")
text_file2 = open("Acc_Data2.txt", "w")
sampleCount = 0
sampleCount2 = 0

try:            
    while True:
        print('Connected: ' + str(len(connection_threads)))
        print('Scanning...')
        devices = scanner.scan(2)

        for d in devices:
            print(d.addr)
            if d.addr in bt_addresses:
                p = Peripheral(d)
                connections.append(p)
                #p.writeCharacteristic(79, "\x01\x00")
                t = ListenerThread(len(connections)-1)
                t.start()
                connection_threads.append(t)
except KeyboardInterrupt:
    pass


text_file.close()        
text_file2.close()




