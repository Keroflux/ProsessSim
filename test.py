# Proof of concept, pressure and level in pygame
# 0 = oil, 1 = gas, 2 = water, 3 = pressure, 4 = temperature

import pygame
import pickle

# import sgc

pygame.init()

wScreen = 1200
hScreen = 800
rW = wScreen
rH = hScreen
panX = 50
panY = 100
zoom = 1
menuX = 0
menuY = 0

ambientTemperature = 20

pause = False
clicked = False
rClicked = False
lClicked = False
edit = False
clickCount = 0
menu = False

adjPosX = 1
adjPosY = 1

tagInfo = ''
tagId = ''


screen = pygame.display.set_mode((wScreen, hScreen), pygame.RESIZABLE)
# screen = sgc.surface.Screen((640,480))

userFPS = 30
clock = pygame.time.Clock()

#facep = pygame.image.load('fp.png')


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
        self.oilOut = 0

    def draw(self, source, out_oil, out_gas, out_water, x=10, y=10):
        global tagInfo, tagId

        self.oilOut = out_oil
        # TODO: fix temp calc
        td = source.temperature / ambientTemperature
        self.temperature = source.temperature - td
        
        pipe(self, out_oil, 4)
        pipe(self, out_gas, 4)
        pipe(self, out_water, 4)
        self.rect = pygame.draw.rect(screen, (85, 85, 85), (self.x, self.y, self.width, self.height))

        update_sep(self, source, out_oil, x, y)
        move(self, x, y)
        try:
            info_box(self, source)
        except AttributeError:
            pass

        font = pygame.font.SysFont('arial', 25, True)
        tag = font.render(str(self.tag), 1, (255, 255, 255))
        screen.blit(tag, (self.x + 5, self.y))
    
        if self.rect.collidepoint(mPos):
            tagInfo = self.tag
            tagId = self.id
            
        if not pause:
            if self.levelWater >= 1:
                self.cubesOil = self.cubesOil + source.flowOil + source.flowWater - out_oil.flowOil
            else:
                self.cubesOil = self.cubesOil - out_oil.flowOil + source.flowOil

            self.cubesWater = self.cubesWater - out_oil.flowWater - out_water.flowWater + source.flowWater
            self.volumeLeft = self.volume - self.cubesOil + self.cubesWater
            self.volumeGas = self.volumeGas - out_oil.flowGas - out_gas.flowGas + source.flowGas

            self.pressure = self.volumeGas / self.volumeLeft + 1

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
        global tagInfo, tagId
        self.rect = pygame.draw.rect(screen, (75, 75, 75), (self.x, self.y, self.width, self.height))
        pygame.draw.line(screen, (255, 255, 255), (self.x + self.width / 2, self.y + self.height),
                         (self.x + self.width / 2, measuring_point.y))

        try:
            info_box(self, measuring_point)
        except AttributeError:
            pass

        move(self, x, y)
        
        if self.rect.collidepoint(mPos):
            tagInfo = self.tag
            tagId = self.id

        font = pygame.font.SysFont('arial', 25, True)
        
        if self.typ == 'pressure':
            content = font.render(str(round(measuring_point.pressure - 1, 2)) + 'Bar', 1, (255, 255, 255))
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
    def __init__(self, tag, typ, size=2):
        self.id = 'valve'
        self.tag = tag
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
        self.faceplate = False
        self.auto = True

    def draw(self, source, out_source, x, y):
        global tagInfo, tagId
        self.dP = source.pressure - out_source.pressure

        if self.opening < 0:
            self.opening = 0

        pipe(self, out_source, 4)
        self.rect = pygame.draw.rect(screen, (5, 5, 5), (self.x, self.y, self.width, self.height))

        if self.rect.collidepoint(mPos):
            tagInfo = self.tag
            tagId = self.id

        font = pygame.font.SysFont('arial', 25, True)
        opening = font.render(str(round(self.opening)) + '%', 1, (255, 255, 255))
        screen.blit(opening, (self.x + 5, self.y + 50))

        try:
            info_box(self, source)
        except AttributeError:
            pass

        move(self, x, y)
        faceplate_valve(self)

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
    def __init__(self, tag):
        self.id = 'controller'
        self.tag = tag
        self.p = 0
        self.i = 0
        self.d = 0
        self.pid = 0
        self.offsetTime = 0
        self.offset = 0
        self.output = 0
        self.setPoint = 3
        self.x = 0
        self.y = 0
        self.dProcessValue = [0, 0]  # List that stores the two last values
        self.dOffset = [0, 0]  # List that stores the two last offset values

        self.mode = 'auto'
        self.rect = 0
        self.faceplate = False
        self.height = 0
        self.width = 0
        self.target = 0
        self.source = 0

    def draw(self, source, target, p_value=5, i_value=10, d_value=5):
        global tagInfo, tagId
        self.x = source.x
        self.y = source.y
        self.height = source.height
        self.width = source.width
        self.rect = source.rect
        self.target = target
        self.source = source

        faceplate_controller(self)

        try:
            info_box(self, source)
        except AttributeError:
            pass

        if self.rect.collidepoint(mPos):
            tagInfo = self.tag
            tagId = self.id

        if not pause:
            self.offset = self.setPoint - source.value
            self.dProcessValue.append(source.value)     # Stores the two last values in a list and calculates delta
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
            if target.auto:
                target.opening = target.opening - self.output
            if target.opening < 0:
                target.opening = 0
            elif target.opening > 100:
                target.opening = 100


