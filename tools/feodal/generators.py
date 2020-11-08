import os
import sys
import math
import random
import operator
import argparse
import logging
from collections import Counter
from operator import itemgetter

import feodal.stats
from feodal.lands import lands
from feodal.constants import Environments, Age, Orientation
import feodal.feods as feods
import feodal.MapTemplate as MT
from feodal.tools import Tools, loadJSON

import pdb

root = os.path.dirname(os.path.dirname(__file__))

"""
Layer's generators.
"""

class LayerGenerator:
    """ Abstract layer generator.  """
    def __init__(self, face):
        self.face = face
        self.size = face*face
        self.dependences = []
        self.latest = []

    def addLinks(self, generators):
        self.dependences.extend(generators)

    def generate(self, tools):
        """ Make a clear-new layer. """
        self.latest = [0 for _ in range(0, self.size)]
        return self.latest

    def updateCircle(self, tools):
        """ Update a layer from latest status. To make a many few a layers (like erosion and history). """
        times = tools.rand.randint(1, self.size)
        for _ in range(0, times):
            idCell = tools.rand.randint(0, self.size)
            self.latest[idCell] = self.latest[idCell] + 1

    def output(self, filePath, layer = None):
        layer = layer if layer != None else self.latest
        lineLength = self.face
        if not os.path.exists(os.path.dirname(filePath)):
            os.mkdir(os.path.dirname(filePath))
        with open(filePath, "w+") as block:
            rows = feods.chunks(layer, lineLength)
            pattern = "{: 05d}" if type(layer[0]) == type(1) else "{: 07.3f}"
            lines = [",".join([pattern.format(val) for val in row]) for row in rows]
            block.write(",\n".join(line for line in lines))
            block.close()

class Void(LayerGenerator):
    """ Fill the layer with once value """
    def init(self, face, fill=0):
        LayerGenerator.__init__(self, face)
        self.latest = [fill for i in self.size]
    def generate(self, tools):
        return self.latest

# Layer 0: Height's map

