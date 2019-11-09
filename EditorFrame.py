from tkinter import *
from tkinter.messagebox import askquestion, showinfo, showerror, _show as show_msg
from tkinter.filedialog import *
from tkinter.ttk import Treeview, Entry, Scrollbar

import pickle

from utils import yesno2bool, validate_lwp_data


class EditorFrame(Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configure weight
        self.rowconfigure(0, weight=1)
        for column_id in range(4):
            self.columnconfigure(column_id, weight=1)
            
        # Create the widget to display the vocabulary words' list and its scrollbar
        self.wtree = Treeview(self, show="headings", columns=["word", "translation"], selectmode=EXTENDED)
        self.wtree.heading("word", text="Word")
        self.wtree.heading("translation", text="Translation")
        self.wtree.grid(row=0, column=0, columnspan=4, sticky="nsew")
        self.scrollbar = Scrollbar(self, command=self.wtree.yview)
        self.scrollbar.grid(row=0, column=6, sticky="ns")
        self.wtree.config(yscrollcommand=self.scrollbar.set)

        # Create the buttons to edit the vocabulary
        Button(self, text="Add", command=self.add).grid(row=1, column=0, sticky="ew")
        Button(self, text="Edit", command=self.edit).grid(row=1, column=1, sticky="ew")
        Button(self, text="Remove", command=self.remove).grid(row=1, column=2, sticky="ew")
        Button(self, text="Clear", command=self.clear).grid(row=1, column=3, sticky="ew")

        # Create a frame for the statusbar
        sbs_frame = Frame(self)
        self.sel_sb = Label(sbs_frame, text="Nothing was selected", relief=RIDGE)
        self.sel_sb.grid(row=0, column=0, sticky="ew")
        self.mod_sb = Label(sbs_frame, text="Unmodified", relief=RIDGE)
        self.mod_sb.grid(row=0, column=1, sticky="ew")
        sbs_frame.grid(row=2, column=0, columnspan=7, sticky="ew")

        # Set the basic values to the class attributes
        self.saved = None
        self.unsaved_prefix = None
        self.filename = "Untitled"

        # Configuring the hotkeys (English only)
        for key in ("AET", "aet"):  # bind keys with letters to work with both UPPERCASE and lowercase English keys       
            self.master.bind("<Control-%s>" % key[0], self.select_all)
            self.master.bind("<Control-Alt-%s>" % key[0], self.add)
            self.master.bind("<Control-Alt-%s>" % key[1], self.edit)
            
        self.master.bind("<Alt-Delete>", self.remove)
        self.master.bind("<Shift-Delete>", self.clear)
        self.master.bind("<Home>", self.select_first)
        self.master.bind("<End>", self.select_last)
        self.master.bind("<Prior>", self.page_up)
        self.master.bind("<Next>", self.page_down)

    def can_be_closed(self):
        """If vocabulary is not saved, and user is trying to create a new one/open another one/quit the app, app asks the user to save the vocabulary."""
        if not self.saved:
            result = show_msg("Warning", "Do you want to save your learning plan?", "warning", "yesnocancel")  # asks about an action
            if result == "yes":  # if user asked to save,
                self.save()  # it saves
                if self.saved:
                    self.wtree.delete(*self.wtree.get_children())  # clear the words list widget
                    return True
            elif result == "no":
                return True
            return False
        return True
    
    def new(self, _event=None):
        """Creates a new vocabulary."""
        if self.can_be_closed():  # if the file can be closed,
            self.wtree.delete(*self.wtree.get_children())  # clear the wtree frame
            self.filename = "Untitled"  # set untitled filename
            self.set_saved(True)  # set the "saved" state
            self.master.update_title()

    def open_(self, _event=None, lwp_filename=None):
        """Opens a vocabulary."""
        if self.can_be_closed():  # if the file can be closed,
            try:  # try to
                if lwp_filename:
                    lwp_file = open(lwp_filename, "rb")
                else:
                    lwp_file = askopenfile(mode="rb", filetypes=[("LearnWords Vocabulary", "*.lwv")])  # ask a LWV (LearnWords Vocabulary) file to open
            except FileNotFoundError as details:  # if submitted file disappeared suddenly
                showerror("Error", "Couldn't open the file. Check file location.\n\nDetails: FileNotFoundError (%s)" % details)
            except PermissionError as details:  # if the access to the file denied
                showerror("Error", "Couldn't open the file. Check your permissions to read it.\n\nDetails: PermissionError (%s)" % details)
            except Exception as details:  # if any other problem happened
                showerror("Error", "During opening the file unexpected error occured\n\nDetails: %s (%s)" % (details.__class__.__name__, details))
            else:  # if all is OK,
                if lwp_file:  # if anything was opened...
                    try:  # try to
                        lwp_data = pickle.load(lwp_file)  # read the vocabulary
                    except pickle.UnpicklingError as details:  # if the file is damaged, or its format is unsupported
                        showerror("Error",
                                  "The file is corrupted or has an unsupported format!\n\nDetails: %s" % details)
                    except Exception as details:  # if unexpected error occured,
                        showerror("Error",
                                  "During opening the file unexpected error occured\n\nDetails: %s (%s)" % (details.__class__.__name__, details))
                    else:  # if the file is unpickleable,
                        try:
                            validate_lwp_data(lwp_data)  # check its format
                        except AssertionError:  # if it is invalid,
                            showerror("Error",
                                      "The file is corrupted or has an unsupported format!\n\nDetails: invalid object is pickled.")
                        else:
                            self.wtree.delete(*self.wtree.get_children())  # clear the words-list,
                            for pair in lwp_data:  # and insert the words from opened vocabulary there
                                self.wtree.insert("", END, values=pair)
                            self.set_saved(True)  # set state to saved
                            self.filename = lwp_file.name  # update the filename value
                            self.master.update_title()  # update the title of the main window

    def _save(self, filename):
        """Provides save mechanism (that basic operation that are repeated both when saving, and saving as."""
        try:  # try to
            outfile = open(filename, "wb")  # try to open a file to write
            pickle.dump([tuple(map(str, self.wtree.item(child)["values"])) for child in self.wtree.get_children()],
                        outfile)  # get the vocabulary content and dump it to selected file
            outfile.close()  # now we can close the outfile
            self.filename = outfile.name  # update the opened file's filename, if changed
            self.set_saved(True)  # set state to saved
        except PermissionError as details:  # if there is a problem with access permissions,
            showerror("Error", "During saving the file an error occured. Check your write permissions\n\nDetails: %s" % details)
        except Exception as details:  # if there is an unexpected problem occured,
            showerror("Error", "During saving the file an unexpected error occured.\n\nDetails: %s (%s)" % (details.__class__.__name__, details))
        
    def save(self, _event=None):
        """Saves the file to the same path and filename, if untitled - calls save as."""
        if self.filename == "Untitled":  # if the file was already saved (even during the other session, and then opened now),
            self.save_as() # save as (to ask user how to name the file)
        else:  # if the file is untitled
            self._save(self.filename)  # save the file with the same filename  
            
    def save_as(self, _event=None):
        try:  # try to
            outfilename = asksaveasfilename(defaultextension=".", filetypes=[("LearnWords Plan", ".lwp")])  # ask a user for the filename to save to
        except Exception as details:  # if an unexpected problem occured,
            showerror("Error", "An unexpected error occured.\n\nDetails: %s (%s)" % (details, details.__class__.__name__))
        else:  # if could get the filename,
            if outfilename:  # if user selected the file (if he canceled the operation, outfilename will equal to None)
                self._save(outfilename)  # save the vocabulary to selected file

    def add_elem(self, elem):
        self.wtree.insert("", END, values=elem)
        self.wtree.update()
        self.set_saved(False)
        self.wtree.selection_set(self.wtree.get_children()[-1])
        self.wtree.yview_moveto(1)
      
    def add(self, _event=None):
        to_add = EditPair("Add")
        if to_add.data:
            self.add_elem(to_add.data)

    def edit(self, _event=None):
        selection = self.wtree.selection()
        if len(selection) == 0:
            showinfo("Information", "Select a \"word-translation\" couple at first!")
        elif len(selection) > 1:
            showinfo("Information",
                     "Select only ONE \"word-translation\" couple - you selected {}".format(len(selection)))
        else:
            edited = EditPair("Edit", *self.wtree.item(selection[0])["values"])
            if edited.data and edited.data != self.wtree.item(selection)["values"]:
                old_id = self.wtree.get_children().index(selection[0])
                self.wtree.delete(selection[0])
                self.wtree.insert("", old_id, values=edited.data)
                self.set_saved(False)

    def remove(self, _event=None):
        """Remove a word (or some words) from the vocabulary."""
        if self.wtree.selection():  # if something is selected,
            if yesno2bool(show_msg("Warning",
                                   "Do you want to remove all the selected (%s) word's pairs?\nNote this action cannot be undone!" % len(self.wtree.selection()),
                                   "warning", "yesno")):  # ask the user to continue deletion
                self.wtree.delete(*self.wtree.selection())  # delete selected words
                self.set_saved(False)  # set saved state to unsaved
        else:  # if nothing is selected,
            showinfo("Information",
                     "Choose something at first.\nIf you want to remove all the words from the list, click \"Clear\"")

    def clear(self, _event=None):
        """Clears all the vocabulary."""
        if self.wtree.get_children():  # if there is any words in vocabulary,
            if yesno2bool(show_msg("Warning",
                                   "All the couples (%s) from this list will be permanently deleted. Do you want to continue?\nNote this action cannot be undone!" % len(self.wtree.get_children()),
                                   "warning", "yesno")):  # ask does user want to continue with clearing
                self.wtree.delete(*self.wtree.get_children())  # clear the vocabulary
                self.set_saved(False)  # set state to unsaved
        else:  # if there is some words in vocabulary,
            showinfo("Information", "The vocabulary is empty. Is it already cleared?")

    def select_all(self, _event=None):
        self.wtree.selection_set(self.wtree.get_children())

    def select_first(self, _event=None):
        first_item = self.wtree.get_children()[0]
        self.wtree.selection_set(first_item)
        self.wtree.yview_moveto(0)

    def select_last(self, _event=None):
        last_item = self.wtree.get_children()[-1]
        self.wtree.selection_set(last_item)
        self.wtree.yview_moveto(1)

    def page_up(self, _event=None):
        self.wtree.yview_scroll(-1, "units")

    def page_down(self, _event=None):
        self.wtree.yview_scroll(1, "units")

    def set_saved(self, state):
        """Set saved attribute to state."""
        if state:  # if state == True
            self.saved = True  # set saved attribute to True
            self.unsaved_prefix = ""  # hide the "unsaved" asterisk at the start of the title
            self.mod_sb["text"] = "Unmodified"  # update the statusbar value
        else:  # if state == False
            self.saved = False  # set saved attribute to False
            self.unsaved_prefix = "*"  # show the "unsaved" asterisk at the start of the title
            self.mod_sb["text"] = "Modified"  # update the statusbar value
        self.master.update_title()  # update the title

class EditPair(Toplevel):
    def __init__(self, title, word=None, translation=None):
        super().__init__()
        self.after(1, lambda: self.focus_force())
        self.grab_set()
        self.title(title)
        self.resizable(False, False)
        Label(self, text="Word:").grid(row=0, column=0)
        self.word_entry = Entry(self)
        self.word_entry.grid(row=0, column=1)
        self.word_entry.focus()
        self.word_entry.bind("<Return>", lambda _event: self.translation_entry.focus())
        Label(self, text="Translation:").grid(row=1, column=0)
        self.translation_entry = Entry(self)
        self.translation_entry.grid(row=1, column=1)
        self.translation_entry.bind("<Return>", self.ok)
        Button(self, text="OK", command=self.ok).grid(row=2, column=0, columnspan=2, sticky="ew")
        self.bind("<Escape>", lambda event: self.destroy())
        if word:
            self.word_entry.insert(END, word)
        if translation:
            self.translation_entry.insert(END, translation)
        self.data = None
        self.wait_window()

    def ok(self, _event=None):
        self.data = (self.word_entry.get(), self.translation_entry.get())
        self.grab_release()
        self.destroy()
