from tkinter import *
from tkinter.messagebox import askretrycancel, askyesnocancel, showerror, _show as show_msg
from tkinter.filedialog import askopenfilename
from tkinter.ttk import Combobox, Scrollbar, Entry
import _tkinter
import functools
import pickle
import os
import sys

import googletrans

from EditorFrame import EditorFrame
from utils import yesno2bool, retrycancel2bool, help_, about, contact_me


class Main(Tk):
    def __init__(self, text_filename=None, vocabulary_filename=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.text_opened = False  # when application is started, the text
        self.vocabulary_opened = False  # and vocabulary are not opened yet
        self.text_filename = "Non-opened" # set the default text filename, when the text was not opened (vocabulary filename is controlled by the EditorFrame
        
        self.protocol("WM_DELETE_WINDOW", self.exit)  # call the self.exit function when user exits
        
        self.LANGS_LIST = {value.lower(): key for key, value in googletrans.LANGUAGES.items()}  # create the constant for the languages names in English and their ISO 639-1 names
        # Create the variables for word and translation
        self.word_variable = StringVar(self)  # create a variable for word to translate
        self.translation_variable = StringVar(self)  # create a variable for translation

        self.vocabulary_editor = EditorFrame(self)  # create a frame for the embedded vocabulary editor
        
        # Create the menus
        self.menubar = Menu(self)  # create the main menu
        self.configure(menu=self.menubar)  # attach it to the ReadIt window
        
        self.filemenu = Menu(self.menubar, tearoff=False)  # create the "File" menu and add the appropriate entries
        self.filemenu.add_command(label="Open a text", command=self.open_text, accelerator="Ctrl+O")
        self.filemenu.add_separator()
        self.filemenu.add_command(label="New vocabulary", command=self.vocabulary_editor.new, accelerator="Ctrl+Alt+N")
        self.filemenu.add_command(label="Open a vocabulary", command=self.vocabulary_editor.open_, accelerator="Ctrl+Alt+O")
        self.filemenu.add_command(label="Save a vocabulary", command=self.vocabulary_editor.save, accelerator="Ctrl+Alt+S")
        self.filemenu.add_command(label="Save as a vocabulary", command=self.vocabulary_editor.save_as, accelerator = "Ctrl+Alt+Shift+S")
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=self.exit, accelerator="Alt+F4")
        self.menubar.add_cascade(label="File", menu=self.filemenu)  # attach it to the menubar
        
        self.bookmarksmenu = Menu(self.menubar, tearoff=False)  # create the "Bookmarks" menu and add the appropriate entries
        self.rem_bookmarksmenu = Menu(self.bookmarksmenu, tearoff=False)  # create the "Remove >" embedded menu
        self.goto_bookmarksmenu = Menu(self.bookmarksmenu, tearoff=False)  # create the "Go to >" nested menu
        self.bookmarksmenu.add_command(label="Add", command=self.add_bookmark)
        self.bookmarksmenu.add_cascade(label="Remove", menu=self.rem_bookmarksmenu)  # attach it to the "Bookmarks" menu
        self.bookmarksmenu.add_command(label="Clear all", command=self.clear_all_bookmarks)
        self.bookmarksmenu.add_cascade(label="Go to", menu=self.goto_bookmarksmenu)  # attach it to the "Bookmarks" menu
        self.menubar.add_cascade(label="Bookmarks", menu=self.bookmarksmenu)  # attach it to the menubar
        self.menubar.entryconfigure("Bookmarks", state="disabled")  # when the program is started, the "Bookmarks" menu is disabled (because text file is not opened)
        
        self.helpmenu = Menu(self.menubar, tearoff=False)  # create the "Help" menu and add the appropriate entries
        self.helpmenu.add_command(label="LearnWords Help", command=help_, accelerator="F1")
        self.helpmenu.add_separator()
        self.helpmenu.add_command(label="About LearnWords", command=about, accelerator="Ctrl+F1")
        self.helpmenu.add_command(label="Contact me", command=contact_me, accelerator="Ctrl+Shift+F1")
        self.menubar.add_cascade(menu=self.helpmenu, label="Help")  # attach it to the menubar

        self.iconbitmap("icon_32x32.ico")  # show the left-top window icon

        # let the widgets stretch using grid_columnconfigure method
        self.grid_columnconfigure(0, weight=1)
        
        self.textbox = Text(self, wrap="word", state="disabled")  # create the textbox widget,
        self.textbox.grid(row=0, column=0, rowspan=6, sticky="nswe")  # and show it using grid geometry manager
        self.textbox.bind("<Button-3>", self.select_and_translate)  # select and translate the unknown words by right-click
        self.tb_scrollbar = Scrollbar(self, command=self.textbox.yview)  # create the scrollbar for the long texts and attach it to the textbox,
        self.tb_scrollbar.grid(row=0, column=1, rowspan=6, sticky="ns")  # and show it using the grid geometry manager
        self.textbox.configure(yscrollcommand=self.tb_scrollbar.set)  # attach the textbox to the scrollbar
        
        Label(self, text="Панель перекладача").grid(row=0, column=2, columnspan=3, sticky="nswe")  # create the label with the toolbar caption and show it using grid geometry manager
        self.src_cbox = Combobox(self, values=["Auto"] + [name.capitalize() for name in self.LANGS_LIST.keys()], state="readonly")  # create and configure the combobox for the source language
        self.src_cbox.set("Auto")  # set its default language to "Auto"
        self.src_cbox.grid(row=2, column=2)  # show it using grid geometry manager
        self.src_cbox.bind("<<ComboboxSelected>>", self.update_replace_btn)  # and bind the function, that updates "Replace Languages" button, to it
        self.replace_btn = Button(self, text="⮂", state="disabled", command=self.replace_langs)  # create the "Replace Languages" button,
        self.replace_btn.grid(row=2, column=3)  # and show it using grid geometry manager
        self.dest_cbox = Combobox(self, values=[name.capitalize() for name in self.LANGS_LIST.keys()],
                                  state="readonly")  # create the combobox for the final language,
        self.dest_cbox.set("Ukrainian")  # set its default language to "Ukrainian",
        self.dest_cbox.grid(row=2, column=4)  # and show it using grid geometry manager
        askword_frame = Frame(self)  # create the frame for the word and translation
        askword_frame.grid(row=3, column=2, columnspan=3, sticky="we")  # and show it using grid geometry manager
        askword_frame.grid_columnconfigure(1, weight=1)  # let the widgets stretch by XY inside the askword_frame
        Label(askword_frame, text="Слово:").grid(row=0, column=0, sticky="w")  # create the "Word: " label
        word_entry = Entry(askword_frame, textvariable=self.word_variable)  # create an entry to enter the word
        word_entry.grid(row=0, column=1, sticky="we")  # create the Entry to enter the words
        word_entry.bind("<Return>", self.translate_word)  # it translates words when you press Enter key
        Button(askword_frame, text="↻", command=self.translate_word).grid(row=0, column=2)  # create the "Translate" button
        Label(askword_frame, text="Переклад:").grid(row=1, column=0)  # create the "Translation: " label
        translate_entry = Entry(askword_frame, textvariable=self.translation_variable)  # create the Entry to show (and edit to add into vocabulary) the translation
        translate_entry.grid(row=1, column=1, sticky="we")  # create the Entry to show (and modify to add to the vocabulary) the translations
        translate_entry.bind("<Return>", lambda _event=None: self.vocabulary_editor.add_elem((self.word_variable.get(), self.translation_variable.get())))  # it adds a words' pair to the dict when you press Enter key
        Button(askword_frame, text="➕", command=lambda: self.vocabulary_editor.add_elem((self.word_variable.get(), self.translation_variable.get()))).grid(row=1, column=2)  # create the button to add the current word to the vocabulary
        self.grid_rowconfigure(4, weight=1)  # configure the 5-th row's widgets stretch
        self.vocabulary_editor.grid(row=4, column=2, columnspan=3, sticky="nswe")  # show the vocabulary editor's frame using grid geometry manager
        self.vocabulary_editor.set_saved(True)  # when you start the program, the vocabulary is not changed

        # create the keys' bindings
        for key in ("ONS", "ons"):  # process every key-char
            self.bind("<Control-%s>" % key[0], self.open_text)
            self.bind("<Control-Alt-%s>" % key[1], self.vocabulary_editor.new)
            self.bind("<Control-Alt-%s>" % key[0], self.vocabulary_editor.open_)
            self.bind("<Control-Alt-%s>" % key[2], self.vocabulary_editor.save)
            self.bind("<Control-Alt-Shift-%s>" % key[2], self.vocabulary_editor.save_as)
        
        # Read bookmarks
        self.bookmarks_data = None  # before bookmarks are read, bookmarks_data is None
        try:  # try to
            with open("bookmarks.dat", "rb") as bdata:  # open bookmarks' file (bookmarks.dat)
                self.bookmarks_data = pickle.load(bdata)  # load its contents
        except FileNotFoundError:  # if the bookmarks.dat file doesn't present in the program directory
            self.bookmarks_data = {}  # bookmarks_data is an empty dict, where user can add bookmarks
        except Exception as details:  # if there is another problem,
            self.withdraw()  # hide the window
            showerror("Error", "Couldn't load the bookmarks list. You won't be able to use bookmarks during this session.\n\nDetails: %s (%s)" % (details.__class__.__name__, details))  # show the appropriate message
            self.deiconify()  # show the window again

        # if opening some files using command-line
        if text_filename:  # if the text was specified,
            self.open_text(text_filename=text_filename)  # open it
        if vocabulary_filename:  # if the vocabulary was specified,
            self.vocabulary_editor.open_(lwp_filename=vocabulary_filename)  # open it
        
    def open_text(self, _event=None, text_filename=None):
        """Opens a text.

        :param _event: tkinter event
        :param text_filename: text filename, when opening from command-line
        :type _event: tkinter.Event
        :type text_filename: none or str
        :return: no value
        :rtype: none
        """
        if self.can_be_closed():
            try:  # try to
                if text_filename:  # if a text file was specified in command line,
                    filename = text_filename  # set its filename as specified
                else:  # if opening from the ReadIt,
                    filename = askopenfilename()  # get the filename
                if filename:  # if user didn't click "Cancel" button or closed the dialog for opening the file
                    with open(filename, "r") as file:  # open the file for reading,
                        data = file.read()  # read it
                        self.textbox.configure(state="normal")  # activate the textbox (otherwise, no text will be inserted)
                        self.textbox.delete("0.0", "end")  # clear the textbox (won't work if couldn't open the file),
                        self.textbox.insert("0.0", data)  # and insert the data from the new file
                        self.textbox.configure(state="disabled")  # disable the textbox (user can't change the textbox content)
                        self.text_filename = filename  # update the text_filename attribute,
                        self.text_opened = True  # text_opened attribute,
                        self.update_title()  # and the title
                        if self.bookmarks_data != None:  # if there is all OK with bookmarks (if the bookmarks.dat was opened without errors),
                            self.menubar.entryconfig("Bookmarks", state="normal")  # enable "Bookmarks menu"
                            self.update_bookmarks_menu()  # updates the bookmarks menu entries according to the opened file
            except UnicodeDecodeError as details:  # if the file has unsupported encoding,
                showerror("Error", "The file has unsupported encoding or this is not a plain text file (e.g. *.txt, *.log etc), so it can't be opened.\n\nDetails: %s (%s)" % (details.__class__.__name__, details))
            except Exception as details:  # if there is an error occurred,
                showerror("Error", "During opening the file an unexpected error occured\n\nDetails: %s (%s)" % (details.__class__.__name__, details))  # show the appropriate message

    def translate_word(self, _event=None):
        """Translates the word or phrase when the user enters something and press Enter key.

        :param _event: tkinter event
        :type _event: tkinter.Event
        :return: no value
        :rtype: none
        """
        origin = self.word_variable.get()  # get the origin word
        if origin:  # if something is entered,
            try:
                src = self.src_cbox.get().lower()  # get the source language
                if src != "auto":  # if it is not "auto",
                    src = self.LANGS_LIST[src]  # get the source language ISO 639-1 representation
                dest = self.LANGS_LIST[self.dest_cbox.get().lower()]  # get the final language
                result = googletrans.Translator().translate(origin, dest, src).text  # translate using the Google Translator API
                self.translation_variable.set(result)  # update the translation variable
            except Exception as details:
                showerror("Error", "Couldn't translate the word. Check your Internet connection.\n\nDetails: %s (%s)" % (details.__class__.__name__, details))
        else:  # if nothing was entered,
            self.translation_variable.set("")  # clear the translation variable

    def replace_langs(self):
        """Replaces the languages.

        :return: no value
        :rtype: none
        """
        src = self.src_cbox.get()  # get the source language,
        dest = self.dest_cbox.get()  # get the final language,
        self.src_cbox.set(dest)  # set the source language combobox value to final language,
        self.dest_cbox.set(src)  # set the final language combobox value to source language,
        self.word_variable.set(self.translation_variable.get())  # set the word_variable to translation (translation will be done again)
        self.translate_word()

    def update_replace_btn(self, _event=None):
        """Updates the replace button state.

        :return: no value
        :rtype: none
        """
        if self.src_cbox.get() == "Auto":  # when the source language is "Auto",
            self.replace_btn.configure(state="disabled")  # it is disabled,
        else:  # when it's not,
            self.replace_btn.configure(state="normal")  # it is enabled

    def select_and_translate(self, event):
        """
        Translate the word (or phrase) from the text on right click.

        :param event: tkinter Event
        :type event: tkinter.Event
        :return: no value
        :rtype: none
        """
        try:  # if there is something selected (for phrases mostly),
            self.word_variable.set(self.textbox.selection_get())  # set the word to be translated to the selection,
            self.translate_word()  # translate the selected word/phrase
            self.textbox.tag_remove("sel", "1.0", "end")  # deselect all the text
        except _tkinter.TclError:  # if nothing is selected (words only; by right-click)
            start = self.textbox.index('@%s,%s wordstart' % (event.x, event.y))  # get the start position of the word,
            end = self.textbox.index('@%s,%s wordend' % (event.x, event.y))  # and the end position of the word,
            self.textbox.tag_add("sel", start, end)  # select the right-clicked word,
            self.textbox.update()  # update the textbox to see the selection, that disappears when the word is translated.
            self.word_variable.set(self.textbox.get(start, end))  # enter to the translation field
            self.translate_word()  # translate the word
            self.textbox.tag_remove("sel", start, end)  # deselect the word
            
    def update_title(self):
        """Updates the title when the text filename or vocabulary filename is changed.

        :return: no value
        :rtype: none
        """
        self.title("%s - %s - LearnWords ReadIt 1.0" % (self.text_filename if self.text_filename else "Untitled", self.vocabulary_editor.filename))  # format the title

    def add_bookmark(self):
        """
        Adds a bookmark so the user cannot lose the text position.

        :return: no value
        :rtype: none
        """
        if not (self.text_filename in self.bookmarks_data):  # if the bookmarks for this file were not added before
            self.bookmarks_data[self.text_filename] = []  # create the bookmarks' list for this file
        self.bookmarks_data[self.text_filename].append(self.textbox.yview()[0])  # add text Y-scroll coords
        self.update_bookmarks_menu()  # update the menu entries accroding to the updated bookmarks' list
        self.update_bookmarks_file()  # update the bookmarks.dat file

    def remove_bookmark(self, bookmark):
        """
        Removes selected bookmark.

        :param bookmark: the Y-scroll value (0.0-1.0) of the textbox to remove.
        :return: no value
        :rtype: none
        """
        if yesno2bool(show_msg("Warning", "Do you really want to remove this bookmark?", "warning", "yesno")):  # ask warning about bookmark removal
            self.bookmarks_data[self.text_filename].remove(bookmark)  # if the users says "Yes", remove it
        self.update_bookmarks_menu()  # update bookmarks_menu
        self.update_bookmarks_file()  # update the bookmarks.dat file

    def goto_bookmark(self, bookmark):
        """
        Goes to a selected bookmark.

        :param bookmark: the Y-scroll value (0.0-1.0) of the texbox to go to.
        :type bookmark: float
        """
        self.textbox.yview_moveto(bookmark)  # set the textbox y position to the selected bookmark record
        
    def clear_all_bookmarks(self):
        """Clears the bookmarks' list after user's confirmation."""
        if yesno2bool(show_msg("Warning", "Do you really want to clear all the bookmarks list for this file?", "warning", "yesno")): # if the user confirms the clearing
            del self.bookmarks_data[self.text_filename]  # remove all the bookmarks for the current filename
        self.update_bookmarks_menu()  # update bookmarks' menu entries

    def disable_bookmarks_lst(self):
        """Disables the bookmarks' menu submenus "Remove >" and "Go to >" when there aren't any bookmarks attached to opened file."""
        self.bookmarksmenu.entryconfigure("Remove", state="disabled")  # disable "Remove >" submenu
        self.bookmarksmenu.entryconfigure("Go to", state="disabled")  # disable "Go to >" submenu

    def enable_bookmarks_lst(self):
        """Enables the bookmarks' menu submenus "Remove >" and "Go to >" when there are some bookmarks attached to opened file."""
        self.bookmarksmenu.entryconfigure("Remove", state="normal")  # enable "Remove >" submenu
        self.bookmarksmenu.entryconfigure("Go to", state="normal")  # enbale "Go to >" submenu
    
    def update_bookmarks_menu(self):
        """Updates bookmarks' menu entries after changing bookmarks' list content."""
        if self.text_filename in self.bookmarks_data:  # if filename is in the bookmarks' list
            if self.bookmarks_data[self.text_filename]:  # if any bookmarks for this file are created
                self.enable_bookmarks_lst()  # enable bookmarks "Remove >" and "Go to >" submenus
                self.rem_bookmarksmenu.delete(0, "end")  # clear all the "Remove >" submenu
                self.goto_bookmarksmenu.delete(0, "end")  # clear all the "Go to >" submenu
                for no, bookmark in enumerate(self.bookmarks_data[self.text_filename]):  # create the menu entries for new bookmarks {1; 2; 3...}
                    self.rem_bookmarksmenu.add_command(label=no + 1, command=functools.partial(self.remove_bookmark, bookmark))  # create the menu entry in the "Remove >" submenu
                    self.goto_bookmarksmenu.add_command(label=no + 1, command=functools.partial(self.goto_bookmark, bookmark))  # and in the "Go to >" submenu
            else:  # if there weren't any bookmarks created for this file yet,
                self.disable_bookmarks_lst()  # disable the "Remove >" and "Go to >" submenus
        else:  # if the filename was not even in the bookmarks' list
            self.disable_bookmarks_lst()  # disable the "Remove >" and "Go to >" submenus
    
    def update_bookmarks_file(self):
        """Updates the "bookmarks.dat" file contents after changing bookmarks' list content"""
        try:  # try to
            with open("bookmarks.dat", "wb") as file:  # open bookmarks.dat for writing
                pickle.dump(self.bookmarks_data, file)  # update it with new bookmarks
        except Exception as details:  # if an error occured, show an appropriate warning and ask to retry
            while retrycancel2bool(show_msg("Error",
                           "During adding a new bookmark an error occured. "
                           "Would you like to retry?\n\nDetails: %s (%s)"
                           % (details.__class__.__name__, details), icon="error", type="retrycancel")):
                try:
                    with open("bookmarks.dat", "wb") as file:
                        pickle.dump(self.bookmarks_data, file)
                except Exception as new_details:
                    details = new_details
                else:
                    break
                
    def can_be_closed(self):
        """Asks the user to add bookmarks before closing the text file (when exits program, or opens a file)"""
        if self.text_opened and self.bookmarks_data != None:  # if both text was opened and bookmarks were not disabled due to an error
            result = askyesnocancel("Add bookmark?", "Do you want to add a bookmark before exit?")  # ask user about adding a bookmarks before exit
            if result:  # if he clicks "Yes",
                self.add_bookmark()  # add a new bookmark,
                # and then return True
            elif result == None:  # if he clicks "Cancel",
                return False  # do not close the window or open a new text
        return True  # if "Yes" and bookmark were added or "No"
    
    def exit(self):
        """Asks to save a bookmark and the vocabulary, and exits then."""
        if self.can_be_closed() and self.vocabulary_editor.can_be_closed():  # if both bookmarks added and vocabulary saved,
            self.destroy()  # destroy the ReadIt window

