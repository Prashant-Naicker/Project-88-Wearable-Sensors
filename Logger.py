from __future__ import division
from bluepy.btle import Scanner, DefaultDelegate, Peripheral
from scipy.fftpack import fft
from pyqtgraph.Qt import QtGui, QtCore
from collections import deque
import pyqtgraph as pg
import numpy as np
import sys
import threading
import time



bt_addresses = ['00:0b:57:51:c0:a9']
connections = []
connection_threads = []
scanner = Scanner(0)

AccX = deque([0.0]*200)
AngVZ = deque([0.0]*200)

sampleCount = 0



class MyDelegate(DefaultDelegate):
    def __init__(self, number):
        DefaultDelegate.__init__(self)
        self.number = number

    def handleNotification(self, cHandle, data):
        global sampleCount

        #This block handles acceleration notifications.
        if cHandle == 78:
            tempAccX = ((ord(data[1])<<8) + ord(data[0])) / 100

            if tempAccX > 327.67:
                tempAccX -= 655.35

            tempAccX -= 9.81

            AccX.pop()
            AccX.appendleft(tempAccX)

            sampleCount += 1

            #Sample window size is set here.
            if sampleCount == 200:
                AccXDC = np.mean(np.abs(AccX))
                AngVZDC = np.mean(np.abs(AngVZ))
                FData = fft(AccX)
                FData = np.abs(FData)
                #We remove DC from the DFT because we already use it as a feature
                #in AccXDC.
                FData[0] = 0
                #Energy is defined as the sum of the squares of each frequency bin
                #divided by the total number of samples.
                FData = np.square(FData)
                FEnergy = np.sum(FData)/200
                print ("%0.2f, %0.2f, %0.2f\n" % (AccXDC, AngVZDC, FEnergy))
                data_file.write("%0.2f, %0.2f, %0.2f\n" % (AccXDC, AngVZDC, FEnergy))
                data_file.flush()
                sampleCount = 0

        #This block handles angular velocity notifications.
        elif cHandle == 81:
            tempAngVZ = ((ord(data[5])<<8) + ord(data[4])) / 100

            if tempAngVZ > 327.67:
                tempAngVZ -= 655.35

            AngVZ.pop()
            AngVZ.appendleft(tempAngVZ)



class ListenerThread(threading.Thread):
    def __init__(self, connection_index):
        threading.Thread.__init__(self)
        self.connection_index = connection_index

    def run(self):
        connection = connections[self.connection_index]
        connection.setDelegate(MyDelegate(self.connection_index))
        #Turning on the sending of accelerometer and angular velocity data.
        connection.writeCharacteristic(79, "\x01\x00")
        connection.writeCharacteristic(82, "\x01\x00")

        while True:
            if connection.waitForNotifications(1):
                continue



if __name__ == '__main__':
    data_file = open("Shuffling.txt", "w")
    print('Connected: ' + str(len(connection_threads)))
    print('Scanning...')
    devices = scanner.scan(2)

    for d in devices:
        print(d.addr)
        if d.addr in bt_addresses:
            p = Peripheral(d)
            connections.append(p)
            t = ListenerThread(len(connections)-1)
            t.start()
            connection_threads.append(t)
