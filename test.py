# Proof of concept, pressure and level in pygame
# 0 = oil, 1 = gas, 2 = water, 3 = pressure, 4 = temperature

import pygame

# import sgc

pygame.init()

wScreen = 1200
hScreen = 800
rW = wScreen
rH = hScreen
panX = 0
panY = 0
zoom = 1
x = 0
y = 0

ambientTemperature = 20

pause = False
clicked = False
rClicked = False
lClicked = False
edit = False
clickCount = 0
menu = False
menu2 = False
inside = False

adjPosX = 1
adjPosY = 1

tagInfo = 'blank'

screen = pygame.display.set_mode((wScreen, hScreen), pygame.RESIZABLE)
# screen = sgc.surface.Screen((640,480))
pygame.display.set_caption('sim')

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
        global tagInfo, inside
 
        # TODO: fix temp calc
        td = source.temperature / ambientTemperature
        self.temperature = source.temperature - td
        
        pipe(self, out_source, 4)
        self.rect = pygame.draw.rect(screen, (85, 85, 85), (self.x, self.y, self.width, self.height))

        update_sep(self, source, out_source, x, y)
        info_box(self, source, out_source)
        move(self, x, y)

        font = pygame.font.SysFont('arial', 25, True)
        tag = font.render(str(self.tag), 1, (255, 255, 255))
        screen.blit(tag, (self.x + 5, self.y))
    
        if self.rect.collidepoint(mPos):
            tagInfo = self.tag
            
        if not pause:
            if self.levelWater >= 1:
                self.cubesOil = self.cubesOil + source.flowOil + source.flowWater - out_source.flowOil
            else:
                self.cubesOil = self.cubesOil - out_source.flowOil + source.flowOil

            self.cubesWater = self.cubesWater - out_source.flowWater + source.flowWater
            self.volumeLeft = self.volume - self.cubesOil + self.cubesWater
            self.volumeGas = self.volumeGas + source.flowGas - out_source.flowGas

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
        global tagInfo
        self.rect = pygame.draw.rect(screen, (75, 75, 75), (self.x, self.y, self.width, self.height))
        pygame.draw.line(screen, (255, 255, 255), (self.x + self.width / 2, self.y + self.height),
                         (self.x + self.width / 2, measuring_point.y))

        info_box(self, measuring_point)
        move(self, x, y)
        if self.rect.collidepoint(mPos):
            tagInfo = self.tag

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

    def draw(self, source, out_source, x, y):
        self.dP = source.pressure - out_source.pressure

        if self.opening < 0:
            self.opening = 0

        pipe(self, out_source, 4)
        self.rect = pygame.draw.rect(screen, (5, 5, 5), (self.x, self.y, self.width, self.height))

        font = pygame.font.SysFont('arial', 25, True)
        opening = font.render(str(round(self.opening)) + '%', 1, (255, 255, 255))
        screen.blit(opening, (self.x + 5, self.y + 50))

        info_box(self, source, out_source)
        move(self, x, y)
        faceplate(self)

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
    def __init__(self, msg, func):
        self.msg = msg
        self.x = 0
        self.y = 0
        self.width = 100
        self.height = 35
        self.click = False
        self.func = func
        self.color = (80, 124, 196)
       
    def draw(self, x, y, width=100, height=35, fontSz=25, bold=True):
        global clickCount
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        border = pygame.draw.rect(screen, (255, 255, 255), (x - 2, y - 7, self.width + 4, self.height + 4), 0)
        rect = pygame.draw.rect(screen, self.color, (x, y - 5, self.width, self.height), 0)
        font = pygame.font.SysFont('arial', fontSz, bold)
        text = font.render((str(self.msg)), 1, (255, 255, 255))
        screen.blit(text, (rect.center[0] - text.get_rect().width / 2, rect.center[1] - text.get_rect().height / 2))
        self.color = (80, 124, 196)
        
        if rect.collidepoint(mPos):
            self.color = (113, 151, 214)
        if rect.collidepoint(mPos) and lClicked:
            self.color = (30, 191, 86)
        if rect.collidepoint(mPos) and lClicked and clickCount == 0:
            self.click = True
            self.func()
            clickCount += 1
        else:
            self.click = False
    

