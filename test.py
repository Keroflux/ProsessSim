# Proof of concept, pressure and level in pygame
# 0 = oil, 1 = gas, 2 = water, 3 = pressure, 4 = temperature

import pygame

pygame.init()

wScreen = 1000
hScreen = 800
screen = pygame.display.set_mode((wScreen, hScreen), pygame.RESIZABLE)

userFPS = 30
clock = pygame.time.Clock()

panX = 0
panY = 0
zoom = 1


class Separator(object):

    def __init__(self, tag, volume=8):
        self.pressure = 1
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
        self.x = x + panX
        self.y = y + panY
        self.width = 300
        self.height = 120

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
        self.x = x + panX
        self.y = y + panY

        pygame.draw.rect(screen, (75, 75, 75), (self.x, self.y, self.width, self.height))
        pygame.draw.line(screen, (255, 255, 255), (self.x + self.width / 2, self.y + self.height),
                         (measuring_point.x, measuring_point.y))

        font = pygame.font.SysFont('arial', 25, True)
        if self.typ == 'pressure':
            content = font.render(str(round(measuring_point.pressure, 2)) + 'Bar', 1, (255, 255, 255))
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
            self.x = mPos[0] + panX
            self.y = mPos[1] + panY
        else:
            self.x = x + panX
            self.y = y + panY

        if self.opening < 0:
            self.opening = 0

        pygame.draw.rect(screen, (5, 5, 5), (self.x, self.y, self.width, self.height))

        pygame.draw.line(screen, (255, 255, 255), (self.x, self.y + self.height / 2),
                         (self.x - 50, self.y + self.height / 2), 4)
        pygame.draw.line(screen, (255, 255, 255), (self.x - 50, self.y + self.height / 2),
                         (self.x - 50, source.y + source.height - 4), 4)
        pygame.draw.line(screen, (255, 255, 255), (self.x - 50, source.y + source.height - 4),
                         (source.x + source.width - 2, source.y + source.height - 4), 4)

        pygame.draw.line(screen, (255, 255, 255), (self.x + self.width, self.y + self.height / 2),
                         (self.x + self.width + 50, self.y + self.height / 2), 4)
        pygame.draw.line(screen, (255, 255, 255), (self.x + self.width + 50, self.y + self.height / 2),
                         (self.x + self.width + 50, out_source.y + out_source.height - 4), 4)
        pygame.draw.line(screen, (255, 255, 255), (self.x + self.width + 50, out_source.y + out_source.height - 4),
                         (out_source.x, out_source.y + source.height - 4), 4)

        font = pygame.font.SysFont('arial', 25, True)
        opening = font.render(str(round(self.opening, 2)) + '%', 1, (255, 255, 255))
        screen.blit(opening, (self.x + 5, self.y))
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
    def __init__(self):
        self.p = 0
        self.i = 0
        self.d = 0
        self.pid = 0
        self.offsetTime = 0
        self.offset = 0
        self.output = 0
        self.setPoint = 0
        self.x = 0
        self.y = 0
        self.dProcessValue = [0, 0]  # List that stores the two last values
        self.dOffset = [0, 0]  # List that stores the two last offset values

    def draw(self, source, target, x=10, y=10, p_value=5, i_value=2, d_value=5):
        self.x = x + panX
        self.y = y + panY

        self.setPoint = 3
        self.offset = self.setPoint - source.value
        # Stores the two last values in a list and calculates delta
        self.dProcessValue.append(source.value)
        if len(self.dProcessValue) > 2:
            self.dProcessValue.pop(0)
        dpv = (self.dProcessValue[1] - self.dProcessValue[0]) / timeStep

        self.dOffset.append(self.offset)
        if len(self.dOffset) > 2:
            self.dOffset.pop(0)
        dof = (self.dOffset[1] - self.dOffset[0]) * timeStep

        self.p = p_value * self.offset
        self.i = p_value / i_value * dof
        self.d = - p_value * d_value * dpv
        self.pid = self.p + self.i + self.d

        self.output = self.pid * timeStep

        target.opening = target.opening - self.output
        if target.opening < 0:
            target.opening = 0
        elif target.opening > 100:
            target.opening = 100


class Dummy(object):
    def __init__(self):
        self.flowOil = 0
        self.flow = 0
        self.flowGas = 0
        self.flowWater = 0
        self.pressure = 0
        self.levelOil = 0
        self.x = 10
        self.y = 10

    def draw(self, flow_oil=50, flow_gas=5000, flow_water=0, pressure=0, level=0):
        self.flowOil = flow_oil / m3h
        self.flowGas = flow_gas / m3h
        self.flowWater = flow_water / m3h
        self.flow = 50 / m3h
        self.pressure = pressure
        self.levelOil = level


dummy = Dummy()
dummy2 = Dummy()
dummy3 = Dummy()

d001 = Separator('d001')
pi001 = Transmitter('pressure')
li001 = Transmitter('level oil')
fv001 = Valve('liquid', 1)
fi001 = Transmitter('flow')
d002 = Separator('d002')
li002 = Transmitter('level oil')
fi002 = Transmitter('flow')
lic001 = Controller()


def redraw():

    screen.fill((128, 128, 128))

    dummy.draw(0, 0)
    dummy2.draw(50, 5000)
    dummy3.draw(5000, 0)

    pi001.draw(d001, 10, 10)
    li001.draw(d001, 200, 300)
    fv001.draw(d001, d002, 450, 300)
    fi001.draw(fv001, 400, 100)
    d001.draw(dummy2, fv001, 50, 100)
    d002.draw(fv001, dummy, 700, 300)
    li002.draw(d002, 600, 200)
    lic001.draw(li001, fv001)

    # FPS and sim-speed
    font = pygame.font.SysFont('arial', 15, False)
    hz = font.render(str(round(trueFPS, 2)) + 'Hz', 1, (0, 0, 0))
    screen.blit(hz, (300, 5))

    font = pygame.font.SysFont('arial', 15, False)
    pros = font.render(str(round(p, 2)) + '%', 1, (0, 0, 0))
    screen.blit(pros, (360, 5))

    pygame.display.update()


clicked = False
run = True

while run:

    clock.tick(userFPS)

    trueFPS = clock.get_fps()
    p = trueFPS / userFPS * 100
    if trueFPS < 0.1:
        timeStep = 1 / userFPS
        m3h = 3600 * userFPS
    else:
        m3h = 3600 * trueFPS
        timeStep = 1 / trueFPS

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            clicked = True
            if event.button == 4:
                zoom = zoom + 1
                print('zoom inn')
            if event.button == 5:
                zoom = zoom - 1
                print('zoom out')
        elif event.type == pygame.MOUSEBUTTONUP:
            clicked = False
        # Makes the window resizable
        if event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

    keys = pygame.key.get_pressed()
    for key in keys:
        if keys[pygame.K_LEFT]:
            panX = panX - 0.01
        if keys[pygame.K_RIGHT]:
            panX = panX + 0.01
        if keys[pygame.K_UP]:
            panY = panY - 0.01
        if keys[pygame.K_DOWN]:
            panY = panY + 0.01

    redraw()

pygame.quit()
