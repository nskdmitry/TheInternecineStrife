''' Set of map generator facades '''
import math, sys
if sys.hexversion < 0x030100F0:
    import generators, tools, lands
else:
    from feodal import generators, tools, lands

class AbstractGeneratorFacade:
    """ Framework for constructs a generators. """
    #DESCRIPTION = "NOT USE THIS CLASS IN SCRIPT, SUCCESSION ONLY"

    def __init__(self, face, playerIDs, regionsLimit=0, age=generators.Age.Bronze):
        self.playerIDs = playerIDs

        self.landings = lands.lands
        self.tools = tools.Tools(face, [self.landings[land] for land in self.landings.keys()])
        self.generator = None
        self.regions = regionsLimit

    def tuneTerrain(self, top, bottom, seaLev):
        self.generator.initHeightsLayerProps(top, bottom, seaLev, self.tools.face - 1)

    def setLandscapeAsset(self, asset):
        self.landings = asset
        self.tools.scapes = [self.landings[land] for land in asset.keys()]
        self.tools.scapes.sort(key=lambda landscape: landscape['ID'])

    def generate(self, name, debugFolder):
        self.generator.regionsCount = self.regions
        self.generator.debugFolder = debugFolder
        print("Save debug output files to", debugFolder)
        return self.generator.new(name, self.tools.face, self.playerIDs, tools=self.tools)


class SeparatesWithoutSea(AbstractGeneratorFacade):
    """ Each cell is domain, water landscape is hadn't """
    #DESCRIPTION = "NOT USE THIS CLASS IN SCRIPT, SUCCESSION ONLY"

    def __init__(self, face, playerIDs, age=generators.Age.Iron, regionsLimit=0):
        super(AbstractGeneratorFacade, self).__init__(face, playerIDs, age)

        terrain = generators.SmoothTerrainGenerator(face, exterms=3, top=3000, bottom=100, sea=0)
        lander = generators.SimpleLandGenerator(face, age)
        capitaler = generators.SelfCapitalCell(face)
        dweller = generators.CommonSenseDwellinger(face, self.scapes, globalPopulation=10000)
        officier = generators.LordCourt(face, self.scapes)
        explorer = generators.SeparatedCells(face)
        historic = generators.NoDomainHistory(face)
        culture = generators.NoBuildingsBefore(face, age)

        self.generator = generators.MapGenerator(terrain, lander, capitaler, dweller, officier, explorer, historic, culture)

class SeparatedCells(SeparatesWithoutSea):
    def __init__(self, face, playerIDs, age=generators.Age.Iron, regionsLimit=0):
        super(SeparatesWithoutSea).__init__(self, face, playerIDs, age)
        self.generator.terrainer = generators.SmoothTerrainGenerator(face, extrms=3, top=3000, bottom=-1000, sea=0)
        self.generator.updateDependences()

class RandomicColonies(AbstractGeneratorFacade):
    """  """
    def __init__(self, face, playersIDs, age=1, regionsLimit=0):
        AbstractGeneratorFacade.__init__(self, face, playersIDs, age)

        wholePopulations = face * face * 10

        terrain = generators.SmoothTerrainGenerator(face, extrems=int(face/2), top=3000, bottom=-500, sea=0)
        lander = generators.SimpleLandGenerator(face, age)
        dweller = generators.EvolutionRandomHomo(face, wholePopulations)
        capitaler = generators.SearchGoodPlaceToCapital(face, age, playersIDs)
        officier = generators.LordCourt(face, self.scapes)
        explorer = generators.InfinityAbsorbation(face)
        historic = generators.NoDomainHistory(face)
        culture = generators.WarAndPease(face, age)

        self.generator = generators.MapGenerator(terrain, lander, capitaler, dweller, officier, explorer, historic, culture)

class Voolcano(AbstractGeneratorFacade):
    """ Circular landscape zones around of high mountain in sea. Neolit only. """
    def __init__(self, face, playersIDs, age=generators.Age.Neolit, regionsLimit=0):
        AbstractGeneratorFacade.__init__(self, face, playersIDs, age)

        oikumenaPopulation = int(face*face*64)

        terrain = generators.VoolcanoIsland(face, top=5000, bottom=-500)
        lander = generators.ZonalLandscape(face, self.landings)
        dweller = generators.BurnInHomes(face, globalPopulation=oikumenaPopulation)
        capitaler = generators.SeparatedTribes(face, playersIDs, regionsCount=face+len(playersIDs))
        officier = generators.AggressiveTribes(face)
        explorer = generators.LazyDevelopment(face)
        historic = generators.NoDomainHistory(face)
        culture = generators.DwellyCaves(face)

        self.generator = generators.MapGenerator(terrain, lander, capitaler, dweller, officier, explorer, historic, culture)

