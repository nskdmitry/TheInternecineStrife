"""
Script make a new Map Pattern by exists Map.
Author: Mironenko Dmitry, 2020 (c).
License: FTUM (free-to-using-and-modificate).

All functions/classes of generation and read/write map and about files declared in feodal package.
__main__ function is successfull generator of maps as clear and with template.
MapGenerator class is framework of generator, see \"typical\" package.

Functions:
    console() - is parser of command-line arguments.
"""

import os
import sys
import argparse

#from feodal.lands import lands
#import feodal.constants as constants
import feodal.feods as feods
#import feodal.MapBackgroundGenerator as mbg
#import feodal.typical as typical
import feodal.MapTemplate as mt
import feodal.Map as World
#from feodal.tools import Tools, Picturization

reload(sys)
sys.setdefaultencoding('utf8')

tools = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(tools)

def console():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--name', help="Title of Patterm")
    parser.add_argument('-s', '--source', help="Name of Map (*.feods) file as source of pattern.")
    parser.add_argument('-d', '--dest', help="Name of new Pattern (*.worldbox) file.")
    return parser.parse_args()

if __name__ == '__main__':
    args = console()
    sourceDiretory = os.path.join(root, 'data', 'assests', 'maps')
    destFilePath = os.path.join(root, 'data', 'assest', 'patterns')
    tempDirectory = os.path.join(root, 'data', 'state', 'maps.open')

    package = feods.load(args.source, path='random', sourceDiretory)
    world = World.Map(package)
    template = mt.MapTemplate(parser.name, world.landscapes)
    template.createFromMap(world)
