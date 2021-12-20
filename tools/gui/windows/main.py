"""
Main Window of MapEdit.
"""

import os
import platform
import time
import sys
from struct import pack
import threading
from feodal import feods, constants, tools, Map
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from gui.windows.meta import MetaWindow
from gui.windows.domain import DomainInfoWindow
from gui.windows.entities import EntityListWindow
import gui.dialogs as dialogs
import gui.resources as res
import gui.controls as ctrls
import gui.panels as panels
from feodal.constants import Age, Environments
import new_map

if sys.hexversion < 0x030100F0:
    def rgb(color): return('#' + pack('BBB', *color).encode('hex'))
else:
    def rgb(color):
        (r, g, b) = color
        return  '#%02x%02x%02x' % (r, g, b)

class MainWindow(tk.Tk):
    """ Show and edit a cells of map. """
    VISUAL_FACE=20
    ZOOM=20

    SHOW_MODE_IMAGE=0
    SHOW_MODE_VALUES=1

    def __init__(self, mapBox, rootFolder, basic=None, pallettes = {}, to_open=False):
        """ Initial user interface """
        tk.Tk.__init__(self)
        self.withdraw()
        # Window
        splash = dialogs.Splash(caption=res.str_resources[21], comment=res.str_resources[22], parent=self)
        splash.message.set(res.str_resources[20])
        self.initPaths(rootFolder)
        self.copyProperties(mapBox=mapBox, pallettes=pallettes)
        self.setMapEdition(mapBox.meta.get('Edition', None))
        self.setWindowRect()
        self.setTitleOfMap(mapBox.meta['Title'], to_open)
        self.setLayersContainer(mapBox.layers, mapBox.face)
        splash.progress['value'] += 5
        splash.progress.update()

        # Events
        self.bind("<KeyRelease>", self.keyDown)

        # Edit options
        splash.message.set(res.str_resources[23])
        self.layer = self.layers.index("domains")
        self.curr_pallette = pallettes.get("domains", [])
        self.curr_layer = self.source.layers["domains"]
        # Cache: capitals map and political pallette
        self.politte = pallettes.get("castles", pallettes.get("domains", []))
        self.capitals = self.source.layers['castles']
        #
        self.showAs = tk.IntVar(value=self.SHOW_MODE_IMAGE)
        self.tool = tk.IntVar(value=ctrls.SelectionTool.USE_TOOL_GET)
        self.setValue = tk.IntVar(value=self.source.layers["domains"][0])
        self.spinnable = tk.StringVar(value=self.source.layers["domains"][0])
        self.curr = (0, 0)
        self.currentCell = 0
        self.selection = []
        if len(self.source.domains) == 0:
            self.source.domains.append(self.toolkit.domain(0, -5))
        splash.progress['value'] += 5
        splash.progress.update()

        #region Main menu
        splash.message.set(res.str_resources[24])
        self.menu = tk.Menu(self)
        self.config(menu=self.menu)
        file_menu = tk.Menu(self.menu)
        # [File]
        file_menu.add_command(label=res.str_resources[66], command=lambda: self.new(None))
        file_menu.add_command(label=res.str_resources[4], underline=4, command=lambda: self.regen(None))
        file_menu.add_command(label=res.str_resources[5], underline=0, command=lambda: self.openMap(None))
        file_menu.add_separator()
        file_menu.add_command(label=res.str_resources[6], underline=0, command=lambda: self.save(None))
        file_menu.add_command(label=res.str_resources[7], command=lambda: self.saveAs(None))
        file_menu.add_separator()
        file_menu.add_command(label=res.str_resources[8], underline=0, command=lambda: self.exit(None))
        self.menu.add_cascade(label=res.str_resources[9], menu=file_menu, underline=0)
        # [Visual]
        visual_menu = tk.Menu(self.menu)
        visual_menu.add_radiobutton(label=res.str_resources[69], var=self.showAs, value=self.SHOW_MODE_IMAGE, command=lambda: self.updMode(None))
        visual_menu.add_radiobutton(label=res.str_resources[11], var=self.showAs, value=self.SHOW_MODE_VALUES, command=lambda: self.updMode(None))
        self.menu.add_cascade(label=res.str_resources[10], menu=visual_menu, underline=0)
        # [Tools]
        tools_menu = tk.Menu(self.menu)
        select_menu = tk.Menu(tools_menu)
        set_tool = lambda: self.updTool(None)
        select_menu.add_radiobutton(label=res.str_resources[12], var=self.tool, value=ctrls.SelectionTool.USE_TOOL_GET, command=set_tool, underline=1)
        select_menu.add_radiobutton(label=res.str_resources[13], var=self.tool, value=ctrls.SelectionTool.USE_TOOL_SELECT, command=set_tool, underline=1)
        select_menu.add_radiobutton(label=res.str_resources[14], var=self.tool, value=ctrls.SelectionTool.USE_TOOL_RECT, command=set_tool, underline=1)
        tools_menu.add_cascade(label=res.str_resources[15], menu=select_menu)
        mouse_menu = tk.Menu(tools_menu)
        mouse_menu.add_radiobutton(label=res.str_resources[16], var=self.tool, value=ctrls.Processor.USE_TOOL_PEN, command=set_tool, underline=0)
        mouse_menu.add_radiobutton(label=res.str_resources[17], var=self.tool, value=ctrls.Processor.USE_TOOL_FILL, command=set_tool)
        tools_menu.add_cascade(label=res.str_resources[18], menu=mouse_menu, underline=1)
        self.menu.add_cascade(label=res.str_resources[19], menu=tools_menu, underline=0)
        # [Windows]
        windows_menu = tk.Menu(self.menu)
        windows_menu.add_command(label=res.str_resources[25], command=self.showMeta)
        windows_menu.add_command(label=res.str_resources[26], underline=0, command=self.showDomains)
        windows_menu.add_command(label=res.str_resources[27], underline=0, command=self.showHierarchy)
        windows_menu.add_command(label=res.str_resources[28], underline=0, command=self.showMarks)
        self.menu.add_cascade(label=res.str_resources[29], menu=windows_menu)
        # [Help]

        splash.progress['value'] += 10
        splash.progress.update()
        #endregion

        # Image with layer visual
        scrollerY = ttk.Scrollbar(self, orient=tk.VERTICAL)
        scrollerX = ttk.Scrollbar(self, orient=tk.HORIZONTAL)
        self.world = tk.Canvas(master=self, width=self.field, height=self.field, xscrollcommand=scrollerX.set, yscrollcommand=scrollerY.set, bg="white")
        self.world.bind("<Button-1>", lambda ev: self.clicked(ev))
        splash.progress['value'] += 5
        splash.progress.update()

        # Selector of layer to show
        self.domainsList = ttk.Combobox(self, values=self.layers)
        self.domainsList.bind("<<ComboboxSelected>>", lambda ev: self.selectLayer(ev))
        self.domainsList.current(self.layer)
        # META DATA
        self.mapName = tk.Label(self, text=res.str_resources[30].format(self.name))
        self.sizes = tk.Label(self, text=res.str_resources[31].format(self.source.face, self.source.face))
        changeMeta = tk.Button(self, text=res.str_resources[32], command=lambda: self.showMeta())
        # Value of cell
        self.valuer = tk.Scale(master=self, from_=0, to=len(mapBox.domains)-1, resolution=1, variable=self.setValue, tickinterval=4, command=self.updValue, orient=tk.HORIZONTAL)
        self.valueControl = tk.Spinbox(master=self, from_=0, to=len(mapBox.domains)-1, increment=1, width=5, textvariable=self.spinnable, command=lambda: self.updValue(self.valueControl.get()))
        addValueButton = tk.Button(master=self, text="+", command=self.addValue)
        # Tools panel
        panel = tk.Frame(master=self)
        self.panel_tools = []
        self.panel_tools.append( tk.Button(master=panel, text=res.str_resources[33], command=lambda: self.updTool(ctrls.SelectionTool.USE_TOOL_GET)) )
        self.panel_tools.append( tk.Button(master=panel, text=res.str_resources[16], command=lambda: self.updTool(ctrls.Processor.USE_TOOL_PEN)) )
        self.panel_tools.append( tk.Button(master=panel, text=res.str_resources[34], command=lambda: self.updTool(ctrls.SelectionTool.USE_TOOL_SELECT)) )
        self.panel_tools.append( tk.Button(master=panel, text=res.str_resources[35], command=lambda: self.updTool(ctrls.SelectionTool.USE_TOOL_RECT)) )
        self.panel_tools.append( tk.Button(master=panel, text=res.str_resources[17], command=lambda: self.updTool(ctrls.Processor.USE_TOOL_FILL)) )
        for btn in self.panel_tools:
            btn.config(relief="flat")
        self.panel_tools[0].config(relief="raised")
        splash.progress['value'] += 5
        splash.progress.update()
        
        # Init edit tools:
        self.roll_val = ctrls.MouseRegulator(self, sensivity=120) # Use mouse wheel to change a value of selections.
        self.roll_val.active = True

        # Show window
        splash.message.set(res.str_resources[36])
        self.domainsList.grid(column=0, columnspan=self.VISUAL_FACE, row=0)
        self.mapName.grid(column=self.VISUAL_FACE+1, row=0)
        self.sizes.grid(column=self.VISUAL_FACE+2, row=0)
        changeMeta.grid(column=self.VISUAL_FACE+3, row=0)
        scrollerY.grid(column=0, rowspan=self.VISUAL_FACE, row=1)
        self.world.grid(column=0, columnspan=MainWindow.VISUAL_FACE, rowspan=MainWindow.VISUAL_FACE, row=1)
        scrollerX.grid(column=0, columnspan=self.VISUAL_FACE, row=1)
        self.valuer.grid(column=self.VISUAL_FACE+1, columnspan=2, row=1)
        self.valueControl.grid(column=self.VISUAL_FACE+3, row=1)
        addValueButton.grid(column=self.VISUAL_FACE+4, row=1)
        panel.grid(column=self.VISUAL_FACE+1, columnspan=3, row=3, rowspan=3)
        self.panel_tools[0].grid(column=0, row=0)
        self.panel_tools[1].grid(column=0, row=1)
        self.panel_tools[2].grid(column=1, row=0)
        self.panel_tools[3].grid(column=2, row=0)
        self.panel_tools[4].grid(column=1, row=1)
        splash.progress['value'] += 10
        splash.progress.update()

        splash.message.set(res.str_resources[37])
        splash.progress['value'] = 100
        splash.progress.update()
        self.showImage()
        splash.destroy()
        self.deiconify()
        self.after(1, lambda: self.focus_force())
        self.limita["landscape"] = (0, len(feods.lands.lands)-1)
        self.limita['marks'] = (0, len(self.source.marks)-1)
        self.mainloop()

    # Commands and events
    def new(self, event):
        mess = res.str_resources[44]
        if self.modify:
            userChoise = messagebox.askyesnocancel(title=res.str_resources[45], message=mess, default=messagebox.YES)
            if userChoise: # YES
                self.save(event)
            elif userChoise is None: # CANCEL
                return
        # Options of new map.
        config = MetaWindow(meta={}, isNew=True, parent=self)
        self.wait_window(config)
        props = config.meta
        self.source.rehead(props)
        #
        name = self.source.name
        w = self.source.face
        t = self.source.top
        b = self.source.bottom
        p = self.source.meta['PlayersLimit']
        a = self.source.meta['Level']
        r = 0
        pattern = "New"
        z = self.ZOOM
        waitForm = dialogs.Splash(caption=res.str_resources[28], comment=res.str_resources[65], parent=self)
        exe = os.path.join(self.root_path, 'tools', 'new_map.py')
        command = "python {0} -n={1} -f={2} -s={3} -t={4} -b={5} -p={6} -l={7} -r={8} -c={9} -z={10}".format(exe, name, name, w, t, b, p, a, r, pattern, z)
        print(command)
        output = os.system(command)
        print(output)
        print("")
        waitForm.progress['value'] = 50
        waitForm.title(res.str_resources[20])
        waitForm.message.set(res.str_resources[21])
        # Load from file
        tmp = os.path.join(self.root_path, "data", "state", "maps.open", name)
        fileName = os.path.join(self.root_path, 'data', 'assets', 'maps', "random")
        if not os.path.exists(os.path.join(fileName, name + ".feods")):
            waitForm.destroy()
            self.deiconify()
            messagebox.showerror(title=res.str_resources[20], message=res.str_resources[64].format(name))
            return
        mapBox = feods.load(name, path=fileName, temp=tmp)
        # Reset window controllers
        mapBox['meta']['Title'] = name
        self.reset(mapBox, pattern=pattern, edition=time.ctime(time.time()))
        waitForm.destroy()
        self.deiconify()
        #os.system("python {0}".format(os.path.join(self.root_path, "tools", "clearCache.py")))
    def regen(self, event):
        # Generate a new map with old parameters and reopen
        mess = res.str_resources[44]
        userChoise = messagebox.askyesnocancel(title=res.str_resources[45], message=mess, default=messagebox.YES)
        if userChoise: # YES
            self.save(None)
        elif userChoise is None: # CANCEL
            return
        # How we name a new map?
        name = simpledialog.askstring(title=res.str_resources[0], prompt=res.str_resources[1])
        if name is None:
            messagebox.showerror(title=res.str_resources[28], message=res.str_resources[2])
            return
        w = self.source.face
        t = self.source.top
        b = self.source.bottom
        p = self.source.meta['PlayersLimit']
        a = self.source.meta['Level']
        r = len(self.source.domains)
        if event is None:
            pattern = self.source.meta.get('Generator', 'Classic')
        else:
            pattern = event
        if type(pattern) == type(0):
            pattern = "Classic"
        z = self.ZOOM
        waitForm = dialogs.Splash(caption=res.str_resources[28], comment=res.str_resources[65], parent=self)
        exe = os.path.join(self.root_path, 'tools', 'new_map.py')
        command = "python {0} -n={1} -f={2} -s={3} -t={4} -b={5} -p={6} -l={7} -r={8} -c={9} -z={10}".format(exe, name, name, w, t, b, p, a, r, pattern, z)
        print(command)
        output = os.system(command)
        print(output)
        print("")
        waitForm.progress['value'] = 50
        waitForm.title(res.str_resources[20])
        waitForm.message.set(res.str_resources[21])
        # Load from file
        tmp = os.path.join(self.root_path, "data", "state", "maps.open", name)
        fileName = os.path.join(self.root_path, 'data', 'assets', 'maps', "random")
        if not os.path.exists(os.path.join(fileName, name + ".feods")):
            waitForm.destroy()
            self.deiconify()
            messagebox.showerror(title=res.str_resources[20], message=res.str_resources[64].format(name))
            return
        mapBox = feods.load(name, path=fileName, temp=tmp)
        # Reset window controllers
        mapBox['meta']['Title'] = name
        self.reset(mapBox, pattern=pattern, edition=time.ctime(time.time()))
        waitForm.destroy()
        self.deiconify()
    def openMap(self, event):
        name = filedialog.askopenfilename(parent=self, title=res.str_resources[21], initialdir=os.path.join(self.root_path, "data", "assets", "maps"), filetypes=[("The Internecine Strife Map files", "*.feods")])
        if name is None:
            return
        try:
            if not os.path.exists(name):
                messagebox.showerror(title="Not exists", message="{} is not found".format(name))
                raise Exception()
            mapBox = self.loadMap(str(name))
        except:
            messagebox.showerror(title=res.str_resources[63], message=res.str_resources[64].format(name))
            return
        # Reset window controllers
        self.reset(mapBox, pattern=mapBox['meta'].get('Generator', None), edition=mapBox['meta']['Edition'])
    def save(self, event):
        self.source.name = self.name
        self.source.meta['Title'] = self.name
        splash = dialogs.Splash(res.str_resources[39], res.str_resources[40], self)
        path = os.path.join(self.root_path, "data", "assets", "maps")
        artist = tools.Picturization(self.source, self.pallettes)
        artist.imagination(self.name, self.ZOOM, os.path.dirname(self.root_folder))
        beStop = False
        splash.progress["value"] = 10
        splash.progress.update()
        # Visual a progress for user. Program is not looped.
        def awaiting():
            while not beStop:
                self.update_idletasks()
                time.sleep(2)
                splash.progress["value"] += 2
                splash.progress.update()
                beStop = splash.progress["value"] == 100
        awaiter = threading.Thread(target=awaiting)
        awaiter.start()
        try:
            splash.message.set(res.str_resources[41])
            self.source.landscapes = [self.source.landscapes[scape] for scape in self.source.landscapes] if type(self.source.landscapes) == type(dict(a=1)) else self.source.landscapes
            feods.save(self.source, self.name, path=path, temp=os.path.dirname(self.root_folder))
        finally:
            splash.message.set(res.str_resources[42])
            beStop = True
            splash.progress["value"] = 100
            splash.progress.update()
            time.sleep(1)
            splash.destroy()
        self.modify = False

        self.edition = time.ctime(time.time())
        self.title(res.str_resources[3].format(self.name, self.edition))
    def saveAs(self, event):
        name = simpledialog.askstring(title=res.str_resources[1], prompt=res.str_resources[43])
        if name is not None:
            self.name = name
        self.mapName.config(text=res.str_resources[30].format(self.name))
        self.save(event)
    def exit(self, event):
        if self.modify:
            mess = res.str_resources[44]
            userChoise = messagebox.askyesnocancel(title=res.str_resources[45], message=mess, default=messagebox.YES)
            if userChoise: # YES
                self.save(None)
            elif userChoise is None: # CANCEL
                return
        os.system("python {} >/dev/null &".format(os.path.join(os.path.dirname(os.path.dirname(__file__)), "clearCache.py")))
        self.destroy()
    def clicked(self, event):
        tool = self.tool.get()
        x, y = (event.x, event.y)
        i, j = (x // self.ZOOM, y // self.ZOOM)
        if i >= self.source.face or j >= self.source.face:
            return
        self.curr = (i, j)
        self.currentCell = i + j * self.source.face
        if tool == ctrls.SelectionTool.USE_TOOL_GET:
            val = self.curr_layer[self.currentCell]
            self.valuer.set(val)
            # Update populations limit
            self.layer = self.domainsList.current()
            layerName = self.layers[self.layer]
            if layerName == "populations":
                self.rescale()
        elif tool == ctrls.Processor.USE_TOOL_PEN:
            val = self.valuer.get()
            x, y = (i * self.ZOOM, j * self.ZOOM)
            if val != self.curr_layer[self.currentCell]:
                self.curr_layer[self.currentCell] = val
                self.pen(x, y, val, mode=self.showAs.get(), capital=self.capitals[self.currentCell])
        elif tool == ctrls.Processor.USE_TOOL_SELECT:
            if self.currentCell in self.selection:
                self.selection.remove(self.currentCell)
            else:
                self.selection.add(self.currentCell)
            val = self.toolkit.average([self.curr_layer[i] for i in self.selection])
            self.valuer.set(value)
    def keyDown(self, event):
        if event.keysym == 'Left' and self.frame[0] > 0:
            self.frame = (self.frame[0] - 1, self.frame[1])
        elif event.keysym == 'Right' and self.frame[0] < self.source.face - self.VISUAL_FACE:
            self.frame = (self.frame[0] + 1, self.frame[1])
        elif event.keysym == 'Up' and self.frame[1] > 0:
            self.frame = (self.frame[0], self.frame[1] - 1)
        elif event.keysym == 'Down' and self.frame[1] < self.source.face - self.VISUAL_FACE:
            self.frame = (self.frame[0], self.frame[1] + 1)
        if self.showAs.get() == self.SHOW_MODE_IMAGE:
            self.showImage()
        else:
            self.showValues()
    def updMode(self, event):
        layer = self.layers[self.layer]
        self.curr_pallette = self.pallettes.get(layer, None)
        self.curr_layer = self.source.layers[layer]
        if self.showAs.get() == self.SHOW_MODE_IMAGE:
            self.showImage()
        else:
            self.showValues()
    def updTool(self, event):
        if type(event) == type(int):
            self.tool.set(event)
            for btn in self.panel_tools:
                btn.config(relief="flat")
            self.panel_tools[event].config(relief="raised")
            self.menu.update()
        if event == self.USE_TOOL_GET or event == self.USE_TOOL_PEN or event == self.USE_TOOL_RECT:
            self.selection.clear()
    def selectLayer(self, event):
        self.layer = self.domainsList.current()
        layerName = self.layers[self.layer]
        self.curr_layer = self.source.layers[layerName]
        self.curr_pallette = self.pallettes.get(layerName, None)
        self.rescale()
        # TODO Save a changes in files?
        if self.showAs.get() == self.SHOW_MODE_IMAGE:
            self.showImage()
        else:
            self.showValues()
    def updValue(self, event):
        val = int(event)
        self.spinnable.set(val)
        val1 = self.valuer.get()
        # Set value of cell
        if len(self.selection) > 0:
            if val != val1:
                shift = val - val1
                for i in self.selection:
                    self.curr_layer[i] += shift
                    x = self.toolkit.x(i) * self.ZOOM
                    y = self.toolkit.y(i) * self.ZOOM
                    self.pen(x, y, val, mode=self.showAs.get())
            return
        if val != val1:
            self.valuer.set(val)
        self.curr_layer[self.currentCell] = val
        # Redraw cell
        x = self.curr[0]*self.ZOOM
        y = self.curr[1]*self.ZOOM
        self.pen(x, y, val, mode=self.showAs.get())
    def addValue(self):
        # Add new item or uppend a maximum on layer
        layer = self.layers[self.layer]
        currValue = self.source.layers[layer][self.currentCell]
        limits = self.getLimits(self.currentCell)
        pallette = self.pallettes.get(layer, None)
        constructors = {"domains": lambda no: self.toolkit.domain(no, self.currentCell), "landscape": lambda no: self.toolkit.landscape(no, "new landscape"), "marks": lambda no: "new mark"}
        isEntity = layer in constructors.keys()

        if not isEntity and pallette is None:
            currValue += 10
            self.source.layers[layer][self.currentCell] += 10
        elif isEntity:
             currValue += 1
             # add item in list
             if limits[0] < currValue:
                if layer == "domains":
                    items = self.source.domains
                elif layer == "landscape":
                    items = self.source.landscapes
                else:
                    items = self.source.marks
                newId = len(items) + 1
                constructor = constructors[layer]
                items.append(constructor(newId))
        else:
            return
        self.source.layers[layer][self.currentCell] = currValue
        if limits[0] < currValue:
            self.rescale()
    #
    def showMeta(self, new=None):
        meta = self.source.meta if not new or new is None else {}
        config = MetaWindow(meta=meta, isNew=False, parent=self)
        self.wait_window(config)
        self.source.rehead(config.meta)
        # Update window
        self.name = self.source.name
        #self.edition = time.ctime(time.time())
        self.title(res.str_resources[3].format(self.name, self.edition))
        self.mapName.config(text=res.str_resources[30].format(self.name))
        self.mapName.update()
        self.sizes.config(text=res.str_resources[31].format(self.source.face, self.source.face))
        self.sizes.update()
        self.update()
    def showDomains(self, event=None):
        variants = EntityListWindow(parent=self, instance=self.source, entityClass="domains", entityConstructor=lambda id_, name: self.toolkit.domain(id_, 0))
        self.wait_window(variants)
        toModify = variants.selected
        variants.destroy()
        self.deiconify()
        #
        informPanel = DomainInfoWindow(self.source, domain=toModify, parent=self)
        self.wait_window(informPanel)
        # ?
        informPanel.destroy()
        self.deiconify()
    def showHierarchy(self, event=None):
        pass
    def showMarks(self, event=None):
        marks = EntityListWindow(parent=self, instance=self.source, entityClass="marks", entityConstructor=lambda id_, name: name)
        self.wait_window(marks)
        if marks.selected is not None:
            newName = simpledialog.askstring(title=res.str_resources[67], prompt=res.str_resources[68].format(marks.selected))
            self.source.marks[-1] = newName
        self.limita["marks"] = (0, len(self.source.marks)-1)
    # Tools
    limita = {"environments": (constants.Environments.Air, constants.Environments.Port), "terrain": (-1000, 5000), "populations": (0, 10000)}
    def getLimits(self, noCell):
        layerName = self.layers[self.layer]
        limits = self.limita.get(layerName, None)
        if limits is None:
            layer = self.source.layers[layerName]
            return (min(layer), max(layer))
        if layerName == "populations":
            lands = self.source.layers['landscape']
            landing = lands[noCell]
            environment = [self.source.landscapes[landscape] for landscape in self.source.landscapes if self.source.landscapes[landscape]['ID'] == landing][0]
            return (limits[0], environment['Capacity'])
        if layerName == "marks":
            return (0, len(self.source.marks) - 1)
        return limits
    def pen(self, x, y, val, mode, capital = 0):
        print("({}, {}) is capital of {} domain".format(x // self.ZOOM, y // self.ZOOM, capital) if capital > 0 else "({}, {}) is not capital".format(x // self.ZOOM, y // self.ZOOM))
        pallette = self.curr_pallette
        if mode == self.SHOW_MODE_IMAGE:
            if pallette is not None and val >= len(pallette): val = - 1
            color = pallette[val] if pallette is not None else self.grayscale(val)
            self.world.create_rectangle(x, y, x + self.ZOOM, y + self.ZOOM, fill=rgb(color))
            if capital > 0:
                if capital >= len(self.politte): capital = -1
                color = self.politte[val]
                self.world.create_oval(x+1, y+1, x+self.ZOOM-1, y+self.ZOOM-1, fill=rgb(color))
        else:
            sh = self.ZOOM//2
            self.world.create_rectangle(x, y, x + self.ZOOM, y + self.ZOOM, fill="white", outline="white")
            self.world.create_text(x + sh, y + sh, text=str(val))
        self.modify = True
    def selected(self, id_):
        return (id_, id_ % self.source.face, id_ // self.source.face)
    # Graphic
    def showImage(self):
        """ Draw graphic view of cells """
        #
        for y in range(0, self.source.face):
            for x in range(0, self.source.face):
                i = x + y * self.source.face
                val = self.curr_layer[i]
                if self.curr_pallette is not None:
                    if val >= len(self.curr_pallette): val = len(self.curr_pallette) - 1
                    color = self.curr_pallette[val]
                else:
                    color = self.grayscale(val)
                self.world.create_rectangle(x*self.ZOOM, y*self.ZOOM, (x + 1)*self.ZOOM, (y + 1)* self.ZOOM, fill=rgb(color))
                # Draw a capital mark
                if self.capitals[i] > 0:
                    val = self.capitals[i]
                    if val >= len(self.politte): val = - 1
                    color = self.politte[val]
                    self.world.create_oval(x*self.ZOOM+1, y*self.ZOOM+1, (x + 1)*self.ZOOM-1, (y + 1)*self.ZOOM-1, fill=rgb(color))
    def grayscale(self, value):
        if self.dia[1] != 0 and self.dia[0] != 0:
            value = int((value - self.dia[0]) * (255.0 / (self.dia[1] - self.dia[0])))
        else:
            value = 0
        if value < 0:
            value = 0
        elif value > 255:
            value = 255
        return (value, value, value)
    def showValues(self):
        layer = self.layers[self.layer]
        pallette = self.pallettes.get(layer, None)
        sh = self.ZOOM//2
        self.world.create_rectangle(0, 0, self.field, self.field, fill="white")
        for y in range(0, self.source.face):
            for x in range(0, self.source.face):
                i = x + y * self.source.face
                val = self.source.layers[layer][i]
                self.world.create_text(x*self.ZOOM + sh, y*self.ZOOM + sh, text=str(val))
    # Other
    def loadMap(self, url):
        url = url.replace('.feods', '')
        print("Path: " + url)
        paths = [url, os.path.join(self.root_path, 'data', 'assets', 'maps', url), os.path.join(self.root_path, 'data', 'assets', 'maps', "random", url)]
        for fileName in paths:
            if os.path.exists(fileName + ".feods"):
                name = str(os.path.basename(fileName))
                tmp = os.path.join(self.root_path, "data", "state", "maps.open")
                print("File {}.feods has name {} and open to {}".format(fileName, name, tmp))
                return feods.load(name, os.path.dirname(fileName), temp=tmp)
            else:
                print("Not found {}.feods".format(fileName))
        raise Exception(res.str_resources[46].format(url, fileName))
    def reset(self, mapBox, pattern=None, edition=None):
        # Update a windows by a new map contains
        self.name = mapBox['meta']['Title']
        self.edition = edition if edition is not None else mapBox['meta'].get('Edition', time.ctime(time.time()))
        self.title(res.str_resources[3].format(self.name, self.edition))
        # Clear map field
        self.world.create_rectangle(0, 0, self.source.face * self.ZOOM, self.source.face * self.ZOOM, fill="white")
        # Update with new values
        self.source = Map.Map(mapBox, generator=pattern)
        self.layers = self.source.layers.keys()
        self.layers = [res._(name) for name in self.layers]
        self.layer = self.layers.index("domains")
        self.setValue.set(self.source.layers["domains"][self.currentCell])
        self.spinnable.set(str(self.source.layers["domains"][self.currentCell]))
        self.domainsList.config(values=self.layers)
        self.domainsList.current(self.layer)
        self.valuer.config(to=len(self.source.domains), variable=self.setValue)
        self.valueControl.config(to=len(self.source.domains), textvariable=self.spinnable)
        self.curr_layer = self.source.layers[self.layers[self.layer]]
        self.mapName.config(text=res.str_resources[30].format(self.name))
        self.mapName.update()
        self.sizes.config(text=res.str_resources[31].format(self.source.face, self.source.face))
        self.sizes.update()
        self.update()
        # Update prepared vars
        self.politte = self.pallettes.get("castles", self.pallettes.get("domains", []))
        self.capitals = self.source.layers['castles']
        self.frame = (0, 0)
        # Update a map field
        if self.showAs.get() == self.SHOW_MODE_IMAGE:
            self.showImage()
        else:
            self.showValues()
    def rescale(self):
        self.dia = (bottom, top) = self.getLimits(self.currentCell)
        self.valuer.config(from_=bottom, to=top)
        self.valueControl.config(from_=bottom, to=top)
        self.spinnable.set(self.source.layers[self.layers[self.layer]][self.currentCell])

    # Substages of __init__()
    def initPaths(self, rootFolder):
        self.root_folder = rootFolder
        self.root_path = rootFolder if basic is None else basic
        # "New" map constanted path
        self.clear = os.path.join(self.root_path, "data", "basis")
        self.cache = os.path.dirname(self.root_folder)
    def setMapEdition(self, edition):
        original = os.path.join(self.root_path, "data", "assets", "maps", self.name + ".feods")
        if not os.path.exists(original):
            original = os.path.join(self.root_path, "data", "assets", "maps", "random", self.name + ".feods")
        self.edition = elf.edition if self.edition is not None else time.ctime(os.path.getmtime(original))
    def setWindowRect(self)    
        # Gets the requested values of the height and widht.
        windowWidth = (self.VISUAL_FACE + 12)*self.ZOOM
        windowHeight = (self.VISUAL_FACE + 1)*self.ZOOM
        # Gets both half the screen width/height and window width/height
        positionRight = int(self.winfo_screenwidth()/2 - windowWidth/2)
        positionDown = int(self.winfo_screenheight()/2 - windowHeight/2)
        self.geometry("{}x{}+{}+{}".format(windowWidth, windowHeight, positionRight, positionDown))
    def setTitleOfMap(self, name, to_open=None):
        self.name = name
        if name is None and to_open:
            fname = tkSimpleDialog.askstring(title=res.str_resources[0], prompt=res.str_resources[1])
            mapBox = Map.Map(self.loadMap(fname))
            self.name = name
        elif name is None:
            raise Exception(res.str_resources[2])
        self.title(res.str_resources[3].format(name, self.edition))
    def setLayersContainer(self, layers, face):
        try:
            self.layers = list(layers.keys())
        except:
            print(type(layers), len(layers))
            raise
        self.toolkit = tools.Tools(face, [landscapes[land] for land in landscapes])
    def copyProperties(self, mapBox, pallettes):
        self.source = mapBox
        self.pallettes = pallettes
        self.modify = False
        self.field = MainWindow.VISUAL_FACE * MainWindow.ZOOM
