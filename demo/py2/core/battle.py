# -*- coding: utf-8 -*-
import sys
import random
import math
import logging
import json

history = logging.getLogger("battle.py")
fh = logging.FileHandler(filename="../history.log")
fmt = bytes("%(asctime)s — %(name)s — %(levelname)s — %(funcName)s:%(lineno)d — %(message)s", "utf-8")
formatter = logging.Formatter(fmt.decode("utf-8"))
fh.setFormatter(formatter)
history.addHandler(fh)

dice = random.Random()

"""
Enumerations
"""

class FormationBonus:
    """
    HIDE is minus to enemies range maximal attack distance from first row of formation.
    CLOSENESS is plus to shiels squer (<= 0.99) in time under enemy range attack.
    CLOSE is plus to shiels squer (<= 0.99) in time of malee.
    QUEUE is count of soldiers when will be strap up to front after enemy strike just-in-time.
    RAM is plus to damage in our malee strike.
    FLANKLESS is minus to bonus of flank's strike by enemy devision.
    """
    HIDE = 1 # used in Battle.calcCover()
    CLOSENESS = 2 # used in Division.blockRange()
    CLOSE = 3 # used in Division.blockMalee()
    QUEUE = 4 # used in Battle.distributeDamage()
    RAM = 5 # used in Division.calcDamageOfRow()
    FLANKLESS = 6 # uses in Division.blockMalee()

class Line:
    LEFT = -1
    CENTER = 0
    RIGHT = 1

class Attack:
    MALEE = 0
    RANGE = 1

class DivisionActivity:
    PREPARE = 0 # Wait in place, reformationing rows.
    MARSH   = 1 # Go to enemy
    RETREET = 2 # Go to backside
    STRIKE  = 3 # Malee attack
    COVER   = 4 # Range attack
    LEFT    = 5 # Exchange of place with more left (center, left wing) division or shift to left.
    RIGHT   = 6 # Exchange of place with more right (C, RW) division or shift to right.
    THIN    = 7 # Set a thin formation of division.
    BOLD    = 8 # Set a tight formation of division.
    DEFEAT  = 9 # Destruct formation and run/get captured/surrender.
    LOOTING = 10 # Kill enamy docters, loot baggage of enemy, capting man and woman.

class InjurySeverity:
    SUPERFICIAL = 0
    LIGHT = 1
    MODERATE = 2
    DANGEROUS = 3
    FATAL = 4

class EnergyConsumption:
    GO = 0.002
    ARROW = 0.003
    FIGHT = 0.01

class Transport:
    LEG = 20
    WAGONE = 50
    HORSE = 60

class Material:
    # Materials of fortification walls. (price of m**3, m**3 density (hp))
    WOOD = (0.5, 20.0)
    WODGROUND = (1.0, 50.00)
    WILDSTONE = (2.5, 100.00)
    ADOBE = (3.5, 150.00)
    BRICK = (12.0, 250)
    BOULDER = (50.00, 500)

"""
Decorators for serializable
"""
def jsonable(cls):
    class JSONED(cls):
        def __init__(self, *args, **kwargs):
            cls.__init__(self, *args, **kwargs)
        def toJSON(self):
            return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
    return JSONED

"""
Limited pre-compile classes.
"""
@jsonable
class Weapon:
    MUSCULE_LIMIT = 1000
    FULL_DEATH = 10
    TYPES = [{'near': 1, 'far': 2}, {'near': 200, 'far': 500}]

    def __init__(self, name, damage, typeRange, price={"gold": 2.0}, d=0, resource=200):
        self.name = name
        self.danger = min((max((1, damage)), Weapon.FULL_DEATH))
        self.type = typeRange
        basic = Weapon.TYPES[typeRange]
        self.D = max((min((d, Weapon.MUSCULE_LIMIT)), 1))
        self.price = price
        self.resource = resource if typeRange == Attack.MALEE else 0

    def calcRepairPrice(self):
        return self.price if self.type == Attack.RANGE else self.price / 2

@jsonable
class Shield:
    IDEAL = 0.98
    COMRADE = 0.5
    """ Defence of warriors. """
    def __init__(self, name, squer=0.2, resource=20):
        self.name = name
        self.squer = min((squer, 0.9))
        self.resource = resource
        self.price = {'gold': resource * squer + 0.2}

    def calcRepairPrice(self, left):
        return (self.resource - left) * self.squer

    def repair(self):
        self.resource = max((self.resource - 1, 0))
        self.left = self.resource

@jsonable
class SoldierProfile:
    def __init__(self, name, weapon, firetool, shield, transport, resource=3):
        self.name = name
        amm = weapon.resource if weapon is not None and weapon.type == Attack.MALEE else resource
        catridges = min((firetool.resource if firetool is not None else 0, resource))
        self.malee = weapon
        self.ranger = firetool
        self.shield = shield
        self.speed = transport if transport in (Transport.LEG, Transport.WAGONE, Transport.HORSE) else Transport.LEG
        w = weapon.price["gold"] if weapon is not None else 0.00
        a = shield.price["gold"] if shield is not None else 0.00
        f = firetool.price["gold"] if firetool is not None else 0.00
        self.price = {'gold': 1 * transport + w * (1 if amm > 0 else resource) + a + catridges * f}

@jsonable
class SeigeMachine(SoldierProfile):
    def __init__(self, name, distance, crashValue, corpus=None, resource=3, sequence=1):
        name_tool = "point" if distance < 5 else "ball"
        dia = Attack.MALEE if distance < 5 else Attack.RANGE
        price = 200.00 + 2.75 * resource * distance if distance > 4 else 150.00 + 10 * int(resource / 10)
        tool = Weapon(name_tool, crashValue, dia, {"gold": price}, d=distance, resource=resource)
        SoldierProfile.__init__(self, name, None, tool, corpus, Transport.WAGONE, resource=resource)
        self.sequence = sequence
        self.process = 0.00
        self.state = DivisionActivity.PREPARE
    def shot(self):
        if DivisionActivity.COVER != self.state:
            return None
        global dice
        self.process = self.process + self.sequence
        full = int(math.floor(self.process))
        if full < 1:
            return None
        self.process -= full
        if abs(self.process - 0.00) < 0.009:
            self.state = DivisionActivity.PREPARE
        return (full, self.ranger.danger, self.ranger.D)

