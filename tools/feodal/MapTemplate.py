import os
import sys
import math
import random
import operator
import argparse
import logging
import numpy as np
from collections import Counter

from feodal.constants import Environments
from feodal.lands import lands
import feodal.feods
from feodal import stats

class MapGenAreaType:
    TERRA=1 #
    ENVIR=2 #
    POLIT=3
    POPUL=4 #
    CAPIT=5
    ARMY=6  #
    CIVIL=7 #
    # With fixed value

    LANDS=10

    def set(typeID, place, areaID):
        if area.type == MapGenAreaType.TERRA:
            place.terra.append(areaID)
        elif area.type == MapGenAreaType.ENVIR:
            place.envir.append(areaID)
        elif area.type == MapGenAreaType.POPUL:
            place.popul.append(areaID)
        elif area.type == MapGenAreaType.CAPIT:
            place.capit.append(areaID)
        elif area.type == MapGenAreaType.POLIT:
            place.polit.append(areaID)
        elif area.type == MapGenAreaType.CIVIL:
            place.polit.append(areaID)
        else:
            place.lands = [areaID]
        return place

class MapGenArea:
    LAST_ID = 0
    def __init__(self, typeOf, value, idArea = None):
        self.id = idArea if idArea != None else MapGenArea.LAST_ID + 1
        self.type = typeOf
        self.value = value
        MapGenArea.LAST_ID = MapGenArea.LAST_ID + 1

class MapGenCellLayers:
    LAST_ID = 0
    def __init(self, terra=[], envir=[], popul=[], capit=[], polit=[], idCell = None):
        if idCell != None:
            MapGenCellLayers.LAST_ID = idCell - 1
        self.id = MapGenCellLayers.LAST_ID + 1
        self.terra = terra + [-1]
        self.envir = envir + [-2]
        self.popul = popul + [-3]
        self.capit = capit + [-4]
        self.polit = polit + [-5]
        self.force = []
        self.lands = []
        self.civil = []
        MapGenCellLayers.LAST_ID = MapGenCellLayers.LAST_ID + 1

