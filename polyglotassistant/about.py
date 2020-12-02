import tkinter as tk
import tkinter.ttk as ttk
from tkinter.font import Font
from functools import partial


class AboutDialog(tk.Toplevel):
    """"About PolyglotAssistant" Dialog."""

    def __init__(self, master):
        super().__init__(master)

        self.title("About...")
        self.resizable(False, False)
        self.bind("<Unmap>", lambda event: self.deiconify())
        self.transient(master)

        self.create_widgets()

    def create_widgets(self):
        self.__app_icon = tk.PhotoImage(file="images/32x32/app_icon.png")
        self.__app_icon = self.__app_icon.zoom(5)
        tk.Label(self, image=self.__app_icon).pack(padx=10, pady=10)

        for no, text in enumerate(
                      ("PolyglotAssistant 1.0",
                      "\u00a9 Demian Volkov 2019-2020",
                      "Thank you for using this app!"),
                      start=1):
            font = Font(size=20) if no == 1 else Font(size=15)
            tk.Label(self, text=text, font=font).pack()

        buttons_frame = tk.Frame(self)
        ttk.Button(buttons_frame, text="OK", command=self.destroy)\
            .pack(side="left", padx=10)
        ttk.Button(buttons_frame, text="Contact me",
                   command=partial(self.event_generate, "<<contact-me>>"))\
            .pack(side="left")
        buttons_frame.pack(padx=10, pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    AboutDialog(root)
    root.mainloop()