# Battle formations:

@jsonable
class Formation:
    def __init__(self, name, density, pricePerSoldier=1.0):
        """ density is soldiers/m2 """
        self.name = name
        self.density = max([density, 4.0])
        self.columns = lambda amount: 10
        self.rows = lambda amount: int(amount / 10)
        self.bonus = 0
        self.bonus_value = 0
        self.pps = pricePerSoldier

class Sparse(Formation):
    """ Minimal chance of arraw to find a body. Bonus: - """
    def __init__(self):
        Formation.__init__(self, name="Sparse", density=0.3, pricePerSoldier=0.00)
        self.columns = lambda amount: int(math.sqrt(amount))
        self.rows = self.columns

class Persian(Formation):
    """ Less distantion of enemy range attack. Bonus: HIDE """
    def __init__(self):
        Formation.__init__(self, name="Persian", density=2, pricePerSoldier=0.5)
        self.rows = lambda amount: min((20, amount / 3))
        self.columns = lambda amount: int(amount / self.rows(amount))
        self.bonus = FormationBonus.HIDE
        self.bonus_value = 5

class Squer(Formation):
    """ Has no voulnerable in flanks of division. Bonus: FLANKLESS """
    def __init__(self):
        Formation.__init__(self, name="Squer", density=2.5, pricePerSoldier=2.0)
        self.columns = lambda amount: int(math.sqrt(amount))
        self.rows = self.columns
        self.bonus = FormationBonus.FLANKLESS
        self.bonus_value = 2

class Wawes(Formation):
    """ Less distance of enemy range attack. Bonus: QUEUE """
    def __init__(self):
        Formation.__init__(self, name="Wawes", density=1, pricePerSoldier=1.0)
        self.columns = lambda amount: int(amount / 2)
        self.rows = lambda amount: 2
        self.bonus = FormationBonus.QUEUE
        self.bonus_value = 5

class Phalanx(Formation):
    """ Soldiers cover for each other neighbour from enemy malee attack. Bonus: CLOSE """
    def __init__(self):
        Formation.__init__(self, name="Phalanx", density=4.0, pricePerSoldier=2.2)
        self.columns = lambda amount: min((int(math.sqrt(amount)), 256))
        self.rows = lambda amount: min((max((amount / self.columns(amount), 1)), 256))
        self.bonus = FormationBonus.CLOSE
        self.bonus_value = 0.2

class LinedPhalanx(Formation):
    """ Strapping up soldiers from previos lines to demaged lines. Save the order and  """
    def __init__(self):
        Formation.__init__(self, name="Lined Phalanx", density=4.0, pricePerSoldier=2.2)
        self.columns = lambda amount: min((int(math.sqrt(amount)), 256))
        self.rows = lambda amount: min((max((amount / self.columns(amount), 1)), 256))
        self.bonus = FormationBonus.QUEUE
        self.bonus_value = 10

class Tortue(Formation):
    """ Wall of shields to defence from arrows and another catridges. Bonus: CLOSENESS """
    def __init__(self):
        Formation.__init__(self, name="Tortue", density=4.0, pricePerSoldier=2.2)
        self.columns = lambda amount: min((int(math.sqrt(amount)), 100))
        self.rows = lambda amount: min((max((amount / self.columns(), 1)), 100))
        self.bonus = FormationBonus.CLOSENESS
        self.bonus_value = 0.4

class Wedge(Formation):
    """ Formation to ram. Bonus: RAM """
    def __init__(self):
        Formation.__init__(self, name="Wedge", density=3.0, pricePerSoldier=3.0)
        self.columns = lambda amount: int(amount / 2.5)
        self.rows = lambda amount: int(math.sqrt(amount))
        self.bonus = FormationBonus.RAM
        self.bonus_value = 2.0

class Defenders(Formation):
    def __init__(self, walls):
        Formation.__init__(self, name="Garrison", density=walls.wide*2, pricePerSoldier=0.0)
        self.columns = lambda amount: int(2 * walls.side)
        self.rows = lambda amount: int(walls.wide)
        self.bonus = FormationBonus.CLOSENESS
        self.bonus_value = min((1.00, walls.height / 10))

"""
Classes of in-time objects.
"""

#region Exceptions
class HumanControl(Exception):
    def __init__(self, owner):
        Exception.__init__(self, "Wait user control")
        self.caller = owner

class DayLeft(Exception):
    def __init__(self, time):
        Exception.__init__(self, "Day {} is left".format(time))
        self.time = time

class BattleEnded(Exception):
    def __init__(self, winner, loser, day):
        Exception.__init__(self, "General {} lose the battle on {} day.".format(winner.general.name, day))
        self.win = winner
        self.lose = loser
        self.day = day
#endregion Exceptions

