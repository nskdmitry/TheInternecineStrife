import argparse
import feodal.feods as feods
import mapgenrandom as pattern

def console():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--source', default='test')
    parser.add_argument('-p', '--path', default='out')
    parser.add_argument('-d', '--dest', default='copy')
    return parser

if __name__ == "__main__":
    parser = console()
    args = parser.parse_args()

    packet = feods.load(args.source, args.path)
    print(packet['meta']['Title'], "{0}x{0}".format(packet['meta']['Face']))
    #template = pattern.unpack(packet, args.path)
    #feods.save(template, args.dest, args.path)
