# Proof of concept, pressure and level in pygame
# 0 = oil, 1 = gas, 2 = water, 3 = pressure, 4 = temperature

import pygame
#import sgc

pygame.init()

wScreen = 1200
hScreen = 800
panX = 0
panY = 0
zoom = 1

ambientTemperature = 20

pause = False
clicked = False
rClicked = False
lClicked = False
edit = False
clickCount = 0

adjPosX = 1
adjPosY = 1

tagInfo = 'blank'


screen = pygame.display.set_mode((wScreen, hScreen), pygame.RESIZABLE)
#screen = sgc.surface.Screen((640,480))

userFPS = 30
clock = pygame.time.Clock()


class Separator(object):

    def __init__(self, tag, volume=8, volume_water_chamber=4):
        self.width = 300
        self.height = 120
        self.x = 0
        self.y = 0

        self.id = 'separator'
        self.tag = tag

        self.volume = volume
        self.volume_water_chamber = volume_water_chamber
        self.pressure = 1
        self.temperature = 0
        self.volumeGas = 0
        self.volumeLeft = 0

        self.levelOil = 0
        self.cubesOil = 0
        self.levelWater = 0
        self.cubesWater = 0

        self.waterInOil = 0
        self.gasInOil = 0
        self.oilInGas = 0

        self.newX = 0
        self.newY = 0
        self.clicked = False
        self.rect = 0

    def draw(self, source, out_source, x=10, y=10):
        global tagInfo
        self.width = 300
        self.height = 120
        # TODO: fix temp calc
        td = source.temperature / ambientTemperature
        self.temperature = source.temperature - td

        pipe(self, out_source, 4)
        move(self, x, y)

        self.rect = pygame.draw.rect(screen, (85, 85, 85), (self.x, self.y, self.width, self.height))

        if self.rect.collidepoint(mPos) and rClicked and edit:
            tagInfo = self.tag
            pygame.draw.rect(screen, (255, 255, 255), (mPos[0], mPos[1], 100, 50))

        font = pygame.font.SysFont('arial', 25, True)
        tag = font.render(str(self.tag), 1, (255, 255, 255))
        screen.blit(tag, (self.x + 5, self.y))

        if not pause:
            if self.levelWater >= 1:
                self.cubesOil = self.cubesOil + source.flowOil + source.flowWater - out_source.flowOil
            else:
                self.cubesOil = self.cubesOil - out_source.flowOil + source.flowOil

            self.cubesWater = self.cubesWater - out_source.flowWater + source.flowWater
            self.volumeLeft = self.volume - self.cubesOil + self.cubesWater
            self.volumeGas = self.volumeGas + source.flowGas - out_source.flowGas

            self.pressure = self.volumeGas / self.volumeLeft

            # TODO: separation efficiency calculation oil in water(draft), oil in gas, gas in oil(draft)
            # Oil level
            if 100 > self.levelOil > 0:
                self.levelOil = self.cubesOil / self.volume * 100
                # Gas in oil calc
                self.gasInOil = self.pressure / self.volume
            elif self.levelOil <= 0:
                self.cubesOil = 0 + source.flowOil
                self.levelOil = self.cubesOil / self.volume * 100
            else:
                self.levelOil = 100
                # Gas in oil calc
                self.gasInOil = self.pressure / self.levelOil / self.volume

            # Water level
            if 100 > self.levelWater > 0:
                self.levelWater = self.cubesWater / self.volume_water_chamber * 100
                # Water in oil calc
                self.waterInOil = self.levelWater * (source.flowOil + source.flowWater) / self.volume * (trueFPS / 2)
            elif self.levelWater <= 0:
                self.levelWater = 0
                self.levelWater = self.cubesWater / self.volume_water_chamber * 100
            else:
                self.levelWater = 100
                # Water in oil calc
                self.waterInOil = source.flowWater / source.flowOil


