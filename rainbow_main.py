from pathlib import Path
from random import shuffle

import pygame

from play import LedPlayer, SequenceTypeChoices
from sensors import Sensors

playlist = ['data/HabibGalbi.mp3']
animations = [Path('xlights_recording', 'habib_45_secs')]


if __name__ == '__main__':
    sensors = Sensors()

    shuffle(playlist)
    shuffle(animations)

    for i, music_file_path in enumerate(playlist):
        pygame.mixer.init()
        pygame.mixer.music.load(music_file_path)
        pygame.mixer.music.play()

        out_file_name = animations[i % len(animations)]
        with open(out_file_name, mode='rb') as file:  # b is important -> binary
            bytes_data = file.read()
            led_player = LedPlayer(sequence_type=SequenceTypeChoices.FRAME, bytes_data=bytes_data)
            led_player.play_animation()
