#!/usr/bin/python3
from tkinter import *
from tkinter.messagebox import showinfo, _show as show_msg
from tkinter.filedialog import *
from tkinter.ttk import Treeview, Entry


class Trainer(Tk):
    def __init__(self):
        super().__init__()
        self.title("Home - LearnWords 1.0 Trainer")
        self.resizable(False, False)

        self.menubar = Menu(self, tearoff=False)
        self.filemenu = Menu(self.menubar, tearoff=False)
        self.filemenu.add_command(label="Open", accelerator="Ctrl+O")
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", accelerator="Alt+F4")
        self.menubar.add_cascade(label="File", menu=self.filemenu)
        self.toolsmenu = Menu(self.menubar, tearoff=False)
        self.toolsmenu.add_command(label="Configuration", accelerator="Ctrl+Alt+Shift+C")
        self.menubar.add_cascade(label="Tools", menu=self.toolsmenu)
        self.helpmenu = Menu(self.menubar, tearoff=False)
        self.helpmenu.add_command(label="LearnWords Help")
        self.helpmenu.add_separator()
        self.helpmenu.add_command(label="About LearnWords")
        self.helpmenu.add_command(label="Contact me")
        self.menubar.add_cascade(label="Help", menu=self.helpmenu)
        self.config(menu=self.menubar)

        self.wtree = Treeview(self, show="headings", columns=["word", "translation"], selectmode=EXTENDED)
        self.wtree.heading("word", text="Word")
        self.wtree.heading("translation", text="Translation")
        self.wtree.grid(row=0, column=0, columnspan=7, sticky="ew")

        self.guessedb = Button(self, text="Guessed: ?", bg="green")
        self.guessedb.grid(row=1, column=0, sticky="ew")
        self.unguessedb = Button(self, text="Unguessed: ?", bg="red")
        self.unguessedb.grid(row=1, column=1, sticky="ew")
        self.nontriedb = Button(self, text="Non-tried: ?", bg="yellow")
        self.nontriedb.grid(row=1, column=2, sticky="ew")
        self.totallyb = Button(self, text="Totally: ?", bg="white")
        self.totallyb.grid(row=1, column=3, sticky="ew")
        Label(self, text="Words a game: ").grid(row=1, column=4, sticky="ew")
        self.wag_entry = Entry(self, width=3)
        self.wag_entry.grid(row=1, column=5, sticky="ew")
        Button(self, text="Start").grid(row=1, column=6, sticky="ew")

if __name__ == "__main__":
    Trainer().mainloop()