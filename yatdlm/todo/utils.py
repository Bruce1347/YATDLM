
def yesnojs(boolean):
    """Returns the JavaScript representation of a boolean value"""
    values = {
        True: 'true',
        False: 'false',
        None: 'null'
    }

    return values[boolean]