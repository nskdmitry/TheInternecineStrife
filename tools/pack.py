import argparse
import os
import feodal.feods as feods
from feodal.tools import Picturization

def console():
    parser = argparse.ArgumentParser(description="Repacker a opened map files to archive.")
    parser.add_argument('name', metavar='N', help="File name without extension like 'Fantasion' or 'KingOfTheHill'.")
    parser.add_argument('-a', '--asset', default=None, help="Subdirectory of assets/maps (asset) for saving a file")
    parser.add_argument('-e', '--extension', choices=['feods', 'worldbox'], default='feods', help="Type of file: map (feods) or map template (worldbox)")
    return parser.parse_args()

if __name__ == "__main__":
    args = console()
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    source = os.path.join(root, 'data', 'state', 'maps.open', args.name)
    dest = os.path.join(root, 'data', 'assets', 'patterns' if args.extension == 'worldbox' else 'maps')
    if args.asset is not None:
        dest = os.path.join(dest, args.asset)
    dest = os.path.join(dest, "{}.{}".format(args.name, args.extension))
    print("Pack {} to {}".format(source, dest))

    feods.packArchive(folder=source, archiveFile=dest)
