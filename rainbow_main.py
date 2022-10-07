from os.path import isfile
from pathlib import Path
from random import shuffle

import os
import pygame

from play import LedPlayer, SequenceTypeChoices
from sensors import Sensors


playlist_dir = Path('data/music/')
playlist = [Path(playlist_dir, f) for f in os.listdir(playlist_dir) if isfile(Path(playlist_dir, f))]
# playlist = [Path('data/HabibGalbi.mp3')]

animations_dir = Path('data/animations/')
# animations = [Path('xlights_recording', 'habib_45_secs')]
animations = [Path(animations_dir, f) for f in os.listdir(animations_dir) if isfile(Path(animations_dir, f))]

if __name__ == '__main__':
    sensors = Sensors()

    shuffle(playlist)
    shuffle(animations)

    led_player = None
    for i, music_file_path in enumerate(playlist):
        out_file_name = animations[i % len(animations)]
        try:
            bytes_data = None
            with open(out_file_name, mode='rb') as file:  # b is important -> binary
                bytes_data = file.read()
            led_player = LedPlayer(sequence_type=SequenceTypeChoices.FRAME, bytes_data=bytes_data, music_file_path=music_file_path, sensors=sensors)
            led_player.play_animation()
        except Exception as e:
            LedPlayer.stop_music()
            if led_player:
                led_player.turn_off_leds()
                led_player = None
