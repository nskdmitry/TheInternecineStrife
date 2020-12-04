"""
Script for generation randomized maps for (non-russian language) \"The Internecine Strife\".
Author: Mironenko Dmitry, 2020 (c).
License: FTUM (free-to-using-and-modificate).\n\n

All functions/classes of generation and read/write map and about files declared in feodal package.
__main__ function is successfull generator of maps as clear and with template.
MapGenerator class is framework of generator, see \"typical\" package.\n\n

Functions:
\n    console() - is parser of command-line arguments.
\n    generatePureRandom(args, root, toTemporary, generator) - make clear-new map.
"""

import os
import sys
import argparse

import feodal.constants as constants
import feodal.feods as feods
import feodal.MapBackgroundGenerator as mbg
import feodal.typical as typical
import feodal.Map as World
from feodal.tools import Tools, Picturization

tools = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(tools)

generators = {'Voolcano': typical.Voolcano, 'Classic': typical.Classic, 'Fantasy': typical.Fantasy, 'RandomicColonies': typical.RandomicColonies, "New": typical.New}
available = ", ".join(generators.keys())

def console():
    """ Get command line arguments. """
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('-n', '--name', default='Another random map', help='Title of map in list of availables maps')
    parser.add_argument('-s', '--face', default=10, type=int, help='Side length of map in cells')
    parser.add_argument('-t', '--top', default=2200, type=float, help='Highest place height under sea')
    parser.add_argument('-b', '--bottom', default=-100, type=float, help='Lowlest place height under/undo sea')
    parser.add_argument('-p', '--players', default=4, type=int, help='Count of high-level players (suzerines)')
    parser.add_argument('-l', '--level', default=constants.Age.Bronze, type=int, help='Stage of civilization development of all fractions')
    parser.add_argument('-r', '--regions', default=0, type=int, help='Count/limit of regions (feods, domains) | 0 - without limit')
    parser.add_argument('-f', '--file', default=None, help='Name of game map file without extension')
    parser.add_argument('-c', '--complex', default='Classic', help="Generator (facade) type: {}".format(available))
    parser.add_argument('-z', '--zoom', default=20, type=int, help="Scale of cell to rastr (pixels per cell)")
    parser.add_argument('-d', '--clear', default=False, type=bool, help="Delete temporary files and temporary folder after .feods file created.")
    return parser


def generatePureRandom(args, root, toTemporary, terra):
    terra.tuneTerrain(args.top, args.bottom, 0)
    rt = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    box = terra.generate(args.name, os.path.join(rt, toTemporary))
    return box

if __name__ == '__main__':
    toStore = os.path.join(root, 'data', 'assets', 'maps', 'random')
    toTemporary = os.path.join(root, 'data', 'state', 'maps.open')

    parser = console()
    args = parser.parse_args()
    idUsers = idUsers = [int(idstr) for idstr in range(0, args.players + 1)]

    generatorComplex = generators.get(args.complex, None)
    if generatorComplex is None:
        print("Map generation complex {} is not found. Please select one of ({}) or add new Generation Facade to 'typical.py' file and generators dictionary.".format(args.complex, available))
        sys.exit("Undefined generator")

    print(generatorComplex.__doc__)
    generator = generatorComplex(args.face, idUsers, age=args.level, regionsLimit=args.regions)
    terra = generatePureRandom(args, root, toTemporary, generator)

    fileName = args.file if args.file is not None else args.name
    world = World.Map(terra)
    # Make background images (photos of layers)
    imgRoot = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    visualer = Picturization(world)
    visualer.imagination(os.path.abspath(os.path.join(imgRoot, toTemporary, fileName)))
    #sys.exit("Debug stop")

    #print("Save map as {}/{}.feods".format(toStore, args.file))
    feods.save(world, fileName=fileName, path=toStore, temp=toTemporary)

    if args.clear:
        print("Clear map generation files cache")
        output = os.system("python {0}/clearCache.py".format(os.path.dirname(__file__)))
        print(output)
