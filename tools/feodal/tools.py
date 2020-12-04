import math
import os
import json
from random import Random

from constants import Environments
import MapBackgroundGenerator as mbg

###
### Instruments.
###

class Tools:
    def __init__(self, face, scapes):
        self.face = face
        self.size = face * face
        scapes.sort(key=lambda landscape: landscape['ID'])
        self.scapes = scapes
        self.rand = Random()

    # Math

    def d(self, cellA, cellB):
        return self.dd(cellA['id'], cellB['id'])

    def dd(self, idA, idB):
        dx = abs(self.x(idA) - self.x(idB))
        dy = abs(self.y(idA) - self.y(idB))
        return dx + dy

    def average(self, collection):
        return (reduce(lambda acc, val: acc + val, collection, 0)/len(collection), len(collection))

    def getKey(self, dictionary, value):
        for k, v in dictionary.iteritems():
            if v == value:
                return k

    def near(self, noCell, noCell2, rad=1):
        dX = abs(self.x(noCell) - self.x(noCell2))
        dY = abs(self.y(noCell) - self.y(noCell2))
        return dX + dY <= rad

    def x(self, idCell):
        return idCell % self.face
    def y(self, idCell):
        return int(idCell / self.face)

    # Landscape operations

    def getVecine(self, noCell, conv = lambda idx: idx):
        return [conv(noCell + step) for step in [-self.face, 1, +self.face, -1] if self.size > noCell + step and noCell + step > 0 and self.near(noCell, noCell + step)]

    def getLandscape(self, idLandscape):
        landscapes = [scape for scape in self.scapes if scape['ID'] == idLandscape]
        return landscapes[0]

    def getHobbitable(self, idLandscape):
        return self.scapes[idLandscape]['Hobbitable']

    def getCapacity(self, idLandscape):
        if idLandscape < 0:
            return 0
        return self.scapes[idLandscape]['Capacity']

    def getAvailableID(self, cond=lambda item: True):
        return [scape['ID'] for scape in self.scapes if cond(scape)]

    # Movement by map layer
    def left(self, fromIndex):
        return fromIndex - 1 if fromIndex > 0 else fromIndex
    def right(self, fromIndex):
        return fromIndex + 1 if (fromIndex + 1) % self.face > 0 else fromIndex
    def up(self, fromIndex):
        return fromIndex - self.face if fromIndex - self.face > 0 else fromIndex
    def down(self, fromIndex):
        return fromIndex + self.face if fromIndex < self.face * self.face else fromIndex

    # Approximation of heights
    def getExtrmumsOf(self, layer):
        mini =  10000000
        maxi = -10000000
        for val in layer:
            if mini > val: mini = val
            if maxi < val: maxi = val
        return (mini, maxi)

    def smoothSlope(self, idCell, high, extrimes, k = 1.1):
        distance = self.dd
        if extrimes.has_key(idCell):
            return extrimes[idCell]
        influences = [self.calcKoolonInfluence(q1=math.sqrt(high), q2=extrimes[i], d=distance(idCell, i), koeff=k) for i in extrimes.iterkeys()]
        upd = self.average(influences)
        return high + upd[0]

    def highApproxy(self, idCell, height, extrimes):
        distances = {i: self.dd(idCell, i) for i in extrimes.iterkeys()}
        ranges = distances.items()
        on = ranges.index(min(ranges))
        influencer = distances.keys()[on]
        return height + Tools.calcKoolonInfluence(self, 1, extrimes[influencer], math.sqrt(distances[influencer]))

    def influenceOf(self, currentHeight, extremumHeight, distance, longOfArms=None):
        longOfArms = abs(longOfArms if longOfArms is not None else self.face)
        return (currentHeight * (longOfArms - distance) + extremumHeight * distance) / longOfArms

    def getNearestCenter(self, idCell, centers):
        distances = [self.dd(idCenter, idCell) for idCenter in centers]
        distance = min(distances)
        return (centers[ distances.index(distance) ], distance)

    # Approximation of heights methods
    def calcKoolonInfluence(self, q1, q2, d, koeff = 1.1):
        distQ = d * d + 1
        return koeff * q1 * q2 / distQ

    # Microconstructors
    def cell(self, ix, high, land, peasants, soldiers, idDomain = -1):
        landscape = self.scapes[land]
        return {'id': ix, 'landscape': land, 'domain': idDomain, 'high': high, 'population': peasants - soldiers, 'army': soldiers, 'capacity': landscape['Hobbitable']}

    def domain(self, no, capitalID, ownerID=0):
        return {'id': no, 'name': "Domain #{}".format(no), 'capital': capitalID, 'owner': ownerID}

    def dwelling(self, no, subtype):
        return {'id': no, 'name': 'village', 'class': subtype, 'walls': {'height': 2, 'perimeter': 800, 'material': 1.0}} # Material - wood, side of wall = 200m, height = 2m

    # Conditional method for landscape's filter

    def constructable(self, high, idBuild, cell):
        building = self.scapes[idBuild]
        if building.get('Hobbitable', building.get('Capacity', 0)) > cell.get('Hobbitable', cell.get('Capacity', 0)):
            return False
        return (building['High'] <= high and building['Low'] >= high) and (cell['High'] <= high and cell['Low'] <= high)

    def canBuildAt(self, build, height, landscape, age):
        place = landscape['Environment']
        if not build['Civilization']:
            return False
        if build['Low'] <= height and build['High'] >= height:
            return False
        return build['Level'] < age + 1 and place == build['Environment']

    def homeable(self, landscapeID, age = 10):
        landscape = self.scapes[landscapeID]
        envir = landscape['Environment']
        return landscape['Civilization'] and envir != Environments.Air and envir != Environments.Bridge and envir != Environments.Water and landscape['Hobbitable'] > 0 and landscape['Level'] <= age