@jsonable
class Division:
    def __init__(self, line, soldprof, force, formation, resource=0):
        self.army = None
        self.side = line
        self.profile = soldprof
        if soldprof is not None:
            self.malee_resources = soldprof.malee.resource if soldprof.malee is not None else 0
            self.catridges = resource if resource > 0 else (soldprof.ranger.resource if soldprof.ranger is not None else 0)
            self.shield_resource = soldprof.shield.resource if soldprof.shield is not None else 0
            self.point_wall = soldprof.malee.D if soldprof.malee is not None else 1
        else:
            self.malee_resources = 0
            self.catridges = 0
            self.shield_resource = 0
            self.point_wall = 0
        self.amount = force
        # Formation parameters calculating
        self._formation = {'class': formation}
        self._formation['columns'] = formation.columns(force)
        self._formation['rows'] = formation.rows(force)
        self.tail = force - self._formation['columns'] * self._formation['rows']
        self.width = self._formation['columns'] / formation.density
        self.length = self._formation['rows'] / formation.density
        self.density = formation.density
        self.energy = 1.0
        self.activity = (DivisionActivity.PREPARE, None)
        self.setDirection(-1)
        self.exp = 0.00

    def setDirection(self, v):
        self.marsh_at = v
        self.position = -v * 500.0
        self._start_position = self.position
    def move(self, crossed = 0.1):
        """ crossed is property 'cross' of landscape """
        realSpeed = self.profile.speed * (1.0 - crossed) * (1.0 - self.profile.shield.squer)
        return self.marsh_at * realSpeed
    def isQueen(self, pos):
        return abs(pos) >= abs(self.marsh_at * self._start_position) and self.marsh_at * pos > 0
    def blockMalee(self, front):
        global dice
        defence = 0.00
        if self.shield_resource > 0:
            defence = self.profile.shield.squer / front['sidekick_bonus']
            armory_bonus = self._formation['class'].bonus
            armory_plus = self._formation['class'].bonus_value
            if armory_bonus == FormationBonus.CLOSE:
                defence = min([defence + Shield.COMRADE,  defence + armory_plus, Shield.IDEAL])
            elif armory_bonus == FormationBonus.FLANKLESS and abs(front['sidekick_bonus'] - 1.0) > 0.1:
                defence = min((defence * armory_plus, self.profile.shield.squer))

        cols = front['cols']
        inRow = min((cols, self._formation['columns']))
        gap = 1.00 - defence
        hedgehog = front['perOne'] * front['cols'] + front['perOne']
        def calcWeaponed(rowNo):
            return min((inRow, dice.randint(0, int(inRow * gap * max((1, hedgehog - rowNo * front['perOne']))))))
        shielded = [calcWeaponed(rowNo) for rowNo in range(0, int(front['rows']))]
        self.shield_resource -= int(sum([count / self.amount for count in shielded]))
        return shielded
    def blockRange(self, beRanged, perOne):
        global dice
        defence = 0.00
        if self.shield_resource > 0:
            defence = self.profile.shield.squer
            if self._formation['class'].bonus == FormationBonus.CLOSENESS:
                defence = min([defence + self._formation['class'].bonus_value, 0.99])
        shielded = 0
        for _ in range(0, beRanged):
            if min((dice.random() * perOne, 1.00)) <= defence:
                shielded = shielded + 1
            else:
                targetedBy = dice.randint(1, perOne)
        self.shield_resource -= 0.1 * shielded/self.amount
        return shielded
    def calcFront(self, weapClass = Attack.MALEE, energy = 1.0, wing=Line.CENTER):
        maleeTool = self.profile.malee if weapClass == Attack.MALEE else self.profile.ranger
        density = self._formation['class'].density
        step = 1 / density
        far  = self.position + self.marsh_at *  int(maleeTool.D * min((1.0, energy)) + self._formation['rows'] * step)
        near = self.position + self.marsh_at *  max((int(0.1 * far), self._formation['rows'] * step))
        width = int(self._formation['columns'] * step)
        attackers = int((maleeTool.D * min((1.0, energy))) * width * (density ** 2))
        return {'width': width, 'near': near, 'far': far, 'step': step, 'amount': attackers, 'line': wing, 'see': self.marsh_at}
    def calcDamageOfRow(self):
        bonus = 0 if self._formation["class"].bonus != FormationBonus.RAM else self._formation["class"].bonus_value
        return self.energy * self.amount * self._formation['columns'] * self._formation['class'].density * min((self.profile.malee.danger + bonus, Weapon.FULL_DEATH))
    def getOrders(self, enemies):
        if self.army is None:
            return
        if self.army.general is None:
            self.activity = (DivisionActivity.RETREET, self.activity[1])
            return
        order = self.army.general.getCommandFor(self, enemies)
        if order is not None:
            self.activity = order
    def reorganization(self):
        force = self.amount
        if force < 10:
            return False
        formation = self._formation['class']
        cols = formation.columns(force)
        rows = formation.rows(force)
        self._formation['columns'] = int(cols)
        self._formation['rows'] = int(rows)
        self.tail = force - rows * cols
        self.length = int(rows) * self.density
        self.width = int(cols) * self.density
        self.energy -= EnergyConsumption.GO
        return True
    def reformation(self, cols):
        cols = int(cols)
        rows = self.amount // cols
        self._formation["columns"] = cols
        self._formation["rows"] = rows
        self.tail = self.amount - cols * rows
        self.energy -= EnergyConsumption.GO
        return True

@jsonable
class Fortification:
    """ Fortifies of towns and castles. """
    def __init__(self, material, height, side, wide=2.00):
        self.material = material
        self._height = height
        self._wide = wide
        self._side = side
        self._actual_height = height
        volume = wide * height * (4 * side)
        self._price = volume * material[0]
        self._hp = material[1] * volume / 4
        self._squer = (side - wide) ** 2

    def repair(self, coins):
        """ Return a price of repair a dangerous segment of walls. """
        repair = (self._height - self._actual_height) * self._side * self._wide
        price = repair * self.material[0]
        upTo = coins / (self.material[0] * self._side * self._wide)
        self._actual_height = min((self._actual_height + upTo, self._height))
        return min((price, coins))

    def calcUpgradePrice(self, newHeight):
        if self._height > newHeight:
            raise Exception("Walls is not deconstructable.")
        repair = (self._height - self._actual_height) * self._side * self._wide
        upAt = (newHeight - self._height) * (4 * self._side) * self._wide
        workKoeff = newHeight / self._height
        return (repair + workKoeff * upAt) * self.material[0]

    def applyDamage(self, damage):
        global history
        self._hp -= damage
        self._actual_height = self._hp / (self.material[1] * self._wide * self._side)
        ah = self._actual_height
        history.debug("Wall took a damage {damage}. Current the lowest wall height is {ah}")

    height = property()
    actual_height = property()
    wide = property()
    price = property()
    squer = property()
    hp = property()

    @height.getter
    def height(self):
        return self._height
    @height.setter
    def height(self, new):
        if new < self._height:
            raise Exception("Walls is not deconstructable.")
        self._height = new
        if new > self._actual_height:
            self._actual_height = new
    @actual_height.getter
    def actual_height(self):
        "Height of the lowest segment of walls."
        return self._actual_height
    @wide.getter
    def wide(self):
        return self._wide
    @squer.getter
    def squer(self):
        return self._squer
    @price.getter
    def price(self):
        return self._price
    @hp.getter
    def hp(self):
        return self._hp

