from __future__ import division
from bluepy.btle import Scanner, DefaultDelegate, Peripheral
import numpy as np
import threading
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque

x = np.arange(200)
y = deque()

runningTotal = 0
runningAv = 0
sampleCount = 0

class MyDelegate(DefaultDelegate):
    def __init__(self, number):
        DefaultDelegate.__init__(self)
        self.number = number

    def handleNotification(self, cHandle, data):
        global sampleCount
        global runningAv
        global runningTotal
        
        
        
        tempX = ((ord(data[1])<<8) + ord(data[0])) / 100

        if tempX > 327.67:
            tempX = (655.35 - tempX)

        tempX -= 9.81
        
        if len(y) < 600:
            y.appendleft(tempX)
        else:
            y.pop()
            y.appendleft(tempX)
            
        runningTotal += abs(tempX)
        sampleCount += 1
        
        if sampleCount > 200:
            runningAv = runningTotal / sampleCount
            runningTotal = 0
            sampleCount = 0

            if runningAv > 2.0:
                print ("Walking")
            elif runningAv > 0.6:
                print ("Shuffling")
            else:
                print ("Idle")
            
            
        
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

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)
axes = plt.gca()
axes.set_ylim([-10.0, 10.0])
yPlot = deque([0.0]*200)

def plot(ax):
    return ax.plot(x, yPlot, 'r-', animated=True)[0]
lines = [plot(ax1)]

def animate(i):
    if len(y) > 0:
        yPlot.pop()
        yPlot.appendleft(y.popleft())
    else:
        print("===============No data in buffer================================")
    for j, line in enumerate(lines, start=1):
        line.set_ydata(yPlot)
    return lines



ani = animation.FuncAnimation(fig, animate, interval=10, blit=True)
plt.show()



