#import QTKit
import os
import platform
import time
import sys
from struct import pack
import threading
from gettext import gettext as _
if sys.hexversion < 0x030100F0:
    import Tkinter as tk
    import ttk
    import tkMessageBox as messagebox
    import tkFileDialog as filedialog
    import tkSimpleDialog as simpledialog
    import demo.core.battle as battle
else:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog, simpledialog
    import demo.core.battle as battle

if sys.hexversion < 0x030100F0:
    def rgb(color): return('#' + pack('BBB', *color).encode('hex'))
else:
    def rgb(color):
        (r, g, b) = color
        return  '#%02x%02x%02x' % (r, g, b)

class MainWindow(tk.Tk):
    def __init__(self, title):
        tk.Tk.__init__(self)
        self.withdraw()
        self.title(_(title))
        self.width = 1280
        self.height = 960
        self.geometry("{}x{}+0+0".format(self.width, self.height))

        #region Main Menu
        menu = tk.Menu(master=self)
        self.initMainMenu(menu)
        self.config(menu=menu)
        #endregion

        #region Display of animation
        self.screen = tk.Canvas(master=self, width=self.width, height=self.height)
        #endregion

        self.screen.pack()

        self.stop = True

    def initMainMenu(self, menu):
        pass

    def initInformPanel(self, panel):
        pass

    def update(self):
        pass

    def draw(self):
        pass
