import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import gui.dialogs as dialogs

class EntityListWindow(dialogs.Dialog):
    """ Show list of some entities: domains, landscapes, marks, etc to select or add. """
    def __init__(self, parent, instance, entityClass, entityConstructor = lambda id_, name: tuple(id_, name)):
        dialogs.Dialog.__init__(self, parent)
        self.title("Choise from {}".format(entityClass))
        # Data
        self._constructor = entityConstructor
        self.selected = None
        self.items = instance.__dict__.get(entityClass, None)
        if self.items is None:
            raise IndexError("Entities {} is not supported on current version of FeodalWorld GE")
        print(self.items[0])
        # Scroll bars
        scrollerY = ttk.Scrollbar(self, orient=tk.VERTICAL)
        scrollerX = ttk.Scrollbar(self, orient=tk.HORIZONTAL)
        # List of entities
        self.options = tk.Listbox(self, width=16, bg="black", fg="white", height=20, xscrollcommand=scrollerX.set, yscrollcommand=scrollerY.set)
        index = 0
        strtype = type("")
        unistr = type(u'')
        for item in self.items:
            if type(item) is strtype or type(item) is unistr:
                name = item
                no = index
            else:
                name = item.get('name', entityClass)
                no = item.get("id", item.get('ID', index + 1))
            self.options.insert(index, "{}. {}".format(no, name))
            index += 1
        # Buttons
        accept = tk.Button(self, text="OK", command=lambda: self.accept())
        append = tk.Button(self, text="Add", command=lambda: self.append())
        cancel = tk.Button(self, text="Cancel", command=lambda: self.cancel())
        # Layering
        self.options.grid(column=0, row=0, columnspan=3, rowspan=10)
        scrollerX.grid(column=0, row=11, columnspan=3)
        scrollerY.grid(column=4, row=0, rowspan=10)
        accept.grid(column=0, row=12)
        append.grid(column=1, row=12)
        cancel.grid(column=2, row=12)
        self.master.update()
    def accept(self):
        no = self.options.curselection()[0]
        self.selected = self.items[no]
        self.exit()
    def append(self):
        self.selected = self._constructor(len(self.items), "(Name)")
        self.items.append(self.selected)
        self.exit()
    def cancel(self):
        self.selected = None
        self.exit()
