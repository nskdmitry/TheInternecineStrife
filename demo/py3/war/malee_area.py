import demo.core.dataset as dataset
import demo.core.display as display
from demo.core.display import tk, ttk, _, battle

class MainWindow(display.MainWindow):
    def __init__(self, profile=dataset.warriors[0], form=dataset.formations[0]):
        display.MainWindow.__init__(self, title=_("Formation train a malee attack"))
        self.warprof = profile
        self.amount = 500
        self.formation = form
        self.division = battle.Divizion(1, line=battle.Line.CENTER, soldprof=profile], force=self.amount, formation=form)

    def initInformPanel(self, panel):
        tk.Label(master=panel, text=_("Soldier's amount"))
