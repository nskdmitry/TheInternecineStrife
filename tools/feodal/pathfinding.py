# import generators
import random
import numpy
import time
import os
import math
from collections import OrderedDict

import sys
if sys.hexversion < 0x030100F0:
    import lands
    from constants import Environments
else:
    from feodal import lands
    from feodal.constants import Environments

"""
Map (a.k.a. Terain) is Cell[]
Cell is {id, id_landscape, height, id_domain, army}
Landscape is {id, civ, env}
Domain is {id, id_owner}

Path is idCell[]
"""

class PathNode:
    def __init__(self, id, prev=None, cost=1, x=None, y=None):
        self.id = id
        self.prev = prev
        self.cost = cost
        self.x = x
        self.y = y

VECTORS = ((0, 0), (-1, 0), (0, -1), (1, 0), (0, 1))

def v(a, b, face):
    a = a - 1
    b = b - 1
    aX = a % face
    aY = a // face
    bX = b % face
    bY = b // face
    return (bX - aX, bY - aY)

class PathTools:
    def __init__(self, face, terrain):
        self.face = face
        self.size = face*face
        self.terrain = terrain

        self.vecines = [[0]]
        self.vecines.append([[-self.face, -1, self.face, 1], [-2*self.face, -self.face-1, -2, self.face-1, 2*self.face, self.face+1, 2, -self.face+1]])
        for r in range(3,4):
            vecine = [dx+dy*self.face for dx in range(-r, r) for dy in range(-r, r) if abs(dx) + abs(dy) == r]
            self.vecines.append(vecine)

    def trace(self, a, b):
        curr = a
        path = [a]
        while curr != b:
            step = self.dv( v(curr, b, self.face) )
            curr = curr + step[0] + step[1]*self.face
            path.append(curr)
        return path

    def linear(self, a, b):
        def around(val):
            return int(math.floor(val))

        (w, h) = v(a, b, self.face)
        wayLong = math.sqrt(w*w + h*h)
        (dx, dy) = (w/wayLong, h/wayLong)
        eps = 0.5
        if dx - math.floor(dx) < eps and dy - math.floor(dy) < eps:
            return self.trace(a, b)
        dx = dx / 2
        dy = dy / 2

        path = [a]
        curr = a
        (x,y) = (float(self.x(a)), float(self.y(a)))
        limit = (abs(dx) + abs(dy))*2
        while curr != b:
            (x, y) = (x + dx, y + dy)
            (posX, posY) = (around(x), around(y))
            curr = self.getId(posX, posY)
            if (x - posX < eps) and (y - posY < eps):
                new = curr - self.face if dx - dy > eps else curr - 1
                path.append(new)
                print("Moved to ({:d}, {:d})".format(self.x(new), self.y(new)))
            path.append(curr)
            print("Moved to ({:d}, {:d})".format(posX, posY))
            limit = limit - 1
            if limit == 0:
                print("Stop! Stop it!")
                break
        return list(OrderedDict.fromkeys(path))

    def dv(self, vec):
        dX = 1 if vec[0] > 0 else (-1 if vec[0] < 0 else 0)
        dY = 1 if vec[1] > 0 else (-1 if vec[1] < 0 else 0)
        horrizontally = abs(vec[0]) > abs(vec[1])
        return (dX if horrizontally else 0, dY if not horrizontally else 0)

    def dirv(self, vec):
        dx = 1 if vec[0] > 0 else -1 if vec[0] < 0 else 0
        dy = 1 if vec[1] > 0 else -1 if vec[1] < 0 else 0
        return (dx, dy)

    def near(self, noCell, noCell2, rad=1):
        dX = abs(self.x(noCell) - self.x(noCell2))
        dY = abs(self.y(noCell) - self.y(noCell2))
        return dX + dY <= rad

    def getVecine(self, noCell, conv = lambda idx: idx):
        return [conv(noCell + step) for step in [-self.face, 1, +self.face, -1] if self.size > noCell + step and noCell + step > 0 and self.near(noCell, noCell + step)]

    def x(self, idCell):
        return (idCell - 1) % self.face
    def y(self, idCell):
        return int((idCell - 1) / self.face)
    def xy(self, idCell):
        return (self.x(idCell), self.y(idCell))

    def getEnvironment(self, noCell):
        placeType = self.terrain[noCell-1]['landscape']
        return self.landscapes[placeType-1]['Environment']

    def getRadius(self, noCell, rad):
        if rad - 1 > len(self.vecines):
            raise Exception("Radius is very wide")
        if rad < 1:
            raise Exception("Radius is very tight")
        return [noCell + step for step in self.vecines[rad] if self.size > noCell + step and noCell + step > 0 and self.near(noCell, noCell + step)]

    def getId(self, x, y):
        return 1 + x + y * self.face

    def getMove(self, pos, vec):
        return pos + vec[0] + self.face * vec[1]

    def step_back(self, vec):
        return (-vec[0], -vec[1])