class Dummy(object):
    def __init__(self, tag):
        self.id = 'dummy'
        self.tag = tag
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
        self.cubesOil = 0
        self.cubesWater = 0

    def draw(self, flow_oil=50, flow_gas=5000, flow_water=0, pressure=0, level=0):
        self.flowOil = flow_oil / m3h
        self.flowGas = flow_gas / m3h
        self.flowWater = flow_water / m3h
        self.flow = 50 / m3h
        self.pressure = pressure
        self.levelOil = level


class Button(object):
    def __init__(self, msg, func=None):
        self.msg = msg
        self.x = 0
        self.y = 0
        self.width = 100
        self.height = 35
        self.click = False
        self.func = func
        self.color = (80, 124, 196)
       
    def draw(self, x, y, width=100, height=35, font_sz=25, bold=True):
        global clickCount
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        pygame.draw.rect(screen, (255, 255, 255), (x - 2, y - 7, self.width + 4, self.height + 4), 0)
        rect = pygame.draw.rect(screen, self.color, (x, y - 5, self.width, self.height), 0)
        font = pygame.font.SysFont('arial', font_sz, bold)
        text = font.render((str(self.msg)), 1, (255, 255, 255))
        screen.blit(text, (rect.center[0] - text.get_rect().width / 2, rect.center[1] - text.get_rect().height / 2))
        self.color = (80, 124, 196)
        
        if rect.collidepoint(mPos):
            self.color = (113, 151, 214)
        if rect.collidepoint(mPos) and lClicked:
            self.color = (30, 191, 86)
        if rect.collidepoint(mPos) and lClicked and clickCount == 0:
            self.click = True
            if self.func is not None:
                self.func()
            clickCount += 1
        else:
            self.click = False
    

'''Drawing from dictionaries, default content'''
dummy = {'dummy0': Dummy('dummy0'),
         'dummy50': Dummy('dummy50'),
         'dummy500': Dummy('dummy500')}

separator = {'d001': Separator('d001', 8, 4),
             'd002': Separator('d002', 80, 4)}

transmitter = {'pi001': Transmitter('pressure', 'pi001'),
               'li001': Transmitter('level oil', 'li001'),
               'li003': Transmitter('level water', 'li003'),
               'fi001': Transmitter('flow', 'fi001'),
               'li002': Transmitter('level oil', 'li002')}

valve = {'fv001': Valve('fv001', 'oil', 1),
         'fv002': Valve('fv002', 'gas', 3),
         'fv003': Valve('fv003', 'water', 1)}
         
controller = {'lic001': Controller('lic001'),
              'pic001': Controller('pic001'),
              'lic002': Controller('lic002')}
         
'''Draw settings'''
dummyDraw = {'dummy0': [0, 0, 0],
             'dummy50': [50, 500, 30],
             'dummy500': [500, 500, 500]}