class MapTemplate:
    def __init__(self, name, landscapes, face = 10, regions=15):
        self.name = name
        self.face = max(10, int(face))
        self.size = self.face * self.face
        self.landscapes = landscapes
        self.domains = regions

        self.vecine = (1, -self.face, 0, -1, self.face)
        allCells = [i for i in range(0, self.face - 1)]
        allRanges = [(i, 1/self.size) for i in range(1, regions)]
        self.areas = []
        self.areas.append( MapGenArea(idArea=-4, typeOf=MapGenAreaType.CAPIT, value=1/self.size) )
        self.areas.append( MapGenArea(idArea=-3, typeOf=MapGenAreaType.POPUL, value=(0, 100)) )
        self.areas.append( MapGenArea(idArea=-2, typeOf=MapGenAreaType.POLIT, value=allRanges) )
        self.areas.append( MapGenArea(idArea=-1, typeOf=MapGenAreaType.ENVIR, value=Environments.Earth) )
        self.areas.append( MapGenArea(idArea=+0, typeOf=MapGenAreaType.TERRA, value=(-1000, 1000)) )

        self.cells = [MapGenCellLayers() for i in allCells]

    def addArea(self, area, cells = []):
        def landingy(place):
            place.lands = [area.id]
        if len(cells) == 0:
            return
        if area.type == MapGenAreaType.TERRA:
            make = lambda place: place.terra.append(area.id)
        elif area.type == MapGenAreaType.ENVIR:
            make = lambda place: place.envir.append(area.id)
        elif area.type == MapGenAreaType.POPUL:
            make = lambda place: place.popul.append(area.id)
        elif area.type == MapGenAreaType.CAPIT:
            make = lambda place: place.capit.append(area.id)
        elif area.type == MapGenAreaType.POLIT:
            make = lambda place: place.polit.append(area.id)
        elif area.type == MapGenAreaType.CIVIL:
            make = lambda place: place.polit.append(area.id)
        else:
            make = landingy

        for cell in cells:
            make(self.cells[cell - 1])
        return self

    def createFromMap(self, source):
        self.face = source.face
        self.size = self.face * self.face
        self.domains = source.domains
        self.landscapes = source.landscapes
        self.cells = [MapGenCellLayers() for i in range(0, self.size-1)]
        self.vecine = [1, -self.face, 0, -1, self.face]

        landing = source.layers['landscapes']
        dominion = source.layers['domains']
        capitals = source.layers['capitals']
        print("Making areas by map layers..")
        print("     ... heights;")
        self.areas.extend(self.extractHeightDiapazones(landing))
        print("     ... landscape type;")
        self.areas.extend(self.extractEnvironments([land['Environment'] for land in landing]))
        print("     ... peasant population;")
        self.areas.extend(self.extractPopulationDiapazones(source.layers['populations'], dominion))
        print("     ... armies at map;")
        self.areas.extend(self.extractForceDiapazones(source.layers['armies'], dominion, landing))
        print("     ... civilization level of cells;")
        self.areas.extend(self.extractCivilization(landing))
        print("     ... domination on land;")
        self.areas.extend(self.extractDominion(dominion, capitals))
        print("     ... probability of capital building;")
        self.areas.extend(self.extractCapitality(dominion, capitals))
        print("OK.")
        return True

    def unpack(self, package):
        self.name = package['meta']['Name']
        self.face = package['meta']['Face']
        self.size = self.face*self.face
        self.cells = package['layers']
        self.areas = package['areas']
        self.landscapes = package['landscapes']

    def pack(self):
        box = {}
        box['meta'] = {'Name': self.name, 'Face': self.face, 'Age': 1}
        box['landscapes'] = self.landscapes
        box['layers'] = self.cells
        box['areas'] = self.areas
        return box

    HEIGHT_ACCCEPTED = 0.010

    def extractHeightDiapazones(self, landscapeLayer):
        ground = self.landscapes
        unsmoothes = { idLandscape: MapGenArea(typeOf=MapGenAreaType.TERRA, value=(ground[idLandscape]['Low'], ground[idLandscape]['High'])) for idLandscape in landscapeLayer }
        ind = 0
        for landscape in landscapeLayer:
            self.cells[ind].terra.append(unsmoothes[landscape].id)
            ind = ind + 1
        return unsmoothes.items()

    def extractEnvironments(self, environmentsMap, capitals = {}):
        placescapes = [MapGenArea(typeOf=MapGenAreaType.ENVIR, value=enviro) for enviro in (Environments.Water, Environments.Bridge, Environments.Port, Environments.Air)]
        for i in range(0, self.size-1):
            regio = self.getVecine(i, environmentsMap)
            state = Counter(regio)
            cellStatuses = self.cells[i].envir
            mustSettable = capitals.items().count(i) > 0
            if state[Environments.Earth] > 0:
                cellStatuses.append(-1)
            if state[Environments.Bridge] > 0 or state[Environments.Water] > 0 or state[Environments.Port] > 0:
                if not mustSettable:
                    cellStatuses.append(placescapes[0].id)
                cellStatuses.append(placescapes[1].id)
            if environmentsMap[i] == Environments.Bridge or environmentsMap[i] == Environments.Port:
                cellStatuses.append(placescapes[2].id)
            if environmentsMap[i] == Environments.Air:
                cellStatuses.append(placescapes[3].id)
            self.cells[i].envir = cellStatuses
        return placescapes

    def extractPopulationDiapazones(self, populationMap, domainsMap, terrain=None):
        """
        IN:
            - populationMap: int[] - peasantman in cells of map.
            - domainsMap: int[] - id of domain for all cells.
            - terrain: int[] - id of landscape type for all cells.
        OUT: MapGenArea[] - list of population area.
        """
        perDomains = {idDomain: 0 for idDomain in domainsMap}
        toMap = []
        for i in range(0, self.size -1):
            inDomain = domainsMap[i]
            perDomains[inDomain] = perDomains[inDomain] + max(0, populationMap[i])
            toMap.append(inDomain)
        areas = [MapGenArea(typeOf=MapGenAreaType.POPUL, value=(0, population)) for _, population in perDomains]
        for i in range(0, self.size -1):
            self.cells[i].popul.append(areas[toMap[i]].id)
        return areas

    def extractForceDiapazones(self, forcesMap, domainsMap, terrain):
        """
        IN:
            - forcesMap: int[] - soldiers in cells of map.
            - domainsMap: int[] - id of domain for all cells.
            - terrain: int[] - id of landscape type for all cells.
        OUT: MapGenArea[] - list of population area.
        """
        dislocations = {idDomain * 100 + idLandscape: 0 for idDomain in domainsMap for idLandscape in terrain}
        toMap = []
        for i in range(0, self.size -1):
            inLocation = domainsMap[i] * 100 + terrain[i]
            dislocations[inLocation] = dislocations[inLocation] + max(0, forcesMap[i])
            toMap.append(inLocation)
        areas = [MapGenArea(typeOf=MapGenAreaType.ARMY, value=(0, forces)) for _, forces in dislocations]
        for i in range(0, self.size - 1):
            self.cells[i].force.append(areas[toMap[i]].id)
        return areas

    def extractCivilization(self, landscapeLayer):
        mapOfCivil = [self.landscapes[land]['Civilization'] for land in landscapeLayer]
        civilizationMap = []
        civilitesArea = [MapGenArea(typeOf=MapGenAreaType.CIVIL, value=percent) for percent in (0.1, 0.3, 0.5, 0.7, 0.9)]
        for i in range(0, self.size -1):
            civility = Counter(self.getVecine(i, area=mapOfCivil))
            no = 4 if mapOfCivil[i] else civility[True]
            civilizationMap.append(civilitesArea[no].value)
            self.cells[i].civil.append(civilitesArea[no].id)
        return civilitesArea

    def extractDominion(self, domainsMap, capitals={}):
        areas = [MapGenArea(typeOf=MapGenAreaType.POLIT, value=(idDomain, 0.85)) for idDomain, _ in capitals]
        areas = areas + [MapGenArea(typeOf=MapGenAreaType.POLIT, value=(idDomain, 0.15)) for idDomain, _ in capitals]
        doms = capitals.keys()
        provincione = len(capitals)
        for i in range(0, self.size-1):
            probability = doms.index(domainsMap[i])
            if capitals[domainsMap[i]] == i+1:
                probability = probability + provincione
            self.cells[i].polit.append(areas[probability].id)
        return areas

    def extractCapitality(self, domainsMap, capitals={}):
        areas = [MapGenArea(typeOf=MapGenAreaType.CAPIT, value=0.85) for _, _ in capitals]
        for idDomain, idCell in capitals:
            no = capitals.keys().index(idDomain)
            around = self.getVecine(idCell-1)
            for cell in around:
                self.cells[cell.id].capit.append(areas[no].id)
        return areas

