import argparse, os, json, base64, numpy, pprint, sys
if sys.hexversion >= 0x030100F0:
    import demo.core.dataset as dataset
    import demo.core.battle as war
    import demo.core.world as world
else:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
    print(sys.path[-1])
    from demo.core import dataset
    from demo.core import battle as war
    from demo.core import world

def console():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=str, default=os.path.join(os.path.dirname(__file__), "battle.fwbattle"), help="Path to .BATTLE file with current state of battle or seige.")
    parser.add_argument("-t", "--time", type=int, default=60, help="How long (min) battle will be calcs?")
    return parser.parse_args()

def loadState(filename):
    """ Load battle state from file. """
    content = numpy.loadtxt(fname=filename, dtype=str)
    serial = content#base64.b64decode(content)
    return json.loads(serial, encoding="UTF-8")

def saveState(state, filename):
    # Save battle state into file.
    serial = json.dumps(obj=state, encoding="UTF-8")
    content = serial#base64.b64encode(serial)
    numpy.savetxt(filename, content, ftm="%s")
    return True

def runBattle(state, endTime):
    time = state.day

if __name__ == "__main__":
    args = console()
    duration = args.time
    fname = args.input

    circle = 0
    place = world.Cell(dataset.landscapes[0])
    your = war.Army(owner=war.GeneralAI(1, name="human"), center=war.Division(line=war.Line.CENTER, soldprof=dataset.warriors[0], force=100, formation=dataset.formations[4]))
    your.machines.profile = dataset.mashines[1]
    your.machines.amount = 1
    enemy = war.Army(owner=war.GeneralAI(2, name="AI"), center=war.Division(line=war.Line.CENTER, soldprof=dataset.warriors[0], force=100, formation=dataset.formations[3]))
    enemy.machines.profile = dataset.mashines[3]
    enemy.machines.amount = 1
    fight = war.Battle(your, enemy, circle, place)
    # One cicle of fight
    try:
        while duration - 0.00 > 0.00:
            fight.play(longtime=1.0)
            duration -= 1.0
    except war.BattleEnded as e:
        print(e.message)
    content = json.dumps(fight.frames, cls=war.BattleEncoder, indent=5)

    result = {'time': "{} days {} minutes".format(fight.day, fight.time), 'attackers': fight.nearside, 'defenders': fight.farside, 'generals': {fight.farside.general.name: fight.farside.general, fight.nearside.general.name: fight.nearside.general}}
    print(json.dumps(result, cls=war.BattleEncoder, indent=5))
    with open(fname, "a+") as fp:
        json.dump(fight, fp, cls=war.BattleEncoder)
    print(content)
