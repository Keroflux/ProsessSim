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
    levelActual = 0
    volumeGas = 0
    volumeLeft = 0

    def __init__(self, tag, inn_source, x=100, y=100, volume=8):
        self.width = 100
        self.height = 40
        self.x = x
        self.y = y
        self.volume = volume
        self.tag = tag
        self.inn_source = inn_source
        self.flowInnGas = self.inn_source[1]
        self.flowInnOil = self.inn_source[0]

    def draw(self):
        pygame.draw.rect(screen, (65, 65, 65), (self.x, self.y, self.width, self.height))
        self.levelActual = self.levelActual + self.flowInnOil / m3h
        self.volumeLeft = self.volume - self.levelActual
        self.volumeGas = self.volumeGas + self.flowInnGas / m3h

        self.pressure = self.volumeGas / self.volumeLeft
        if self.levelActual < self.volume:
            self.level = self.levelActual / self.volume
        else:
            self.levelActual = self.volume
            self.volumeLeft = 0


class Transmitter(object):
    def __init__(self, typ, tag, x=200, y=200):
        self.width = 100
        self.height = 50
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
            content = font.render('Level: ' + str(round(measuring_point * 100, 2)) + '%', 1, (255, 255, 255))
            screen.blit(content, (self.x, self.y))
        else:
            content = font.render('fault: ' + str(round(measuring_point, 2)) + '%', 1, (255, 255, 255))
            screen.blit(content, (self.x, self.y))


d001 = Separator('d001', (5000, 5000), 500, 10)
pi001 = Transmitter('pressure', 'pi001')
li001 = Transmitter('level', 'li001', 500, 500)


def redraw():
    screen.fill((128, 128, 128))
    d001.draw()
    pi001.draw(d001.pressure)
    li001.draw(d001.level)
    pygame.display.update()
    print(d001.volumeLeft)


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

    redraw()

pygame.quit()
