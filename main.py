import pygame
from time import sleep
from random import randint, choice

pygame.init()
from utils import *
pygame.display.set_caption("codewars")

SIZE = 64
SCALE = 4

w = int(SIZE*SCALE*4)
h = w

screen = pygame.display.set_mode((w,h))

background_color = (0, 0, 0)

from battle import *

RED = (255,0,0)
BLUE = (0,0,255)


shells = []

for p in range(10):
	color = tuple([randint(0,255) for i in range(3)])
	shell = Shell(f"Player{p}", color, [randint(0,NUM_INSTR-1) for i in range(50)])
	shells.append(shell)

battles = []

def init_battles():
	global battles

	battles = []

	for i in range(9):
		v1 = choice(shells)
		v2 = choice([shell for shell in shells if shell!=v1])

		battle = Battle(SCALE, SIZE, [((16,16), v1), ((SIZE-16,SIZE-16), v2)])
		battles.append(battle)

init_battles()
battlew = SIZE*SCALE*3

i = 0
running = True
while running:

	screen.fill(background_color)
	i += 1

	for b, battle in enumerate(battles):
		battle.update()
		surf = pygame.Surface([SIZE*SCALE, (SIZE+3)*SCALE], pygame.SRCALPHA)
		battle.draw(surf)
		bx = (SIZE*SCALE*b)%battlew//(SIZE*SCALE)*(SIZE*SCALE)
		by = ((SIZE+3)*SCALE*b)//battlew*((SIZE+3)*SCALE)
		screen.blit(surf, [bx, by])

	if battles[0].over:
		init_battles()

	for s, shell in enumerate(sorted(shells, key=lambda shell:rating(shell.rating), reverse=True)):
		text(screen, battlew, 12*s, f"{s}. {rating(shell.rating)} {shell.owner}", color=shell.color)

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_r:
				init_battles()

	pygame.display.flip()
	sleep(0.016)
