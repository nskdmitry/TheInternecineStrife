from gui import main
from feodal import feods, Map

import sys
import os
import argparse
import json

tools = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(tools)

new = os.path.join(root, "data", "basis", "new.feods")

def console():
    parser = argparse.ArgumentParser(description="Map Editor of 'The Intenecine Strife' game (*.feods files)")
    parser.add_argument("action", metavar="A", type=str, choices=["open", "new"], default="new", help="Action by start of edit")
    parser.add_argument("-f", "--file", default=None, help="Name of feods usual placed file or path to custom-placed file. Name of new file else.")

    return parser.parse_args()

def openMap(url):
    global root
    fileName = url
    if not os.path.exists(fileName):
        fileName = os.path.join(root, 'data', 'assets', 'maps', url + ".feods")
        if not os.path.exists(fileName):
            fileName = os.path.join(root, 'data', 'assets', 'maps', "random", url + ".feods")
    if not os.path.exists(fileName):
        raise Exception("File {} is not found (latest {})".format(url, fileName))

    name = str(os.path.basename(fileName)).partition('.')[0]
    tmp = os.path.join(root, "data", "state", "maps.open")
    return feods.load(name, os.path.dirname(fileName), temp=tmp)

def create(name, config):
    global root
    global tools

    # Use script
    w = config["width"]
    t = config['top']
    b = config['bottom']
    p = config['players']
    a = config['age']
    r = config['regions']
    pattern = config['pattern']
    z = config['zoom']
    output = os.system("python {0}/new_map.py -n={1} -f={2} -s={3} -t={4} -b={5} -p={6} -l={7} -r={8} -c={9} -z={10}".format(tools, name, name, w, t, b, p, a, r, pattern, z))
    print(output)
    print("")
    # Load
    tmp = os.path.join(root, "data", "state", "maps.open", name)
    fileName = os.path.join(root, 'data', 'assets', 'maps', "random")
    return feods.load(name, path=fileName, temp=tmp)

if __name__ == "__main__":
    args = console()

    configProfile = os.path.join(tools, "data", "new.profile.json")
    with open(configProfile, 'r') as store:
        config = json.load(store)

    pallettesAddr = os.path.join(root, "data", "basis", "pallette.json")
    with open(pallettesAddr, 'r') as store:
        pallettes = json.load(store)

    if args.file is None:
        gamebox = openMap(new)
    else:
        gamebox = openMap(args.file) if args.action == "open" else create(args.file, config)
        gamebox['meta']['Edition'] = main.time.ctime(main.time.time())
    complect = Map.Map(gamebox, generator=(config['pattern'] if args.action == "new" else (gamebox.get("generator", "Classic") if gamebox is not None else "Classic")))
    name = str(os.path.basename(args.file)).partition('.')[0] if (args.file is not None) else "new"
    main = main.MainWindow(complect, rootFolder=os.path.join(root, "data", "state", "maps.open", name), basic=root, pallettes=pallettes, to_open=args.file is None)