class MapByTemplate:
    SELF_ORDERABLE = 0.2

    def __init__(self, face=10, top=3.0, bottom=-1.0, seaLev=0.0, logPath=None):
        random.seed()
        self.face = face
        self.size = face*face
        self.highest = top
        self.lowest = bottom
        self.sealev = seaLev

        self.landings = []
        self.buildings = []

        self.domains = []
        self.bases = [-10, face + 1, self.size - face - 2, 2*face - 2, self.size - 2*face + 1]
        self.pallettes = {}
        palletePath = os.path.join(root, 'tools', 'data', 'pallette.json')
        with open(palletePath, 'r') as basis:
            self.pallettes = feods.json.load(basis)
        # Game
        self.latest = None
        self.times = 0

        logPath = os.path.join(logPath, "generate.log") if logPath != None else "generate.log"
        logging.basicConfig(filename=logPath, level=logging.DEBUG)

    def makeByTemplate(self, name, template, isClear=True):
        self.rand = random.Random()
        self.name = self.name if name == None else name
        self.landings = template.landscapes
        self.face = template.face
        self.size = template.size
        logging.debug("Make new map {} like as pattern {}".format(self.name, template.name))

        extsLeft = 0
        extsRight = 0
        # Stage A. of domain-capitals generation.
        domainable = [area for area in template.areas if area.type == MT.MapGenAreaType.POLIT]
        domainsList = [self.domain(domainArea.value[0], 0) for domainArea in domainable]
        #self.domains = domainsList
        domainsMap = []
        capitalSet = {domain['id']: 0 for domain in domainsList}
        def makeCell(idCell, cell):
            (high, extsLeft, extsRight) = self.makeHeight(template.areas, cell, extsLeft, extsRight)
            land = self.makeLandscape(template.areas, cell, high)
            peasants = self.makePopulation(template.areas, cell, land)
            soldiers = self.makeArmy(template.areas, cell, peasants)
            idDomain = self.makeDomain(domainable, cell, land, peasants, domainable)
            domainsMap.append(idDomain)
            return self.cell(idCell, high, land, peasants, soldiers, idDomain)
        cells = [makeCell(cell.id, cell) for cell in template.cells]
        exterminals = {i: cell['high'] for cell in cells if abs(cell['high'] - extsLeft) < 0.001 or cell['high'] - extsRight > -0.001}
        # Second stage of Heightmap genertion: approximation of heights.
        for cell in cells['high']:
            cell['high'] = self.highApproxy(cell['id'], cell['high'], exterminals)

        if isClear:
            print("Generation of uncovered cells:")
            print("... heights")
            heights  = self.genHighmap(self.face if topics == None else topics, sharping=False)
            print("... castles")
            castles  = self.genCastles(landings, heights, playersNo)
            print("... peasants")
            peasants = self.genPopulation(landings, oikumenaPopulation)
            print("... strength")
            strength = self.genArmies(peasants, landings)
            print("... domains")
            domains = self.genDomains(peasants, strength, castles, landings)
        else:
            heights = self.layers['terrain']
            landings = self.layers['landscapes']
            castles = self.layers['castles']
            peasants = self.layers['populations']
            strength = self.layers['armies']
            domains = self.layers['domains']

        # Stage B. of domain-capitals generation: Battle for extends of borders and free.
        freeNow = [cell['id'] for cell in cells if cell['domain'] == 0]
        for idCell in freeNow:
            around = self.getVecine(idCell, conv=lambda cell: cell['domain'])
            degreePresence = Counter(around)
            domainsAround = degreePresence.iterkeys()
            injectTo = 0
            for domainId in domainsAround:
                if self.rand.random() < 0.20 * degreePresence[domainId]:
                    injectTo = domainId
                    break
            if injectTo == 0 and self.rand.random() < GravityOfCities.SELF_ORDERABLE:
                independed = self.domain(len(domainsList), idCell)
                domainsList.append(independed)
                injectTo = independed['id']
                capitalSet[injectTo] = idCell
            domainsMap[idCell - 1] = injectTo

        # Stage C. of domains generation: final of pregame borders extending.
        for idCell in freeNow:
            if cells[idCell-1]['domain'] > 0:
                continue
            around = self.getVecine(idCell, conv=lambda cell: cell['domain'])
            degreePresence = Counter(around)
            domainsAround = degreePresence.iterkeys()
            injectTo = 0
            for domainId in domainsAround:
                if self.rand.random() < 0.20 * degreePresence[domainId]:
                    injectTo = domainId
                    break
            domainsMap[idCell - 1] = injectTo

        # Final of capitals generation.
        for idDomain, idCapital in variable:
            if idCapital > 0:
                continue
            domainLand = [cell['id'] for cell in cells if cell['domain'] == idDomain]
            # Weighted choice of capital's place
            weights = {0: 0.1}
            for cellId in domainLand:
                probability = 0.5
                for area in template.cells[cellId-1].capit:
                    probability = (probability + area.value) / 2
                weights[cellId] = probability
            idCapital = 0
            for idCell, weight in variable:
                if self.rand.random() > weight:
                    continue
                idCapital = idCell
                break
            # Capital is undefined?
            if capitalSet.get(idDomain, 0) == 0:
                idCapital =self.rand.choice(domainLand)
            capitalSet[idDomain] = idCapital
            domainsList[idDomain-1]['capital'] = idCapital

        # Appling a domains map and map of capitals

        print("Stage 3. Merge a cell's layers")
        self.layers = {}
        self.layers['terrain'] = heights
        self.layers['landscapes'] = landings
        capitals = [-1 for i in xrange(self.face * self.face)]
        for place, user in castles.iteritems():
            capitals[place] = user
        self.layers['castles'] = capitals
        self.layers['populations'] = peasants
        self.layers['armies'] = strength
        self.layers['domains'] = domains
        self.meta = {'Title': name, 'Face': self.face, 'PlayersLimit': len(playersNo)-1, 'SeaHeight': self.sealev, 'Top': self.highest, 'Bottom': self.lowest, 'Extrems': len(self.extremums)}
        return self.mergeLayers(heights, landings, castles, peasants, strength, domains)

    #
    # Generation by Template
    #
    USER_AREALES = 4

    def makeHeight(self, areas, cell, extsLeft = 0, extsRight = 0):
        if len(areas) == 0 or len(layers) == 0:
            return None

        skip = GravityOfCities.USER_AREALES
        # Available heights in result is intersection of all areas heights.
        values = [areas[idArea+skip].value for idArea in cell.terra]
        if len(values) == 0:
            cells.append(0.000)
            return None
        (bottom, top, extsLeft, extsRight) = self.intersects(values, extsLeft, extsRight)
        return (self.rand.randint(bottom, top), extsLeft, extsRight)

    def makeLandscape(self, areas, cell, high):
        # Default landscape - grassfields
        if len(areas) == 0:
            return 1
        # Waterline
        if high < 0.0001:
            return 28
        # Definitely
        skip = GravityOfCities.USER_AREALES
        if len(cell.lands) > 0:
            lands = []
            for idArea in cell.lands:
                lands = lands + areas[idArea + skip].value
            return self.rand.choice(lands)

        # Search by parameters
        civilityValues = [areas[idArea+skip].value for idArea in cell.civil]
        environments = [areas[idArea+skip].value for idArea in cell.envir] # flat array! .value is not array!
        civily = self.rand.random() < sum(civilityValues) / len(civilityValues)
        environment = self.rand.choice(environments)

        available = [land['ID'] for land in self.landings if land['Civilization'] == civ and land['Environment'] == envir and land['Low'] <= high and land['High'] >= high]
        return self.rand.choice(available)

    def makePopulation(self, areas, cell):
        if len(areas) == 0 or cell == None:
            return None
        settlers = []
        skip = GravityOfCities.USER_AREALES
        values = [areas[idArea+skip].value for idArea in cell.popul]
        if len(values) == 0:
            return 0
        (mini, maxi, _, _) = self.intersects(values)
        if maxi < mini:
            mini = maxi
        if mini < 1:
            return 0

        # Full true: this cell of all areals is hobbited and it considers.
        communna = self.rand.randint(0, mini)
        for areaId in cell.popul:
            areas[idArea].value = areas[idArea].value - (communna, communna)
        return communna

    def makeArmy(self, areas, cell, communna):
        if len(areas) == 0:
            return None
        skip = GravityOfCities.USER_AREALES
        values = [areas[idArea+skip].value for idArea in cell.force]
        if len(values) == 0:
            forces.append(0)
            return None
        (mini, maxi, _, _) = self.intersects(values)
        if maxi < mini:
            mini = maxi
        if mini < 1:
            return 0

        # Considers forces on all areals.
        squid = self.rand.randint(0, min([mini, communna]))
        for areaId in cell.popul:
            areas[idArea].value = areas[idArea].value - (squid, squid)
        return squid

    def makeDomain(self, areas, cell, land, population, domainsList):
        if len(cell.polit) > 0:
            return 0
        skip = GravityOfCities.USER_AREALES
        domainable = [domain for domain in areas if domain.id in cell.polit]
        return self.weighted_choice(domainable, key=lambda item: -item.value[1])

    # Difficult: overwriteable areas.
    def makeCastle(self, areas, cell, domainsMap, domainsList):
        if len(cell.civil) == 0:
            return 0

        # Available variants
        capitul = {i: [] for i in generedCapitals if i > 0}
        chance = {i: [] for i in generedCapitals if i > 0}
        i = 1
        for domainId in generedDomains:
            capitul[domainId].append(i)
            chance[domainId].append(0.7 if generedCapitals[i] == 0.3 else 0.3)
            i = i + 1
        # Calc probabilites
        for area in capitality:
            probability = area.values

        return generedCapitals

    ###############################################################

    def getVecine(self, idc, area=None):
        area = self.cells if area == None else area
        return [area[idc + shift] for shift in self.vecine if idc + shift > 0 and idc + shift < self.size]