class Arrow(PathTools):
    def findPath(self, a, b):
        return self.linear(a, b)

    def calcPathDifficult(self, path):
        cost = 0.0
        curr = path[0]
        for nextCell in path:
            if curr == nextCell:
                continue

            # Unknown and enemity land
            cost = cost + self.calcMoveCost(curr, nextCell)
            curr = nextCell
        return cost

    def calcPathLong(self, path):
        return len(path)

    def calcMoveCost(self, curr, idCell):
        return 0.3

class Tracer(PathTools):
    def __init__(self, terrain, domains, face):
        PathTools.__init__(self, face, terrain)
        self.domains = domains

    def findPath(self, a, b):
        return self.trace(a, b)

    def calcPathDifficult(self, path):
        cost = 0.0
        curr = path[0]
        escape = self.terrain[curr-1]
        self.marshal = self.domains[escape['domain'] - 1]['owner']
        for nextCell in path:
            if curr == nextCell:
                continue

            # Unknown and enemity land
            cost = cost + self.calcMoveCost(curr, nextCell)
            curr = nextCell
        return cost

    def calcPathLong(self, path):
        longs = 0.0
        curr = path[0]
        escape = self.terrain[curr-1]
        marshal = self.domains[escape['domain'] - 1]['owner']
        for nextCell in path:
            enter = self.terrain[nextCell-1]
            inDomain = enter['domain'] - 1
            lordOfNext = self.domains[inDomain]['owner']
            lordOfPlace = self.domains[self.terrain[curr - 1]['domain'] - 1]['owner']
            longs = longs + (0.3 if marshal == lordOfNext and lordOfPlace == lordOfNext else 1)
            curr = nextCell
        return int(math.ceil(longs))

    def calcMoveCost(self, curr, idCell):
        enter = self.terrain[nextCell-1]
        inDomain = enter['domain'] - 1
        return 0.0 if marshal == self.domains[inDomain]['owner'] else 0.6

    def around(self, a, b, horizontal=True, frame=None):
        path = []
        if frame == None:
            (aX, aY) = (self.x(a-1), self.y(a-1))
            (bX, bY) = (self.x(b-1), self.y(b-1))
            frame = ((aX, bX) if aX <= bX else (bX, aX), (aY, bY) if aY <= bY else (bY, aY))
        x = bX
        y = bY
        if horizontal:
            for x in range(aX, bX):
                path.append(self.getId(x, y))
            for y in range(aY, bY):
                path.append(self.getId(x, y))
        else:
            for y in range(aY, bY):
                path.append(self.getId(x, y))
            for x in range(aX, bX):
                path.append(self.getId(x, y))
        return (path, frame)

