import pygame
from time import sleep, time
from random import randint, choice, random
from copy import deepcopy

from chat import messages

pygame.init()
from utils import *
pygame.display.set_caption("codewars")

SIZE = 52
SCALE = 5

w = 1920#int(SIZE*SCALE*5)
h = 1080#int((SIZE+3)*SCALE*4)

GW = 3

screen = pygame.display.set_mode((w,h))

background_color = (0, 0, 0)

from battle import *

RED = (255,0,0)
BLUE = (0,0,255)

explanation = pygame.image.load("explanation.png")

shells = []

PLAYER_ID = 0

def new_shell(owner=None, color=None, code=None):
	global PLAYER_ID
	if owner is None:
		PLAYER_ID += 1
		owner = f"Player{PLAYER_ID}"

	#if color is None:
	# Have to avoid same colors
	color = hsv2rgb(random(), 0.5+random()/2, 0.5+random()/2)


	if code is None:
		code = [randint(0,NUM_INSTR-1) for i in range(50)]
	shell = Shell(owner, color, code)
	return shell

#for p in range(64):
#	shells.append(new_shell())

battles = []

def init_battles():
	global battles

	battles = []

	if len(shells) < 2:
		return

	for i in range(9):
		v1 = choice(shells)
		v2 = choice([shell for shell in shells if shell!=v1])

		battle = Battle(SCALE, SIZE, [((16,16), v1), ((SIZE-16,SIZE-16), v2)])
		battles.append(battle)

def mutate(shell):
	shell = deepcopy(shell)
	p = random()
	for i,c in enumerate(shell.code):
		if random() < p:
			shell.code[i] = randint(0, NUM_INSTR-1)
	return shell

def splice(a,b):
	code = []
	p = random()
	c = 0
	for i in range(len(a.code)):
		if c == 0:
			code.append(a.code[i])
		else:
			code.append(b.code[i])
		if random() < p:
			c = 1-c

	return new_shell(a.owner, a.color, code)

def cull_and_mutate():
	global shells
	shells = sorted(shells, key=lambda shell:rating(shell.rating), reverse=True)
	for i in range(5):
		shells[-1-i] = new_shell()

	for i in range(5):
		shells[-5-i] = mutate(splice(mutate(shells[i]), mutate(choice(shells))))

init_battles()
battlew = SIZE*SCALE*GW

def codify(text):
	code = []
	for c in text.lower():
		if c in INAMES:
			code.append(INAMES.index(c))
	return code

i = 0
running = True
battlerounds = 0
while running:

	if len(battles) == 0:
		init_battles()

	while messages:
		message = messages.pop(0)
		#print(message.channel, message.sender, message.text)
		#print(dir(message))
		# TODO use user-set color
		#if "!" not in message.text:
		#	continue

		code = codify(message.text)
		if len(code) == 0:
			continue

		pshells = [shell for shell in shells if shell.owner==message.sender]
		if len(pshells) > 0:
			pshells[0].code = code
			print("Changed code", message.sender, code)
		else:
			print("New player", message.sender, code)
			shells.append(new_shell(owner=message.sender, code=code))

	screen.fill(background_color)
	i += 1

	if time() % 20 < 10:
		sortedshells = sorted(shells, key=lambda shell:rating(shell.rating), reverse=True)
	else:
		sortedshells = sorted(shells, key=lambda shell:shell.owner)


	linesurf = pygame.Surface([w,h], pygame.SRCALPHA)
	# reuse, clear?

	for b, battle in enumerate(battles):
		battleshells = list(battle.shells.values())

		s1score = [i for i,s in enumerate(sortedshells) if s.owner==battleshells[0].owner][0]
		s2score = [i for i,s in enumerate(sortedshells) if s.owner==battleshells[1].owner][0]

		bx = (SIZE*SCALE*b)%battlew//(SIZE*SCALE)*(SIZE*SCALE)
		by = ((SIZE)*SCALE*b)//battlew*((SIZE+3)*SCALE)
		# only draw in the first few battle iterations?
		pygame.draw.line(linesurf, battleshells[0].color+(100,), [bx+SIZE*SCALE/2, by+SIZE*SCALE/2], [battlew, 12*s1score+6])
		pygame.draw.line(linesurf, battleshells[1].color+(100,), [bx+SIZE*SCALE/2, by+SIZE*SCALE/2], [battlew, 12*s2score+6])

	screen.blit(linesurf, (0,0))

	for b, battle in enumerate(battles):
		battle.update()
		surf = pygame.Surface([SIZE*SCALE, (SIZE+3)*SCALE], pygame.SRCALPHA)
		battle.draw(surf)
		bx = (SIZE*SCALE*b)%battlew//(SIZE*SCALE)*(SIZE*SCALE)
		by = ((SIZE)*SCALE*b)//battlew*((SIZE+3)*SCALE)
		screen.blit(surf, [bx, by])
		battleshells = list(battle.shells.values())

		dx = text(screen, bx, by, f"{battleshells[0].owner}", battleshells[0].color)
		dx += text(screen, bx+dx, by, " vs ")
		text(screen, bx+dx, by, f"{battleshells[1].owner}", battleshells[1].color)



	if battles and battles[0].over:
		#XXX
		#if battlerounds % 1 == 0:
		#	cull_and_mutate()
		init_battles()
		battlerounds += 1
		# TODO mutate them over time so they begin to lose?

	for s, shell in enumerate(sortedshells):
		text(screen, battlew, 12*s, f"{s+1}. {rating(shell.rating)} {shell.owner} {shell.codestr()}", color=shell.color)

	screen.blit(explanation, [battlew+SIZE*SCALE, 0])

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_r:
				init_battles()

	pygame.display.flip()
	#sleep(0.016)
