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

class MyDelegate(DefaultDelegate):
    def __init__(self, number):
        DefaultDelegate.__init__(self)
        self.number = number

    def handleNotification(self, cHandle, data):
        tempY = ((ord(data[3])<<8) + ord(data[2])) / 100

        if tempY > 327.67:
            tempY = (655.35 - tempY)
            
        if len(y) < 600:
            y.appendleft(tempY)
        else:
            y.pop()
            y.appendleft(tempY)

        
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
axes.set_ylim([-5.0, 17.0])
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



