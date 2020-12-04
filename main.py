import pygame
from time import sleep, time
from random import randint, choice, random
from copy import deepcopy

from chat import messages

pygame.init()
from utils import *
pygame.display.set_caption("codewars")

SIZE = 90
SCALE = 10

w = 1920#int(SIZE*SCALE*5)
h = 1080#int((SIZE+3)*SCALE*4)

GW = 1
BATTLES = 1

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
	global battles, GW, SIZE, SCALE, BATTLES, battlew

	battles = []

	if len(shells) < 2:
		return

	if len(shells) < 5:
		GW = 1
		SIZE = 45
		SCALE = 20
		BATTLES = 1
	elif len(shells) < 10:
		GW = 1
		SIZE = 45
		SCALE = 10
		BATTLES = 2
	elif len(shells) < 20:
		GW = 2
		SIZE = 45
		SCALE = 10
		BATTLES = 4
	else:
		GW = 3
		SIZE = 40
		SCALE = 8
		BATTLES = 9

	battlew = SIZE*SCALE*GW

	for i in range(BATTLES):#GW**2
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
	for i in range(max(len(a.code), len(b.code))):
		if c == 0 and i < len(a.code) or i >= len(b.code):
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

def createOrChange(owner, code):
	pshells = [shell for shell in shells if shell.owner==owner]
	if len(pshells) > 0:
		pshells[0].code = code
		print("Changed code", owner, code)
	else:
		print("New player", owner, code)
		shells.append(new_shell(owner=owner, code=code))

def reload_custom():
	createOrChange("random", [randint(0,NUM_INSTR-1) for i in range(1,50)])
	if len(shells) > 0:
		createOrChange("mutant", mutate(splice(mutate(choice(shells)), mutate(choice(shells)))).code)

#shells.append(new_shell("H", (100, 150, 190), codify("lsclsrcselhc")))
shells.append(new_shell("playsdwarffortress", (200, 150, 30), codify("srchrehhhrchhh")))
shells.append(new_shell("str0hhalm", (255, 255, 0), codify("crschc")))
#shells.append(new_shell("Simple", (255,255,255), codify("r")))

running = True
battlerounds = 0
while running:

	if len(battles) == 0:
		init_battles()

	while messages:
		message = messages.pop(0)
		## XXX:
		#continue
		#print(message.channel, message.sender, message.text)
		#print(dir(message))
		# TODO use user-set color
		#if "!" not in message.text:
		#	continue
		msg = message.text

		#if True:
			#code = codify(msg)
		if msg.startswith("!code "):
			code = codify(msg.split(" ", 1)[1])
			if len(code) == 0:
				continue

			createOrChange(message.sender, code)

	screen.fill(background_color)

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
		pygame.draw.line(linesurf, battleshells[0].color+(100,), [bx+SIZE*SCALE//2, by+SIZE*SCALE//2], [battlew, TEXTSIZE*s1score+TEXTSIZE//2])
		pygame.draw.line(linesurf, battleshells[1].color+(100,), [bx+SIZE*SCALE//2, by+SIZE*SCALE//2], [battlew, TEXTSIZE*s2score+TEXTSIZE//2])

	screen.blit(linesurf, (0,0))

	for b, battle in enumerate(battles):
		battle.update()
		surf = pygame.Surface([SIZE*SCALE, (SIZE+3)*SCALE], pygame.SRCALPHA)
		battle.draw(surf)
		bx = (SIZE*SCALE*b)%battlew//(SIZE*SCALE)*(SIZE*SCALE+10)
		by = ((SIZE)*SCALE*b)//battlew*((SIZE+3)*SCALE)
		screen.blit(surf, [bx, by])
		battleshells = list(battle.shells.values())

		dx = 2
		dx += text(screen, bx+dx, by, f"{battleshells[0].owner}", battleshells[0].color)
		dx += text(screen, bx+dx, by, " vs ")
		text(screen, bx+dx, by, f"{battleshells[1].owner}", battleshells[1].color)



	if battles and battles[0].over and battles[0].ticks > BATTLESCREENTICKS:
		#XXX
		#if battlerounds % 1 == 0:
		#	cull_and_mutate()
		reload_custom()
		init_battles()
		battlerounds += 1
		# TODO mutate them over time so they begin to lose?

	for s, shell in enumerate(sortedshells):
		text(screen, (SIZE*SCALE+10)*GW, TEXTSIZE*s, f"{s+1}. {rating(shell.rating)} {shell.owner} {shell.codestr()}", color=shell.color)

	screen.blit(explanation, [w-explanation.get_size()[0], 0])#[battlew+SIZE*SCALE, 0])

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_r:
				init_battles()

	pygame.display.flip()
	#sleep(0.016)
