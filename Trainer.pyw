#!/usr/bin/python3

# This application uses sound from Scratch 1.4 and https://noisefx.ru/
from tkinter import *
from tkinter.messagebox import showinfo, showerror, _show as show_msg
from tkinter.filedialog import askopenfile
from tkinter.ttk import Treeview, Entry, Progressbar, Scrollbar
try:
    # if Python >= 3.7:
    from tkinter.ttk import Spinbox
except ImportError:
    # otherwise
    pass
import winsound
import random
import pickle
import os
import sys

import pystray

from utils import yesno2bool, validate_users_dict, validate_lwp_data, reverse_pairs, help_, about, contact_me, tidy_stats


## TODO: fix back function
## TODO: add timer and score viewer in the right down corner of the window
## TODO: add opening from Editor and from a .lwp file
# TODO: add config dialog
## TODO: shuffle the translations' list (unknown, good, bad separately)
# TODO: to make the entered password character turn into the black circles only after a second
## TODO: configure the smart timer

class Trainer(Tk):
    def __init__(self, lwp_filename=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.withdraw()
        ul_window = UserLoginWindow()  # create a toplevel for user logging
        if ul_window.user.get():  # if user is logged in,
            ul_window.destroy()  # destroy the user login window
            HomeWindow(ul_window.users_dict, ul_window.user.get(), lwp_filename)  # and create the home window


class UserLoginWindow(Toplevel):
    def __init__(self):
        super().__init__()
        self.title("Login - LearnWords 1.0 Trainer")  # set title "Login" to the frame
        self.resizable(False, False)  # make the trainer window unresizable
        self.after(1, lambda: self.focus_force())  # focus to the trainer window on start
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
        Label(pwd_frame, text="Password:").grid(row=0, column=0, sticky="ew")  # a label, which says "Password:"
        self.pwd_entry = Entry(pwd_frame, show="●")  # entry for the password
        self.pwd_entry.grid(row=0, column=1, sticky="ew")  # grid the password entry
        self.pwd_entry.bind("<Return>", self.login_as_this_user)
        pwd_frame.grid(columnspan=5)  # grid password frame
        # create the buttons
        Button(self, text="Login as this user", command=self.login_as_this_user).grid(row=2, column=0, sticky="ew")
        Button(self, text="Add a new user", command=self.add_a_new_user).grid(row=2, column=1, sticky="ew")
        Button(self, text="Remove this user", command=self.remove_this_user).grid(row=2, column=2, sticky="ew")
        Button(self, text="Cancel", command=self.destroy).grid(row=2, column=3, columnspan=2, sticky="ew")
        self.bind("<Escape>", lambda _event: self.destroy())
        self.update_ulist()  # update user list (it is empty)
        self.grid()  # grid this frame in the master window
        self.wait_variable(self.user)  # wait (don't return anything) while the user won't log in

    def login_double_click(self, event):
        if event.y <= 17 * self.userslistbox.size():  # if the mouse y on the users' list belongs to any username
            self.login_as_this_user()  # login as the selected user

    def login_as_this_user(self, _event=None):
        selection = self.userslistbox.curselection()  # get user's selection
        if selection:  # if any user is selected,
            selected_user = self.userslistbox.get(selection[0])  # get the first (the single one) element from selection
            if self.pwd_entry.get() == self.users_dict[selected_user]["password"]:  # if right password is entered
                self.user.set(selected_user)  # return (see "wait_variable" above) the username of the selected user
            else:
                # if the wrong password entered
                showerror("Error", "Unfortunately, you entered the wrong password! Try again, please.")
        else:
            # if user was not selected, show an appropriate message
            showinfo("Information", "Choose a user at first. If there is no users in the list, add a new one.")

    def add_a_new_user(self):
        udata = AddUser().data  # get the user's data - (name, password) if wasn't canceled, None otherwise
        if udata:  # if the new user's adding was not canceled,
            if "users.dat" in os.listdir(os.path.curdir):  # if there is "users.dat" in the app path already
                try:
                    udat = open("users.dat", "rb")
                except FileNotFoundError as details:  # if submitted file disappeared suddenly
                    showerror("Error", "Couldn't open the users.dat file. Check its location. Application will exit now.\n\nDetails: FileNotFoundError (%s)" % details)
                    self.destroy()
                except PermissionError as details:  # if the access to the file denied
                    showerror("Error", "Couldn't open the users.dat file. Check your permissions to read it. Application will exit now.\n\nDetails: PermissionError (%s)" % details)
                    self.destroy()
                except Exception as details:  # if any other problem happened
                    showerror("Error", "During opening the users.dat file unexpected error occured. Application will exit now.\n\nDetails: %s (%s)" % (details.__class__.__name__, details))
                    self.destroy()
                else:
                    try:
                        ulist = pickle.load(udat)  # try to read it,
                    except (pickle.UnpicklingError, EOFError) as details:  # if the file is damaged, or its format is unsupported
                        showerror("Error",
                                  "The users.dat is corrupted or has an unsupported format!\n\nDetails: %s" % details)
                    except Exception as details:  # if unexpected error occured,
                        showerror("Error",
                                  "During opening the users.dat unexpected error occured\n\nDetails: %s (%s)" % (details.__class__.__name__, details))
            else:
                ulist = {}  # if there is no "users.dat" in the app path, create a new users' dictionary
            ulist[udata[0]] = {"password": udata[1], "stats": {}}  # assign new user's name with his password and stats
            try:
                pickle.dump(ulist, open("users.dat", "wb"))  # dump it all into new "users.dat" file
            except Exception as details:
                while yesno2bool(show_msg("Error", "During saving the users.dat file an unexpected error occured. New user was not saved. "
                         "Do you want to retry?\n\nDetails: %s (%s)" % (details.__class__.__name__, details), "error", "yesno")):
                    try:
                        pickle.dump(ulist, open("users.dat", "wb"))
                    except:
                        pass
                    else:
                        break
        self.update_ulist()  # update the users' list

    def remove_this_user(self):
        if self.userslistbox.curselection():  # if any user is selected,
            selected_user = self.userslistbox.get(self.userslistbox.curselection()[0])  # get selected user's name
            # if deletion was confirmed,
            if yesno2bool(show_msg("Warning", "This will permanently delete the user with name \"{}\". "
                                              "Do you want to continue?".format(selected_user), "warning", "yesno")):
                if self.pwd_entry.get() == self.users_dict[selected_user]["password"]:  # if the right password entered,
                    del self.users_dict[selected_user]  # delete this user from the users' dict
                    try:
                        outf = open("users.dat", "wb")  # open the "users.dat" with bytes-writing mode,
                        pickle.dump(self.users_dict, outf)  # dump the dictionary
                        outf.close()  # close the "users.dat"
                    except PermissionError:
                        # if there is a PermissionError occured, show an appropriate error.
                        showerror("Error", "Unable to access the user.dat file. Check your permissions for reading.")
                    self.update_ulist()  # update the users' list from the "users.dat"
                else:
                    showerror("Error", "Enter the right password!")  # if the wrong password was entered, show an error
        else:
            showinfo("Information", "Choose what to remove at first.")  # if none is selected, show a message

    def update_ulist(self):
        self.userslistbox.delete(0, END)  # clear all the users' list at first
        if "users.dat" in os.listdir(os.path.curdir):  # if there is the "users.dat" file in the app path,
            try:
                self.users_dict = pickle.load(open("users.dat", "rb"))  # try to read the users' dict from the pickle
            except PermissionError:
                # if it couldn't open "users.dat" due to permissions error, show an error and exit.
                showerror("Error", "Couldn't open users.dat. Check your permissions for reading this file and retry.")
                self.destroy()
            except pickle.UnpicklingError as details:
                if yesno2bool(show_msg("Error", "The users.dat is damaged. "
                                       "Do you want to remove it and add new users then?\n\nDetails: %s (%s)" %
                                       (details.__class__.__name__, details), "error", "yesno")):
                    try:
                        os.remove("users.dat")
                    except Exception as details:
                        showerror("Error", "Couldn't remove the damaged users.dat file.\n\nDetails: %s (%s)" % (details.__class__.__name__, details))
                    self.focus_force()
                else:
                    self.destroy()
            except EOFError:
                pass
            # TODO: exceptions
            else:
                try:
                    validate_users_dict(self.users_dict)  # if the users' dict is valid
                except:
                    # if the users' dict is invalid, show an error, remove the "users.dat" file, and then continue
                    showerror("Error",
                              "The users.dat is damaged. It'll be removed. Add new users then. "
                              "\n\nDetails: invalid object is pickled.")
                    os.remove("users.dat")
                else:
                    self.userslistbox.insert(END, *self.users_dict.keys())  # if all is OK insert all users to the list
        else:
            # Hide the empty main window (this frame wasn't grid yet)
            self.withdraw()
            # show the message about the first run of the program.
            showinfo("Information", "Hello, dear user! Probably, this is the first run of this program."
                                    "\nAt first you need to Add a new user.")
            self.deiconify()  # Show the main window now
        self.userslistbox.focus()  # focus on the users' list (to select a user without mouse, only with arrow keys)
        # And now select the first user from the list using .select_set(0) and .activate(0)
        self.userslistbox.select_set(0)
        self.userslistbox.activate(0)


class AddUser(Toplevel):
    def __init__(self):
        super().__init__()
        self.resizable(False, False)  # make this dialog unresizable
        # TODO: why doesn't it work?
        # self.transient(self.master)  # make it transient from its master (self.master)
        self.title("Add User")  # set the title of the dialog to "Add User"
        self.grab_set()  # set grab to disable the master window controls while adding a new user
        self.data = None  # now data is None
        Label(self, text="Username:").grid(row=0, column=0)  # create label with text "Username:"
        self.username_entry = Entry(self)  # create entry for the username,
        self.username_entry.grid(row=0, column=1)  # grid this entry,
        self.username_entry.focus()  # and focus on it
        Label(self, text="Password:").grid(row=1, column=0)  # create label with text "Password:"
        self.pwd_entry = Entry(self, show="●")  # create entry for the password,
        self.pwd_entry.grid(row=1, column=1)  # grid this entry
        # when the username is entered and the user press "Enter" ("Return") key, Tkinter focus on the password entry
        self.username_entry.bind("<Return>", lambda _event: self.pwd_entry.focus())
        # when both the username and the password are entered, app submits the user's data on "Enter" press
        self.pwd_entry.bind("<Return>", self.ok)
        Button(self, text="OK", command=self.ok).grid(row=2, column=0, sticky="ew")  # create "OK" button
        Button(self, text="Cancel", command=self.destroy).grid(row=2, column=1, sticky="ew")  # create "Cancel" button
        self.wait_window()  # doesn't returns anything while the window is not destroyed

    def ok(self, _event=None):
        if not self.username_entry.get():  # if the user skipped username entry, give him a warning
            showwarning("Warning", "Cannot create a user without username! Enter a username, please!")
            return
        if not self.pwd_entry.get():  # if the user skipped password entry, give him a warning
            if not yesno2bool(show_msg("Warning",
                                       "It's highly unrecommended to create users with empty passwords. "
                                       "Everyone can change your statistics (by doing your exercises) or even remove "
                                       "your user account at all! Do you want to continue?",
                                       "warning", "yesno")):
                return
        self.data = self.username_entry.get(), self.pwd_entry.get()  # set user's data according to entries' values
        self.grab_release()  # release grab to allow usage of the master window again
        self.destroy()  # destroys the dialog


class HomeWindow(Toplevel):
    def __init__(self, users_dict, user, lwp_filename, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # TODO: hotkeys support
        self.CTRL_HOTKEYS_DICT = {111: self.open_lwp, 1097: self.open_lwp, 79: self.open_lwp, 1065: self.open_lwp}
        self.CTRL_SHIFT_HOTKEYS_DICT = {67: self.configure_trainer, 1057: self.configure_trainer,
                                        99: self.configure_trainer, 1089: self.configure_trainer}

        self.focus_force()
        self.title("{} - Home ({}) - LearnWords 1.0".format("Untitled", user))  # set master window's title
        # create lists for good, bad, and unknown words
        self.good = []
        self.bad = []
        self.unknown = []
        # get users_dict and username (for stats)
        self.users_dict = users_dict
        self.user = user
        self.learning_plan = None
        self.lwp_filename = lwp_filename # get .lwp filename
        # create menus
        self.menubar = Menu(self.master, tearoff=False)
        self.filemenu = Menu(self.menubar, tearoff=False)
        self.filemenu.add_command(label="Open", command=self.open_lwp, accelerator="Ctrl+O")
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=lambda: self.destroy(), accelerator="Alt+F4")
        self.menubar.add_cascade(label="File", menu=self.filemenu)
        self.toolsmenu = Menu(self.menubar, tearoff=False)
        self.toolsmenu.add_command(label="Configure Trainer", command=self.configure_trainer,
                                   accelerator="Ctrl+Shift+C")
        self.menubar.add_cascade(label="Tools", menu=self.toolsmenu)
        self.helpmenu = Menu(self.menubar, tearoff=False)
        self.helpmenu.add_command(label="LearnWords Help", accelerator="F1")
        self.helpmenu.add_separator()
        self.helpmenu.add_command(label="About LearnWords", accelerator="Ctrl+F1")
        self.helpmenu.add_command(label="Contact me", accelerator="Ctrl+Shift+F1")
        self.menubar.add_cascade(label="Help", menu=self.helpmenu)
        self.config(menu=self.menubar)  # set master window's menu = self.menubar

        # Configure weight
        self.rowconfigure(0, weight=1)
        for column_id in (1, 2, 3, 4, 7):
            self.columnconfigure(column_id, weight=1)
        
        # create and configure treeview for showing the words pairs
        self.wtree = Treeview(self, show="headings", columns=["word", "translation"], selectmode=EXTENDED)
        self.wtree.heading("word", text="Word")
        self.wtree.heading("translation", text="Translation")
        self.wtree.grid(row=0, column=0, columnspan=8, sticky="nsew")  # grid it to the screen
        # create, grid, and configure self.scrollbar)
        self.scrollbar = Scrollbar(self, command=self.wtree.yview)
        self.scrollbar.grid(row=0, column=8, sticky="ns")
        self.wtree.config(yscrollcommand=self.scrollbar.set)

        Button(self, text="⏎", command=self.back).grid(row=1, column=0, sticky="ew")  # create "Back" button
        self.good_button = Button(self, bg="green")  # create button for good words pairs,
        self.good_button.grid(row=1, column=1, sticky="ew")  # and grid it on the master window
        self.bad_button = Button(self, bg="red")  # create button for bad words pairs,
        self.bad_button.grid(row=1, column=2, sticky="ew")  # and grid it on the master window
        self.unknown_button = Button(self, bg="yellow")  # create button for unknown words,
        self.unknown_button.grid(row=1, column=3, sticky="ew")  # and grid it on the master window
        self.total_button = Button(self, bg="white")  # create button for total quantity of words,
        self.total_button.grid(row=1, column=4, sticky="ew")  # and grid it on the master window
        Label(self, text="Words per game: ").grid(row=1, column=5, sticky="ew")  # create label "Words per game:"
        self.wpg_var = IntVar(self)  # create variable for quantity of words
        self.wpg_var.set(12)  # set it 12 by default
        self.wpg_spb = Spinbox(self, width=3, from_=1, to_=999, textvariable=self.wpg_var,
                               validate="all", validatecommand=(self.register(self.validate_wpg), '%P'))
        self.wpg_spb.grid(row=1, column=6, sticky="ew")  # create the words per game spinbox
        self.wpg_spb.bind("<Return>", self.start)
        Button(self, bg="#add8e6", text="Start! ▶", command=self.start) \
            .grid(row=1, column=7, columnspan=2, sticky="ew")  # create the start button

        self.bind("<F1>", help_)
        self.bind("<Control-F1>", about)
        self.bind("<Control-Shift-F1>", contact_me)
        self.bind("<Control-Key>", self.ctrl_hotkeys_handler)
        self.bind("<Control-Shift-Key>", self.ctrl_shift_hotkeys_handler)
        
        self.update_stats()  # get stats for this user
        self.get_words_list()  # get words' list

        if self.lwp_filename:
            self.open_lwp(self.lwp_filename)
        # print(self.learning_plan)

    def open_lwp(self, lwp_filename=None):
        try:
            # try to open this file
            if lwp_filename:
                file = open(lwp_filename, "rb")
            else:
                file = askopenfile(mode="rb", filetypes=[("Learn Words Plan", ".lwp")])
            assert file
        except AssertionError:
            pass
        except:
            # if couldn't, show an error message
            showerror("Error", "Unable to open this file!")
        else:
            try:
                # try to load learning plan from the file
                self.learning_plan = pickle.load(file)
            except pickle.UnpicklingError as error:
                # if couldn't unpickle it, show an error message
                showerror("Error", "Unable to open the file!\n\nDetails: {}".format(error))
            else:
                try:
                    # validate the learning plan data, if the app could unpickle something
                    validate_lwp_data(self.learning_plan)
                except AssertionError:
                    # if this is invalid learning plan data, show an error message
                    showerror("Error",
                              "Unable to open the file!\n\nDetails: it doesn't looks like a valid learning plan file!")
                else:
                    # if it is a valid learning plan,
                    self.lwp_filename = file.name  # and set up the filename attribute
                    self.get_words_list()  # get words list from the learning plan,
                    self.title(
                        "{} - Home ({}) - LearnWords 1.0".format(self.lwp_filename, self.user))  # update the title
                    lwp_len = len(self.learning_plan)
                    if lwp_len > 12:
                        self.wpg_var.set(12)
                        self.wpg_spb.configure(to=lwp_len if lwp_len < 1000 else 999)
                    else:
                        self.wpg_var.set(lwp_len)
                        self.wpg_spb.configure(to=lwp_len)

    def configure_trainer(self):
        ConfigureTrainer()

    def ctrl_hotkeys_handler(self, event):
        if event.keysym_num in self.CTRL_HOTKEYS_DICT:
            self.CTRL_HOTKEYS_DICT[event.keysym_num]()

    def ctrl_shift_hotkeys_handler(self, event):
        if event.keysym_num in self.CTRL_SHIFT_HOTKEYS_DICT:
            self.CTRL_SHIFT_HOTKEYS_DICT[event.keysym_num]()

    def get_words_list(self):
        # clear all the words' lists (good, bad and unknown),
        self.good.clear()
        self.bad.clear()
        self.unknown.clear()
        self.wtree.delete(*self.wtree.get_children())  # and clear the list with the previous learning plan words' pairs
        if self.learning_plan:  # if any learning plan is opened,
            if self.lwp_filename in self.users_dict[self.user]["stats"]:  # if the user trained this file before
                for pair in self.learning_plan:  # check every pair,
                    if pair in self.users_dict[self.user]["stats"][self.lwp_filename]["good"]:  # if it is in the list of the "good" pairs,
                        self.wtree.insert("", END, values=pair, tag="good")  # add it to the pairs' list with tag "good"
                        self.good.append(pair)  # append pair to the list for good words' pairs
                    elif pair in self.users_dict[self.user]["stats"][self.lwp_filename]["bad"]:  # if it is in the list of the "bad" pairs,
                        self.wtree.insert("", END, values=pair, tag="bad")  # add it in the  list with tag "bad"
                        self.bad.append(pair)  # append pair to the list for bad words' pairs
                    else:
                        # if the word wasn't trained yet,
                        self.wtree.insert("", END, values=pair,
                                          tag="unknown")  # add it to the list with "unknown" tag
                        self.unknown.append(pair)  # append the pair to the list for unknown words' pairs
            else:
                self.users_dict[self.user]["stats"][self.lwp_filename] = {"good": set(), "bad": set()}
                # if the user opened this learning plan at first
                for pair in self.learning_plan:  # add every pair
                    self.wtree.insert("", END, values=pair,
                                      tag="unknown")  # to the pairs' list with "unknown" tag,
                    self.unknown.append(pair)  # and append to the list for unknown words' pairs
            # set appropriate colors to every word's pair        
            self.wtree.tag_configure("good", background="green")
            self.wtree.tag_configure("bad", background="red")
            self.wtree.tag_configure("unknown", background="yellow")
            self.update_stats()  # and update the stats (buttons labels)

    def update_stats(self):
        good, bad, unknown, total = (len(self.good), len(self.bad), len(self.unknown),
                                       len(self.wtree.get_children())) if self.lwp_filename else ("?", "?", "?", "?")
        self.good_button["text"] = "Good: %s" % good
        self.bad_button["text"] = "Bad: %s" % bad
        self.unknown_button["text"] = "Unknown: %s" % unknown
        self.total_button["text"] = "Total: %s" % total

    def validate_wpg(self, P):
        if P.isdigit():
            if int(P) in range(1, self.wpg_spb["to"] + 1):
                return True
        elif P == "":
            return True
        self.bell()
        return False

    def back(self):
        self.destroy()
        Trainer(self.learning_plan, self.lwp_filename)

    def start(self, _event=None):
        if self.lwp_filename:  # if any learning plan is opened,
            self.withdraw()
            gym = GymWindow(self.good, self.bad, self.unknown, self.wpg_var.get())
            # TODO: if canceled, no error
            if self.lwp_filename not in self.users_dict[self.user]["stats"]:
                self.users_dict[self.user]["stats"][self.lwp_filename] = {"good": set(), "bad": set()}
            new_good = tidy_stats(gym.new_good, self.learning_plan)
            new_bad = tidy_stats(gym.new_bad, self.learning_plan)
            for pair in new_good:
                if pair in self.users_dict[self.user]["stats"][self.lwp_filename]["bad"]:
                    self.users_dict[self.user]["stats"][self.lwp_filename]["bad"].remove(pair)
                self.users_dict[self.user]["stats"][self.lwp_filename]["good"].add(pair)
            for pair in new_bad:
                if pair in self.users_dict[self.user]["stats"][self.lwp_filename]["good"]:
                    self.users_dict[self.user]["stats"][self.lwp_filename]["good"].remove(pair)
                self.users_dict[self.user]["stats"][self.lwp_filename]["bad"].add(pair)      
            try:
                udat = open("users.dat", "wb")
                pickle.dump(self.users_dict, udat)
            except Exception as details:  # if there is an unexpected problem occured,
                while yesno2bool(show_msg("Error", "During saving the users.dat file an unexpected error occured. Statistics were not saved. "
                         "Do you want to retry?\n\nDetails: %s (%s)" % (details.__class__.__name__, details), "error", "yesno")):
                    try:
                        udat = open("users.dat", "wb")
                        pickle.dump(self.users_dict, udat)
                    except:
                        pass
                    else:
                        break
            self.get_words_list()
            self.deiconify()
        else:
            # if no learning plan was opened, show an error
            showerror("Error",
                      "Before you start, open your learning plan file."
                      "\nTo create a new learning plan, create it using Editor")


class GymWindow(Toplevel):
    def __init__(self, good, bad, unknown, wpg, *args, **kwargs):
        # TODO: score counter
        # TODO: automatic time counter
        super().__init__(*args, **kwargs)
        self.title("Gym - LearnWords 1.0")  # set the master window title "Gym..."
        self.tg_after = None
        self.new_good = set()
        self.new_bad = set()
        self.score = 0  # at first the score is 0
        # generate the words' pairs list (shuffle all the lists, and then generate a "smart" queue)
        random.shuffle(good)
        random.shuffle(bad)
        random.shuffle(unknown)
        self.queue = (2 * bad + unknown + good)[:wpg]
        self.queue += reverse_pairs(self.queue)
        """rp_bad = reverse_pairs(bad)
        rp_ntr = reverse_pairs(unknown)
        rp_good = reverse_pairs(good)
        random.shuffle(rp_bad)
        random.shuffle(rp_ntr)
        random.shuffle(rp_good)
        reversed_pairs = rp_bad + rp_ntr + rp_good
        self.queue += reversed_pairs[:wpg]"""
        self.totally = len(self.queue)
        self.pair = None  # current pair is None (at first)
        self.word_label = Label(self)  # create a label for the word,
        self.word_label.grid(row=0, column=0, columnspan=5, sticky="ew")  # and grid it
        self.time_pb = Progressbar(self)  # create the time progressbar,
        self.time_pb.grid(row=1, column=0, columnspan=5, sticky="nsew")  # and grid it
        Button(self, text="⏎", command=self.back).grid(row=2, column=0,
                                                       sticky="ew")  # create and grid the "Back" button
        Label(self, text="Translation: ").grid(row=2, column=1,
                                               sticky="ew")  # create and grid the "Translation: " label
        self.translation_entry = Entry(self)  # create the translation entry (where the user enters the translation),
        self.translation_entry.grid(row=2, column=2, sticky="ew")  # and grid it
        self.translation_entry.focus()  # focus on this entry
        self.ok_button = Button(self, text="OK", command=self.ok)  # create the "OK" button
        self.ok_button.grid(row=2, column=3, sticky="ew")  # grid the "OK" button
        self.skip_button = Button(self, text="Skip", command=self.skip)  # create the "Skip" button
        self.skip_button.grid(row=2, column=4, sticky="ew")  # grid the the "Skip" button
        self.score_label = Label(self)
        self.score_label.grid(row=2, column=5, sticky="ew")
        self.update_score_label()
        self.pass_a_word()  # get the first word
        self.grid()
        self.wait_window()

    def pass_a_word(self):
        if self.queue:
            self.ok_button["state"] = "normal"
            self.skip_button["state"] = "normal"
            self.translation_entry["state"] = "normal"
            self.translation_entry.delete(0, END)
            self.pair = self.queue.pop(0)
            self.word_label["text"] = self.pair[0]
            # self.time_pb.start(400 * len(self.pair[1]) // 100)
            # self.tg_after = self.after(400 * len(self.pair[1]) - 100, self.timeout)
            self.time_pb.start(100)
            self.tg_after = self.after(9900, self.timeout)
            self.enable_controls()
        else:
            self.disable_controls()
            winsound.PlaySound("sound/applause.wav", winsound.SND_ASYNC)
            self.word_label["text"] = "Hooray! You've shot all the words!"
            self.translation_entry["state"] = "disabled"
            self.ok_button["state"] = "disabled"
            self.skip_button["state"] = "disabled"
            self.after(3000, self.back)

    def back(self):
        self.destroy()

    def ok(self, _event=None):
        if self.is_right_answer():
            winsound.PlaySound("sound/shot.wav", winsound.SND_ASYNC)
            self.score += 1
            self.update_score_label()
            if (not self.pair in self.new_good) and (not tuple(reversed(self.pair)) in self.new_good):
                if (not self.pair in self.new_bad) and (not tuple(reversed(self.pair)) in self.new_bad):  # if it is not in the bads' set,
                    self.new_good.add(self.pair)  # add it to the goods' one
            self.time_pb.stop()
            self.after_cancel(self.tg_after)
            self.pass_a_word()
        else:
            pass
            winsound.PlaySound("sound/wrong.wav", winsound.SND_ASYNC)

    def _skip(self, action):
        if self.is_right_answer() and action == "Timeout!":
            self.ok()
        else:
            self.totally += 2
            self.update_score_label()
            self.disable_controls()
            winsound.PlaySound("sound/skip.wav", winsound.SND_ASYNC)
            self.time_pb.stop()
            self.word_label["text"] = "Oops! {} \"{}\" <=> \"{}\"".format(action, *self.pair)
            self.translation_entry["state"] = "disabled"
            self.ok_button["state"] = "disabled"
            self.skip_button["state"] = "disabled"
            if (not self.pair in self.new_bad) and (not tuple(reversed(self.pair)) in self.new_bad):
                self.new_bad.add(self.pair)  # add it to bads' set
                if self.pair in self.new_good:
                    self.new_good.remove(self.pair)  # remove it from there
                elif tuple(reversed(self.pair)) in self.new_good:  # if it is in goods' set,self.new_good.remove(tuple(reversed(self.pair)))
                    self.new_good.remove(tuple(reversed(self.pair)))
            for _ in range(2):
                self.queue.append(self.pair)
            self.after(3000, self.pass_a_word)

    def skip(self, _event=None):
        self.after_cancel(self.tg_after)
        self._skip("Skip?")

    def timeout(self):
        self._skip("Timeout!")

    def enable_controls(self):
        self.translation_entry.bind("<Return>", self.ok)  # on "Return" press the word will be accepted (if it is right)
        self.translation_entry.bind("<Escape>", self.skip)  # if the user press "Esc", the word will be skipped

    def disable_controls(self):
        self.translation_entry.unbind("<Return>")
        self.translation_entry.unbind("<Escape>")

    def is_right_answer(self):
        return True if self.translation_entry.get().replace("ё", "е").replace("Ё", "Е") == self.pair[1].\
            replace("ё", "е").replace("Ё", "Е") else False
    def update_score_label(self):
        self.score_label["text"] = "%s/%s" % (self.score, self.totally)
        
if __name__ == "__main__":
    if len(sys.argv) > 1:
        # TODO: sys.argv good work
        Trainer(sys.argv[-1].replace("\\", "/")).mainloop()
    else:
        Trainer().mainloop()
