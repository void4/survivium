import pygame
import colorsys

TEXTSIZE = 16

font = pygame.font.SysFont('Mono', TEXTSIZE)

def reloadFont(TEXTSIZE):
    global font
    font = pygame.font.SysFont('Mono', TEXTSIZE)


def text(surf, x, y, t, color=(255, 255, 255)):
    textsurface = font.render(t, False, color)
    surf.blit(textsurface, (x, y))
    return textsurface.get_size()[0]

def textcenter(surf, x, y, w, t, color=(255,255,255)):
    textsurface = font.render(t, False, color)
    tw = textsurface.get_size()[0]
    surf.blit(textsurface, (x+(w-tw)//2, y))
    return textsurface.get_size()[0]

def rating(r):
    return int((r.mu-r.sigma*3)*100)

def hsv2rgb(h,s,v):
    return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h,s,v))