separatorDraw = {'d001': [dummy.get('dummy50'), valve.get('fv001'), valve.get('fv002'), valve.get('fv003'), 50, 100],
                 'd002': [valve.get('fv001'), dummy.get('dummy0'), dummy.get('dummy0'), dummy.get('dummy0'), 750, 300]}
         
transmitterDraw = {'pi001': [separator.get('d001'), 10, 10],
                   'li001': [separator.get('d001'), 200, 10],
                   'li003': [separator.get('d001'), 170, 300],
                   'fi001': [valve.get('fv001'), 550, 200],
                   'li002': [separator.get('d002'), 800, 200]}
         
valveDraw = {'fv001': [separator.get('d001'), separator.get('d002'), 450, 300],
             'fv002': [separator.get('d001'), dummy.get('dummy0'), 370, 0],
             'fv003': [separator.get('d001'), dummy.get('dummy0'), 200, 500]}
         
controllerDraw = {'lic001': [transmitter.get('li001'), valve.get('fv001'), 5, 10, 5],
                  'pic001': [transmitter.get('pi001'), valve.get('fv002'), 5, 10, 5],
                  'lic002': [transmitter.get('li003'), valve.get('fv003'), 5, 10, 5]}

# btn = sgc.Button(label='click', pos=(1000, 200))
# btn.add(0)


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
        

def draw_dummy():
    for tag in dummyDraw:
        dummy.get(tag).draw(dummyDraw.get(tag)[0], dummyDraw.get(tag)[1], dummyDraw.get(tag)[2])
        

def new_sep(volume=8, volume_water=4, source=dummy.get('dummy0')):
    tag = input('Tag: ')
    x = mPos[0]
    y = mPos[1]
    out = input('Out: ')
    out_gas = dummy.get('dummy0')
    out_water = dummy.get('dummy0')
    if out in valve:
        out_oil = valve.get(out)
    else:
        out_oil = dummy.get('dummy0')
        print(out + 'does not exist')
    separator.setdefault(tag, Separator(tag, volume, volume_water))
    separatorDraw.setdefault(tag, [source, out_oil, out_gas, out_water, x, y])


def draw_sep():
    for sep in separatorDraw:
        separator.get(sep).draw(separatorDraw.get(sep)[0], separatorDraw.get(sep)[1],
                                separatorDraw.get(sep)[2], separatorDraw.get(sep)[3],
                                separatorDraw.get(sep)[4], separatorDraw.get(sep)[5])


def update_sep(self, source, out_source, x, y): # TODO: Make menu pop up width choises on what to update
    if self.rect.collidepoint(mPos) and rClicked and edit:
        tag = self.tag
        source = source
        out_source = out_source
        x = self.x
        y = self.y
        
        new_source = input('Old: ' + source.tag + ' New: ')
        if new_source == '':
            source = source
        elif new_source in dummy:
            source = dummy.get(new_source)
        elif new_source in separator:
            source = separator.get(new_source)
        elif new_source in valve:
            source = valve.get(new_source)
        else:
            print('Tag does not exist')

        new_out = input('New target:')
        out_source = valve.get(new_out)
        
        #separator.update({tag: Separator(tag, volume, volume_water)})
        separatorDraw.update({tag: [source, out_source, x, y]})


def new_transmitter(tag='lll', typ='level oil', x=100, y=100, source=dummy.get('dummy0')):
    tag = input('Tag: ')
    new_src = input('Source: ')
    source = separator.get(new_src)
    x = mPos[0]
    y = mPos[1]
    transmitter.setdefault(tag, Transmitter(typ, tag))
    transmitterDraw.setdefault(tag, [source, x, y])


def draw_transmitter():
    for trans in transmitterDraw:
        transmitter.get(trans).draw(transmitterDraw.get(trans)[0], transmitterDraw.get(trans)[1],
                                    transmitterDraw.get(trans)[2])


def new_valve(tag='v001', typ='oil', size=1, source=dummy.get('dummy0'), out_source=dummy.get('dummy0'), x=1000, y=100):
    tag = input('Tag: ')
    new_src = input('source: ')
    source = separator.get(new_src)
    x = mPos[0]
    y = mPos[1]
    valve.setdefault(tag, Valve(tag, typ, size))
    valveDraw.setdefault(tag, [source, out_source, x, y])


