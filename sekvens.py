
import pygame


pygame.init()

wScreen = 1200
hScreen = 800
rW = wScreen
rH = hScreen

clicked = False
lCLicked = False
RClicked = False

counter = 0

currentStep = 1
timer = 0
stepName = ''
stepAct = ''


screen = pygame.display.set_mode((wScreen, hScreen), pygame.RESIZABLE)

userFPS = 30
clock = pygame.time.Clock()

class Block(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.h = 100
        self.w = 200
        self.step = 0
        self.rect = 0
        self.color = (0, 255, 0)
        self.timer = 0
        self.name = ''
        self.act = 'unset'

    def draw(self):

        pygame.draw.rect(screen, self.color, (self.x, self.y, self.w, self.h))
        pygame.draw.rect(screen, (120, 120, 120), (self.x+2, self.y+2, self.w-4, self.h-4))
        
        self.timer = timer
        self.step = currentStep
        self.name = stepName
        self.act = stepAct

        font = pygame.font.SysFont('Consolas', 20)
        screen.blit(font.render(self.name, True, (0, 0, 0)), (self.x+50, self.y+10))
        screen.blit(font.render('step: ' + str(self.step), True, (0, 0, 0)), (self.x+50, self.y+25))
        screen.blit(font.render('aksjon: ' + self.act, True, (0, 0, 0)), (self.x+50, self.y+45))
        screen.blit(font.render('timer: ' + str(round(self.timer,1)), True, (0, 0, 0)), (self.x+50, self.y+80))


class slaveBlock(object):
    def __init__(self, x, y, step, name, tmax):
        self.x = x
        self.y = y
        self.h = 100
        self.w = 200
        self.step = step
        self.rect = 0
        self.color = (160, 160, 160)
        self.timer = tmax
        self.name = name

    def draw(self):
        global currentStep, timer, stepName
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.w, self.h))
        pygame.draw.rect(screen, (120, 120, 120), (self.x+2, self.y+2, self.w-4, self.h-4))
        if self.step == currentStep:
            self.color = (0, 255, 0)
            if self.timer > 0: 
                self.timer -= dt / 1000
                currentStep = self.step
                timer = self.timer
                stepName = self.name
            else:
                self.color = (160, 160, 160)
                currentStep += 1

        font = pygame.font.SysFont('Consolas', 20)
        screen.blit(font.render(self.name, True, (0, 0, 0)), (self.x+50, self.y+10))
        screen.blit(font.render('step: ' + str(self.step), True, (0, 0, 0)), (self.x+50, self.y+25))
        screen.blit(font.render('timer: ' + str(round(self.timer,1)), True, (0, 0, 0)), (self.x+50, self.y+80))


class subStep(object):
    def __init__(self, x, y, step, name, tmax):
        self.x = x
        self.y = y
        self.h = 50
        self.w = 200
        self.step = step
        self.rect = 0
        self.color = (160, 160, 160)
        self.timer = tmax
        self.name = name

    def draw(self):
        global currentStep, timer, stepName
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.w, self.h))
        pygame.draw.rect(screen, (120, 120, 120), (self.x+2, self.y+2, self.w-4, self.h-4))

        font = pygame.font.SysFont('Consolas', 20)
        screen.blit(font.render(self.name, True, (0, 0, 0)), (self.x+50, self.y+10))
            

master = Block(500, 300)
step1 = slaveBlock(500, 450, 1, 'test', 3)
sub1_1 = subStep(200, 450, 1, '63XV001 åpen', 2)
step2 = slaveBlock(500, 600, 2, 'test2', 3) 


def redraw():
    screen.fill((128, 128, 128))
    font = pygame.font.SysFont('Consolas', 20)
    timer2 = str(round(counter,1))
    screen.blit(font.render(str(timer), True, (0, 0, 0)), (100, 100))
    
    master.draw()
    step1.draw()
    sub1_1.draw()
    step2.draw()
        
    pygame.display.flip()


run = True
while run:
    
    rW = screen.get_width()  # Gets current width of the screen
    rH = screen.get_height()  # Gets current height of the screen
    clock.tick(userFPS)
    dt = clock.get_time()
    counter += dt / 1000
   
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            clicked = True
            if event.button == 1:
                lClicked = True
            if event.button == 3:
                rClicked = True
    
        elif event.type == pygame.MOUSEBUTTONUP:
            clicked = False
            lClicked = False
            rClicked = False
            clickCount = 0
        if event.type == pygame.VIDEORESIZE: # Makes the window resizable
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

    #keys = pygame.key.get_pressed()
    #for key in keys:

    redraw()

pygame.quit()