'''Drawing from dictionaries, default content'''
dummyD = {'dummy0': Dummy('dummy0'), 'dummy50': Dummy('dummy50'), 'dummy500': Dummy('dummy500')}
separator = {'d001': Separator('d001', 8, 4), 'd002': Separator('d002', 80, 4)}
transmitter = {'pi001': Transmitter('pressure', 'pi001'), 'li001': Transmitter('level oil', 'li001'),
               'li003': Transmitter('level water', 'li003'), 'fi001': Transmitter('flow', 'fi001'), 'li002': Transmitter('level oil', 'li002')}
valve = {'fv001': Valve('fv001', 'oil', 1)}
controller = {'lic001': Controller('lic001')}

dummyDraw = {'dummy0': [0, 0, 0], 'dummy50': [50, 500, 30], 'dummy500': [500, 500, 500]}
separatorDraw = {'d001': [dummyD.get('dummy50'), valve.get('fv001'), 50, 100], 'd002': [valve.get('fv001'), dummyD.get('dummy0'), 750, 300]}
transmitterDraw = {'pi001': [separator.get('d001'), 10, 10], 'li001': [separator.get('d001'), 200, 300],
                   'li003': [separator.get('d001'), 150, 10], 'fi001': [valve.get('fv001'), 400, 100], 'li002': [separator.get('d002'), 800, 200]}
valveDraw = {'fv001': [separator.get('d001'), separator.get('d002'), 450, 300]}
controllerDraw = {'lic001': [transmitter.get('li001'), valve.get('fv001'), 100, 100, 5, 10, 5]}

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
    for dum in dummyDraw:
        dummyD.get(dum).draw(dummyDraw.get(dum)[0], dummyDraw.get(dum)[1], dummyDraw.get(dum)[2])
        

def new_sep(tag='ddd', volume=8, volume_water=4, source=dummyD.get('dummy0'), out_source=dummyD.get('dummy0'), x=1000, y=100):
    tag = input('Tag: ')
    x = mPos[0]
    y = mPos[1]
    out = input('Out: ')
    if out in valve:
        out_source = valve.get(out)
    else:
        out_source = dummyD.get('dummy0')
        print(out + 'does not exist')
    separator.setdefault(tag, Separator(tag, volume, volume_water))
    separatorDraw.setdefault(tag, [source, out_source, x, y])


def draw_sep():
    for sep in separatorDraw:
        separator.get(sep).draw(separatorDraw.get(sep)[0], separatorDraw.get(sep)[1],
                                separatorDraw.get(sep)[2], separatorDraw.get(sep)[3])


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
        elif new_source in dummyD:
            source = dummyD.get(new_source)
        elif new_source in separator:
            source = separator.get(new_source)
        elif new_source in valve:
            source = valve.get(new_source)
        else:
            print('Tag does not exist')

        nOut = input()
        out_source = valve.get(nOut)
        
        #separator.update({tag: Separator(tag, volume, volume_water)})
        separatorDraw.update({tag: [source, out_source, x, y]})


def new_transmitter(tag='lll', typ='level oil', x=100, y=100, source=dummyD.get('dummy0')):
    tag = input('Tag: ')
    nSource = input('Source: ')
    source = separator.get(nSource)
    x = mPos[0]
    y = mPos[1]
    transmitter.setdefault(tag, Transmitter(typ, tag))
    transmitterDraw.setdefault(tag, [source, x, y])


def draw_transmitter():
    for trans in transmitterDraw:
        transmitter.get(trans).draw(transmitterDraw.get(trans)[0], transmitterDraw.get(trans)[1],
                                    transmitterDraw.get(trans)[2])


def new_valve(tag='v001', typ='oil', size=1, source=dummyD.get('dummy0'), out_source=dummyD.get('dummy0'), x=1000, y=100):
    tag = input('Tag: ')
    nSource = input('source: ')
    source = separator.get(nSource)
    x = mPos[0]
    y = mPos[1]
    valve.setdefault(tag, Valve(tag, typ, size))
    valveDraw.setdefault(tag, [source, out_source, x, y])


def draw_valve():
    for tag in valveDraw:
        valve.get(tag).draw(valveDraw.get(tag)[0], valveDraw.get(tag)[1],
                            valveDraw.get(tag)[2], valveDraw.get(tag)[3])

def new_controller(tag='c001', source='dummy0', target='dummy0', x=100, y=100, p=5, i=10, d=5):
    tag = input('Tag: ')
    nSource = input('Source: ')
    source = transmitter.get(nSource)
    x = mPos[0]
    y = mPos[1]
    controller.setdefault(tag, Controller(tag))
    controllerDraw.setdefault(tag, [source, target, x, y, p, i, d])
    