def distance(regiment1, regiment2):
    av1 = regiment1.position * regiment2.marsh_at
    av2 = regiment2.position * regiment1.marsh_at
    intersec = (av1 < av2 and regiment1.marsh_at < regiment2.marsh_at) or (av1 > av2 and regiment1.marsh_at > regiment2.marsh_at)
    return abs(regiment1.position - regiment2.position) if not intersec else 0

# AI who will control a divisions in battle.
@jsonable
class General(object):
    """Human player or AI in battle-time."""
    def __init__(self, uid, name):
        self.uid = uid
        self.name = name
    def inBattle(self, forces, enemies, landscape, fort = None):
        self.army = forces
        self.opponent = enemies
        self.fort = fort
        self.assessment = []
        self.cell = landscape
    def riskAssessment(self, minute):
        """
        General sees a battlefield and makes a decision about of main goals.
        Return a list of goals.
        Goal is (regiment, opponent).
        """
        raise NotImplementedError()
    def makeDecisions(self, goals):
        """ Make orders for all our regiments. """
        raise NotImplementedError()
    def getCommandFor(self, division, enemies):
        raise NotImplementedError()
    def distanceBetween(self, div1, div2):
        av1 = div1.position * div2.marsh_at
        av2 = div2.position * div1.marsh_at
        horizontale = 0 if div1.side == div2.side else abs(div2.side - div1.side) * (div1.width + div2.width) / 2
        intersec = (av1 < av2 and div1.marsh_at < div2.marsh_at) or (av1 > av2 and div1.marsh_at > div2.marsh_at)
        return abs(div1.position - div2.position) if not intersec else 0

@jsonable
class GeneralAI(General):
    def riskAssessment(self, minute):
        orders = []
        if minute == 0:
            orders.append((self.army.left, self.opponent.right))
            orders.append((self.army.center, self.opponent.center))
            orders.append((self.army.right, self.opponent.left))
        else:
            our = [self.army.left, self.army.center, self.army.right]
            they = [self.opponent.right, self.opponent.center, self.opponent.left]
            powerMap = [self.suprimative(regiment, target) for regiment in out for target in they]
            sorted(powerMap, key=lambda case: case[3] + case[2], reverse=True)
        return orders
    def getCommandFor(self, division, enemies):
        arcs = division.profile.ranger
        if division.army.general.uid != self.uid:
            return None
        line = division.side
        if line == Line.LEFT:
            op = self.opponent.right
            d = self.distanceBetween(division, op)
            if arcs is not None and d > arcs.D * division.energy:
                op = self.opponent.center
            return self.makeCommandIf(division, op)
        if line == Line.RIGHT:
            op = self.opponent.left
            d = self.distanceBetween(division, op)
            if arcs is not None and d > arcs.D * division.energy:
                op = self.opponent.center
            return self.makeCommandIf(division, op)
        if line == Line.CENTER:
            op = self.opponent.center
            d = self.distanceBetween(division, op)
            if arcs is not None and d > arcs.D * division.energy:
                d1 = self.distanceBetween(division, self.opponent.left)
                d2 = self.distanceBetween(division, self.opponent.right)
                op = self.opponent.left if d1 < d2 else self.opponent.right
            return self.makeCommandIf(division, op)
        return None
    def makeCommandIf(self, division, op):
        # Thinking...
        distance = self.distanceBetween(division, op)
        # Limit of range distance by division
        arcs = division.profile.ranger
        firesAt = arcs.D * division.energy if arcs is not None and division.catridges > 0 else 0.000
        # Critical damage to this division formation.
        unformation = (division._formation['columns'] * division._formation['class'].density - 2) * 2 * Weapon.FULL_DEATH
        if op.side != division.side:
            firesAt = 0.6 * firesAt
        canTook = op.calcDamageOfRow()

        # Ordering:
        if distance <= division.profile.malee.D:
            return (DivisionActivity.STRIKE if division.amount >= 0.1 * op.amount else DivisionActivity.RETREET, op)
        if division.tail > division._formation['columns']:
            return (DivisionActivity.PREPARE, op)
        if division.activity[0] == DivisionActivity.RETREET and distance > op.profile.malee.D:
            return (DivisionActivity.PREPARE, op)
        if distance > firesAt:
            return (DivisionActivity.MARSH, op)
        if arcs is None and canTook > unformation:
            return (DivisionActivity.RETREET if distance <= op.profile.malee.D else DivisionActivity.STRIKE, op)
        elif canTook >= unformation and distance < int(0.6 * arcs.D):
            return (DivisionActivity.RETREET if division.profile.speed >= op.profile.speed and distance <= op.profile.malee.D else DivisionActivity.COVER, op)
        return (DivisionActivity.STRIKE if distance <= division.profile.malee.D else DivisionActivity.COVER, op)
    def suprimative(self, regiment, target):
        d = self.distanceBetween(regiment, target) - regiment.move_at*target.move_at*target.move(self.cell)
        suprimo = (regiment.amount/target.amount - regiment.profile.shield.squer - target.profile.shield.squer) * (regiment.calcDamageOfRow() - target.calcDamageOfRow()) * abs(regiment.side - target.side)
        return (regiment, target, d, suprimo)

