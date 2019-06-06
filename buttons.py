import pygame


pygame.init()


def is_mouse_inside(x, y, width, height):
    m_pos = pygame.mouse.get_pos()
    if x < m_pos[0] < x + width and y < m_pos[1] < y + height:
        return True


def button(x, y, width, height, screen, msg='BUTTON', func=None):

    pygame.draw.rect(screen, (0, 100, 0), (x, y, width, height))
    font = pygame.font.SysFont('arial', 25, True)
    opening = font.render((str(msg)), 1, (255, 255, 255))
    screen.blit(opening, (x + 5, y))

