#!/usr/bin/python3

from tkinter import *
from tkinter.messagebox import showinfo, showerror
import os
import sys

from PIL import Image
import pystray

from EditorFrame import EditorFrame
from Hotkeys import HKManager
from utils import help_, about, contact_me, set_window_icon
exec("from lang.%s import LANG" % "ua")


class Editor(Tk):
    """
    The Editor's main class.

    :param vocabulary_filename: the vocabulary filename from the command line (optional)
    :type vocabulary_filename: str
    :return: no value
    :rtype: none
    """

    def __init__(self, *args, vocabulary_filename=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.hk_man = HKManager(self)  # create the hotkeys manager
        self.create_wgts()
        self.create_menu()
        self.bind_keybindings()
        set_window_icon(self)
        self.protocol("WM_DELETE_WINDOW", self.exit)

        if vocabulary_filename:
            self.vocabulary_editor.open(vocabulary_filename=vocabulary_filename)

    def create_wgts(self):
        """
        This method creates the widgets.

        :return: no value
        :rtype: none
        """
        
        # Configure rows and columns to let the widgets stretch
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        # Create the vocabulary editor
        self.vocabulary_editor = EditorFrame()
        self.vocabulary_editor.grid(sticky="nswe")  # show it using grid geometry manager
        self.vocabulary_editor.set_saved(True)  # set the vocabulary "saved" state to True

    def create_menu(self):
        """
        This method creates the menu.

        :return: no value
        :rtype: none
        """
        
        # Create menu at the top of the main window
        self.menubar = Menu(self, tearoff=False)  # create the menubar
        self.config(menu=self.menubar)  # set the menubar widget for the main window

        # Create the "File" menu and add the appropriate entries
        self.filemenu = Menu(self.menubar, tearoff=False)
        self.filemenu.add_command(label=LANG["new"], command=self.vocabulary_editor.new, accelerator="Ctrl+N")
        self.filemenu.add_command(label=LANG["open"], command=self.vocabulary_editor.open, accelerator="Ctrl+O")
        self.filemenu.add_command(label=LANG["save"], command=self.vocabulary_editor.save, accelerator="Ctrl+S")
        self.filemenu.add_command(label=LANG["save_as"], command=self.vocabulary_editor.save_as, accelerator="Ctrl+Shift+S")
        self.filemenu.add_separator()
        self.filemenu.add_command(label=LANG["exit"], command=self.exit, accelerator="Alt+F4")
        self.menubar.add_cascade(menu=self.filemenu, label=LANG["file_menu"])
        # Create the "Edit" menu and add the appropriate entries
        self.editmenu = Menu(self.menubar, tearoff=False)
        self.editmenu.add_command(label=LANG["add"], command=self.vocabulary_editor.add, accelerator="Ctrl+Alt+A")
        self.editmenu.add_command(label=LANG["edit"], command=self.vocabulary_editor.edit, accelerator="Ctrl+Alt+E")
        self.editmenu.add_command(label=LANG["remove"], command=self.vocabulary_editor.remove, accelerator="Alt+Del")
        self.editmenu.add_command(label=LANG["clear"], command=self.vocabulary_editor.clear, accelerator="Shift+Del")
        self.editmenu.add_command(label=LANG["reverse"], command=self.vocabulary_editor.reverse,
                                  accelerator="Control+Alt+R")
        self.menubar.add_cascade(menu=self.editmenu, label=LANG["edit_menu"])
        # Create the "Help" menu and add the appropriate entries
        self.helpmenu = Menu(self.menubar, tearoff=False)
        self.helpmenu.add_command(label=LANG["call_help"], command=help_, accelerator="F1")
        self.helpmenu.add_separator()
        self.helpmenu.add_command(label=LANG["about_pa"], command=about, accelerator="Ctrl+F1")
        self.helpmenu.add_command(label=LANG["contact_me"], command=contact_me, accelerator="Ctrl+Shift+F1")
        self.menubar.add_cascade(menu=self.helpmenu, label=LANG["help_menu"])

    def bind_keybindings(self):
        """
        This method binds the key bindings.

        :return: no value
        :rtype: none
        """
        
        # Bind the keybindings
        self.bind("<F1>", help_)
        self.bind("<Control-F1>", about)
        self.bind("<Control-Shift-F1>", contact_me)
        self.hk_man.add_binding("<Control-N>", self.vocabulary_editor.new)
        self.hk_man.add_binding("<Control-O>", self.vocabulary_editor.open)
        self.hk_man.add_binding("<Control-S>", self.vocabulary_editor.save)
        self.hk_man.add_binding("<Control-Shift-S>", self.vocabulary_editor.save_as)

    def exit(self):
        """
        Exits the application.

        :return: no value
        :rtype: none
        """
        
        if self.vocabulary_editor.can_be_closed():
            self.destroy()

    def update_title(self):
        """
        Updates the title of the app.

        :return: no value
        :rtype: none
        """
        
        self.title("%s%s - PolyglotAssistant 1.00 Editor" % (self.vocabulary_editor.unsaved_prefix,
                                                             self.vocabulary_editor.filename))


def show_usage():
    """
    Shows the usage of the command-line interface.

    :return: no value
    :rtype: none
    """
    
    Tk().withdraw()  # creates and hides a dummy window (otherwise, an empty window is shown with the message)
    showerror("Error", LANG["error_clargs_Editor"])  # displays the error


if __name__ == "__main__":
    # Processes the sys.argv list (command-line arguments list)
    if len(sys.argv) == 1:  # if no arguments specified,
        Editor().mainloop()  # run the main window with a new file created
    elif len(sys.argv) == 2:  # if a file was specified,
        Editor(vocabulary_filename=sys.argv[-1]).mainloop()  # open the vocabulary
    else:  # if there were multiple arguments specified,
        show_usage()  # show usage
