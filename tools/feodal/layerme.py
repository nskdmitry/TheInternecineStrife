import generators, tools
import argparse
import os.path as p

def console():
    args = argparse.ArgumentParser(description="Test a generator")
    args.add_argument("-f", "--face", default=20, type=int, help="Side of map in cells")
    args.add_argument("-s", "--surface", default=200, type=int, help="Basic height of ground surface")
    args.add_argument("-p", "--power", default=500, type=int, help="How much deeper bomb make crater?")
    args.add_argument("-r", "--radius", default=3, type=int, help="How wide crater be maked by bomb?")
    return args.parse_args()

if __name__ == '__main__':
    args = console()
    count = 10
    generator = generators.Bombing(args.face, start=args.surface, power=args.power, radius=args.radius, bombs=count)
    toolset = tools.Tools(args.face, [])
    print(min(generator.latest))
    layer = generator.generate(toolset)
    fname = p.abspath(p.join(p.dirname(__file__), 'test', 'bombed.layer'))
    generator.output(fname, layer)
    print("OK. See {}".format(fname))
