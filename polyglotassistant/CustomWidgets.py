from tkinter.ttk import Entry


class Spinbox(Entry):

    def __init__(self, master=None, **kwargs):
        super().__init__(master, "ttk::spinbox", **kwargs)

    def set(self, value):
        self.tk.call(self._w, "set", value)
