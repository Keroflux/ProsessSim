
import pygame

pygame.init()

wScreen = 1000
hScreen = 800
screen = pygame.display.set_mode((wScreen, hScreen), pygame.RESIZABLE)

userFPS = 25
clock = pygame.time.Clock()


def redraw():
    pass


clicked = False
run = True

while run:

    trueFPS = clock.get_fps()
    if trueFPS < 1:
        m3h = 3600 * 30
    else:
        m3h = 3600 * trueFPS
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

