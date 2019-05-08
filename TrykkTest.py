# Testing av beregning av trykk og nivå i

import pygame
import math

pygame.init()

wScreen = 1000
hScreen = 800
screen = pygame.display.set_mode((wScreen, hScreen))


class Separator(object):
    def __init__(self, tag, x=100, y=100, volume=8):
        self.width = 100
        self.height = 40
        self.x = x
        self.y = y
        self.volume = volume
        self.tag = tag

    def draw(self):
        pygame.draw.rect(screen, (65, 65, 65), (self.x, self.y, self.width, self.height))


def transmitter(unit, x, y):
    font = pygame.font.SysFont('arial', 30, True)
    if unit == pressure:
        content = font.render('Bar: ' + str(round(unit, 2)), 1, (255, 255, 255))
        screen.blit(content, (x, y))
    elif unit == level:
        content = font.render('Level: ' + str(round(unit / volume * 100, 2)) + '%', 1, (255, 255, 255))
        screen.blit(content, (x, y))


d001 = Separator('d001', 100, 500, 10)


def redraw():
    screen.fill((128, 128, 128))
    transmitter(pressure, 100, 300)
    transmitter(level, 100, 100)
    d001.draw()
    pygame.display.update()


# Pressure and simulation
flowGas = 1000
flowLiquid = 500
volume = 8
volumeGas = 8
pressure = 0
level = 0
volumeLeft = volume

clock = pygame.time.Clock()
fps = 30
run = True
while run:
    clock.tick(fps)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            clicked = True
        elif event.type == pygame.MOUSEBUTTONUP:
            clicked = False

    # Pressure and simulation
    m3h = 3600 * fps
    volumeGas = volumeGas + flowGas / m3h
    pressure = volumeGas / volumeLeft
    level = level + flowLiquid / m3h / volume
    volumeLeft = volume - level
    redraw()

pygame.quit()
