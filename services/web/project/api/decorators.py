from flask import current_app, request
from functools import wraps

from project import db
from project.api.errors import error_response
from project.models import User


def check_apikey(function):
    """ Checks if the HTTP method exists in the app's config.
    If it does, it uses the value as the user role required to perform the function. """

    @wraps(function)
    def decorated_function(*args, **kwargs):

        # Return an error if the HTTP method is not in the app's config.
        if request.method not in current_app.config:
            return error_response(401, '{} HTTP method not defined in config'.format(request.method))

        # Get the role of the function name in the config.
        required_role = current_app.config[request.method]

        # If the role is None/False/etc, just return the function.
        if not required_role:
            return function(*args, **kwargs)

        # Get the API key if there is one.
        apikey = None
        if 'apikey' in request.values:
            try:
                apikey = request.values.get('apikey')
            except ValueError:
                pass

        # If there is an API key, look it up and get the user's roles.
        if apikey:
            user = db.session.query(User).filter_by(apikey=apikey).first()

            # If the user exists and they have the required role, return the function.
            if user:
                if user.active:
                    if any(role.name.lower() == required_role for role in user.roles):
                        return function(*args, **kwargs)
                    else:
                        return error_response(401, 'Insufficient privileges')
                else:
                    return error_response(401, 'API user is not active')
            else:
                return error_response(401, 'API user does not exist')
        else:
            return error_response(401, 'Bad or missing API key')

    return decorated_function


def verify_admin(function):
    """ Verifies that the calling user has the admin role. """

    @wraps(function)
    def decorated_function(*args, **kwargs):

        # Get the role of the function name in the config.
        required_role = 'admin'

        # Get the API key if there is one.
        apikey = None
        if 'apikey' in request.values:
            try:
                apikey = request.values.get('apikey')
            except ValueError:
                pass

        # If there is an API key, look it up and get the user's roles.
        if apikey:
            user = db.session.query(User).filter_by(apikey=apikey).first()

            # If the user exists and they have the required role, return the function.
            if user:
                if user.active:
                    if any(role.name.lower() == required_role for role in user.roles):
                        return function(*args, **kwargs)
                    else:
                        return error_response(401, 'Insufficient privileges')
                else:
                    return error_response(401, 'API user is not active')
            else:
                return error_response(401, 'API user does not exist')
        else:
            return error_response(401, 'Bad or missing API key')

    return decorated_function
