import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import gui.dialogs as dialogs

class DomainInfoWindow(dialogs.Dialog):
    def __init__(self, mapBox, domain={}, parent=None):
        dialogs.Dialog.__init__(self, parent if parent is not None else tk.Tk())
        self.info = domain
        self.landscapes = [mapBox.landscapes[item] for item in mapBox.landscapes] if type(mapBox.landscapes) == type({'a': 1}) else mapBox.landscapes
        sorted(self.landscapes, key=lambda item: item['ID'])
        face = mapBox.face
        positionRight = int(self.winfo_screenwidth()/2 - 225)
        positionDown = int(self.winfo_screenheight()/2 - 60)

        def isAvailableCell(no, owned=True):
            region = mapBox.layers['domains'][no]
            envir = mapBox.layers['environments'][no]
            return ((owned and region == domain['id']) or (not owned and region == 0)) and (envir == Environments.Earth or envir == Environments.Port)
        def makeCellName(place):
            no = place[2]
            return "[{}, {}] ({} man)".format(place[0], place[1], mapBox.layers['populations'][no])

        self.title("Domain {} show and edit".format(domain.get('name', 'New')))
        self.geometry("450x120+{}+{}".format(positionRight, positionDown))
        domaindedCells = [i for i in range(0, face*face) if isAvailableCell(i)]
        if len(domaindedCells) == 0:
            self.availableCapitals = [(i % face, i // face, i) for i in range(0, face*face) if isAvailableCell(i, False)]
        else:
            self.availableCapitals = [(i % face, i // face, i) for i in domaindedCells]
        self.availableLords = ["(Free land)"] + ["Lord No" + str(i) for i in range(1, mapBox.meta['PlayersLimit']+1)]
        self.cells = {place[2]: makeCellName(place) for place in self.availableCapitals}

        self.ID = tk.StringVar(value=str(domain.get('id', 1)))
        self.Name = tk.StringVar(value=domain.get('name', 'Domain #{}'.format(domain.get('id', 1))))
        self.Capital = tk.IntVar(value=domain.get('capital', self.availableCapitals[0]))

        tk.Label(self, textvariable=self.ID).grid(column=0, row=0)
        tk.Entry(self, textvariable=self.Name).grid(column=1, row=0)
        tk.Label(self, text="Owner lord").grid(column=0, row=1)
        self.lordsList = ttk.Combobox(self, values=self.availableLords)
        currLord = domain.get('owner', -1)
        if currLord > -1:
            self.lordsList.current(currLord)
        self.lordsList.grid(column=1, row=1)
        tk.Label(self, text="Capital cell").grid(column=0, row=2)
        self.capitalsList = ttk.Combobox(self, values=self.cells.values())
        self.capitalsList.bind("<<ComboboxSelected>>", lambda ev: self.setCapital(ev))
        currCapital = domain.get('capital', -1)
        if currCapital > -1 and currCapital in self.cells:
            self.capitalsList.current(currCapital)
        self.capitalsList.grid(column=1, row=2)
        tk.Button(self, text="Accept", command=self.accept).grid(column=2, row=3)
        tk.Button(self, text="Cancel", command=self.cancel).grid(column=3, row=3)

        if parent is None:
            self.master.mainloop()
        self.master.update()

    def setCapital(self, ev):
        no = self.capitalsList.current()
        self.Capital.set(no)
    def accept(self):
        self.saveConfiguration()
        self.exit()
    def cancel(self):
        self.exit()

    def saveConfiguration(self):
        self.info['id'] = int(self.ID.get())
        self.info['name'] = self.Name.get()
        noCapital = self.Capital.get()
        self.info['capital'] = self.cells.keys()[noCapital]
        self.info['owner'] = self.lordsList.current()
        return self.info
