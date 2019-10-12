# Proof of concept, pressure and level in pygame
# 0 = oil, 1 = gas, 2 = water, 3 = pressure, 4 = temperature

import pygame
import pickle

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
enter = False
edit = False
clickCount = 0
menu = False
menuSep = False
menuCont = False
editMenu = False

newSep = False
updateSep = False
updateCont = False

adjPosX = 1
adjPosY = 1

tagInfo = ''
tagId = ''
currentTag = ''

# Textbox things
COLOR_INACTIVE = pygame.Color('gray39')
COLOR_ACTIVE = pygame.Color('gray10')
FONT = pygame.font.Font(None, 25)


screen = pygame.display.set_mode((wScreen, hScreen), pygame.RESIZABLE)

userFPS = 30
clock = pygame.time.Clock()

#facep = pygame.image.load('fp.png')


class Separator(object):

    def __init__(self):
        self.width = 300
        self.height = 120
        self.x = 0
        self.y = 0

        self.id = 'separator'
        self.tag = 0

        self.volume = 0
        self.volume_water_chamber = 0
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
        self.trendLevelOil = []

    def draw(self, source, out_oil, out_gas, out_water, x=10, y=10, tag='d00x', volume=8, volume_water_chamber=4):
        global tagInfo, tagId

        self.oilOut = out_oil
        self.tag = tag
        self.volume = volume
        self.volume_water_chamber = volume_water_chamber
        # TODO: fix temp calc
        td = source.temperature / ambientTemperature
        self.temperature = source.temperature - td
        
        pipe(self, out_oil, 4)
        pipe(self, out_gas, 4)
        pipe(self, out_water, 4)
        self.rect = pygame.draw.rect(screen, (85, 85, 85), (self.x, self.y, self.width, self.height))
        
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

    def __init__(self):
        self.id = 'transmitter'
        self.width = 100
        self.height = 50
        self.value = 0
        self.x = 0
        self.y = 0
        self.typ = 0
        self.tag = 0

        self.newX = 0
        self.newY = 0
        self.clicked = False
        self.rect = pygame.draw.rect(screen, (75, 75, 75), (self.x, self.y, self.width, self.height))
        self.trendValue = []

    def draw(self, measuring_point, x, y, typ, tag='t00x'):
        global tagInfo, tagId
        
        self.typ = typ
        self.tag = tag
        
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
            self.trendValue.append(self.value)

        elif self.typ == 'level oil':
            content = font.render('Level: ', 1, (255, 255, 255))
            value = font.render(str(round(measuring_point.levelOil, 2)) + '%', 1, (255, 255, 255))
            screen.blit(content, (self.x + 5, self.y))
            screen.blit(value, (self.x + 5, self.y + 20))

            self.value = measuring_point.levelOil
            
            self.trendValue.append(self.value)
            #if len(self.trendValue) > 10:
                #self.trendValue.pop(0)

        elif self.typ == 'level water':
            content = font.render('Level: ', 1, (255, 255, 255))
            value = font.render(str(round(measuring_point.levelWater, 2)) + '%', 1, (255, 255, 255))
            screen.blit(content, (self.x + 5, self.y))
            screen.blit(value, (self.x + 5, self.y + 20))

            self.value = measuring_point.levelWater

        elif self.typ == 'flow':
            content = font.render(str(round(measuring_point.flow * measuring_point.m3h, 2)) + 'm3/h', 1, (255, 255, 255))
            screen.blit(content, (self.x, self.y))

            self.value = measuring_point.flow

        else:
            content = font.render('fault: ' + str(self.typ) + '%', 1, (255, 255, 255))
            screen.blit(content, (self.x, self.y))


class Valve(object):
    def __init__(self):
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

        self.size = 0
        self.typ = 0
        self.x = 0
        self.y = 0
        self.newX = 0
        self.newY = 0

        self.clicked = False
        self.rect = 0
        self.faceplate = False
        self.auto = True
        self.m3h = 0

    def draw(self, source, out_source, x, y, tag, typ, size=2):
        global tagInfo, tagId

        self.tag = tag
        self.typ = typ
        self.size = size
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
                    self.m3h = m3h
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
        self.tag = 0
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

    def draw(self, source, target, p_value=5, i_value=10, d_value=5, tag='c00x'):
        global tagInfo, tagId
        self.x = source.x
        self.y = source.y
        self.height = source.height
        self.width = source.width
        self.rect = source.rect
        self.target = target
        self.source = source
        self.tag = tag

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
            if i_value != 0:
                self.i = p_value / i_value * dof
            else:
                self.i = 0
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
            

