def get_apikey(request):
    # Get the API key if there is one.
    # The header should look like:
    #     Authorization: Apikey blah-blah-blah
    # So strip off the first 7 characters to get the actual key.
    authorization = request.headers.get('Authorization')
    if authorization and 'apikey' in authorization.lower():
        apikey = authorization[7:]

        # Look up the user by their API key.
        if apikey:
            return apikey

    return None


def parse_boolean(string, default=False):
    string = str(string).lower()

    true = ['1', 'true', 'y', 'yes', 'yep']
    false = ['0', 'false', 'n', 'no', 'nope']

    if string in true:
        return True

    if string in false:
        return False

    return default
