import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style

style.use('fivethirtyeight')

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)

def animate(i):
    graph_data = open('Acc_Data.txt', 'r').read()
    lines = graph_data.split('\n')
    sample = []
    xs = []
    ys = []
    zs = []
    cnt = 0
    for line in lines:
        if len(line) > 1:
            x, y, z = line.split(',')
            sample.append(cnt)
            cnt += 1
            xs.append(x)
            ys.append(y)
            zs.append(z)
    ax1.clear()
    ax1.plot(sample, xs, 'r', sample, ys, 'b', sample, zs, 'g')

ani = animation.FuncAnimation(fig, animate, interval=50)
plt.show()
