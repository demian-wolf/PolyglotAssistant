#!/usr/bin/python3

from tkinter import *
from tkinter.messagebox import askyesnocancel, showerror, _show as show_msg
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


class ReadIt(Tk):
    """
    The ReadIt main class.

    :param text_filename: the text filename from the command line (optional)
    :param vocabulary_filename: the vocabulary filename from the command line (optional)
    :type text_filename: str
    :type vocabulary_filename: str or none
    :return: no value
    :rtype: none
    """

    def __init__(self, text_filename=None, vocabulary_filename=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.text_opened = False  # when application is started, the text
        self.vocabulary_opened = False  # and vocabulary are not opened yet
        # Vocabulary filename is controlled by the EditorFrame, but the text is controlled by the ReadIt
        # Set the default text filename, when the text was not opened
        self.text_filename = "Не відкрито"

        self.protocol("WM_DELETE_WINDOW", self.exit)  # call the self.exit function when user exits

        self.LANGS_LIST = {value.lower(): key for key, value in
                           googletrans.LANGUAGES.items()
                           }  # create a constant for the languages names in English and their ISO 639-1 codes
        # Create the variables for word and translation
        self.word_variable = StringVar(self)  # create a variable for word to translate
        self.translation_variable = StringVar(self)  # create a variable for translation

        self.vocabulary_editor = EditorFrame(self)  # create a frame for the embedded vocabulary editor

        # Create the menus
        self.menubar = Menu(self)  # create the main menu
        self.configure(menu=self.menubar)  # attach it to the ReadIt window

        self.filemenu = Menu(self.menubar, tearoff=False)  # create the "File" menu and add the appropriate entries
        self.filemenu.add_command(label="Відкрити текст", command=self.open_text, accelerator="Ctrl+O")
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Новий словник", command=self.vocabulary_editor.new, accelerator="Ctrl+Alt+N")
        self.filemenu.add_command(label="Відкрити словник", command=self.vocabulary_editor.open,
                                  accelerator="Ctrl+Alt+O")
        self.filemenu.add_command(label="Зберегти словник", command=self.vocabulary_editor.save,
                                  accelerator="Ctrl+Alt+S")
        self.filemenu.add_command(label="Зберегти як словник", command=self.vocabulary_editor.save_as,
                                  accelerator="Ctrl+Alt+Shift+S")
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Вихід", command=self.exit, accelerator="Alt+F4")
        self.menubar.add_cascade(label="Файл", menu=self.filemenu)  # attach it to the menubar

        self.bookmarksmenu = Menu(self.menubar,
                                  tearoff=False)  # create the "Bookmarks" menu and add the appropriate entries
        self.rem_bookmarksmenu = Menu(self.bookmarksmenu, tearoff=False)  # create the "Remove >" embedded menu
        self.goto_bookmarksmenu = Menu(self.bookmarksmenu, tearoff=False)  # create the "Go to >" nested menu
        self.bookmarksmenu.add_command(label="Додати", command=self.add_bookmark)
        self.bookmarksmenu.add_cascade(label="Видалити", menu=self.rem_bookmarksmenu)  # attach it to the "Bookmarks" menu
        self.bookmarksmenu.add_command(label="Очистити", command=self.clear_all_bookmarks)
        self.bookmarksmenu.add_cascade(label="Перейти", menu=self.goto_bookmarksmenu)  # attach it to the "Bookmarks" menu
        self.menubar.add_cascade(label="Закладки", menu=self.bookmarksmenu)  # attach it to the menubar
        # when the program is started, the "Bookmarks" menu is disabled (because no text file was opened)
        self.menubar.entryconfigure("Закладки", state="disabled")

        self.helpmenu = Menu(self.menubar, tearoff=False)  # create the "Help" menu and add the appropriate entries
        self.helpmenu.add_command(label="Виклик допомоги", command=help_, accelerator="F1")
        self.helpmenu.add_separator()
        self.helpmenu.add_command(label="Про PolyglotAssistant", command=about, accelerator="Ctrl+F1")
        self.helpmenu.add_command(label="Зв'яжіться зі мною", command=contact_me, accelerator="Ctrl+Shift+F1")
        self.menubar.add_cascade(menu=self.helpmenu, label="Допомога")  # attach it to the menubar

        self.iconbitmap("icon_32x32.ico")  # show the left-top window icon

        # let the widgets stretch using grid_columnconfigure method
        self.grid_columnconfigure(0, weight=1)

        self.textbox = Text(self, wrap="word")  # create the textbox widget,
        self.textbox.grid(row=0, column=0, rowspan=6, sticky="nswe")  # and show it using grid geometry manager
        self.textbox.bind("<Button-3>",
                          self.select_and_translate)  # select and translate the unknown words by right-click
        self.tb_scrollbar = Scrollbar(self,
                                      command=self.textbox.yview)  # create a text scrollbar, attach it to the textbox,
        self.tb_scrollbar.grid(row=0, column=1, rowspan=6, sticky="ns")  # and show it using the grid geometry manager
        self.textbox.configure(yscrollcommand=self.tb_scrollbar.set)  # attach the textbox to the scrollbar

        # Create the label with the toolbar caption and show it using grid geometry manager
        Label(self, text="Панель перекладача").grid(row=0, column=2, columnspan=3, sticky="nswe")
        self.src_cbox = Combobox(self, values=["Auto"] + [name.capitalize() for name in self.LANGS_LIST.keys()],
                                 state="readonly")  # create and configure the combobox for the source language
        self.src_cbox.set("Auto")  # set its default language to "Auto"
        self.src_cbox.grid(row=2, column=2)  # show it using grid geometry manager
        self.src_cbox.bind("<<ComboboxSelected>>",
                           self.update_replace_btn)  # and bind the function, that updates "Replace Langs" button, to it
        self.replace_btn = Button(self, text="⮂", state="disabled",
                                  command=self.replace_langs)  # create the "Replace Languages" button,
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
        Button(askword_frame, text="↻", command=self.translate_word).grid(row=0,
                                                                          column=2)  # create the "Translate" button
        Label(askword_frame, text="Переклад:").grid(row=1, column=0)  # create the "Translation: " label
        translate_entry = Entry(askword_frame, textvariable=self.translation_variable
                                )  # create the Entry to show (and edit before adding into vocabulary) the translation
        # Create an Entry to show (and modify before adding to the vocabulary) the translations
        translate_entry.grid(row=1, column=1, sticky="we")
        # it adds a words' pair to the dict when you press Enter key
        translate_entry.bind("<Return>",
                             lambda _event=None: self.vocabulary_editor.add_elem((self.word_variable.get(),
                                                                                  self.translation_variable.get())))
        # Create the button to add the current word to the vocabulary
        Button(askword_frame, text="➕", command=lambda: self.vocabulary_editor.add_elem(
            (self.word_variable.get(), self.translation_variable.get()))).grid(row=1, column=2)
        self.grid_rowconfigure(4, weight=1)  # configure the 5-th row's widgets stretch
        self.vocabulary_editor.grid(row=4, column=2, columnspan=3,
                                    sticky="nswe")  # show the vocabulary editor's frame using grid geometry manager
        self.vocabulary_editor.set_saved(True)  # when you start the program, the vocabulary is not changed

        # create the keys' bindings
        for key in ("ONS", "ons"):  # process every key-char
            self.bind("<Control-%s>" % key[0], self.open_text)
            self.bind("<Control-Alt-%s>" % key[1], self.vocabulary_editor.new)
            self.bind("<Control-Alt-%s>" % key[0], self.vocabulary_editor.open)
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
            showerror("Помилка",
                      "Не вдалося завантажити список закладок, "
                      "тому ви не зможете користуватися закладками під час цієї сессії."
                      "\n\nДеталі: %s (%s)" % (details.__class__.__name__, details))  # show the appropriate message
            self.deiconify()  # show the window again

        # if opening some files using command-line
        if text_filename:  # if the text was specified,
            self.open_text(text_filename=text_filename)  # open it
        if vocabulary_filename:  # if the vocabulary was specified,
            self.vocabulary_editor.open(vocabulary_filename=vocabulary_filename)  # open it

    def open_text(self, _event=None, text_filename=None):
        """Opens a text.

        :param _event: tkinter event
        :param text_filename: text filename, when opening from command-line
        :type _event: tkinter.Event
        :type text_filename: none or str
        :return: no value
        :rtype: none
        """
        if self.can_be_closed():  # if the user confirms the text closing,
            try:  # try to
                if text_filename:  # if a text file was specified in command line,
                    filename = text_filename  # set its filename as specified
                else:  # if opening from the ReadIt,
                    filename = askopenfilename()  # get the filename
                if filename:  # if user didn't click "Cancel" button or closed the dialog for opening the file
                    with open(filename, "r") as file:  # open the file for reading,
                        data = file.read()  # read it
                        self.textbox.delete("0.0", "end")  # clear the textbox (won't work if couldn't open the file),
                        self.textbox.insert("0.0", data)  # and insert the data from the new file
                        self.text_filename = filename  # update the text_filename attribute,
                        self.text_opened = True  # text_opened attribute,
                        self.update_title()  # and the title
                        if self.bookmarks_data is not None:  # if the bookmarks.dat was opened without errors),
                            self.menubar.entryconfig("Закладки", state="normal")  # enable "Bookmarks menu"
                            self.update_bookmarks_menu()  # updates the bookmarks menu entries as in the opened file
            except UnicodeDecodeError as details:  # if the file has unsupported encoding,
                showerror("Помилка",
                          "Кодування цього текстового файлу не підтримується, або це не простий текстовий файл "
                          "(наприклад, .txt, .log тощо), тому його не можна відкрити."
                          "\n\nДеталі: %s (%s)" % (details.__class__.__name__, details))
            except Exception as details:  # if there is an error occurred,
                showerror("Помилка", "Під час відкриття цього файлу сталася невідома помилка.\n\nДеталі: %s (%s)" % (
                    details.__class__.__name__, details))  # show the appropriate message

    def translate_word(self, _event=None):
        """Translates the word or phrase when the user enters something and press Enter key.

        :param _event: tkinter event
        :type _event: tkinter.Event
        :return: no value
        :rtype: none
        """
        origin = self.word_variable.get()  # get the origin word
        if origin:  # if something is entered,
            try:  # try to
                src = self.src_cbox.get().lower()  # get the source language
                if src != "auto":  # if it is not "auto",
                    src = self.LANGS_LIST[src]  # get the source language ISO 639-1 representation
                dest = self.LANGS_LIST[self.dest_cbox.get().lower()]  # get the final language
                result = googletrans.Translator().translate(origin, dest,
                                                            src).text  # translate using the Google Translator API
                self.translation_variable.set(result)  # update the translation variable
            except Exception as details:  # if something went wrong,
                showerror("Помилка",
                          "Не вдалося перекласти слово. Перевірте доступ до мережі Інтернет!\n\nДеталі: %s (%s)" % (
                              details.__class__.__name__, details))
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
        self.word_variable.set(
            self.translation_variable.get())  # set the word_variable to translation (translation will be done again)
        self.translate_word()  # translates the word from the word_variable using Google Translator API

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
            self.textbox.update()  # update the textbox to see the selection (disappears after the word is translated)
            self.word_variable.set(self.textbox.get(start, end))  # enter to the translation field
            self.translate_word()  # translate the word
            self.textbox.tag_remove("sel", start, end)  # deselect the word

    def update_title(self):
        """Updates the title when the text filename or vocabulary filename is changed.

        :return: no value
        :rtype: none
        """
        self.title("%s - %s - PolyglotAssistant 1.00 ReadIt" % (
            self.text_filename if self.text_filename else "Untitled",
            self.vocabulary_editor.filename))  # format the title

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
        if yesno2bool(show_msg("Увага", "Ви дійсно хочете видалити цю закладку?", "warning",
                               "yesno")):  # ask warning about bookmark removal
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
        """
        Clears the bookmarks' list after user's confirmation.

        :return: no value
        :rtype: none
        """
        if yesno2bool(
                show_msg("Увага", "Ви дійсно хочете очистити весь список закладок для цього файлу?", "warning",
                         "yesno")):  # if the user confirms the clearing
            del self.bookmarks_data[self.text_filename]  # remove all the bookmarks for the current filename
        self.update_bookmarks_menu()  # update bookmarks' menu entries

    def disable_bookmarks_lst(self):
        """
        Disables the bookmarks' menu submenus "Remove >" and "Go to >".
        It's useful when there aren't any bookmarks attached to the opened file.

        :return: no value
        :rtype: none
        """
        self.bookmarksmenu.entryconfigure("Видалити", state="disabled")  # disable "Remove >" submenu
        self.bookmarksmenu.entryconfigure("Перейти", state="disabled")  # disable "Go to >" submenu

    def enable_bookmarks_lst(self):
        """
        Enables the bookmarks' menu submenus "Remove >" and "Go to >"
        It's used to enable the "Bookmarks" menu when there are some bookmarks attached to the opened file.

        :return: no value
        :rtype: none
        """
        self.bookmarksmenu.entryconfigure("Видалити", state="normal")  # enable "Remove >" submenu
        self.bookmarksmenu.entryconfigure("Перейти", state="normal")  # enbale "Go to >" submenu

    def update_bookmarks_menu(self):
        """
        Updates bookmarks' menu entries after changing bookmarks' list content.

        :return: no value
        :rtype: none
        """
        if self.text_filename in self.bookmarks_data:  # if filename is in the bookmarks' list
            if self.bookmarks_data[self.text_filename]:  # if any bookmarks for this file are created
                self.enable_bookmarks_lst()  # enable bookmarks "Remove >" and "Go to >" submenus
                self.rem_bookmarksmenu.delete(0, "end")  # clear all the "Remove >" submenu
                self.goto_bookmarksmenu.delete(0, "end")  # clear all the "Go to >" submenu
                for no, bookmark in enumerate(self.bookmarks_data[self.text_filename]
                                              ):  # create the menu entries for the new bookmarks {1; 2; 3...}
                    self.rem_bookmarksmenu.add_command(label=no + 1, command=functools.partial(self.remove_bookmark,
                                                                                               bookmark)
                                                       )  # create the menu entry in the "Remove >" submenu
                    self.goto_bookmarksmenu.add_command(label=no + 1, command=functools.partial(self.goto_bookmark,
                                                                                                bookmark)
                                                        )  # and in the "Go to >" submenu
            else:  # if there weren't any bookmarks created for this file yet,
                self.disable_bookmarks_lst()  # disable the "Remove >" and "Go to >" submenus
        else:  # if the filename was not even in the bookmarks' list
            self.disable_bookmarks_lst()  # disable the "Remove >" and "Go to >" submenus

    def update_bookmarks_file(self):
        """
        Updates the "bookmarks.dat" file contents after changing bookmarks' list content.

        :return: no value
        :rtype: none
        """
        try:  # try to
            with open("bookmarks.dat", "wb") as file:  # open bookmarks.dat for writing
                pickle.dump(self.bookmarks_data, file)  # update it with new bookmarks
        except Exception as details:  # if an error occurred, show an appropriate warning and ask to retry
            while retrycancel2bool(show_msg("Помилка",
                                            "Під час створення нової закладки сталася помилка. "
                                            "Чи не бажаєте повторити спробу?\n\nДеталі: %s (%s)"
                                            % (details.__class__.__name__, details), icon="error",
                                            type="retrycancel")):  # while user allows to retry,
                try:  # try to
                    with open("bookmarks.dat", "wb") as file:  # open the bookmarks.dat file,
                        pickle.dump(self.bookmarks_data, file)  # dump the updated bookmarks list there
                except Exception as new_details:  # if something went wrong agin,
                    details = new_details  # update the error details
                else:  # if all is OK,
                    break  # there is no reason to retry again

    def can_be_closed(self):
        """
        Asks the user to add bookmarks before closing the text file (when exits program, or opens a file)

        :return: no value
        :rtype: none
        """
        if self.text_opened and self.bookmarks_data is not None:  # if text was opened and bookmarks were not disabled
            result = askyesnocancel("Додати закладку",
                                    "Чи бажаєте додати закладку перед продовженням?")  # ask user about adding a bookmark
            if result:  # if he clicks "Yes",
                self.add_bookmark()  # add a new bookmark,
                # and then return True
            elif result is None:  # if he clicks "Cancel",
                return False  # do not close the window or open a new text
        return True  # if "Yes" and bookmark were added or "No"

    def exit(self):
        """
        Asks to save a bookmark and the vocabulary, and exits then.

        :return: no value
        :rtype: none
        """
        if self.can_be_closed() and self.vocabulary_editor.can_be_closed():  # if bookmarks added and vocabulary saved,
            self.destroy()  # destroy the ReadIt window


def show_usage():
    """
    Shows the command-line usage, if called.

    :return: no value
    :rtype: none
    """
    Tk().withdraw()  # create and hide a Tk() window (to avoid the blank window appearance on the screen)
    showerror("Помилка",
              "Ви намагаєтеся відкрити цю програму якимось дивним чином."
              "\n\nВикористання:\nReadIt.exe text.*\nReadIt.exe vocabulary.pav"
              "\nReadIt.exe text.* vocabulary.pav")  # show the command-line usage
    os._exit(0)  # terminate the application process


if __name__ == "__main__":
    # Parses the sys.argv (command-line arguments)
    files = list(map(lambda s: s.replace("\\", "/"), sys.argv[1:]))  # get the command-line arguments (probably files)
    if len(files) > 0:  # if any files specified,
        text_filename = None  # by default there is no text opened
        vocabulary_filename = None  # by default there is no vocabulary opened
        if len(files) == 1:  # if only one file specified,
            ext = os.path.splitext(files[-1])[-1]  # get its extension
            if ext == ".pav":  # if it is ".pav",
                vocabulary_filename = files[-1]  # this is a vocabulary,
            else:  # otherwise,
                text_filename = files[-1]  # this is a text file
        elif len(files) == 2:  # if two files specified,
            fexts = {os.path.splitext(fname)[-1]: fname for fname in files}  # get files' extensions
            if ".pav" in fexts and len(
                    fexts) > 1:  # if ".pav" is in extensions, and the second file has another extension
                vocabulary_filename = fexts.pop(".pav")  # the ".pav"-ending filename belongs to a vocabulary,
                text_filename = list(fexts.values())[-1]  # the other one belongs to a text file
            else:  # if there is no vocabulary (i.e. two texts),
                show_usage()  # show the command-line usage
        else:  # if more than two files specified,
            show_usage()  # show the command-line usage
        ReadIt(text_filename, vocabulary_filename).mainloop()  # open the specified files
    else:  # if no files passed in command line,
        ReadIt().mainloop()  # create the ReadIt window and start its mainloop.