class Flat(Tracer):
    def __init__(self, terrain, domains, landscapes, face):
        Tracer.__init__(self, terrain, domains, face)
        self.heights = [place['height'] for place in terrain]
        self.landscapes = landscapes

    # Method: greedy search by cost of moving between environments
    def findPath(self, a, b):
        curr = a
        path = [a]
        debug_counter = 20
        r = random.Random()
        while curr != b:
            envFrom = self.landscapes[self.terrain[curr-1]['landscape']]['Environment']
            d = self.dirv(v(curr, b, self.face))
            if (d[0] == 0) and (d[1] == 0):
                break

            toX = self.getMove(curr, (d[0], 0))
            toY = self.getMove(curr, (0, d[1]))
            envX = self.getEnvironment(toX)
            envY = self.getEnvironment(toY)
            costX = Environments.Cost[envFrom][envX]
            costY = Environments.Cost[envFrom][envY]

            case = curr
            if d[1] == 0 or costX < costY:
                case = toX
            elif d[0] == 0 or costX > costY:
                case = toY
            else:
                case = toX if r.randint(0, 1) == 0 else toY
                (c_x, c_y) = (self.x(curr), self.y(curr))
                (n_x, n_y) = (self.x(case), self.y(case))
                print("Position: ({:d}, {:d}). Random: ({:d}, 0) or (0, {:d}). Moved at ({:d}, {:d})".format(c_x, c_y, d[0], d[1], n_x, n_y))
            if case == curr:
                (c_x, c_y) = (self.x(case), self.y(case))
                print("Circled at ({0:d}, {1:d}) is {2:d}. Vector: ({3:d}, {4:d})".format(c_x, c_y, curr, d[0], d[1]))
                break
            path.append(case)
            curr = case

            debug_counter = debug_counter - 1
            if debug_counter == 0:
                (c_x, c_y) = (self.x(curr), self.y(curr))
                (n_x, n_y) = (self.x(case), self.y(case))
                print("Stoped in ({0:d},{1:d}). Move at ({2:d},0) cost a {3:0.02f}. Move at (0,{4:d}) cost a {5:0.02f}. Moved to ({6:d},{7:d})".format(c_x, c_y, d[0], costX, d[1], costY, n_x, n_y))
                break
        return path

    def calcMoveCost(self, curr, idCell):
        if curr == idCell:
            return 0.00
        envFrom = self.getEnvironment(curr)
        envTo = self.getEnvironment(idCell)
        return Environments.Cost[envFrom][envTo]

class Merchant(Tracer):
    def __init__(self, terrain, domains, landscapes, face=10):
        Tracer.__init__(self, terrain, domains, face)
        self.landscapes = landscapes

    def findPath(self, a, b):
        trackt = Tracer.findPath(self, a, b)
        prev = None
        curr = a
        for c in trackt:
            difficult = self.calcMoveCost(curr, c)
            if difficult > 1.0:
                adapter = self.makeAdapterTerrain(prev, curr, c)
                if adapter == None:
                    return trackt[0:trackt.index(c)]
                before = self.terrain[curr-1]['landscape']
                self.terrain[curr-1]['landscape'] = adapter
                print("Terraformation of ({:d},{:d}): {:d} -> {:d}".format(self.x(c), self.y(c), before, adapter))
            prev = curr
            curr = c
        return trackt

    def calcMoveCost(self, idCurrent, idCell):
        if idCurrent == None and not idCell == None:
            return 0.000
        if not idCurrent == None and idCell == None:
            return 100000000.00
        if idCurrent == idCell:
            return 0.000
        envFrom = self.getEnvironment(idCurrent)
        envTo = self.getEnvironment(idCell)
        return Environments.Cost[envFrom][envTo]

    def makeAdapterTerrain(self, prev, curr, nextc):
        envPrev = self.getEnvironment(prev)
        envCurr = self.getEnvironment(curr)
        envNext = self.getEnvironment(nextc)

        def adaptable(enver):
            return Environments.Cost[envPrev][enver] < 10.0 and Environments.Cost[enver][envNext] < 10.0

        def findAdapters():
            envers = [enver for enver in range(Environments.Air, Environments.Port, 1) if adaptable(enver)]
            if len(envers) == 0:
                return [None]
            types = self.landscapes
            return [landscape['ID'] for landscape in types if envers.count(landscape['Environment']) > 0 and landscape['Civilization']]

        if adaptable(envCurr):
            return envCurr
        adapters = findAdapters()
        return envCurr if len(adapters) == 0 else adapters[0]

