from tkinter import *
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import showerror, showinfo
from io import BytesIO
import webbrowser
import pickle
import os

import pygame.mixer
import requests
import googletrans
import gtts


exec("from lang.%s import *" % "ua")

pygame.mixer.init()

def play_sound(what):
    """
    Plays the given sound file object or filename.
    
    param what: file object or filename
    type what: string or file object
    """
    
    pygame.mixer.music.load(what)
    pygame.mixer.music.play()

def yesno2bool(result):
    """
    Returns True if the result equals "yes" and False otherwise (useful for the messageboxes).

    :param result: user's answer that is returned by "yesno" messagebox
    :type result: str
    :return: a bool interpretation of the user's answer
    :rtype: bool
    """

    return True if result == "yes" else False


def retrycancel2bool(result):
    """
    Returns True if the result equals "retry" and False otherwise (useful for the messageboxes).

    :param result: user's answer that is returned by "yesno" messagebox
    :type result: str
    :return: a bool interpretation of the user's answer
    :rtype: bool
    """

    return True if result == "retry" else False


def help_(_event=None):
    """
    Calls the "Help" Dialog.

    :param _event: unused Tkinter event
    :type _event: tkinter.Event
    :return: no value
    :rtype: none
    """

    showinfo("Інформація", "Див. manual.pdf")


def about(_event=None):
    """
    Calls the "About" Dialog

    :param _event: unused Tkinter event
    :type _event: tkinter.Event
    :return: no value
    :rtype: none
    """

    showinfo("Про PolyglotAssistant",
             "PolyglotAssistant 1.00\n"
             "(C) Дем'ян Волков aka Demian Wolf, 2019-2020"
             "\nPolyglotAssistant - легкий спосіб швидко поповнити свій словниковий запас з іноземної мови!"
             "\nДякую за використання моєї програми!")


def contact_me(_event=None):
    """
    Opens the standard mail program to write an e-mail to the author.

    :param _event: unused Tkinter event
    :type _event: tkinter.Event
    :return: no value
    :rtype: none
    """

    webbrowser.open("mailto:demianwolfssd@gmail.com")


def validate_vocabulary_data(data):
    """
    Validates the vocabulary's data.

    :param data: vocabulary's data
    :type data: list
    :raise AssertionError: if the data is invalid
    :return: no value
    :rtype: none
    """
    assert isinstance(data, list)  # the data must be a list
    for pair in data:  # and every pair in it must be
        assert isinstance(pair, tuple)  # a tuple
        assert len(pair) == 2  # with length 2
        for elem in pair:  # and every of the two elements of this tuple
            assert isinstance(elem, str)  # must be strings


def validate_users_dict(data):
    """
    Validates users' dict.

    :param data: users' dict data
    :type data: dict
    :raise AssertionError: if the user's dict is invalid
    :return: no value
    :rtype: none
    """
    
    assert isinstance(data, dict)  # it must be a dictionary, at first
    for user in data:  # and every user in it
        assert sorted(data[user]) == ["password", "stats"]  # must have password and stats
        assert isinstance(data[user]["stats"], dict)  # stats must be a dict
        for file in data[user]["stats"]:  # and every file in user's stats
            assert sorted(data[user]["stats"][file].keys()) == ["bad",
                                                                "good"]  # must have two lists - for good and bad words
            for type_ in data[user]["stats"][file]:  # and every words' type (good/bad)
                for pair in data[user]["stats"][file][type_]:  # must have pairs that
                    assert isinstance(pair, tuple)  # are tuples
                    assert len(pair) == 2  # with length 2
                    for elem in pair:  # and every element of that tuple (word and its translation)
                        assert isinstance(elem, str)  # must be a string


def reverse_pairs(data):
    """
    Reverses pairs (that is needed in Gym when the word-translation are replaced).

    :param data: the list of the words
    :type data: list
    :return: a list, where the every pair is reversed now
    :rtype: list
    """
    
    return [tuple(reversed(pair)) for pair in data]  # every pair is reversed now


def tidy_stats(result, vocabulary_content):
    """
    Tidies the results (reverses pairs, that are reversed in learning plan).

    :param result: the result after the Gym
    :param vocabulary_content: the contents of the vocabulary
    :type result: set
    :type vocabulary_content: list(tuple, tuple, tuple...)
    :return: tidied result
    :rtype: set
    """
    
    new_result = set()
    for elem in result:
        if elem in vocabulary_content:
            new_result.add(elem)
        else:
            new_result.add(tuple(reversed(elem)))
    return new_result

