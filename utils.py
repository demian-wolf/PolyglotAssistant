#!/usr/bin/python3
from tkinter.messagebox import showinfo
import webbrowser


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

    pass


def about(_event=None):
    """
    Calls the "About" Dialog

    :param _event: unused Tkinter event
    :type _event: tkinter.Event
    :return: no value
    :rtype: none
    """

    showinfo("About PolyglotAssistant",
             "PolyglotAssistant 1.0 (C) Demian Wolf, 2019"
             "\nLearnWords is an easy way to learn words of foreign language - "
             "convenient learning plan editor and smart autotrainer."
             "\nProgram licensed AS-IS\nThank you for using my program!")


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
