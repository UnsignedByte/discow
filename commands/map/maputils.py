# @Author: Edmund Lam <edl>
# @Date:   07:17:41, 20-Apr-2018
# @Filename: utils.py
# @Last modified by:   edl
# @Last modified time: 14:46:53, 21-Apr-2018

import math
import string
import random

def smartmod(a, b):
    if a >= 0:
        return a % b
    else:
        return b-(-1*a % b)

def addblock(a, b):
    return '\n'.join(map(lambda x, y:x+' '+y, a.split('\n'), b.split('\n')))

class PoissonDisc:
    def __init__(self, w, h, r, tries = 30, cSize = math.sqrt(2)):
        if cSize <= 0:
            raise ValueError("cellsize must be positive!")
        self.tries = int(tries)
        self.cSize = cSize
        self.r = r
        self.gw = math.ceil(w/cSize)
        self.gh = math.ceil(h/cSize)
        self.grid = [None]*(self.gw*self.gh)
        self.queue = []
        self.oldQ = 0
        self.initiated = False
        self.w = w
        self.h = h
    def addPoint(self):
        if not self.initiated:
            return self.sample((random.random()/2+1/4) * self.w, (random.random()/2+1/4) * self.h)

        while self.oldQ:
            choiceind = int(random.random()*self.oldQ)
            choice = self.queue[choiceind]

            for j in range(self.tries):
                radians = math.pi*random.random()*2
                dist = math.sqrt(random.random())*self.r*2
                x = choice[0]+dist*math.cos(radians)
                y = choice[1]+dist*math.sin(radians)

                if (0 <= x and x < self.w and 0 <= y and y < self.h and self.inRange(x, y)):
                    return self.sample(x, y)

            self.queue[choiceind] = self.queue[-1]
            del self.queue[-1]
            self.oldQ-=1
        return None
    def inRange(self, x, y):
        xx = int(x / self.cSize)
        yy = int(y / self.cSize)
        rX = (max(0, math.floor((x-self.r)/self.cSize)), min(self.gw, math.ceil((x+self.r)/self.cSize)))
        rY = (max(0, math.floor((y-self.r)/self.cSize)), min(self.gh, math.ceil((y+self.r)/self.cSize)))
        for yy in range(*rY):
            Y = yy*self.gw
            for xx in range(*rX):
                pt = self.grid[Y+xx]
                if (pt and ((pt[0]-x)**2+(pt[1]-y)**2 < self.r**2)):
                    return False
        return True
    def sample(self, x, y):
        p = (x, y)
        self.queue.append(p)
        self.grid[self.gw*int(y/self.cSize)+int(x/self.cSize)] = p
        self.initiated = True
        self.oldQ+=1
        return p
    def get(self, x, y):
        return self.grid[int(y)*self.gw+int(x)]
    def find(self, x, y):
        return (int(x/self.cSize), int(y/self.cSize))
    def getAll(self):
        pts = []
        for a in range(len(self.grid)):
            if self.grid[a]:
                q, r = divmod(a, self.gw)
                pts.append((r, q))
        return pts

class Village:
    def __init__(self, chunksize, houses=random.randint(32, 48), spread=random.randint(2,5), townhalls = random.randint(1, 5)):
        self.homes = PoissonDisc(chunksize, chunksize, spread, cSize=1)
        self.townhall = []
        for i in range(houses):
            if i < townhalls:
                self.townhall.append(self.homes.find(*self.homes.addPoint()))
            else:
                self.homes.addPoint()
        self.homes = self.homes.getAll()