class Canderra(Voolcano):
    """ Mountain's wall around of lake. """
    def __init__(self, face, playersIDs, age=generators.Age.Neolit, regionsLimit=0):
        Voolcano.__init__(self, face, playerIDs, age, regionsLimit=regionsLimit)
        self.generator.terrainer = generators.VoolcanoLake(face, top=5000, bottom=-1000)
        self.generator.updateDependences()

class Classic(AbstractGeneratorFacade):
    """ Smooth landscape and good-placed capitals of domains with history of wars. """
    def __init__(self, face, playersIDs, age=generators.Age.Iron, regionsLimit=0):
        AbstractGeneratorFacade.__init__(self, face, playersIDs, regionsLimit, age)

        oikumenaPopulation = face*face*100

        terrain = generators.SmoothTerrainGenerator(face, extrems=int(face/2), top=5000, bottom=-1000, sea=0)
        lander = generators.SimpleLandGenerator(face, age)
        dweller = generators.CommonSenseDwellinger(face, globalPopulation=oikumenaPopulation)
        capitaler = generators.SearchGoodPlaceToCapital(face, age, playersIDs)
        officier = generators.LordCourt(face)
        explorer = generators.InfinityAbsorbation(face, playersIDs)
        historic = generators.IntegrationRegions(face)
        culture = generators.WarAndPease(face, age)

        self.generator = generators.MapGenerator(terrain, lander, capitaler, dweller, officier, explorer, historic, culture)

class Fantasy(AbstractGeneratorFacade):
    """ Like a fantasy map: domains for whole landscapes like forest, mountain chain and other. """
    def __init__(self, face, playersIDs, age=generators.Age.Iron, regionsLimit=0):
        AbstractGeneratorFacade.__init__(self, face, playersIDs, regionsLimit, age)
        print("Regions limit", regionsLimit, self.regions)
        oikumenaPopulation = face*face*100
        # Layers
        terrain = generators.PikesAndPlatos(face, top=5000, bottom=-500, mounts=face)
        lander = generators.ExtensibleAreas(face, landscapes=self.landings)
        #lander = generators.PlanetEvo(face, age, landscapes=self.landings, envUpdateCircle=10)
        dweller = generators.StateCities(face, oikumenaPopulation)
        capitaler = generators.DistancedCapitals(face, playersIDs, self.regions)
        officier = generators.Guards(face)
        explorer = generators.SpeciesArials(face)
        historic = generators.NoDomainHistory(face)
        culture = generators.WarAndPease(face, age=age)

        self.generator = generators.MapGenerator(terrain, lander, capitaler, dweller, officier, explorer, historic, culture)

class Balanced(AbstractGeneratorFacade):
    """ Balanced map with constantable towns and small domains"""

    def __init__(self, face, playersIDs, age=generators.Age.Iron, regionsLimit=0):
        AbstractGeneratorFacade.__init__(self, face, playersIDs, regionsLimit, age)
        oikumenaPopulation = face * face * int(math.sqrt(face))

        bases = list([0, face*face - 1, face*(face - 1) - 1, face - 1])
        odd = face % 2 == 1
        bases.extend([face//2, face*face - face//2, (face*face + face)//2 if odd else face*(face + 1)//2 - 1, (face*face - face)//2 if odd else face*face//2 - 1])

        terrain = generators.VoolcanoLake(face, top=500, bottom=-500)
        lander = generators.SimpleLandGenerator(face, age)
        capitaler = generators.ConstantableCapitals(face, playerIDs, bases)
        dweller = generators.EvolutionRandomHomo(face, oikumenaPopulation)
        officier = generators.LordCourt(face)
        explorer = generators.NearestVecine(face)
        historic = generators.NoDomainHistory(face)
        culture = generators.FamilyCastles(face)

        self.generator = generators.MapGenerator(terrain, lander, capitaler, dweller, officier, explorer, historic, culture)
