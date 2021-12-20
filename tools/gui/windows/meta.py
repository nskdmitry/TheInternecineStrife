import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import new_map

class MetaWindow(tk.Toplevel):
    """ Show and modify a map options. """
    def __init__(self, meta, isNew = False, parent = None):
        tk.Toplevel.__init__(self, parent if parent is not None else tk.Tk())
        self.title(res.str_resources[47])
        self.meta = meta
        # Options of map
        face = meta.get('Face', 10)
        self.caption = tk.StringVar(value=meta.get('Title', ''))
        self.face = tk.StringVar(value=str(face))
        self.age = tk.IntVar(value=meta.get('Level', Age.Neolit))
        self.humanLimit = tk.StringVar(value=str(meta.get('PlayersLimit', 4)))
        self.top = tk.IntVar(value=meta.get('Top', 2000))
        self.bottom = tk.IntVar(value=meta.get('Bottom', -500))
        self.orientiers = tk.StringVar(value=str(meta.get('Extrems', meta.get('Face', 5) - 1)))
        self.population = tk.StringVar(value=str(meta.get('WholePopulation', 1000)))
        generators = new_map.generators.keys()
        actual = meta.get('Generator', 'New')
        self.generator = tk.IntVar(value=generators.index(actual))
        editable = "normal" if isNew else "disabled"
        self.meta['Generator'] = self.meta.get('Generator', 'New')
        self.meta['SeaLevel'] = self.meta.get('SeaLevel', 0)
        # Make a form
        self.title(res.str_resources[48].format(meta.get('Title', '')))
        positionRight = int(self.winfo_screenwidth()/2 - 200)
        positionDown = int(self.winfo_screenheight()/2 - 150)
        self.geometry("400x300+{}+{}".format(positionRight, positionDown))
        # Display
        tk.Label(self, text=res.str_resources[49]).grid(row=0, column=0)
        tk.Entry(self, textvariable=self.caption).grid(row=0, column=1)
        tk.Label(self, text=res.str_resources[50]).grid(row=1, column=0)
        tk.Label(self, textvariable=self.face).grid(row=1, column=1, sticky="W")
        tk.Label(self, text="x").grid(row=1, column=1)
        tk.Spinbox(self, textvariable=self.face, from_=2, to=999, increment=1, width=3, state=editable).grid(row=1, column=1, sticky="E")
        tk.Label(self, text=res.str_resources[51]).grid(row=2, column=0)
        tk.Spinbox(self, textvariable=self.humanLimit, from_=1, to=int(face*1.5), width=3, increment=1).grid(row=2, column=1)
        tk.Label(self, text=res.str_resources[52]).grid(row=3, column=0)
        ager = ttk.Combobox(self, values=[res.str_resources[58], res.str_resources[59], res.str_resources[60], res.str_resources[61], res.str_resources[62]], width=10)
        ager.bind("<<ComboboxSelected>>", lambda ev: self.updAge(ev))
        ager.current(self.age.get())
        ager.grid(row=3, column=1)
        tk.Label(self, text=res.str_resources[53]).grid(row=4, column=0, columnspan=2)
        self.more = tk.Scale(self, from_=-1000, to=self.top.get(), var=self.bottom, resolution=10, tickinterval=100, orient=tk.HORIZONTAL, command=self.updBottom)
        self.more.grid(row=5, column=0, sticky="WE")
        self.less = tk.Scale(self, from_=self.bottom.get(), to=5000, var=self.top, resolution=10, tickinterval=100, orient=tk.HORIZONTAL, command=self.updTop)
        self.less.grid(row=5, column=1, sticky="WE")
        tk.Label(self, text=res.str_resources[54]).grid(row=6, column=0)
        tk.Spinbox(self, textvariable=self.orientiers, from_=1, to=face*face//2, width=3, increment=1).grid(row=6, column=1)
        tk.Label(self, text=res.str_resources[55]).grid(row=7, column=0)
        self.pattern = ttk.Combobox(self, values=generators)
        self.pattern.bind("<<ComboboxSelected>>", lambda ev: self.updPattern())
        self.pattern.grid(row=7, column=1)
        tk.Button(self, text=res.str_resources[56], command=self.ok).grid(row=8, column=0)
        tk.Button(self, text=res.str_resources[57], command=self.exit).grid(row=8, column=1)
        # Initial a new map metadata
        if len(self.meta) == 0 or isNew:
            self.saveConfiguration()
        if parent is None:
            self.master.mainloop()

    def updAge(self, value): self.age.set(value)
    def updBottom(self, value): self.less.config(from_=value, to=5000)
    def updTop(self, value): self.more.config(from_=-1000, to=value)
    def updPattern(self): self.meta['Generator'] = self.pattern.current()
    def ok(self):
        self.saveConfiguration()
        self.exit()
    def exit(self):
        self.destroy()
        self.master.deiconify()

    def saveConfiguration(self):
        self.meta['Title'] = self.caption.get()
        self.meta['Generator'] = self.pattern.current()
        self.meta['Face'] = int(self.face.get())
        self.meta['PlayersLimit'] = int(self.humanLimit.get())
        self.meta['Level'] = self.age.get()
        self.meta['WholePopulation'] = int(self.population.get())
        self.meta['Top'] = int(self.top.get())
        self.meta['Bottom'] = int(self.bottom.get())
        self.meta['Extrems'] = int(self.orientiers.get())
        return self.meta
