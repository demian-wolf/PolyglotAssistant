from tkinter import *
from tkinter.ttk import Entry


class Entry(Entry):
    def __init__(self, master):
        super().__init__(master)

        self.popup_menu = Menu(self, tearoff=0)
        self.popup_menu.add_command(label="Undo")
        self.popup_menu.add_separator()
        self.popup_menu.add_command(label="Cut")
        self.popup_menu.add_command(label="Copy")
        self.popup_menu.add_command(label="Paste")
        self.popup_menu.add_command(label="Delete",
                                    command=self.delete_selected)
        self.popup_menu.add_separator()
        self.popup_menu.add_command(label="Select All",
                                    command=self.select_all)
        self.bind("<MouseWheel>", self.popup)
    def popup(self, event):
        try:
            self.popup_menu.tk_popup(event.x_root, event.y_root, 0)
        finally:
            self.popup_menu.grab_release()

    def delete_selected(self):
        print("del_sel")

    def select_all(self):
        print("sel_all")



if __name__ == "__main__":
    root = Tk()
    Entry(root).pack()
    root.mainloop()