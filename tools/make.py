import os
import sys
import argparse

from lands import lands
import feodal.feods
import MapTemplate as MT
import generators as Gen
import mapgenrandom as funcy


def console():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--pattern', default='HollowLand', help='Name of pattern file')
    parser.add_argument('-n', '--name', default='The Hollow Land', help='Title of map')
    parser.add_argument('-s', '--save', default='HollowLand', help='Name of genered map file')
    return parser

try:
    xrange
except Exception:
    xrange = range

if __name__ == '__main__':
    tools = os.path.dirname(__file__)
    root = os.path.dirname(tools)
    toLoad = os.path.join(root, 'data', 'assets', 'patterns')
    toStore = os.path.join(root, 'data', 'assets', 'maps', 'random')
    toTemporary = os.path.join(root, 'data', 'state', 'maps.open')

    parser = console()
    args = parser.parse_args()

    # Load a template
    package = feods.loadTemplate(args.pattern, toLoad, toStore)
    template = MT.MapTemplate(package['meta']['Name'], package['landscapes'], package['meta']['Face'], len(package['domains']))
    template.unpack(package)
    # Generate a map by template
    product = Gen.InfinityAbsorbation()
    mapBox = product.makeByTemplate(args.name, template, isClear=True)
    # Make package to write into *.feod file
    mapBox = product.new(name, playersNo)
    # Save
    funcy.saveAsMap(mapBox, args.file, toStore, toTemporary)
