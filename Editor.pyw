#!/usr/bin/python3

from tkinter import *
from tkinter.messagebox import showinfo, showerror
import os
import sys

from PIL import Image
import pystray

from EditorFrame import EditorFrame
from utils import help_, about, contact_me


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

        self.tray_icon = None  # create the tray_icon attribute (will be changed when the application is hidden to tray)

        self.protocol("WM_DELETE_WINDOW", self.hide_to_tray)  # hides to tray when user closes the window
        
        # Configure rows and columns to let the widgets stretch
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # Create the vocabulary editor
        self.vocabulary_editor = EditorFrame()  # create the vocabulary_-editor
        self.vocabulary_editor.grid(sticky="nswe")  # show it using grid geometry manager
        self.vocabulary_editor.set_saved(True)  # set the vocabulary "saved" state to True

        # Create menu at the top of the main window
        self.menubar = Menu(self, tearoff=False)  # create the menubar
        self.config(menu=self.menubar)  # set the menubar widget for the main window

        # Create the "File" menu and add the appropriate entries
        self.filemenu = Menu(self.menubar, tearoff=False)
        self.filemenu.add_command(label="Новий", command=self.vocabulary_editor.new, accelerator="Ctrl+N")
        self.filemenu.add_command(label="Відкрити", command=self.vocabulary_editor.open, accelerator="Ctrl+O")
        self.filemenu.add_command(label="Зберегти", command=self.vocabulary_editor.save, accelerator="Ctrl+S")
        self.filemenu.add_command(label="Зберегти як", command=self.vocabulary_editor.save_as, accelerator="Ctrl+Shift+S")
        self.filemenu.add_command(label="Статистика", command=self.statistics)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Сховати до трею", command=self.hide_to_tray)
        self.filemenu.add_command(label="Вихід", command=self.exit, accelerator="Alt+F4")
        self.menubar.add_cascade(menu=self.filemenu, label="Файл")
        # Create the "Edit" menu and add the appropriate entries
        self.editmenu = Menu(self.menubar, tearoff=False)
        self.editmenu.add_command(label="Додати", command=self.vocabulary_editor.add, accelerator="Ctrl+Alt+A")
        self.editmenu.add_command(label="Редагувати", command=self.vocabulary_editor.edit, accelerator="Ctrl+Alt+E")
        self.editmenu.add_command(label="Видалити", command=self.vocabulary_editor.remove, accelerator="Alt+Del")
        self.editmenu.add_command(label="Очистити", command=self.vocabulary_editor.clear, accelerator="Shift+Del")
        self.menubar.add_cascade(menu=self.editmenu, label="Правка")
        # Create the "Help" menu and add the appropriate entries
        self.helpmenu = Menu(self.menubar, tearoff=False)
        self.helpmenu.add_command(label="Виклик допомоги", command=help_, accelerator="F1")
        self.helpmenu.add_separator()
        self.helpmenu.add_command(label="Про PolyglotAssistant", command=about, accelerator="Ctrl+F1")
        self.helpmenu.add_command(label="Зв'яжіться зі мною", command=contact_me, accelerator="Ctrl+Shift+F1")
        self.menubar.add_cascade(menu=self.helpmenu, label="Допомога")

        self.iconbitmap("images/32x32/app_icon.ico")  # show the left-top window icon

        # Bind the keybindings
        self.bind("<F1>", help_)
        self.bind("<Control-F1>", about)
        self.bind("<Control-Shift-F1>", contact_me)
        for key in ("NOS", "nos"):  # process every key
            self.bind("<Control-%s>" % key[0], self.vocabulary_editor.new)
            self.bind("<Control-%s>" % key[1], self.vocabulary_editor.open)
            self.bind("<Control-%s>" % key[2], self.vocabulary_editor.save)
            self.bind("<Control-Shift-%s>" % key[2], self.vocabulary_editor.save_as)

        if vocabulary_filename:  # if a file was specified in command-line,
            self.vocabulary_editor.open(vocabulary_filename=vocabulary_filename)  # open the vocabulary

    def statistics(self):
        """
        Opens the "Statistics" dialog.

        :return: no value
        :rtype: none
        """
        if self.vocabulary_editor.wtree.get_children():  # if anything in the vocabulary,
            alphabet_dict = {}  # create the Python dict object to store the count of words, starting with every char
            for word_pair in self.vocabulary_editor.wtree.get_children():  # process every words' pair
                first_letter = self.vocabulary_editor.wtree.item(word_pair)["values"][0][0].upper()  # get the 1st char
                if first_letter in alphabet_dict:  # if the first char is already in the alphabet dict,
                    alphabet_dict[first_letter] += 1  # increase the words' pairs count for this char (letter) by 1
                else:  # if the letter was found the first time (so it wasn't in the alphabet_dict before)
                    alphabet_dict[first_letter] = 1  # set the first char count to 1
            # create the results' list in a way it is shown in the dialog
            result_list = ["За першою літерою:"]  # the start caption
            result_list.extend(
                ["{} - {}".format(first_letter, count) for first_letter, count in sorted(alphabet_dict.items())])
            result_list.append("\nУсього: {}".format(len(self.vocabulary_editor.wtree.get_children())))  # totally
            showinfo("Статистика", ("\n".join(result_list)))  # show the statistics dialogue
        else:  # if the vocabulary is empty,
            showinfo("Статистика", "У словнику поки ще не має слів. Спершу додайте кілька.")  # it is nothing to show

    def hide_to_tray(self, _event=None):
        """
        Hides the application to the tray.

        :param _event: the unused Tkinter event
        :type _event: tkinter.Event
        :return: no value
        :rtype: none
        """
        self.tray_icon = pystray.Icon("EditorTrayIcon", title="PolyglotAssistant Editor")  # create the tray icon
        self.tray_icon.icon = Image.open("images/32x32/app_icon.ico")  # open the icon using PIL
        self.tray_icon.menu = pystray.Menu(pystray.MenuItem("Розгорнути", lambda: self.tray_icon.stop(), default=True),
                                           pystray.MenuItem("Вийти", lambda: self.tray_exit()))  # add the menu items
        self.withdraw()  # hide the window
        self.tray_icon.run()  # run the icon's main loop
        # icon mainloop
        self.deiconify()  # when the icon mainloop had been stopped, show the window again
        self.focus_force()  # focus on it

    def tray_exit(self):
        """
        Run exit command from tray.

        :return: no value
        :rtype: none
        """
        self.tray_icon.stop()  # stop the tray icon mainloop
        self.after(0, self.exit)  # exit from the application

    def exit(self):
        """
        Exits the application.

        :return: no value
        :rtype: none
        """
        if self.vocabulary_editor.can_be_closed():  # ask user to save the vocabulary; if can close the window then,
            self.destroy()  # close it
            os._exit(0)  # terminate the application process

    def update_title(self):
        """
        Updates the title of the app.

        :return: no value
        :rtype: none
        """
        self.title("%s%s - PolyglotAssistant 1.00 Editor" % (self.vocabulary_editor.unsaved_prefix,
                                                             self.vocabulary_editor.filename))  # formats the title


def show_usage():
    """
    Shows the usage of the command-line interface.

    :return: no value
    :rtype: none
    """
    Tk().withdraw()  # hide the window (otherwise, an empty window is shown)
    showerror("Error", "Ви намагаєтеся відкрити цю програму якимось дивним чином."
                       "\n\nВикористання:\nEditor.exe vocabulary.pav")  # displays the error
    os._exit(0)  # terminates the application process


if __name__ == "__main__":
    # Processes the sys.argv list (command-line arguments list)
    if len(sys.argv) == 1:  # if no arguments specified,
        Editor().mainloop()  # run the main window with a new file created
    elif len(sys.argv) == 2:  # if a file was specified,
        if os.path.splitext(sys.argv[-1])[-1] == ".pav":  # and if it has got ".pav" extension
            Editor(vocabulary_filename=sys.argv[-1].replace("\\", "/")).mainloop()  # open the vocabulary
    else:  # if there were multiple arguments specified,
        show_usage()  # show usage