class Picturization:
    def __init__(self, mapInstance, pallette = None):
        self.source = mapInstance
        self.lowest = mapInstance.bottom
        self.highest = mapInstance.top
        self.face = mapInstance.face
        self.pallettes = pallette
        if pallette is None:
            path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'basis', 'pallette.json')
            with open(path, "r") as source:
                self.pallettes = json.load(source)

    def getExtrmumsOf(self, layer):
        mini =  10000000
        maxi = -10000000
        for val in layer:
            if mini > val: mini = val
            if maxi < val: maxi = val
        return (mini, maxi)

    def saveAsGrayscale(self, folder, layerName, layer, zoom=10):
        """ Save compareable-values layer as grayscale PNG image """
        path = os.path.join(folder, layerName + ".png")
        layer = mbg._zoom(layer, self.face, ppc=zoom)
        image = mbg.grayscaling(layer, self.lowest, self.highest)
        #print("... ... Save {0} image".format(path))
        mbg.saveGray(path, image, side)
        return image

    def saveAsRGB(self, folder, layerName, layer, zoom=10):
        """ Save ID_values layer as full-color PNG image """
        path = os.path.join(folder, layerName + ".png")
        side = zoom * self.face
        pallette = self.pallettes.get(layerName, None)
        if pallette is None:
            return False
        image = mbg.colorize(mbg.packLayer(mbg._zoom(layer, self.face, pixelPerCell), side), pallette)
        mbg.savePNG(path, mbg.toLine(image, side), side)

    def imagination(self, mapName, pixelPerCell=10, path="."):
        """ Make images by layers """
        pngMask = "{}/{}.png"
        side = pixelPerCell*self.face
        folder = mapName

        # Create folder for image
        dirPath = os.path.join(path, folder)
        if not os.path.exists(dirPath):
            os.mkdir(dirPath)
        dirPath = os.path.join(dirPath, 'visual')
        if not os.path.exists(dirPath):
            os.mkdir(dirPath)

        print("... images (grayscaling of heights: {}-{} => 0-255)".format(self.lowest, self.highest))
        def saveGray(layer, layerName):
            path = pngMask.format(dirPath, layerName)
            #print("... ... Save {0} image".format(path))
            mbg.saveGray(path, image, side)


        layers = self.source.layers
        # Terrain with smooth, other with not
        layer = layers['terrain']
        image = mbg.grayscaling(layer, self.lowest, self.highest)
        image = mbg._zoom(image, self.face, pixelPerCell)
        saveGray(image, 'heights')
        image = mbg._blur(image, pixelPerCell * 0.10)
        saveGray(image, 'terrain')

        for layerName in ['populations', 'armies']:
            layer = layers[layerName]
            limits = self.getExtrmumsOf(layer)
            image = mbg.grayscaling(layer, limits[0], limits[1])
            image = mbg._zoom(layer, self.face, pixelPerCell)
            saveGray(image, layerName)

        for layerName, pallette in self.pallettes.iteritems():
            fname = pngMask.format(dirPath, layerName)
            #print("... ... Save {0} image".format(fname))
            try:
                if layerName not in layers:
                    continue
                layer = layers[layerName]
                image = mbg.colorize(mbg.packLayer(mbg._zoom(layer, self.face, pixelPerCell), side), pallette)
            except mbg.InvalidIndex as e:
                print("Error on {} layer: {}. Collection len: {}".format(layerName, e.message, len(e.collection)))
                continue
            except KeyError as e:
                print("Error on {} layer: {}. Collection: ".format(layerName, e.message), layers.keys())
            mbg.savePNG(fname, mbg.toLine(image, side), side)

        try:
            fname = pngMask.format(dirPath, 'landscape')
            layer = layers['landscape']
            image = mbg.colorize(mbg.packLayer(mbg._zoom(layer, self.face, pixelPerCell), side), self.pallettes['landscape'])
            writeable = mbg.toLine(mbg._blur(image, 2.5), side)
            mbg.savePNG(fname, writeable, side)
        except mbg.InvalidIndex as e:
            print("Error on landscape layer: {}. Collection len: {}.".format(e.message, len(self.pallettes['landscape'])))

class AreaAgregation:
    def __init__(self):
        self.rand = Random()

    def intersects(self, values, extsLeft=0, extsRight=0):
        bottom = -10000.0
        top = 10000.0
        for left, right in values:
            if left > right:
                continue
            bottom = bottom if bottom >= left else left
            top = top if top <= right else right
            extsLeft = extsLeft if extsLeft <= left else left
            extsRight = extsRight if extsRight >= right else right
        return (bottom, top, extsLeft, extsRight)

    # Value of area is weight of choice it
    def weighted_choice(self, areas, key=None):
        key = key if key != None else lambda item: item.value
        if len(values) == 0:
            return 0
        sorted(areas, key=lambda area: key(area))
        availble = [area.id for area in areas]
        for i in range(0, len(areas) - 1):
            if self.rand.random() < areas[i].value:
                return areas[i].id
        return 0

    def extends(self, values):
        pass

def loadJSON(path):
    with open(path, "r") as source:
        return json.load(source)