class Transmitter(object):

    def __init__(self, typ, tag):
        self.id = 'transmitter'
        self.width = 100
        self.height = 50
        self.value = 0
        self.x = 0
        self.y = 0
        self.typ = typ
        self.tag = tag

        self.newX = 0
        self.newY = 0
        self.clicked = False
        self.rect = 0

    def draw(self, measuring_point, x=10, y=10):

        move(self, x, y)

        self.rect = pygame.draw.rect(screen, (75, 75, 75), (self.x, self.y, self.width, self.height))
        pygame.draw.line(screen, (255, 255, 255), (self.x + self.width / 2, self.y + self.height),
                         (self.x + self.width / 2, measuring_point.y))

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

            self.value = measuring_point.levelWater

        elif self.typ == 'flow':
            content = font.render(str(round(measuring_point.flow * m3h, 2)) + 'm3/h', 1, (255, 255, 255))
            screen.blit(content, (self.x, self.y))

            self.value = measuring_point.flow

        else:
            content = font.render('fault: ' + str(round(measuring_point, 2)) + '%', 1, (255, 255, 255))
            screen.blit(content, (self.x, self.y))


class Valve(object):
    def __init__(self, typ, size=2):
        self.id = 'valve'
        self.width = 100
        self.height = 50

        self.opening = 10

        self.flow = 0
        self.flowOil = 0
        self.flowGas = 0
        self.flowWater = 0
        self.dP = 0
        self.temperature = 0

        self.size = size
        self.typ = typ

        self.x = 0
        self.y = 0
        self.newX = 0
        self.newY = 0
        self.clicked = False
        self.rect = 0

    def draw(self, source, out_source, x, y):
        self.dP = source.pressure - out_source.pressure

        move(self, x, y)

        if self.opening < 0:
            self.opening = 0

        pipe(self, out_source, 4)

        self.rect = pygame.draw.rect(screen, (5, 5, 5), (self.x, self.y, self.width, self.height))

        font = pygame.font.SysFont('arial', 25, True)
        opening = font.render(str(round(self.opening, 2)) + '%', 1, (255, 255, 255))
        screen.blit(opening, (self.x + 5, self.y))

        # TODO: fix calculations
        if not pause:
            if self.typ == 'oil':
                if source.cubesOil > 0:
                    self.flowOil = self.size * self.dP * self.opening / m3h
                    self.flowGas = self.flowOil * source.gasInOil
                    self.flowWater = self.flowOil * source.waterInOil
                    # TODO: flow water and gas calculation
                else:
                    self.flowOil = 0
                    self.flowGas = self.size * self.dP * self.opening / m3h

                self.flow = self.flowOil

            elif self.typ == 'gas':
                self.flowGas = self.size * self.dP * self.opening / m3h
                # TODO: flow water and oil calculation

                self.flow = self.flowGas

            elif self.typ == 'water':
                if source.cubesWater > 0:
                    self.flowWater = self.size * self.dP * self.opening / m3h
                else:
                    self.flowWater = 0
                    if source.cubesOil > 0:
                        self.flowOil = self.size * self.dP * self.opening / m3h
                        self.flowGas = self.flowOil * source.gasInOil


class Controller(object):
    def __init__(self):
        self.id = 'controller'
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

    def draw(self, source, target, x=10, y=10, p_value=5, i_value=10, d_value=5):
        self.x = x + panX
        self.y = y + panY

        self.setPoint = 3

        if not pause:
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
        self.id = 'dummy'
        self.flowOil = 0
        self.flow = 0
        self.flowGas = 0
        self.flowWater = 0
        self.pressure = 0
        self.levelOil = 0
        self.temperature = 70
        self.x = 10
        self.y = 10
        self.opening = 0

    def draw(self, flow_oil=50, flow_gas=5000, flow_water=0, pressure=0, level=0):
        self.flowOil = flow_oil / m3h
        self.flowGas = flow_gas / m3h
        self.flowWater = flow_water / m3h
        self.flow = 50 / m3h
        self.pressure = pressure
        self.levelOil = level


# Draw default stuff
dummy = Dummy()
dummy2 = Dummy()
dummy3 = Dummy()