class Trend(object):
    def __init__(self):
        self.trend = []
        self.series = []
        self.shift = 0
        
    def draw(self, tag):
        self.trend = []
        self.series = transmitter.get(tag).trendValue
        self.shift += 1
        for i in range(len(self.series)):
            if len(self.trend) > 1:
                self.trend.append(pygame.draw.line(screen, (255, 255, 255), ((500 + i-1) - self.shift, -self.series[i-1]*50 + 500), ((500 + i) - self.shift, -self.series[i]*50 + 500), 2))
            else:
                self.trend.append(pygame.draw.line(screen, (255, 255, 255), ((500 + i) - self.shift, -self.series[i]*50 + 500), ((500 + i) - self.shift, -self.series[i]*50 + 500), 2))


class InputBox:

    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.txt_surface = FONT.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    pass
                    #self.text = ''
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                # Re-render the text.
                self.txt_surface = FONT.render(self.text, True, self.color)

    def update(self):
        # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, screen):
        # Blit the rect.
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 0)
        pygame.draw.rect(screen, self.color, self.rect, 2)
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        
    

# Default settings for the sim
setting = {'dummy0': ['dummy0', 0, 0, 0, 'dummy'],
           'dummy50': ['dummy50', 50, 500, 30, 'dummy'],
           'dummy500': ['dummy500', 500, 500, 500, 'dummy'],

           'd001': ['dummy50', 'fv001', 'fv002', 'fv003', 50, 100, 'd001', 10, 4, 'separator'],
           'd002': ['fv001', 'dummy0', 'dummy0', 'dummy0', 750, 300, 'd002', 20, 4, 'separator'],

           'pi001': ['d001', 10, 10, 'pressure', 'pi001', 'transmitter'],
           'li001': ['d001', 200, 10, 'level oil', 'li001', 'transmitter'],
           'li003': ['d001', 170, 300, 'level water', 'li003', 'transmitter'],
           'fi001': ['fv001', 550, 200, 'flow', 'fi001', 'transmitter'],
           'li002': ['d002', 800, 200, 'level oil', 'li002', 'transmitter'],

           'fv001': ['d001', 'd002', 450, 300,'fv001', 'oil', 1, 'valve'],
           'fv002': ['d001', 'dummy0', 370, 0, 'fv002', 'gas', 3, 'valve'],
           'fv003': ['d001', 'dummy0', 200, 500, 'fv003', 'water', 1, 'valve'],

           'lic001': ['li001', 'fv001', 5, 10, 5, 'lic001', 'controller'],
           'pic001': ['pi001', 'fv002', 5, 10, 5, 'pic001', 'controller'],
           'lic002': ['li003', 'fv003', 5, 10, 5, 'lic002', 'controller']
           }

assets ={}
print('loding assets...')
for tag in setting:
    if setting.get(tag)[-1] == 'separator':
        assets.setdefault(tag, Separator())
    elif setting.get(tag)[-1] == 'dummy':
        assets.setdefault(tag, Dummy(tag))
    elif setting.get(tag)[-1] == 'valve':
        assets.setdefault(tag, Valve())
    elif setting.get(tag)[-1] == 'transmitter':
        assets.setdefault(tag, Transmitter())
    elif setting.get(tag)[-1] == 'controller':
        assets.setdefault(tag, Controller())

assetsDraw ={}
print('drawing assets...')
for tag in setting:
    if setting.get(tag)[-1] == 'separator':
        assetsDraw.setdefault(tag, [assets.get(setting.get(tag)[0]), assets.get(setting.get(tag)[1]),
                                    assets.get(setting.get(tag)[2]), assets.get(setting.get(tag)[3]),
                                    setting.get(tag)[4], setting.get(tag)[5], setting.get(tag)[6],
                                    setting.get(tag)[7], setting.get(tag)[8]])
    elif setting.get(tag)[-1] == 'dummy':
        assetsDraw.setdefault(tag, [setting.get(tag)[1], setting.get(tag)[2], setting.get(tag)[3]])
    elif setting.get(tag)[-1] == 'transmitter':
        assetsDraw.setdefault(tag, [assets.get(setting.get(tag)[0]), setting.get(tag)[1], setting.get(tag)[2],
                                    setting.get(tag)[3], setting.get(tag)[4], setting.get(tag)[5]])
    elif setting.get(tag)[-1] == 'valve':
        assetsDraw.setdefault(tag, [assets.get(setting.get(tag)[0]), assets.get(setting.get(tag)[1]), setting.get(tag)[2],
                                    setting.get(tag)[3], setting.get(tag)[4], setting.get(tag)[5],
                                    setting.get(tag)[6], setting.get(tag)[7]])
    elif setting.get(tag)[-1] == 'controller':
        assetsDraw.setdefault(tag, [assets.get(setting.get(tag)[0]), assets.get(setting.get(tag)[1]), setting.get(tag)[2],
                                    setting.get(tag)[3], setting.get(tag)[4], setting.get(tag)[5],
                                    setting.get(tag)[6]])
    

