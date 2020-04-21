from tkinter import *
from threading import Thread
import time


def func():
    my_button["command"] = root.bell
    my_button["text"] = "Thread is running, but you can press this button"
    while True:
        for i in range(10):
            time.sleep(1)
            print(i)

root = Tk()
my_thread = Thread(target=func)
my_button = Button(root, text="Start", command=my_thread.start)
my_button.pack()
root.mainloop()