class Arounder(Tracer):
    TIRED = 0.001

    def __init__(self, terrain, domains, landscapes, face, energy = 1.0):
        Tracer.__init__(self, terrain, domains, face)
        self.energy = energy
        self.landscapes = landscapes

    def findPath(self, a, b):
        e = self.energy
        curr = a
        path = [curr]
        blocked = []
        explored = [a]

        vec = v(curr, b, self.face)
        primo = self.dv(vec)
        secondo = self.dirv(vec)
        turn = (abs(primo[1])*secondo[0], abs(primo[0])*secondo[1])

        (aX, aY) = (self.x(a), self.y(a))
        (bX, bY) = (self.x(b), self.y(b))
        frame = ((aX, bX) if aX <= bX else (bX, aX), (aY, bY) if aY <= bY else (bY, aY))

        def in_bound(pos):
            return pos[0] >= frame[0][0] and pos[0] <= frame[0][1] and pos[1] >= frame[1][0] and pos[1] <= frame[1][1] and pos > 0 and pos < self.size + 1

        def shift_way(pos, envFrom, energy):
            step = self.getMove(pos, turn)
            difficult = self.calcMoveCost(envFrom, step)
            already_blocked = blocked.count(step) > 0
            if already_blocked or not in_bound(step) or energy - difficult < -Arounder.TIRED:
                if not already_blocked:
                    blocked.append(step)

                turn = self.step_back(turn)
                step = self.getMove(pos, turn)
                difficult = self.calcMoveCost(envFrom, step)
                already_blocked = blocked.count(step) > 0
                if already_blocked or not in_bound(step) or energy - difficult < -Arounder.TIRED:
                    return path
            return step

        def next_step(new, e, difficult):
            path.append(new)
            e = e - difficult
            return e

        def retrit(pos, movement, difficult):
            blocked.append(pos)
            e = e + difficult
            return self.getMove(pos, movement)

        while not curr == b:
            ray = self.getMove(curr, primo)
            step = ray
            envFrom = self.getEnvironment(curr)
            difficult = self.calcMoveCost(envFrom, step)
            way_not_clear = blocked.count(step) > 0
            if (not ray == a and way_not_clear):
                curr = self.retrit(curr, primo)
                continue
            elif way_not_clear:
                step = shift_way(curr, envFrom, e)
                if not in_bound(step):
                    return path
                difficult = self.calcMoveCost(envFrom, step-1)

            if e - difficult > Arounder.TIRED:
                e = next_step(step, e, difficult)
                continue

            step = shift_way(curr, envFrom, e)
            if step != None:
                curr = next_step(step, difficult)
            else:
                step = retrit(curr, primo, difficult)
                difficult = self.calcMoveCost(envFrom, step)
                if e - difficult < -Arounder.TIRED:
                    return path
                curr = step

        return path

    def calcMoveCost(self, envFrom, idCell):
        envTo = self.getEnvironment(idCell)
        return Environments.Cost[envFrom][envTo]

class OrientFlat(Flat):
    def __init__(self, backbreaking, heigths, terrain, lanscapes, domains, face):
        Flat.__init__(self, heigths, terrain, lanscapes, domains, face)
        self.breaker = backbreaking

    def findPath(self, a, b):
        path = []
        traced = self.trace(a, b)
        return path

    def getBreakCellId(self, path, to=True):
        way = path if to else path.reverse()
        cost = 0.0
        iEnd = 0
        while cost < self.breaker and iEnd < len(way) - 1:
            iEnd = iEnd + 1
            cost = cost + self.calcMoveCost(path[iEnd-1], path[iEnd])
        return None if cost < self.breaker else iEnd

