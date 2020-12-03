import pygame
from random import shuffle
from itertools import product
from collections import Counter
from trueskill import Rating, rate_1vs1

from utils import *

def getColor(t):
    if isinstance(t, tuple):
        return t
    return (50,50,50)

directions = [(0,1), (1,0), (0,-1), (-1,0)]

NUM_INSTR = 7

I_STEP, I_WAIT, I_LEFT, I_RIGHT, I_EAT, I_HOP, I_CLONE = range(NUM_INSTR)

class Player:
    def __init__(self, color, shell):
        self.color = color
        self.shell = shell

class Shell:
    def __init__(self, owner, color, code):
        self.owner = owner
        self.color = color
        self.code = code
        self.rating = Rating()

    def instantiate(self):
        return Virus(self.color, self.code)

class Virus:
    def __init__(self, color, code):
        self.color = color
        self.code = code
        self.ip = 0
        self.orientation = 0

class Battle:
    def __init__(self, scale, size, starters):
        self.maxsteps = 256
        self.over = False
        self.ticks = 0
        self.counter = None
        self.scale = scale
        self.w = self.h = size
        self.coords = list(product(range(self.w), range(self.h)))
        self.world = [[None for x in range(self.w)] for y in range(self.h)]
        self.shells = {}
        for starter in starters:
            self.shells[starter[1].color] = starter[1]
            self.world[starter[0][1]][starter[0][0]] = starter[1].instantiate()

    def bound(self, x, y):
        return x%self.w, y%self.h

    def step(self, coord, active, number):
        dr = directions[active.orientation]
        nxy = self.bound(coord[0]+dr[0]*number, coord[1]+dr[1]*number)
        return nxy

    def update(self):
        if self.over:
            return
        # cache active!
        # just pop random every time?
        #for coord in coords:
        #oldactives = self.actives
        #self.actives = []
        #for coord in oldactives:

        shuffle(self.coords)
        for xy in self.coords:
            x,y = xy
            active = self.world[y][x]

            if not isinstance(active, Virus):
                continue

            instr = active.code[active.ip%len(active.code)]

            if instr == I_STEP:
                # One step into the looking direction
                nxy = self.step(xy, active, 1)
                nx, ny = nxy
                self.world[ny][nx] = active
                self.world[y][x] = active.color

            elif instr == I_WAIT:
                # Does nothing
                pass

            elif instr == I_LEFT:
                # Turns left
                active.orientation = (active.orientation - 1) % 4

            elif instr == I_RIGHT:
                # Turns right
                active.orientation = (active.orientation + 1) % 4

            elif instr == I_EAT:
                # Removes all cells one step into the looking direction
                nx, ny = self.step(xy, active, 1)
                self.world[ny][nx] = None

            elif instr == I_HOP:
                # Jumps two cells, but doesn't color the old one
                nxy = self.step(xy, active, 2)
                nx, ny = nxy
                self.world[ny][nx] = active
                self.world[y][x] = None

            elif instr == I_CLONE:
                #self.actives.append((x, y))
                nx, ny = self.step(xy, active, 1)
                new = Virus(active.color, active.code)
                self.world[ny][nx] = new

            active.ip += 1

        self.ticks += 1

        if self.ticks >= self.maxsteps and self.counter is not None:
            fields = sorted([item for item in self.counter.items() if item[0] is not None], key=lambda kv:kv[1], reverse=True)
            if len(fields) > 0:
                winner = self.shells[fields[0][0]]
                loser = self.shells[fields[1][0]]
                winner.rating, loser.rating = rate_1vs1(winner.rating, loser.rating)
                self.over = True


    def draw(self, surf):
        self.counter = Counter({shellcolor: 0 for shellcolor in self.shells.keys()})
        for x,y in self.coords:
            tile = self.world[y][x]
            if tile is None:
                self.counter[None] += 1
                continue
            elif isinstance(tile, Virus):
                color = tile.color
            else:
                color = tile
            pygame.draw.rect(surf, color, pygame.Rect(x*self.scale, y*self.scale, self.scale, self.scale))
            self.counter[color] += 1

        #text(surf, 0, 0, str(self.counter))

        pygame.draw.rect(surf, (200,200,200), pygame.Rect(0, (self.h+1)*self.scale, self.w*self.scale*self.ticks/self.maxsteps, self.scale))

        area = self.w*self.h

        # Assume two players for now
        colors = sorted(list(self.counter.keys()), key=lambda k:hash(k))
        if None in colors:
            colors.remove(None)
        colors.insert(1, None)

        offset = 0
        for color in colors:
            perc = self.counter.get(color, 0)/area
            width = perc*self.w*self.scale
            pygame.draw.rect(surf, getColor(color), pygame.Rect(offset, (self.h+2)*self.scale, width, self.scale))
            offset += width
