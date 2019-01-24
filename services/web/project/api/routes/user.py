import uuid

from flask import jsonify, request, url_for
from flask_security import SQLAlchemyUserDatastore
from flask_security.utils import hash_password
from sqlalchemy import exc

from project import db
from project.api import bp
from project.api.decorators import check_apikey, verify_admin
from project.api.errors import error_response
from project.api.helpers import parse_boolean
from project.models import Role, User

"""
CREATE
"""


@bp.route('/users', methods=['POST'])
@verify_admin
def create_user():
    """ Creates a new user. Requires the admin role. """

    data = request.values or {}

    # Verify the required fields are present.
    if 'email' not in data or 'first_name' not in data or 'last_name' not in data or 'password' not in data \
            or 'roles' not in data or 'username' not in data:
        return error_response(400, 'Request must include: email, first_name, last_name, password, roles, username')

    # Verify this email does not already exist.
    existing = User.query.filter_by(email=data['email']).first()
    if existing:
        return error_response(409, 'User email already exists')

    # Verify this username does not already exist.
    existing = User.query.filter_by(username=data['username']).first()
    if existing:
        return error_response(409, 'User username already exists')

    # Verify any roles that were specified.
    roles = data.getlist('roles')
    if not roles:
        return error_response(400, 'At least one role must be specified')
    valid_roles = []
    for role in roles:

        # Verify each role is actually valid.
        r = Role.query.filter_by(name=role).first()
        if not r:
            results = Role.query.all()
            acceptable = sorted([r.name for r in results])
            return error_response(400, 'Valid roles: {}'.format(', '.join(acceptable)))
        valid_roles.append(r)

    # Create the user in the user datastore.
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    user_datastore.create_user(email=data['email'], password=hash_password(data['password']), username=data['username'],
                               first_name=data['first_name'], last_name=data['last_name'])

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

    # Add the user's API key to the response.
    user_dict = user.to_dict()
    user_dict['apikey'] = user.apikey
    response = jsonify(user_dict)
    response.status_code = 201
    response.headers['Location'] = url_for('api.read_user', user_id=user.id)
    return response


"""
READ
"""


@bp.route('/users/<int:user_id>', methods=['GET'])
@check_apikey
def read_user(user_id):
    """ Gets a single user given its ID. """

    user = User.query.get(user_id)
    if not user:
        return error_response(404, 'User ID not found')

    return jsonify(user.to_dict())


@bp.route('/users', methods=['GET'])
@check_apikey
def read_users():
    """ Gets a list of all the users. """

    data = User.query.all()
    return jsonify([item.to_dict() for item in data])


"""
UPDATE
"""


@bp.route('/users/<int:user_id>', methods=['PUT'])
@verify_admin
def update_user(user_id):
    """ Updates an existing user. Requires the admin role. """

    data = request.values or {}

    # Verify the ID exists.
    user = User.query.get(user_id)
    if not user:
        return error_response(404, 'User ID not found')

    # Verify at least one required field was specified.
    required = ['active', 'apikey_refresh', 'email', 'first_name', 'last_name', 'password', 'roles', 'username']
    if not any(r in data for r in required):
        return error_response(400, 'Request must include at least one of: {}'.format(', '.join(sorted(required))))

    # Verify active if it was specified. Defaults to False.
    if 'active' in data:
        user.active = parse_boolean(data['active'], default=False)

    # Verify apikey if it was specified. Defaults to True.
    if 'apikey_refresh' in data:
        if parse_boolean(data['apikey_refresh'], default=True):
            user.apikey = str(uuid.uuid4())

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
        user.password = hash_password(data['password'])

    # Verify roles if any were specified.
    roles = data.getlist('roles')
    valid_roles = []
    for role in roles:

        # Verify each role is actually valid.
        r = Role.query.filter_by(name=role).first()
        if not r:
            results = Role.query.all()
            acceptable = sorted([r.name for r in results])
            return error_response(400, 'Valid roles: {}'.format(', '.join(acceptable)))
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

    # Add the user's API key to the response.
    user_dict = user.to_dict()
    user_dict['apikey'] = user.apikey
    response = jsonify(user_dict)
    return response


"""
DELETE
"""


@bp.route('/users/<int:user_id>', methods=['DELETE'])
@verify_admin
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
