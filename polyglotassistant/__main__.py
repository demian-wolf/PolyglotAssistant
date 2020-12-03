import tkinter as tk
import tkinter.ttk as ttk
import argparse


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
        
        MainMenu().pack(fill="both")

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
