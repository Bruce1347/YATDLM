def yesnojs(boolean):
    """Returns the JavaScript representation of a boolean value"""
    values = {True: "true", False: "false", None: "null"}

    return values[boolean]


def yesnopython(jsboolean):
    """Returns the Python equivalent of a boolean value"""
    values = {"true": True, "false": False, "null": None}

    return values[jsboolean]