'''Trends'''
ntrend = Trend()
mtrend = Trend()

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

def draw_assets():
    for tag in setting:
        if setting.get(tag)[-1] == 'dummy':
            assets.get(tag).draw(assetsDraw.get(tag)[0], assetsDraw.get(tag)[1], assetsDraw.get(tag)[2])
        elif setting.get(tag)[-1] == 'separator':
            assets.get(tag).draw(assetsDraw.get(tag)[0], assetsDraw.get(tag)[1],
                                    assetsDraw.get(tag)[2], assetsDraw.get(tag)[3],
                                    assetsDraw.get(tag)[4], assetsDraw.get(tag)[5],
                                    assetsDraw.get(tag)[6], assetsDraw.get(tag)[7],
                                    assetsDraw.get(tag)[8])
        elif setting.get(tag)[-1] == 'transmitter':
            assets.get(tag).draw(assetsDraw.get(tag)[0], assetsDraw.get(tag)[1],
                                        assetsDraw.get(tag)[2], assetsDraw.get(tag)[3],
                                        assetsDraw.get(tag)[4])
        elif setting.get(tag)[-1] == 'valve':
            assets.get(tag).draw(assetsDraw.get(tag)[0], assetsDraw.get(tag)[1],
                                assetsDraw.get(tag)[2], assetsDraw.get(tag)[3],
                                assetsDraw.get(tag)[4], assetsDraw.get(tag)[5],
                                assetsDraw.get(tag)[6])
        elif setting.get(tag)[-1] == 'controller':
            assets.get(tag).draw(assetsDraw.get(tag)[0], assetsDraw.get(tag)[1],
                                     assetsDraw.get(tag)[2], assetsDraw.get(tag)[3],
                                     assetsDraw.get(tag)[4], assetsDraw.get(tag)[5])

def new_sep(): # TODO: Add more options
    global newSep
    tag = 'd00x'
    x = mPos[0]
    y = mPos[1]
    out_oil = 'dummy0'
    out_gas = 'dummy0'
    out_gas = 'dummy0'
    out_water = 'dummy0'
    source = 'dummy0'
    volume = 8
    volume_water = 4
    plate = pygame.draw.rect(screen, (193, 193, 193), (500, 350, 250, 400))
    if not newSep:
        tag_box = InputBox(plate.x + 10, plate.y + 30, 100, 25, tag) 
        source_box = InputBox(plate.x + 10, plate.y + 65, 100, 25, source)
        input_boxes.append(tag_box)
        input_boxes.append(source_box)
        newSep = True
    elif newSep:
        plate
        heading = FONT.render('Add new separator', True, (0, 0, 0))
        screen.blit(heading, (plate.x + 15, plate.y + 5))
        tagTXT = FONT.render('Tag', True, (0, 0, 0))
        screen.blit(tagTXT, (plate.x + 120, plate.y + 30))
        sourceTXT = FONT.render('Source', True, (0, 0, 0))
        screen.blit(sourceTXT, (plate.x + 120, plate.y + 65))

        if enter:
            tag = input_boxes[0].text
            source = input_boxes[1].text
            assets.setdefault(tag, Separator())
            assetsDraw.setdefault(tag, [assets.get(source), assets.get(out_oil),
                                        assets.get(out_gas), assets.get(out_water), x, y, tag, volume, volume_water])
            setting.setdefault(tag, [source, out_oil, out_gas, out_water, x, y, tag, volume, volume_water, 'separator'])
            print(tag + ' created')
            input_boxes.clear()
            newSep = False