def draw_controller():
    for tag in controllerDraw:
        controller.get(tag).draw(controllerDraw.get(tag)[0], controllerDraw.get(tag)[1],
                                 controllerDraw.get(tag)[2], controllerDraw.get(tag)[3],
                                 controllerDraw.get(tag)[4], controllerDraw.get(tag)[5])


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


def info_box(self, source, out_source=dummyD.get('dummy0')):
    global tagInfo
    if self.rect.collidepoint(mPos) and edit and not clicked:
            font = pygame.font.SysFont('arial', 15, False)
            fontB = pygame.font.SysFont('arial', 15, True)
            width = 100
            height = 50
            
            info0 = fontB.render(str(self.tag), 1, (0, 0, 0))
            info1 = font.render('source: ' + str(source.tag), 1, (0, 0, 0))
            info2 = font.render('target: ' + str(out_source.tag), 1, (0, 0, 0))
            width = info1.get_rect().width + 10
            height = info0.get_rect().height + info1.get_rect().height + info2.get_rect().height - 5
            pygame.draw.rect(screen, (255, 205, 186), (mPos[0] + 20, mPos[1], width, height)) # TODO: Make width dependent in longest string
            
            screen.blit(info0, (mPos[0] + 25, mPos[1]))
            screen.blit(info1, (mPos[0] + 25, mPos[1] + 15))
            screen.blit(info2, (mPos[0] + 25, mPos[1] + 30))


def edit_menu():
    global menu, x, y
    if edit and rClicked and tagInfo == '':
        menu = True
        x = mPos[0]
        y = mPos[1]
    if menu:
        nSepBtn.draw(x, y, 100, 25, 15, False)
        nValveBtn.draw(x, y + 25, 100, 25, 15, False)
        nTransmitterBtn.draw(x, y + 50, 100, 25, 15, False)
    if lClicked:
        menu = False


def faceplate(self):
    faceplate = pygame.draw.rect(screen, (255, 205, 186), (0, 0, 0, 0))
    font = pygame.font.SysFont('comicsans', 20, False)
    fontB = pygame.font.SysFont('arial', 20, True)
    
    if not edit and self.rect.collidepoint(mPos) and rClicked:
        self.faceplate = True
        x = mPos[0]
        y = mPos[1]
        
    if self.faceplate:
        faceplate = pygame.draw.rect(screen, (193, 193, 193), (self.x, self.y + self.height + 10, 150, 200))
        tag = fontB.render(str(self.tag), 1, (0, 0, 0))
        opening = font.render('Output: ' + str(round(self.opening, 2)) + ' %', 1, (0, 0, 0))
        screen.blit(tag, (faceplate.x - tag.get_rect().width / 2 + faceplate.width / 2, faceplate.y))
        screen.blit(opening, (faceplate.x, faceplate.y + 50))
        
        bar = pygame.draw.rect(screen, (28, 173, 0), (faceplate.x + 10, faceplate.y + faceplate.height - 10 - 1 * self.opening , 10, 1 * self.opening))
        
    if lClicked and not faceplate.collidepoint(mPos):
        self.faceplate = False
               

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


'''def is_mouse_inside(x, y, width, height):
    m_pos = pygame.mouse.get_pos()
    if x < m_pos[0] < x + width and y < m_pos[1] < y + height:
        return True'''


'''Setting up UI'''
pauseBtn = Button('Pause', pause_sim)
testBtn = Button('Test', new_sep)
editBtn = Button('Edit', edit_mode)
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

    edit_menu()

    #pygame.draw.rect(screen, (255, 205, 186), (0, 0, rW, 30))

    '''Debug text'''
    '''font = pygame.font.SysFont('arial', 15, False)
    debug = font.render(str(fv001.flowOil * m3h), 1, (0, 0, 0))
    screen.blit(debug, (460, 5))
    debug2 = font.render(str(fv001.flowWater * m3h), 1, (0, 0, 0))
    screen.blit(debug2, (460, 25))'''

    if edit:
        fontB = pygame.font.SysFont('arial', 25, True)
        mode = fontB.render('EDIT', 1, (0, 0, 0))
        screen.blit(mode, (600, 5))
        editBtn.color = (30, 191, 86)
        
    pygame.display.set_caption('Pyton Control System --- FPS: ' + str(round(trueFPS, 1))+ ' --- ' + str(round(simSpeed, 1)) + '%' )
    
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
            speed = 0.3 / (trueFPS + 0.01)
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
