import datetime
import sys
from enum import Enum
from pathlib import Path
from time import sleep

import pygame


# activate simulation if he "--sim" flag is set
from sensors import Sensors

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
LARGE_RAINBOW_LEDS = 10 * 7  # num_per_rainbow * rainbows
SMALL_RAINBOW_LEDS = 7 * 7  # num_per_rainbow * rainbows
CLOUD_LEDS = 25 * 2
TOTAL_NUM_OF_LEDS = LARGE_RAINBOW_LEDS + SMALL_RAINBOW_LEDS + CLOUD_LEDS  # One extra led will always be recorded and added to the packet.

TIME_PACKET_BYTE_SIZE = 4

BYTES_PER_FRAME = TIME_PACKET_BYTE_SIZE + (TOTAL_NUM_OF_LEDS + 1) * 3   # One extra led will always be recorded and added to the packet.

FPS = 25
TIME_FOR_FRAME_IN_MILLISECONDS = 1000 / FPS


class SequenceTypeChoices(Enum):
    MUSIC = 'MUSIC'
    TIME = 'TIME'
    FRAME = 'FRAME'


def diff_in_milli_secs(t0: datetime.datetime, t1: datetime.datetime) -> int:
    diff = t1 - t0
    return int(diff.total_seconds() * 1000)


class LedPlayer:
    def __init__(self, sequence_type: SequenceTypeChoices, bytes_data: bytes,
                 music_file_path: Path = None, sensors: Sensors = None):
        self.sequence_type = sequence_type

        if music_file_path:
            assert music_file_path.exists()
            self.music_file_path = music_file_path
            pygame.mixer.init()

        if sensors:
            self.sensors = sensors

        self.bytes_data = bytes_data
        self.total_frames = len(self.bytes_data) / BYTES_PER_FRAME

        self.total_num_of_leds = TOTAL_NUM_OF_LEDS
        self.pixels = neopixel.NeoPixel(board.D18, (self.total_num_of_leds), auto_write=False)
        self.fps = FPS

    def play_animation(self, **kwargs):
        if self.sequence_type == SequenceTypeChoices.FRAME:
            self.play_animation_by_fps()
            return

        t0 = datetime.datetime.now()
        frame_index = 0
        t_now_in_milli_sec = 0

        if self.sequence_type == SequenceTypeChoices.MUSIC:
            self.play_music()

        while frame_index <= self.total_frames:
            animation_timestamp_in_mill_secs = self.get_timestamp_from_frame(frame_index)
            t_now_in_milli_sec = self.get_now_by_sequence_type(animation_timestamp_in_mill_secs,
                                                               frame_index, t0,  t_now_in_milli_sec)
            self.show_led_frame(frame_index)

            frame_index += 1
            if animation_timestamp_in_mill_secs + TIME_FOR_FRAME_IN_MILLISECONDS < t_now_in_milli_sec:
                milliseconds_diff = t_now_in_milli_sec - animation_timestamp_in_mill_secs
                frame_index += int(milliseconds_diff // TIME_FOR_FRAME_IN_MILLISECONDS)

    def show_led_frame(self, frame_index, turn_off=False):
        for LED in range(len(self.pixels.pixels)):
            led_data = self.get_led_from_frame(LED, frame_num=frame_index) if not turn_off else [0, 0, 0]
            self.pixels[LED] = led_data
        self.pixels.show()

    def turn_off_leds(self):
        for LED in range(len(self.pixels.pixels)):
            self.pixels[LED] = [0, 0, 0]
        self.pixels.show()

    def get_timestamp_from_frame(self, frame_index):
        frame_start_byte = frame_index * BYTES_PER_FRAME
        frame_t_millisec_in_bytes = self.bytes_data[frame_start_byte:frame_start_byte + 4]
        return int.from_bytes(frame_t_millisec_in_bytes, byteorder='little')

    def get_now_by_sequence_type(self, animation_timestamp_in_mill_secs, frame_index, t0, t_now_in_milli_sec):
        t0 = datetime.datetime.now()
        while t_now_in_milli_sec <= animation_timestamp_in_mill_secs:
            if self.sequence_type == SequenceTypeChoices.FRAME:
                t_now_in_milli_sec = pygame.mixer.music.get_pos()
            elif self.sequence_type == SequenceTypeChoices.TIME:
                t_now_in_sec = datetime.datetime.now() - t0
                t_now_in_milli_sec = int(t_now_in_sec.total_seconds() * 1_000)
            elif self.sequence_type == SequenceTypeChoices.MUSIC:
                t_now_in_milli_sec = pygame.mixer.music.get_pos()
            sleep(0.001)
        return t_now_in_milli_sec

    def play_music(self):
        pygame.mixer.music.load(self.music_file_path)
        pygame.mixer.music.play()

    @classmethod
    def stop_music(cls):
        pygame.mixer.music.stop()

    def get_led_from_frame(self, led_index, frame_num, *args, **kwargs):
        byte_start = int(BYTES_PER_FRAME * (frame_num - 1) + TIME_PACKET_BYTE_SIZE + led_index * 3)
        r, g, b = self.bytes_data[byte_start], self.bytes_data[byte_start + 1], self.bytes_data[byte_start + 2]
        return g, r, b

    def play_animation_by_fps(self):
        frame_i = 0
        t0 = datetime.datetime.now()
        self.play_music()

        while pygame.mixer.music.get_busy():
            ttf = 1_000 // self.fps  # time to frame in milli secs
            last_show_frame_time = datetime.datetime.now()
            self.show_led_frame(frame_index=frame_i % self.total_frames)
            while diff_in_milli_secs(t0=last_show_frame_time, t1=datetime.datetime.now()) < ttf:
                sleep(0.001)
            frames_diff = diff_in_milli_secs(t0=last_show_frame_time, t1=datetime.datetime.now()) // ttf
            frame_i += frames_diff
            self.fps = 25
            if self.sensors and self.sensors.is_distrupt_animation():
                raise Exception('Distrupted by sensors.')


if __name__ == '__main__':
    out_file_name = Path('xlights_recording', 'habib_45_secs')

    with open(out_file_name, mode='rb') as file:  # b is important -> binary
        bytes_data = file.read()

        # player = LedPlayer(sequence_type=SequenceTypeChoices.TIME, bytes_data=bytes_data)
        habib_galabi_file_path = Path('data/HabibGalbi.mp3')
        player = LedPlayer(sequence_type=SequenceTypeChoices.FRAME, bytes_data=bytes_data, music_file_path=habib_galabi_file_path)
        player.play_animation()
