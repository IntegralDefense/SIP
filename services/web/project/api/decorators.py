import uuid

from flask import request
from functools import wraps

from project import db
from project.api.errors import error_response
from project.models import User


def api_admin(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        apikey = None
        if 'apikey' in request.values:
            apikey = uuid.UUID(request.values.get('apikey'))

        if apikey:
            user = db.session.query(User).filter_by(apikey=apikey).first()
            if user and any(role.name.lower() == 'admin' for role in user.roles):
                return view_function(*args, **kwargs)
            else:
                return error_response(401, 'Insufficient privileges')
        return error_response(401, 'Bad or missing API key')
    return decorated_function


def api_analyst(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        apikey = None
        if 'apikey' in request.values:
            apikey = uuid.UUID(request.values.get('apikey'))

        if apikey:
            user = db.session.query(User).filter_by(apikey=apikey).first()
            if user and any(role.name.lower() == 'analyst' for role in user.roles):
                return view_function(*args, **kwargs)
            else:
                return error_response(401, 'Insufficient privileges')
        return error_response(401, 'Bad or missing API key')
    return decorated_function