d001 = Separator('d001')
pi001 = Transmitter('pressure', 'pi001')
li001 = Transmitter('level oil', 'li001')
li003 = Transmitter('level water', 'li003')
fv001 = Valve('oil', 1)
fi001 = Transmitter('flow', 'fi001')
d002 = Separator('d002', 80)
li002 = Transmitter('level oil', 'li002')
fi002 = Transmitter('flow', 'fi002')
lic001 = Controller()

#btn = sgc.Button(label='click', pos=(1000, 200))
#btn.add(0)


# Functions
def pipe(start, end, size):

    y1 = 2
    y2 = 2
    x1 = 1

    if start.id == 'valve':
        y1 = start.height / 2
        x1 = start.x + start.width + 50
    elif start.id == 'separator':
        y1 = start.height - size
        x1 = end.x - 50

    if end.id == 'separator':
        y2 = end.height - size
    elif end.id == 'valve':
        y2 = end.height / 2

    # Draw pipes
    if end.id != 'dummy':
        pygame.draw.line(screen, (255, 255, 255), (start.x + start.width - 2, start.y + y1), (x1, start.y + y1), size)
        pygame.draw.line(screen, (255, 255, 255), (x1, start.y + y1), (x1, end.y + y2), size)
        pygame.draw.line(screen, (255, 255, 255), (x1, end.y + y2), (end.x, end.y + y2), size)


def move(self, x, y):        # Function for moving assets
    global adjPosX, adjPosY
    if not self.clicked:
        self.x = x + panX
        self.y = y + panY
    if self.clicked and not edit:
        self.x = self.newX + panX
        self.y = self.newY + panY
    if edit and self.rect.collidepoint(mPos):
        self.x = self.x
        self.y = self.y
                
        if not lClicked:
            adjPosX = (mPos[0] - self.x) / self.width
            adjPosY = (mPos[1] - self.y) / self.height
        elif lClicked:
            self.clicked = True
            self.x = mPos[0] - self.width * adjPosX
            self.y = mPos[1] - self.height * adjPosY
            self.newX = self.x - panX
            self.newY = self.y - panY


# Drawing from dictionaris
separator = {}             # Stores int values for the class
separatorDraw = {}         # Stores values for drawing

transmitter = {}
transmitterSetting = []
transmitterDraw = []


def new_sep(tag='ddd', volume=8, volume_water=4, source=dummy2, out_source=fv001, x=1000, y=100):
    separator.setdefault(tag, Separator(tag, volume, volume_water))
    separatorDraw.setdefault(tag, [source, out_source, x, y])


def new_transmitter(tag='lll', typ='level oil', x=100, y=100, source=dummy):
    transmitter.setdefault(tag, Transmitter(typ, tag))
    transmitterSetting.append((source, x, y))
    transmitterDraw.append(transmitter.get(tag))


def draw_sep():
    for sep in separatorDraw:
        separator.get(sep).draw(separatorDraw.get(sep)[0], separatorDraw.get(sep)[1],
                                separatorDraw.get(sep)[2], separatorDraw.get(sep)[3])
    

def update_sep(self):
    tag = self.tag
    separator.update({tag: Separator(tag, volume, volume_water)})


def draw_transmitter():
    for i in range(len(transmitterDraw)):
        transmitterDraw[i].draw(transmitterSetting[i][0], transmitterSetting[i][1], transmitterSetting[i][2])


def pause_sim():
    global pause
    if pause:
        pause = False
    else:
        pause = True


def button(x, y, width, height, msg='BUTTON', func=None):
    global clickCount
    rect = pygame.draw.rect(screen, (0, 100, 0), (x, y, width, height))
    font = pygame.font.SysFont('arial', 25, True)
    text = font.render((str(msg)), 1, (255, 255, 255))
    screen.blit(text, (rect.center[0], rect.center[1]))

    if clicked and rect.collidepoint(mPos) and clickCount == 0:
        new_sep('dpp3', 8, 4, dummy2, fv001, 500, 200)
        s = input()
        s = separator.get(s)
        new_transmitter('111', 'level oil', 100, 100, s)
        clickCount += 1


