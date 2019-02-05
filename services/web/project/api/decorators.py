from flask import current_app, request
from flask_jwt_extended import verify_jwt_in_request, verify_fresh_jwt_in_request, get_jwt_claims
from functools import wraps
from jsonschema import validate
from jsonschema.exceptions import SchemaError, ValidationError
from werkzeug.exceptions import BadRequest

from project.api.errors import error_response


def check_if_token_required(function):
    """ If the called HTTP method exists in the config file, it uses the value as the
    user role required of the JWT token to perform the function. """

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

        # Verify the JWT exists and that it has the required role.
        verify_jwt_in_request()
        claims = get_jwt_claims()
        if required_role in claims['roles']:
            return function(*args, **kwargs)
        else:
            return error_response(401, '{} role required'.format(required_role))

    return decorated_function


def admin_required(function):
    """ Verifies the JWT is present and that the user has the admin role """

    @wraps(function)
    def decorated_function(*args, **kwargs):

        # Verify the (fresh) JWT token exists and that it has the admin role.
        verify_fresh_jwt_in_request()
        claims = get_jwt_claims()
        if 'admin' in claims['roles']:
            return function(*args, **kwargs)
        else:
            return error_response(401, 'admin role required')

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
