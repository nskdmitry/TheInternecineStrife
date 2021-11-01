import tkinter as tk
import gui.resources as res
import gui.controls as ctrls

### Value Setting Controllers

class ValuePallette(tk.LabelFrame):
    """ Dynamic render panel with imaged buttons of value. """
    
    def __init__(self, parent, layer, width=200, callback=None):
        tk.LabelFrame.__init__(self, parent, text=res.str_resources[100], cursor="hand", visual=False, width=width, height=parent.height-60, bd=2, relief=tk.RIDGE)
        self.variants = []
        self.current = tk.IntVar(value=1)
        self.curr_layer = layer
        self.master_callback = callback if callback is callable else lambda layer: layer
    def widgets_render(self, pallette=None):
        """ Reset a range of values (pallette) """
        self.visual = False
        self.variants.clear()
        if pallette is None:
            return
        rended = tk.Canvas("20x20")
        index = 0
        in_row_count = int(self.width / 20)
        for valueObj in pallette:
            rended.create_rectangle(0,0,20,20, fill=valueObj.Color)
            colorette = tk.Button(self, command=lambda e: self.select_one, image=rended.render(), relief=tk.RELIEFS.flat)
            colorette.value_id = valueObj.Id
            colorette.grid(row=int(index / in_row_count), column=index%in_row_count)
            self.variants.append(colorette)
        self.visual = True
    def select_one(self, e, sender):
        """ Trigger of all of buttons. """
        self.current.set(sender.value_id)
        self.curr_layer = ctrls.update_selection(self.curr_layer, self.master.section, sender.value_id)
        self.master_callback(self.curr_layer)

class ValueReglator(tk.LabelFrame):
    """ Slider and buttons to set a value of cell. """
    
    def __init__(self, parent, layer, width=200, callback=lambda updated_layer: updated_layer):
        tk.Frame.__init__(self, parent, cursor="hand", text=res.str_resources[100], visual=False, width=width, height=40, bd=2, relief=tk.RIDGE)
        self.curr_layer = layer
        self.master_callback = callback
        self.setValue = tk.IntVar(value=0)
        self.spinnable = tk.StringVar(value=tk.IntVar.get)
        self.dia = (0, 100)
        
        self.valuer = tk.Scale(master=self, from_=self.dia[0], to=self.dia[1], resolution=1, variable=self.setValue, tickinterval=4, command=self.updValue, orient=tk.HORIZONTAL)
        self.valueControl = tk.Spinbox(master=self, from_=self.dia[0], to=self.dia[1], increment=1, width=5, textvariable=self.spinnable, command=lambda: self.updValue(self.valueControl.get()))
        self.addOne = tk.Button(master=self, text="+1", command=lambda: self.modify(+1))
        self.subOne = tk.Button(master=self, text="-1", command=lambda: self.modify(-1))
        self.add10 = tk.Button(master=self, text="+10", command=lambda: self.modify(+10))
        self.sub10 = tk.Button(master=self, text="-10", command=lambda: self.modify(-10))
        self.add100 = tk.Button(master=self, text="+100", command=lambda: self.modify(+100))
        self.sub100 = tk.Button(master=self, text="-100", command=lambda: self.modify(-100))
        
        self.sub100.grid(row=0, column=0)
        self.sub10.grid(row=0, column=1)
        self.subOne.grid(row=0, column=2)
        self.valueControl.grid(row=0, column=3)
        self.valuer.grid(row=0, column=4, columnspan=3)
        self.addOne.grid(row=0, column=7)
        self.add10.grid(row=0, column=8)
        self.add100.grid(row=0, column=9)
    # Out-callable methods
    def init(self, layer, value=None):
        """ Select another cell or another layer """
        self.curr_layer = layer
        area = self.master.section
        be_compute = len(area) > 0
        self.dia = (mn, mx) = (min([layer[i] for i in area]) if be_compute else 0, max([layer[i] for i in area]) if be_compute > 0 else 10)
        if value is None:
            if len(self.master.section) == 1:
                value = layer[self.master.section[0]]
            else:
                value = (mx + mn) / 2
        self.updValue(self.valueControl.get())
        self.widgets_render()
    def widgets_render(self):
        """ Updare a limits and show/hide scale-refered buttons. """
        (bottom, top) = self.dia
        self.valuer.config(from_=bottom, to=top)
        self.valueControl.config(from_=bottom, to=top)
        # Show/Hide scalle-related buttons
        self.sub100.config(visual=bottom>100)
        self.sub10.config(visual=bottom>10)
        self.add10.config(visual=top>10)
        self.add100.config(visual=top>100)
    # Triggers
    def updValue(self, value):
        """ Trigger of Valuer Scale """
        val = int(event)
        self.spinnable.set(val)
        val1 = self.valuer.get()
        if val != val1:
            self.valuer.set(val)
        # Set value of cell
        if len(self.selection) > 0:
            if val != val1:
                shift = val - val1
                ctrls.update_selection(self.curr_layer, self.master.selection, val)
                self.master_callback(self.curr_layer)
        return
    def modify(self, shift):
        """ Trigger of Scale-Refered Buttons """
        updated = self.setValue.get() + shift
        self.setValue.set(updated)
        outbound = False
        if updated > self.dia[1]:
            self.dia = (self.dia[0], updated)
            outbound = True
        elif updated < self.dia[0] and updated > -1:
            self.dia = (updated, self.dia[1])
            outbound = True
        if outbound:
            self.widgets_render()
        ctrls.update_selection(self.curr_layer, self.master.selection, updated)
        self.master_callback(self.curr_layer)

### Tool panels
# Abstract
class ToolPanel(tk.Frame):
    def __init__(self, master, tools=[]):
        tk.Frame.__init__(self, master, cursor="hand", visual=len(tools)>0)
        self._options = tools
        self.buttons = []
        for tool in tools:
            clicker = tk.Button(self, img=tool.sign, command=tool._input)
            clicker.pack()
            self.buttons.append(clicker)
        return
    def _tools_factory(self, master, toolname):
        """ Create instance of tool handler by name of class """
        cls = getattr(ctrls, toolname)
        return cls(master)
    def _tool_init(self, master, refs=dict(), on=set()):
        return [ToolPanel._tools_factory(self, master, refs[code]) for code in on]

class SelectionToolPanel(ToolPanel):
    REF = {ctrls.SelectionTool.USE_TOOL_GET: "SelectionSingle", ctrls.SelectionTool.USE_TOOL_CLEAR: "SelectionCancel", ctrls.SelectionTool.USE_TOOL_INVERSE: "SelectionInverse"}

    def __init__(self, master, on={0,1,2,3,4,5,6}):
        SelectionToolPanel.REF[ctrls.SelectionTool.USE_TOOL_SELECT] = "SelectionOneByOne"
        SelectionToolPanel.REF[ctrls.SelectionTool.USE_TOOL_RECT] = "SelectionRect"
        SelectionToolPanel.REF[ctrls.SelectionTool.USE_WAND] = "SelectionMagicWand"
        SelectionToolPanel.REF[ctrls.SelectionTool.USE_LIKE] = "SelectionAllAs"
        
        tools = ToolPanel._tool_init(self, master, SelectionToolPanel.REF, on)
        self.shows = on
        
        ToolPanel.__init__(self, master, tools)
