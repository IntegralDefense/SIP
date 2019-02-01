from flask import jsonify, request, url_for
from sqlalchemy import exc

from project import db
from project.api import bp
from project.api.decorators import check_apikey, verify_admin
from project.api.errors import error_response
from project.models import Role

"""
CREATE
"""


@bp.route('/roles', methods=['POST'])
@verify_admin
def create_role():
    """ Creates a new role. Requires the admin role. """

    data = request.values or {}

    # Verify the required fields (name) are present.
    if 'name' not in data:
        return error_response(400, 'Request must include: name')

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
@check_apikey
def read_role(role_id):
    """ Gets a single role given its ID. """

    role = Role.query.get(role_id)
    if not role:
        return error_response(404, 'Role ID not found')

    return jsonify(role.to_dict())


@bp.route('/roles', methods=['GET'])
@check_apikey
def read_roles():
    """ Gets a list of all the roles. """

    data = Role.query.all()
    return jsonify([item.to_dict() for item in data])


"""
UPDATE
"""


@bp.route('/roles/<int:role_id>', methods=['PUT'])
@verify_admin
def update_role(role_id):
    """ Updates an existing role. Requires the admin role. """

    data = request.values or {}

    # Verify the ID exists.
    role = Role.query.get(role_id)
    if not role:
        return error_response(404, 'Role ID not found')

    # Verify at least one required field was specified.
    if 'name' not in data and 'description' not in data:
        return error_response(400, 'Request must include at least name or description')

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
@verify_admin
def delete_role(role_id):
    """ Deletes a role. Requires the admin role. """

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