def draw_valve():
    for tag in valveDraw:
        valve.get(tag).draw(valveDraw.get(tag)[0], valveDraw.get(tag)[1],
                            valveDraw.get(tag)[2], valveDraw.get(tag)[3])


def new_controller(tag='c001', source='dummy0', target='dummy0', p=5, i=10, d=5):
    tag = input('Tag: ')
    new_src = input('Source: ')
    source = transmitter.get(new_src)
    controller.setdefault(tag, Controller(tag))
    controllerDraw.setdefault(tag, [source, target, p, i, d])
    

def draw_controller():
    for tag in controllerDraw:
        controller.get(tag).draw(controllerDraw.get(tag)[0], controllerDraw.get(tag)[1],
                                 controllerDraw.get(tag)[2], controllerDraw.get(tag)[3])


def move(self, x, y):  # Function for moving assets
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


def info_box(self, source):
    global tagInfo
    if self.rect.collidepoint(mPos) and edit and not clicked:
        font = pygame.font.SysFont('arial', 15, False)
        font_b = pygame.font.SysFont('arial', 15, True)
        color = (255, 255, 255)
        if tagId == 'separator':
            info0 = font_b.render(str(self.tag), 1, (color))
            info1 = font.render('source: ' + str(source.tag), 1, (color))
            info2 = font.render('oil out: ' + str(self.oilOut.tag), 1, (color))
            info3 = font.render('size: ' + str(self.volume), 1, (color))
            width = info1.get_rect().width + 10
            #height = info0.get_rect().height + info1.get_rect().height + info2.get_rect().height + info3.get_rect().height - 5
            #pygame.draw.rect(screen, (255, 205, 186), (mPos[0] + 20, mPos[1], width, 20))  # TODO: Make width dependent in longest string

            screen.blit(info0, (mPos[0] + 25, mPos[1]))
            screen.blit(info1, (mPos[0] + 25, mPos[1] + 15))
            screen.blit(info2, (mPos[0] + 25, mPos[1] + 30))
            screen.blit(info3, (mPos[0] + 25, mPos[1] + 45))


def faceplate_valve(self):
    global facep
    font = pygame.font.SysFont('consolas', 15, False)
    font_b = pygame.font.SysFont('arial', 20, True)
    ex_btn = Button('X')
    man_btn = Button('manuel')
    aut_btn = Button('auto')

    if not edit and self.rect.collidepoint(mPos) and lClicked:
        self.faceplate = True
    if self.faceplate:
        #plate = screen.blit(facep, (self.x, self.y + self.height + 8))
        plate = pygame.draw.rect(screen, (193, 193, 193), (self.x, self.y + self.height + 10, 150, 200))
        pygame.draw.rect(screen, (0, 0, 0), (self.x, self.y + self.height + 10, 150, 200), 1)
        tag = font_b.render(str(self.tag), 1, (0, 0, 0))
        opening = font.render('Output: ' + str(round(self.opening, 2)) + ' %', 1, (0, 0, 0))
        screen.blit(tag, (plate.x - tag.get_rect().width / 2 + plate.width / 2, plate.y))
        screen.blit(opening, (plate.x + 5, plate.y + 50))

        ex_btn.draw(plate.x + 130, plate.y + 10, 15, 15, 12)
        man_btn.draw(plate.x + 50, plate.y + 140, 80, 25, 20)
        aut_btn.draw(plate.x + 50, plate.y + 170, 80, 25, 20)

        pygame.draw.rect(screen, (28, 173, 0),
                         (plate.x + 10, plate.y + plate.height - 10 - 1 * self.opening, 10, 1 * self.opening))
        pygame.draw.rect(screen, (255, 255, 255),
                         (plate.x + 10, plate.y + plate.height - 110 , 10, 100), 1)

        if ex_btn.click:
            self.faceplate = False
        if man_btn.click:
            self.auto = False
        if aut_btn.click:
            self.auto = True
        