@jsonable
class Army:
    def __init__(self, owner, left=None, center=None, right=None):
        global dice
        if left is not None:
            left.army = self
        if center is not None:
            center.army = self
        if right is not None:
            right.army = self
        self.left = left
        self.center = center
        self.right = right
        self.general = owner
        self.machines = Division(Line.CENTER, None, 0, Sparse(), resource=0)
        self.hospital = {"left": [0, 0, 0, 0, 0], "center": [0, 0, 0, 0, 0], "left": [0, 0, 0, 0, 0]}
        self.medics = 0
        self.energy = 1.0
        self.story = []

        # Treasure of army
        price = 0.00
        count = 0
        if left is not None:
            price = price + left.profile.price['gold']
            count = count + left.amount
        if right is not None:
            price = price + right.profile.price['gold']
            count = count + right.amount
        if center is not None:
            price = price + center.profile.price['gold']
            count = count + center.amount
        self.gold = dice.randint(int(math.ceil(price)), int(math.ceil(price * count)))
        self.captured = 0
    def addMachines(self, machineType, count, resources=0):
        self.machines = (machineType, count, resource)
    def rest(self, time, place):
        self.energy = min((self.energy + place['comfort'], 1.0))
        healers = self.medics
        for wound in InjurySeverity.__dict__:
            room = InjurySeverity.__dict__[wound]
            palate = self.hospital[room]
            for i in ("center", "right", "left"):
                toHeal = 0
                if healers > 1:
                    toHeal = min((palate[i], healers))
                    palate[i] -= toHeal
                    healers -= toHeal
                if room < InjurySeverity.MODERATE and toHeal > 0:
                    division = self.center if i == "center" else (self.left if i == "left" else self.right)
                    division.amount += toHeal
                    self.story.append("Day {}. {} soldiers is recicled in {} division.".format(time, toHeal, i))
                elif toHeal > 0:
                    self.hospital[room - 1][i] += toHeal
                if room > InjurySeverity.LIGHT:
                    deterioration = palate[i]
                    palate[i] = 0
                    if room < InjurySeverity.FATAL:
                        self.hospital[room+1][i] += deterioration
                    else:
                        self.story.append("Day {}. Division {} lose {} wounded soldiers.")
    def prepareToFight(self, time, place):
        if self.left is not None: self.left.energy = self.energy
        if self.center is not None: self.center.energy = self.energy
        if self.right is not None: self.right.energy = self.energy

class BattleFrame:
    def __init__(self, minute, day, farside, nearside, fort=None):
        self.day = day
        self.minute = minute
        if isinstance(farside, Army):
            self.farside = self._makeArmyStatus(farside)
        if isinstance(nearside, Army):
            self.nearside = self._makeArmyStatus(nearside)
        if isinstance(fort, Fortification):
            self.fort = fort
    def _makeArmyStatus(self, obj):
        army = {}
        if isinstance(obj, Army):
            if obj.left is not None: army["left"] = self._makeRegimentStatus(obj.left)
            if obj.center is not None: army["center"] = self._makeRegimentStatus(obj.center)
            if obj.right is not None: army["right"] = self._makeRegimentStatus(obj.right)
            #army["mashines"] = self._makeRegimentStatus(obj.machines)
            #army["captured"] = obj.captured
            #army["medics"] = obj.medics
            #army["gold"] = obj.gold
        return army
    def _makeRegimentStatus(self, obj):
        if isinstance(obj, Division):
            regiment = {"resources": {"malee": obj.malee_resources, "range": obj.catridges, "armor": obj.shield_resource}}
            regiment["amount"] = obj.amount
            regiment["position"] = obj.position
            #regiment["formation"] = obj._formation["class"]
            #regiment["width"] = obj.width
            #regiment["length"] = obj.length
            #regiment["tail"] = obj.tail
            #regiment["density"] = obj.density
            #regiment["energy"] = obj.energy
            regiment["order"] = self.decodeOrder(obj.activity[0])
            regiment["view"] = obj.marsh_at
            return regiment
        return None
    def _makeFortifiednesStatus(self, obj):
        fort = {}
        if isinstance(obj, Fortification):
            fort["actual_height"] = obj.actual_height()
            fort["hp"] = obj.hp()
            return fort
        return None
    def decodeOrder(self, order):
        if order == DivisionActivity.BOLD: return "Concentrate"
        if order == DivisionActivity.COVER: return "Fire"
        if order == DivisionActivity.DEFEAT: return "Surrender"
        if order == DivisionActivity.LEFT: return "Move to Left"
        if order == DivisionActivity.LOOTING: return "Looting"
        if order == DivisionActivity.MARSH: return "Marsh"
        if order == DivisionActivity.PREPARE: return "Rest"
        if order == DivisionActivity.RETREET: return "Retreet"
        if order == DivisionActivity.RIGHT: return "Move to Right"
        if order == DivisionActivity.STRIKE: return "Attack"
        if order == DivisionActivity.THIN: return "Deconcentrate"
        return "Rest"

