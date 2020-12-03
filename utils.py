import pygame
import colorsys

font = pygame.font.SysFont('Mono', 12)

def text(surf, x, y, t, color=(255, 255, 255)):
    textsurface = font.render(t, False, color)
    surf.blit(textsurface, (x, y))

def rating(r):
    return int((r.mu-r.sigma*3)*100)

def hsv2rgb(h,s,v):
    return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h,s,v))