def faceplate_controller(self):
    ex_btn = Button('X')
    setp_btn = Button('+')
    setm_btn = Button('-')
    font = pygame.font.SysFont('consolas', 15, False)
    font_b = pygame.font.SysFont('arial', 20, True)

    if not edit and self.rect.collidepoint(mPos) and lClicked:
        self.faceplate = True
    if self.faceplate:
        plate = pygame.draw.rect(screen, (193, 193, 193), (self.x, self.y + self.height + 10, 150, 200))
        pygame.draw.rect(screen, (0, 0, 0), (self.x, self.y + self.height + 10, 150, 200), 1)
        tag = font_b.render(str(self.tag), 1, (0, 0, 0))
        opening = font.render('Setpoint: ' + str(round(self.setPoint, 2)) + ' %', 1, (0, 0, 0))
        screen.blit(tag, (plate.x - tag.get_rect().width / 2 + plate.width / 2, plate.y))
        screen.blit(opening, (plate.x + 5, plate.y + 50))

        ex_btn.draw(plate.x + 130, plate.y + 10, 15, 15, 12)
        setp_btn.draw(plate.x + 70, plate.y + 100, 20, 20, 20)
        setm_btn.draw(plate.x + 40, plate.y + 100, 20, 20, 20)

        pygame.draw.rect(screen, (28, 173, 0),
                         (plate.x + 10, plate.y + plate.height - 10 - 1 * self.source.value, 10, 1 * self.source.value))
        pygame.draw.rect(screen, (255, 255, 255),
                         (plate.x + 10, plate.y + plate.height - 110 , 10, 100), 1)
        pygame.draw.line(screen, (0, 106, 255), (plate.x + 6, plate.y + plate.height - 10 - self.setPoint), (plate.x + 23, plate.y + plate.height - 10 - self.setPoint), 2)
        
        pygame.draw.rect(screen, (28, 173, 0),
                         (plate.x + 30, plate.y + plate.height - 20, 1 * self.target.opening, 10))
        pygame.draw.rect(screen, (255, 255, 255),
                         (plate.x + 30, plate.y + plate.height - 20, 100, 10), 1)
        
        if setp_btn.click:
            self.setPoint += 1
        if setm_btn.click:
            self.setPoint -= 1
        if ex_btn.click:
            self.faceplate = False
        

def edit_menu():
    global menu, menuX, menuY
    if edit and rClicked and tagInfo == '':
        menu = True
        menuX = mPos[0]
        menuY = mPos[1]
    if menu:
        nSepBtn.draw(menuX, menuY, 115, 25, 15, False)
        nValveBtn.draw(menuX, menuY + 25, 115, 25, 15, False)
        nTransmitterBtn.draw(menuX, menuY + 50, 115, 25, 15, False)
    if lClicked:
        menu = False
               

def pause_sim():
    global pause
    if pause:
        pause = False
    else:
        pause = True


def edit_mode():
    global edit
    if edit:
        edit = False
    else:
        edit = True


def clear():
    separator.clear()
    separatorDraw.clear()
    transmitter.clear()
    transmitterDraw.clear()
    valve.clear()
    valveDraw.clear()
    controller.clear()
    controllerDraw.clear()


def save():
    print('Saving...')
    pickle.dump(separator, open('sepsave.p', 'wb'))
    pickle.dump(separatorDraw, open('sepdsave.p', 'wb'))
    pickle.dump(transmitter, open('transsave.p', 'wb'))
    pickle.dump(transmitterDraw, open('transdsave.p', 'wb'))
    pickle.dump(valve, open('valsave.p', 'wb'))
    pickle.dump(valveDraw, open('valdsave.p', 'wb'))
    pickle.dump(controller, open('contsave.p', 'wb'))
    pickle.dump(controllerDraw, open('contdsave.p', 'wb'))
    print('Saved')


def load():    
    separator = pickle.load(open('sepsave.p', 'rb'))
    separatorDraw = pickle.load(open('sepdsave.p', 'rb'))
    transmitter = pickle.load(open('transsave.p', 'rb'))
    transmitterDraw = pickle.load(open('transdsave.p', 'rb'))
    valve = pickle.load(open('valsave.p', 'rb'))
    valveDraw = pickle.load(open('valdsave.p', 'rb'))
    controller = pickle.load(open('contsave.p', 'rb'))
    controllerDraw = pickle.load(open('contdsave.p', 'rb'))
    print(separator)


time = 0
shift = 0
trendl = []
tlines = []
def trend(tag):  # TODO: Fix first line and how long trend is
    global time, shift
    trendl.append(tag.opening)
    shift += 1
    for i in range(len(trendl)):
        tlines.append(pygame.draw.line(screen, (255, 255, 255), ((500 + i-1) - shift, -trendl[i-1]*5 + 500), ((500 + i) - shift, -trendl[i]*5 + 500), 5))

