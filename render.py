import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
plt.style.use("dark_background")


class Line:
    def __init__(self, a, b, color):
        self.a = a
        self.b = b
        self.color = color
        self.x = [a[0], b[0]]
        self.y = [a[1], b[1]]
        self.z = [a[2], b[2]]

    
class Renderer:
    def __init__(self):
        fig1 = plt.figure(1)
        self.ax = plt.axes(projection="3d")
 
        self.clear()
    
    def clear(self):
        self.lines = {}
        self.y2 = [[]]

    def __setitem__(self, index, line):
        self.lines[index] = line

    def __getitem__(self, index):
        self.lines[index]

    def show(self):
        self.ax.cla()
        self.ax.set_xticks([-1, -0.5, 0 ,0.5, 1])
        self.ax.set_yticks([-1, -0.5, 0 ,0.5, 1])
        self.ax.set_zticks([-1, -0.5, 0 ,0.5, 1])

        self.ax.axes.set_xlim3d(left=-1.2, right=1.2) 
        self.ax.axes.set_ylim3d(bottom=-1.2, top=1.2) 
        self.ax.axes.set_zlim3d(bottom=-1.2, top=1.2) 
        for idx in self.lines:
            line = self.lines[idx]
            self.ax.plot3D(line.x, line.y, line.z, c=line.color)

        plt.figure(2)
        plt.cla()
        for y in self.y2:
            plt.plot(y)

        plt.pause(1 / 1000)
