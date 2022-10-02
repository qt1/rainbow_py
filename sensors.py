import serial
import json 

class Weight:
    w = 0
    samples =0

    def add_sample(self, s):
        w = s

class Acceleration:
    a = [0,0,0]
    samples =0
    
    def add_sample(self, s):
        w = s

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
    pass

if __name__ == "__main__":
    listener()