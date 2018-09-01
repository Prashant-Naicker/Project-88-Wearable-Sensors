from __future__ import division
from bluepy.btle import Scanner, DefaultDelegate, Peripheral
from collections import deque
import numpy as np
import threading
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation


class MyDelegate(DefaultDelegate):
    global ax
    global ay
    global sampleCount
    
    def __init__(self, number):
        DefaultDelegate.__init__(self)
        self.number = number

    def handleNotification(self, cHandle, data):
        global ax
        global ay
        global sampleCount
        
        tempX = ((ord(data[1])<<8) + ord(data[0])) / 100
        
        
        if tempX > 327.67:
            tempX = (655.35 - tempX)
        print tempX
        sampleCount += 1

        if len(ay) < 300:
            ay.append(tempX)
            ax.append(sampleCount)
        else:
            ay.pop()
            ax.pop()
            ay.appendleft(tempX)
            ax.appendLef(sampleCount)


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

def animate(self, a0, a1):
    global ax
    global ay
    a0.set_data(range(300), ax)
    a1.set_data(range(300), ay)
    return a0,

ax = deque([0.0]*300)
ay = deque([0.0]*300)
sampleCount = 0

fig = plt.figure()
axis = plt.axes(xlim=(0,300), ylim=(0,20))
a0, = axis.plot([], [])
a1, = axis.plot([], [])
anim = animation.FuncAnimation(fig, animate, fargs=(a0, a1), interval=50)
plt.show()
print("I'm here")


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
                t = ListenerThread(len(connections)-1)
                t.start()
                connection_threads.append(t)
except KeyboardInterrupt:
    pass
