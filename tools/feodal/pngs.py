#! /usr/bin/python
import zlib
import struct

def I1(value, scale=255):
    value = value if isinstance(value, int) else int(value * scale)
    return struct.pack("!B", int(value) & (2**8-1))
def I4(value):
    value = value if isinstance(value, int) else int(value)
    return struct.pack("!I", value & (2**32-1))
def RGBA(r, g, b, a=0):
    dword = 2**32-1
    return struct.pack("!I", (r * (2**24)) & dword + (g * (2**16)) & dword + (b * (2**8)) & dword + a & dword)

""" Converts a list of list into gray-scale PNG image. """
__copyright__ = "Copyright (C) 2014 Guido Draheim"
__licence__ = "Public Domain"
def makeGrayPNG(data, height = None, width = None):
    # compute width&height from data if not explicit
    if height is None:
        height = len(data) # rows
    if width is None:
        width = 0
        for row in data:
            if width < len(row):
                width = len(row)
    # generate these chunks depending on image type
    makeIHDR = True
    makeIDAT = True
    makeIEND = True
    png = b"\x89" + "PNG\r\n\x1A\n".encode('ascii')
    if makeIHDR:
        colortype = 0 # true gray image (no palette)
        bitdepth = 8 # with one byte per pixel (0..255)
        compression = 0 # zlib (no choice here)
        filtertype = 0 # adaptive (each scanline seperately)
        interlaced = 0 # no
        IHDR = I4(width) + I4(height) + I1(bitdepth)
        IHDR += I1(colortype) + I1(compression)
        IHDR += I1(filtertype) + I1(interlaced)
        block = "IHDR".encode('ascii') + IHDR
        png += I4(len(IHDR)) + block + I4(zlib.crc32(block))
    if makeIDAT:
        raw = b""
        for y in xrange(height):
            raw += b"\0" # no filter for this scanline
            for x in xrange(width):
                c = b"\0" # default black pixel
                if y < len(data) and x < len(data[y]):
                    c = I1(data[y][x])
                raw += c
        compressor = zlib.compressobj()
        compressed = compressor.compress(raw)
        compressed += compressor.flush() #!!
        block = "IDAT".encode('ascii') + compressed
        png += I4(len(compressed)) + block + I4(zlib.crc32(block))
    if makeIEND:
        block = "IEND".encode('ascii')
        png += I4(0) + block + I4(zlib.crc32(block))
    return png

def makeColorPNG(data, height = None, width = None, opacity = 0):
    global ARGB
    # compute width&height from data if not explicit
    if height is None:
        height = len(data) # rows
    if width is None:
        width = 0
        for row in data:
            if width < len(row):
                width = len(row)
    # generate these chunks depending on image type
    makeIHDR = True
    makeIDAT = True
    makeIEND = True
    png = b"\x89" + "PNG\r\n\x1A\n".encode('ascii')
    if makeIHDR:
        colortype = 6 # true RGBA (no pallette)
        bitdepth = 32 # with four byte per pixel (AARRGGBB where AA, RR, GG, BB in 0..255 or 00h..FFh)
        compression = 0 # zlib (no choice here)
        filtertype = 0 # adaptive (each scanline seperately)
        interlaced = 0 # no
        IHDR = I4(width) + I4(height) + I1(bitdepth)
        IHDR += I1(colortype) + I1(compression)
        IHDR += I1(filtertype) + I1(interlaced)
        block = "IHDR".encode('ascii') + IHDR
        png += I4(len(IHDR)) + block + I4(zlib.crc32(block))
    if makeIDAT:
        raw = b""
        for y in xrange(height):
            raw += b"\0" # no filter for this scanline
            for x in xrange(width):
                c = b"\0" # default black pixel
                if y < len(data) and x < len(data[y]):
                    color = data[y][x]
                    alpha = opacity
                    c = RGBA(r=color[0], g=color[1], b=color[2], a=alpha)
                raw += c
        compressor = zlib.compressobj()
        compressed = compressor.compress(raw)
        compressed += compressor.flush() #!!
        block = "IDAT".encode('ascii') + compressed
        png += I4(len(compressed)) + block + I4(zlib.crc32(block))
    if makeIEND:
        block = "IEND".encode('ascii')
        png += I4(0) + block + I4(zlib.crc32(block))
    return png

def prepareGrayscaleImageBuffer(face, ppc = 10):
    return [[0 for j in xrange(face * ppc) ] for i in xrange(face * ppc) ]

def prepareRGBImageBuffer(face, ppc = 10):
    return [[(0, 0, 0) for j in xrange(face * ppc) ] for i in xrange(face * ppc) ]

def saveAsPNG(filename, rowsData, width, height, coder):
    width = width if width else len(rowsData[0])
    height = height if height else len(rowsData)
    with open(filename + '.png', 'wb') as f:
        f.write(coder(rowsData))

def rgb2hsb(color):
    mul = 255
    rgb = [component/mul for component in color]
    maxy = max(rgb)
    miny = min(rgb)
    scale = 60 / (maxy - miny)

    if maxy == miny:
        h = 0.0
    elif maxy == rgb[0] and rgb[1] >= rgb[2]:
        h = int(scale * (rgb[1] - rgb[2]))
    elif maxy == rgb[1]:
        h = int(scale * (rgb[2] - rgb[0]) + 120)
    elif maxy == rgb[2]:
        h = int(scale * (rgb[0] - rgb[2]))
    else:
        h = int(scale * (rgb[1] - rgb[2]) + 360)
    s = 0.0 if maxy == 0.0 else 1 - miny/maxy
    v = maxy

    return (h,s,v)

def hsb2rgb(color):
    scale = 255

    sector = int(color[0] / 60) % 6
    v = color[2]
    Vmin = (1 - color[1])*v
    a = (v - Vmin)*(color[0] % 60) / 60
    Vinc = Vmin + a
    Vdec = v - a
    if sector == 0:
        prev = (scale, Vinc, Vmin)
    elif sector == 1:
        prev = (Vdec, v, Vmin)
    elif sector == 2:
        prev = (Vmin, v, Vinc)
    elif sector == 3:
        prev = (Vmin, Vdec, v)
    elif sector == 4:
        prev = (Vinc, Vmin, v)
    else:
        prev = (v, Vmin, Vdec)
    return [component*scale for component in prev]

def dimming(color, lightValue):
    """
    Less the bright of pixel without rgb -> hsv -> rgb conversion
    """
    brightest = max(color)
    propotions = [component/brightest for component in color]
    mist = lightValue / 255
    return [int(mist*propotions[i]*color[i]) for i in xrange(3)]
