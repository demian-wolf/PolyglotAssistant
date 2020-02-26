from tkinter import *
import itertools


# TODO: check bindings
# TODO: make user able to specify func to remove binding

class HKManager:
    def __init__(self, master):
        self.master = master
        self.master.bind("<Key>", lambda event, mods=(): self.process_binding(event, mods=mods))
        for comb_quantity in range(1, 4):
            for mods_group in itertools.combinations(("Alt", "Control", "Shift"), comb_quantity):
                self.master.bind("".join(("<", "-".join(sorted(mods_group)), "-Key>")), lambda event, mods=sorted(mods_group): self.process_binding(event, mods=mods))
        
        self.bindings = {}

    def add_binding(self, binding, function):
        binding = "".join(("<", "-".join(sorted(binding[1:-1].split("-")[:-1])), "-", binding[-2], ">"))
        if binding in self.bindings:
            self.bindings[binding].append(function)
        else:
            self.bindings[binding] = [function]
            
    def remove_binding(self, binding, function=None):
        if binding in self.bindings:
            if function:
                if function in self.bindings[binding]:
                    while function in self.bindings[binding]:
                        self.bindings[binding].remove(function)
                else:
                    raise ValueError("the function is not bound to the specified binding")
            else:
                del self.bindings[binding]
        else:
            raise ValueError("the binding was not found")

    def process_binding(self, event, mods):
        # TODO: work in the right way when <Control-o> pressed instead of <Control-O> etc.
        binding = "".join(("<", "-".join(mods), "-%s>" % chr(event.keycode))) if mods else "<%s>" % chr(event.keycode)
        if binding in self.bindings:
            for function in self.bindings[binding]:
                function()

if __name__ == "__main__":
    root = Tk()
    hk_man = HKManager(root)
    hk_man.add_binding("<Control-Shift-S>", lambda: print("Ctrl-Shift-S pressed"))
    hk_man.add_binding("<Alt-S>", lambda: print("Alt-S pressed"))
    root.mainloop()
