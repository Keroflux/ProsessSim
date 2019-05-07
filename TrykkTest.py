# Testing av beregning av trykk og nivå i

import pygame

pygame.init()

wScreen = 500
hScreen = 500
screen = pygame.display.set_mode((wScreen, hScreen))


class Separator(object):
    def __init__(self, tag, x=100, y=100, volume=8):
        self.width = 100
        self.height = 40
        self.x = x
        self.y = y
        self.volume = volume
        self.tag = tag

    def draw(self):
        pygame.draw.rect(screen, (65, 65, 65), (self.x, self.y, self.width, self.height))


class FlowMeter(object):
    def __init__(self, tag, x=100, y=100):
        self.tag = tag
        self.x = x
        self.y = y
        self.width = 10
        self.height = 5

    def draw(self):
        pygame.draw.rect(screen, (255, 255, 255), (self.x, self.y, self.width, self.height))


font = pygame.font.SysFont('comicsans', 30, True)


def redraw():
    screen.fill((0, 0, 0))
    text = font.render('Bar: ' + str(pressure), 1, (255, 255, 255))
    screen.blit(text, (100, 100))
    pygame.display.update()


flowInn = 50
volume = 8
volumeGas = 0
pressure = 0

clock = pygame.time.Clock()
fps = 30
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

    unit = 3600 * fps
    volumeGas = volumeGas + (flowInn / unit)
    pressure = volume * volumeGas
    redraw()

pygame.quit()