def show_usage():
    """Shows the command-line usage, if called."""
    Tk().withdraw()
    showerror("Error", "You are trying to run this program in an unusual way.\n\nUsage:\nReadIt.exe text.*\nReadIt.exe vocabulary.lwv\nReadIt.exe text.* vocabulary.lwv")  # show the command-line usage
    os._exit(0)

if __name__ == "__main__":
    files = list(map(lambda s: s.replace("\\", "/"), sys.argv[1:]))  # get the command-line arguments (probably files)
    if len(files) > 0:  # if any files specified,
        text_filename = None  # by default there is no text opened
        vocabulary_filename = None  # by default there is no vocabulary opened
        if len(files) == 1:  # if only one file specified,
            ext = os.path.splitext(files[-1])[-1]  # get its extension
            if ext == ".lwv":  # if it is ".lwv",
                vocabulary_filename = files[-1]  # this is a vocabulary,
            else:  # otherwise,
                text_filename = files[-1]  # this is a text file
        elif len(files) == 2:  # if two files specified,
            fexts = {os.path.splitext(fname)[-1]:fname for fname in files}  # get files' extensions
            if ".lwv" in fexts and len(fexts) > 1:  # if ".lwv" is in extensions, and the second file has another extension
                vocabulary_filename = fexts.pop(".lwv")  # the ".lwv"-ending filename belongs to a vocabulary,
                text_filename = list(fexts.values())[-1]  # the other one belongs to a text file
            else:  # if there is no vocabulary (i.e. two texts),
                show_usage()  # show the command-line usage
        else:  # if more than two files specified,
            show_usage() # show the command-line usage
        Main(text_filename, vocabulary_filename).mainloop()
    else:  # if no files passed in command line,
        Main().mainloop()  # create the ReadIt window and start its mainloop.