class Basic(Flat):
    def __init__(self, backbreaking, heigths, terrain, lanscapes, domains, face):
        Flat.__init__(self, heigths, terrain, lanscapes, domains, face)
        self.breaker = backbreaking

    def findPath(self, a, b):
        reacheable = [PathNode(a, cost=0, x=self.x(a), y=self.y(a))]
        reached = [a]
        explored = []

        while len(reacheable) > 0:
            node = self.chooseNode(reacheable)
            if node.id == b:
                return self.buildPath(node)
            reacheable.remove(node)
            reached.remove(node.id)
            explored.append(node.id)

            new_reached = [cell for cell in self.getVecine(node.id) if cell not in reached and cell not in explored]
            new_reacheable = [
                PathNode(adjacent, prev=node, cost=node.cost+self.calcMoveCost(node, adjacent), x=self.x(adjacent), y=self.y(adjacent))
                for adjacent in new_reached
            ]
            reacheable.extend(new_reacheable)
            reached.extend(new_reached)
        return None

    def getBreakCellId(self, path, to=True):
        way = path if to else path.reverse()
        cost = 0.0
        iEnd = 0
        while cost < self.breaker and iEnd < len(way) - 1:
            iEnd = iEnd + 1
            cost = cost + self.calcMoveCost(path[iEnd - 1], path[iEnd])
        return None if cost < self.breaker else iEnd

    def buildPath(self, end_node):
        path = []
        while end_node != None:
            path.append(end.node.id)
            end_node = end_node.prev
        return path

    def chooseNode(self, reacheable):
        return random.choise(reacheable)

def cell(ix, high, land, peasants, soldiers, idDomain = -1):
    return {'id': ix, 'landscape': land, 'domain': idDomain, 'height': high, 'population': peasants - soldiers, 'army': soldiers}

def domain(no, capitalID, ownerID=0):
    return {'id': no, 'name': "Domain #{}".format(no), 'capital': capitalID, 'owner': ownerID}

if __name__ == '__main__':
    face = 10
    r = random.Random()
    land = [1, 2, 4, 5, 9, 12, 16, 27, 28, 30]
    landing = [scape[1] for scape in lands.lands.items()]
    shaping = (face, face)

    box = [cell(i + 1, r.randint(100, 1500), r.choice(land), r.randint(10, 1000), r.randint(1, 100), r.randint(1, 3)) for i in range(0, face*face, 1)]
    capitals = [11, 18, 81, 88]
    domains = [domain(i + 1, capitals[i], i+1) for i in range(0, 3)]

    display = numpy.array([ landing[place['landscape']]['Environment'] for place in box ])
    screen = display.reshape(shaping)
    print("0 = Air, 1 = Earth, 2 = Water, 3 = Beach, 4 = Port")
    print(screen)

    display = numpy.array([cell['domain'] for cell in box])
    screen = display.reshape(shaping)
    print("Domains")
    print(screen)

    a = r.randint(1, face*face)
    b = r.randint(1, face*face)
    os.system('clear')
    print("From {0:d} to {1:d}".format(a,b))

    # Search path
    nav = Arounder(box, domains, landing, face, energy=2.0)
    path = nav.findPath(a, b)
    cost = nav.calcPathDifficult(path)
    timing = nav.calcPathLong(path)

    display = numpy.array(['__' for cell in box])
    i = 0
    for idCell in path:
        display[idCell-1] = "{:02d}".format(i)
        i = i + 1
    screen = display.reshape(shaping)
    print(screen)

    print("Path", path)
    print("Cost of path: {:4.2f}. Days long: {:d}".format(cost, timing))
