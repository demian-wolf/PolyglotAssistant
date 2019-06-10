#!/usr/bin/python3
from tkinter import *
from tkinter.messagebox import showinfo, showerror, _show as show_msg
from tkinter.filedialog import *
from tkinter.ttk import Treeview, Entry
import pickle
import os

from utils import yesno2bool, validate_users_dict


class Trainer(Tk):
    def __init__(self, learning_plan=None, lwp_filename=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Login - LearnWords 1.0 Trainer")
        self.resizable(False, False)
        ul_frame = UserLoginFrame()
        if ul_frame.user.get():
            HomeFrame(ul_frame.users_dict, ul_frame.user.get(), learning_plan, lwp_filename).grid()

class UserLoginFrame(Frame):
    def __init__(self):
        super().__init__()
        self.user = StringVar()
        self.user.set("")
        self.users_dict = {}
        self.userslistbox = Listbox(self)
        self.userslistbox.grid(row=0, column=0, columnspan=6, sticky="nsew")
        self.userslistbox.bind("<Double-1>", self.login_double_click)
        self.userslistbox.bind("<Return>", self.login_as_this_user)
        self.scrollbar = Scrollbar(self, command=self.userslistbox.yview)
        self.scrollbar.grid(row=0, column=6, sticky="ns")
        self.userslistbox.config(yscrollcommand=self.scrollbar.set)
        pwd_frame = Frame(self)
        Label(pwd_frame, text="Password:").grid(row=0, column=0, sticky="ew")
        self.pwd_entry = Entry(pwd_frame)
        self.pwd_entry.grid(row=0, column=1, sticky="ew")
        pwd_frame.grid(columnspan=5)
        Button(self, text="Login as this user", command=self.login_as_this_user).grid(row=2, column=0, sticky="ew")
        Button(self, text="Add a new user", command=self.add_a_new_user).grid(row=2, column=1, sticky="ew")
        Button(self, text="Remove this user", command=self.remove_this_user).grid(row=2, column=2, sticky="ew")
        Button(self, text="Cancel", command=self.master.destroy).grid(row=2, column=3, columnspan=2, sticky="ew")
        self.update_ulist()
        self.grid()
        self.wait_variable(self.user)
    def login_double_click(self, event):
        if event.y <= 17 * self.userslistbox.size():
            self.login_as_this_user()
    def login_as_this_user(self, event=None):
        selection = self.userslistbox.curselection()
        if selection:
            selected_user = self.userslistbox.get(selection[0])
            if self.pwd_entry.get() == self.users_dict[selected_user]["password"]:
                self.user.set(selected_user)
                self.destroy()
            else:
                showerror("Error", "Unfortunately, you entered the wrong password! Try again, please.")
        else:
            showinfo("Information", "Choose a user at first. If there is no users in the list, add a new one.")
    def add_a_new_user(self):
        udata = AddUser().data
        if udata:
            if "users.dat" in os.listdir(os.path.curdir):
                try:
                    ulist = pickle.load(open("users.dat", "rb"))
                except:
                    ulist = {}
            else:
                ulist = {}
            ulist[udata[0]] = {"password": udata[1], "stats": {}}
            pickle.dump(ulist, open("users.dat", "wb"))
        self.update_ulist()
    def remove_this_user(self):
        if self.userslistbox.curselection():
            selected_user = self.userslistbox.get(self.userslistbox.curselection()[0])
            if yesno2bool(show_msg("Warning", "This will permanently delete the user with name \"{}\". Do you want to continue?".format(selected_user), "warning", "yesno")):
                if self.pwd_entry.get() == self.users_dict[selected_user]["password"]:
                    del self.users_dict[selected_user]
                    try:
                        outf = open("users.dat", "wb")
                        pickle.dump(self.users_dict, outf)
                        outf.close()
                    except PermissionError:
                        showerror("Error", "Unable to access the user.dat file. Check your permissions for reading.")
                    self.update_ulist()
                else:
                    showerror("Error", "Enter the right password!")
        else:
            showinfo("Information", "Choose what to remove at first.")


    def update_ulist(self):
        self.userslistbox.delete(0, END)
        if "users.dat" in os.listdir(os.path.curdir):
            try:
                self.users_dict = pickle.load(open("users.dat", "rb"))
            except PermissionError:
                showerror("Error", "Couldn't open users.dat. Check your permissions for reading this file.")
                self.master.destroy()
            except pickle.UnpicklingError as details:
                showerror("Error", "The users.dat is damaged. It'll be removed. Add new users after removing.\n\nDetails: {}".format(details))
                os.remove("users.dat")
            else:
                try:
                    validate_users_dict(self.users_dict)
                except:
                    showerror("Error", "The users.dat is damaged. It'll be removed.\n\nDetails: invalid object is pickled.")
                    os.remove("users.dat")
                else:
                    self.userslistbox.insert(END, *self.users_dict.keys())
        else:
            self.master.withdraw()
            showinfo("Information", "Hello, dear user! Probably, this is the first run of this program.\nAt first you need to Add a new user.")
            self.master.deiconify()
        self.userslistbox.focus()
        self.userslistbox.select_set(0)
        self.userslistbox.activate(0)
class AddUser(Toplevel):
    def __init__(self):
        super().__init__()
        self.resizable(False, False)
        self.transient(self.master)
        self.title("Add User")
        self.grab_set()
        self.data = None
        Label(self, text="Username:").grid(row=0, column=0)
        self.username_entry = Entry(self)
        self.username_entry.grid(row=0, column=1)
        self.username_entry.focus()
        Label(self, text="Password:").grid(row=1, column=0)
        self.pwd_entry = Entry(self)
        self.pwd_entry.grid(row=1, column=1)
        self.username_entry.bind("<Return>", lambda event=None: self.pwd_entry.focus())
        self.pwd_entry.bind("<Return>", self.ok)
        Button(self, text="OK", command=self.ok).grid(row=2, column=0, sticky="ew")
        Button(self, text="Cancel", command=self.destroy).grid(row=2, column=1, sticky="ew")
        self.wait_window()
    def ok(self, event=None):
        if not self.username_entry.get():
            if not yesno2bool(show_msg("Warning", "It's highly unrecommended to create users with empty usernames. Do you want to continue?", "warning", "yesno")):
                return
        if not self.pwd_entry.get():
            if not yesno2bool(show_msg("Warning", "It's highly unrecommended to create users with empty passwords. Everyone can change your statistics (by doing your exercises) or even remove your user account at all! Do you want to continue?", "warning", "yesno")):
                return
        self.data = self.username_entry.get(), self.pwd_entry.get()
        self.grab_release()
        self.destroy()

class HomeFrame(Frame):
    def __init__(self, users_dict, user, lwp_filename, learning_plan, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.master.title("Home ({}) - LearnWords 1.0".format(user))
        self.users_dict = users_dict
        self.user = user
        self.learning_plan = learning_plan
        self.lwp_filename = lwp_filename
        self.menubar = Menu(self.master, tearoff=False)
        self.filemenu = Menu(self.menubar, tearoff=False)
        self.filemenu.add_command(label="Open", command=self.open_lwp, accelerator="Ctrl+O")
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", accelerator="Alt+F4")
        self.menubar.add_cascade(label="File", menu=self.filemenu)
        self.toolsmenu = Menu(self.menubar, tearoff=False)
        self.toolsmenu.add_command(label="Configuration", accelerator="Ctrl+Alt+Shift+C")
        self.menubar.add_cascade(label="Tools", menu=self.toolsmenu)
        self.helpmenu = Menu(self.menubar, tearoff=False)
        self.helpmenu.add_command(label="LearnWords Help")
        self.helpmenu.add_separator()
        self.helpmenu.add_command(label="About LearnWords")
        self.helpmenu.add_command(label="Contact me")
        self.menubar.add_cascade(label="Help", menu=self.helpmenu)
        self.master.config(menu=self.menubar)

        self.wtree = Treeview(self, show="headings", columns=["word", "translation"], selectmode=EXTENDED)
        self.wtree.heading("word", text="Word")
        self.wtree.heading("translation", text="Translation")
        self.wtree.grid(row=0, column=0, columnspan=7, sticky="ew")
        self.yscrollbar = Scrollbar(self, command=self.wtree.yview)
        self.yscrollbar.grid(row=0, column=8, sticky="ns")
        self.wtree.config(yscrollcommand=self.yscrollbar.set)

        self.good_button = Button(self, bg="green")
        self.good_button.grid(row=1, column=0, sticky="ew")
        self.bad_button = Button(self, bg="red")
        self.bad_button.grid(row=1, column=1, sticky="ew")
        self.non_tried_button = Button(self, bg="yellow")
        self.non_tried_button.grid(row=1, column=2, sticky="ew")
        self.total_button = Button(self, bg="white")
        self.total_button.grid(row=1, column=3, sticky="ew")
        Label(self, text="Words a game: ").grid(row=1, column=4, sticky="ew")
        self.wag_entry = Entry(self, width=3)
        self.wag_entry.grid(row=1, column=5, sticky="ew")
        Button(self, text="Start").grid(row=1, column=6, columnspan=3, sticky="ew")
        self.update_stats(*"????")
        self.get_words_list()
    def open_lwp(self):
        try:
            file = askopenfile(mode="rb")
        except:
            showerror("Error", "Unable to open this file!")
        else:
            try:
                self.learning_plan = pickle.load(file)
            except pickle.UnpicklingError as error:
                showerror("Error", "Unable to open the file!\n\nDetails: {}".format(error))
            else:
                self.get_words_list()
                self.lwp_filename = file.name

    def get_words_list(self):
        good = 0
        bad = 0
        non_tried = 0
        self.wtree.delete(*self.wtree.get_children())
        if self.learning_plan:
            print(self.users_dict)
            if self.lwp_filename in self.users_dict[self.user]["stats"]:
                for pair in self.learning_plan:
                    if pair in self.users_dict[self.user]["stats"]["good"]:
                        self.wtree.insert("", END, values=pair, tag="good")
                        good += 1
                    elif pair in self.users_dict[self.user]["stats"]["bad"]:
                        self.wtree.insert("", END, values=pair, tags=("bad", ))
                        bad += 1
                    else:
                        self.wtree.insert("", END, values=pair, tags=("non-tried"))
                        non_tried += 1
            else:
                for pair in self.learning_plan:
                    self.wtree.insert("", END, values=pair, tags=("non-tried", ))
                    non_tried += 1
            self.wtree.tag_configure("good", background="green")
            self.wtree.tag_configure("bad", background="red")
            self.wtree.tag_configure("non-tried", background="yellow")
            self.update_stats(good, bad, non_tried, len(self.wtree.get_children()))

    def update_stats(self, good, bad, non_tried, total):
        self.good_button["text"] = "Good: {}".format(good)
        self.bad_button["text"] = "Bad: {}".format(bad)
        self.non_tried_button["text"] = "Non-tried: {}".format(non_tried)
        self.total_button["text"] = "Total: {}".format(total)
if __name__ == "__main__":
    Trainer().mainloop()