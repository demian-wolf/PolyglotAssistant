#!/usr/bin/python3

# This application uses sound from Scratch 1.4 and https://noisefx.ru/
from tkinter import *
from tkinter.messagebox import showinfo, showerror, showwarning, _show as show_msg
from tkinter.filedialog import askopenfilename
from tkinter.ttk import Treeview, Entry, Progressbar, Scrollbar

try:
    # if Python >= 3.7:
    from tkinter.ttk import Spinbox
except ImportError:
    # otherwise
    from tkinter import Spinbox
import pygame
import random
import pickle
import os
import sys

from Hotkeys import HKManager
from utils import yesno2bool, retrycancel2bool, validate_users_dict, validate_vocabulary_data, reverse_pairs, help_, \
    about, contact_me, tidy_stats, play_sound, set_window_icon


exec("from lang.%s import *" % "ua")
# TODO: focus after help, about and contact_me; when user was (or was not) deleted
# TODO: replace Buttons with ttk.Buttons

class Trainer(Tk):
    """
    The Trainer main class.

    :param vocabulary_filename: the vocabulary filename from the command line (optional)
    :type vocabulary_filename: str or none
    :return: no value
    :rtype: none
    """

    def __init__(self, vocabulary_filename=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        set_window_icon(self)  # set the titlebar icon
        self.withdraw()  # hide this empty window (there are Toplevels to display something)
        ul_window = UserLoginWindow()  # create a toplevel for user logging
        if ul_window.user.get():  # if user is logged in,
            ul_window.destroy()  # destroy the user login window
            HomeWindow(ul_window.users_dict, ul_window.user.get(), vocabulary_filename)  # and create the home window


class UserLoginWindow(Toplevel):
    """
    The main class for the user login window (user (player) selection)

    :return: no value
    :rtype: none
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("%s - PolyglotAssistant 1.00 Trainer" % LANG["Authorization"])  # set title "Login" to the frame
        self.protocol("WM_DELETE_WINDOW", self.close)  # when the user closes the window, terminate the whole process
        self.resizable(False, False)  # make the user login window unresizable
        self.after(0, self.focus_force)  # focus to the trainer window on start

        # self.iconbitmap("images/32x32/app_icon.ico")  # show the left-top window icon

        self.user = StringVar(self)  # create variable for username
        self.user.set("")  # now username is empty, and it stays empty if user won't log in.
        self.users_dict = {}  # dict for all the users, will be soon read from the "users.dat" file, if it exists
        self.userslistbox = Listbox(self)  # create a listbox for usernames
        self.userslistbox.grid(row=0, column=0, columnspan=6, sticky="nsew")  # grid the listbox
        self.userslistbox.bind("<Double-1>", self.login_double_click)  # log in as the selected user on double click
        self.userslistbox.bind("<Return>", self.login_as_this_user)  # log in as the selected user on "Return" key press
        self.scrollbar = Scrollbar(self, command=self.userslistbox.yview)  # create a scrollbar for the users' list
        self.scrollbar.grid(row=0, column=6, sticky="ns")  # grid the scrollbar
        self.userslistbox.config(yscrollcommand=self.scrollbar.set)  # configure the users' list
        pwd_frame = Frame(self)  # create frame for the password input
        Label(pwd_frame, text=LANG["Password_if_set:"]).grid(row=0, column=0, sticky="ew")  # a label, which says "Password:"
        self.pwd_entry = Entry(pwd_frame, show="●")  # entry for the password
        self.pwd_entry.grid(row=0, column=1, sticky="ew")  # grid the password entry
        self.pwd_entry.bind("<Return>",
                            self.login_as_this_user)  # after password entering, user can press "Enter" to continue
        pwd_frame.grid(columnspan=5)  # grid password frame

        # Create the buttons
        Button(self, text=LANG["Log_in_as_selected"], command=self.login_as_this_user).grid(row=2, column=0, sticky="ew")
        Button(self, text=LANG["Add_new"], command=self.add_a_new_user).grid(row=2, column=1, sticky="ew")
        Button(self, text=LANG["Remove_selected"], command=self.remove_this_user).grid(row=2, column=2, sticky="ew")
        Button(self, text=LANG["exit"], command=self.close).grid(row=2, column=3, columnspan=2, sticky="ew")

        self.bind("<Escape>", lambda _event: self.close())  # when the user strokes Escape key, close the window
        self.update_ulist()  # update user list (it is empty)
        self.grid()  # grid this frame in the master window
        self.wait_variable(self.user)  # wait (don't return anything) while the user won't log in

    def login_double_click(self, event):
        """
        This method is called on double click on the users' listbox (when the user tries to log in by double click)

        :param event: the unused Tkinter event
        :type event: tkinter.Event
        :return: no value
        :rtype: none
        """

        # TODO: replace event.y <= 17 with something more right
        if event.y <= 17 * self.userslistbox.size():  # if the mouse y on the users' list belongs to any username
            self.login_as_this_user()  # login as the selected user

    def login_as_this_user(self, _event=None):
        """
        Logs as the selected user.
        :param _event: the unused Tkinter event
        :return: tkinter.Event
        """
        selection = self.userslistbox.curselection()  # get user's selection
        if selection:  # if any user is selected,
            selected_user = self.userslistbox.get(selection[0])  # get the first (the single one) element from selection
            if self.pwd_entry.get() == self.users_dict[selected_user]["password"]:  # if the right password is entered
                self.user.set(selected_user)  # return (see "wait_variable" above) the username of the selected user
            else:  # if the wrong password is entered
                showerror(LANG["error"], LANG["error_wrong_password_try_again"])
                self.focus_force()  # set focus on the window again
        else:
            # if user was not selected, show an appropriate message
            showinfo(LANG["information"], LANG["information_select_user_or_add_a_new_one"])

    def add_a_new_user(self):
        """
        Opens the dialog for adding users.

        :return: no value
        :rtype: none
        """
        
        udata = AddUser().data  # get the user's data - (name, password) if wasn't canceled, None otherwise
        ulist = None  # users list should be None (it will be changed later, if no error during opening "users.dat")
        if udata:  # if the new user's adding was not canceled,
            if "users.dat" in os.listdir(os.path.curdir):  # if there is "users.dat" in the app path already
                try:  # try to open the users list
                    udat = open("users.dat", "rb")  # users.dat will be opened
                except FileNotFoundError as details:  # if the "users.dat" file had disappeared from the app directory,
                    showerror(LANG["error"], LANG["error_users_dat_missing"] +
                              (LANG["error_details"] % (details.__class__.__name__, details)))
                    self.close()  # terminate the program process
                except PermissionError as details:  # if the access to the file denied
                    showerror(LANG["error"], LANG["error_users_dat_permissions"] +
                              (LANG["error_details"] % (details.__class__.__name__, details)))
                    self.close()  # terminate the program process
                except Exception as details:  # if any other problem happened
                    showerror(LANG["error"], LANG["error_users_dat_unexpected"] +
                              (LANG["error_details"] % (details.__class__.__name__, details)))
                    self.close()  # terminate the program process
                else:  # if could open the "users.dat" file,
                    try:  # try to
                        ulist = pickle.load(udat)  # decode it,
                        validate_users_dict(ulist)
                    except (pickle.UnpicklingError, EOFError, AssertionError) as details:  # if it's spoiled, or has unsupported format
                        showerror(LANG["error"], LANG["error_users_dat_damaged"] +
                                  (LANG["error_details"] % (details.__class__.__name__, details)))
                    except Exception as details:  # if unexpected error occurred,
                        showerror(LANG["error"], LANG["error_users_dat_unexpected"] +
                                  (LANG["error_details"] % (details.__class__.__name__, details)))
                        self.close()
            else:  # if there is no "users.dat" in the app path,
                ulist = {}  # create a new users' dictionary
            if ulist is not None:  # if could open users' list,
                ulist[udata[0]] = {"password": udata[1],
                                   "stats": {}}  # assign new user's name with password and stats
                try:  # try to
                    pickle.dump(ulist, open("users.dat", "wb"))  # dump it all into new "users.dat" file
                except Exception as details:  # if something went wrong,
                    while retrycancel2bool(show_msg(LANG["error"],
                                                    LANG["error_users_dat_saving_error"] + (LANG["error_details"]
                                                    % (details.__class__.__name__, details)), icon="error",
                                                    type="retrycancel")):  # ask about retry while the error is going on
                        try:  # try to
                            with open("users.dat", "wb") as file:  # open the users.dat,
                                pickle.dump(ulist, file)  # and dump users list here
                        except Exception as new_details:  # if something went wrong again,
                            details = new_details  # the new error details will be shown
                        else:  # if all is ok,
                            break  # there is no reason to ask anything again
        self.update_ulist()  # update the users' list

    def remove_this_user(self):
        """
        Removes the user after the user's confirm and if the password is right

        :return: no value
        :rtype: none
        """
        if self.userslistbox.curselection():  # if any user is selected,
            selected_user = self.userslistbox.get(self.userslistbox.curselection()[0])  # get selected user's name
            # if deletion was confirmed,
            if yesno2bool(show_msg(LANG["warning"], LANG["warning_remove_user"] % selected_user, "warning", "yesno")):
                if self.pwd_entry.get() == self.users_dict[selected_user]["password"]:  # if the right password entered,
                    del self.users_dict[selected_user]  # delete this user from the users' dict
                    try:  # try to
                        outf = open("users.dat", "wb")  # open the "users.dat" with bytes-writing mode,
                        pickle.dump(self.users_dict, outf)  # dump the dictionary
                        outf.close()  # close the "users.dat"
                    except PermissionError as details:
                        # if there is a PermissionError occurred, show an appropriate error.
                        showerror(LANG["error"],
                                  LANG["error_users_dat_could_not_open"] + (LANG["error_details"]
                                                    % (details.__class__.__name__, details)))
                    self.update_ulist()  # update the users' list from the "users.dat"
                else:
                    showerror(LANG["error"], LANG["error_wrong_password_try_again"])  # if the wrong password was entered, show an error
        else:
            showinfo(LANG["information"], LANG["information_select_something_at_first"])  # if nothing is selected, show a message

    def update_ulist(self):
        """
        Updates the users' listbox (after the users adding/removal)

        :return: no value
        :rtype: none
        """
        self.userslistbox.delete(0, END)  # clear all the users' list at first
        if "users.dat" in os.listdir(os.path.curdir):  # if there is the "users.dat" file in the app path,
            try:  # try to:
                self.users_dict = pickle.load(open("users.dat", "rb"))  # read the users' dict from the pickle
            except PermissionError:  # if you have no permissions to access the "users.dat",
                showerror(LANG["error"], LANG["error_users_dat_permissions"])
                self.close()  # terminate the process
            except (pickle.UnpicklingError, EOFError) as details:  # if the "users.dat" is damaged,
                if yesno2bool(show_msg(LANG["error"],
                                       LANG["error_users_dat_damaged_would_you_like_to_remove"] +
                                       (LANG["error_details"] %
                                                (details.__class__.__name__, details)), "error", "yesno")):
                    try:  # try to
                        os.remove("users.dat")  # remove it (after asking the user)
                    except Exception as details:  # if couldn't remove "users.dat",
                        showerror(LANG["error"], LANG["error_users_dat_could_not_remove"] + (LANG["error_details"]
                                                    % (details.__class__.__name__, details)))
                        self.destroy()
                        # TODO: destroy or close?
                    self.after(0, self.focus_force)  # set focus to the application window
                else:  # if user canceled the removal,
                    self.close()  # terminate the application process
            else:  # if could open the "users.dat"
                try:  # check
                    validate_users_dict(self.users_dict)  # if the users' dict has valid format
                except AssertionError:  # if it isn't,
                    showerror(LANG["error"],
                              LANG["error_users_dat_invalid_obj_is_pickled"])
                    os.remove("users.dat")  # remove the "users.dat" file
                else:
                    self.userslistbox.insert(END, *self.users_dict.keys())  # if all is OK, insert all users to the list
        else:
            # Hide the empty main window (this frame wasn't grid yet)
            self.withdraw()
            # show the message about the first run of the program.
            showinfo(LANG["information"], LANG["information_Trainer_hi_dear_user"])
            self.deiconify()  # show the main window now
        self.userslistbox.focus()  # focus on the users' list (to select a user without mouse, only with arrow keys)
        # And now select the first user from the list using .select_set(0) and .activate(0)
        self.userslistbox.select_set(0)  # select the first item of the user's listbox
        self.userslistbox.activate(0)  # activate the first item of the user's listbox

    def close(self):
        """
        Closes the users login window.

        :return: no value
        :rtype: none
        """
        self.destroy()  # destroy the window
        os._exit(0)  # terminate the process


class AddUser(Toplevel):
    """
    Class for the Toplevel window that is used to add a new user.
    """

    def __init__(self):
        super().__init__()

        self.resizable(False, False)  # make this dialog unresizable
        self.title(LANG["Add_user"])  # set the title of the dialog to "Add User"
        self.grab_set()  # set grab to disable the master window controls while adding a new user
        self.data = None  # now data is None
        Label(self, text=LANG["Name:"]).grid(row=0, column=0)  # create label with text "Username:"
        self.username_entry = Entry(self)  # create entry for the username,
        self.username_entry.grid(row=0, column=1)  # grid this entry,
        self.username_entry.focus()  # and focus on it
        Label(self, text=LANG["Password:"]).grid(row=1, column=0)  # create label with text "Password:"
        self.pwd_entry = Entry(self, show="●")  # create entry for the password,
        self.pwd_entry.grid(row=1, column=1)  # grid this entry
        # when the username is entered and the user press "Enter" ("Return") key, Tkinter focus on the password entry
        self.username_entry.bind("<Return>", lambda _event: self.pwd_entry.focus())
        # when both the username and the password are entered, app submits the user's data on "Enter" press
        self.pwd_entry.bind("<Return>", self.ok)
        Button(self, text="ОК", command=self.ok).grid(row=2, column=0, sticky="ew")  # create "OK" button
        Button(self, text=LANG["Cancel"], command=self.destroy).grid(row=2, column=1, sticky="ew")  # create "Cancel" button
        self.wait_window()  # doesn't return anything while the window is not destroyed

    def ok(self, _event=None):
        """
        Submits the new user when "OK" button is pressed.

        :param _event: the unused Tkinter event
        :return: no value
        """
        if not self.username_entry.get():  # if the user skipped username entry, give him a warning
            showwarning(LANG["warning"], "Будь ласка, введіть ім'я користувача!")
            return  # stop this function
        if not self.pwd_entry.get():  # if the user skipped password entry, give him a warning
            if not yesno2bool(show_msg("Увага",
                                       "Не рекомендується створювати користувачів без паролю. "
                                       "Оскільки кожен, хто має доступ до цього ПК може змінити вашу статистику або "
                                       "навіть просто видалити ваш акаунт користувача! Ви дійсно бажаєте продовжити?",
                                       "warning", "yesno")):  # ask the user about continuation
                return  # and stop the function
        self.data = self.username_entry.get(), self.pwd_entry.get()  # set user's data according to entries' values
        self.grab_release()  # release grab to allow usage of the master window again
        self.destroy()  # destroys the dialog


class HomeWindow(Toplevel):
    """
    The "Home" window class. This one is used to view the vocabulary contents and configuring words/game attribute.

    :param users_dict: the dict with the users (their names, passwords and stats)
    :param user: the username
    :param vocabulary_filename: the vocabulary filename (if passed to Trainer class before)
    :type users_dict: dict
    :type user: str
    :type vocabulary_filename: str
    """

    def __init__(self, users_dict, user, vocabulary_filename, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.after(0, self.focus_force)  # set focus on the "Home" window
        self.title("{} - Головна ({}) - PolyglotAssistant 1.00 Trainer".format("Без імені", user))  # set master window's title
        self.protocol("WM_DELETE_WINDOW", self.back)  # when the user tries to close the window, UserLoginWindow opens

        # create lists for good, bad, and unknown words  (they're empty while nothing is opened)
        self.good = []
        self.bad = []
        self.unknown = []

        # get users_dict and username (for stats)
        self.users_dict = users_dict  # set the users_dict attribute to the users_dict argument
        self.user = user  # set the user attribute to the same argument
        self.vocabulary_data = None  # while nothing is opened, vocabulary data is none
        self.vocabulary_filename = vocabulary_filename  # get .pav filename

        self.hk_man = HKManager(self)

        # Create menus
        self.menubar = Menu(self.master, tearoff=False)  # create the menubar at the top of the window
        self.config(menu=self.menubar)  # attach it to the master window
        # Create the "File" menu
        self.filemenu = Menu(self.menubar, tearoff=False)
        self.filemenu.add_command(label="Відкрити", command=self.open_vocabulary, accelerator="Ctrl+O")
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Увійти як інший користувач", command=lambda: self.back(), accelerator="Alt+F4")
        self.menubar.add_cascade(label="Файл", menu=self.filemenu)  # attach the "File" menu to the menubar
        # Create the "Help" menu
        self.helpmenu = Menu(self.menubar, tearoff=False)
        self.helpmenu.add_command(label="Виклик допомоги", command=help_, accelerator="F1")
        self.helpmenu.add_separator()
        self.helpmenu.add_command(label="Про PolyglotAssistant", command=about, accelerator="Ctrl+F1")
        self.helpmenu.add_command(label="Зв'язатися зі мною", command=contact_me, accelerator="Ctrl+Shift+F1")
        self.menubar.add_cascade(label="Допомога", menu=self.helpmenu)  # attach the "Help" menu to the menubar

        # self.iconbitmap("images/32x32/app_icon.ico")  # show the left-top window icon

        # Configure widgets' weight (to let them stretch)
        self.rowconfigure(0, weight=1)
        for column_id in (1, 2, 3, 4, 7):
            self.columnconfigure(column_id, weight=1)

        # Create and configure a Treeview widget for viewing the words pairs
        self.wtree = Treeview(self, show="headings", columns=["word", "translation"], selectmode=EXTENDED)
        self.wtree.heading("word", text="Слово")  # create the "Word" column
        self.wtree.heading("translation", text="Переклад")  # create the "Translation" column
        self.wtree.grid(row=0, column=0, columnspan=8, sticky="nsew")  # grid it to the screen

        # Create, grid, and configure self.scrollbar
        self.scrollbar = Scrollbar(self, command=self.wtree.yview)  # create and attach it to the words' tree
        self.scrollbar.grid(row=0, column=8, sticky="ns")  # show it using grid geometry manager
        self.wtree.config(yscrollcommand=self.scrollbar.set)  # attach the words' tree to the scrollbar

        # Create the bottom widgets
        Button(self, text="⏎", command=self.back, bg="#add8e6").grid(row=1, column=0, sticky="ew")  # create Back button
        self.good_label = Label(self, bg="#90EE90", relief=RAISED)  # create a label for good words pairs,
        self.good_label.grid(row=1, column=1, sticky="ew")  # and grid it on the master window
        self.bad_label = Label(self, bg="#FFCCCB", relief=RAISED)  # create a label for bad words pairs,
        self.bad_label.grid(row=1, column=2, sticky="ew")  # and grid it on the master window
        self.unknown_label = Label(self, bg="#EEEEEE", relief=RAISED)  # create a label for unknown words,
        self.unknown_label.grid(row=1, column=3, sticky="ew")  # and grid it on the master window
        self.total_label = Label(self, bg="white", relief=RAISED)  # create a label for total quantity of words,
        self.total_label.grid(row=1, column=4, sticky="ew")  # and grid it on the master window
        Label(self, text="Слів за гру: ").grid(row=1, column=5, sticky="ew")  # create "Words per game:" label
        self.wpg_var = IntVar(self)  # create variable for quantity of words
        self.wpg_var.set(12)  # set it 12 by default
        self.wpg_spb = Spinbox(self, width=3, from_=1, to_=999, textvariable=self.wpg_var,
                               validate="all")
        self.wpg_spb.configure(validatecommand=(self.register(self.validate_wpg), '%P'))  # set the validate command
        self.wpg_spb.grid(row=1, column=6, sticky="ew")  # create the words per game spinbox
        self.wpg_spb.bind("<Return>", self.start)  # after entering w/g value, the user can press "Enter" to continue
        Button(self, bg="#add8e6", text="Почати! ▶", command=self.start) \
            .grid(row=1, column=7, columnspan=2, sticky="ew")  # create the "Start" button

        # Create keybindings
        self.bind("<F1>", help_)
        self.bind("<Control-F1>", about)
        self.bind("<Control-Shift-F1>", contact_me)
        self.hk_man.add_binding("<Control-O>", self.open_vocabulary)

        self.update_stats()  # get stats for this user
        self.get_words_list()  # get words' list

        if self.vocabulary_filename:  # if a vocabulary filename was specified as a command-line arg,
            self.open_vocabulary(vocabulary_filename=self.vocabulary_filename)  # throw this arg to the open_vocabulary

    def open_vocabulary(self, _event=None, vocabulary_filename=None):
        """
        Opens a vocabulary from file.

        :param _event: the unused Tkinter event
        :param vocabulary_filename: the vocabulary filename (e.g. from command-line)
        :type _event: tkinter.Event
        :type vocabulary_filename: str or none
        :return: no value
        :rtype: none
        """
        try:  # try to
            # Get the filename
            if vocabulary_filename:  # if the vocabulary filename was passed (e.g from command-line),
                filename = vocabulary_filename  # set the filename to this,
            else:  # if the vocabulary filename was not passed,
                filename = askopenfilename(filetypes=[("Словник PolyglotAssitant", ".pav")])  # use the "Open" dialog
        except Exception as details:  # if something went wrong, show an error message
            showerror("Помилка", "На жаль, не вдалося відкрити цей словник!\n\nДеталі: %s (%s)" % (
                details.__class__.__name__, details))
        else:  # if could get filename,
            if filename:  # if the user didn't clicked "Cancel" in the open-file dialog,
                try:  # try to open this file
                    file = open(filename, "rb")  # open the file by its filename
                    self.vocabulary_data = pickle.load(file)  # and try to load the vocabulary from it
                except pickle.UnpicklingError:
                    # if couldn't unpickle it, show an error message
                    showerror("Помилка", "На жаль, не вдалося відкрити цей словник!\n\nДеталі: невідомий формат"
                                         "словнику, або він пошкоджений")
                except Exception as details:  # if something another went wrong
                    showerror("Помилка", "На жаль, не вдалося відкрити цей словник!\n\nДеталі: %s (%s)" % (
                        details.__class__.__name__, details))
                else:  # otherwise,
                    try:
                        # validate the unpickled vocabulary data
                        validate_vocabulary_data(self.vocabulary_data)
                    except AssertionError:  # if this vocabulary data is invalid, show an error message
                        showerror("Помилка",
                                  "На жаль, не вдалося відкрити цей словник!"
                                  "\n\nДеталі: формат цього словника не підтримується!")
                    else:  # if it is a valid learning plan,
                        self.vocabulary_filename = file.name  # and set up the filename attribute
                        self.get_words_list()  # get words list from the learning plan,
                        self.title("{} - Головна ({}) - PolyglotAssistant 1.00 Trainer".format(
                            self.vocabulary_filename, self.user))  # update the title
                        vocabulary_len = len(self.vocabulary_data)  # get the vocabulary length
                        if vocabulary_len > 12:  # if it is bigger, than 12,
                            self.wpg_var.set(12)  # set the default words-per-game value to 12
                            self.wpg_spb.configure(
                                to=vocabulary_len if vocabulary_len < 1000 else 999)  # set its max value
                        else:  # if it is less, than 12,
                            self.wpg_var.set(vocabulary_len)  # set the default words-per-game value to the length
                            self.wpg_spb.configure(to=vocabulary_len)  # set its max value
        self.after(0, self.focus_force)  # set the focus on the window

    def get_words_list(self):
        """
        Get the words' list and fill the Treeview with its data.

        :return: no value
        :rtype: none
        """
        # clear all the words' lists (good, bad and unknown),
        self.good.clear()
        self.bad.clear()
        self.unknown.clear()
        self.wtree.delete(*self.wtree.get_children())  # and clear the list with the previous vocabualry words' pairs
        if self.vocabulary_data:  # if any vocabulary is opened,
            if self.vocabulary_filename in self.users_dict[self.user]["stats"]:  # if the user trained this file before
                for pair in self.vocabulary_data:  # check every pair,
                    # if it is in the list of the "good" pairs,
                    if pair in self.users_dict[self.user]["stats"][self.vocabulary_filename]["good"]:
                        self.wtree.insert("", END, values=pair, tag="good")  # add it to the pairs' list with tag "good"
                        self.good.append(pair)  # append pair to the list for good words' pairs
                    # if it is in the list of the "bad" pairs,
                    elif pair in self.users_dict[self.user]["stats"][self.vocabulary_filename]["bad"]:
                        self.wtree.insert("", END, values=pair, tag="bad")  # add it in the  list with tag "bad"
                        self.bad.append(pair)  # append pair to the list for bad words' pairs
                    else:
                        # if the word wasn't trained yet,
                        self.wtree.insert("", END, values=pair, tag="unknown")  # add it to the list with "unknown" tag
                        self.unknown.append(pair)  # append the pair to the list for unknown words' pairs
            else:  # if this is the first time user uses this vocabulary,
                # add this filename to the users_dict
                self.users_dict[self.user]["stats"][self.vocabulary_filename] = {"good": set(),
                                                                                 "bad": set()}
                for pair in self.vocabulary_data:  # add every pair
                    self.wtree.insert("", END, values=pair, tag="unknown")  # to the pairs' list with "unknown" tag,
                    self.unknown.append(pair)  # and append to the list for unknown words' pairs
            # set the appropriate colors to every word's pair
            self.wtree.tag_configure("good", background="#90EE90")
            self.wtree.tag_configure("bad", background="#FFCCCB")
            self.wtree.tag_configure("unknown", background="#EEEEEE")
            self.update_stats()  # and update the stats (labels' text values)

    def update_stats(self):
        """
        Update the statistics (at the bottom of the window).

        :return: no value
        :rtype: none
        """
        # if anything is opened, get the values from there, otherwise use queestion marks instead
        good, bad, unknown, total = (len(self.good), len(self.bad), len(self.unknown),
                                     len(self.wtree.get_children())) if self.vocabulary_filename else (
            "?", "?", "?", "?")
        self.good_label["text"] = "Добре: %s" % good
        self.bad_label["text"] = "Погано: %s" % bad
        self.unknown_label["text"] = "Не треновано: %s" % unknown
        self.total_label["text"] = "Усього: %s" % total

    def validate_wpg(self, P):
        """
        Validates the words per game entry.

        Its value must be an empty string, or a string integer in the allowed range

        :param P: the WPG value
        :type P: str
        :return: `True` for a valid WPG value, `False` - for an invalid one.
        :rtype: bool
        """
        if P.isdigit():  # if the value is a number,
            if int(P) in range(1, int(self.wpg_spb["to"]) + 1):  # and if P is in the allowed range,
                return True  # this is a valid value
        elif P == "":  # if the value is empty, it is also correct
            return True
        # if the value doesn't meet these criterias,
        self.bell()  # play the bell sound,
        return False  # it is incorrect

    def back(self):
        """
        Return to the users login window.

        :return: no value
        :rtype: none
        """
        self.destroy()  # destroy the Home window
        Trainer(self.vocabulary_filename)  # reopen the Trainer with the same vocabulary values

    def start(self, _event=None):
        """
        Starts a Gym session if the vocabulary is opened.

        :param _event: the unused Tkinter event
        :type _event: tkinter.Event
        :return: no value
        :rtype: none
        """
        if self.vocabulary_filename:  # if any vocabulary is opened,
            self.withdraw()  # close the Home window,
            gym = GymWindow(self.good, self.bad, self.unknown, self.wpg_var.get())  # and create a Gym window
            # if the user opens this vocabulary at first,
            if self.vocabulary_filename not in self.users_dict[self.user]["stats"]:
                self.users_dict[self.user]["stats"][self.vocabulary_filename] = {"good": set(),
                                                                                 "bad": set()}  # add it to the list
            # Tidy the stats (reverse them to accord the vocabulary data)
            new_good = tidy_stats(gym.new_good, self.vocabulary_data)  # get the tidied good stats
            new_bad = tidy_stats(gym.new_bad, self.vocabulary_data)  # get the tidied bad stats
            for pair in new_good:  # process every pair in the new good-known words' list
                # if the pair was in bad-known words before,
                if pair in self.users_dict[self.user]["stats"][self.vocabulary_filename]["bad"]:
                    self.users_dict[self.user]["stats"][self.vocabulary_filename]["bad"].remove(
                        pair)  # remove it from there,
                self.users_dict[self.user]["stats"][self.vocabulary_filename]["good"].add(
                    pair)  # and add it to the good-known words' list
            for pair in new_bad:  # process every pair in the new bad-known words' list
                # if the pair was in good-known words' list before,
                if pair in self.users_dict[self.user]["stats"][self.vocabulary_filename]["good"]:
                    self.users_dict[self.user]["stats"][self.vocabulary_filename]["good"].remove(
                        pair)  # remove it from there,
                self.users_dict[self.user]["stats"][self.vocabulary_filename]["bad"].add(
                    pair)  # and add it to the bad-known words list
            try:  # try to
                udat = open("users.dat", "wb")  # open the users.dat file,
                pickle.dump(self.users_dict, udat)  # and dump the stats there
            except Exception as details:  # if there is an unexpected problem occurred,
                while retrycancel2bool(show_msg("Помилка",
                                                "Не вдалося зберегти users.dat через невідому помилку, тому "
                                                "статистику не збережено. "
                                                "Чи не бажаєте повторити?\n\nДеталі: %s (%s)"
                                                % (details.__class__.__name__, details), icon="error",
                                                type="retrycancel")):  # while the user asks to retry,
                    try:  # try to
                        with open("users.dat", "wb") as udat:  # open it again,
                            pickle.dump(self.users_dict, udat)  # and dump the new stats there
                    except Exception as new_details:  # if something went wrong again,
                        details = new_details  # show the new details
                    else:  # if all is OK,
                        break  # there is no reason to ask to retry again
            self.get_words_list()  # get the list of the words
            self.deiconify()  # show the window
            self.after(0, self.focus_force)  # set the focus to the window
        else:  # if nothing opened,
            showerror("Помилка",
                      "Перед тим, як почати, відкрийте словник."
                      "\nЩоб створити новий словник, використовуйте Editor.")


class GymWindow(Toplevel):
    """
    The class for the Gym window. Here you can learn new words.

    :param good: the list of the good words
    :param bad: the list of the bad words
    :param unknown: the list of the untried words
    :param wpg: how many words should be asked per game
    :type good: list[tuples]
    :type bad: list[tuples]
    :type unknown: list[tuples]
    :type wpg: int
    """

    def __init__(self, good, bad, unknown, wpg, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.after(0, self.focus_force)  # set the focus on the GymWindow
        self.title("Спортзала - PolyglotAssistant 1.00 Trainer")  # set the master window title

        # self.iconbitmap("images/32x32/app_icon.ico")  # show the left-top window icon

        self.tg_after = None  # set the future after timer event to None (before it is created)
        # Create two sets - for good and bad words
        self.new_good = set()
        self.new_bad = set()
        self.score = 0  # the score is 0 at the game start

        # Generate the words' pairs list (shuffle all the lists, and then generate a "smart" queue)
        random.shuffle(bad)
        random.shuffle(unknown)
        random.shuffle(good)
        self.queue = (2 * bad + unknown + good)[:wpg]  # create the queue,
        random.shuffle(self.queue)  # and shuffle it
        self.queue += random.sample(reverse_pairs(self.queue), len(self.queue))  # add the reversed pairs to queue
        self.totally = len(self.queue)  # get the total quantity of the words'pairs

        self.pair = None  # current pair is None (at first)
        self.word_label = Label(self)  # create a label for the word,
        self.word_label.grid(row=0, column=0, columnspan=5, sticky="ew")  # and grid it
        self.time_pb = Progressbar(self)  # create the time progressbar,
        self.time_pb.grid(row=1, column=0, columnspan=6, sticky="nsew")  # and grid it
        Button(self, text="⏎", command=self.back).grid(row=2, column=0,
                                                       sticky="ew")  # create and grid the "Back" button
        Label(self, text="Переклад: ").grid(row=2, column=1,
                                               sticky="ew")  # create and grid the "Translation: " label
        self.translation_entry = Entry(self)  # create the translation entry (where the user enters the translation),
        self.translation_entry.grid(row=2, column=2, sticky="ew")  # and grid it
        self.translation_entry.focus()  # focus on this entry
        self.ok_button = Button(self, text="ОК", command=self.ok)  # create the "OK" button
        self.ok_button.grid(row=2, column=3, sticky="ew")  # grid the "OK" button
        self.skip_button = Button(self, text="Пропустити", command=self.skip)  # create the "Skip" button
        self.skip_button.grid(row=2, column=4, sticky="ew")  # grid the the "Skip" button
        self.score_label = Label(self)  # create a label that displays score value (answered/totally)
        self.score_label.grid(row=2, column=5, sticky="ew")  # show it using grid geometry manager
        self.update_score_label()  # update it with the first values
        self.pass_a_word()  # ask user to translate the first word
        self.wait_window()  # wait until the Gym will be closed

    def pass_a_word(self):
        """
        Pass a new word to the user.

        :return: no value
        :rtype: none
        """
        if self.queue:  # if there is something in the queue
            self.enable_controls()  # enable the controls
            self.translation_entry.delete(0, END)  # clear it
            self.pair = self.queue.pop(0)  # get the pair from the queue
            self.word_label["text"] = self.pair[0]  # show the pair source
            self.time_pb.start(100)  # start the time progress bar with the 100ms interval
            # after the 9.9 seconds; not 10 seconds - the progressbar restarts then
            self.tg_after = self.after(9900, self.timeout)
            self.enable_controls()  # enable the controls
        else:  # if the queue is empty,
            self.disable_controls()  # disable the controls
            play_sound("sound/applause.wav")  # play the applause sound
            self.word_label["text"] = "Ура! Ви закінчили тренування!"  # show the congrats-label instead of a word
            self.after(3000, self.back)  # close the Gym

    def back(self):
        """
        Return back to the "Home" window.

        :return: no value
        :rtype: none
        """
        self.destroy()  # destroys the Gym window

    def ok(self, _event=None):
        """
        Submits the right words and plays the "right" sound for them, otherwise only plays the sound for the "wrong" one

        :param _event: the unused Tkinter event
        :type _event: tkinter.Event
        :return: no value
        :rtype: none
        """
        if self.is_right_answer():  # if the right answer entered
            play_sound("sound/shot.wav")  # play the shoot sound
            self.score += 1  # increase the score value by 1
            self.update_score_label()  # update the score label
            # if the current pair is not neither in good-known words nor in bad-known ones
            if (self.pair not in self.new_good) and (not tuple(reversed(self.pair)) in self.new_good):
                if (self.pair not in self.new_bad) and (not tuple(reversed(self.pair)) in self.new_bad):
                    self.new_good.add(self.pair)  # add it to the goods' one
            self.time_pb.stop()  # stop the progressbar
            self.after_cancel(self.tg_after)  # stop the timer event
            self.pass_a_word()  # pass a new word to user
        else:  # if the wrong answer entered,
            play_sound("sound/wrong.wav")  # play the wrong sound

    def _skip(self, action):
        """
        The function that called for the bad-known words (timeout and skip)

        :param action: can be `"Timeout"` or `"Skip?"`for timeout and skip
        :type action: str
        :return: no value
        :rtype: none
        """
        if self.is_right_answer() and action == "Час сплив!":  # if the answer is right, and the skip is caused by timeout
            self.ok()  # submit the word
        else:  # if the answer is wrong,
            self.score += 1  # increase the score by 1
            self.totally += 2  # increase the total quantity by two (2 pairs will be added)
            self.update_score_label()  # update the score label
            self.disable_controls()  # disable controls
            play_sound("sound/skip.wav")  # play the skip sound
            self.time_pb.stop()  # stop the progressbar
            self.word_label["text"] = "Упс! {} \"{}\" <=> \"{}\"".format(action, *self.pair)  # update the word label
            self.disable_controls()  # disable controls
            # If the pair was not add to bad-known list before, add it now
            if (self.pair not in self.new_bad) and (not tuple(reversed(self.pair)) in self.new_bad):
                self.new_bad.add(self.pair)  # add it to bad-known words set
                if self.pair in self.new_good:  # if the pair is in the good words,
                    self.new_good.remove(self.pair)  # remove it from there
                elif tuple(reversed(self.pair)) in self.new_good:  # if the reversed pair is in good-known words' set
                    self.new_good.remove(tuple(reversed(self.pair)))  # remove it from there
            # Add the pair to the queue for two times
            for _ in range(2):
                self.queue.append(self.pair)
            self.after(3000, self.pass_a_word)  # wait for 3 seconds, and then pass a new word to user

    def skip(self, _event=None):
        """
        Skip the word (Esc key press or "Skip" button click)

        :param _event: the unused Tkinter event
        :type _event: tkinter.Event
        :return: no value
        :rtype: none
        """
        self.after_cancel(self.tg_after)  # cancel the timer after event
        self._skip("Пропуск?")  # and skip the pair as a skip

    def timeout(self):
        """
        Timeout for the word (30 seconds)

        :return: no value
        :rtype: none
        """
        self._skip("Час сплив!")  # skip the pair as a timeout

    def enable_controls(self):
        """
        Enable the controls ("OK", "Skip" buttons, their hotkey bindings and the translation entry)

        :return: no value
        :rtype: none
        """
        # Unbind the hotkeys bindings
        self.translation_entry.bind("<Return>", self.ok)  # on "Return" press the word will be accepted (if it is right)
        self.translation_entry.bind("<Escape>", self.skip)  # if the user press "Esc", the word will be skipped
        # Disable the GUI objects
        self.ok_button["state"] = "normal"  # enable the "OK" button
        self.skip_button["state"] = "normal"  # enable the "Skip" button
        self.translation_entry["state"] = "normal"  # enable the enter for entering translation

    def disable_controls(self):
        """
        Disable the controls ("OK", "Skip" buttons, their hotkey bindings and the translation entry)

        :return: no value
        :rtype: none
        """
        # Unbind the hotkeys bindings
        self.translation_entry.unbind("<Return>")
        self.translation_entry.unbind("<Escape>")
        # Disable the GUI objects
        self.ok_button["state"] = "disabled"  # disable the "OK" button
        self.skip_button["state"] = "disabled"  # disable the "Skip" button
        self.translation_entry["state"] = "disabled"  # disable the enter for entering translation

    def is_right_answer(self):
        """
        Checks is the answer is right. Returns `True` if yes, otherwise `False`

        :return: `True` or `False` depending on the answer quality
        :rtype: bool
        """
        return True if self.translation_entry.get().replace("ё", "е").replace("Ё", "Е") == self.pair[1]. \
            replace("ё", "е").replace("Ё", "Е") else False

    def update_score_label(self):
        """
        Updates the score label.

        :return: no value
        :rtype: none
        """

        self.score_label["text"] = "%s/%s" % (self.score, self.totally)  # format the score label


def show_usage():
    """
    Shows the usage of the command-line interface.

    :return: no value
    :rtype: none
    """
    Tk().withdraw()  # create and hide the window to avoid the appearance of the blank window on the screen
    showerror("Помилка", "Ви намагаєтеся запустити цю програму якимось дивним чином."
                       "\n\nВикористання:\nTrainer.exe vocabulary.pav")
    os._exit(0)  # terminate the process


if __name__ == "__main__":
    # Check the command-line arguments
    if len(sys.argv) == 1:  # if no command-line arguments specified,
        Trainer().mainloop()  # create a Trainer's window
    elif len(sys.argv) == 2:  # if a file is specified as a command-line argument,
        if os.path.splitext(sys.argv[-1])[-1] == ".pav":  # if its extension is ".pav" (PolyglotAssistant Vocabulary)
            Trainer(sys.argv[-1].replace("\\", "/")).mainloop()  # create a window, and pass the file arg to opener
        else:  # if the file's extension doesn't looks like a valid PolyglotAssistant Vocabulary file extension
            show_usage()  # show usage
    else:  # if there are multiple args,
        show_usage()  # show the command-line interface usage
