import datetime
import logging

import serial
import json 


WEIGHT_THRESHOLD = 0.002

class Weight:
    w = 0
    samples = 0

    def add_sample(self, s):
        self.w = s
        self.samples += 1

    def is_sitting(self):
        return self.w > WEIGHT_THRESHOLD


class Acceleration:
    a = [0, 0, 0]
    samples = 0
    
    def add_sample(self, s):
        self.a = s
        self.samples += 1

    def get_angle_multiplier(self):
        return 1


class Sensors:
    serial_connection = None

    swing_1_acceleration = Acceleration()
    swing_1_weight = Weight()
    swing_2_acceleration = Acceleration()
    swing_2_weight = Weight()

    def __init__(self):
        try:
            self.serial_connection = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)  # open serial port
        except Exception:
            return
        print(self.serial_connection.name)  # check which port was really used
        self.serial_connection.write(b'hello')  # write a string


    @property
    def swing_multiplier(self):
        # TODO - calculate speed multiplier
        return 1

    def is_disrupt_animation(self):
        # TODO - disrupt when new person sits on an empty swing.
        return False

    def get_sample(self):
        line = None
        max_tries = 10
        i = 0
        while line is None or line == b'' or i > max_tries:
            line = self.serial_connection.readline()
            i += 1

        try:
            j = json.loads("{" + line.decode("utf-8") + "}")
            swing_1_acceleration, swing_1_weight, swing_2_acceleration, swing_2_weight = process_line(j)
        except Exception as e:
            swing_1_acceleration, swing_1_weight, swing_2_acceleration, swing_2_weight = [1, 1, 1], 1, [1, 1, 1], 1

        self.swing_1_acceleration.add_sample(swing_1_acceleration)
        self.swing_2_acceleration.add_sample(swing_2_acceleration)
        self.swing_1_weight.add_sample(swing_1_weight)
        self.swing_2_weight.add_sample(swing_2_weight)



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
                process_line(j)
            except:
                pass

            print(line)
        ser.close()             # close port


#{'HX711_0': {'data': 16659756}, 'HX711_1': {'data': 137991}, 'MPU0': {'ax': -6204, 'ay': -14972, 'az': -1872, 'temp': 1648}, 'MPU1': {'ax': 16228, 'ay': 2912, 'az': -6084, 'temp': 2832}}
def process_line(j):
    swing_1 = j.get('MPU0')
    swing_2 = j.get('MPU1')

    swing_1_acceleration = [1, 1, 1]
    swing_2_acceleration = [1, 1, 1]

    swing_1_weight = 1
    swing_2_weight = 1

    return swing_1_acceleration, swing_1_weight, swing_2_acceleration, swing_2_weight

if __name__ == "__main__":
    listener()