def is_mouse_inside(x, y, width, height):
    m_pos = pygame.mouse.get_pos()
    if x < m_pos[0] < x + width and y < m_pos[1] < y + height:
        return True


# Drawing from dictionaries
new_sep('dpp1', 8, 4, dummy2, fv001, 500, 500)
new_sep('dpp2', 8, 4, dummy2, fv001, 10, 500)

def redraw():

    screen.fill((128, 128, 128))
    dummy.draw(0, 0)
    dummy2.draw(50, 5000, 30)
    dummy3.draw(5000, 0)
    button(rW / 3, rH - 50, 100, 50, 'test')

    pi001.draw(d001, 10, 10)
    li001.draw(d001, 200, 300)
    fv001.draw(d001, d002, 450, 300)
    fi001.draw(fv001, 400, 100)
    d001.draw(dummy2, fv001, 50, 100)
    d002.draw(fv001, dummy, 700, 300)
    li002.draw(separator.get('dpp1'), 600, 200)
    lic001.draw(li001, fv001)
    li003.draw(d001, 150, 10)
    # Test of drawing from list
    #draw_sep()
    draw_transmitter()
    draw_sep()

    # FPS and sim-speed info
    font = pygame.font.SysFont('arial', 15, False)
    hz = font.render(str(round(trueFPS, 2)) + 'Hz', 1, (0, 0, 0))
    screen.blit(hz, (300, 5))
    pros = font.render(str(round(simSpeed, 2)) + '%', 1, (0, 0, 0))
    screen.blit(pros, (360, 5))
    # Debug text
    debug = font.render(str(fv001.flowOil * m3h), 1, (0, 0, 0))
    screen.blit(debug, (460, 5))
    debug2 = font.render(str(fv001.flowWater * m3h), 1, (0, 0, 0))
    screen.blit(debug2, (460, 25))
    #sgc.update(clock.tick(userFPS))
    pygame.display.flip()


run = True
while run:

    rW = screen.get_width()        # Gets current width of the screen
    rH = screen.get_height()       # Gets current height of the screen
    clock.tick(userFPS)
    mPos = pygame.mouse.get_pos()
    trueFPS = clock.get_fps()
    simSpeed = trueFPS / userFPS * 100
    if trueFPS < 0.1:
        timeStep = 1 / userFPS
        m3h = 3600 * userFPS
    else:
        m3h = 3600 * trueFPS
        timeStep = 1 / trueFPS

    for event in pygame.event.get():
        #sgc.event(event)
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            clicked = True
            if event.button == 1:
                lClicked = True
                print('left')
            if event.button == 3:
                rClicked = True
                print('right')
            if event.button == 4:
                zoom = zoom + 1
                print('zoom inn')
            if event.button == 5:
                zoom = zoom - 1
                print('zoom out')
        elif event.type == pygame.MOUSEBUTTONUP:
            clicked = False
            lClicked = False
            rClicked = False
            clickCount = 0
        #if event.type == GUI:
            #print(event)

        # Makes the window resizable
        if event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

        if event.type == pygame.KEYUP:
            # Edit mode
            if event.key == pygame.K_e and not edit:
                edit = True
            elif event.key == pygame.K_e and edit:
                edit = False
            # Pause sim
            if event.key == pygame.K_SPACE and not pause:
                pause = True
            elif event.key == pygame.K_SPACE and pause:
                pause = False

    keys = pygame.key.get_pressed()
    for key in keys:
        # Panning keys
        if keys[pygame.K_LCTRL]:
            speed = 3 / (trueFPS + 0.01)
        else:
            speed = 0.3 / (trueFPS + 0.01)
        if keys[pygame.K_LEFT]:
            panX = panX + speed
        if keys[pygame.K_RIGHT]:
            panX = panX - speed
        if keys[pygame.K_UP]:
            panY = panY + speed
        if keys[pygame.K_DOWN]:
            panY = panY - speed
    print(tagInfo)
    redraw()

pygame.quit()
