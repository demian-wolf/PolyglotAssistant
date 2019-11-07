#!/usr/bin/python3

# (C) Demian Wolf, 2019
# email: demianwolfssd@gmail.com

from tkinter import *
from tkinter.messagebox import showinfo, showerror, _show as show_msg
import sys

from PIL import Image
import pystray

# from Trainer import Trainer
from EditorFrame import EditorFrame
from utils import yesno2bool, help_, about, contact_me, validate_lwp_data


class Editor(Tk):
    def __init__(self, *args, lwp_filename=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.protocol("WM_DELETE_WINDOW", self.close_command)  # ask yes/no/cancel before exit
        
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.editor_frame = EditorFrame()
        self.editor_frame.grid(sticky="nswe")
        self.editor_frame.set_saved(True)
        
        # Create menu at the top of the main window
        self.menubar = Menu(self, tearoff=False)  # create the menubar
        self.config(menu=self.menubar)  # set the menubar widget for the main window
        
        # Create the "File" menu
        self.filemenu = Menu(self.menubar, tearoff=False)
        self.filemenu.add_command(label="New", command=self.editor_frame.new, accelerator="Ctrl+N")
        self.filemenu.add_command(label="Open", command=self.editor_frame.open_, accelerator="Ctrl+O")
        self.filemenu.add_command(label="Save", command=self.editor_frame.save, accelerator="Ctrl+S")
        self.filemenu.add_command(label="Save As", command=self.editor_frame.save_as, accelerator="Ctrl+Shift+S")
        self.filemenu.add_command(label="Statistics", command=self.statistics)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Hide to tray", command=self.hide_to_tray)
        self.filemenu.add_command(label="Exit", command=self.exit_, accelerator="Alt+F4")
        self.menubar.add_cascade(menu=self.filemenu, label="File")
        # Create the "Edit" menu
        self.editmenu = Menu(self.menubar, tearoff=False)
        self.editmenu.add_command(label="Add", command=self.editor_frame.add, accelerator="Ctrl+Alt+A")
        self.editmenu.add_command(label="Edit", command=self.editor_frame.edit, accelerator="Ctrl+Alt+E")
        self.editmenu.add_command(label="Remove", command=self.editor_frame.remove, accelerator="Del")
        self.editmenu.add_command(label="Clear", command=self.editor_frame.clear, accelerator="Shift+Del")
        self.editmenu.add_separator()
        self.editmenu.add_command(label="Train Now!", command=self.editor_frame.train_now, accelerator="Ctrl+Alt+T")
        self.menubar.add_cascade(menu=self.editmenu, label="Edit")
        # Create the "Help" menu
        self.helpmenu = Menu(self.menubar, tearoff=False)
        self.helpmenu.add_command(label="LearnWords Help", command=help_, accelerator="F1")
        self.helpmenu.add_separator()
        self.helpmenu.add_command(label="About LearnWords", command=about, accelerator="Ctrl+F1")
        self.helpmenu.add_command(label="Contact me", command=contact_me, accelerator="Ctrl+Shift+F1")
        self.menubar.add_cascade(menu=self.helpmenu, label="Help")

        self.iconbitmap("icon_32x32.ico")
        
        self.bind("<F1>", help_)
        self.bind("<Control-F1>", about)
        self.bind("<Control-Shift-F1>", contact_me)
        for key in ("NOS", "nos"):
            self.bind("<Control-%s>" % key[0], self.editor_frame.new)
            self.bind("<Control-%s>" % key[1], self.editor_frame.open_)
            self.bind("<Control-%s>" % key[2], self.editor_frame.save)
            self.bind("<Control-Shift-%s>" % key[2], self.editor_frame.save_as)
            
        if lwp_filename:
            self.editor_frame.open_(lwp_filename=lwp_filename)
        
    def statistics(self):
        if self.editor_frame.wtree.get_children():
            alphabet_dict = {}
            for word_pair in self.editor_frame.wtree.get_children():
                first_letter = self.editor_frame.wtree.item(word_pair)["values"][0][0].upper()
                if first_letter in alphabet_dict:
                    alphabet_dict[first_letter] += 1
                else:
                    alphabet_dict[first_letter] = 1
            result_list = ["By first letters:"]
            result_list.extend(["{} - {}".format(first_letter, count) for first_letter,
                                                                          count in sorted(alphabet_dict.items())])
            result_list.append("\nTotally: {}".format(len(self.editor_frame.wtree.get_children())))
            showinfo("Statistics", ("\n".join(result_list)))
        else:
            showinfo("Statistics", "There are no words in the vocabulary. Add some at first.")

    def close_command(self):
        # TODO: config onclose-command (to tray/exit)           
        if True:
            self.hide_to_tray()
        else:
            self.exit_()

    def hide_to_tray(self):
        self.withdraw()
        self.tray_icon = pystray.Icon("EditorTrayIcon", title="LearnWords Editor")
        self.tray_icon.icon = Image.open("icon_32x32.ico")
        self.tray_icon.menu = pystray.Menu(pystray.MenuItem("Розгорнути", lambda: self.tray_icon.stop(), default=True),
                                       pystray.MenuItem("Вийти", lambda: self.tray_exit()))
        self.tray_icon.run()
        self.deiconify()
        self.focus_force()
        
    def tray_exit(self):
        self.tray_icon.stop()
        self.after(0, self.exit_)
        
    def exit_(self):
        """Exits the app."""
        if self.editor_frame.can_be_closed():
            self.destroy()

    def update_title(self):
        """Updates the title of the app."""
        self.title("%s%s - LearnWords 1.0 Editor" % (self.editor_frame.unsaved_prefix, self.editor_frame.filename))

if __name__ == "__main__":
    Editor(lwp_filename=sys.argv[-1] if len(sys.argv) > 1 else None).mainloop()
