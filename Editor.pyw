#!/usr/bin/python3
from tkinter import *
from tkinter.messagebox import showinfo, showerror, _show as show_msg
from tkinter.filedialog import *
from tkinter.ttk import Treeview, Entry
import pickle

from Trainer import Trainer
from utils import yesno2bool, contact_me, validate_lwp_data

UNTITLED = "Untitled"


class Editor(Tk):
    def __init__(self):
        super().__init__()
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.exit_)
        self.saved = None
        self.unsaved_prefix = None
        self.filename = UNTITLED
        self.set_saved(True)

        self.menubar = Menu(self, tearoff=False)
        self.config(menu=self.menubar)
        self.filemenu = Menu(self.menubar, tearoff=False)
        self.filemenu.add_command(label="New", command=self.new, accelerator="Ctrl+N")
        self.filemenu.add_command(label="Open", command=self.open_, accelerator="Ctrl+O")
        self.filemenu.add_command(label="Save", command=self.save, accelerator="Ctrl+S")
        self.filemenu.add_command(label="Save As", command=self.save_as, accelerator="Ctrl+Shift+S")
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=self.exit_, accelerator="Alt+F4")
        self.menubar.add_cascade(menu=self.filemenu, label="File")
        self.editmenu = Menu(self.menubar, tearoff=False)
        self.editmenu.add_command(label="Add", command=self.add, accelerator="Ctrl+Alt+A")
        self.editmenu.add_command(label="Edit", command=self.edit, accelerator="Ctrl+Alt+E")
        self.editmenu.add_command(label="Remove", command=self.remove, accelerator="Ctrl+Alt+R")
        self.editmenu.add_command(label="Clear", command=self.clear, accelerator="Ctrl+Alt+C")
        self.editmenu.add_separator()
        self.editmenu.add_command(label="Train Now!", command=self.train_now, accelerator="Ctrl+Alt+T")
        self.menubar.add_cascade(menu=self.editmenu, label="Edit")
        self.helpmenu = Menu(self.menubar, tearoff=False)
        self.helpmenu.add_command(label="LearnWords Help", command=self.help, accelerator="F1")
        self.helpmenu.add_separator()
        self.helpmenu.add_command(label="About LearnWords", command=self.about, accelerator="Ctrl+F1")
        self.helpmenu.add_command(label="Contact me", command=contact_me, accelerator="Ctrl+Alt+F1")
        self.menubar.add_cascade(menu=self.helpmenu, label="Help")

        self.wtree = Treeview(self, show="headings", columns=["word", "translation"], selectmode=EXTENDED)
        self.wtree.heading("word", text="Word")
        self.wtree.heading("translation", text="Translation")
        self.wtree.grid(row=0, column=0, columnspan=5, sticky="nsew")
        self.scrollbar = Scrollbar(self, command=self.wtree.yview)
        self.scrollbar.grid(row=0, column=6, sticky="ns")
        self.wtree.config(yscrollcommand=self.scrollbar.set)
        Button(self, text="Add", command=self.add).grid(row=1, column=0, sticky="ew")
        Button(self, text="Edit", command=self.edit).grid(row=1, column=1, sticky="ew")
        Button(self, text="Remove", command=self.remove).grid(row=1, column=2, sticky="ew")
        Button(self, text="Clear", command=self.clear).grid(row=1, column=3, sticky="ew")
        Button(self, text="Train Now!", command=self.train_now).grid(row=1, column=4, columnspan=3, sticky="ew")

    def _tocontinue(self):
        if not self.saved:
            result = show_msg("Warning", "Do you want to save your learning plan?", "warning", "yesnocancel")
            if result == "yes":
                self.save()
                return self.saved
            elif result == "no":
                return True
            return False
        return True

    def new(self):
        if self._tocontinue():
            self.wtree.delete(*self.wtree.get_children())
            self.filename = UNTITLED
            self.set_saved(True)

    def open_(self):
        if self._tocontinue():
            try:
                lwp_file = askopenfile(mode="rb", filetypes=[("LearnWords Plan", "*.lwp")])
            except:
                showerror("Error", "Couldn't open the file. Check file location and your permission to open it.")
            else:
                if lwp_file:
                    try:
                        lwp_data = pickle.load(lwp_file)
                    except PermissionError:
                        showerror("Error", "Unable to access this file! Check your permissions for reading.")
                    except pickle.UnpicklingError as error:
                        showerror("Error", "The file is corrupted or has an unsupported format!\n\nDetails: {}".format(error))
                    else:
                        try:
                            validate_lwp_data(lwp_data)
                        except AssertionError:
                            showerror("Error", "The file is corrupted or has an unsupported format!\n\nDetails: invalid object is pickled.")
                        else:
                            for pair in lwp_data:
                                self.wtree.insert("", END, values=pair)
                            self.set_saved(True)
                            self.filename = lwp_file.name
                            self.update_title()

    def save(self):
        if self.filename != UNTITLED:
            try:
                outfile = open(self.filename, "wb")
                pickle.dump([list(map(str, self.wtree.item(child)["values"])) for child in self.wtree.get_children()], outfile)
                outfile.close()
                self.filename = outfile.name
                self.set_saved(True)
            except:
                showerror("Error", "Sorry, an unexpected error occurred!")
        else:
            self.save_as()

    def save_as(self):
        try:
            outfile = asksaveasfile(mode="wb", defaultextension=".", filetypes=[("LearnWords Plan", ".lwp")])
        except:
            showerror("Error", "Couldn't open the file. Probably, it doesn't exists or you have not permissions")
        else:
            if outfile:
                try:
                    pickle.dump([list(map(str, self.wtree.item(child)["values"])) for child in self.wtree.get_children()], outfile)
                except:
                    showerror("Error", "Sorry, an unexpected error occurred!")
                else:
                    outfile.close()
                    self.filename = outfile.name
                    self.set_saved(True)

    def exit_(self):
        if self._tocontinue():
            self.destroy()

    def add(self):
        to_add = Edit("Add")
        if to_add.data:
            self.wtree.insert("", END, values=to_add.data)
            self.set_saved(False)

    def edit(self):
        selection = self.wtree.selection()
        if len(selection) == 0:
            showinfo("Information", "Select a \"word-translation\" couple at first!")
        elif len(selection) > 1:
            showinfo("Information",
                     "Select only ONE \"word-translation\" couple - you selected {}".format(len(selection)))
        else:
            edited = Edit("Edit", *self.wtree.item(selection[0])["values"])
            if edited.data:
                old_id = self.wtree.get_children().index(selection[0])
                self.wtree.delete(selection[0])
                self.wtree.insert("", old_id, values=edited.data)
                self.set_saved(False)

    def remove(self):
        if self.wtree.selection():
            if yesno2bool(show_msg("Warning",
                                   "All selected words' couples will be permanently deleted. Do you want to continue?\nNote this action cannot be undone!",
                                   "warning", "yesno")):
                self.wtree.delete(*self.wtree.selection())
                self.set_saved(False)
        else:
            showinfo("Information",
                     "Choose something at first.\nIf you want to remove all the words from the list, click \"Clear\"")

    def clear(self):
        if self.wtree.get_children():
            if yesno2bool(show_msg("Warning",
                                   "All the couples from this list will be permanently deleted. Do you want to continue?\nNote this action cannot be undone!",
                                   "warning", "yesno")):
                self.wtree.delete(*self.wtree.get_children())
                self.set_saved(False)
        else:
            showinfo("Information", "The list is empty. Is it already cleared?")

    def train_now(self):
        pass

    def help(self):
        pass

    def about(self):
        showinfo("About LearnWords",
                 "LearnWords 1.0 (C) Demian Wolf, 2019\nLearnWords is an easy way to learn words of foreign language - convenient learning plan editor and smart autotrainer.\nProgram licensed AS-IS\nThank you for using my program!")

    def set_saved(self, state):
        if state:
            self.saved = True
            self.unsaved_prefix = ""
        else:
            self.saved = False
            self.unsaved_prefix = "*"
        self.update_title()

    def update_title(self):
        self.title("{}{} - LearnWords 1.0 Editor".format(self.unsaved_prefix, self.filename))


class Edit(Toplevel):
    def __init__(self, title, word=None, translation=None):
        super().__init__()
        self.title(title)
        self.resizable(False, False)
        Label(self, text="Word:").grid(row=0, column=0)
        self.word_entry = Entry(self)
        self.word_entry.grid(row=0, column=1)
        self.word_entry.focus()
        self.word_entry.bind("<Return>", lambda event=None: self.translation_entry.focus())
        Label(self, text="Translation:").grid(row=1, column=0)
        self.translation_entry = Entry(self)
        self.translation_entry.grid(row=1, column=1)
        self.translation_entry.bind("<Return>", self.ok)
        Button(self, text="OK", command=self.ok).grid(row=2, column=0, columnspan=2, sticky="ew")
        if word:
            self.word_entry.insert(END, word)
        if translation:
            self.translation_entry.insert(END, translation)
        self.data = None
        self.wait_window()

    def ok(self, event=None):
        self.data = (self.word_entry.get(), self.translation_entry.get())
        self.destroy()


if __name__ == "__main__":
    Editor().mainloop()
