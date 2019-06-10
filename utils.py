#!/usr/bin/python3
import webbrowser


def yesno2bool(result):
    return True if result == "yes" else False


def contact_me():
    webbrowser.open("mailto:demianwolfssd@gmail.com")


def validate_lwp_data(data):
    assert isinstance(data, list)
    for pair in data:
        assert isinstance(pair, list)
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
                    assert isinstance(pair, list)
                    assert len(pair) == 2
                    for elem in pair:
                        assert isinstance(elem, str)
