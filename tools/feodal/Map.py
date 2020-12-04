from tools import Tools
import pathfinding

class Map:
    def __init__(self, package=None, generator=None):
        self.meta = {'Title': None}
        self.domains = []
        self.generator = generator if generator is None else (package['meta'].get("Generator", "Classic") if package is not None else "Classic")
        self.landscapes = {}
        self.nodes = []
        self.roads = []
        self.layers = []
        self.dwells = []
        if package != None:
            self.unpack(package)

    def rehead(self, packet):
        self.meta = packet
        self.name = packet['Title']
        self.face = packet['Face']
        self.size = self.face * self.face
        self.top = packet['Top']
        self.bottom = packet['Bottom']
        self.sealev = packet['SeaLevel']
        if 'Edition' in packet:
            self.edition = packet['Edition']

    def unpack(self, packet):
        self.rehead(packet['meta'])
        self.landscapes = packet['landscape']
        self.layers = packet['layers']
        self.domains = packet['domains']
        self.marks = packet['marks']
        try:
            self.dwellings = packet.get('buildings', packet.get('dwellings', []))
        except:
            print(packet.keys())
            raise

        heights = self.layers['terrain']
        landscape = self.layers['landscape']
        civil = self.layers['populations']
        force = self.layers['armies']
        domains = self.layers['domains']

        scapes = self.landscapes
        if type(self.landscapes) == type(dict({})):
            scapes = [self.landscapes[scape] for scape in self.landscapes]
        self.tools = Tools(self.face, scapes)
        self.cells = [self.tools.cell(i+1, heights[i], landscape[i], civil[i], force[i], domains[i]) for i in range(0, self.size-1)]

    def pack(self):
        pass

    def makeRoads(self, restrictor = 0):
        """ Generate a roads graph """
        fairs = self.layers['commerce']
        # Get nodes of Graph
        self.nodes = [cell for cell in range(0, self.size) if fairs[i] > 0]
        # Prepare data
        count = len(self.nodes)
        distances = [[self.tools.dd(self.nodes[i], self.nodes[j]) for i in range(0, count) if i != j] for j in range(0, count)]
        nearest = [min(distances[i]) for i in range(0, count)]
        nearTo = [[j for j in range(0, count - 1) if distances[i][j] == nearest[i]] for i in range(0, count)]
        linkedFor = [0 for i in range(0, count)]
        linkedLeft = count
        # Restriction of Graph rebuilding circles count.
        if restrictor < 1:
            restrictor = self.face // 2
        # Make arcs (roads) of Graph
        while linkedLeft > 0:
            for i in range(0, count):
                if linkedFor[i] > 0:
                    continue
                if len(nearTo[i]) == 1:
                    j = nearTo[i][0]
                    no = j if j < i else j + 1
                    if linkedFor[no] > 0 and restrictor > 0:
                        # All leafs should be linket at first stage
                        linkedFor = [0 for i in range(0, count)]
                        self.roads = []
                        restrictor = restrictor - 1
                        break
                else:
                    j = self.tools.rand.choice(nearTo[i])
                    no = j if j < i else j + 1
                    if linkedFor[no] > 0 and restrictor > 0:
                        continue
                self.roads.append(self.road(i, no, cost=distances[i][no]))
                linkedLeft = linkedLeft - 1
        return self.roads


    def getIdRoad(self, idFrom, idTo):
        return max([idFrom, idTo]) + self.face * min([idFrom, idTo])

    def road(self, idFrom, idTo, cost=1):
        return (self.getIdRoad(idFrom, idTo), idFrom, idTo, cost)
