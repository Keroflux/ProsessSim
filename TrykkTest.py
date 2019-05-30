# Proof of concept, pressure and level in pygame
# 0 = oil, 1 = gas, 2 = water, 3 = pressure, 4 = temperature

import pygame

pygame.init()

wScreen = 1000
hScreen = 800
screen = pygame.display.set_mode((wScreen, hScreen), pygame.RESIZABLE)

userFPS = 30
clock = pygame.time.Clock()


class Separator(object):

    def __init__(self, tag, volume=8):
        self.pressure = 0
        self.temperature = 0
        self.volumeGas = 0
        self.volumeLeft = 0

        self.levelOil = 0
        self.cubesOil = 0
        self.levelWater = 0
        self.cubesWater = 0

        self.flowInnOil = 0
        self.flowInnGas = 0
        self.flowInnWater = 0

        self.waterOilSep = 0
        self.gasOilSep = 0

        self.width = 300
        self.height = 120

        self.tag = tag
        self.x = 0
        self.y = 0
        self.volume = volume

    def draw(self, source, out_source, x=10, y=10):
        self.x = x
        self.y = y

        pygame.draw.rect(screen, (85, 85, 85), (self.x, self.y, self.width, self.height))
        font = pygame.font.SysFont('arial', 25, True)
        tag = font.render(str(self.tag), 1, (255, 255, 255))
        screen.blit(tag, (self.x + 5, self.y))
        self.flowInnOil = source.flowOil
        self.flowInnGas = source.flowGas
        self.flowInnWater = source.flowWater

        self.cubesOil = self.cubesOil - out_source.flowOil + self.flowInnOil
        self.volumeLeft = self.volume - self.cubesOil
        self.volumeGas = self.volumeGas + self.flowInnGas

        # TODO: separation efficiency calculation for oil/gas oil/water

        self.pressure = self.volumeGas / self.volumeLeft
        self.levelOil = self.cubesOil / self.volume * 100


class Transmitter(object):

    def __init__(self, typ):
        self.width = 100
        self.height = 50
        self.value = 0
        self.x = 0
        self.y = 0
        self.typ = typ

    def draw(self, measuring_point, x=10, y=10):
        self.x = x
        self.y = y

        pygame.draw.rect(screen, (75, 75, 75), (self.x, self.y, self.width, self.height))
        pygame.draw.line(screen, (255, 255, 255), (self.x + self.width / 2, self.y + self.height),
                         (measuring_point.x, measuring_point.y))

        font = pygame.font.SysFont('arial', 25, True)
        if self.typ == 'pressure':
            content = font.render('Pressure: ' + str(round(measuring_point.pressure, 2)) + 'Bar', 1, (255, 255, 255))
            screen.blit(content, (self.x, self.y))

            self.value = measuring_point.pressure

        elif self.typ == 'level oil':
            content = font.render('Level: ', 1, (255, 255, 255))
            value = font.render(str(round(measuring_point.levelOil, 2)) + '%', 1, (255, 255, 255))
            screen.blit(content, (self.x + 5, self.y))
            screen.blit(value, (self.x + 5, self.y + 20))

            self.value = measuring_point.levelOil

        elif self.typ == 'level water':
            content = font.render('Level: ', 1, (255, 255, 255))
            value = font.render(str(round(measuring_point.levelWater, 2)) + '%', 1, (255, 255, 255))
            screen.blit(content, (self.x + 5, self.y))
            screen.blit(value, (self.x + 5, self.y + 20))

            self.value = measuring_point.flowWater

        elif self.typ == 'flow':
            content = font.render(str(round(measuring_point.flow * m3h, 2)) + 'm3/h', 1, (255, 255, 255))
            screen.blit(content, (self.x, self.y))

            self.value = measuring_point.flow

        else:
            content = font.render('fault: ' + str(round(measuring_point, 2)) + '%', 1, (255, 255, 255))
            screen.blit(content, (self.x, self.y))


class Valve(object):
    def __init__(self, typ, size=2):
        self.width = 100
        self.height = 50

        self.opening = 10

        self.flow = 0
        self.flowOil = 0
        self.flowGas = 0
        self.flowWater = 0

        self.size = size
        self.typ = typ

        self.x = 0
        self.y = 0

    def draw(self, source, out_source, x, y):
        mPos = pygame.mouse.get_pos()  # TODO: fix this
        if clicked:
            self.x = mPos[0]
            self.y = mPos[1]
        else:
            self.x = x
            self.y = y
        pygame.draw.rect(screen, (5, 5, 5), (self.x, self.y, self.width, self.height))
        pygame.draw.line(screen, (255, 255, 255), (self.x, self.y + self.height / 2),
                         (source.x + source.width, source.y + source.height), 4)
        pygame.draw.line(screen, (255, 255, 255), (self.x + self.width, self.y + self.height / 2),
                         (out_source.x, out_source.y + out_source.height), 4)
        if self.typ == 'liquid':
            if source.cubesOil > 0:
                self.flowOil = self.size * source.pressure * self.opening / m3h
                # TODO: flow water and gas calculation
            else:
                self.flowOil = 0

            self.flow = self.flowOil + self.flowWater

        elif self.typ == 'gas':
            self.flowGas = self.size * source.pressure - out_source.pressure * self.opening / m3h
            # TODO: flow water and oil calculation

            self.flow = self.flowGas


class Controller(object):
    def __init__(self, p=10, i=5, d=0):
        self.p = p
        self.i = i
        self.d = d
        self.offsetTime = 0
        self.offset = 0
        self.output = 0
        self.setPoint = 0
        self.x = 0
        self.y = 0

    def draw(self, source, target, x=10, y=10):
        self.x = x
        self.y = y

        self.setPoint = 10
        self.offset = self.setPoint - source.value
        self.output = self.output + self.offset
        target.opening = target.opening + self.output


class Dummy(object):
    def __init__(self, flow_oil, flow_gas, flow_water=0, pressure=0, level=0):
        m3h = 3600 * 30  # TODO: make draw function and get rid of dummy m3h
        self.flowOil = flow_oil / m3h
        self.flowGas = flow_gas / m3h
        self.flowWater = flow_water / m3h
        self.pressure = pressure
        self.levelOil = level


dummy = Dummy(0, 0)
dummy2 = Dummy(50, 5000)
dummy3 = Dummy(5000, 0)

d001 = Separator('d001')
pi001 = Transmitter('pressure')
li001 = Transmitter('level oil')
fv001 = Valve('liquid', 2)
fi001 = Transmitter('flow')
d002 = Separator('d002')
li002 = Transmitter('level oil')


def redraw():

    screen.fill((128, 128, 128))

    pi001.draw(d001, 10, 10)
    li001.draw(d001, 200, 300)
    fv001.draw(d001, d002, 400, 200)
    fi001.draw(fv001, 400, 100)
    d001.draw(dummy2, fv001, 50, 100)
    d002.draw(fv001, dummy, 600, 300)
    li002.draw(d002, 600, 200)

    print(fps)

    pygame.display.update()


clicked = False
run = True

while run:

    trueFPS = clock.get_fps()
    if trueFPS < 1:
        fps = 1
        m3h = 3600 * fps
    else:
        fps = trueFPS
        m3h = 3600 * fps
    clock.tick(userFPS)

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
