# Proof of concept, pressure and level in pygame
# 0 = oil, 1 = gas, 2 = water, 3 = pressure, 4 = temperature

import pygame

pygame.init()

wScreen = 1000
hScreen = 800
screen = pygame.display.set_mode((wScreen, hScreen), pygame.RESIZABLE)


class Separator(object):

    def __init__(self, inn_source, x=100, y=100, volume=8, out_source=0):
        self.volumeLeft = 0
        self.pressure = 0
        self.volumeGas = 0
        self.level = 0
        self.levelCubes = 0
        self.width = 300
        self.height = 120

        self.x = x
        self.y = y
        self.volume = volume

        self.inn_source = inn_source
        self.out_source = out_source

        self.flowInnOil = self.inn_source[0]
        self.flowInnGas = self.inn_source[1]

    def draw(self):
        pygame.draw.rect(screen, (85, 85, 85), (self.x, self.y, self.width, self.height))
        self.levelCubes = self.levelCubes + self.flowInnOil / m3h
        self.volumeLeft = self.volume - self.levelCubes
        self.volumeGas = self.volumeGas + self.flowInnGas / m3h

        self.pressure = self.volumeGas / self.volumeLeft
        self.level = self.levelCubes / self.volume * 100


class Transmitter(object):
    def __init__(self, typ, x=200, y=200):
        self.width = 100
        self.height = 50
        self.x = x
        self.y = y
        self.typ = typ

    def draw(self, measuring_point):
        pygame.draw.rect(screen, (75, 75, 75), (self.x, self.y, self.width, self.height))
        font = pygame.font.SysFont('arial', 25, True)
        if self.typ == 'pressure':
            content = font.render('Pressure: ' + str(round(measuring_point.pressure, 2)) + 'Bar', 1, (255, 255, 255))
            screen.blit(content, (self.x, self.y))
        elif self.typ == 'level':
            content = font.render('Level: ' + str(round(measuring_point.level, 2)) + '%', 1, (255, 255, 255))
            screen.blit(content, (self.x, self.y))
        elif self.typ == 'flow':
            content = font.render(str(round(measuring_point, 2)) + 'm3/h', 1, (255, 255, 255))
            screen.blit(content, (self.x, self.y))
        else:
            content = font.render('fault: ' + str(round(measuring_point, 2)) + '%', 1, (255, 255, 255))
            screen.blit(content, (self.x, self.y))


d001 = Separator((5000, 5000), 500, 10)
pi001 = Transmitter('pressure')
li001 = Transmitter('level', 500, 500)


def redraw():
    screen.fill((128, 128, 128))
    d001.draw()
    pi001.draw(d001)
    li001.draw(d001)
    pygame.display.update()


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
        # Makes the window resizable
        if event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

    redraw()

pygame.quit()
