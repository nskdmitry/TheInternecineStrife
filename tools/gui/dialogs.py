""" Collection of dialog windows. """

import os
import platform
import sys
if sys.hexversion < 0x030100F0:
    import Tkinter as tk
    import ttk
else:
    import tkinter as tk
    from tkinter import ttk

class Splash(tk.Toplevel):
    WIDTH=220
    HEIGHT=120
    def __init__(self, caption, comment, parent):
        tk.Toplevel.__init__(self, parent)

        positionRight = int(parent.winfo_screenwidth()/2 - self.WIDTH/2)
        positionDown = int(parent.winfo_screenheight()/2 - self.HEIGHT/2)

        self.geometry("{}x{}+{}+{}".format(self.WIDTH, self.HEIGHT, positionRight, positionDown))
        self.title(caption)
        self.message = tk.StringVar(self, value=comment)
        messager = tk.Message(self, textvariable=self.message, width=300)
        messager.grid(column=1, columnspan=10, row=0)
        self.progress = ttk.Progressbar(self, length=100, mode="indeterminate")
        self.progress.grid(column=0, columnspan=14, row=2)
        self.progress['value'] = 0

        ## required to make window show before the program gets to the mainloop
        self.update()

class Dialog(tk.Toplevel):
    def __init(self, master, cfg={}):
        tk.Toplevel.__init__(self, master, cfg)
    def exit(self):
        self.destroy()
        self.master.deiconify()