'''def is_mouse_inside(x, y, width, height):
    m_pos = pygame.mouse.get_pos()
    if x < m_pos[0] < x + width and y < m_pos[1] < y + height:
        return True'''


'''Setting up UI'''
pauseBtn = Button('Pause', pause_sim)
testBtn = Button('Clear', clear)
editBtn = Button('Edit', edit_mode)
saveBtn = Button('Save', save)
'''Left click menu'''
nSepBtn = Button('New Separator', new_sep)
nValveBtn = Button('New Valve', new_valve)
nTransmitterBtn = Button('New Transmitter', new_transmitter)


def redraw():
    screen.fill((128, 128, 128))
    
    '''Drawing stuff in the dictionaries'''
    draw_transmitter()
    draw_sep()
    draw_dummy()
    draw_valve()
    draw_controller()
    '''Draw UI'''
    pauseBtn.draw(100, rH - 35)
    testBtn.draw(pauseBtn.x + 110, rH - 35)
    editBtn.draw(testBtn.x + 110, rH - 35)
    saveBtn.draw(editBtn.x + 110, rH - 35)

    edit_menu()

    #pygame.draw.rect(screen, (255, 205, 186), (0, 0, rW, 30))

    '''Debug text'''
    '''font = pygame.font.SysFont('arial', 15, False)
    debug = font.render(str(fv001.flowOil * m3h), 1, (0, 0, 0))
    screen.blit(debug, (460, 5))
    debug2 = font.render(str(fv001.flowWater * m3h), 1, (0, 0, 0))
    screen.blit(debug2, (460, 25))'''

    if edit:
        font_b = pygame.font.SysFont('arial', 25, True)
        mode = font_b.render('EDIT', 1, (0, 0, 0))
        screen.blit(mode, (550, 5))
        editBtn.color = (30, 191, 86)
    if pause:
        font_b = pygame.font.SysFont('arial', 25, True)
        mode = font_b.render('PAUSE', 1, (0, 0, 0))
        screen.blit(mode, (650, 5))
        pauseBtn.color = (30, 191, 86)
        
    pygame.display.set_caption('Python Control System --- FPS: ' + str(round(trueFPS, 1)) + ' --- ' + str(round(simSpeed, 1)) + '%')
    trend(valve.get('fv001'))
    # sgc.update(clock.tick(userFPS))
    pygame.display.flip()


run = True
while run:
    
    rW = screen.get_width()  # Gets current width of the screen
    rH = screen.get_height()  # Gets current height of the screen
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
        # sgc.event(event)
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            clicked = True
            if event.button == 1:
                lClicked = True
            if event.button == 3:
                rClicked = True
            if event.button == 4:
                zoom = zoom + 1
            if event.button == 5:
                zoom = zoom - 1
        elif event.type == pygame.MOUSEBUTTONUP:
            clicked = False
            lClicked = False
            rClicked = False
            clickCount = 0
        if event.type == pygame.MOUSEMOTION:
            tagInfo = ''
                
        # if event.type == GUI:
        # print(event)

        if event.type == pygame.VIDEORESIZE: # Makes the window resizable
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

        if event.type == pygame.KEYUP:
            '''Edit mode'''
            if event.key == pygame.K_e and not edit:
                edit = True
            elif event.key == pygame.K_e and edit:
                edit = False
            '''Pause'''
            if event.key == pygame.K_SPACE and not pause:
                pause = True
            elif event.key == pygame.K_SPACE and pause:
                pause = False

    keys = pygame.key.get_pressed()
    for key in keys:
        '''Panning'''
        if keys[pygame.K_LCTRL]:
            speed = 3 / (trueFPS + 0.01)
        else:
            speed = 0.05 / (trueFPS + 0.01)
        if keys[pygame.K_LEFT]:
            panX = panX + speed
        if keys[pygame.K_RIGHT]:
            panX = panX - speed
        if keys[pygame.K_UP]:
            panY = panY + speed
        if keys[pygame.K_DOWN]:
            panY = panY - speed

    redraw()

pygame.quit()
