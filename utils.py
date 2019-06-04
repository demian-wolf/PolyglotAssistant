#!/usr/bin/python3
import webbrowser


def yesno2bool(result):
    return True if result == "yes" else False

def contact_me():
    webbrowser.open("mailto:demianwolfssd@gmail.com")

def validate_lwp_data(data):
    if isinstance(data, list):
        for pair in data:
            if isinstance(pair, list):
                if len(pair) == 2:
                    for i in pair:
                        if isinstance(i, str):
                            return True
    return False