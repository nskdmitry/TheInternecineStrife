import math


class Landscape:
    """ Type of terrain.  """
    def __init__(self, name, cross):
        self.name = name
        self.cross = cross
    def a(self):
        pass

class Cell:
    """ Cell in map. """
    FULL_SIDE = 10000.00
    def __init__(self, landscape):
        self.landscape = landscape
        self.width = int(math.ceil(self.FULL_SIDE * (1.0 - landscape.cross)))
