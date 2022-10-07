import datetime
import logging
import time
import serial
import json 
import sys
from math import sqrt, acos, pi
import socket

import threading

drawing_enabled = False

if '--sim' in sys.argv or 'baruch' in socket.gethostname():
    from render import * 
    drawing_enabled = True
else:    
    from render_stub import * 





#some very lightwaight 3d vector operations
def vlen(v):
   return sqrt(sum([x*x for x in v]))

def vadd(v,w):
   return [x[0]+x[1] for x in zip(v,w)]

def scale(a, v):
   return [x*a for x in v]

def dot(a,b):
   return sum([x[0]*x[1] for x in zip(a,b)])

def vnorm(v):
    d = vlen(v)
    return [x/d for x in v]

class RunAvg:
    s = 0
    init_from_sample = True
    history = []
    history_max_len = 100

    def __init__(self, initial, a):
        self.a = a
        self.s = initial
    
    def add(self,v):
        if self.init_from_sample:
            self.init_from_sample = False
            self.s = v

        if type(self.s) in (tuple, list):
            self.s = [z[0]*(1-self.a) + self.a*z[1] for z in zip (self.s,v) ]
        else:
            self.s = self.s*(1-self.a) + v*self.a

        self.history = (self.history + [v])[-self.history_max_len:]


#WEIGHT_THRESHOLD = 0.002

class Weight:
    last = 0
    count = 0
    avg1 = RunAvg(0, 0.1)

    def add_sample(self, v):
        self.last = v
        self.count += 1

        self.avg1.add(v)

    # def is_sitting(self):
    #     return self.w > WEIGHT_THRESHOLD


class Acceleration:
    last = [0, 0, 0]
    count = 0
    color = [0,0,1]
    
    down = RunAvg([0,0,1], 0.01) 
    avg = RunAvg([0,0,1], 0.2) 

    def __init__(self, color):
        self.color = color
    
    def add_sample(self, s):
        s = [s['ax'], s['ay'], s['az']]
        self.last = vnorm(s) 
        self.count = self.count + 1
        self.down.add(self.last)
        self.avg.add(self.last)

    def angle(self):
        a = vnorm(self.avg.s)
        d = vnorm(down.avg.s)
        return acos(dot(a,d))

waight0 = Weight()
waight1 = Weight()
accel0 = Acceleration([1,0,0])
accel1 = Acceleration([0,1,0])


#{'HX711_0': {'data': 16659756}, 'HX711_1': {'data': 137991}, 'MPU0': {'ax': -6204, 'ay': -14972, 'az': -1872, 'temp': 1648}, 'MPU1': {'ax': 16228, 'ay': 2912, 'az': -6084, 'temp': 2832}}
def process_line(j):
    if 'HX711_0' in j and 'data' in j['HX711_0']:
        waight0.add_sample(j['HX711_0']['data'])

    if 'HX711_1' in j and 'data' in j['HX711_1']:
        waight1.add_sample(j['HX711_1']['data'])

    if 'MPU0' in j and 'ax' in j['MPU0']:
        accel0.add_sample(j['MPU0'])

    if 'MPU1' in j and 'ax' in j['MPU1']:
        accel1.add_sample(j['MPU1'])



# class Sensors:
#     serial_connection = None

#     swing_1_acceleration = Acceleration()
#     swing_1_weight = Weight()
#     swing_2_acceleration = Acceleration()
#     swing_2_weight = Weight()

#     def __init__(self):
#         try:
#             self.serial_connection = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)  # open serial port
#         except Exception:
#             return
#         print(self.serial_connection.name)  # check which port was really used
#         self.serial_connection.write(b'hello')  # write a string


#     @property
#     def swing_multiplier(self):
#         # TODO - calculate speed multiplier.
#         return 1

#     def is_new_person_sitting(self):
#         # TODO - define terms for correct sitting disruption.
#         return False

#     def is_disrupt_animation(self):
#         return self.is_new_person_sitting()

#     def get_sample(self):
#         line = None
#         max_tries = 10
#         i = 0
#         while line is None or line == b'' or i > max_tries:
#             line = self.serial_connection.readline()
#             i += 1

#         try:
#             j = json.loads("{" + line.decode("utf-8") + "}")
#             swing_1_acceleration, swing_1_weight, swing_2_acceleration, swing_2_weight = process_line(j)
#         except Exception as e:
#             swing_1_acceleration, swing_1_weight, swing_2_acceleration, swing_2_weight = [1, 1, 1], 1, [1, 1, 1], 1

#         self.swing_1_acceleration.add_sample(swing_1_acceleration)
#         self.swing_2_acceleration.add_sample(swing_2_acceleration)
#         self.swing_1_weight.add_sample(swing_1_weight)
#         self.swing_2_weight.add_sample(swing_2_weight)



def listener():
    while True:
        ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)  # open serial port
        print(ser.name)         # check which port was really used
        ser.write(b'hello')     # write a string

        while 1:
            line = ser.readline()
            if line is None or line == b'':
                break # retry
            try:
                j = json.loads("{"+line.decode("utf-8")+"}")
                if j != {}:
                    process_line(j)
            except:
                pass

            print(line)
        ser.close()             # close port


def draw_worker():
    renderer = Renderer()
    while 1:
        renderer[10] = Line([0,0,0], accel0.last, accel0.color)
        renderer[11] = Line([0,0,0], accel0.down.s, [0,0,1])
        renderer[12] = Line([0,0,0], accel0.avg.s, [0,1,1])
        renderer[20] = Line([0,0,0], accel1.last, accel1.color)
        renderer[21] = Line([0,0,0], accel1.down.s, [0,0,1])
        renderer[22] = Line([0,0,0], accel1.avg.s, [1,1,0])

        # y2 = []
        # y2 = y2  + [[h[0] for h in accel1.avg.history]]
        # y2 = y2  + [[h[1] for h in accel1.avg.history]]
        # y2 = y2  + [[h[2] for h in accel1.avg.history]]
        # renderer.y2 = y2

        renderer.show()


if __name__ == "__main__":
    listener_thread = threading.Thread(target=listener)
    listener_thread.start()

    if drawing_enabled:
        draw_thread = threading.Thread(target=draw_worker)
        draw_thread.start()

    #do yar shit
    listener_thread.join()

