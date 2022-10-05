import datetime
import sys
from enum import Enum
from pathlib import Path

import pygame


# activate simulation if he "--sim" flag is set
is_simulation = False
if '--sim' in sys.argv:
    print("Simulation Mode - starting")

    import matplotlib
    matplotlib.use('TkAgg')
    import matplotlib.pyplot as plt

    from sim import board
    from sim import neopixel
    is_simulation = True
else:
    print("The real rainbow should light up now!")
    import board
    import neopixel


# pygame.mixer.init()
# pygame.mixer.music.load('data/HabibGalbi.mp3')
# pygame.mixer.music.play()
# while pygame.mixer.music.get_busy() == True:
#     pass

# Xlights Recording Config
NUM_OF_LEDS_PER_STRING = 11
NUM_OF_STRINGS = 1
TIME_PACKET_BYTE_SIZE = 4
BYTES_PER_FRAME = TIME_PACKET_BYTE_SIZE + NUM_OF_LEDS_PER_STRING * NUM_OF_STRINGS * 3
FPS = 40


class SequenceTypeChoices(Enum):
    MUSIC = 'MUSIC'
    TIME = 'TIME'
    FRAME = 'FRAME'


class LedPlayer:
    def __init__(self, sequence_type: SequenceTypeChoices, bytes_data: bytes,
                 music_file_path: Path = None):
        if sequence_type == SequenceTypeChoices.MUSIC:
            assert music_file_path.exists()
            self.music_file_path = music_file_path
        self.sequence_type = sequence_type

        self.bytes_data = bytes_data
        self.total_frames = len(self.bytes_data) / BYTES_PER_FRAME

        self.leds_per_string = NUM_OF_LEDS_PER_STRING
        self.num_of_strings = NUM_OF_STRINGS
        self.pixels = neopixel.NeoPixel(board.D18, self.leds_per_string - 1, auto_write=False)

    def play_animation(self, **kwargs):
        t0 = datetime.datetime.now()
        frame_count = 0

        while frame_count <= self.total_frames:
            if self.sequence_type == SequenceTypeChoices.FRAME:
                t_now_in_sec = (frame_count / FPS) * 1_000
            elif self.sequence_type == SequenceTypeChoices.TIME:
                t_now_in_sec = datetime.datetime.now() - t0
            elif self.sequence_type == SequenceTypeChoices.MUSIC:
                # TODO - add t_now_in_sec from music player.
                t_now_in_sec = datetime.datetime.now() - t0

            t_now_in_milli_sec = t_now_in_sec.total_seconds() * 1_000
            frame_start_byte = frame_count * BYTES_PER_FRAME


            frame_t_millisec_in_bytes = self.bytes_data[frame_start_byte:frame_start_byte + 4]
            animation_timestamp = int.from_bytes(frame_t_millisec_in_bytes, byteorder='little')


            if animation_timestamp > t_now_in_milli_sec:
                print(f'skipping by time {t_now_in_milli_sec=}')
                continue

            for LED in range(len(self.pixels.pixels)):
                led_data = self.get_led_from_frame(LED, frame_num=frame_count)
                self.pixels[LED] = led_data

            frame_count += 1
            self.pixels.show()


    def get_led_from_frame(self, led_index, frame_num, *args, **kwargs):
        byte_start = BYTES_PER_FRAME * (frame_num - 1) + TIME_PACKET_BYTE_SIZE + led_index * 3
        r, g, b = self.bytes_data[byte_start], self.bytes_data[byte_start + 1], self.bytes_data[byte_start + 2]
        return g, r, b


if __name__ == '__main__':
    out_file_name = Path('xlights_recording', 'out_file2')

    with open(out_file_name, mode='rb') as file:  # b is important -> binary
        bytes_data = file.read()
        player = LedPlayer(sequence_type=SequenceTypeChoices.TIME, bytes_data=bytes_data)
        player.play_animation()
