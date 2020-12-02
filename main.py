import pygame
from time import sleep
from random import randint

pygame.init()
pygame.display.set_caption("codewars")

w = 800
h = 600

screen = pygame.display.set_mode((w,h))

color = (0, 0, 0)

from battle import *

RED = (255,0,0)
BLUE = (0,0,255)

v1 = Virus(RED, [randint(0,NUM_INSTR-1) for i in range(10)])
v2 = Virus(BLUE, [randint(0,NUM_INSTR-1) for i in range(10)])

SIZE = 128

battle = Battle(2, SIZE, [((16,16), v1), ((SIZE-16,SIZE-16), v2)])

i = 0
running = True
while running:
	battle.update()
	screen.fill(color)
	i += 1

	battle.draw(screen)

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

	pygame.display.flip()
	sleep(0.016)
