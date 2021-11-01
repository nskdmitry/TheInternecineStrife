import os
#import platform
#import time
#import sys
import tkinter as tk
from tkinter import ttk#, messagebox, filedialog, simpledialog
from PIL import Image, ImageTk
import gui.resources as res

# Abstractions

class Tool:    
    """ Features of the Edit GUI. """
    def __init__(self, window, name="", shortcut=None, picto="./resources/btns/none.png"):
        self.tool_name = name
        self.parent = window
        self.active = False
        self.sign = ImageTk.PhotoImage(Image.open(os.path.realpath(picto)))
        self.latest_mouse = None
        if shortcut is not None:
            window.bind(shortcut, self._actuality)
        else:
            self._actuality(None)
        self.face = self.parent.source.face
    # To rewrite in inhabbites
    def apply_conditions(self): return False
    def process_input(self, event): raise NotImplementedError()
    def apply(self): raise NotImplementedError()
    def _actuality(self, event):
        """ Activate tool and bind all mouse event handlers. """
        self.active = True
        self.parent.bind("<Button-1>", self._input)
    # All tools helpers
    def _input(self, mouse_event=None):
        event = self._get_cell_props(mouse_event)
        if event is None:
            return
        self.process_input(event)
        if self.active and elf.apply_conditions(self):
            self.apply()
    def _get_cell_props(self, mouse_event):
        x, y = (mouse_event.x, mouse_event.y)
        i, j = (x // self.parent.ZOOM, y // self.parent.ZOOM)
        if i >= self.source.face or j >= self.source.face or i < 0 or j < 0:
            return None
        mouse_event.x = i
        mouse_event.y = j
        mouse_event.cell_index = self._index(i, j)
        return mouse_event
    def _index(self, x, y):
        return  x + y * self.face
    def _explose(self, index):
        return (index % self.face, int(index / self.face), index)
    def _in(self, index):
        (x, y, _) = self._explose(index)
        return x < 0 or x >= self.face or y < 0 or y >= self.face
    
class SelectionTool(Tool):
    """ Tool function to set a rule of selection cells in the current layer. """
    
    # To show a buttons in panels
    USE_TOOL_GET=0
    USE_TOOL_SELECT=1
    USE_TOOL_RECT=2
    USE_TOOL_WAND=3
    USE_TOOL_LIKE=4
    USE_TOOL_INVERSE=5
    USE_TOOL_CLEAR=6

    #region New methods
    def selection_rule(self, layer):
        """ Return [cellNo1, cellNo2,...] or None """
        return None
    #endregion
    # Inherited methods realisation
    def apply():
        layer = self.parent.curr_layer
        cells = self.selection_rule(layer)
        self.selection = cells if cells is not None else self.section

class Processor(Tool):
    """ Tool function to modify a selected area in layer. """
    USE_TOOL_PEN=7
    USE_TOOL_FILL=8
    USE_TOOL_MIN=9
    USE_TOOL_MAX=10
    USE_TOOL_AVER=11

    # To implementation.
    def process(self, layer, selection): raise NotImplementedError
    #
    def apply_conditions(self): return len(self.parent.selection)
    def process_input(self, event): pass
    def apply(self):
        layer = self.parent.curr_layer
        selection = self.parent.selection
        self.process(layer, selection)
#
# For uses.
#

### Selection tools

class SelectionSingle(SelectionTool):
    def __init__(self, window):
        SelectionTool.__init__(self, window, name="One", shortcut="<Alt+S>", picto="../data/resources/btns/narrow.png")
        self.new_cell = None
    def apply_conditions(self):
        return self.new_cell is not None
    def process_input(self, event):
        self.new_cell = (event.x, event.y, event.cell_index)
    def selection_rule(self, layer):
        return [self.new_cell]
 
class SelectionOneByOne(SelectionTool):
    def __init__(self, window):
        SelectionTool.__init__(self, window, name="One by one", shortcut="<Alt+Q>", picto="../data/resources/btns/plumin.png")
        self.click = None
        self.selection = []
    def apply_conditions(self):
        return True
    def process_input(self, event):
        self.click = event
    def selection_rule(self, layer):
        if self.click.cell_index in self.selection:
            self.selection.remove(self.click.cell_index)
        else:
            self.selection.append(self.click.cell_index)
        return self.selection

class SelectionRect(SelectionTool):
    def __init__(self, window):
        SelectionTool.__init__(self, window, name="Rect selection", shortcut="<Alt+R>", picto="../data/resources/btns/rect.png")
        self.corner = None
        self.last = None
    def apply_conditions(self):
        return self.corner is not None and self.last is not None and self.corner.cell_index != self.last.cell_index
    def _actuality(self, event):
        Tool._actuality(self, event)
        self.parent.bind("<B1-Motion>", self._input)
        self.parent.bind("<ButtonRelease-1>", self._input)
    def process_input(self, event):
        wind = self.parent
        face = self.parent.ZOOM
        if self.corner is not None:
            if event.type == "Down":
                self.corner = (event.x, event.y, event.cell_index,)
        elif event.type == "Motion":
            # Visual selection
            if wind.showAs.get() == wind.SHOW_MODE_IMAGE:
                wind.showImage()
            else:
                wind.showValues()
            wind.world.create_rectangle(self.corner.x*face, self.corner.y*face, event.x*face, event.x*face, outline="gold")
        elif event.type == "Release":
            self.last = event
    def selection_rule():
        s_x = self.corner.x
        s_y = self.corner.y
        e_x = self.last.x
        e_y = self.last.y
        self.corner = None
        self.last = None
        return [(x, y, self._index(x, y)) for x in range(s_x, e_x, 1 if s_x < e_x else -1) for y in range(s_y, e_y, 1 if s_y < e_y else -1)]

class SelectionAllAs(SelectionTool):
    def __init__(self, window, sensivity):
        SelectionTool.__init__(self, window, name="Like as", shortcut="<Alt+A>", picto="../data/resources/btns/like.png")
        self.sensivity = abs(int(sensivity))
        self.click = None
    def apply_conditions(self):
        self.click is not None
    def process_input(self, event):
        self.click = event
    def selection_rule(self, layer):
        ideal = layer[self.click.cell_index]
        return [(i % self.world.face, int(i / self.world.face), i) for i in range(0, len(layer)) if self.like(layer[i], ideal)]
    def like(self, value, ideal):
        return abs(ideal - value) <= self.sensivity

class SelectionMagicWand(SelectionAllAs):
    def __init__(self, window, sensivity):
        SelectionTool.__init__(self, window, name="Magic wand", shortcut="<Alt+M>", picto="../data/resources/btns/like.png")
        self.sensivity = abs(sensivity)
        self.click = None
        self.saw = []
    def apply_conditions(self):
        return self.click is not None
    def selection_rule(self, layer):
        selection = [(self.click.x, self.click.y, self.click.cell_index)]
        #
        base = self.click.cell_index
        front = [self._explose(shft + base) for shft in [-1, +self.face, 1, -self.face] if self._in(shft + base) and self.check(shft + base, base, layer)]
        self.saw = [self.click.cell_index]
        #
        while len(front) > 0:
            selection.extend(front)
            self.saw.extend([point[2] for point in front])
            # Front will make by front
            front = [self._explose(shft + base) for shft in [-1, +self.face, 1, -self.face] for base in front if self._in(shft + base) and self.check(shft + base, base, layer)]
        return selection
    def check(self, index, base, layer):
        x, y = (index % self.face, int(index / self.face))
        if index in self.saw: return False
        if abs(base.x - x) < abs(self.click.x - x): return False
        if abs(base.y - y) < abs(self.click.y - y): return False
        return self.like(value, layer[self.click.cell_index])

class SelectionInverse(SelectionTool):
    def __init__(self, window):
        SelectionTool.__init__(self, window, name="Inverse", shortcut="<Alt-i>", picto="../data/resources/btns/inverse.png")
        self._has = window.selection
    def apply_conditions(self): return len(self._has) > 0
    def process_input(self, event): pass
    def selection_rule(self, layer):
        to_skip = [point.cell_index for point in self._has]
        return [i for i in range(0, len(layer)) if i not in to_skip]
        
class SelectionCancel(SelectionTool):
    def __init__(self, window):
        SelectionTool.__init__(self, window, name="Inverse", shortcut="<Alt-c>", picto="../data/resources/btns/clr_select.png")
    def apply_conditions(self): return len(self._has) > 0
    def process_input(self, event): pass
    def selection_rule(self, layer): return []
    
### Handler of layer values in selection

class Minimizator(Processor):
    def __init__(self, window):
        Processor.__init__(self, window, "Minimize selection", shortcut="<Alt-D>", picto="../data/resources/btns/down.png")
    def process(self, layer, selection):
        minimum = min([layer[point[2]] for point in selection])
        for point in selection:
            layer[point[2]] = minimum
        self.parent.layer = layer

class Maximizator(Processor):
    def __init__(self, window):
        Processor.__init__(self, window, "Maximize selection", shortcut="<Alt-U>", picto="../data/resources/btns/up.png")
    def process(self, layer, selection):
        maximum = max([layer[point[2]] for point in selection])
        for point in selection:
            layer[point[2]] = maximum
        self.parent.layer = layer
        
class MouseRegulator(Processor):
    def __init__(self, window, sensivity=90):
        Processor.__init__(self, window, "Roll", shortcut="<MouseWheel>", picto="../data/resources/btns/roll.png")
        self.sensivity = sensivity
        self.step = None
    def process_input(self, event):
        if event.num < 4 or event.num > 5 or abs(event.delta) < self.sensivity: return
        self.step = int(event.delta / self.sensivity) 
    def process(self, layer, selection):
        for point in selection:
            layer[point[2]] += self.step

# tols

def update_selection(layer, selection, new_value):
    for i in selection:
        layer[i] = new_value
    return layer
