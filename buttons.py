import pygame
import sgc
from sgc.locals import *

pygame.init()
wScreen = 1200
hScreen = 800

#screen = pygame.display.set_mode((wScreen, hScreen), pygame.RESIZABLE)
screen = sgc.surface.Screen((640,480))

userFPS = 30
clock = pygame.time.Clock()
pause = False
clicked = False
rClicked = False
lClicked = False
edit = False
clickCount = 0

btn = sgc.Button(label='click', pos=(100, 200))
btn.add(0)


class InBox(sgc.InputBox):
    def on_enter(self):
        print('no')



def test():
    print('test')


tBox = InBox()
tBox.add(0)

testt = 'test'
fontB = pygame.font.SysFont('arial', 25, True)
hz = fontB.render(testt, 1, (0, 0, 0))




def redraw():
    screen.fill((128, 128, 128))
    sgc.update(clock.tick(userFPS))
    fontB = pygame.font.SysFont('arial', 25, True)
    testt = tBox.text
    hz = fontB.render(testt, 1, (0, 0, 0))
    screen.blit(hz, (300, 5))
    pygame.display.flip()


run = True
while run:
    clock.tick(userFPS)
    mPos = pygame.mouse.get_pos()
    trueFPS = clock.get_fps()

    for event in pygame.event.get():
        sgc.event(event)
        if event.type == GUI:
            if event.widget_type == InBox:
                print(event)
                testt = event.text
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            clicked = True
        elif event.type == pygame.MOUSEBUTTONUP:
            clicked = False
            lClicked = False
            rClicked = False
            clickCount = 0


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

    redraw()

pygame.quit()


