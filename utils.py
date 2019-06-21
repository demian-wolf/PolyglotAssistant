#!/usr/bin/python3
from tkinter.messagebox import showinfo
import webbrowser


def yesno2bool(result):
    return True if result == "yes" else False


def help_(_event=None):
    pass

def about(_event=None):
    showinfo("About LearnWords",
             "LearnWords 1.0 (C) Demian Wolf, 2019\nLearnWords is an easy way to learn words of foreign language - convenient learning plan editor and smart autotrainer.\nProgram licensed AS-IS\nThank you for using my program!")


def contact_me(_event=None):
    webbrowser.open("mailto:demianwolfssd@gmail.com")


def validate_lwp_data(data):
    assert isinstance(data, list)
    for pair in data:
        assert isinstance(pair, tuple)
        assert len(pair) == 2
        for elem in pair:
            assert isinstance(elem, str)


def validate_users_dict(data):
    assert isinstance(data, dict)
    for user in data:
        assert sorted(data[user]) == ["password", "stats"]
        assert isinstance(data[user]["stats"], dict)
        for file in data[user]["stats"]:
            assert sorted(data[user]["stats"][file].keys()) == ["bad", "good", "unknown"]
            for type_ in data[user]["stats"][file]:
                for pair in data[user]["stats"][file][type_]:
                    assert isinstance(pair, tuple)
                    assert len(pair) == 2
                    for elem in pair:
                        assert isinstance(elem, str)


def reverse_pairs(data):
    return [tuple(reversed(pair)) for pair in data]

def count(pair, data):
    pass