def set_window_icon(window):
    """
    Sets the icon on the window's titlebar.
    
    :param window: the Tkinter window, where it is necessary to set the titlebar icon
    :type window: tkinter.Tk or tkinter.Toplevel object
    """
    
    window.iconphoto(True, PhotoImage(master=window, file="images/32x32/app_icon.png"))

def open_vocabulary(vocabulary_filename=None):
    """
    Opens the vocabulary.
    :param vocabulary_filename: the filename of the vocabulary
    :type vocabulary_filename: str
    :return: no value
    :rtype: none
    """
    
    if vocabulary_filename:  # if a vocabulary filename was specified to this function
        try:
            vocabulary_file = open(vocabulary_filename, "rb")  # open the vocabulary file
            if vocabulary_file:
                vocabulary_data = pickle.load(vocabulary_file)  # read the vocabulary
                validate_vocabulary_data(vocabulary_data)  # check its format
                return (vocabulary_file.name, vocabulary_data)
        except FileNotFoundError as details:  # if submitted file disappeared suddenly
            showerror(LANG["error"],
                      LANG["error_notfound_opening_file"] + (
                          LANG["error_details"] % (details.__class__.__name__, details)))
        except PermissionError as details:  # if the access to the file denied
            showerror(LANG["error"],
                      LANG["error_permissions_opening_file"] + (
                          LANG["error_details"] % (details.__class__.__name__, details)))
        except pickle.UnpicklingError as details:  # if the file is damaged, or its format is unsupported
                        showerror(LANG["error"],
                                  LANG["error_invalid_opening_file"] + (
                                      LANG["error_details"] % (details.__class__.__name__, details)))
        except AssertionError:  # if it is invalid,
            showerror(LANG["error"], LANG["error_invalid_obj_opening_file"])
        except Exception as details:  # if any other problem happened
            showerror(LANG["error"],
                      LANG["error_unexpected_opening_file"] + (
                          LANG["error_details"] % (details.__class__.__name__, details)))

    else:  # if nothing was specified
        return open_vocabulary(askopenfilename(filetypes=[(LANG["pav_vocabulary_filetype"], "*.pav")]))

def save_vocabulary(self, vocabulary_filename=None):
    """
    Saves the vocabulary.
    :param vocabulary_filename: the filename of the vocabulary
    :type vocabulary_filename: str
    :return: no value
    :rtype: none
    """

    if vocabulary_filename:
        try:
            outfile = open(filename, "wb")  # try to open a file to write
            pickle.dump([tuple(map(str, self.wtree.item(child)["values"])) for child in self.wtree.get_children()],
                        outfile)  # get the vocabulary content and dump it to selected file
            outfile.close()  # now we can close the outfile
            self.filename = os.path.abspath(outfile.name)  # update the opened file's filename, if changed
            self.set_saved(True)  # set state to saved
        except PermissionError as details:  # if there is a problem with access permissions,
            showerror(LANG["error"],
                          LANG["error_permissions_opening_file"] + (
                              LANG["error_details"] % (details.__class__.__name__, details)))
        except Exception as details:  # if there is an unexpected problem occurred,
            showerror(LANG["error"], LANG["error_unexpected_saving_file"] + (
                              LANG["error_details"] % (details.__class__.__name__, details)))
    else:
        save_vocabulary(asksaveasfilename(filetypes=[(LANG["pav_vocabulary_fileetype"], "*pav")]))

def show_usage(app):
    """
    Shows the command-line usage, if called.

    :return: no value
    :rtype: none
    """
    Tk().withdraw()  # create and hide a Tk() window (to avoid the blank window appearance on the screen)
    showerror(LANG["error"], LANG["error_clargs_%s" % app])  # show the command-line usage
    os._exit(0)


def speak(text, lang):
    if text.strip():
        try:
            tmp_file = BytesIO()
            gtts.gTTS(text=text, lang=lang).write_to_fp(tmp_file)
            tmp_file.seek(0)
            play_sound(tmp_file)
        except ValueError as details:
            showerror(LANG["error"],
                      LANG["error_speak_language_not_supported"] % googletrans.LANGUAGES[str(details).split(": ")[-1]].capitalize())
        except requests.exceptions.ConnectionError as details:
            showerror(LANG["error"],
                      LANG["error_translate_internet_connection_problems"] + LANG["error_details"] % (
                      details.__class__, details))
        except Exception as details:
            showerror(LANG["error"], LANG["error_translate_unexpected"] + LANG["error_details"] % (details.__class__.__name__, details))