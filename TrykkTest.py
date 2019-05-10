# Testing av beregning av trykk og nivå i

import pygame
import math

pygame.init()

wScreen = 1000
hScreen = 800
screen = pygame.display.set_mode((wScreen, hScreen))


class Separator(object):
    pressure = 0
    level = 0
    flowInn = 5000
    volumeGas = 8
    volumeLef = 0

    def __init__(self, tag, inn_source, x=100, y=100, volume=8):
        self.width = 100
        self.height = 40
        self.x = x
        self.y = y
        self.volume = volume
        self.tag = tag
        self.inn_source = inn_source

    def draw(self):
        pygame.draw.rect(screen, (65, 65, 65), (self.x, self.y, self.width, self.height))
        self.volumeLef = self.volume
        self.volumeGas = self.volumeGas + self.flowInn / m3h
        self.pressure = self.volumeGas / self.volumeLef


class Transmitter(object):
    def __init__(self, typ, tag, x=100, y=100):
        self.width = 10
        self.height = 10
        self.x = x
        self.y = y
        self.tag = tag
        self.typ = typ

    def draw(self, measuring_point):
        pygame.draw.rect(screen, (75, 75, 75), (self.x, self.y, self.width, self.height))
        font = pygame.font.SysFont('arial', 30, True)
        if self.typ == 'pressure':
            content = font.render('Bar: ' + str(round(measuring_point, 2)), 1, (255, 255, 255))
            screen.blit(content, (self.x, self.y))
        elif self.typ == 'level':
            content = font.render('Level: ' + str(round(measuring_point / volume * 100, 2)) + '%', 1, (255, 255, 255))
            screen.blit(content, (self.x, self.y))
        else:
            content = font.render('fault: ' + str(round(measuring_point, 2)) + '%', 1, (255, 255, 255))
            screen.blit(content, (self.x, self.y))


'''def transmitter(unit, x, y):
    font = pygame.font.SysFont('arial', 30, True)
    if unit == pressure:
        content = font.render('Bar: ' + str(round(unit, 2)), 1, (255, 255, 255))
        screen.blit(content, (x, y))
    elif unit == level:
        content = font.render('Level: ' + str(round(unit / volume * 100, 2)) + '%', 1, (255, 255, 255))
        screen.blit(content, (x, y))'''


d001 = Separator('d001', 100, 500, 10)
pi001 = Transmitter('pressure', 'pi001', d001.pressure)


def redraw():
    screen.fill((128, 128, 128))
    #transmitter(pressure, 100, 300)
    #transmitter(level, 100, 100)
    d001.draw()
    pi001.draw(d001.pressure)
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
m3h = 3600 * fps
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
    volumeGas = volumeGas + flowGas / m3h
    pressure = volumeGas / volumeLeft
    level = level + flowLiquid / m3h / volume
    volumeLeft = volume - level
    print(d001.pressure)
    redraw()

pygame.quit()
