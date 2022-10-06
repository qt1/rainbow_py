from pathlib import Path
from random import shuffle

import pygame

from play import LedPlayer, SequenceTypeChoices
from sensors import Sensors

playlist = [Path('data/HabibGalbi.mp3')]
animations = [Path('xlights_recording', 'habib_45_secs')]


if __name__ == '__main__':
    sensors = Sensors()

    shuffle(playlist)
    shuffle(animations)

    led_player = None
    for i, music_file_path in enumerate(playlist):
        out_file_name = animations[i % len(animations)]
        try:
            with open(out_file_name, mode='rb') as file:  # b is important -> binary
                bytes_data = file.read()
                led_player = LedPlayer(sequence_type=SequenceTypeChoices.FRAME, bytes_data=bytes_data, music_file_path=music_file_path, sensors=sensors)
                led_player.play_animation()
        except Exception as e:
            LedPlayer.stop_music()
            if led_player:
                led_player.turn_off_leds()
                led_player = None
