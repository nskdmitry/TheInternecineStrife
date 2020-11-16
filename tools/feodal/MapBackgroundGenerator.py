import os
import png
from feodal import pngs
import numpy as np
from scipy.ndimage.filters import gaussian_filter
from scipy.ndimage.filters import median_filter
import scipy

class InvalidIndex(IndexError):
    def __init__(self, message, index, collection):
        self.message = message
        self.index = index
        self.collection = collection

# Stages

def getExtremusMap(heightsMap, face, ppc = 10):
    centerCells = getExtremumCenters(face, ppc)
    centers = { {centerCells[i]: heightsMap[i]} for i in range(0, len(heightsMap))}
    return centers

def colorize(image, pallette):
    face = len(image)
    def getColor(i, j):
        inx = int(image[j][i])
        if inx >= len(pallette):
            return (0, 0, 0)
            raise InvalidIndex("Index {} is outbounded".format(inx), inx, pallette)
        return pallette[ inx ]
    return [[getColor(i, j) for i in range(0, face)] for j in range(0, face)]

def grayscaling(layer, low, high):
    scale = float(255 / abs(high - low if high > low else 1))
    return [int(val * scale) for val in layer]

def packLayer(layer, side):
    image = np.array(layer)
    return np.reshape(image, (side, -1))

def _zoom(source, face, ppc=10):
    base = np.reshape(np.array(source), (face, face))
    shape = (ppc, ppc)
    scale = np.ones(shape)
    return np.kron(base, scale)

def _blur(source, sigma=2):
    image = np.array(source)
    return gaussian_filter(image, 0.5*sigma)
    return median_filter(image, sigma)

# Save

def savePNG(filename, data, side):
    with open(filename, 'wb') as dest:
        w = png.Writer(width=side, height=side, greyscale=False)
        w.write(dest, data)

def saveGray(filename, data, side, depth=8):
    picture = pngs.makeGrayPNG(data, width=side, height=side)
    with open(filename, 'wb') as dest:
        dest.write(picture)
        #w = png.Writer(width=side, height=side, greyscale=True, bitdepth=depth)
        #w.write(dest, data)

def toLine(data, side):
    def lineze(row):
        immedited = []
        for pixel in row:
            immedited.append(pixel[0])
            immedited.append(pixel[1])
            immedited.append(pixel[2] if len(pixel) > 2 else 0)
        return immedited

    return [lineze(row) for row in data]

if __name__ == '__main__':
    print('Hello?')
    pass
