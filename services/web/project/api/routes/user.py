from flask import current_app, jsonify, request, url_for
from flask_security import SQLAlchemyUserDatastore
from flask_security.utils import hash_password
from sqlalchemy import exc

from project import db
from project.api import bp
from project.api.decorators import check_apikey, validate_json, validate_schema, verify_admin
from project.api.errors import error_response
from project.api.schemas import user_create, user_update
from project.models import Role, User


"""
CREATE
"""


@bp.route('/users', methods=['POST'])
@verify_admin
@validate_json
@validate_schema(user_create)
def create_user():
    """ Creates a new user. Requires the admin role.

    .. :quickref: User; Creates a new user. Requires the admin role.

    **Example request**:

    .. sourcecode:: http

      POST /users HTTP/1.1
      Host: 127.0.0.1
      Content-Type: application/json

      {
        "email": "johndoe@company.com",
        "first_name": "John",
        "last_name": "Doe",
        "password": "asdfasdfasdf",
        "roles": ["analyst"],
        "username": "johndoe"
      }

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 201 Created
      Content-Type: application/json

      {
        "active": true,
        "apikey": "11111111-1111-1111-1111-111111111111",
        "email": "johndoe@company.com",
        "first_name": "John",
        "id": 2,
        "last_name": "Doe",
        "roles": ["analyst"],
        "username": "johndoe"
      }

    :reqheader Authorization: Optional Apikey value
    :resheader Content-Type: application/json
    :status 201: User created
    :status 400: Password does not meet length requirement
    :status 400: JSON does not match the schema
    :status 401: Invalid role to perform this action
    :status 404: Role not found
    :status 409: Email address already exists
    :status 409: Username already exists
    :status 500: Unable to add user to datastore
    """

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
    """ Gets a single user given its ID.

    .. :quickref: User; Gets a single user given its ID.

    **Example request**:

    .. sourcecode:: http

      GET /users/2 HTTP/1.1
      Host: 127.0.0.1
      Accept: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "active": true,
        "email": "johndoe@company.com",
        "first_name": "John",
        "id": 2,
        "last_name": "Doe",
        "roles": ["analyst"],
        "username": "johndoe"
      }

    :reqheader Authorization: Optional Apikey value
    :resheader Content-Type: application/json
    :status 200: User found
    :status 401: Invalid role to perform this action
    :status 404: User ID not found
    """

    user = User.query.get(user_id)
    if not user:
        return error_response(404, 'User ID not found')

    return jsonify(user.to_dict())


@bp.route('/users', methods=['GET'])
@check_apikey
def read_users():
    """ Gets a list of all the users.

    .. :quickref: User; Gets a list of all the users.

    **Example request**:

    .. sourcecode:: http

      GET /users HTTP/1.1
      Host: 127.0.0.1
      Accept: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      [
        {
          "active": true,
          "email": "admin@localhost",
          "first_name": "Admin",
          "id": 1,
          "last_name": "Admin",
          "roles": ["admin", "analyst"],
          "username": "admin"
        },
        {
          "active": true,
          "email": "johndoe@company.com",
          "first_name": "John",
          "id": 2,
          "last_name": "Doe",
          "roles": ["analyst"],
          "username": "johndoe"
        }
      ]

    :reqheader Authorization: Optional Apikey value
    :resheader Content-Type: application/json
    :status 200: Users found
    :status 401: Invalid role to perform this action
    """

    data = User.query.all()
    return jsonify([item.to_dict() for item in data])


"""
UPDATE
"""


@bp.route('/users/<int:user_id>', methods=['PUT'])
@verify_admin
@validate_json
@validate_schema(user_update)
def update_user(user_id):
    """ Updates an existing user. Requires the admin role.

    .. :quickref: User; Updates an existing user. Requires the admin role.

    **Example request**:

    .. sourcecode:: http

      PUT /users/2 HTTP/1.1
      Host: 127.0.0.1
      Content-Type: application/json

      {
        "active": false
      }

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "active": false,
        "email": "johndoe@company.com",
        "first_name": "John",
        "id": 2,
        "last_name": "Doe",
        "roles": ["analyst"],
        "username": "johndoe"
      }

    :reqheader Authorization: Optional Apikey value
    :resheader Content-Type: application/json
    :status 200: User updated
    :status 400: Password does not meet length requirement
    :status 400: JSON does not match the schema
    :status 401: Invalid role to perform this action
    :status 404: Role not found
    :status 404: User ID not found
    :status 409: Email address already exists
    :status 409: Username already exists
    """

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
@verify_admin
def delete_user(user_id):
    """ Deletes a user. Requires the admin role.

    .. :quickref: User; Deletes a user. Requires the admin role.

    **Example request**:

    .. sourcecode:: http

      DELETE /users/2 HTTP/1.1
      Host: 127.0.0.1

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 204 No Content

    :reqheader Authorization: Optional Apikey value
    :status 204: User deleted
    :status 401: Invalid role to perform this action
    :status 404: User ID not found
    :status 409: Unable to delete user due to foreign key constraints
    """

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