class Battle:
    BATTLE_DAY = 24 * 60 * 60
    ROW_DESTRACTION = 0.5
    REAR_STRIKE_BONUS = 5.0

    def __init__(self, your, enemy, circle, place):
        self.cell = place
        if enemy.left is not None: enemy.left.setDirection(-1)
        if enemy.center is not None: enemy.center.setDirection(-1)
        if enemy.right is not None: enemy.right.setDirection(-1)
        if your.left is not None: your.left.setDirection(1)
        if your.center is not None: your.center.setDirection(1)
        if your.right is not None: your.right.setDirection(1)
        enemy.prepareToFight(circle, place)
        enemy.general.inBattle(enemy, your)
        your.prepareToFight(circle, place)
        your.general.inBattle(your, enemy)
        self.farside = enemy
        self.nearside = your
        # Losses of soldiers: (wounded, killed, captured) in left, center and right division
        self.casualtis = {enemy.general.name: [(0, 0, 0), (0, 0, 0), (0, 0, 0)], your.general.name: [(0, 0, 0), (0, 0, 0), (0, 0, 0)]}
        # Areas of fire and fight
        self.fire_areas = []
        # Time in battle
        self.time = 1
        self.day = circle
        self.timespeed = 1
        self.frames = []
        self.frames.append(BattleFrame(minute=self.time, day=self.day, farside=self.farside, nearside=self.nearside))

        self.wondedList = []
        self.moves = []
    def play(self, longtime):
        """
        One circle of battle time.
        longtime - limit of circle length.
        """
        self.fire_areas = []
        if self.farside.center is not None: self.farside.center.getOrders(self.nearside)
        if self.nearside.center is not None: self.nearside.center.getOrders(self.farside)
        if self.farside.left is not None: self.farside.left.getOrders(self.nearside)
        if self.nearside.right is not None: self.nearside.right.getOrders(self.farside)
        if self.farside.right is not None: self.farside.right.getOrders(self.nearside)
        if self.nearside.left is not None: self.nearside.left.getOrders(self.farside)

        land = self.cell.landscape
        if self.nearside.center is not None: self.executeOrders(self.nearside.center, longtime)
        if self.farside.center is not None: self.executeOrders(self.farside.center, longtime)
        if self.nearside.right is not None: self.executeOrders(self.nearside.center, longtime)
        if self.farside.left is not None: self.executeOrders(self.farside.center, longtime)
        if self.nearside.left is not None: self.executeOrders(self.nearside.center, longtime)
        if self.farside.right is not None: self.executeOrders(self.farside.center, longtime)

        self.time += self.apply(self.wondedList, self.moves)
        self.frames.append(BattleFrame(minute=self.time, day=self.day, farside=self.farside, nearside=self.nearside))

        far_loss = 0
        near_loss = 0
        if self.destroyed(self.farside.left): far_loss = far_loss + 1
        if self.destroyed(self.farside.center): far_loss = far_loss + 1
        if self.destroyed(self.farside.right): far_loss = far_loss + 1
        if self.destroyed(self.nearside.left): near_loss = near_loss + 1
        if self.destroyed(self.nearside.center): near_loss = near_loss + 1
        if self.destroyed(self.nearside.right): near_loss = near_loss + 1
        if far_loss == 3 and near_loss < 3:
            raise BattleEnded(self.nearside, self.farside, day=self.day)
        elif far_loss < 3 and near_loss == 3:
            raise BattleEnded(self.farside, self.nearside, day=self.day)

        if self.time >= Battle.BATTLE_DAY:
            self.time = 0.00
            self.day = self.day + 1
            raise DayLeft(self.dea - 1)
    def executeOrders(self, division, longtime):
        """ Execute battle-context-dependenced order. """
        global dice
        order, target = division.activity
        inline = division.side == target.side
        damagePoints = division.profile.ranger.danger if division.profile.ranger is not None else 0
        landscape = self.cell.landscape
        pikes = max((division.point_wall, target.point_wall))
        d = distance(regiment1=division, regiment2=target) - pikes

        # moving status
        verse = division.marsh_at * target.marsh_at < 0
        me_attack = division.marsh_at * division._start_position < 0
        they_attack = target.marsh_at * target._start_position < 0
        incomming = verse and me_attack and they_attack

        if order == DivisionActivity.MARSH:
            if not incomming:
                division.marsh_at = - division.marsh_at
                return
            if division.energy < EnergyConsumption.GO:
                division.energy += EnergyConsumption.GO
                return
            # Calc a speed of incomming and time to comming
            marsh = division.move(landscape.cross)
            speed = marsh + -target.move(landscape.cross)
            timeTo = min((longtime * self.timespeed, abs(d / speed)))
            self.moves.append((division, marsh, timeTo))
            stepped = timeTo * marsh
            pos = division.position + stepped
            if abs(pos - division.position) < max((target.point_wall, division.point_wall)):
                division.activity = (DivisionActivity.PREPARE, target)
            if division.isQueen(pos):
                division.activity = (DivisionActivity.LOOTING, target)
            return
        if order == DivisionActivity.COVER:
            if division.energy <= EnergyConsumption.ARROW:
                division.energy += EnergyConsumption.GO
                division.activity = (DivisionActivity.PREPARE, target)
                return
            if division.catridges < 1:
                division.energy += EnergyConsumption.GO
                division.activity = (DivisionActivity.RETREET, target)
                return
            if division.profile.ranger is None:
                division.energy += EnergyConsumption.GO
                division.activity = (DivisionActivity.RETREET, target)
                return
            area = division.calcFront(Attack.RANGE, division.energy, division.side)
            area['type'] = DivisionActivity.COVER
            self.fire_areas.append(area)
            if not inline:
                area['width'] *= math.sin(math.pi * 0.3)
                area['height'] *= math.cos(math.pi * 0.3)
            underAttack = self.calcCover(target, area)
            if underAttack is None or underAttack['rows'] < 1 or underAttack['cols'] < 1: return
            timeOf = max((0.1, 1.0 - division.exp))
            self.wondedList.append([Attack.RANGE, target, underAttack, damagePoints, timeOf, False])
            division.energy -= EnergyConsumption.ARROW
            return
        if order == DivisionActivity.STRIKE:
            if division.energy <= EnergyConsumption.FIGHT:
                # Sir, soldiers is tided.
                division.energy += EnergyConsumption.GO
                division.activity = (DivisionActivity.RETREET, target)
                return
            if division.malee_resources == 0:
                # Weapon of this division is invalided.
                division.energy += EnergyConsumption.GO
                division.activity = (DivisionActivity.RETREET, target)
                return
            if target.tail >= target.amount:
                # Enemy division has not order and cannot fight.
                if division.tail >= division.amount:
                    division.energy += EnergyConsumption.GO
                    target.activity = (DivisionActivity.RETREET, division)
                    division.activity = (DivisionActivity.RETREET, target)
                    return
                division.energy += EnergyConsumption.GO
                division.activity = (DivisionActivity.LOOTING, target)
                target.activity = (DivisionActivity.DEFEAT, division)
                return
            front = division.calcFront(Attack.MALEE, division.energy, target.side)
            front = self.clash(target, front)
            if front is not None:
                timeOf = max((0.1, 1.0 - division.exp))
                powerPoints = division.profile.malee.danger if division.profile.malee is not None else 0
                self.wondedList.append([Attack.MALEE, target, front, powerPoints, timeOf, False])
            target.activity = (target.activity[0], division)
            division.energy -= EnergyConsumption.FIGHT
            return
        if order == DivisionActivity.DEFEAT:
            #TODO Defeating od division.
            return
        # In baggage of enemy
        if order == DivisionActivity.LOOTING:
            roger = division.army
            victum = target.army
            roger.gold = roger.gold + victum.gold
            victum.gold = 0

            #TODO Marodering enemy division's bodies.


            # Kills a doctors, captures and kills a they clients
            if victum.medics > 0:
                roger.medics = roger.medics + int(victum.medics / 2)
                victum.medics = 0
            for wing in victum.hospital:
                palates = victum.hospital[wing]
                for injurity in palates:
                    if injurity < InjurySeverity.MODERATE:
                        roger.captured = roger.captured + palates[injurity]
                    palates[injurity] = 0

            # What victum (enemy) will do?
            victum.left.activity = (DivisionActivity.DEFEAT, division)
            victum.center.activity = (DivisionActivity.DEFEAT, division)
            victum.right.activity = (DivisionActivity.DEFEAT, division)

            division.marsh_at = - division.marsh_at
            return
        if order == DivisionActivity.RETREET:
            if not incomming:
                division.marsh_at = - division.marsh_at
                return
            if division.energy < EnergyConsumption.GO:
                division.energy += EnergyConsumption.GO
                return
            speed = -division.move(landscape.cross)
            timeTo = min((longtime * self.timespeed, abs(d / speed)))
            self.moves.append((division, speed, timeTo))
            if abs(division.position - toMarch) > abs(division._start_position):
                division.activity = (DivisionActivity.DEFEAT, None)
            return
        if order == DivisionActivity.PREPARE:  division.reorganization()
        return
    def apply(self, casualists, moves):
        left_time_move = min([move[2] for move in moves]) if len(moves) > 0 else self.timespeed
        left_time_fight = min([act[4] for act in casualists]) if len(casualists) > 0 else left_time_move
        left_time = min((left_time_move, left_time_fight))
        for moving in moves:
            division, v, _ = moving
            movement = left_time * v
            division.position += movement
            division.energy -= EnergyConsumption.GO

        for case in casualists:
            close, target, underAttack, damagePoints, timeOf, ok = case
            if ok: continue
            timeOf -= left_time
            ok = timeOf <= 0
            if close == Attack.RANGE and ok:
                whole = min((int(underAttack['cols'] * underAttack['rows'] * target.density), target.amount))
                shielded = target.blockRange(whole, underAttack['perOne'])
                wounded = whole - shielded
                for rowNo in range(1, underAttack['rows']):
                    if wounded < 1: break
                    wounded = self.distributeDamage(target, wounded, underAttack['perOne'], damPoints=damagePoints)
            elif ok:
                surviving = target.blockMalee(underAttack)
                #TODO Disctributing damage in malee fight.
                for soldiers in surviving:
                    if soldiers < 1: break
                    wounded = underAttack['cols'] * target.density - soldiers
                    self.distributeDamage(target, victums=wounded, density=underAttack['perOne'], damPoints=damagePoints, full=True)
            casualists[casualists.index(case)] = (close, target, underAttack, damagePoints, timeOf, ok)
            # Bonus of phalanx
            #target.reorganization()
        self.moves = []
        self.wondedList = [case for case in casualists if not case[5]]

        return left_time
    def calcCover(self, division, area):
        """ Get area and soldivers who was under arrow cloud. """
        if area['line'] != division.side:
            return None
        width = min((area['width'], division.width))
        simmetry = -division.marsh_at
        simm_far = simmetry * area['far']
        simm_near = simmetry * area['near']
        simm_avan = simmetry * division.position
        simm_back = simmetry * (division.position + simmetry*division.length)
        if simm_back < simm_near or simm_avan > simm_far:
            return None
        near = max((simm_near, simm_avan))
        far = min((simm_far, simm_back))
        hide_bonus = 0 if division._formation["class"].bonus != FormationBonus.HIDE else division._formation["class"].bonus_value
        densityFire = area['step'] / division.density
        deep = max((far - near - hide_bonus, 0))
        return {'cols': division.density * width, 'rows': division.density * deep, 'perOne': densityFire, 'far': area['far'], 'near': area['near']}
    def clash(self, division, front):
        flankKoeff = abs(division.side - front['line']) + 1.0
        if division.marsh_at == front['see']:
            flankKoeff = self.REAR_STRIKE_BONUS
        width = min((front['width'], division.width))
        simmetry = -division.marsh_at
        simm_far = simmetry * front['far']
        simm_near = simmetry * front['near']
        simm_avan = simmetry * division.position
        simm_back = simmetry * (division.position + simmetry*division.length)
        if simm_back < simm_near or simm_avan > simm_far:
            return None
        near = max((simm_near, simm_avan))
        far = min((simm_far, simm_back))
        deep = abs(far - near)
        den = division.density
        densityStrike = front['step'] * deep / (division.density ** 2)
        return {'cols': den * width, 'rows': 1, 'perOne': densityStrike, 'sidekick_bonus': flankKoeff}
    def distributeDamage(self, target, victums, density, damPoints=2, full=False):
        global dice
        if victums < 1:
            return 0
        goaled = dice.randint(0, victums) if not full else victums
        intoTail = min((int(target.width / target.density) - goaled, 0))
        if target._formation["class"].bonus == FormationBonus.QUEUE:
            canStrap = min((target._formation["class"].bonus_value, goaled, target.tail))
            if canStrap >= goaled:
                target.tail -= canStrap
                intoTail = 0
        target.tail += intoTail
        target.amount -= goaled
        side = "left" if target.side == Line.LEFT else ("right" if target.side == Line.RIGHT else "center")
        itog = self.casualtis[target.army.general.name][target.side + 1]
        wounded, killed, captured = itog
        # Distribute
        while goaled > 0:
            part = dice.randint(0, goaled)
            puts = dice.randint(1, math.ceil(density)) if math.ceil(density) > 1 else 1
            damage = damPoints * puts
            injurity = InjurySeverity.SUPERFICIAL
            if damage >= Weapon.FULL_DEATH:
                goaled = goaled - part
                killed = killed + part
                target.army.story.append("Division in {}of {} lost {} soldiers as killed.".format(side, target.army.general.name, part))
                continue
            if damPoints <= Weapon.FULL_DEATH - 2: injurity = InjurySeverity.FATAL
            if damPoints <= Weapon.FULL_DEATH / 2: injurity = InjurySeverity.DANGEROUS
            if damPoints <= Weapon.FULL_DEATH / 3: injurity = InjurySeverity.MODERATE
            if damPoints > 1: injurity = InjurySeverity.LIGHT
            target.army.hospital[side][injurity] += part
            goaled = goaled - part
            wounded = wounded + part
            target.army.story.append("Division in {} of {} lost {} soldiers as wounded.".format(side, target.army.general.name, part))
        captured = captured + 0
        self.casualtis[target.army.general.name][target.side + 1] = (wounded, killed, captured)
        return victums - goaled
    def destroyed(self, division):
        return division is None or division.amount <= 1 or division.activity[0] == DivisionActivity.DEFEAT or division.amount == division.tail or division.amount < 1

