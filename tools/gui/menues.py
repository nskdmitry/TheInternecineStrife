import tkinter as tk

class MainMenu(tk.Menu):
    self __init__(self, master)
        tk.Menu.__init__(self, master)
        master.config(menu=self)
        self.addSubmenuFile()
        self.addSubmenuVisual()
        self.addSubmenuTools()
        self.addSubmenuWindows()
        self.addSubmenuHelp()
    def addSubmenuFile(self):
        file_menu = tk.Menu(self)
        file_menu.add_command(label=res.str_resources[66], command=lambda: self.master.new(None))
        file_menu.add_command(label=res.str_resources[4], underline=4, command=lambda: self.master.regen(None))
        file_menu.add_command(label=res.str_resources[5], underline=0, command=lambda: self.master.openMap(None))
        file_menu.add_separator()
        file_menu.add_command(label=res.str_resources[6], underline=0, command=lambda: self.master.save(None))
        file_menu.add_command(label=res.str_resources[7], command=lambda: self.master.saveAs(None))
        file_menu.add_separator()
        file_menu.add_command(label=res.str_resources[8], underline=0, command=lambda: self.master.exit(None))
        self.add_cascade(label=res.str_resources[9], menu=file_menu, underline=0)
        return file_menu
    def addSubmenuVisual(self):
        visual_menu = tk.Menu(self)
        visual_menu.add_radiobutton(label=res.str_resources[69], var=master.showAs, value=master.SHOW_MODE_IMAGE, command=lambda: self.updMode(None))
        visual_menu.add_radiobutton(label=res.str_resources[11], var=master.showAs, value=master.SHOW_MODE_VALUES, command=lambda: self.updMode(None))
        self.add_cascade(label=res.str_resources[10], menu=visual_menu, underline=0)
    def addSubmenuTools(self):
        tools_menu = tk.Menu(self)
        select_menu = tk.Menu(tools_menu)
        set_tool = lambda: master.updTool(None)
        select_menu.add_radiobutton(label=res.str_resources[12], var=master.tool, value=ctrls.SelectionTool.USE_TOOL_GET, command=set_tool, underline=1)
        select_menu.add_radiobutton(label=res.str_resources[13], var=master.tool, value=ctrls.SelectionTool.USE_TOOL_SELECT, command=set_tool, underline=1)
        select_menu.add_radiobutton(label=res.str_resources[14], var=master.tool, value=ctrls.SelectionTool.USE_TOOL_RECT, command=set_tool, underline=1)
        tools_menu.add_cascade(label=res.str_resources[15], menu=select_menu)
        mouse_menu = tk.Menu(tools_menu)
        mouse_menu.add_radiobutton(label=res.str_resources[16], var=master.tool, value=ctrls.Processor.USE_TOOL_PEN, command=set_tool, underline=0)
        mouse_menu.add_radiobutton(label=res.str_resources[17], var=master.tool, value=ctrls.Processor.USE_TOOL_FILL, command=set_tool)
        tools_menu.add_cascade(label=res.str_resources[18], menu=mouse_menu, underline=1)
        self.add_cascade(label=res.str_resources[19], menu=tools_menu, underline=0)
    def addSubmenuWindows(self):
        windows_menu = tk.Menu(self)
        windows_menu.add_command(label=res.str_resources[25], command=master.showMeta)
        windows_menu.add_command(label=res.str_resources[26], underline=0, command=master.showDomains)
        windows_menu.add_command(label=res.str_resources[27], underline=0, command=mastr.showHierarchy)
        windows_menu.add_command(label=res.str_resources[28], underline=0, command=master.showMarks)
        self.add_cascade(label=res.str_resources[29], menu=windows_menu)
    def addSubmenuHelp(self):
        pass