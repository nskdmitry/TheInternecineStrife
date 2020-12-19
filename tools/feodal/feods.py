import glob
import json
import tarfile
import os, sys
import math
#import MapTemplate as MT
import datetime
import time

if sys.hexversion < 0x030100F0:
    import lands
else:
    from feodal import lands

LAYERS = ['terrain', 'environments', 'landscape', 'buildings', 'dwellings', 'castles', 'populations', 'domains', 'armies', 'control', 'marks', 'commerce']


maskBox = "{}/{}.worldbox"
maskMap = "{}/{}.feods"
maskJson = "{}/{}.json"
maskLayer = "{}/{}.layer"

def load(mapName, path='.', temp='.'):
    """
    Load a Feudal World Engine (The Internecine Strife Game) map from *.feods file (layered map)
    """

    global LAYERS
    global maskJson
    global maskLayer

    packet = {'layers': {}}

    # Full name of path to map archive file
    map_name = mapName.replace('.feods', '')
    print("{} is set. {} is find".format(mapName, map_name))
    dirPath = os.path.join(path, map_name + '.feods')
    if not os.path.dirname(dirPath):
        os.mkdir(dirPath)
    # Extract all files to temporary folder
    directory = '.'
    print(dirPath + " open")
    with tarfile.open(dirPath, 'r:gz') as arch:
        directory = temp# os.path.join(temp, mapName)
        arch.extractall(directory)
        arch.close()
    # Parse JSON files to data of map
    fname = maskJson.format(os.path.join(temp, mapName), 'meta')
    if not os.path.exists(fname):
        raise Exception("Metadata of map is not exists. File is defected.")
    with open(fname, 'r') as source:
        packet['meta'] = json.load(source)
    for info in ['landscape', 'domains', 'marks', 'dwellings']:
        fname = maskJson.format(os.path.join(temp, mapName, 'entities'), info)
        if not os.path.exists(fname):
            continue
        with open(fname, 'r') as source:
            packet[info] = json.load(source)
    # Landscape set of map can will basis. Map contains landset is not necessarily.
    if len(packet['landscape']) == 0:
        packet['landscape'] = lands.lands
    # Parse each layer (matrix of float values)
    for layer in LAYERS:
        block = loadLayer(mapName, layer, path=temp)
        if block is None:
            continue
        packet['layers'][layer] = block
    if 'dwellings' not in packet['layers']:
        packet['layers']['dwellings'] = packet['layers']['buildings']
    # Add edition time
    packet['meta']['Edition'] = time.ctime(os.path.getatime(dirPath))
    # Return a hash-table with full information
    return packet

def loadTemplate(patternName, path='.', temp='.'):
    """
    Load a Feudal World Engine (The Internecine Strife Game) pattern of maps from *.worldbox file
    """
    global maskBox
    global maskJson
    global maskLayer
    packet = {'meta': {}, 'layers': [], 'areas': []}

    # Extract all information files from compressed folder
    dirPath = os.path.join(path, patternName + '.worldbox')
    if not os.path.dirname(dirPath):
        os.mkdir(dirPath)
    directory = '.'
    with tarfile.open(dirPath, 'r:gz') as arch:
        directory = dirPath.replace('.worldbox', '')
        arch.extractall(directory)
        arch.close()
    # Parse JSON files to data of map
    for info in ['meta', 'areas', 'landscapes']:
        fname = maskJson.format(path, patternName, info)
        with open(fname, 'r') as source:
            packet[info] = json.load(source)

    #setters
    def setLandscape(place, area):
        place.lands = area.id
    setTerra = lambda place, area: place.terra.append(area.id)
    setEnvironment = lambda place, area: place.envir.append(area.id)
    setPeasants = lambda place, area: place.popul.append(area.id)
    setCapitals = lambda place, area: place.capit.append(area.id)
    setDomain = lambda place, area: place.polit.append(area.id)
    setHobbitable = lambda place, area: place.polit.append(area.id)

    # Init areas and cells/layers
    areals = [MT.MapGenArea(pack['type'], pack['value'], pack['id']) for pack in packet['areas']]
    sorted(areals, key=lambda package: package['id'])
    cells = [MT.MapGenCellLayers() for values in range(packet['meta']['Face'] * packet['meta']['Face'])]

    # Parse Areas
    for arealID in glob.glob(os.path.join(directory, 'areas')):
        area = areals[int(arealID)-1]
        if area.type == MapGenAreaType.TERRA:
            make = setTerra
        elif area.type == MapGenAreaType.ENVIR:
            make = setEnvironment
        elif area.type == MapGenAreaType.POPUL:
            make = setPeasants
        elif area.type == MapGenAreaType.CAPIT:
            make = setCapitals
        elif area.type == MapGenAreaType.POLIT:
            make = setDomain
        elif area.type == MapGenAreaType.CIVIL:
            make = setHobbitable
        else:
            make = setLandscape

        mapping = loadAreal(mapName, arealID, path=path)
        for no in range(0, len(mapping-1)):
            if mapping[no] > 0:
                make(cells[no], area)
    packet['layers'] = cells
    packet['areas'] = areals
    return packet

