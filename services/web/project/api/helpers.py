

def parse_boolean(string, default=False):
    string = str(string).lower()

    true = ['1', 'true', 'y', 'yes', 'yep']
    false = ['0', 'false', 'n', 'no', 'nope']

    if string in true:
        return True

    if string in false:
        return False

    return default
