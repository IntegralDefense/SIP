from flask import current_app, jsonify, request, url_for
from flask_security import SQLAlchemyUserDatastore
from flask_security.utils import hash_password
from sqlalchemy import exc

from project import db
from project.api import bp
from project.api.decorators import admin_required, check_if_token_required, validate_json, validate_schema
from project.api.errors import error_response
from project.models import Role, User


"""
CREATE
"""

create_schema = {
    'type': 'object',
    'properties': {
        'email': {'type': 'string', 'minLength': 1, 'maxLength': 255},
        'first_name': {'type': 'string', 'minLength': 1, 'maxLength': 50},
        'last_name': {'type': 'string', 'minLength': 1, 'maxLength': 50},
        'password': {'type': 'string', 'minLength': 1},
        'roles': {
            'type': 'array',
            'items': {'type': 'string', 'minLength': 1, 'maxLength': 80},
            'minItems': 1
        },
        'username': {'type': 'string', 'minLength': 1, 'maxLength': 255}
    },
    'required': ['email', 'first_name', 'last_name', 'password', 'roles', 'username'],
    'additionalProperties': False
}


@bp.route('/users', methods=['POST'])
@admin_required
@validate_json
@validate_schema(create_schema)
def create_user():
    """ Creates a new user. Requires the admin role. """

    data = request.get_json()

    # Verify this email does not already exist.
    existing = User.query.filter_by(email=data['email']).first()
    if existing:
        return error_response(409, 'User email already exists')

    # Verify this username does not already exist.
    existing = User.query.filter_by(username=data['username']).first()
    if existing:
        return error_response(409, 'User username already exists')

    # Verify the password length.
    minimum_password_length = current_app.config['MINIMUM_PASSWORD_LENGTH']
    if len(data['password']) < minimum_password_length:
        return error_response(400, 'Password must be at least {} characters'.format(minimum_password_length))

    # Verify any roles that were specified.
    valid_roles = []
    for role in data['roles']:

        # Verify each role is actually valid.
        r = Role.query.filter_by(name=role).first()
        if not r:
            return error_response(404, 'User role not found: {}'.format(role))
        valid_roles.append(r)

    # Create the user in the user datastore.
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    user_datastore.create_user(email=data['email'],
                               first_name=data['first_name'],
                               last_name=data['last_name'],
                               password=hash_password(data['password']),
                               username=data['username'])

    # Get the user from the database.
    user = User.query.filter_by(username=data['username']).first()
    if not user:
        return error_response(500, 'Unable to add user to datastore')

    # Add the roles to the user.
    for role in valid_roles:
        user.roles.append(role)

    # Save the user.
    db.session.add(user)
    db.session.commit()

    response = jsonify(user.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.read_user', user_id=user.id)
    return response


"""
READ
"""


@bp.route('/users/<int:user_id>', methods=['GET'])
@check_if_token_required
def read_user(user_id):
    """ Gets a single user given its ID. """

    user = User.query.get(user_id)
    if not user:
        return error_response(404, 'User ID not found')

    return jsonify(user.to_dict())


@bp.route('/users', methods=['GET'])
@check_if_token_required
def read_users():
    """ Gets a list of all the users. """

    data = User.query.all()
    return jsonify([item.to_dict() for item in data])


"""
UPDATE
"""

update_schema = {
    'type': 'object',
    'properties': {
        'active': {'type': 'boolean'},
        'email': {'type': 'string', 'minLength': 1, 'maxLength': 255},
        'first_name': {'type': 'string', 'minLength': 1, 'maxLength': 50},
        'last_name': {'type': 'string', 'minLength': 1, 'maxLength': 50},
        'password': {'type': 'string', 'minLength': 1},
        'roles': {
            'type': 'array',
            'items': {'type': 'string', 'minLength': 1, 'maxLength': 80},
            'minItems': 1
        },
        'username': {'type': 'string', 'minLength': 1, 'maxLength': 255}
    },
    'additionalProperties': False
}


@bp.route('/users/<int:user_id>', methods=['PUT'])
@admin_required
@validate_json
@validate_schema(update_schema)
def update_user(user_id):
    """ Updates an existing user. Requires the admin role. """

    data = request.get_json()

    # Verify the ID exists.
    user = User.query.get(user_id)
    if not user:
        return error_response(404, 'User ID not found')

    # Verify active if it was specified. Defaults to False.
    if 'active' in data:
        user.active = data['active']

    # Verify email if one was specified.
    if 'email' in data:

        # Verify this email does not already exist.
        existing = User.query.filter_by(email=data['email']).first()
        if existing:
            return error_response(409, 'User email already exists')
        else:
            user.email = data['email']

    # Verify first_name if one was specified.
    if 'first_name' in data:
        user.first_name = data['first_name']

    # Verify last_name if one was specified.
    if 'last_name' in data:
        user.last_name = data['last_name']

    # Verify password if one was specified.
    if 'password' in data:

        # Verify the password length.
        minimum_password_length = current_app.config['MINIMUM_PASSWORD_LENGTH']
        if len(data['password']) < minimum_password_length:
            return error_response(400, 'Password must be at least {} characters'.format(minimum_password_length))

        user.password = hash_password(data['password'])

    # Verify roles if any were specified.
    if 'roles' in data:
        valid_roles = []
        for role in data['roles']:

            # Verify each role is actually valid.
            r = Role.query.filter_by(name=role).first()
            if not r:
                return error_response(404, 'User role not found: {}'.format(role))
            valid_roles.append(r)
        if valid_roles:
            user.roles = valid_roles

    # Verify username if one was specified.
    if 'username' in data:

        # Verify this username does not already exist.
        existing = User.query.filter_by(username=data['username']).first()
        if existing:
            return error_response(409, 'User username already exists')
        else:
            user.username = data['username']

    db.session.commit()

    response = jsonify(user.to_dict())
    return response


"""
DELETE
"""


@bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """ Deletes a user. Requires the admin role. """

    user = User.query.get(user_id)
    if not user:
        return error_response(404, 'User ID not found')

    try:
        db.session.delete(user)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        return error_response(409, 'Unable to delete user due to foreign key constraints')

    return '', 204
