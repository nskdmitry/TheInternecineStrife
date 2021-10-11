import argparse, os, json, base64, numpy, pprint, sys
mod_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, mod_path)
import core.dataset as dataset
import core.battle as war
import core.world as world

def console():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=str, default=os.path.join(os.path.dirname(__file__), "battle.fwbattle"), help="Path to .FWBATTLE file with current state of battle or seige.")
    parser.add_argument("-o", "--output", type=str, default=None, help="Path of .FWBATTLE what be contain a new state of battle or seige + history.")
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
    fname = args.output or args.input

    circle = 0
    place = world.Cell(dataset.landscapes[0])
    your = war.Army(owner=war.GeneralAI(1, name="Markus"), center=war.Division(line=war.Line.CENTER, soldprof=dataset.warriors[-2], force=120, formation=dataset.formations[4]))
    your.machines.profile = dataset.mashines[1]
    your.machines.amount = 1
    enemy = war.Army(owner=war.Woodwoman(2, name="Boudicca"), center=war.Division(line=war.Line.CENTER, soldprof=dataset.warriors[-1], force=150, formation=dataset.formations[3]))
    enemy.machines.profile = dataset.mashines[3]
    enemy.machines.amount = 1
    fight = war.Battle(your, enemy, circle, place)
    # One cicle of fight
    far = enemy.center
    near = your.center
    war.history.info("Defenders ({}): {} of {} as {} {}x{} + {}.".format(id(far), far.amount, far.profile.name, far._formation['class'].name, far._formation['columns'], far._formation['rows'], far.tail))
    war.history.info("Attackers ({}): {} of {} as {} {}x{} + {}.".format(id(near), near.amount, near.profile.name, near._formation['class'].name, near._formation['columns'], near._formation['rows'], near.tail))
    try:
        while duration - 0.00 > 0.00:
            fight.play(longtime=1.0)
            duration -= 1.0
    except war.BattleEnded as e:
        print(e.message)
    fight.history("Stop battle modulation.")
    war.history.info("")
    content = json.dumps(fight.frames, cls=war.BattleEncoder, indent=5)

    result = {'time': "{} days {} minutes".format(fight.day, fight.time), 'attackers': fight.nearside, 'defenders': fight.farside, 'generals': {fight.farside.general.name: fight.farside.general, fight.nearside.general.name: fight.nearside.general}}
    #print(json.dumps(result, cls=war.BattleEncoder, indent=5))
    with open(fname, "w") as fp:
        json.dump(fight, fp, cls=war.BattleEncoder)
    #print(content)
    print("Ok. see hystory.log")
