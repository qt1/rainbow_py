import datetime
import sys
from enum import Enum
from pathlib import Path
from time import sleep

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





# Xlights Recording Config
RAINBOW_LEDS = 10 * 7  # num_per_rainbow * rainbows
CLOUD_LEDS = 25 * 2
NUM_OF_LEDS_PER_STRING = RAINBOW_LEDS + CLOUD_LEDS + 1  # One extra led will always be recorded and added to the packet.
NUM_OF_STRINGS = 1
TIME_PACKET_BYTE_SIZE = 4
BYTES_PER_FRAME = TIME_PACKET_BYTE_SIZE + NUM_OF_LEDS_PER_STRING * NUM_OF_STRINGS * 3
FPS = 25
TIME_FOR_FRAME_IN_MILLISECONDS = 1000 / FPS


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
        self.pixels = neopixel.NeoPixel(board.D18, (self.leds_per_string - 1), auto_write=False)

    def play_animation(self, **kwargs):
        t0 = datetime.datetime.now()
        frame_index = 0
        t_now_in_milli_sec = 0

        if self.sequence_type == SequenceTypeChoices.MUSIC:
            self.play_music()

        while frame_index <= self.total_frames:
            animation_timestamp_in_mill_secs = self.get_timestamp_from_frame(frame_index)
            t_now_in_milli_sec = self.get_now_by_sequence_type(animation_timestamp_in_mill_secs,
                                                               frame_index, t0,  t_now_in_milli_sec)

            for LED in range(len(self.pixels.pixels)):
                led_data = self.get_led_from_frame(LED, frame_num=frame_index)
                self.pixels[LED] = led_data
            self.pixels.show()

            frame_index += 1
            if animation_timestamp_in_mill_secs + 25 < t_now_in_milli_sec:
                milliseconds_diff = t_now_in_milli_sec - animation_timestamp_in_mill_secs
                frame_index += int(milliseconds_diff // TIME_FOR_FRAME_IN_MILLISECONDS)

    def get_timestamp_from_frame(self, frame_index):
        frame_start_byte = frame_index * BYTES_PER_FRAME
        frame_t_millisec_in_bytes = self.bytes_data[frame_start_byte:frame_start_byte + 4]
        return int.from_bytes(frame_t_millisec_in_bytes, byteorder='little')

    def get_now_by_sequence_type(self, animation_timestamp_in_mill_secs, frame_index, t0, t_now_in_milli_sec):
        while t_now_in_milli_sec <= animation_timestamp_in_mill_secs:
            if self.sequence_type == SequenceTypeChoices.FRAME:
                swing_multiplier = 1  # TODO - add swing multiplier.
                t_now_in_milli_sec = ((frame_index / FPS) * 1_000 * swing_multiplier) % self.total_frames
            elif self.sequence_type == SequenceTypeChoices.TIME:
                t_now_in_sec = datetime.datetime.now() - t0
                t_now_in_milli_sec = int(t_now_in_sec.total_seconds() * 1_000)
            elif self.sequence_type == SequenceTypeChoices.MUSIC:
                t_now_in_milli_sec = pygame.mixer.music.get_pos()
            sleep(0.001)
        return t_now_in_milli_sec

    def play_music(self):
        pygame.mixer.init()
        pygame.mixer.music.load(self.music_file_path)
        pygame.mixer.music.play()

    def get_led_from_frame(self, led_index, frame_num, *args, **kwargs):
        byte_start = int(BYTES_PER_FRAME * (frame_num - 1) + TIME_PACKET_BYTE_SIZE + led_index * 3)
        r, g, b = self.bytes_data[byte_start], self.bytes_data[byte_start + 1], self.bytes_data[byte_start + 2]
        return g, r, b


if __name__ == '__main__':
    out_file_name = Path('xlights_recording', 'out_file2')

    with open(out_file_name, mode='rb') as file:  # b is important -> binary
        bytes_data = file.read()

        # player = LedPlayer(sequence_type=SequenceTypeChoices.TIME, bytes_data=bytes_data)
        habib_galabi_file_path = Path('data/HabibGalbi.mp3')
        player = LedPlayer(sequence_type=SequenceTypeChoices.MUSIC, bytes_data=bytes_data, music_file_path=habib_galabi_file_path)
        player.play_animation()
