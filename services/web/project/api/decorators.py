import gzip

from flask import current_app, request, after_this_request
from functools import wraps
from jsonschema import validate
from jsonschema.exceptions import SchemaError, ValidationError
from werkzeug.exceptions import BadRequest

from project import db
from project.api.errors import error_response
from project.models import User


def gzipped_response(function):
    """ Returns a gzipped version of the response JSON. """

    @wraps(function)
    def decorated_function(*args, **kwargs):
        @after_this_request
        def zipper(response):
            response.direct_passthrough = False

            if response.status_code < 200 or response.status_code >= 300 or 'Content-Encoding' in response.headers:
                return response

            compressed = gzip.compress(response.data)

            response.data = compressed
            response.headers['Content-Encoding'] = 'gzip'
            response.headers['Content-Length'] = len(response.data)

            return response

        return function(*args, **kwargs)

    return decorated_function


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
        # The header should look like:
        #     Authorization: Apikey blah-blah-blah
        # So strip off the first 7 characters to get the actual key.
        authorization = request.headers.get('Authorization')
        apikey = None
        if authorization and 'apikey' in authorization.lower():
            apikey = authorization[7:]

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
        # The header should look like:
        #     Authorization: Apikey blah-blah-blah
        # So strip off the first 7 characters to get the actual key.
        authorization = request.headers.get('Authorization')
        apikey = None
        if authorization and 'apikey' in authorization.lower():
            apikey = authorization[7:]

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


def validate_json(function):
    """ Verifies that the request contains valid JSON """

    @wraps(function)
    def decorated_function(*args, **kwargs):
        try:
            if not request.get_json():
                return error_response(400, 'Request must include valid JSON')
        except BadRequest:
            return error_response(400, 'Request must include valid JSON')
        return function(*args, **kwargs)

    return decorated_function


def validate_schema(schema):
    """ Verifies that the request JSON conforms to the given schema """

    def decorator(function):

        @wraps(function)
        def decorated_function(*args, **kwargs):
            try:
                validate(request.json, schema)
            except SchemaError as e:
                return error_response(400, 'JSON schema is not valid: {}'.format(e.message))
            except ValidationError as e:
                return error_response(400, 'Request JSON does not match schema: {}'.format(e.message))
            return function(*args, **kwargs)
        return decorated_function

    return decorator
