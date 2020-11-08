"""
Main Window of MapEdit.
"""

#import pygame
import os
import platform
import time
import sys
if sys.hexversion < 0x030100F0:
    import Tkinter as tk
    import ttk
    import tkMessageBox as messagebox
    import tkFileDialog as filedialog
    import tkSimpleDialog as simpledialog
    import dialogs
    import resources as res
else:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog, simpledialog
    import gui.dialogs as dialogs
    import gui.resources as res
from feodal import feods, constants, tools, Map
from feodal.constants import Age
from struct import pack
import threading
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

    USE_TOOL_GET=0
    USE_TOOL_PEN=1
    USE_TOOL_SELECT=2
    USE_TOOL_RECT=3
    USE_TOOL_FILL=4

    def __init__(self, mapBox, rootFolder, basic=None, pallettes = {}, to_open=False):
        """ Initial user interface """
        tk.Tk.__init__(self)
        self.withdraw()
        splash = dialogs.Splash(caption=res.str_resources[21], comment=res.str_resources[22], parent=self)
        self.root_folder = rootFolder
        self.root_path = rootFolder if basic is None else basic

        splash.message.set(res.str_resources[20])
        self.name = mapBox.meta['Title']
        if self.name is None:
            fname = tkSimpleDialog.askstring(title=res.str_resources[0], prompt=res.str_resources[1])
            if to_open:
                mapBox = Map.Map(self.loadMap(fname))
                self.name = mapBox.meta['Title']
            elif to_open is None:
                raise Exception(res.str_resources[2])
        # Window
        original = os.path.join(self.root_path, "data", "assets", "maps", self.name + ".feods")
        if not os.path.exists(original):
            original = os.path.join(self.root_path, "data", "assets", "maps", "random", self.name + ".feods")
        self.edition = time.ctime(os.path.getmtime(original))
        self.title(res.str_resources[3].format(self.name, self.edition))
        # Gets the requested values of the height and widht.
        windowWidth = (self.VISUAL_FACE + 12)*self.ZOOM
        windowHeight = (self.VISUAL_FACE + 1)*self.ZOOM

        # Gets both half the screen width/height and window width/height
        positionRight = int(self.winfo_screenwidth()/2 - windowWidth/2)
        positionDown = int(self.winfo_screenheight()/2 - windowHeight/2)

        self.geometry("{}x{}+{}+{}".format(windowWidth, windowHeight, positionRight, positionDown))
        self.source = mapBox
        self.toolkit = tools.Tools(mapBox.face, [mapBox.landscapes[land] for land in mapBox.landscapes])
        self.pallettes = pallettes
        self.field = MainWindow.VISUAL_FACE * MainWindow.ZOOM
        try:
            self.layers = list(mapBox.layers.keys())
        except:
            print(type(mapBox.layers), len(mapBox.layers))
            raise
        self.modify = False
        splash.progress['value'] += 5
        time.sleep(1)

        # Edit options
        splash.message.set(res.str_resources[23])
        self.layer = self.layers.index("domains")
        self.curr_pallette = pallettes.get("domains", [])
        self.curr_layer = self.source.layers["domains"]
        self.showAs = tk.IntVar(value=self.SHOW_MODE_IMAGE)
        self.tool = tk.IntVar(value=self.USE_TOOL_GET)
        self.setValue = tk.IntVar(value=self.source.layers["domains"][0])
        self.spinnable = tk.StringVar(value=self.source.layers["domains"][0])
        self.curr = (0, 0)
        self.currentCell = 0
        self.selection = set({})
        splash.progress['value'] += 5
        splash.progress.update()

        #region Main menu
        splash.message.set(res.str_resources[24])
        self.menu = tk.Menu(self)
        self.config(menu=self.menu)
        file_menu = tk.Menu(self.menu)
        # [File]
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
        visual_menu.add_radiobutton(label=res.str_resources[10], var=self.showAs, value=self.SHOW_MODE_IMAGE, command=lambda: self.updMode(None))
        visual_menu.add_radiobutton(label=res.str_resources[11], var=self.showAs, value=self.SHOW_MODE_VALUES, command=lambda: self.updMode(None))
        self.menu.add_cascade(label=res.str_resources[10], menu=visual_menu, underline=0)
        # [Tools]
        tools_menu = tk.Menu(self.menu)
        select_menu = tk.Menu(tools_menu)
        set_tool = lambda: self.updTool(None)
        select_menu.add_radiobutton(label=res.str_resources[12], var=self.tool, value=self.USE_TOOL_GET, command=set_tool, underline=1)
        select_menu.add_radiobutton(label=res.str_resources[13], var=self.tool, value=self.USE_TOOL_SELECT, command=set_tool, underline=1)
        select_menu.add_radiobutton(label=res.str_resources[14], var=self.tool, value=self.USE_TOOL_RECT, command=set_tool, underline=1)
        tools_menu.add_cascade(label=res.str_resources[15], menu=select_menu)
        mouse_menu = tk.Menu(tools_menu)
        mouse_menu.add_radiobutton(label=res.str_resources[16], var=self.tool, value=self.USE_TOOL_PEN, command=set_tool, underline=0)
        mouse_menu.add_radiobutton(label=res.str_resources[17], var=self.tool, value=self.USE_TOOL_FILL, command=set_tool)
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
        # Tools panel
        panel = tk.Frame(master=self)
        self.panel_tools = []
        self.panel_tools.append( tk.Button(master=panel, text=res.str_resources[33], command=lambda: self.updTool(self.USE_TOOL_GET)) )
        self.panel_tools.append( tk.Button(master=panel, text=res.str_resources[16], command=lambda: self.updTool(self.USE_TOOL_PEN)) )
        self.panel_tools.append( tk.Button(master=panel, text=res.str_resources[34], command=lambda: self.updTool(self.USE_TOOL_SELECT)) )
        self.panel_tools.append( tk.Button(master=panel, text=res.str_resources[35], command=lambda: self.updTool(self.USE_TOOL_RECT)) )
        self.panel_tools.append( tk.Button(master=panel, text=res.str_resources[17], command=lambda: self.updTool(self.USE_TOOL_FILL)) )
        for btn in self.panel_tools:
            btn.config(relief="flat")
        self.panel_tools[0].config(relief="raised")
        splash.progress['value'] += 5
        splash.progress.update()

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
        panel.grid(column=self.VISUAL_FACE+1, columnspan=3, row=3, rowspan=3)
        self.panel_tools[0].grid(column=0, row=0)
        self.panel_tools[1].grid(column=0, row=1)
        self.panel_tools[2].grid(column=1, row=0)
        self.panel_tools[3].grid(column=2, row=0)
        self.panel_tools[4].grid(column=1, row=1)
        splash.progress['value'] += 10
        splash.progress.update()

        self.world.focus_set()
        splash.message.set(res.str_resources[37])
        splash.progress['value'] = 85
        self.showImage()
        ## finished loading so destroy splash
        time.sleep(2)
        splash.progress['value'] = 100
        splash.progress.update()
        splash.destroy()
        self.deiconify()
        self.mainloop()

    # Commands and events
    def regen(self, event):
        # Generate a new map with old parameters and reopen
        name = tkSimpleDialog.askstring(title=res.str_resources[0], prompt=res.str_resources[1])
        if name is None:
            messagebox.showerror(title=res.str_resources[38], message=res.str_resources[2])
            return
        w = self.source.face
        t = self.source.top
        b = self.source.bottom
        p = self.source.meta['PlayersLimit']
        a = self.source.meta['Level']
        r = len(self.source.domains)
        pattern = self.source.generator
        z = self.ZOOM
        output = os.system("python {0}/new_map.py -n={1} -f={2} -s={3} -t={4} -b={5} -p={6} -l={7} -r={8} -c={9} -z={10}".format(tools, name, name, w, t, b, p, a, r, pattern, z))
        print(output)
        print("")
        # Load from file
        tmp = os.path.join(root, "data", "state", "maps.open", name)
        fileName = os.path.join(root, 'data', 'assets', 'maps', "random")
        mapBox = feods.load(name, path=fileName, temp=tmp)
        # Reset window controllers
        self.name = name
        self.title(res.str_resources[3].format(self.name))
        self.source = Map.Map(mapBox, generator=pattern)
        self.layers = self.source.domains.keys()
        self.layer = self.layers.index("domains")
        self.setValue.set(self.source.layers["domains"][self.currentCell])
        self.spinnable.set(str(self.source.layers["domains"][self.currentCell]))
        self.domainsList.config(values=self.layers)
        self.domainsList.current(self.layer)
        self.valuer.config(to=len(self.source.domains), variable=self.setValue)
        self.valueControl.config(to=len(self.source.domains), variable=self.spinnable)
        # Update a map field
        if self.showAs.get() == self.SHOW_MODE_IMAGE:
            self.showImage()
        else:
            self.showValues()
    def openMap(self, event):
        pass
    def save(self, event):
        splash = dialogs.Splash(res.str_resources[39], res.str_resources[40], self)
        path = os.path.join(self.root_path, "data", "assets", "maps")
        artist = tools.Picturization(self.source, self.pallettes)
        artist.imagination(self.name, self.ZOOM, self.root_folder)
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
        # TODO MessageBox with "Are you real close now?". User case.
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
        if tool == self.USE_TOOL_GET:
            val = self.curr_layer[self.currentCell]
            self.valuer.set(val)
            # Update populations limit
            self.layer = self.domainsList.current()
            layerName = self.layers[self.layer]
            if layerName == "populations":
                self.dia = (bottom, top) = self.getLimits(self.currentCell)
                self.valuer.config(from_=bottom, to=top)
                self.spinnable.config(from_=bootom, to=top)
        elif tool == self.USE_TOOL_PEN:
            val = self.valuer.get()
            x, y = (i * self.ZOOM, j * self.ZOOM)
            if val != self.curr_layer[self.currentCell]:
                self.curr_layer[self.currentCell] = val
                self.pen(x, y, val, mode=self.showAs.get())
        elif tool == self.USE_TOOL_SELECT:
            if self.currentCell in self.selection:
                self.selection.remove(self.currentCell)
            else:
                self.selection.add(self.currentCell)
            val = self.toolkit.average([self.curr_layer[i] for i in self.selection])
            self.valuer.set(value)
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
        self.dia = (bottom, top) = self.getLimits(self.currentCell)
        self.valuer.config(from_=bottom, to=top)
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
    def showMeta(self, new=None):
        meta = self.source.meta if not new or new is None else {}
        config = MetaWindow(meta=meta, isNew=False, parent=self)
        self.wait_window(config)
        self.source.rehead(config.meta)
        # Update window
        self.name = self.source.name
        self.title(res.str_resources[3].format(self.name))
        self.mapName.config(text=res.str_resources[30].format(self.name))
        self.mapName.update()
        self.sizes.config(text=res.str_resources[31].format(self.source.face, self.source.face))
        self.sizes.update()
        self.update()
    #
    def showDomains(self, event=None):
        variants = EntityListWindow(parent=self, instance=self.source, entityClass="domains", entityConstructor=lambda id_, name: self.toolkit.domain(id_, 0))
        self.wait_window(variants)
        toModify = variants.selected
        print("Selected domain:", toModify)
        # TODO: show domain edit window
    def showHierarchy(self, event=None):
        pass
    def showMarks(self, event=None):
        pass
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
        return limits
    def pen(self, x, y, val, mode):
        pallette = self.curr_pallette
        if mode == self.SHOW_MODE_IMAGE:
            if pallette is not None and val >= len(pallette): val = len(pallette) - 1
            color = pallette[val] if pallette is not None else self.grayscale(val)
            self.world.create_rectangle(x, y, x + self.ZOOM, y + self.ZOOM, fill=rgb(color))
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
        # Mark a capital cell attributes
        capitals = self.source.layers['castles']
        politte = self.pallettes['castles']
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
                if capitals[i] > 0:
                    val = capitals[i]
                    if val >= len(politte): val = len(politte) - 1
                    color = politte[val]
                    self.world.create_oval(x*self.ZOOM+1, y*self.ZOOM+1, (x + 1)*self.ZOOM-1, (y + 1)*self.ZOOM-1, fill=rgb(color))
    def grayscale(self, value):
        value = int((value - self.dia[0]) * (255.0 / self.dia[1]))
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
        fileName = url
        if not os.path.exists(fileName):
            fileName = os.path.join(self.root_path, 'data', 'assets', 'maps', url + ".feods")
            if not os.path.exists(fileName):
                fileName = os.path.join(self.root_path, 'data', 'assets', 'maps', "random", url + ".feods")
        if not os.path.exists(fileName):
            raise Exception(res.str_resources[46].format(url, fileName))

        name = str(os.path.basename(fileName)).partition('.')[0]
        tmp = os.path.join(self.root_path, "data", "state", "maps.open")
        return feods.load(name, os.path.dirname(fileName), temp=tmp)

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
        actual = meta.get('Generator', 'Classic')
        self.generator = tk.IntVar(value=generators.index(actual))
        editable = "normal" if isNew else "disabled"
        # Make a form
        self.title(res.str_resources[48].format(meta['Title']))
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
        for item in self.items:
            name = item.get('name', entityClass) if type(item) is not strtype else item
            no = index + 1 if type(item) is strtype else item.get("id", item.get('ID', index + 1))
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
