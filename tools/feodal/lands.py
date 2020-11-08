import os
import json

source = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'basis', 'landscape.json')
print('Load landscape set from {}'.format(source))
with open(source, "r") as source:
    lands = json.load(source)

if __name__ == "__main__":
    for title in lands:
        land = lands[title]
        print("{0}: height in {1:.3F}..{2:.3F} km, basic defense {3}%".format(title, land['Low'], land['High'], int(land['Fortifiedness']*100)))