class Chunk:
    def __init__(self, hasvillage=random.randint(0,1), chunksize = 64):
        self.map = list([' ']*chunksize for x in range(chunksize))
        self.weightmap = list([0]*chunksize for x in range(chunksize))
        self.chunksize = chunksize
        self.hasvillage = hasvillage
        self.plain = PoissonDisc(chunksize, chunksize, 0.8, cSize=1)
        self.grass = random.randint(400, 800)
        for i in range(self.grass):
            blade = self.plain.find(*self.plain.addPoint())
            self.map[blade[1]][blade[0]] = "·"

        self.forest = PoissonDisc(chunksize, chunksize, 0.8, cSize=1)
        self.trees = random.randint(400, 800)
        for i in range(self.trees):
            tree = self.forest.find(*self.forest.addPoint())
            self.map[tree[1]][tree[0]] = 'T'
        if self.hasvillage:
            self.village = Village(chunksize)
            for a in self.village.homes:
                self.map[a[1]][a[0]] = "b"
                self.weightmap[a[1]][a[0]] = -1
                self.maximumPathSum(random.choice(self.village.townhall), a)
            for a in self.village.townhall:
                self.map[a[1]][a[0]] = "B"
                self.maximumPathSum(self.village.townhall[0], a)
        else:
            self.swamp = PoissonDisc(chunksize, chunksize, 0.8, cSize=1)
            self.water = random.randint(200, 400)
            for i in range(self.water):
                water = self.swamp.find(*self.swamp.addPoint())
                self.map[water[1]][water[0]] = '≡'
    def __str__(self):
        return '\n'.join(list(' '.join(v) for v in self.map))
    def maximumPathSum(self, p1, p2):
        if p1 == p2:
            return
        rl = int(math.copysign(1, p2[0]-p1[0]))
        ud = int(math.copysign(1, p2[1]-p1[1]))
        xmin, xmax = sorted((p1[0], p2[0]))
        ymin, ymax = sorted((p1[1], p2[1]))
        x, y = p2
        while (x, y) != p1:
            if self.map[y][x].lower() not in ['b']:
                self.weightmap[y][x]+=1
                if self.weightmap[y][x] > 2:
                    self.map[y][x] = '#'
                else:
                    self.map[y][x] = '•'
            if ymin <= y-ud <= ymax:
                b1 = self.weightmap[y-ud][x]
            else:
                b1 = -2
            if xmin <= x-rl <= xmax:
                b2 = self.weightmap[y][x-rl]
            else:
                b2 = -2
            if b1 > b2:
                y-=ud
            elif b2 > b1:
                x-=rl
            elif random.random() < 0.5:
                y-=ud
            else:
                x-=rl
    def getCircle(self, radius, center):
        if radius < 0:raise ValueError("Radius must be positive")
        xmin = max(0, center[0]-radius)
        xmax = min(center[0]+radius, self.chunksize)
        ymin = max(0, center[1]-radius)
        ymax = min(center[1]+radius, self.chunksize)
        outgrid = list([' ']*(xmax-xmin) for a in range(ymax-ymin))
        for y in range(ymin, ymax):
            for x in range(xmin, xmax):
                if (x-center[0])**2 + (y-center[1])**2 <= radius**2:
                    outgrid[y-ymin][x-xmin] = self.map[y][x]
        return '\n'.join(list(' '.join(v) for v in outgrid))

class Player:
    def __init__(self, pos=(0,0), health=25, hunger=1, thirst=1, speed=1):
        self.pos = pos
        self.attribs = {"hunger":hunger, "health":health, "thirst":thirst, "speed":speed}
    def add(self, elem, amount):
        if elem in self.attribs:
            self.attribs[elem]+=amount
        else:
            self.attribs[elem]=amount
    def move(self, dir, dst):
        self.pos = tuple(map(lambda x, y: x + y, self.pos, tuple(dst*x for x in [(0,-1), (1,0), (0,1), (-1,0)][dir])))

class World:
    def __init__(self, size=64):
        self.makeMap(size)
        self.players = {}
    def makeMap(size):
        self.chunksize = 64
        self.chunks = list([Chunk(chunksize=self.chunksize)]*size for x in range(size))
    def addPlayer(self, pos=(96,96), id=None):
        if not id:
            id = len(self.players)
        self.players[id] = Player(pos=pos)
    def reqScope(self, id, radius=10):
        pos = self.players[id].pos
        cx, x = divmod(pos[0], self.chunksize)
        cy, y = divmod(pos[1], self.chunksize)
        def getchunk(cx, cy, x, y):
            return self.chunks[smartmod(cy, len(self.chunks))][smartmod(cx, len(self.chunks))].getCircle(radius, (x, y))
        def blockRow(cx, cy, y):
            return addblock(addblock(getchunk(cx-1, cy, x+self.chunksize, y), getchunk(cx, cy, x, y)), getchunk(cx+1, cy, x-self.chunksize, y))
        return '\n'.join([blockRow(cx, cy-1, y+self.chunksize), blockRow(cx, cy, y), blockRow(cx, cy+1, y-self.chunksize)])
    def move(self, id, dir, dst):
        self.players[id].move(dir, dst)