class Seige(Battle):
    def __init__(self, beseigers, beseiged, circle, place):
        Battle.__init__(self, beseigers, beseiged, circle, place)
        beseiged.machines.setDirecion(0)
        beseiged.fortress = place.fortress
        beseigers.machines.setDirecion(1)
    def time(self):
        """ One circle of battle time. """
        self.fire_areas = []
        self.farside.center.getOrders(self.nearside)
        self.nearside.center.getOrders(self.farside)
        self.farside.left.getOrders(self.nearside)
        self.nearside.right.getOrders(self.farside)
        self.farside.right.getOrders(self.nearside)
        self.nearside.left.getOrders(self.farside)
        self.nearside.machines.getOrders(self.farside)
        self.farside.machines.getOrders(self.nearside)

        if not self.nearside.center.act(): self.executeOrders(self.nearside.center)
        if not self.farside.center.act(): self.executeOrders(self.farside.center)
        if not self.nearside.right.act(): self.executeOrders(self.nearside.center)
        if not self.farside.left.act(): self.executeOrders(self.farside.center)
        if not self.nearside.left.act(): self.executeOrders(self.nearside.center)
        if not self.farside.right.act(): self.executeOrders(self.farside.center)

        far_loss = 0
        near_loss = 0
        if self.farside.left.activity[0] == DivisionActivity.DEFEAT: far_loss = far_loss + 1
        if self.farside.center.activity[0] == DivisionActivity.DEFEAT: far_loss = far_loss + 1
        if self.farside.right.activity[0] == DivisionActivity.DEFEAT: far_loss = far_loss + 1
        if self.nearside.left.activity[0] == DivisionActivity.DEFEAT: near_loss = near_loss + 1
        if self.nearside.center.activity[0] == DivisionActivity.DEFEAT: near_loss = near_loss + 1
        if self.nearside.right.activity[0] == DivisionActivity.DEFEAT: near_loss = near_loss + 1
        if far_loss == 3 and near_loss < 3:
            raise BattleEnded(self.nearside, self.farside, day=self.day)
        elif far_loss < 3:
            raise BattleEnded(self.farside, self.nearside, day=self.day)
        else:
            raise HumanControl(owner=self.nearside.general)

        self.time += 1
        if self.time >= Battle.BATTLE_DAY:
            self.time = 1
            self.day = self.day + 1
            raise DayLeft(self.dea - 1)

