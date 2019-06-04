#!/usr/bin/python3
import webbrowser


def yesno2bool(result):
    return True if result == "yes" else False

def contact_me():
    webbrowser.open("mailto:demianwolfssd@gmail.com")
