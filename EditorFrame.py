from tkinter import *
from tkinter.messagebox import showinfo, showerror, _show as show_msg
from tkinter.filedialog import *
from tkinter.ttk import Treeview, Entry, Scrollbar, Button

import pickle

from Hotkeys import HKManager
from utils import yesno2bool, validate_vocabulary_data



exec("from lang.%s import *" % "ua")
# TODO: try to make "Reverse" tool work using self._edit_pair method (for example, there is no need to pass the select arg, because everywhere there is selected[0] used
# TODO: make hotkeys work on Linux, too - only check if not Windows OS and if yes, simply bind using the standard Tkinter interface

class EditorFrame(Frame):
    """
    The vocabulary editor's frame class. Because it is in a separate class, you can embed it both in ReadIt and Editor.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.create_wgts()
        
        self.saved = False
        self.unsaved_prefix = ""
        self.filename = LANG["non_opened_filename"]  # the default filename is "Untitled"

        self.hk_man = self.master.hk_man  # TODO: find another solution
        self.bind_keybindings()

    def create_wgts(self):
        """
        This method creates the widgets.

        :return: no value
        :rtype: none
        """
        
        # Let the widgets stretch (by configuring weight)
        self.rowconfigure(0, weight=1)
        for column_id in range(5):
            self.columnconfigure(column_id, weight=1)

        # Create a Treeview widget to display the vocabulary words' list and its scrollbar
        self.wtree = Treeview(self, show="headings", columns=["word", "translation"], selectmode=EXTENDED)
        self.wtree.heading("word", text=LANG["word"])  # add the "Word" column
        self.wtree.heading("translation", text=LANG["translation"])  # add the "Translation" column
        self.wtree.grid(row=0, column=0, columnspan=5, sticky="nsew")  # show it using grid geometry manager
        self.scrollbar = Scrollbar(self, command=self.wtree.yview)  # create a scrollbar, attach the words' tree to it
        self.scrollbar.grid(row=0, column=6, sticky="ns")  # show the scrollbar using grid geometry manager
        self.wtree.config(yscrollcommand=self.scrollbar.set)  # attach it to the words' tree

        # Create the buttons to edit the vocabulary
        Button(self, text=LANG["add"], command=self.add).grid(row=1, column=0, sticky="ew")
        Button(self, text=LANG["edit"], command=self.edit).grid(row=1, column=1, sticky="ew")
        Button(self, text=LANG["remove"], command=self.remove).grid(row=1, column=2, sticky="ew")
        Button(self, text=LANG["clear"], command=self.clear).grid(row=1, column=3, sticky="ew")
        Button(self, text=LANG["reverse"], command=self.reverse).grid(row=1, column=4, sticky="ew")

        # Create a frame for the statusbar
        sbs_frame = Frame(self)  # create the statusbar frame
        self.tot_sb = Label(sbs_frame, text=LANG["totally"] % "?")  # create a label that shows the total words quantity
        self.tot_sb.grid(row=0, column=0, sticky="ew")  # show it using the grid geometry manager
        self.mod_sb = Label(sbs_frame, text=LANG["unmodified"], width=13)  # create a label that shows was the vocabulary modified
        self.mod_sb.grid(row=0, column=1, sticky="ew")  # show it using the grid geometry manager
        sbs_frame.grid(row=2, column=0, columnspan=7, sticky="ew")  # show the whole frame using grid geometry manager

    def bind_keybindings(self):
        self.hk_man.add_binding("<Control-A>", self.select_all)
        self.hk_man.add_binding("<Control-Alt-A>", self.add)
        self.hk_man.add_binding("<Control-Alt-E>", self.edit)
        self.hk_man.add_binding("<Control-Alt-R>", self.reverse)
        # TODO: don't be overriden
        self.master.bind("<Alt-Delete>", self.remove)
        self.master.bind("<Shift-Delete>", self.clear)
        self.master.bind("<Home>", self.select_first)
        self.master.bind("<End>", self.select_last)
        self.master.bind("<Prior>", self.page_up)  # bind the PgUp key
        self.master.bind("<Next>", self.page_down)  # bind the PgDn key

    def can_be_closed(self):
        """
        If the vocabulary is not saved, and user is trying to create a new one/open another one/quit the app,
        app asks the user to save the vocabulary.

        :return: no value
        :rtype: none
        """
        
        if not self.saved:  # if the vocabulary is not saved,
            result = show_msg(LANG["warning"], LANG["warning_save_vocabulary_before_continue"], "warning",
                              "yesnocancel")  # asks about an action
            if result == "yes":  # if user asked to save,
                self.save()  # it saves
                if self.saved:  # if the file became saved,
                    self.wtree.delete(*self.wtree.get_children())  # clear the words list widget
                    return True  # this vocabulary can be closed
            elif result == "no":  # if the user doesn't want to save the file,
                return True  # this vocabulary can be closed
            return False  # if the user said "Cancel" or the file was not saved, this vocabulary cannot be closed
        return True  # if the file was saved before, this vocabulary can be closed

    def new(self, _event=None):
        """
        Creates a new vocabulary.

        :param _event: the unused Tkinter event
        :type _event: tkinter.Event
        :return: no value
        :rtype: none
        """
        if self.can_be_closed():  # if the file can be closed,
            self.wtree.delete(*self.wtree.get_children())  # clear the wtree frame
            self.filename = LANG["non_opened_filename"]  # set untitled filename
            self.set_saved(True)  # set the "saved" state
            self.master.update_title()  # update the master window title

    def open(self, _event=None, vocabulary_filename=None):
        """
        Opens a vocabulary.

        :param _event: the unused Tkinter event
        :param vocabulary_filename:
        :type _event: tkinter.Event
        :type vocabulary_filename: str
        :return: no value
        :rtype: none
        """

        if self.can_be_closed():  # if the file can be closed,
            try:  # try to
                if vocabulary_filename:  # if a vocabulary filename was specified to this function
                    vocabulary_file = open(vocabulary_filename, "rb")  # open the vocabulary file
                else:  # if nothing was specified,
                    vocabulary_file = askopenfile(mode="rb", filetypes=[(LANG["pav_vocabulary_filetype"],
                                                                         "*.pav")])  # ask for a .PAV file to open
                    
            except FileNotFoundError as details:  # if submitted file disappeared suddenly
                showerror(LANG["error"],
                          "Не вдалося відкрити файл. Перевірте його наявність у директорії."
                          "\n\nДеталі: FileNotFoundError (%s)" % details)
            except PermissionError as details:  # if the access to the file denied
                showerror(LANG["error"],
                          "Не вдалося відкрити файл. Перевірте Ваші права доступу до нього."
                          "\n\nДеталі: PermissionError (%s)" % details)
            except Exception as details:  # if any other problem happened
                showerror(LANG["error"], "Під час відкриття файлу сталася невідома помилка.\n\nДеталі: %s (%s)" % (
                    details.__class__.__name__, details))
            else:  # if all is OK,
                if vocabulary_file:  # if anything was opened...
                    try:  # try to
                        vocabulary_data = pickle.load(vocabulary_file)  # read the vocabulary
                    except pickle.UnpicklingError as details:  # if the file is damaged, or its format is unsupported
                        showerror(LANG["error"],
                                  "Файл пошкоджено або його формат не підтримується!\n\nДеталі: %s" % details)
                    except Exception as details:  # if unexpected error occurred,
                        showerror(LANG["error"],
                                  "Під час відкриття файлу сталася невідома помилка.\n\nДеталі: %s (%s)" % (
                                      details.__class__.__name__, details))
                    else:  # if the file can be decoded,
                        try:
                            validate_vocabulary_data(vocabulary_data)  # check its format
                        except AssertionError:  # if it is invalid,
                            showerror(LANG["error"],
                                      "Файл пошкоджено або його формат не підтримується!"
                                      "\n\nДеталі: закодований у файлі об'єкт не є словником PolyglotAssistant.")
                        else:  # if the file format is OK,
                            self.wtree.delete(*self.wtree.get_children())  # clear the words-list,
                            for pair in vocabulary_data:  # and insert the words from opened vocabulary there
                                self.wtree.insert("", END, values=pair)  # insert every pair
                            self.update_totally()  # update the "Totally" status bar label
                            self.set_saved(True)  # set state to saved
                            self.filename = os.path.abspath(vocabulary_file.name)  # update the filename value
                            self.master.update_title()  # update the title of the main window

    def _save(self, filename):
        """
        Provides save mechanism (that basic operation that are repeated both when saving, and saving as.

        :param filename: the filename of the file where to save
        :type filename: str
        :return: no value
        :rtype: none
        """
        try:  # try to
            outfile = open(filename, "wb")  # try to open a file to write
            pickle.dump([tuple(map(str, self.wtree.item(child)["values"])) for child in self.wtree.get_children()],
                        outfile)  # get the vocabulary content and dump it to selected file
            outfile.close()  # now we can close the outfile
            self.filename = os.path.abspath(outfile.name)  # update the opened file's filename, if changed
            self.set_saved(True)  # set state to saved
        except PermissionError as details:  # if there is a problem with access permissions,
            showerror("Error",
                      "Не вдалося зберегти файл. Перевірте Ваші права доступу до нього, в тому числі на запис"
                      "\n\nДеталі: %s" % details)
        except Exception as details:  # if there is an unexpected problem occurred,
            showerror("Error", "Під час збереження файлу сталася невідома помилка.\n\nДеталі: %s (%s)" % (
                details.__class__.__name__, details))

    def save(self, _event=None):
        """
        Saves the file to the same path and filename, if untitled - calls save as.

        :param _event: the unused Tkinter event
        :type _event: tkinter.Event
        :return: no value
        :rtype: none
        """
        if self.filename == "Без імені":  # if the file is untitled,
            self.save_as()  # save as (to ask user how to name the file)
        else:  # if the file was already saved (even during the other session, and then opened now),
            self._save(self.filename)  # save the file with the same filename  

    def save_as(self, _event=None):
        """
        Save the file as,

        :param _event: the unused Tkinter event
        :type _event: tkinter.Event
        :return: no value
        :rtype: none
        """
        try:  # try to
            outfilename = asksaveasfilename(defaultextension=".", filetypes=[
                ("Словник PolyglotAssistant", ".pav")])  # ask a user for the filename to save to
        except Exception as details:  # if an unexpected problem occurred,
            showerror("Помилка",
                      "Під час збереження файлу сталася невідома помилка.\n\nДеталі: %s (%s)" % (details, details.__class__.__name__))
        else:  # if could get the filename,
            if outfilename:  # if user selected the file (if he canceled the operation, outfilename will equal to None)
                self._save(outfilename)  # save the vocabulary to selected file

    def _add_pair(self, pair):
        """
        Add a word pair to the vocabulary directly without opening the "Add" dialog

        :param elem: (word, translation) pair
        :type elem: tuple
        :return: no value
        :rtype: none
        """
        self.wtree.insert("", END, values=pair)  # insert the word pair to the words' tree
        self.wtree.update()  # update the words' tree
        self.set_saved(False)  # set the saved state to False (the vocabulary content was modified)
        self.wtree.selection_set(self.wtree.get_children()[-1])  # select the last word of the vocabulary
        self.wtree.yview_moveto(1)  # move to the end of the vocabulary

    def _edit_pair(self, selection, pair):
        """
        Edit a word pair from the vocabulary directly without opening the "Edit" dialog

        :param elem: (word, translation) pair
        :type elem: tuple
        :return: no value
        :rtype: none
        """
        
        old_id = self.wtree.get_children().index(selection[0])
        self.wtree.delete(selection[0])  # remove the old 
        self.wtree.insert("", old_id, values=pair)  # insert the edited element to that position
        self.set_saved(False)  # set the vocabulary "saved" state to unsaved

    def add(self, _event=None):
        """
        Open the "Add" dialog to add a new word to the vocabulary.

        :param _event: the unused Tkinter event
        :type _event: tkinter.Event
        :return: no value
        :rtype: none
        """
        to_add = EditPair("Додати")  # call the EditPair dialog with the "Add" caption
        if to_add.data:  # if the user pressed "OK" button,
            self._add_pair(to_add.data)  # add the word pair to the vocabulary

    def edit(self, _event=None):
        """
        Open the "Edit" dialog to edit an existing word from the vocabulary.

        :param _event: the unused Tkinter event
        :type _event: tkinter.Event
        :return: no value
        :rtype: none
        """
        selection = self.wtree.selection()  # get the selection
        if not selection:  # if nothing is selected,
            showinfo("Інформація", "Виберіть пару \"слово-переклад\" спочатку.")
        elif len(selection) > 1:  # if multiple elements selected
            showinfo("Інформація",
                     "Виберіть лише одну пару \"слово-переклад\" - ви вибрали %s" % len(selection))
        else:  # if only one word is selected,
            edited = EditPair("Редагувати", *self.wtree.item(selection[0])["values"])  # get the edited word
            if edited.data and edited.data != tuple(self.wtree.item(selection)["values"]):  # if user edited something
                self._edit_pair(selection, edited.data)  # get the element position

    def remove(self, _event=None):
        """
        Remove a word (or some words) from the vocabulary.

        :param _event: the unused Tkinter event
        :type _event: tkinter.Event
        :return: no value
        :rtype: none
        """
        if self.wtree.selection():  # if something is selected,
            if yesno2bool(show_msg("Увага",
                                   "Ви дійсно хочете видалити усі вибрані (%s) пари слів?"
                                   % len(self.wtree.selection()),
                                   "warning", "yesno")):  # ask the user to continue deletion
                self.wtree.delete(*self.wtree.selection())  # delete selected words
                self.set_saved(False)  # set saved state to unsaved
        else:  # if nothing is selected,
            showinfo("Інформація",
                     "Спочатку щось виберіть.\nЯкщо ви хочете видалити всі слова зі словнику, натисніть \"Очистити\"")

    def clear(self, _event=None):
        """
        Clears all the vocabulary.

        :param _event: the unused Tkinter event
        :type _event: tkinter.Event
        :return: no value
        :rtype: none
        """
        if self.wtree.get_children():  # if there are some words in vocabulary,
            if yesno2bool(show_msg("Увага",
                                   "Всі пари (%s) з цього словнику будуть видалені!"
                                   "Ви дійсно бажаєте продовжити?" % len(self.wtree.get_children()),
                                   "warning", "yesno")):  # ask does user want to continue with clearing
                self.wtree.delete(*self.wtree.get_children())  # clear the vocabulary
                self.set_saved(False)  # set state to unsaved
        else:  # if there aren't any words in vocabulary,
            showinfo("Інформація", "Цей словник порожній. Можливо ви вже його очистили?")
    # TODO: remove _event=None from inappropriate places

    def reverse(self, _event=None):
        selection = self.wtree.selection()
        if selection:  # if something is selected,
            for item in selection:
                reversed_pair = list(reversed(self.wtree.item(item)["values"]))
                old_id = self.wtree.get_children().index(item)
                self.wtree.delete(item)  # remove the old item
                self.wtree.insert("", old_id, values=reversed_pair)  # insert the edited element to that position
                self.set_saved(False)  # set the vocabulary "saved" state to unsaved
        else:  # if nothing is selected,
            showinfo("Інформація", "Спочатку щось виберіть.")

    def train_now(self, _event=None):
        pass

    def select_all(self, _event=None):
        """
        Selects all the vocabulary words' pairs.

        :param _event: the unused Tkinter event
        :type _event: tkinter.Event
        :return: no value
        :rtype: none
        """
        self.wtree.selection_set(self.wtree.get_children())  # select all the words' pairs

    def select_first(self, _event=None):
        """
        Selects the first word in the vocabulary.

        :param _event: the unused Tkinter event
        :type _event: tkinter.Event
        :return: no value
        :rtype: none
        """

        wtree_children = self.wtree.get_children()
        if wtree_children:
            first_item = wtree_children[0]  # get the first item of the words' list
            self.wtree.selection_set(first_item)  # set the selection to it
            self.wtree.yview_moveto(0)  # scroll to the start of the words' list (by Y)

    def select_last(self, _event=None):
        """
        Selects the last word in the vocabulary.

        :param _event: the unused Tkinter event
        :type _event: tkinter.Event
        :return: no value
        :rtype: none
        """

        wtree_children = self.wtree.get_children()
        if wtree_children:
            last_item = wtree_children[-1]  # get the last item of the words' list
            self.wtree.selection_set(last_item)  # set the selection to it
            self.wtree.yview_moveto(1)  # scroll to the end of the words' list (by Y)

    def page_up(self, _event=None):
        """
        Scrolls up for 1 yview unit.

        :param _event: the unused Tkinter event
        :type _event: tkinter.Event
        :return: no value
        :rtype: none
        """
        self.wtree.yview_scroll(-1, "units")  # scroll up for 1 unit

    def page_down(self, _event=None):
        """
        Scrolls down for 1 yview unit.

        :param _event: the unused Tkinter event
        :type _event: tkinter.Event
        :return: no value
        :rtype: none
        """
        self.wtree.yview_scroll(1, "units")  # scroll down for 1 unit

    def set_saved(self, state):
        """
        Set saved attribute to state.

        :param state: is the vocabulary saved?
        :type state: bool
        :return: no value
        :rtype: none
        """
        if state:  # if state == True
            self.saved = True  # set saved attribute to True
            self.unsaved_prefix = ""  # hide the "unsaved" asterisk at the start of the title
            self.update_totally()
            self.mod_sb["text"] = LANG["unmodified"]  # update the statusbar value
        else:  # if state == False
            self.saved = False  # set saved attribute to False
            self.unsaved_prefix = "*"  # show the "unsaved" asterisk at the start of the title
            self.update_totally()
            self.mod_sb["text"] = LANG["modified"]  # update the statusbar value
        self.master.update_title()  # update the title of the master window

    def update_totally(self):
        """
        Updates the "Totally: <total words count>" status bar label

        :return: no value
        :rtype: none
        """
        self.tot_sb.configure(text=LANG["totally"] % len(self.wtree.get_children()))


class EditPair(Toplevel):
    """
    Class for the pair editor window.

    :param word: the word
    :param translation: the translation of the word
    :type word: str
    :type translation: str
    """

    def __init__(self, title, word=None, translation=None):
        super().__init__()

        self.after(1, lambda: self.focus_force())  # set the focus on this window
        self.grab_set()  # deny the user to use the master window
        self.title(title)  # set the title of this window
        self.resizable(False, False)  # deny the user to resize this window
        Label(self, text="Слово:").grid(row=0, column=0)  # create the "Word:" label, show it using grid geometry manager
        self.word_entry = Entry(self)  # create the entry widget to enter the word
        self.word_entry.grid(row=0, column=1)  # show the word entry using the grid geometry manager
        self.word_entry.focus()  # focus on the word entry
        self.word_entry.bind("<Return>",
                             lambda _event: self.translation_entry.focus()
                             )  # when the user press "Enter" key focus on the translation entry
        Label(self, text="Переклад:").grid(row=1, column=0)  # create the "Translation:" label, show it using grid GM
        self.translation_entry = Entry(self)  # create the translation entry to let user enter the translation
        self.translation_entry.grid(row=1, column=1)  # and show it using the grid geometry manager
        self.translation_entry.bind("<Return>",
                                    self.ok)  # save changes, when the user presses Enter after entering the translation
        Button(self, text="OK", command=self.ok).grid(row=2, column=0, columnspan=2,
                                                      sticky="ew")  # create the OK button
        self.bind("<Escape>", lambda event: self.destroy())  # if the user presses "Escape" key, close this dialog

        # if we are editing the word,
        if word:  # if the word was passed
            self.word_entry.insert(END, word)  # insert it in the word entry
        if translation:  # if the translation was passed,
            self.translation_entry.insert(END, translation)  # insert it in the translation entry
        self.data = None  # the data is None before the submit (avoid AttributeError, when the operation is canceled)
        self.wait_window()  # wait while the window is closed

    def ok(self, _event=None):
        """
        Submits the entered (word, translation) pair.

        :param _event: the unused Tkinter event
        :type _event: tkinter.Event
        :return: no value
        :rtype: none
        """
        self.data = (self.word_entry.get(), self.translation_entry.get())  # set the data attribute to the entered data
        self.grab_release()  # allow user to use the master window again
        self.destroy()  # destroy this window
