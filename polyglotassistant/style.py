import tkinter as tk
import tkinter.ttk as ttk


class AppStyles(object):
    def __init__(self, master):
        self.master = master

        self.options = {"*Menu.activeBackground": "#3DAEE9",
                        "*Menu.background": "#EFF0F1",
                        "*Menu.activeBorderWidth": 0,
                        "*Menu.borderWidth": 1,
                        "*Menu.tearOff": False,
                        "*Menu.relief": "flat"}

        self.ttk_styles = [("TButton", {"padding": 6,
                                        "relief": "flat",
                                        "background": "blue"})]
        self.ttk_styles_maps = [('TButton',
                                {"background": [('active', '#3DAEE9')],
                                 "foreground": [('active', 'black')]})]

    def apply(self):
        for option, value in self.options.items():
            self.master.option_add(option, value)

        self.master.style = ttk.Style(self.master)

        for name, style in self.ttk_styles:
            self.master.style.configure(name, **style)

        for name, style in self.ttk_styles_maps:
            self.master.style.map(name, **style)