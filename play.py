import pygame
import time
pygame.mixer.init()
pygame.mixer.music.load('data/HabibGalbi.mp3')
pygame.mixer.music.play()
while pygame.mixer.music.get_busy() == True:
    pass