def update_sep(): # TODO: Add more options
    global updateSep, enter
    tag = currentTag
    x = mPos[0]
    y = mPos[1]
    out_oil = 'dummy0'
    out_gas = 'dummy0'
    out_gas = 'dummy0'
    out_water = 'dummy0'
    source = 'dummy0'
    volume = 8
    volume_water = 4
    plate = pygame.draw.rect(screen, (193, 193, 193), (500, 350, 250, 400))
    if not updateSep:
        source_box = InputBox(plate.x + 10, plate.y + 30, 100, 25, setting.get(currentTag)[0]) 
        out_oil_box = InputBox(plate.x + 10, plate.y + 65, 100, 25, setting.get(currentTag)[1])
        volume_box = InputBox(plate.x + 10, plate.y + 100, 100, 25, str(setting.get(currentTag)[7]))
        input_boxes.append(source_box)
        input_boxes.append(out_oil_box)
        input_boxes.append(volume_box)
        updateSep = True
    if updateSep:
        plate
        heading = FONT.render('Update ' + currentTag, True, (0, 0, 0))
        screen.blit(heading, (plate.x + 15, plate.y + 5))
        tagTXT = FONT.render('Source', True, (0, 0, 0))
        screen.blit(tagTXT, (plate.x + 120, plate.y + 30))
        sourceTXT = FONT.render('Oil out', True, (0, 0, 0))
        screen.blit(sourceTXT, (plate.x + 120, plate.y + 65))
        sourceTXT = FONT.render('Volume', True, (0, 0, 0))
        screen.blit(sourceTXT, (plate.x + 120, plate.y + 100))
        if enter:
            assetsDraw.get(currentTag)[0] = assets.get(input_boxes[0].text)
            assetsDraw.get(currentTag)[1] = assets.get(input_boxes[1].text)
            assetsDraw.get(currentTag)[7] = float(input_boxes[2].text)
            setting.get(currentTag)[0] = input_boxes[0].text
            setting.get(currentTag)[1] = input_boxes[1].text
            setting.get(currentTag)[7] = float(input_boxes[2].text)
            input_boxes.clear()
            updateSep = False
            enter = False


def new_transmitter(tag='lll', typ='level oil', x=100, y=100, source=assets.get('dummy0')):
    tag = input('Tag: ')
    new_src = input('Source: ')
    source = assets.get(new_src)
    x = mPos[0]
    y = mPos[1]
    transmitter.setdefault(tag, Transmitter())
    transmitterDraw.setdefault(tag, [source, x, y, typ, tag])


def new_valve(tag='v001', typ='oil', size=1, source=assets.get('dummy0'), out_source=assets.get('dummy0'), x=1000, y=100):
    tag = input('Tag: ')
    new_src = input('source: ')
    source = assets.get(new_src)
    x = mPos[0]
    y = mPos[1]
    assets.setdefault(tag, Valve())
    assetsDraw.setdefault(tag, [source, out_source, x, y, tag, typ, size])
    setting.setdefault(tag, [new_src, 'dummy0', x, y, tag, typ, size, 'valve'])


def new_controller(tag='c001', source='dummy0', target='dummy0', p=5, i=10, d=5):
    tag = input('Tag: ')
    new_src = input('Source: ')
    source = assets.get(new_src)
    assets.setdefault(tag, Controller())
    assetsDraw.setdefault(tag, [source, target, p, i, d, tag])
    setting.setdefault(tag, [source, target, p, i, d, tag, 'controller'])