def save(mapBox, fileName=None, path='.', temp='.', bg=False):
    """
    Save a Feudal World Engine (The Internecine Strife Game) map as *.feods file (layered map)
    """
    global maskJson
    global maskLayer

    fileName = mapBox.meta.get('Name', 'new_' + datetime.date.today()) if fileName == None else fileName
    dirPath = os.path.join(temp, fileName)
    layersPath = os.path.join(dirPath, 'layers')
    entityPath = os.path.join(dirPath, 'entities')
    filePath = os.path.join(path, fileName)
    #print("feods.save():  {0} and pack to {1}".format(dirPath, filePath))
    if not os.path.exists(dirPath):
        os.mkdir(dirPath)
    if not os.path.exists(layersPath):
        os.mkdir(layersPath)
    if not os.path.exists(entityPath):
        os.mkdir(entityPath)

    print("Make storable files")
    scapes = {scape['ID']: scape for scape in mapBox.landscapes}
    inform = zip(['landscape', 'domains', 'marks', 'dwellings'], [scapes if len(scapes) > 0 else lands.lands, mapBox.domains, mapBox.marks, mapBox.dwellings])

    # Meta will store in root of archive.
    fname = maskJson.format(dirPath, 'meta')
    with open(fname, "w+") as stock:
        json.dump(mapBox.meta, stock)
    # Entities will store in 'entities' sub-directory
    for infoBlock, block in inform:
        fname = maskJson.format(entityPath, infoBlock)
        #print("... ... {0} to {1}".format(infoBlock, fname))
        with open(fname, "w+") as stock:
            json.dump(block, stock)
    # Layers will store in 'layers' sub-directory
    for layerName, layer in mapBox.layers.iteritems():
        #print("... ... {}".format(layerName))
        saveLayer(layerName, layer, lineLength=mapBox.face, path=layersPath)

    print("Pack files into compressed archive file (*.feods) (folder: {})".format(temp))
    packAsFeods(fileName, path=path, folder=dirPath)
    return True

def saveTemplate(patternBox, fileName=None, path='.', temp='.'):
    """
    Save a Feudal World Engine (The Internecine Strife Game) map's pattern as *.worldbox file
    """
    global maskJson
    global maskLayer

    fileName = patternBox['meta']['Name'] if fileName else fileName
    dirPath = os.path.join(temp, fileName)
    filePath = os.path.join(path, fileName)
    print("feods.saveTemplate(): {0} and pack to {1}".format(dirPath, filePath))
    if not os.path.exists(dirPath):
        os.mkdir(dirPath)

    print("Save in folder")
    scapes = {scape['Name']: scape for scape in patternBox['landscapes']}
    patternBox['landscapes'] = scapes
    for infoBlock in ['meta', 'landscapes' 'areas']:
        block = patternBox[infoBlock]
        fname = maskJson.format(temp, fileName, infoBlock)
        print("... ... {0} to {1}".format(infoBlock, fname))
        with open(fname, "w+") as stock:
            json.dump(block, stock)

    for layer in patternBox['layers']:
        blocks = []


    print("Pack files into compressed archive (*.worldbox)")

    return False

def saveAsTemplate(templateBox, fileName=None, temp='.'):
    """
    Save as Feudal World Engine (The Internecine Strife Game) map template as *.worldbox file
    """

    global maskJson
    global maskLayer

    fileName = templateBox.meta['name'] if fileName == None else fileName
    dirPath = os.path.join(temp, fileName)
    filePath = os.path.join(path, fileName)
    print("feods.saveAsTemplate(): {0} and pack to {1}".format(dirPath, filePath))

    print("... make")
    scapes = {scape['Name']: scape for scape in mapBox.scapes}
    inform = zip(['meta', 'landscape', 'domains'], [mapBox.meta, scapes if len(scapes) > 0 else lands.lands, mapBox.domains])
    for infoBlock, block in inform:
        fname = maskJson.format(temp, fileName, infoBlock)
        print("... ... {0} to {1}".format(infoBlock, fname))
        with open(fname, "w+") as stock:
            json.dump(block, stock)

    for layerName in ['environment', 'population', 'armies', 'civilization', 'capitals']:
        layer = mapBox.map_layers[layerName]
        saveLayer(fileName, layerName, layer, lineLength=mapBox.face, path=temp)

    print("... pack")
    packAsWorldbox(fileName, path=path, folder=temp)
    return True

def packAsFeods(mapName, path='.', folder='.'):
    global maskMap
    farch = maskMap.format(path, mapName)
    packArchive(folder, farch)

def packAsWorldbox(boxName, path='.', folder='.'):
    global maskBox
    farch = maskBox.format(path, boxName)
    packArchive(folder, farch)

def packArchive(folder, archiveFile):
    content = "{}/*".format(folder)
    with tarfile.open(archiveFile, 'w:gz') as arch:
        files = glob.glob(content)
        for filename in files:
            shortPath = os.path.join(os.path.basename(os.path.dirname(filename)), os.path.basename(filename))
            arch.add(filename, arcname=shortPath)
        arch.close()

def saveLayer(layerName, layer, lineLength=None, path='.'):
    global maskLayer
    lineLength = lineLength if lineLength != None else len(layer)
    with open(maskLayer.format(path, layerName), "w+") as block:
        rows = chunks(layer, lineLength)
        pattern = "{: 05d}" if type(layer[0]) == type(1) else "{: 07.3f}"
        lines = [",".join([pattern.format(val) for val in row]) for row in rows]
        block.write(",\n".join(line for line in lines))
        block.close()

def loadLayer(mapName, layerName, path='.'):
    global maskLayer
    path = maskLayer.format(os.path.join(path, mapName, 'layers'), layerName)
    if not os.path.exists(path):
        return None
    with open(path, "r") as block:
        serial = "".join(block.readlines())
        block.close()
    return [float(val) if round(float(val),0) != float(val) else int(val) for val in serial.split(',')]

def saveAreal(mapName, arealID, path='.'):
    global maskLayer
    pass

def loadAreal(mapName, arealID, path='.'):
    global maskLayer
    with open(maskLayer.format(path, mapName, arealID), "r") as block:
        serial = "".join(block.readlines())
        block.close()
    return [int(val) for val in serial]

def chunks(array, face):
    return [array[i:i+face] for i in xrange(0, len(array), face)]

if __name__ == '__main__':
    pass
