import tkinter.ttk as ttk


class Spinbox(ttk.Entry):
    """A workaround for ttk.Spinbox on some versions of Python."""

    def __init__(self, master=None, **kwargs):
        super().__init__(master, "ttk::spinbox", **kwargs)

    def set(self, value):
        self.tk.call(self._w, "set", value)
