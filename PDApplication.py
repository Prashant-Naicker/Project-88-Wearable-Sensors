from __future__ import division
from bluepy.btle import Scanner, DefaultDelegate, Peripheral
from scipy.fftpack import fft
from pyqtgraph.Qt import QtGui, QtCore
from collections import deque
from datetime import datetime
import pyqtgraph as pg
import numpy as np
import socket
import sys
import struct
import threading
import time



bt_addresses = ['00:0b:57:51:c0:a9', '00:0b:57:51:bd:7e']
connections = []
connection_threads = []
scanner = Scanner(0)

AccX = deque([0.0]*200)
AngVZ = deque([0.0]*200)
AccXPlot = deque([0.0]*200)
AngVZPlot = deque([0.0]*200)

sampleCount = 0
AccXDC = 0
AngVZDC = 0
FEnergy = 0
statusCode = '0'
status = 'Idle'



class MyDelegate(DefaultDelegate):
    def __init__(self, number):
        DefaultDelegate.__init__(self)
        self.number = number

    def handleNotification(self, cHandle, data):
        global sampleCount
        global AccXDC
        global AngVZDC
        global FEnergy

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



class LiveGraphs(object):
    def __init__(self):
        #Graphing stuff.
        pg.setConfigOptions(antialias=True)

        self.traces = dict()
        self.app = QtGui.QApplication(sys.argv)
        self.win = pg.GraphicsWindow(title='P4P')
        self.win.setWindowTitle('P4P')
        self.pastStatus = 'Idle'
        self.win.addLabel('Status: ' + status,0,1, size='22pt', color='fff400')
        self.win.resize(1000,600)

        AccX_xlabels = [(0, '0'), (50, '50'), (100, '100'),(150, '150'), (200, '200')]
        AccX_xaxis = pg.AxisItem(orientation='bottom')
        AccX_xaxis.setTicks([AccX_xlabels])
        AccX_xaxis.setLabel('Sample No.')
        AccX_yaxis = pg.AxisItem(orientation='left')
        AccX_yaxis.setLabel('Acc X (m/s2)')

        AngVZ_xlabels = [(0, '0'), (50, '50'), (100, '100'),(150, '150'), (200, '200')]
        AngVZ_xaxis = pg.AxisItem(orientation='bottom')
        AngVZ_xaxis.setTicks([AngVZ_xlabels])
        AngVZ_xaxis.setLabel('Sample No.')
        AngVZ_yaxis = pg.AxisItem(orientation='left')
        AngVZ_yaxis.setLabel('AngV Z (deg/s)')

        Fenergy_xaxis = pg.AxisItem(orientation='bottom')
        Fenergy_xaxis.setLabel('Freq (hz)')
        Fenergy_yaxis = pg.AxisItem(orientation='left')
        Fenergy_yaxis.setLabel('Acc X (m/s2)')

        self.accelerationX = self.win.addPlot(
            row=1, col=1, axisItems={'bottom': AccX_xaxis, 'left': AccX_yaxis},
        )
        self.angularVelocityZ = self.win.addPlot(
            row=2, col=1, axisItems={'bottom': AngVZ_xaxis, 'left': AngVZ_yaxis},
        )

        self.spectrum = self.win.addPlot(
            row=3, col=1, axisItems={'bottom': Fenergy_xaxis, 'left': Fenergy_yaxis},
        )

        #Waveform and spectrum x points.
        self.windowLength = 200
        self.x = np.arange(self.windowLength)
        self.f = np.arange(20)

    def start(self):
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()

    def set_plotdata(self, name, data_x, data_y):
        if name in self.traces:
            self.traces[name].setData(data_x, data_y)
        else:
            if name == 'accelerationX':
                self.traces[name] = self.accelerationX.plot(pen='c', width=3)
                self.accelerationX.setYRange(-10, 10, padding=0)
                self.accelerationX.setXRange(0, self.windowLength, padding=0.005)
            if name == 'angularVelocityZ':
                self.traces[name] = self.angularVelocityZ.plot(pen='m', width=3)
                self.angularVelocityZ.setYRange(-250, 200, padding=0)
                self.angularVelocityZ.setXRange(0, self.windowLength, padding=0.005)
            if name == 'spectrum':
                self.traces[name] = self.spectrum.plot(pen='g', width=3)
                self.spectrum.setYRange(0, 2, padding=0)
                self.spectrum.setXRange(0, 20, padding=0.005)

    def update(self):
        global AccX
        global AngVZ
        global AccXPlot
        global AngVZPlot
        
        if len(AccX) > 0:
            AccXPlot.pop()
            AccXPlot.appendleft(AccX[0])
        else:
            print("===============No data in buffer================================")
        if len(AngVZ) > 0:
            AngVZPlot.pop()
            AngVZPlot.appendleft(AngVZ[0])
        else:
            print("===============No data in buffer================================")
    
        self.set_plotdata(name='accelerationX', data_x=self.x, data_y=AccX,)
        self.set_plotdata(name='angularVelocityZ', data_x=self.x, data_y=AngVZ,)

        sp_data = fft(AccX)
        #Normalising.
        sp_data = np.abs(sp_data[0:20])/200
        #Removing the DC component as it is its own feature.
        sp_data[0] = 0
        self.set_plotdata(name='spectrum', data_x=self.f, data_y=sp_data)

        #Only update the label if the status has changed.
        if self.pastStatus != status:
            self.win.getItem(0,1).setText('Status: ' + status)
            self.pastStatus = status

    def animation(self):
        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        #Setting the refresh rate.
        timer.start(30)
        self.start()



class RecognitionThread(threading.Thread):
    def run(self):
        global status
        global statusCode

        while True:
            currentTime = str(datetime.now())

            #Decision tree classification.
            if AngVZDC <= 40.6:
                if AngVZDC <= 2.605:
                    statusCode = '3'
                    status = 'Idle'
                    print (currentTime + "  -  Idle")
                else:
                    if AngVZDC <= 13.455:
                        statusCode = '2'
                        status = 'Up Down'
                        print (currentTime + "  -  UpDown")
                    else:
                        statusCode = '1'
                        status = 'Shuffling'
                        print (currentTime + "  -  Shuffling")
            else:
                statusCode = '0'
                status = 'Walking'
                print (currentTime + "  -  Walking")

            messageBytes = str(statusCode).decode('utf-8')
            dataLength = len(messageBytes)
            dataLengthRaw = bytearray(struct.pack("<H", dataLength))
            
            s.send(dataLengthRaw)
            s.send(messageBytes)

            time.sleep(2)



if __name__ == '__main__':
    host = '165.227.60.238'
    port = 8081
    s = socket.socket()
    s.connect((host, port))
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

    time.sleep(3)

    recognition = RecognitionThread()
    recognition.start()

    dataStream = LiveGraphs()
    dataStream.animation()

    try:
        while True:
            continue
    except KeyboardInterrupt:
        pass

    s.close()
