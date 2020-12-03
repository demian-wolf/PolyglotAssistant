import tkinter as tk
from functools import partial

import readit.menus as menus


class AutoMenu(tk.Menu):
    def __init__(self, master, scheme, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        for label, data in scheme:
            underline, label = self._underline_and_label(label)
            self.add_cascade(label=label,
                             menu=self._submenu(self, data),
                             underline=underline)

    def _underline_and_label(self, label):
        underline = None
        if "&" in label:
            underline = label.find("&")
        label = label.replace("&", "")
        return underline, label

    def _submenu(self, parent, scheme):
        current = tk.Menu(parent)
        for item in scheme:
            if item is None:  # separator
                current.add_separator()
                continue
            if isinstance(item, tuple):
                if isinstance(item[1], tuple):  # submenu
                    label, submenu = item
                    underline, label = self._underline_and_label(label)
                    current.add_cascade(label=label,
                                        menu=self._submenu(current, submenu),
                                        underline=underline)
                    continue
                # command
                label, event, accelerator = item
                underline, label = self._underline_and_label(label)
                command = partial(self.event_generate, event)
                current.add_command(label=label, command=command,
                                    underline=underline,
                                    accelerator=accelerator)
                # TODO: bind the command to the accelerator
        return current

def _test():
    root = tk.Tk()

    MENU_OPTIONS = {"*Menu.activeBackground": "#3DAEE9",
                    "*Menu.background": "#EFF0F1",
                    "*Menu.activeBorderWidth": 0,
                    "*Menu.borderWidth": 1,
                    "*Menu.tearOff": False,
                    "*Menu.relief": "flat"}

    for option, value in MENU_OPTIONS.items():
        root.option_add(option, value)

    menubar = AutoMenu(root, menus.MENUBAR)
    root.config(menu=menubar)

    root.mainloop()

if __name__ == "__main__":
    _test()