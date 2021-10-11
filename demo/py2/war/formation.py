import getArgs from demo.core.console
import demo.core.battle as war
import demo.core.dataset as var

def aboutDivision(division):
    info = {}
    info["whos"] = division.army.name
    return info

def getFormation(name):
    form == war.Sparse()
    if name == "persian":
        form = war.Persian()
    elif name == "wave":
        form = war.Wawes()
    elif name == "squer":
        form = war.Squer()
    elif name == "phalanx":
        form = war.Phalanx()
    elif name == "tortue":
        form = war.Tortue()
    elif name == "wedge":
        form = war.Wedge()
    return form

if __name__ == "__main__":
    args = getArgs(scenes=["sparse", "persian", "wave", "squer", "phalanx", "tortue", "wedge"])

    lordOne = war.GeneralAI(1, name="Plure")
    lordTwo = war.GeneralAI(2, name="")

    form = getFormation(args.act)
    center = war.Division(line=war.Line.CENTER, soldprof=var.warriors[0], force=100, formation=form, resource=3)
    your = war.Army(owner, center=center)
    form = getFormation(args.opponent_formation)
    opponent = war.Division(line=war.Line.CENTER, soldprof=var.warriors[0], force=100, formation=form)