"""
Serialize Encoders and Decoders
"""


class BattleEncoder(json.JSONEncoder):
    def default(self, obj):
        description = {}
        if not isinstance(obj, Battle):
            if isinstance(obj, Army):
                description["left"] = self.default(obj.left)
                description["center"] = self.default(obj.center)
                description["right"] = self.default(obj.right)
                description["general"] = obj.general.name if obj.general is not None else None
                #description["machines"] = self.default(obj.machines or None)
                description["gold"] = obj.gold
                description["captured"] = obj.captured
                description["energy"] = obj.energy
                return description
            if isinstance(obj, Division):
                description["army"] = id(obj.army)
                description["side"] = obj.side
                description["profile"] = obj.profile.name
                description["width"] = obj.width
                description["length"] = obj.length
                description["tail"] = obj.tail
                description["density"] = obj.density
                description["energy"] = obj.energy
                description["position"] = obj.position
                description["energy"] = obj.energy
                description["order"] = self.decodeOrder(obj.activity[0])
                description["resources"] = {"malee": obj.malee_resources, "range": obj.catridges, "armor": obj.shield_resource}
                return description
            if isinstance(obj, GeneralAI) or isinstance(obj, General):
                description["uid"] = obj.uid
                description["name"] = obj.name
                description["army"] = id(obj.army)
                description["enemy"] = id(obj.opponent)
                return description
            if isinstance(obj, Formation) or issubclass(type(obj), Formation):
                description["name"] = obj.name
                return description
            return obj.__dict__ if obj is not None else None
        description["generals"] = [self.default(obj.farside.general), self.default(obj.nearside.general)]
        #description["divisions"] = []
        description["armies"] = {id(obj.farside): self.default(obj.farside), id(obj.nearside): self.default(obj.nearside)}

        #description["defenders"] = 0
        #description["intruders"] = 1
        #description["casualtis"] = obj.casualtis
        description['time'] = obj.time
        description['day'] = obj.day
        #description['timespeed'] = obj.timespeed
        #description['ground'] = None
        #description['fortification'] = None
        description['class'] = "Seige" if isinstance(obj, Seige) else "Battle"
        description['animation'] = [self.default(frame) for frame in obj.frames]
        return description
    def decodeOrder(self, order):
        if order == DivisionActivity.BOLD: return "Concentrate"
        if order == DivisionActivity.COVER: return "Fire"
        if order == DivisionActivity.DEFEAT: return "Surrender"
        if order == DivisionActivity.LEFT: return "Move to Left"
        if order == DivisionActivity.LOOTING: return "Looting"
        if order == DivisionActivity.MARSH: return "Marsh"
        if order == DivisionActivity.PREPARE: return "Rest"
        if order == DivisionActivity.RETREET: return "Retreet"
        if order == DivisionActivity.RIGHT: return "Move to Right"
        if order == DivisionActivity.STRIKE: return "Attack"
        if order == DivisionActivity.THIN: return "Deconcentrate"
        return "Rest"

class BattleDecoder(json.JSONDecoder):
    def __init__(self, diction):
        json.JSONDecoder.__init__(self, encoding="UTF-8")
        return None
