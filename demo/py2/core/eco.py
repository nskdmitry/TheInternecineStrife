import random
import math
import logging

history = logging.getLogger("eco.py")

@jsonable
class Dwelling():
    """ Towns, cities, villages and castles. """
    def __init__(self, name, walls, owner, man=10):
        global dice
        self.name = name
        self.walls = walls
        self.owner = owner
        self.man = man
        self.woman = int(3*man/4)
        self.kids = dice.randint(1, 5 * man)
        Division.__init__(self, line=Line.CENTER, soldprof=None, force=0, formation=Persian())
