import tkinter as tk
import tkinter.ttk as ttk


class AppStyles(object):
    def __init__(self, master):
        self.master = master

        NORMAL_BG = "#EFF0F1"
        ACTIVE_BG = "#3DAEE9"
        ACTIVE_FG = "black"

        self.options = {"*Menu.activeBackground": ACTIVE_BG,
                        "*Menu.background": NORMAL_BG,
                        "*Menu.activeBorderWidth": 0,
                        "*Menu.borderWidth": 1,
                        "*Menu.tearOff": False,
                        "*Menu.relief": "flat"}

        self.ttk_theme = "alt"
        self.ttk_styles = [] # [("TButton", {"background": NORMAL_BG})]
        self.ttk_styles_maps = [('TButton',
                                {"background": [("active", ACTIVE_BG)],
                                 "foreground": [("active", ACTIVE_FG)]})]

    def apply(self):
        for option, value in self.options.items():
            self.master.option_add(option, value)

        self.master.style = ttk.Style(self.master)

        self.master.style.theme_use(self.ttk_theme)

        for name, style in self.ttk_styles:
            self.master.style.configure(name, **style)

        for name, style in self.ttk_styles_maps:
            self.master.style.map(name, **style)