#!/usr/bin/python3
from tkinter import *

from Editor import Editor
from Trainer import Trainer


class StartDialog(Tk):
    def __init__(self):
        super().__init__()
        self.title("LearnWords 1.0")
        self.resizable(False, False)
        self.create_wgts()
    def create_wgts(self):
        Label(self, text="What do you want to use?", width=20).grid()
        Button(self, text="Editor", width=20, command=self.open_editor).grid()
        Button(self, text="Trainer", width=20).grid()
    def open_editor(self):
        self.withdraw()
        Editor().mainloop()
        self.deiconify()
    def open_trainer(self):
        self.withdraw()
        Trainer().mainloop()
        self.deiconify()

if __name__ == "__main__":
    StartDialog().mainloop()