def update_controller(): # TODO: Add more options
    global updateCont, enter
    tag = currentTag
    x = mPos[0]
    y = mPos[1]
    source = 'dummy0'
    target = 'dummy0'
    p = 5
    i = 10
    d = 5
    ex_btn = Button('X')
    plate = pygame.draw.rect(screen, (193, 193, 193), (500, 350, 250, 300))
    if not updateCont:
        source_box = InputBox(plate.x + 10, plate.y + 30, 100, 25, setting.get(currentTag)[0]) 
        target_box = InputBox(plate.x + 10, plate.y + 65, 100, 25, setting.get(currentTag)[1])
        p_box = InputBox(plate.x + 10, plate.y + 100, 100, 25, str(setting.get(currentTag)[2]))
        i_box = InputBox(plate.x + 10, plate.y + 135, 100, 25, str(setting.get(currentTag)[3]))
        d_box = InputBox(plate.x + 10, plate.y + 170, 100, 25, str(setting.get(currentTag)[4]))
        input_boxes.append(source_box)
        input_boxes.append(target_box)
        input_boxes.append(p_box)
        input_boxes.append(i_box)
        input_boxes.append(d_box)
        updateCont = True
    if updateCont:
        plate
        ex_btn.draw(plate.x + 230, plate.y + 10, 15, 15, 12)
        heading = FONT.render('Update ' + tag, True, (0, 0, 0))
        screen.blit(heading, (plate.x + 15, plate.y + 5))
        sourceTXT = FONT.render('Source', True, (0, 0, 0))
        screen.blit(sourceTXT, (plate.x + 120, plate.y + 30))
        targetTXT = FONT.render('Target', True, (0, 0, 0))
        screen.blit(targetTXT, (plate.x + 120, plate.y + 65))
        pTXT = FONT.render('P', True, (0, 0, 0))
        screen.blit(pTXT, (plate.x + 120, plate.y + 100))
        iTXT = FONT.render('I', True, (0, 0, 0))
        screen.blit(iTXT, (plate.x + 120, plate.y + 135))
        dTXT = FONT.render('D', True, (0, 0, 0))
        screen.blit(dTXT, (plate.x + 120, plate.y + 170))
        if enter:
            assetsDraw.get(currentTag)[0] = assets.get(input_boxes[0].text)
            assetsDraw.get(currentTag)[1] = assets.get(input_boxes[1].text)
            assetsDraw.get(currentTag)[2] = float(input_boxes[2].text)
            assetsDraw.get(currentTag)[3] = float(input_boxes[3].text)
            assetsDraw.get(currentTag)[4] = float(input_boxes[4].text)
            setting.get(currentTag)[0] = input_boxes[0].text
            setting.get(currentTag)[1] = input_boxes[1].text
            setting.get(currentTag)[2] = float(input_boxes[2].text)
            setting.get(currentTag)[3] = float(input_boxes[3].text)
            setting.get(currentTag)[4] = float(input_boxes[4].text)
            input_boxes.clear()
            updateCont = False
            enter = False
        if ex_btn.click:
            updateCont = False
            input_boxes.clear()
    

def move(self, x, y):  # Function for moving assets. How the fuck does this work?!
    global adjPosX, adjPosY # TODO: Update X/Y pos in setting for all assets
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
            if self.id == 'separator':
                setting.get(self.tag)[4] = self.newX
                setting.get(self.tag)[5] = self.newY
            elif self.id == 'valve':
                setting.get(self.tag)[2] = self.newX
                setting.get(self.tag)[3] = self.newY


def info_box(self, source):
    global tagInfo, editMenu, currentTag
    if self.rect.collidepoint(mPos) and edit and not clicked:
        font = pygame.font.SysFont('arial', 15, False)
        font_b = pygame.font.SysFont('arial', 15, True)
        color = (255, 255, 255)
        if not updateSep and not updateCont:
            currentTag = self.tag
        if tagId == 'separator' and not updateSep:
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
    global menu, menuSep, menux, menuX, menuY, menuCont
    if edit and rClicked and tagInfo == '':
        menu = True
        menuX = mPos[0]
        menuY = mPos[1]
    elif edit and rClicked and tagId == 'separator':
        menuSep = True
        menuX = mPos[0]
        menuY = mPos[1]
    elif edit and rClicked and tagId == 'controller':
        menuCont = True
        menuX = mPos[0]
        menuY = mPos[1]
    if menu:
        nSepBtn.draw(menuX, menuY, 115, 25, 15, False)
        nValveBtn.draw(menuX, menuY + 25, 115, 25, 15, False)
        nTransmitterBtn.draw(menuX, menuY + 50, 115, 25, 15, False)
    if menuSep:
        udSepBtn.draw(menuX, menuY, 115, 25, 15, False)
        deleteBtn.draw(menuX, menuY + 25, 115, 25, 15, False)
    elif menuCont:
        udContBtn.draw(menuX, menuY, 115, 25, 15, False)
        deleteBtn.draw(menuX, menuY + 25, 115, 25, 15, False)
    if lClicked:
        menu = False
        menuSep = False
        menuCont = False
        

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

def delete():
    setting.pop(currentTag)
    assets.pop(currentTag)
    assetsDraw.pop(currentTag)

def clear():
    setting.clear()
    assets.clear()
    assetsDraw.clear()

def save(): # TODO: Chose save name
    print('Saving...')
    pickle.dump(setting, open('save.p', 'wb'))
    print('Saved')


