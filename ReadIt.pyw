from tkinter import *
from tkinter.messagebox import *
from tkinter.ttk import Combobox


class Main(Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("ReadIt 1.0")

        self.menubar = Menu(self)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.textbox = Text(self)
        self.textbox.grid(row=0, column=0, sticky="nswe")
        
        self.trans_bar = Frame(self)
        self.trans_bar.grid(row=0, column=1, sticky="nswe")
        Label(self.trans_bar, text="Панель перекладача").grid(row=0, column=0, columnspan=3, sticky="nswe")
        Label(self.trans_bar).grid(row=1, column=0)
        Combobox(self.trans_bar).grid(row=2, column=0)
        Button(self.trans_bar, text="⮂").grid(row=2, column=1)
        Combobox(self.trans_bar).grid(row=2, column=2)
        Label(self.trans_bar, text="Слово:").grid(row=3, column=0)
        Entry(self.trans_bar).grid(row=3, column=0, columnspan=2, sticky="nswe")

if __name__ == "__main__":
    Main().mainloop()
