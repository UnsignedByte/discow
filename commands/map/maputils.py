# @Author: Edmund Lam <edl>
# @Date:   06:50:24, 02-May-2018
# @Filename: maputils.py
# @Last modified by:   edl
# @Last modified time: 15:56:41, 12-Aug-2018


import math
import string
import random

iteminfo = {"food":{"🍖":(6, 2), "🍗":(3, 2), "🍞":(2, 0), "🍌":(4, 3), "🌽":(1, 1), "🥔":(3, 4), "🥛":(0, 6), "🥃":(0, 3), "🍹":(0, 4)}}

def smartmod(a, b):
    if a >= 0:
        return a % b
    else:
        return b-(-1*a % b)

def closest_factors(a):
    n = int(math.sqrt(a))
    while a % n != 0:
        n-=1
    return n

def addblock(a, b):
    return '\n'.join(map(lambda x, y:x+' '+y, a.split('\n'), b.split('\n')))
def getbar(v, l):
    full_block = '\u2588'
    bars = ['', '\u258F', '\u258E', '\u258D', '\u258C', '\u258B', '\u258A', '\u2589']
    d, i = math.modf(v*l)
    return (int(i)*'\u2588'+bars[int(d*8)]).ljust(l, ' ')

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
        return [tuple(reversed(divmod(a, self.gw))) for a in range(len(self.grid)) if self.grid[a]]

class Village:
    def __init__(self, chunksize, houses=random.randint(32, 48), spread=random.randint(2,5), townhalls = random.randint(1, 5)):
        self.homepoisson = PoissonDisc(chunksize, chunksize, spread, cSize=1)
        self.townhall = []
        for i in range(houses):
            if i < townhalls:
                self.townhall.append(self.homepoisson.find(*self.homepoisson.addPoint()))
            else:
                self.homepoisson.addPoint()
        self.homes = self.homepoisson.getAll()

class Chunk:
    def __init__(self, hasvillage=None, chunksize = 64):
        self.map = list([' ']*chunksize for x in range(chunksize))
        self.weightmap = list([0]*chunksize for x in range(chunksize))
        self.chunksize = chunksize
        if not hasvillage:
            hasvillage = random.randint(0,1)
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
                self.map[water[1]][water[0]] = '≈'
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
                if x == center[0] and y == center[1]:
                    outgrid[y-ymin][x-xmin] = "X"
                elif (x-center[0])**2 + (y-center[1])**2 <= radius**2:
                    outgrid[y-ymin][x-xmin] = self.map[y][x]
        return '\n'.join(list(' '.join(v) for v in outgrid))

class Player:
    def __init__(self, id, pos=(0,0), health=1, hunger=1, thirst=1, speed=1, maxhealth=25, maxthirst=15, maxhunger=20):
        self.pos = pos
        self.save = pos
        self.id = id
        self.attribs = {"hunger":hunger, "health":health, "thirst":thirst, "speed":speed, "maxhealth":maxhealth, "maxthirst":maxthirst, "maxhunger":maxhunger}
        self.inventory = {"🍖":0, "🍗":0, "🍞":0, "🍌":0, "🌽":0, "🥔":0, "🥛":0, "🥃":0, "🍹":0}
    def __str__(self):
        return "health:  ["+getbar(self.attribs["health"], 30)+"]\nhunger:  ["+getbar(self.attribs["hunger"], 30)+"]\nthirst:  ["+getbar(self.attribs["thirst"], 30)+']\nPosition:'+str(self.pos)
    def add(self, elem, amount):
        if elem in self.attribs:
            self.attribs[elem]+=amount
        else:
            self.attribs[elem]=amount
    def move(self, dir, dst):
        self.pos = tuple(map(lambda x, y: x + y, self.pos, tuple(dst*x for x in [(0,-1), (1,0), (0,1), (-1,0)][dir])))
        if self.attribs["health"] == 0:
            self.__init__(self.id, pos=self.save)
            return
        if self.attribs["thirst"] == 0:
            self.attribs["health"]=max(0, self.attribs["health"]-0.5/self.attribs["maxhealth"])
        if self.attribs["hunger"] == 0:
            self.attribs["health"]=max(0, self.attribs["health"]-0.5/self.attribs["maxhealth"])
        self.attribs["health"]=min(1, self.attribs["health"]+1/self.attribs["maxhealth"])
        self.attribs["hunger"]=max(0, self.attribs["hunger"]-1/self.attribs["maxhunger"])
        self.attribs["thirst"]=max(0, self.attribs["thirst"]-1/self.attribs["maxthirst"])
    def useItem(self, item):
        if item in self.inventory and self.inventory[item] >= 1:
            self.inventory[item]-=1
            if item in iteminfo["food"]:
                itemINFO = iteminfo["food"][item]
                self.attribs["hunger"]+=itemINFO[0]/self.attribs["maxhunger"]
                self.attribs["thirst"]+=itemINFO[1]/self.attribs["maxthirst"]

class World:
    def __init__(self, size=64):
        self.makeMap(size)
        self.players = {}
    def makeMap(self, size):
        self.chunksize = 64
        self.chunks = list([Chunk(chunksize=self.chunksize)]*size for x in range(size))
    def getPlayerAttr(self, id, name):
        try:
            return self.players[id].attribs[name]
        except KeyError:
            return None
    def setPlayerAttr(self, id, name):
        self.players[id].attribs[name]=val
    def addPlayer(self, pos=None, id=None):
        if not pos:
            chunkid = random.randint(0, len(self.chunks)-1)
            initchunkid = chunkid
            for i in range(0, len(self.chunks)*len(self.chunks[0])):
                x, y = divmod(chunkid, len(self.chunks))
                if self.chunks[x][y].hasvillage:
                    while True:
                        rhouse = random.choice(self.chunks[x][y].village.homes)
                        if rhouse not in self.chunks[x][y].village.townhall:
                            break
                    pos = (x*len(self.chunks)+rhouse[0], y*len(self.chunks[0])+rhouse[1])
                    break
                chunkid+=1
                chunkid%=len(self.chunks)*len(self.chunks[0])
        if not id:
            id = len(self.players)
        if not pos:
            pos = (random.randint(0, len(self.chunks)*self.chunksize-1),random.randint(0, len(self.chunks[0])*self.chunksize-1))
        self.players[id] = Player(id, pos=pos)
    def reqPlayerInv(self, id):
        l = ['%s: %s' % (k, v) for (k, v) in sorted(self.players[id].inventory.items(), key=lambda x:x[1], reverse=True)]
        n = closest_factors(len(l))
        return '\n\n'.join(['\t\t\t'.join(l[i:i+n]) for i in range(0, len(l), n)])
    def reqPlayer(self, id, radius=10):
        pos = self.players[id].pos
        cx, x = divmod(pos[0], self.chunksize)
        cy, y = divmod(pos[1], self.chunksize)
        def getchunk(cx, cy, x, y):
            return self.chunks[smartmod(cx, len(self.chunks[0]))][smartmod(cy, len(self.chunks[1]))].getCircle(radius, (x, y))
        def blockRow(cx, cy, y):
            return addblock(addblock(getchunk(cx-1, cy, x+self.chunksize, y), getchunk(cx, cy, x, y)), getchunk(cx+1, cy, x-self.chunksize, y))
        return str(self.players[id])+'\n'+'\n'.join([blockRow(cx, cy-1, y+self.chunksize), blockRow(cx, cy, y), blockRow(cx, cy+1, y-self.chunksize)])
    def move(self, id, dir, dst):
        self.players[id].move(dir, dst)
