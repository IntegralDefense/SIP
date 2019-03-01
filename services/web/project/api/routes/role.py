from flask import jsonify, request, url_for
from sqlalchemy import exc

from project import db
from project.api import bp
from project.api.decorators import admin_required, check_if_token_required, validate_json, validate_schema
from project.api.errors import error_response
from project.api.schemas import role_create, role_update
from project.models import Role

"""
CREATE
"""


@bp.route('/roles', methods=['POST'])
@admin_required
@validate_json
@validate_schema(role_create)
def create_role():
    """ Creates a new role. Requires the admin role.

    .. :quickref: Role; Creates a new role. Requires the admin role.

    **Example request**:

    .. sourcecode:: http

      POST /roles HTTP/1.1
      Host: 127.0.0.1
      Content-Type: application/json

      {
        "name": "analyst",
        "description": "Users that create and process intel"
      }

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 201 Created
      Content-Type: application/json

      {
        "id": 1,
        "name": "analyst",
        "description": "Users that create and process intel"
      }

    :reqheader Authorization: Optional JWT Bearer token
    :resheader Content-Type: application/json
    :status 201: Role created
    :status 400: JSON does not match the schema
    :status 401: Invalid role to perform this action
    :status 409: Role already exists
    """

    data = request.get_json()

    # Verify this name does not already exist.
    existing = Role.query.filter_by(name=data['name']).first()
    if existing:
        return error_response(409, 'Role already exists')

    # Create and add the new value.
    role = Role(name=data['name'])

    # Add the description if one was given.
    if 'description' in data:
        role.description = data['description']

    db.session.add(role)
    db.session.commit()

    response = jsonify(role.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.read_role', role_id=role.id)
    return response


"""
READ
"""


@bp.route('/roles/<int:role_id>', methods=['GET'])
@check_if_token_required
def read_role(role_id):
    """ Gets a single role given its ID.

    .. :quickref: Role; Gets a single role given its ID.

    **Example request**:

    .. sourcecode:: http

      GET /roles/1 HTTP/1.1
      Host: 127.0.0.1
      Accept: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "id": 1,
        "name": "analyst",
        "description": "Users that create and process intel"
      }

    :reqheader Authorization: Optional JWT Bearer token
    :resheader Content-Type: application/json
    :status 200: Role found
    :status 401: Invalid role to perform this action
    :status 404: Role ID not found
    """

    role = Role.query.get(role_id)
    if not role:
        return error_response(404, 'Role ID not found')

    return jsonify(role.to_dict())


@bp.route('/roles', methods=['GET'])
@check_if_token_required
def read_roles():
    """ Gets a list of all the roles.

    .. :quickref: Role; Gets a list of all the roles.

    **Example request**:

    .. sourcecode:: http

      GET /roles HTTP/1.1
      Host: 127.0.0.1
      Accept: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      [
        {
          "id": 1,
          "name": "analyst",
          "description": "Users that create and process intel"
        },
        {
          "id": 2,
          "name": "readonly",
          "description": "Users that can only read the database"
        }
      ]

    :reqheader Authorization: Optional JWT Bearer token
    :resheader Content-Type: application/json
    :status 200: Roles found
    :status 401: Invalid role to perform this action
    """

    data = Role.query.all()
    return jsonify([item.to_dict() for item in data])


"""
UPDATE
"""


@bp.route('/roles/<int:role_id>', methods=['PUT'])
@admin_required
@validate_json
@validate_schema(role_update)
def update_role(role_id):
    """ Updates an existing role. Requires the admin role.

    .. :quickref: Role; Updates an existing role. Requires the admin role.

    **Example request**:

    .. sourcecode:: http

      PUT /roles/1 HTTP/1.1
      Host: 127.0.0.1
      Content-Type: application/json

      {
        "name": "intelusers"
      }

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "id": 1,
        "name": "intelusers",
        "description": "Users that create and process intel"
      }

    :reqheader Authorization: Optional JWT Bearer token
    :resheader Content-Type: application/json
    :status 200: Role updated
    :status 400: JSON does not match the schema
    :status 401: Invalid role to perform this action
    :status 404: Role ID not found
    :status 409: Role already exists
    """

    data = request.get_json()

    # Verify the ID exists.
    role = Role.query.get(role_id)
    if not role:
        return error_response(404, 'Role ID not found')

    # Verify name if one was specified.
    if 'name' in data:

        # Verify this name does not already exist.
        existing = Role.query.filter_by(name=data['name']).first()
        if existing:
            return error_response(409, 'Role already exists')
        else:
            role.name = data['name']

    # Verify description if one was specified.
    if 'description' in data:
        role.description = data['description']

    db.session.commit()
    response = jsonify(role.to_dict())
    return response


"""
DELETE
"""


@bp.route('/roles/<int:role_id>', methods=['DELETE'])
@admin_required
def delete_role(role_id):
    """ Deletes a role. Requires the admin role.

    .. :quickref: Role; Deletes a role. Requires the admin role.

    **Example request**:

    .. sourcecode:: http

      DELETE /roles/1 HTTP/1.1
      Host: 127.0.0.1

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 204 No Content

    :reqheader Authorization: Optional JWT Bearer token
    :status 204: Role deleted
    :status 401: Invalid role to perform this action
    :status 404: Role ID not found
    :status 409: Unable to delete role due to foreign key constraints
    """

    role = Role.query.get(role_id)
    if not role:
        return error_response(404, 'Role ID not found')

    try:
        db.session.delete(role)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        return error_response(409, 'Unable to delete role due to foreign key constraints')

    return '', 204
