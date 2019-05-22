# Proof of concept, pressure and level in pygame
# 0 = oil, 1 = gas, 2 = water, 3 = pressure, 4 = temperature

import pygame

pygame.init()

wScreen = 1000
hScreen = 800
screen = pygame.display.set_mode((wScreen, hScreen), pygame.RESIZABLE)
fps = 30
m3h = 3600 * fps

class Separator(object):

    def __init__(self, x=100, y=100, volume=8):
        self.volumeLeft = 0
        self.pressure = 0
        self.volumeGas = 0
        self.level = 0
        self.temperature = 0
        self.levelCubes = 0
        self.width = 300
        self.height = 120

        self.x = x
        self.y = y
        self.volume = volume

    def draw(self, oil_inn, gas_inn, water_inn, out_source):
        pygame.draw.rect(screen, (85, 85, 85), (self.x, self.y, self.width, self.height))
        flow_inn_oil = oil_inn.flow * m3h
        flowInnGas = gas_inn.flow * m3h
        flowInnWater = water_inn.flow
        self.levelCubes = self.levelCubes - out_source.flow + flow_inn_oil / m3h
        self.volumeLeft = self.volume - self.levelCubes
        self.volumeGas = self.volumeGas + flowInnGas / m3h

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
            content = font.render('Level: ', 1, (255, 255, 255))
            value = font.render(str(round(measuring_point.level, 2)) + '%', 1, (255, 255, 255))
            screen.blit(content, (self.x + 5, self.y))
            screen.blit(value, (self.x + 5, self.y + 20))
        elif self.typ == 'flow':
            content = font.render(str(round(measuring_point.flow * m3h, 2)) + 'm3/h', 1, (255, 255, 255))
            screen.blit(content, (self.x, self.y))
        else:
            content = font.render('fault: ' + str(round(measuring_point, 2)) + '%', 1, (255, 255, 255))
            screen.blit(content, (self.x, self.y))


class Valve(object):
    def __init__(self, typ, size=2, x=200, y=200):
        self.width = 100
        self.height = 50
        self.opening = 10
        self.flow = 0
        self.size = size
        self.typ = typ
        self.x = x
        self.y = y

    def draw(self, source):
        pygame.draw.rect(screen, (5, 5, 5), (self.x, self.y, self.width, self.height))
        self.flow = self.size * source.pressure * self.opening / m3h


class Dummy(object):
    def __init__(self, flow, pressure):
        self.flow = flow
        self.pressure = pressure


dummy = Dummy(0, 0)
dummy2 = Dummy(50 / m3h, 0)
dummy3 = Dummy(5000 / m3h, 0)
d001 = Separator(500, 10)
pi001 = Transmitter('pressure')
li001 = Transmitter('level', 500, 500)
fv001 = Valve('flow', 2, 500, 600)
fi001 = Transmitter('flow', 500, 650)
d002 = Separator(100, 500)
li002 = Transmitter('level', 400, 750)


def redraw():
    screen.fill((128, 128, 128))

    pi001.draw(d001)
    li001.draw(d001)
    fv001.draw(d001)
    fi001.draw(fv001)
    d001.draw(dummy2, dummy3, dummy2, fv001)
    d002.draw(fv001, dummy2, dummy, dummy)
    li002.draw(d002)

    pygame.display.update()


clock = pygame.time.Clock()

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