class VoolcanoIsland(LayerGenerator):
    """
    One big mount in the ocean
    """
    def __init__(self, face, top=5000, bottom=-5000, earth_wide = 0.6):
        LayerGenerator.__init__(self, face)
        self.lowest = bottom
        self.highest = top
        self.extremums = 4 * face - 1
        self.latest = [self.lowest for i in range(0, self.size)]
        r = random.Random()
        self.earth_wide = earth_wide if earth_wide >= 0.0 and earth_wide <= 1.0 else 2.0

    def generate(self, tools):
        """
        Layer #0 - map of heights.
        """
        def tune(height):
            return int(max([min([height, self.highest]), self.lowest]))
        def shift(height):
            low = height if height < 0 else (self.lowest + height) // 2
            high = (self.highest + height) // 2 if height > 0 else height
            return tools.rand.randint(low, high)

        if self.earth_wide > 1.0:
            self.earth_wide = tools.rand.random()
        C = self.size // 2 + self.face // 2 if self.face % 2 == 0 else self.size // 2
        D = int(math.ceil(self.face * self.earth_wide))
        for i in range(0, self.size):
            d = tools.dd(i, C)
            self.latest[i] = tune((self.lowest * d + self.highest * (D - d)) / D)
        self.updateCircle(tools)
        return self.latest

    def updateCircle(self, tools):
        """ Erosion and tectonic process: up and down of cells. """
        new = [height for height in self.latest]
        for i in range(0, self.size):
            if new[i] == self.highest:
                continue
            around = tools.getVecine(i, conv=lambda idCell: self.latest[idCell])
            tectonic = [high for high in around if high > new[i]]
            water = [high for high in around if high < new[i]]
            borders = (new[i], self.latest[i])
            up_down = tools.rand.randint(1, 2)
            if len(tectonic) > up_down:
                borders = (self.latest[i], (self.latest[i] + min(tectonic)) // 2)
            elif len(water) > up_down:
                borders = ((self.latest[i] + max(water)) // 2, self.latest[i])
            new[i] = tools.rand.randint(borders[0], borders[1])
        self.latest = new
        return new

class VoolcanoLake(LayerGenerator):
    """ Lake with circular wall of mounting. """
    def __init__(self, face, top=5000, bottom=-200):
        LayerGenerator.__init__(self, face)
        self.lowest = bottom
        self.highest = top
        self.extremums = 9
        self.earth_wide = 0.8

    def generate(self, tools):
        """
        Layer #0 - map of heights.
        """
        C = int(math.ceil(self.size / 2))
        D = int(math.ceil(self.face * self.earth_wide))

        side = (top + bottom) / 2
        knownHeights = {no: side for no in [0, self.size - 1, self.face - 1, self.size - self.face + 1]}

        def heightRegulator(i):
            d = tools.dd(i, C)
            if d > D:
                return int(max([min([self.lowest * d / D + self.highest * (D - d) / D, self.highest]), self.lowest]))
            return max([min([int(self.lowest * (D - d) / D + self.highest * d / D), self.highest]), self.lowest])

        self.latest[i] = [heightRegulator(i) for i in range(0, self.size)]
        return self.latest

class SmoothTerrainGenerator(LayerGenerator):
    def __init__(self, face, extrems = 0, top=5000, bottom=-5000, sea=0):
        LayerGenerator.__init__(self, face)
        self.extremums = extrems if extrems >= 0 else face
        self.lowest = bottom
        self.highest = top
        self.sealev = sea

    def generate(self, tools):
        """
        Layer #0 - Terrain (height's map)
        IN: int extrimes - count of bottom or highest cells on map
            bool sharping - bolding a extremums, not so smooth
        OUT: float[] - heights (km) of cell's centers
        """

        #all tops and bottoms
        case = random.Random()
        exterminals = {case.randint(0, self.size-1): self.highest if case.random() > 0.3 else self.lowest for i in range(0, self.extremums)}
        #exterminals[0] = self.lowest
        #exterminals[self.size-1] = self.lowest
        highmap = [int(math.floor(tools.smoothSlope(i, exterminals.get(i, self.sealev + 100), exterminals, 1.1))) for i in range(0, self.size)]

        # Output layer
        self.latest = highmap
        return highmap

    def updateCircle(self, tools):
        return VoolcanoIsland.updateCircle(self, tools)

class PikesAndPlatos(LayerGenerator):
    """ Mountings and wide slide spaces. """
    def __init__(self, face, top=5000, bottom=-5000, mounts=None):
        LayerGenerator.__init__(self, face)
        self.lowest = bottom
        self.highest = top
        self.extremums = mounts if mounts is not None else face
        self.earth_wide = 0.2

    def generate(self, tools):
        self.latest = [200 for i in range(0, self.size)]
        extremums = {tools.rand.randint(0, self.size): self.highest for _ in range(0, self.extremums)}
        waters = tools.rand.randint(0, 2)
        for _ in range(0, waters):
            deep = tools.rand.randint(0, self.size)
            extremums[deep] = extremums.get(deep, self.lowest)

        D = int(math.ceil(self.earth_wide * self.face))
        for i in range(0, self.size):
            # Water and mounting has a influence to very near cells
            if extremums.has_key(i):
                continue
            distances = {idCell: tools.dd(idCell, i) for idCell in extremums.iterkeys() if tools.dd(idCell, i) < D}
            if len(distances) == 0:
                continue

            # Influence of nearest
            ranges = distances.items()
            on = ranges.index(min(ranges))
            try:
                influencer = distances.keys()[on]
                d = distances[influencer]
                power = extremums[influencer]
            except Exception as e:
                print("Invalid index: {} on 'extremums'".format(influencer))
                continue
            height = int(math.ceil(tools.influenceOf(self.latest[i], power, d, D)))
            self.latest[i] = height

        self.extremums = self.extremums + waters
        return self.latest

    def updateCircle(self, tools):
        """ Erosion of mountings. """
        for i in range(0, self.size):
            current = self.latest[i]
            self.latest[i] = current if current <= 100 else current - 1
        self.latest = new
        return new

class Mountains(LayerGenerator):
    """ Generation a randomic lanscape by sinusoid noise. """

    octaves = [1, 2, 4, 8, 16, 32, 64, 128, 256]
    color_weigts = [0.1, 0.2, 0.2, 0.3] # white noise, red noise, pink noise, blue noise

    def __init__(self, face, top=5000, bottom=-5000):
        LayerGenerator.__init__(self, face)
        self.lowest = bottom
        self.highest = top

    def generate(self, tools):
        self.latest = []
        phase = None
        for i in range(0, self.face):
            pallette = []
            pallette.append(self.random_ift(Mountains.octaves, tools, self.size, phase, amplitudeFunc=lambda f: 1)) # white component
            pallette.append(self.random_ift(Mountains.octaves, tools, self.size, phase, amplitudeFunc=lambda f: 1/f/f)) # red component
            pallette.append(self.random_ift(Mountains.octaves, tools, self.size, phase, amplitudeFunc=lambda f: 1/f)) # pink component
            pallette.append(self.random_ift(Mountains.octaves, tools, self.size, phase, amplitudeFunc=lambda f: f)) # blue component


            wide = self.highest - self.lowest
            terrain = self.weighted_sum(Mountains.color_weigts, pallette)
            self.latest.extend([int(koef * wide) + self.lowest for koef in terrain])
            phase = terrain[1]

        # Smoothing a terrain
        extremums = {c: self.latest[c] for c in range(0, self.size) if self.latest[c] == self.highest or self.latest[c] == self.lowest}
        power = int(math.sqrt(self.face))
        for i in range(0, self.size):
            self.latest[i] = int(self.latest[i] + tools.average([tools.influenceOf(self.latest[i], extremums[c], tools.dd(i, c), longOfArms=power)])[0]) // 2
        return self.latest

    def random_ift(self, frequences, tools, length, phase=None, amplitudeFunc=lambda f: 1):
        """ Generate a noise with defined form (amplitudeFunc), length and frequences from declared phase-shift (phase). """
        amplitudes = [amplitudeFunc(f) for f in frequences]
        noises = [self.__noise(tools, f, length, phase) for f in frequences]
        return self.weighted_sum(amplitudes, noises, length)

    def weighted_sum(self, amplitudes, noises, length = None):
        """ Sum of noises with weigths (amplitudes/octaves) """
        if length is None:
            length = len(noises[0])
        output = [0.0] * length
        for k in range(0, len(noises)):
            for x in range(0, length):
                output[x] = output[x] + amplitudes[k] * noises[k][x]
        return output

    def __noise(self, tools, frequence, length, phase=None):
        """ Sinusoid as noise. """
        if phase is None:
            phase = tools.random.uniform(0, 2*math.pi)
        return [math.sin(2*math.pi*frequence*x / length + phase) for x in range(0, length)]

# Layer 0.5: Environments

class PlanetBurn(LayerGenerator):
    """ Make randomized environments for cells by heights """
    def __init__(self, face):
        """ Init a zonal distribution of environments and mapping Environments -> Landscapes. """
        LayerGenerator.__init__(self, face)
        self.zones = []
        self.zones.append({'min': -10000, 'max': -10, 'has': {Environments.Water: 1.1}})
        self.zones.append({'min': -10, 'max': 0, 'has': {Environments.Water: 0.3, Environments.Bridge: 0.8}})
        self.zones.append({'min': 0, 'max': 9, 'has': {Environments.Bridge: 0.6, Environments.Water: 0.1, Environments.Earth: 0.5}})
        self.zones.append({'min': 10, 'max': 99, 'has': {Environments.Bridge: 0.3, Environments.Earth: 0.6, Environments.Water: 0.3}})
        self.zones.append({'min': 100, 'max': 999, 'has': {Environments.Earth: 0.7, Environments.Water: 0.2, Environments.Bridge: 0.2, Environments.Port: 0.2}})
        self.zones.append({'min': 1000, 'max': 3499, 'has': {Environments.Earth: 0.8, Environments.Water: 0.3}})
        self.zones.append({'min': 3500, 'max': 7000, 'has': {Environments.Earth: 0.8, Environments.Air: 0.5}})
        #self.zones.append({'min': 7000, 'max': 12000, 'has': {Environments.Air: 1.1}})

    def generate(self, tools):
        heights = self.dependences[0].latest
        self.latest = [self.choiceEnv(tools, height) for height in heights]
        return self.latest

    def choiceEnv(self, tools, height):
        """ Choise environment by height's zones. """
        for zone in self.zones:
            if zone['min'] > height or zone['max'] < height:
                continue
            case = tools.rand.random()
            for envir in zone['has']:
                probability = zone['has'][envir]
                if case > probability:
                    case = case - probability
                    continue
                return envir
        return Environments.Air

    def updateCircle(self, tools):
        """ Waterized and drying of cells """
        heights = self.dependences[0].latest
        aqued = {Environments.Bridge, Environments.Port, Environments.Water}

        for i in range(0, self.size):
            envCurr = self.latest[i]
            heightCurr = heights[i]
            around = tools.getVecine(i)
            wtrs = 0
            for j in around:
                sphere = self.latest[j]
                if sphere in aqued:
                    wtrs = wtrs + 1
                if heights[j] >= heightCurr:
                    if sphere == Environments.Bridge or sphere == Environments.Port:
                        self.latest[i] = Environments.Bridge
                        continue
                    if sphere == Environments.Water:
                        self.latest[i] = sphere
                        continue
            if wtrs == 0 and envCurr in aqued:
                self.latest[i] = Environments.Earth
        return self.latest

# Layer 1: Terrain (wild? Wild!)

class SimpleLandGenerator(LayerGenerator):
    """ Random with age and height using. """
    def __init__(self, face, age):
        LayerGenerator.__init__(self, face)
        self.level = age

    def generate(self, tools):
        """
        Layer #1 - Landscape (textures, soils, land types)
        IN: float[] highmap - terrain
        OUT: id[] - id of landscape types
        """
        logging.debug("Stage Landscape layer")

        i = 0
        def highToLandscape(self, high):
            eps = 0.00001
            def selector(landing):
                soil = landing
                return soil['High'] - high > eps and high - soil['Low'] > eps and soil['Level'] <= self.level
            suitable = [landing['ID'] for landing in tools.scapes if selector(landing)]
            about = "  Available for height={}: {}".format(high, ", ".join(["{} ({})".format(tools.scapes[scape]['Name'], scape) for scape in suitable]))
            logging.debug(about)
            case = random.choice(suitable) if len(suitable) > 0 else 0
            return case
        self.latest = [highToLandscape(self, height) for height in self.dependences[0].latest]
        return self.latest

    def updateCircle(self, tools):
        """ Erosion and water moving """
        heights = self.dependences[0].latest
        humidity = (Environments.Water, Environments.Port)
        dry = (Environments.Earth, Environments.Air, Environments.Bridge)
        for idCell in range(0, self.size):
            height = heights[idCell]
            terrain = tools.scapes[self.latest[idCell]]
            vecine = tools.getVecine(idCell, conv=lambda no: (no, heights[no], tools.scapes[self.latest[no]]['ID'], tools.scapes[self.latest[no]]['Environment'], tools.scapes[self.latest[no]]['Civilization']))
            if terrain['Environment'] in humidity or terrain['Environment'] == Environments.Bridge:
                waters = [cell for cell in vecine if cell[3] in humidity]
                waterUnder=[item[2] for item in waters if item[1] > height and item[3] == Environments.Water]
                if len(waterUnder) > 1:
                    self.latest[idCell] = tools.rand.choice(waterUnder)
                    continue

                earth = [cell[2] for cell in vecine if cell[3] in dry and terrain['Civilization'] == cell[4]]
                if len(waters) == 0:
                    if len(earth) > 0 and terrain['Civilization']:
                        earth = tools.getAvailableID(cond=lambda transform: tools.homeable(transform['ID'], self.level))
                    if len(earth) == 0:
                        continue
                    self.latest[idCell] = tools.rand.choice(earth)
                    continue
            elif terrain['Environment'] == Environments.Earth:
                pass

        return self.latest

class ZonalLandscape(LayerGenerator):
    def __init__(self, face, landscapes):
        LayerGenerator.__init__(self, face)
        self.landscapes = landscapes
        self.zones = []
        self.zones.append({'min': -10000, 'max': -500, 'id': 0, 'available': [landscapes[land]["ID"] for land in landscapes if self.isOnZone(land, -10000, -500)]})
        self.zones.append({'min': -500, 'max': -0, 'id': 0, 'available': [landscapes[land]['ID'] for land in landscapes if self.isOnZone(land, -500, 0)]})
        self.zones.append({'min': 0, 'max': 499, 'id': 0, 'available': [landscapes[land]['ID'] for land in landscapes if self.isOnZone(land, 0, 500)]})
        self.zones.append({'min': 500, 'max': 999, 'id': 0, 'available': [landscapes[land]['ID'] for land in landscapes if self.isOnZone(land, 500, 1000)]})
        self.zones.append({'min': 1000, 'max': 1499, 'id': 0, 'available': [landscapes[land]['ID'] for land in landscapes if self.isOnZone(land, 1000, 1500)]})
        self.zones.append({'min': 1500, 'max': 2499, 'id': 0, 'available': [landscapes[land]['ID'] for land in landscapes if self.isOnZone(land, 1500, 2500)]})
        self.zones.append({'min': 2500, 'max': 5999, 'id': 0, 'available': [landscapes[land]['ID'] for land in landscapes if self.isOnZone(land, 2500, 6000)]})
        self.zones.append({'min': 6000, 'max': 10000, 'id': 0, 'available': [landscapes[land]['ID'] for land in landscapes if self.isOnZone(land, 6000, 10000)]})

    def generate(self, tools):
        """
        Layer #1 - Landscape (textures, soils, land types)
        IN: float[] highmap - terrain
        OUT: id[] - id of landscape types
        """
        logging.debug("Stage Landscape layer")

        self.case = random.Random()
        terrain = self.dependences[0].latest
        # Init a land types id for all zones
        for zone in self.zones:
            if len(zone['available']) == 0:
                continue
            zone['id'] = tools.rand.choice(zone['available'])
        # Wild
        self.latest = [self.setZone(height, tools) for height in terrain]
        return self.latest

    def updateCircle(self, tools):
        """ Rotation of zones. """
        return self.generate(tools)

    def isOnZone(self, name, mini, maxi, civy = False):
        landscape = self.landscapes[name]
        low = landscape['Low']
        high = landscape['High']
        return ((mini <= low and maxi >= low) or (high <= maxi and mini <= high)) and landscape['Civilization'] == civy

    def setZone(self, height, tools):
        zone = tools.rand.choice([zone for zone in self.zones if zone['min'] <= height and height <= zone['max']])
        return zone['id']

class ExtensibleAreas(ZonalLandscape):
    """ Big areas of united landscape. """
    def isOnZone(self, name, mini, maxi, civy = False):
        landscape = self.landscapes[name]
        low = landscape['Low']
        high = landscape['High']
        return ((mini <= low and maxi >= low) or (high <= maxi and mini <= high)) and landscape['Civilization'] == civy

    def generate(self, tools):
        """ Make a big eco-systems. """
        probability = float(0.5 / self.face)
        terrain = self.dependences[0].latest
        wild = [i for i in xrange(self.size)]
        self.latest = [-1 for _ in wild]
        while len(wild) > 0:
            # Init a land types id for all zones
            for zone in self.zones:
                if len(zone['available']) == 0:
                    continue
                zone['id'] = tools.rand.choice(zone['available'])
            # Update cells
            for cell in wild:
                if tools.rand.random() > 1.0 - probability:
                    self.latest[cell] = self.setZone(terrain[cell], tools)
                    wild.remove(cell)
        #self.output(os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'data', 'state', 'maps.open', 'wild.layer'))
        return self.latest

class PlanetEvo(LayerGenerator):
    """ Heights -> Environments -> Landscapes """
    def __init__(self, face, age, landscapes, envUpdateCircle=3):
        """ Init a zonal distribution of environments and mapping Environments -> Landscapes. """
        LayerGenerator.__init__(self, face)
        self.age = age
        # Frequency of modify a landscape & environment relations
        self.updateTime = envUpdateCircle
        # Landscapes for
        self.defines = [-1, -1, -1, -1, -1]
        r = random.Random()
        for envir, _ in enumerate(self.defines):
            available = [landscapes[name]['ID'] for name in landscapes if landscapes[name]['Environment'] == envir]
            if len(available) == 0:
                continue
            self.defines[envir] = r.choice(available)

    def generate(self, tools):
        """ Make a new terrain (map of landscape) """
        heights = self.dependences[0].latest
        self.spheres = self.dependences[1].latest

        self.latest = [-1 for _ in range(0, self.size)]
        undefined = [i for i in range(0, self.size)]
        timer = 0
        progress = 0
        counter = 1
        while len(undefined) > 0:
            upd = []
            for x in undefined:
                envir = self.spheres[x]
                scape = self.defines[envir]
                if self.adecvate(tools.scapes[scape], heights[x], envir):
                    self.latest[x] = scape
                    upd.append(x)
                    timer = timer + 1
                    if timer % self.updateTime:
                        self.updateDefines(envir, tools, heights[x])
                else:
                    self.updateDefines(envir, tools, heights[x])
            for x in upd:
                undefined.remove(x)

            curr = len(undefined)
            if progress == curr:
                counter = counter + 1
            else:
                counter = 0
            if counter == 3:
                raise LookupError("Iternal loop at {} cells (example {}: height {}, environment {})".format(curr, undefined[0], heights[undefined[0]], self.spheres[undefined[0]]))
            progress = curr
        return self.latest

    def updateCircle(self, tools):
        """ Update landscapes without modify environment. """
        heights = self.dependences[0].latest
        for envir in self.defines:
            self.updateDefines(envir)

        for no in range(0, self.size):
            envir = self.spheres[no]
            scape = self.defines[envir]
            case = self.choiceEnv(tools, heights[no])
            if self.adecvate(tools.scapes[scape], heights[x], envir) and envir == case:
                self.latest[x] = scape
        return self.latest

    # Tools
    def updateDefines(self, envir, tools, height):
        """ Choice a new landscape """
        available = [landscape for landscape in tools.scapes if self.adecvate(landscape, height, envir)]
        if len(available) == 0:
            self.defines[envir] = 0
            return
        self.defines[envir] = tools.rand.choice(available)["ID"]

    def adecvate(self, landscape, height, envir):
        """ This landscape is available for cell with this character """
        return landscape['Environment'] == envir and not landscape['Civilization']# and landscape['High'] >= height and landscape['Low'] <= height

# Layer 2: Capitals of regions

class ConstantableCapitals(LayerGenerator):
    """ Generator of capitals layer """
    def __init__(self, face, playerIDs, bases):
        LayerGenerator.__init__(self, face)
        self.playersIDs = playerIDs
        self.bases = bases

    def generate(self, tools):
        """
        Layer #2 - Castles (users bases, capitals of regions)
        IN: id[] landscape - id of landscape types
            float[] highmap - height of center of cell
            id[] playerIDs - id of Lords
        OUT: dict<cell.id, player.id> - id of player who have a castle in this cell or -1 (not-castle cell)
        """
        logging.debug("Stage Capitals layer")
        playersLimit = len(self.bases)
        self.players = min([playersLimit, len(self.playerIDs)])
        if self.players < 1:
            self.players = len(playerIDs)

        building = self.buildings[1]
        # Capitals of user manors
        def buider(no):
            return self.buildCastle(no, playerIDs.index(no), self.bases[no], landscape, highmap)
        castles = {self.bases[no]: buider(no) for no in playerIDs}
        self.domains = [self.domain(i + 1, self.bases[i], playerIDs[i]) for i in range(0, self.players)]

        # Free capitals of free regions
        amount = self.regions if self.regions != None else len(castles) + self.face + 1
        itercount = 0
        cap = len(castles) + 1
        while cap <= self.regions:
            placeId = self.rand.randint(0, self.size-1)
            # No reset exists capital
            if placeId in self.bases:
                logging.debug("  Cell {} is capital already".format(placeId))
                itercount = itercount + 1
                continue
            if castles.has_key(placeId):
                logging.debug("  Cell {} is capital already".format(placeId))
                itercount = itercount + 1
                continue

            # Variousity of capital building in this place. Time influences for it.
            remote = [ Tools.calcKoolonInfluence(1, 1, tools.dd(placeId, capitalId), koeff=3) for capitalId in castles]
            remoteness = min(remote)
            # Remoteness between already set castles
            trakes = [ tools.dd(capital1, capital2) for capital1 in castles for capital2 in castles if capital1 != capital2 ]
            relation = min(trakes)
            # Circle breaker
            timeCorrection = itercount / self.size
            # Building
            if relation - remoteness > timeCorrection:
                self.domains.append(self.domain(cap, placeId))
                castles[placeId] = cap
                landscape[placeId] = building
                cap = cap + 1
            itercount = itercount + 1

        self.latest = castles
        return castles

    def buildCastle(self, no, playerID, idCell, landscape, highs):
        if idCell < 0:
            return playerID
        scape = landscape[idCell]
        cell = self.scapes[scape]
        high = highs[idCell]
        fortifications = [build for build in self.buildings if self.constructable(high, build, cell)]
        building = self.rand.choice(fortifications) if len(fortifications) > 0 else self.buildings[0]
        landscape[idCell] = building
        raport = "{} ({}) is build at {}".format(self.scapes[building]['Name'], building, idCell)
        logging.debug(raport)
        return playerID

class SeparatedTribes(LayerGenerator):
    """
    Each dwelling - full-mate tribe and area center
    """

    def __init__(self, face, playerIDs, regionsCount = 0):
        LayerGenerator.__init__(self, face)
        self.playersIDs = playerIDs
        self.domains = []
        self.regions = regionsCount if regionsCount > 0 else self.face * 2

    def generate(self, tools):
        highmap = self.dependences[0].latest
        places = self.dependences[1].latest
        tribes = {}
        tribeNo = 1
        self.domains.append(tools.domain(0, -self.face, 0))
        self.domains.extend([tools.domain(noDom + 1, -1, idPlayer) for noDom, idPlayer in enumerate(self.playersIDs)])

        # Circle will not infinity loop
        leftToAdd = len(self.playersIDs)
        circles = 2 * self.size
        while leftToAdd > 0 and circles > 0:
            idCell = tools.rand.randint(0, self.size - 1)
            if tribes.get(idCell, -1) > 0:
                circles = circles - 1
                continue

            if tools.homeable(places[idCell]):
                tribes[idCell] = self.playersIDs[tribeNo] if tribeNo < len(self.playersIDs) else tribeNo
                if len(self.domains) > tribeNo:
                    self.domains[tribeNo]['capital'] = idCell
                else:
                    self.domains.append(tools.domain(tribeNo, idCell, tribeNo))
                tribeNo = tribeNo + 1
                leftToAdd = leftToAdd - 1
            circles = circles - 1
        if self.regions < tribeNo:
            self.latest = tribes
            print("Regions waited: {}, real: {}".format(self.regions, len(tribes)))
            return tribes

        # Very few?
        leftToAdd = self.regions - len(tribes)
        circles = self.size
        while leftToAdd > 0:
            circles = circles - 1
            if circles == 0:
                break
            idCell = tools.rand.randint(0, self.size - 1)
            if tribes.has_key(idCell):
                continue
            landscape = tools.scapes[places[idCell]]

            # Unbuildable place
            placeType = landscape['Environment']
            if placeType == Environments.Air or placeType == Environments.Water or placeType == Environments.Bridge:
                continue

            tribes[idCell] = self.playersIDs[tribeNo] if tribeNo < len(self.playersIDs) else tribeNo
            self.domains.append(tools.domain(tribeNo, idCell, 0))
            if not landscape['Civilization']:
                builds = [dwelling['ID'] for dwelling in tools.scapes if tools.canBuildAt(dwelling, highmap[idCell], tools.scapes[places[idCell]], 1)]
                self.dependences[1].latest[idCell] = tools.rand.choice(builds)

            tribeNo = tribeNo + 1
            leftToAdd = leftToAdd - 1
        self.latest = tribes
        return tribes

class SelfCapitalCell(LayerGenerator):
    def generate(self, tools):
        self.latest = {idCell+1: idCell+1 for idCell in xrange(self.size)}
        return self.latest

class SearchGoodPlaceToCapital(LayerGenerator):
    """docstring for SearchGoodPlaceToCapital."""
    def __init__(self, face, age, playerIDs, regions = None):
        LayerGenerator.__init__(self, face)
        self.playerIDs = playerIDs
        self.level = age
        self.regions = regions if regions != None else face

    def generate(self, tools):
        """
        Layer #2 - Castles (users bases, capitals of regions)
        IN: id[] landscape - id of landscape types
            float[] highmap - height of center of cell
            id[] playerIDs - id of Lords
        OUT: dict<cell.id, player.id> - id of player who have a castle in this cell or -1 (not-castle cell)
        """
        self.landscape = self.dependences[1].latest
        terrain = self.landscape
        highmap = self.dependences[0].latest
        self.buildings = [land['ID'] for land in tools.scapes if land['Civilization']]
        self.domains = []

        logging.debug("Stage Capitals layer")
        capitalLevelLimit = self.level + 1
        castles = {}

        # Critery of place to castle searching like a lord's logic
        def calcLovelyPlace(idLandscape, noCell, iterationNo):
            # Skip castled and
            if castles.has_key(noCell):
                return -1000
            land = tools.getLandscape(idLandscape)
            if land['Environment'] == Environments.Water or land['Environment'] == Environments.Air or land['Environment'] == Environments.Bridge:
                return -10000
            basis = int(land['Civilization'] * 1000)
            basis = basis + int(land['Fortifiedness'] * 100)
            basis = basis + int(land['YieldStart'] * 10)

            # Good castle is not near than another castles - near is danger, near is warrable
            already = len(castles)
            success = 0
            if already > 0:
                nearings = [tools.dd(noCell, idCell) for idCell in castles.keys()]
                nearest = min(nearings)
                # Then more and more amount of castles, then more and more important distantion between castles
                success = success + int((5 ** (already if already < 10 else 10)) * nearest)

            # Good vicine - good critery of searching
            about = tools.getVecine(noCell, lambda cellId: tools.getLandscape(terrain[cellId]))
            # Near water? Build port!
            portable = 4 > len([place['ID'] for place in about if place['Environment'] == Environments.Water]) > 0
            success = success + (100 if portable else 0)
            # Near bridge or port? Collect taxes from users!
            trollable = len([place['ID'] for place in about if place['Environment'] == Environments.Bridge or place['Environment'] == Environments.Port]) > 0
            success = success + (100 if trollable else 0)
            for landing in about:
                # Castle as center of civilization.
                success = success + (100 if landing['Civilization'] else 0) + int(landing['YieldStart'] * 10)
                # Castle more success if it builded on most defenced place.
                success = success + int(100 * (land['Fortifiedness'] - landing['Fortifiedness']))
            return basis + success + iterationNo

        cap = 1
        iterationNo = 1
        businessView = [1 for _ in range(0, self.size)]
        while len(self.domains) < self.regions:
            print("{}. Domains: {}/{}".format(iterationNo, len(self.domains), self.regions))
            if iterationNo > tools.size * 1.5:
                print("Times {}. Capital #{}. Regions: {}/{} Break a circle".format(iterationNo, cap, len(self.domains), self.regions))
                break
            businessView = [calcLovelyPlace(self.landscape[i], i, iterationNo) for i in range(0, self.size)]
            # Exclude a castles already
            for idCell in castles.keys():
                businessView[idCell] = -100
            extremums = sorted([i for i in range(0, self.size - 1) if businessView[i] > 0], key=lambda cell: businessView[cell])
            if len(extremums) == 0:
                iterationNo = iterationNo + 1
                continue
            areNext = extremums[-1]
            #if (cap > 3):
                #pdb.set_trace()

            def landByID(idCell):
                try:
                    cell = terrain[idCell]
                except Exception as e:
                    print("Index is invalid", idCell, len(terrain))
                    return tools.getLandscape(0)
                return tools.getLandscape(cell)

            # Get logically cases of buildings
            def buildingsFilter(idLand):
                land = tools.getLandscape(idLand)
                if land['Environment'] == 2:
                    return false
                high = highmap[areNext]
                about = tools.getVecine(areNext, landByID)
                onShore = len([scape['ID'] for scape in about if scape['Environment'] == 1]) > 0
                port = onShore and land['Environment'] == 4
                onHeight = land['High'] - high > 0.0 and high - land['Low'] > 0.0
                return (port or not port) and land['Level'] <= capitalLevelLimit and onHeight

            # Available types of building in referense to environment's cells
            availableBuildings = [idLand for idLand in self.buildings if buildingsFilter(idLand)]
            building = random.choice(availableBuildings)

            # Add castle
            self.domains.append(Tools.domain(tools, cap, areNext))
            castles[areNext] = cap
            self.dependences[1].latest[areNext] = building
            cap = cap + 1
            iterationNo = iterationNo + 1
        self.latest = castles
        return castles

class DistancedCapitals(LayerGenerator):
    """ Distance a capitals as long as possible with random. """
    def __init__(self, face, playerIDs, regionsCount = 0):
        LayerGenerator.__init__(self, face)
        self.playersIDs = playerIDs
        self.domains = []
        self.regions = regionsCount if regionsCount > 0 else self.face * 2

    def generate(self, tools):
        landscape = self.dependences[1].latest
        left = self.regions
        circles = self.size
        self.latest = {}
        critical = self.face // left
        fine = [Environments.Port, Environments.Earth]
        self.domains.append(tools.domain(0, self.size*2, 0))

        settableMap = [idCell for idCell in range(0, self.size) if tools.scapes[landscape[idCell]]['Environment'] in fine]

        def addCapital(idCell, left):
            no = len(self.domains)
            settableMap.remove(idCell)
            self.latest[idCell] = no
            self.domains.append(tools.domain(no, idCell, self.playersIDs[no-1] if no <= len(self.playersIDs) else 0))
            # A capital places is more and more close for each time
            critical = self.face // (2 * self.regions - left)
            return left - 1

        while left > 0 and circles > 0:
            circles = circles - 1
            if len(settableMap) == 0:
                break
            idCell = tools.rand.choice(settableMap)
            if self.latest.has_key(idCell):
                continue
            # First capital?
            try:
                landTypeID = landscape[idCell]
            except Exception as e:
                print("Invalid index {}/{}".format(idCell, len(landscape)))
                raise
            if len(self.latest) == 0:
                left = addCapital(idCell, left)
                circles = circles - 1
                continue
            # Each other caitals
            neary = min([tools.dd(idCell, idPlace) for idPlace in self.latest.keys()])
            if neary >= critical:
                left = addCapital(idCell, left)
            circles = circles - 1
        return self.latest

class HiddenStrongholds(LayerGenerator):
    """ Fantasy placement for cities and castles, inspired by J. R. R. Tolkien """
    def __init__(self, face, playerIDs, regionsCount = 0):
        LayerGenerator.__init__(self, face)
        self.playersIDs = playerIDs
        self.domains = []
        self.regions = regionsCount if regionsCount > 0 else self.face * 2
        print("... ... Region await: {}".format(self.regions))

    def generate(self, tools):
        landscape = self.dependences[1].latest

        def calcHiddenFirst(no):
            like = landscape[no]
            if tools.scapes[like]['Environment'] in (Environments.Water, Environments.Air):
                return 0
            around = tools.getVecine(no, conv=lambda x: landscape[x])
            return len([cell for cell in around if cell == like])
        def recalculateHidden(cell):
            like = landscape[cell]
            around = tools.getVecine(cell)
            likely = [no for no in around if landscape[no] == like]
            bonus = sum([hidy[no] for no in likely if hidy[no] < hidy[cell]])
            return bonus + len(likely)
        # Calc points of cells hidden
        hidy = [calcHiddenFirst(no) for no in range(0, self.size)]
        hidy = [tuple((no, recalculateHidden(no))) for no in range(0, self.size)]
        hidy.sort(key=itemgetter(1), reverse=True)
        # Make potantial cities dictionary
        strongholds = [place[0] for place in hidy[0:self.regions*2]]
        castles = {strongholds[i]: i+1 for i in range(0, self.regions*2)}
        # Extract distanced cells
        cells = castles.keys()
        self.latest = {}
        added = []
        D = 2
        ticks = 0
        while len(self.latest) < self.regions:
            for no in range(0, len(cells)):
                noCell = cells[no]
                if len(added) == 0:
                    added.append(noCell)
                    self.latest[noCell] = len(self.latest) + 1
                    continue
                if self.latest.has_key(noCell):
                    continue
                distances = [tools.dd(noCell, x) for x in added]
                if len(distances) == 0:
                    self.latest[noCell] = len(self.latest) + 1
                    added.append(noCell)
                    continue
                if min(distances) < D:
                    continue
                self.latest[noCell] = len(self.latest) + 1
                added.append(noCell)
            cells = [cell for cell in cells if not self.latest.has_key(cell)]
            ticks = ticks + 1
            if ticks > self.regions:
                D = 1
        return self.latest

# Layer 3: Populations

class EvolutionRandomHomo(LayerGenerator):
    """ Generator of population. Random choice of place while globalPopulation > 0 """
    def __init__(self, face, globalPopulation = 100000):
        LayerGenerator.__init__(self, face)
        self.oikumenaPopulation = globalPopulation

    def generate(self, tools):
        landscape = self.dependences[1].latest
        scapes = self.dependences[1].landing
        logging.debug("Stage Population level")
        toSet = math.ceil(self.oikumenaPopulation / self.size)
        case = random.Random()

        population = [0 for _ in xrange(self.size)]

        circles = 2 * self.size
        while self.oikumenaPopulation > 0 and circles > 0:
            toSet = min((self.oikumenaPopulation, toSet))
            noCell = case.randint(0, self.size - 1)
            place = scapes[landscape[noCell]]
            settlers = min((max(place.get('Hobbitable', 0) - population[noCell], 0), toSet))
            if settlers > 0:
                population[noCell] = population[noCell] + settlers
                self.oikumenaPopulation = self.oikumenaPopulation - settlers
            circles = circles - 1
        self.latest = population
        return population

class BurnInHomes(LayerGenerator):
    """ Generator of population. Random dwells growing """
    def __init__(self, face, globalPopulation = 10000):
        LayerGenerator.__init__(self, face)
        self.oikumenaPopulation = globalPopulation
        self.burnAtCircle = 10
        self.selector = lambda idCell, tools, landscape: tools.homeable(landscape[idCell])
        self.mainLayer = 0

    def generate(self, tools):
        self.landscape = self.dependences[self.mainLayer].latest
        self.latest = [0 for _ in range(0, self.size)]
        dwellings = {idCell: 10 for idCell in range(0, self.size) if self.selector(idCell, tools, self.landscape) }
        self.oikumenaPopulation = self.oikumenaPopulation - self.burnAtCircle * len(dwellings)
        # Limit of how many can be set (Capacity, how many can be fed is Hobbitable) on each cell
        limits = [tools.getCapacity(self.landscape[i] if type(self.landscape) is list else self.landscape.get(i, -1)) for i in range(0, self.size)]

        circles = 5 * self.size
        while self.oikumenaPopulation > 0:
            if len(dwellings) == 0:
                break
            place = tools.rand.choice(dwellings.keys())
            already = dwellings[place]
            burn = min([self.burnAtCircle, max([limits[place] - already, 0]), self.oikumenaPopulation])
            already = already + burn
            dwellings[place] = already
            self.latest[place] = already
            self.oikumenaPopulation = self.oikumenaPopulation - burn
            circles = circles - 1
            if circles == 0:
                dwellings = [dwellID for dwellID in dwellings if limits[dwellID] - self.latest[dwellID] > 0]
                if len(dwellings) > 0:
                    dwellID = tools.rand.choice(dwellings)
                    left = limits[dwellID] - self.latest[dwellID]
                    self.latest[dwellID] = limits[dwellID]
                    self.oikumenaPopulation = 0
        return self.latest

class StateCities(BurnInHomes):
    """ Population growns on capitals only. """
    def __init__(self, face, globalPopulation = 10000):
        BurnInHomes.__init__(self, face, globalPopulation)
        self.mainLayer = 1
        self.selector = lambda idCell, tools, landscape: landscape.get(idCell, 0) > 0

class CommonSenseDwellinger(LayerGenerator):
    def __init__(self, face, globalPopulation = 100000):
        LayerGenerator.__init__(self, face)
        self.oikumenaPopulation = globalPopulation

    def generate(self, tools):
        landscape = self.dependences[0].latest

        logging.debug("Stage Population layer")
        def isCastle(landscape):
            cell = tools.scapes[landscape]
            return cell['Civilization'] or (cell['Fortifiedness'] > 0.1)
        culture = [c for c in landscape if isCastle(c)]
        def calcPoputation(self, idScape, idCell):
            cell = tools.scapes[landscape[idScape]]
            peasantLimit = cell.get('Hobbitable', 0)
            if peasantLimit < 1:
                return 0
            if not cell.get('Civilization', False):
                return tools.rand.randint(0, int(0.01 * peasantLimit))
            # Near of dwellings and capacity of cell
            near = min([tools.dd(idCell, place) for place in culture])
            populoK = 0.25/(1 + near) + 0.15*peasantLimit/self.oikumenaPopulation
            # Rich and security
            populoK = populoK + 0.25*cell.get('Fortifiedness', 0.0) + 0.35*cell.get('YieldStart', 0.0)
            # Calc a population of cell
            return min([int(self.oikumenaPopulation * populoK / self.size), peasantLimit])

        self.latest = [calcPoputation(self, landscape[i], i) for i in xrange(len(landscape))]
        return self.latest


# Layer 4: Armies and forces

class LordCourt(LayerGenerator):
    """ Armies in capitals. """
    def generate(self, tools):
        populationMap = self.dependences[1].latest
        cells = self.dependences[0].latest
        capitals = self.dependences[2].latest

        logging.debug("Stage Force's layer")
        self.latest = [self.calcForce(tools, population, icell, capitals) for icell, population in enumerate(populationMap)]
        return self.latest

    def calcForce(self, tools, population, cell, capitals):
        return tools.rand.randint(0, int(0.5*population)) if capitals.has_key(cell) else 0

class AggressiveTribes(LayerGenerator):
    """ Part of all mans will be soldiers. """

    def generate(self, tools):
        populationMap = self.dependences[1].latest

        logging.debug("Stage Force's layer")
        self.latest = [tools.rand.randint(0, int(population / 2)) for population in populationMap]
        return self.latest

class Guards(LayerGenerator):
    """ Soldiers has count in capitals and in distanced cells. """

    min_propbability = 0.02

    def generate(self, tools):
        landscape = self.dependences[0].latest
        population = self.dependences[1].latest
        capitals = self.dependences[2].latest

        ungrounded = [Environments.Air, Environments.Water]

        def awaitGuard(idCell):
            """ Get demand for soldiers. """
            if capitals.has_key(idCell):
                return 0.75
            capitalsList = capitals.keys()
            distances = [tools.dd(idCell, idCapital) for idCapital in capitalsList]
            near = min(distances)
            if near > self.face / 2:
                return Guards.min_propbability
            no = distances.index(near)
            idNearCapital = capitalsList[no]
            regionaly = 0.25 if landscape[idNearCapital] == landscape[idCell] else 0.0
            counter = Counter(distances)
            crossOf = counter[near]
            if crossOf > 1:
                return min([1.0 - (1.0 / (crossOf + 1)) + regionaly, 0.95])
            return Guards.min_propbability if tools.scapes[landscape[idCell]]['Environment'] not in ungrounded else - 0.1
        def recruitGuard(idCell, awaiting):
            u""" Recruit harrison proportianally for soldier's demand. """
            man = population[idCell]
            chance = tools.rand.random() < awaiting
            return int(man * awaiting) if man > 0 else (int(tools.rand.randint(0, 100) * awaiting) if chance else 0)

        self.latest = [recruitGuard(idCell, awaitGuard(idCell)) for idCell in range(0, self.size)]
        return self.latest

# Layer 5: Regions and domains (burn-time sizes).

class SeparatedCells(LayerGenerator):
    def generate(self, tools):
        allPlayers = len(self.players)
        self.latest = [idCell+1 for idCell in xrange(len(landscape))]
        self.domains= [Tools.domain(idDomain, idDomain, idDomain - 1 if idDomain < self.players else 0) for idDomain in self.latest]
        return self.latest

class GravityOfCitiesPrehistory(LayerGenerator):
    """Generator of political (domains) layer. Insettling a humanless land."""
    def __init__(self, face):
        LayerGenerator.__init__(self, face)

    def generate(self, tools):
        """
        Layer #5 - Domains (regions, countries, manors)
        IN: int[] peasants - population of cells,
            int[] armies - forces of cells,
            dict<cell.id, player.id> castles - capitals of regions
            id[] landscape - list of id of landcape in cells
        OUT: id[] - identifiers of cell's domain
        """
        # Collect a macro domains
        castles = self.dependences[1].latest
        capitals = [cell for cell in castles.keys() if cell > -1]
        peasants = self.dependences[3].latest
        self.domains = []
        dd = tools.dd

        def relation(idCell, idCapital):
            return tools.calcKoolonInfluence(1, 1, dd(idCell, idCapital))

        def setDomain(idCell):
            nearing = [relation(idCell, capitalId) for capitalId in capitals]
            nearestNo = nearing.index(max(nearing))
            idDomain = castles[capitals[nearestNo]]
            return idDomain

        domainsMap = [setDomain(i) for i in xrange(len(peasants))]
        self.latest = domainsMap
        return self.latest

class LazyDevelopment(LayerGenerator):
    def __init__(self, face):
        LayerGenerator.__init__(self, face)

    def generate(self, tools):
        """ Collect regios from more hobbitable cells to less hobbitable (resettlement). """
        castles = self.dependences[1].latest
        peasants = self.dependences[3].latest
        domainsList = [tools.domain(0, -15, 0)]
        for castle in castles:
            domainsList.append(tools.domain(castles[castle], castle, 0))
        domainsMap = [castles.get(i, 0) for i in xrange(self.size)]

        # Sort by descending a population
        spreadingCenters = sorted([idCell for idCell in xrange(self.size)], key=lambda noCell: -peasants[noCell])
        for idCell in spreadingCenters:
            idDomain = domainsMap[idCell]
            if idDomain == 0:
                idDomain = castles.get(idCell, 0)
            # Create new region with center in current cell
            if idDomain == 0:
                domain = tools.domain(len(domainsList), idCell, 0)
                domainsList.append(domain)
                idDomain = domain['id']
                domainsMap[idCell] = idDomain
            # Development nearest cells
            conquestions = [ cell for cell in tools.getVecine(idCell) if domainsMap[cell] == 0 or peasants[cell] < peasants[idCell] ]
            for target in conquestions:
                domainsMap[target] = idDomain
        self.domains = domainsList
        self.latest = domainsMap
        return domainsMap

class InfinityAbsorbation(LayerGenerator):
    """
    All cell-domains can absorbes and append a near cell with one probability.
    This process do while domains count more than ordered by creator.
    """
    def __init__(self, face, playersIDs, regionsCount = None):
        LayerGenerator.__init__(self, face)
        self.regionsCount = regionsCount if regionsCount is not None else face
        self.players = playersIDs

    def generate(self, tools):
        """  Simulation of wars and absorbation a most weak regions before game started. """
        domainsMap = [0 for _ in range(0, self.size)]
        castles = self.dependences[1].latest
        armies = self.dependences[2].latest
        peasants = self.dependences[3].latest

        # Fix a capitals of domains
        dices = random.Random()
        absorbing = castles.keys()
        domains = []
        mask = (-self.face, -1, 1, self.face)

        # What a domain will absorbed it's neibour cell?
        def chooseWinner(idCell1, idCell2):
            chanceFirst = dices.random() * (armies[idCell1] - armies[idCell2])
            chanceSecond = dices.random() * (armies[idCell2] - armies[idCell1])
            if chanceFirst == chanceSecond:
                return idCell1  if dices.random() > dices.random() else idCell2
            return idCell1 if chanceFirst >= chanceSecond else idCell2

        def absorbation(idCell1, idCell2):
            capturer = chooseWinner(idCell1, idCell2)
            looser = idCell2 if capturer == idCell1 else idCell1
            domainsMap[looser] = domainsMap[capturer]
            if castles.has_key(looser):
                castles.pop(looser)

        # Absorbation of cells process:
        self.times = 0
        while len(absorbing) > self.regionsCount:
            idCell = dices.choice(absorbing)
            idNearbor = dices.choice(tools.getVecine(idCell))
            if domainsMap[idCell] == domainsMap[idNearbor]:
                continue
            absorbation(idCell, idNearbor)
            absorbing.remove(idCell)
            self.times = self.times + 1

        # Create domains by left capitals
        newId = 1
        replaces = {}
        for capital in castles.keys():
            domains.append(tools.domain(newId, capital, newId if newId > len(self.players) else 0))
            replaces[capital] = newId
            newId = newId + 1
        for i in xrange(len(domainsMap)):
            oldId = domainsMap[i]
            if not replaces.has_key(oldId):
                oldId = domainsMap[domainsMap[oldId]]
            newId = replaces[oldId]
            domainsMap[i] = newId

        self.domains = domains
        self.latest = domainsMap
        return domainsMap

class BigUnknownWorld(LayerGenerator):
    """ Step-by-step accumulate a cells in domains. Result map can contains a 'free' cells. """
    def __init__(self, face):
        LayerGenerator.__init__(self, face)

    def generate(self, tools):
        """ Random-size and random-choice circle for capitals and not. """
        capitals = self.dependences[1].latest

        self.domains = [tools.domain(1, idCell, idDomain) for idCell, idDomain in capitals.iteritems()]
        for i in range(1, len(self.domains)):
            self.domains[i]['id'] = i
        political = [capitals.get(i, 0) for i in xrange(self.size)]

        circles = tools.rand.randint(self.face, self.size) * tools.rand.randint(1, self.face)
        bridgeheads = [i for i in xrange(self.size) if political[i] > 0 and len([cell for cell in tools.getVecine(i) if political[cell] == 0]) > 0]
        while circles > 0 and len(bridgeheads) < self.size:
            """ Random circle by cell in domain's borders. """
            bridgehead = tools.rand.choice(bridgeheads)
            around = tools.getVecine(bridgehead)
            exploringCell = tools.rand.choice(around)
            # Is it real unknown before cell?
            if political[exploringCell] == 0:
                political[exploringCell] = political[bridgehead]
                # Update of border cells list.
                bridgeheads.append(exploringCell)

            circles = circles - 1
        self.latest = political
        return political

class SpeciesArials(LayerGenerator):
    """ 'Elves' into forests, 'gnomes' into holes... """
    def __init__(self, face):
        LayerGenerator.__init__(self, face)

    def generate(self, tools):
        landscape = self.dependences[0].latest
        capitals = self.dependences[1].latest
        heights = self.dependences[4].latest

        capitalsList = capitals.keys()
        areals = {capitals[capitalId]: landscape[capitalId] for capitalId in capitalsList}
        self.domains = [tools.domain(i, capitalsList[i], i) for i in range(1, len(capitals))]
        self.latest = [capitals.get(i, 0) for i in range(0, self.size)]
        included = len(capitals)
        undomened = [i for i in range(0, self.size) if self.latest[i] == 0]
        while included > 0:
            included = 0
            for cell in undomened:
                around = tools.getVecine(cell)
                accumulaters = [idCell for idCell in around if self.latest[idCell] > 0 and (landscape[idCell] == self.latest[cell] or tools.rand.randint(0, abs(heights[idCell])) > abs(heights[idCell] - heights[cell]))]
                if len(accumulaters) == 0:
                    continue
                idConquier = tools.rand.choice(accumulaters)
                self.latest[cell] = self.latest[idConquier]
                included = included + 1
            undomened = [cell for cell in undomened if self.latest[cell] == 0]
        return self.latest

class NearestVecine(LayerGenerator):
    """ Domains is quadro about of capital. """
    def __init__(self, face):
        LayerGenerator.__init__(self, face)
        self.quadro = [-1, -1-face, -face, -face+1, +1, +1+face, +face, face-1]

    def generate(self, tools):
        capitals = self.dependences[1].latest
        self.latest = [0 for _ in range(0, self.size)]

        for cell, noDomain in capitals.iteritems():
            self.latest[cell] = noDomain
            around = [sh + cell for sh in self.quadro if tools.dd(sh+cell, cell) <= 2 and sh+cell > -1 and sh+cell < self.size]
            for i in around:
                self.latest[i] = noDomain
        return self.latest

# Layer 6: History of worldbox (map) before a start of game.

class NoDomainHistory(LayerGenerator):
    def generate(self, tools = None):
        """
        Layer #5 - Domains (regions, countries, manors)
        IN: int[] peasants - population of cells,
            int[] armies - forces of cells,
            dict<cell.id, player.id> castles - capitals of regions
            id[] landscape - list of id of landcape in cells
        OUT: id[] - identifiers of cell's domain
        """
        self.latest = self.dependences[0].latest
        self.domains = self.dependences[0].domains
        return self.latest

class IntegrationRegions(LayerGenerator):
    def __init__(self, face):
        LayerGenerator.__init__(self, face)

    def generate(self, tools):
        domainsMap = self.dependences[0].latest
        domainsList = self.dependences[0].domains
        castles = self.dependences[0].dependences[1].latest
        armies = self.dependences[1].latest
        peasants = self.dependences[2].latest

        greatCapitals = castles.keys()
        collectors = {}
        fullplace = []
        for castleCell in greatCapitals:
            idDomain = domainsMap[castleCell]
            domainsList[idDomain]['capital'] = castleCell
            collectors[idDomain] = 0
            fullplace.append(domainsList[idDomain])

        # What a cells we will integrate?
        def toAbsorb(idCell):
            idNativeDomain = domainsMap[idCell]
            return not collectors.has_key(idNativeDomain)

        # Sort by ascending a population
        absorbing = sorted([idCell for idCell in xrange(self.size) if toAbsorb(idCell)], key=lambda idCell: peasants[idCell])

        def integrater(idDom):
            return collectors.has_key(idDom)

        # Absorbation of "ownerless" cells:
        self.times = 0
        while len(absorbing) > 0:
            absorbed = 0
            canceled = 0
            for idCell in absorbing:
                # Who will left they not will captured
                idNativeDomain = domainsMap[idCell]
                if integrater(idNativeDomain) or castles.has_key(idCell):
                    absorbing.remove(idCell)
                    continue

                # Who will capture this cell?
                nearbores = self.getVecine(idCell, conv=lambda cell: domainsMap[cell])
                foes = [idDomain for idDomain in nearbores if idDomain != idNativeDomain]
                secure = len(foes) == 0
                # Cell has not agressive neibors who can capture it.
                if (secure):
                    message = "Cell #{} is not has danger".format(idCell)
                    logging.debug(message)
                    continue
                # A great lords/regions has a advantage on integration process
                mostAgressive = [idDomain for idDomain in nearbores if integrater(idDomain)]
                if len(mostAgressive) > 0:
                    idCapturer = random.choice(mostAgressive)
                else:
                    idCapturer = random.choice(foes)
                if idCapturer == None:
                    message = "Cell #{} is not has danger: balance".format(idCell)
                    logging.debug(message)
                    continue

                if not collectors.has_key(idCapturer):
                    canceled = canceled + 1
                    continue
                absorbed = absorbed + 1
                domainsMap[idCell] = idCapturer
                absorbing.remove(idCell)
                collectors[idCapturer] = collectors.get(idCapturer, 0) + 1
            self.times = self.times + 1

        # Renumeration of domains
        newId = 1
        replaces = {}
        for domain in fullplace:
            oldId = domain['id']
            replaces[oldId] = newId
            fullplace[newId - 1]['id'] = newId
            newId = newId + 1
        for i in xrange(len(domainsMap)):
            oldId = domainsMap[i]
            newId = replaces[oldId]
            domainsMap[i] = newId
        self.domains = fullplace
        self.latest = domainsMap
        return domainsMap

# Layer 7: Hats and Palaces (terraformation by civilizations)

class NoBuildingsBefore(LayerGenerator):
    """
    Only natural terraformation (erosion by wind and water).
    What about move erosion/weather to separate layer between layer #2 and layer #3?
    """

    def __init__(self, face, age = Age.Neolit):
        LayerGenerator.__init__(self, face)
        self.age = Age.Neolit

    def generate(self, tools):
        return self.dependences[0].latest

class DwellyCaves(LayerGenerator):
    """
    Whole civilizations is living caves and camps of nomads.
    """

    def __init__(self, face, age = Age.Neolit):
        LayerGenerator.__init__(self, face)
        self.age = Age.Neolit

    def generate(self, tools):
        wild = self.dependences[0].latest
        population = self.dependences[1].latest
        armies = self.dependences[2].latest
        heights = self.dependences[3].latest
        domains = self.dependences[4].latest

        dwellTypes = [dwellsType for dwellsType in tools.scapes if tools.homeable(dwellsType['ID'], Age.Neolit)]
        buildings = {idCell: wild[idCell] for idCell in range(0, self.size) if tools.scapes[wild[idCell]]['Civilization'] or population[idCell] > 0 or armies[idCell] > 0}
        for idCell in buildings:
            place = wild[idCell]
            canWill = self.selectDwellingType(tools, dwellTypes, heights[idCell], tools.scapes[place])
            if len(canWill) == 0:
                continue
            buildings[idCell] = tools.rand.choice(canWill)

        self.latest = [buildings.get(i, wild[i]) for i in range(0, self.size)]
        return self.latest

    def selectDwellingType(self, tools, allDwellTypes, height, placeType, peasants = 0, warriors = 0):
        return [terraformation['ID'] for terraformation in allDwellTypes if tools.canBuildAt(terraformation, height, placeType, self.age)]

class WarAndPease(DwellyCaves):
    """ Build a fort if soldiers more than civils. And peasefull settling else. """
    def __init__(self, face, age = Age.Neolit):
        LayerGenerator.__init__(self, face)
        self.age = age

    def selectDwellingType(self, tools, allDwellTypes, height, placeType, peasants = 0, warriors = 0):
        orient = [Orientation.Tax, Orientation.Food, Orientation.Source, Orientation.Progress] if peasants > warriors else [Orientation.Weapon, Orientation.Recruit]
        return [terraformation['ID'] for terraformation in allDwellTypes if tools.canBuildAt(terraformation, height, placeType, self.age) and terraformation['Orient'] in orient]

class DefenceOfBorders(LayerGenerator):
    """
    Near of domain border build a castles and fortes, in the deep of domain build a civil dwellings.
    """
    def generate(self, tools):
        wild = self.dependences[0].latest
        population = self.dependences[1].latest
        armies = self.dependences[2].latest
        heights = self.dependences[3].latest
        domains = self.dependences[4].latest

        dwellTypes = [dwellsType for dwellsType in tools.scapes if tools.homeable(dwellsType['ID'], Age.Neolit)]
        buildings = {idCell: wild[idCell] for isCell in range(0, self.size) if population[idCell] > 0 or armies[idCell] > 0}
        for idCell in buildings:
            aroundLands = tools.getVecine(idCell, conv=lambda idPlace: domains[idPlace])
            canWill = self.selectDwellingType(tools, dwellTypes, domains[idCell], aroundLands, heights[idCell], wild[idCell])
            if len(canWill) == 0:
                continue
            buildings[idCell] = tools.rand.choice(canWill)

        self.latest = [buildings.get(i, wild[i]) for i in range(0, self.size)]
        return self.latest

    def selectDwellingType(self, tools, allDwellTypes, ownersDomain, around, height, landscape):
        onBorder = len([region for region in around if region != ownersDomain]) > 0
        orient = [Orientation.Tax, Orientation.Food, Orientation.Source, Orientation.Progress] if not onBorder else [Orientation.Weapon, Orientation.Recruit]
        return [terraformation['ID'] for terraformation in allDwellTypes if tools.canBuildAt(terraformation, height, landscape, self.age) and terraformation['Orient'] in orient]

class FamilyCastles(LayerGenerator):
    """ Set castle in capital """
    def __init__(self, face):
        LayerGenerator.__init__(self, face)

    def generate(self, tools):
        capitals = self.dependences[5].latest
        landscape = self.dependences[0].latest
        self.latest = [landscape[i] for i in range(0, self.size)]

        dwells = [holder['ID'] for holder in tools.scapes if holder['Civilization'] and holder['Fortifiedness'] > 0.0]
        dwells.sort(key=lambda no: tools.scapes[no]['Capacity'])
        dwell = dwells[0]

        for cell in capitals:
            self.latest[cell] = dwell
        return self.latest

# Layer 8: Roads and commerce

class Crossroads(LayerGenerator):
    """ Mark a castles and cells by Roads """
    def __init__(self, face):
        LayerGenerator.__init__(self, face)
        self.D = face // 2 + 1
        self.disable = {Environments.Air, Environments.Water}
        self.fairs = [] # Fairs - most commerce-effective cells

    CAPITAL = 10

    def generate(self, tools):
        capitals = self.dependences[0].latest   # Capitals of domains
        placements = self.dependences[1].latest # Landscape

        self.latest = [self.calcCommerceLev(i, tools, capitals, placements) for i in range(0, self.size)]
        return self.latest

    def calcCommerceLev(self, idCell, tools, capitals, placements):
        """ Get level of commerce effective """
        if capitals.has_key(idCell):
            return Crossroads.CAPITAL
        if tools.scapes[placements[idCell]]['Environment'] in self.disable:
            return 0
        capitalsList = capitals.keys()
        distances = [tools.dd(idCell, idCapital) for idCapital in capitalsList]
        near = min(distances)
        if near >= self.D:
            return 0
        no = distances.index(near)
        idNearCapital = capitalsList[no]
        noNearCapital = capitalsList.index(idNearCapital)
        counter = Counter(distances)
        crossOf = counter[near]
        if crossOf > 1:
            self.fairs.append(idCell)
            return crossOf + self.D // (self.D - near) if tools.rand.random() > 0.5 else 0
        return 0

# Layer 9: Welfare of people

# Layer 10: Treasures and founds

# Layer 11: Control over the land and armies

class InTheNameOfLord(LayerGenerator):
    """ Absolutly loyality """

    def generate(self, tools):
        domains = self.dependences[2].latest # Map of domains
        if len(domains) == 0:
            domains = self.dependences[2].dependences[0].latest
        self.latest = [domains[x] for x in range(0, self.size)]
        return self.latest

class BanditsAtBorderlands(LayerGenerator):
    """ Then more far, then less loyality and more bandity. """

    def generate(self, tools):
        """ Make a Army.Owner map """
        lords = self.dependences[0].latest # Castles, capitals of players
        forces = self.dependences[1].latest # Armies soldier count
        domains = self.dependences[2].latest # Map of domains
        if len(domains) == 0:
            domains = self.dependences[2].dependences[0].latest
        self.latest = [domains[x] for x in range(0, self.size)]
        capitals = {idCell: idDomain for idDomain, idCell in lords.iteritems()}
        runInDistance = int(math.ceil(math.sqrt(self.face)))

        def calcLoyality(idCell):
            noDomain = domains[idCell]
            if noDomain == 0:
                return 0
            center = capitals.get(noDomain, self.size * 2)
            if center == idCell:
                return 1.0
            d = tools.dd(idCell, center)
            return float(runInDistance) / d if d > runInDistance else 1.0

        def changeLoyality(idCell):
            return 0

        for x in range(0, self.size):
            loyality = calcLoyality(x)
            betrayal = tools.rand.random()
            if betrayal > loyality:
                #print("Cell loyality {}, chance of betrayal {} is shotted.".format(loyality, betrayal))
                self.latest[x] = changeLoyality(x)
        return self.latest

# Layer 12: Marks on the map

# TODO Include little regions into big regions.
class UnifiedNatureRegions(LayerGenerator):
    """ Make name of region by nearest orientier name. """
    def __init__(self, face, table):
        LayerGenerator.__init__(self, face)
        self.marks = ['']
        self.table = table

    def generate(self, tools):
        heights = self.dependences[0].latest
        top = max(heights)
        bottom = min(heights)
        landscapes = self.dependences[1].latest
        spheres = [tools.scapes[no]['Environment'] for no in landscapes]
        orientiers = {noCell: ('Mountains' if heights[noCell] > bottom else 'Deeps') for noCell in range(0, self.size) if heights[noCell] == top or heights[noCell] == bottom}
        self.latest = [0 for _ in landscapes]

        regions = [0]
        # Stage 1: naming of orientiers, create centers of big regions
        for noCell in orientiers:
            category = orientiers[noCell]
            if len(self.table[category]) > 0:
                name = tools.rand.choice(self.table[category])
                self.table[category].remove(name)
                noRegion = len(self.marks)
            else:
                continue
            orientiers[noCell] = noRegion
            self.marks.append(name)
            self.latest[noCell] = noRegion
            regions.append(noRegion)
        orientiers = {noCell: orientiers[noCell] for noCell in orientiers if orientiers[noCell] != False}


        # Stage 2: Grouping cells by environments
        groups = len(regions) - 1
        left = set(i for i in range(0, self.size) if self.latest[i] == 0)
        while len(left) > 0:
            for cell in left:
                if self.latest[cell] > 0:
                    continue
                currentSphere = spheres[cell]
                around = tools.getVecine(cell)
                grouped = [self.latest[no] for no in around if spheres[no] == currentSphere and self.latest[no] > 0]
                if len(grouped) == 0:
                    # Make a new group of cell
                    groups = groups + 1
                    self.latest[cell] = groups
                    regions.append(0)
                    continue
                # Include to exists region.
                selected = tools.rand.choice(grouped)
                self.latest[cell] = selected
            left = set(i for i in range(0, self.size) if self.latest[i] == 0)

        # Stage 3: Including a region without orientier into region with orientier
        included = 1
        while included > 0:
            included = 0
            for cell in range(0, self.size):
                noRegion = self.latest[cell]
                try:
                    if regions[noRegion] == noRegion:
                        continue
                    if regions[noRegion] > 0:
                        included = included + 1
                        self.latest[cell] = regions[noRegion]
                        continue
                    around = tools.getVecine(cell, conv=lambda noCell: self.latest[noCell])
                    biggers = [idRegion for idRegion in around if idRegion != noRegion and regions[idRegion] == idRegion]
                except:
                    print("... ... Region {}/{} is not defined (cell {})".format(noRegion, len(regions) - 1, cell))
                    continue
                if len(biggers) == 0:
                    continue
                regions[noRegion] = tools.rand.choice(biggers)
                included = included + 1
                self.latest[cell] = regions[noRegion]

        # Result
        return self.latest

### Other generators: map's and pattern's
###

class PatternGenerator:
    LAYERS = ['heights']

    def __init__(self, pattern=None):
        global lands
        if pattern != None:
            self.meta = pattern['meta']
            self.landscape = {land['id']: land for land in pattern.get('landscape', lands)}
            self.layers = pattern['layers']
            self.size = self.meta['Face'] ** 2
        else:
            self.meta = {}
            self.landscape = lands
            self.size = 100
            self.layers = {}

        self.map_layers = []
        self.rand = random.Random()

    # Make map by template
    def makeByTemplate(self):
        """
        Generate a map dictionary (writtable) by this template.
        OUT: dict(map)
        """
        package = {}
        package['meta'] = self.meta
        package['landscape'] = self.landscape
        package['pallette'] = lands

        # Generation of map layers
        heightPairs = self.layers['heights']
        envs = self.layers['landscape']
        culture = self.layers['civilization']
        capitals = self.layer['capitals']
        domains = self.layers['domains']

        heights = self.makeHeights(heightPairs)
        self.map_layers['heights'] = heights
        self.map_layers['domains'] = domains
        self.map_layers['populations'] = self.layers['population']
        self.map_layers['armies'] = self.layers['armies']
        self.map_layers['landscape'] = self.makeLandscape(heights, envs, culture)
        self.map_layers['capitals'] = self.makeCapitals(capitals, domains, threshold=0.5)

        self.domains = []

        package['layers'] = self.map_layers
        return package

    ### Convert Map to Pattern

    def initFromMap(self, mapDefinition):
        self.meta = pattern['meta']
        self.landscape = {land['id']: land for land in pattern['landscape']}
        self.map_layers = pattern['layers']
        self.layers = {}

        # Calc a parameter diapazones
        self.size = self.meta['Face'] ** 2
        terrain = self.map_layers['landscape']
        castles = self.map_layers['castles']
        domains = self.map_layers['domains']
        people = self.map_layers['populations']
        armies = self.map_layers['armies']

        heights = self.getHeights(terrain)
        envire = self.getLandscape(terrain)
        civ = self.getCivilization(terrain)

        self.layers['environment'] = envire
        self.layers['civilization'] = civ
        self.layers['domains'] = domains
        self.layers['population'] = people
        self.layers['armies'] = armies
        self.layers['heights'] = self.getHeights(terrain)
        self.layers['capitals'] = self.getCapitals(castles, domains, civ, envire)

        return True


    def getHeights(self, terrain):
        return [(self.landscape[envir]['Low'] - 0.1, self.landscape[envir]['High'] + 0.1) for envir in terrain]

    def getLandscape(self, terrain):
        def getEnvironment(idLandscape):
            return self.landscape[cell]['Environment']
        return [getEnvironment(cell) for cell in terrain]

    def getCivilization(self, terrain):
        def getEnvironment(idLandscape):
            return self.landscape[cell]['Civilization']
        return [getEnvironment(cell) for cell in terrain]

    def getCapitals(self, castles, domains, civilizations, envire):
        def getCapitalFlag(cell):
            face = self.meta['Face']
            idDomain = domains[cell]
            isCapital = castles[cell] == idDomain
            isCivil = civilizations[cell]
            neares = (envire[cell - 1], envire[cell + 1], envire[cell + face], envire[cell - face])
            nearWater = [i for i in xrange(4) if neares[i] == Environments.Water]
            isPort = envire[cell] == Environments.Port
            isPortable = envire[cell] == Environments.Earth and len(nearWater) > 0

            points = (1.00 if isCapital else 0.0) + (0.75 if isPort else 0.0) + (0.50 if isCivil else 0.0) + (0.25 if isPortable else 0.0)
            return min([points, 1.0])
        return [getCapitalFlag(idDomain) for cell in xrange(self.size)]

    ### END

    ### Generation layers by template
    ###
    ###

    # Layer #0: Heights
    def makeHeights(self, heightPairs):
        """
        Layer #0 - Terrain (height's map)
        OUT: float[] - heights (km under sea) of cell's centers
        """
        heights = [0.0 for i in xrange(self.size)]

        cell = 0
        for cell in xrange(self.size):
            low = 2 * cell
            high = 2 * cell + 1
            low = heightPairs[low]
            high = heightPairs[high]
            heights[cell] = low + self.rand.random()*(high - low)
        return heights

    # Layer #1: Landscapes
    def makeLandscape(self, heights, envs, civil):
        """
        Level #1 - Landscape (textures, soils, land types).
        INPUT:
            float[] heights - layer of cell center heights;
            Environment[] envs - layer of Environment constant's values;
            bool[] civil - layer of Civil flag of landscape type values.
        OUTPUT:
            id[] landscape - matrix of landscape type's id for each cell.
        """
        def makeLandscape(cell, high):
            idEnv = envs[cell]
            isCiv = civil[cell]
            eps = 0.00001
            def selector(landing):
                soil = self.scapes[landing]
                return soil['High'] - high > eps and high - soil['Low'] > eps and soil['Level'] <= self.level and soil['Environment'] == idEnv and soil['Civilization'] == isCiv
            suitable = [landing for landing in self.landings if selector(landing)]
            about = "  Available to cell #{}: {}".format(cell, ", ".join(["{} ({})".format(self.scapes[scape]['Name'], scape) for scape in suitable]))
            logging.debug(about)
            case = random.choice(suitable) if len(suitable) > 0 else 0
            return case

        return [makeLandscape(cell, heights[cell]) for cell in xrange(self.size)]

    # Layer #2: Capitals of players
    def makeCapitals(self, capitolity, domains, threshold=0.1):
        """
        Layer #2 - capitals of domains (0 || id of domain).
        INPUT:
            float[] capitolity - layer of suitability for set capital of region in;
            id[] domains - layer of cells affiliation;
            float threshold - cell will skip if suitability less than threshold value.
        OUTPUT:
            id[] domain's - layer of capitals: 0 if not capital else domain's id.
        """
        size = len(capitolity)
        buildChance = {i: capitolity[i] for i in xrange(size) if capitolity[i] > threshold}
        regions = {}
        for idCell in buildChance.iterkeys():
            idDomain = domains[idCell]
            region = capitalsSet.get(idDomain, [])
            region.append(idCell)
            regions[idDomain] = region

        def choiceCapital(cellIds):
            cellIds.sort(cmp=lambda a,b: capitolity[a] > capitolity[b])
            choiced = self.rand.choice([self.rand.randint(0, len(cellIds) - 1) for _ in xrange(3)])
            return cellIds[choiced]

        capitals = {choiceCapital(cells): idDomain for idDomain, cells in regions}
        return [capitals[i] if capitals.count(i) > 0 else 0 for i in xrange(size)]

    ### END

# TODO List of dependences of loyality layer is not full. Add: welfare and treasures.
class MapGenerator:
    """ Pattern method of generation map. It create a layer by layer and merge it to map. """
    def __init__(self, terrainGenerator, landscapeGenerator, capitalGenerator, populationGenerator, armyGenerator, domainPrehistory, domainHistory, terraformation):
        self.terrainer = terrainGenerator
        self.spheres = PlanetBurn(terrainGenerator.face)
        self.lander = landscapeGenerator
        self.capitaler = capitalGenerator
        self.populator = populationGenerator
        self.forcer = armyGenerator
        self.prehistory = domainPrehistory
        self.history = domainHistory
        self.culture = terraformation
        # Other layers
        self.commerce = Crossroads(self.terrainer.face)
        self.loyality = BanditsAtBorderlands(self.terrainer.face)
        table = loadJSON(os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'data', 'basis', 'toponims.json'))
        self.toponames = UnifiedNatureRegions(self.terrainer.face, table)

        self.spheres.addLinks([self.terrainer, self.lander])
        self.lander.addLinks([self.terrainer, self.spheres])
        self.capitaler.addLinks([self.terrainer, self.lander])
        self.populator.addLinks([self.lander, self.capitaler])
        self.forcer.addLinks([self.lander, self.populator, self.capitaler])
        self.prehistory.addLinks([self.lander, self.capitaler, self.forcer, self.populator, self.terrainer])
        self.history.addLinks([self.prehistory, self.forcer, self.populator])
        self.culture.addLinks([self.lander, self.populator, self.forcer, self.terrainer, self.history, self.capitaler])
        # Other layers
        self.commerce.addLinks([self.capitaler, self.lander])
        self.loyality.addLinks([self.capitaler, self.forcer, self.history])
        self.toponames.addLinks([self.terrainer, self.lander])

        self.domains = []
        self.debugFolder = '/tmp'
        self.name = ""
        self.sealev = 0

    def updateDependences(self):
        self.lander.dependences = (self.terrainer)
        self.capitaler.dependences = (self.terrainer, self.lander)
        self.populator.dependences = (self.lander, self.capitaler)
        self.forcer.dependences = (self.populator, self.lander)
        self.prehistory.dependences = (self.lander, self.capitaler, self.forcer, self.populator)
        self.history.addLinks([self.prehistory, self.forcer, self.populator])
        self.culture.addLinks([self.lander, self.populator, self.forcer, self.terrainer, self.history])

    def new(self, name, face, playersNo, tools=None):
        self.name = name
        self.players=playersNo
        self.face = face
        self.size = face * face
        tools = tools if tools != None else Tools(face)

        logging.debug("New map {}".format(name))
        print("Generation:")
        print("... heights")
        self.terrainer.generate(tools)
        #self.terrainer.output(os.path.join(self.debugFolder, name, 'terrain.layer'), self.terrainer.latest)
        print("... environments")
        self.spheres.generate(tools)
        #self.spheres.output(os.path.join(self.debugFolder, name, 'environments.layer'), self.spheres.latest)
        print("... landings")
        self.lander.generate(tools)
        #self.terrainer.output(os.path.join(self.debugFolder, name, 'landscape.layer'), self.lander.latest)
        print("... castles")
        self.capitaler.generate(tools)
        capitals = [self.capitaler.latest.get(i, 0) for i in xrange(self.size)]
        #self.capitaler.output(os.path.join(self.debugFolder, name, 'castles.layers'), capitals)
        print("... peasants")
        self.populator.generate(tools)
        #self.terrainer.output(os.path.join(self.debugFolder, name, 'populations.layer'), self.populator.latest)
        print("... strength")
        self.forcer.generate(tools)
        #self.terrainer.output(os.path.join(self.debugFolder, name, 'armies.layer'), self.forcer.latest)
        print("... domains")
        domains = self.prehistory.generate(tools)
        self.domains = self.prehistory.domains
        #self.prehistory.output(os.path.join(self.debugFolder, name, 'domains.start.layer'), domains)
        self.history.limit = self.regionsCount
        domains = self.history.generate(tools)
        self.domains = self.history.domains
        #self.prehistory.output(os.path.join(self.debugFolder, name, 'domains.layer'), domains)
        print("... culture and terraformation")
        self.culture.generate(tools)
        print("... commerce and fairs")
        self.commerce.generate(tools)
        #self.culture.output(os.path.join(self.debugFolder, name, 'buildings.layer'), self.culture.latest)
        print("... control over the cells and armies")
        self.loyality.generate(tools)
        #self.loyality.output(os.path.join(self.debugFolder, name, 'control.layer'), self.loyality.latest)
        print("... toponames of nature areals")
        self.toponames.generate(tools)
        #self.toponames.output(os.path.join(self.debugFolder, name, 'marks.layer'), self.toponames.latest)

        print("Initialize a Map package...")
        package = {'meta': {}, 'layers': {}, 'landscape': tools.scapes}
        sea = self.sealev
        top = self.highest
        bottom = self.lowest
        topics = self.extremums
        self.level = self.culture.age
        oikumenaPopulation = sum(self.populator.latest)

        package['meta'] = {'Title': name, 'Face': face, 'PlayersLimit': len(playersNo)-1, 'SeaLevel': 0, 'Top': top, 'Bottom': bottom, 'Extrems': topics, 'Level': self.level}
        package['meta']['WholePopulation'] = oikumenaPopulation
        package['domains'] = self.domains
        package['marks'] = self.toponames.marks
        package['landscape'] = tools.scapes
        package['layers']['terrain'] = self.terrainer.latest
        package['layers']['environments'] = [tools.scapes[scapeNo]['Environment'] for scapeNo in self.lander.latest]
        package['layers']['landscape'] = self.lander.latest
        package['layers']['buildings'] = self.culture.latest
        capitals = [-1 for i in xrange(self.size)]
        for place, user in self.capitaler.latest.iteritems():
            capitals[place] = user
        package['layers']['castles'] = capitals
        package['layers']['populations'] = self.populator.latest
        package['layers']['armies'] = self.forcer.latest
        package['layers']['domains'] = domains
        # Other layers
        package['layers']['commerce'] = self.commerce.latest
        package['layers']['control'] = self.loyality.latest
        package['layers']['marks'] = self.toponames.latest

        return package

    def initBy(self, template, args):
        self.template = template

        self.meta = template['meta']
        self.layers = template['layers']

        self.face = self.meta.get('Face', args.face)
        self.size = self.face * self.face
        self.highest = self.meta.get('Top', args.top)
        self.lowest = self.meta.get('Bottom', args.bottom)
        self.sealev = self.meta.get('SeaHeight', 0.0)
        self.players = self.meta.get('PlayersLimit', args.players)
        self.extremums = self.meta.get('Extrems', int(self.size * 0.1))

        self.initLandscapeLayerProps(self.layers.get['landings'], self.meta['Level'])
        return None

    def initHeightsLayerProps(self, top, bottom, seaLev, limited=None):
        self.highest = top
        self.lowest = bottom
        self.sealev = seaLev
        self.extremums = limited if limited != None else int(math.ceil(self.size * 0.1))

    def initLandscapeLayerProps(self, landTypes, level):
        self.level = level
        def copyScape(scape):
            return landTypes[scape]
        self.scapes = [copyScape(typed) for typed in landTypes]
        self.landings = [land['ID'] for land in self.scapes if not land['Civilization'] and land['Level'] < level + 1]
        self.buildings = [construct['ID'] for construct in self.scapes if construct['Civilization'] and (construct['Level'] < level + 1)]
        sorted(self.scapes, key=lambda item: item['ID'])
        sorted(self.landings)

    def setRegionsLimit(self, limit):
        self.regions = int(limit if limit > 0 else len(self.players) + self.face + 1)