def load(): # TODO: Chose witch save to load
    global setting
    print('loading...')
    setting.update(pickle.load(open('save.p', 'rb')))
    
    for tag in setting:
        if setting.get(tag)[-1] == 'separator':
            assets.setdefault(tag, Separator())
        elif setting.get(tag)[-1] == 'dummy':
            assets.setdefault(tag, Dummy(tag))
        elif setting.get(tag)[-1] == 'valve':
            assets.setdefault(tag, Valve())
        elif setting.get(tag)[-1] == 'transmitter':
            assets.setdefault(tag, Transmitter())
        elif setting.get(tag)[-1] == 'controller':
            assets.setdefault(tag, Controller())

    for tag in setting:
        if setting.get(tag)[-1] == 'separator':
            assetsDraw.setdefault(tag, [assets.get(setting.get(tag)[0]), assets.get(setting.get(tag)[1]),
                                        assets.get(setting.get(tag)[2]), assets.get(setting.get(tag)[3]),
                                        setting.get(tag)[4], setting.get(tag)[5], setting.get(tag)[6],
                                        setting.get(tag)[7], setting.get(tag)[8]])
        elif setting.get(tag)[-1] == 'dummy':
            assetsDraw.setdefault(tag, [setting.get(tag)[1], setting.get(tag)[2], setting.get(tag)[3]])
        elif setting.get(tag)[-1] == 'transmitter':
            assetsDraw.setdefault(tag, [assets.get(setting.get(tag)[0]), setting.get(tag)[1], setting.get(tag)[2],
                                        setting.get(tag)[3], setting.get(tag)[4], setting.get(tag)[5]])
        elif setting.get(tag)[-1] == 'valve':
            assetsDraw.setdefault(tag, [assets.get(setting.get(tag)[0]), assets.get(setting.get(tag)[1]), setting.get(tag)[2],
                                        setting.get(tag)[3], setting.get(tag)[4], setting.get(tag)[5],
                                        setting.get(tag)[6], setting.get(tag)[7]])
        elif setting.get(tag)[-1] == 'controller':
            assetsDraw.setdefault(tag, [assets.get(setting.get(tag)[0]), assets.get(setting.get(tag)[1]), setting.get(tag)[2],
                                        setting.get(tag)[3], setting.get(tag)[4], setting.get(tag)[5],
                                        setting.get(tag)[6]])
    print('done loading')


def new_trend(tag):
    pass


'''Setting up UI'''
pauseBtn = Button('Pause', pause_sim)
testBtn = Button('Clear', clear)
editBtn = Button('Edit', edit_mode)
saveBtn = Button('Save', save)
loadBtn = Button('Load', load)
'''Left click menu'''
nSepBtn = Button('New Separator', new_sep)
nValveBtn = Button('New Valve', new_valve)
nTransmitterBtn = Button('New Transmitter', new_transmitter)
udSepBtn = Button('Update Separator', update_sep)
udContBtn = Button('Update Controller', update_controller)
deleteBtn = Button('Delete', delete)
'''Input boxes for edit menus'''
input_boxes = []


def redraw():
    screen.fill((128, 128, 128))

    '''Drawing stuff from the dictionaries'''
    draw_assets()
    '''Draw UI'''
    pauseBtn.draw(100, rH - 35)
    testBtn.draw(pauseBtn.x + 110, rH - 35)
    editBtn.draw(testBtn.x + 110, rH - 35)
    saveBtn.draw(editBtn.x + 110, rH - 35)
    loadBtn.draw(saveBtn.x + 110, rH - 35)

    edit_menu()

    #ntrend.draw('li001')
    #mtrend.draw('pi001')

    #pygame.draw.rect(screen, (255, 205, 186), (0, 0, rW, 30))

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
    if newSep:
        new_sep()
    elif updateSep:
        update_sep()
    elif updateCont:
        update_controller()
    for box in input_boxes:
        box.draw(screen)
        
    pygame.display.set_caption('Python Control System --- FPS: ' + str(round(trueFPS, 1)) + ' --- ' + str(round(simSpeed, 1)) + '%')
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
        if event.type == pygame.QUIT:
            run = False
        for box in input_boxes:
                box.handle_event(event)
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

        if event.type == pygame.VIDEORESIZE: # Makes the window resizable
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                enter = True

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_RETURN:
                enter = False
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
            speed = 0.5 / (trueFPS + 0.01)
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
