# Stateless functional animator
# https://github.com/qt1/xmastree2020
# Written by baruch@ibn-labs.com
# Enjoy!
import datetime
import sys
import time
import re
import math
from math import sin, cos, pi
from pathlib import Path

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

TIME_PACKET_BYTE_SIZE = 4

# activate simulation if he "--sim" flag is set
if '--sim' in sys.argv:
    print("Simulation Mode - starting")
    from sim import board
    from sim import neopixel
else:
    print("The real tree should light up now!")
    import board
    import neopixel

# the animation loop
coords = []
pixels = {}

def init_rainbow():
    global coords, pixels

    # NOTE THE LEDS ARE GRB COLOUR (NOT RGB)

    # If you want to have user changable values, they need to be entered from the command line
    # so import sys sys and use sys.argv[0] etc
    # some_value = int(sys.argv[0])

    # IMPORT THE COORDINATES (please don't break this bit)
    coordfilename = "coords.txt"
    init_coords_from_file(coordfilename)

    # init_rainbow_coords()

    # set up the pixels (AKA 'LEDs')
    PIXEL_COUNT = len(coords)
    pixels = neopixel.NeoPixel(board.D18, PIXEL_COUNT, auto_write=False)

def init_coords_from_file(coordfilename):
    global coords
    fin = open(coordfilename, 'r')
    coords_raw = fin.readlines()
    coords_bits = [i.split(",") for i in coords_raw]
    coords = []
    for slab in coords_bits:
        new_coord = []
        for i in slab:
            new_coord.append(int(re.sub(r'[^-\d]', '', i)))
        coords.append(new_coord)


NUM_OF_LEDS_PER_STRING = 11
NUM_OF_STRINGS = 1
FPS = 40


def rainbow(duration=60, **kwargs):
    "run space+time animation function fx for a given duration (0=forever) "
    global coords, pixels

    t0 = datetime.datetime.now()
    t_now_seconds = 0
    out_file_name = Path('xlights_recording', 'out_file2')

    with open(out_file_name, mode='rb') as file:  # b is important -> binary
        fileContent = file.read()
        frame_count = 0
        FPS = 40
        bytes_per_frame = TIME_PACKET_BYTE_SIZE + NUM_OF_LEDS_PER_STRING * NUM_OF_STRINGS * 3

        while duration <= 0 or duration >= t_now_seconds:
            t_now = datetime.datetime.now() - t0
            t_now_seconds = t_now.seconds
            t_now_in_millisec = t_now.total_seconds() * 1_000

            frame_start_byte = frame_count * bytes_per_frame
            frame_t_millisec_in_bytes = fileContent[frame_start_byte:frame_start_byte + 4]
            animation_timestamp = int.from_bytes(frame_t_millisec_in_bytes, byteorder='little')

            if animation_timestamp > t_now_in_millisec:
                print(f'{t_now_in_millisec=}')
                continue

            print(f'printing frame - {t_now_in_millisec=}')
            for LED in range(len(coords)):
                led_data = play_rainbow_from_out_file(fileContent, LED, frame_num=frame_count, bytes_per_frame=bytes_per_frame,  **kwargs)
                pixels[LED] = led_data
            frame_count += 1
            pixels.show()


def play_rainbow_from_out_file(byte_data, led_index, frame_num, bytes_per_frame, *args, **kwargs):
    byte_start = bytes_per_frame * (frame_num - 1) + TIME_PACKET_BYTE_SIZE + led_index * 3
    r, g, b = byte_data[byte_start], byte_data[byte_start + 1], byte_data[byte_start + 2]
    return r, b, g


########################## Calling Rendering  #########################
init_rainbow()

print("play Animation from Xlights recording.")
rainbow()




