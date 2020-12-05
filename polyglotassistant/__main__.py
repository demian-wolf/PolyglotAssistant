import tkinter as tk
import tkinter.ttk as ttk
import argparse

from readit.menus import MENUBAR
from automenu import AutoMenu
from style import AppStyles


class Main(tk.Tk):
    def __init__(self, args=None):
        super().__init__()

        apps_args = {args.editor: "Editor",
                     args.readit: "ReadIt",
                     args.trainer: "Trainer"}

        if True in args:
            self.withdraw()
            print(apps_args[True], args.files)
            self.destroy()
            return

        AppStyles(self).apply()
        TestingToplevel(self)

        #MainMenu().pack(fill="both")

class TestingToplevel(tk.Toplevel):
    def __init__(self, master):
        super().__init__()

        self.title("HAHA")
        menu = AutoMenu(self, MENUBAR)
        self.config(menu=menu)

        ttk.Button(self, text="Button").pack()

class MainMenu(tk.Frame):
    def __init__(self):
        super().__init__()

    
parser = argparse.ArgumentParser()

app_group = parser.add_mutually_exclusive_group(required=False)
app_group.add_argument("-e", "--editor",
                       action="store_true",
                       help="launch the Editor")
app_group.add_argument("-r", "--readit",
                       action="store_true",
                       help="launch the ReadIt")
app_group.add_argument("-t", "--trainer",
                       action="store_true",
                       help="launch the Trainer")

parser.add_argument("files", nargs="*")

Main(args=parser.parse_args()).mainloop()
