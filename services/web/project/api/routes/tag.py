from flask import jsonify, request, url_for
from sqlalchemy import exc

from project import db
from project.api import bp
from project.api.decorators import check_if_token_required, validate_json, validate_schema
from project.api.errors import error_response
from project.models import Tag

"""
CREATE
"""

create_schema = {
    'type': 'object',
    'properties': {
        'value': {'type': 'string', 'minLength': 1, 'maxLength': 255}
    },
    'required': ['value'],
    'additionalProperties': False
}


@bp.route('/tags', methods=['POST'])
@check_if_token_required
@validate_json
@validate_schema(create_schema)
def create_tag():
    """ Creates a new tag. """

    data = request.get_json()

    # Verify this value does not already exist.
    existing = Tag.query.filter_by(value=data['value']).first()
    if existing:
        return error_response(409, 'Tag already exists')

    # Create and add the new value.
    tag = Tag(value=data['value'])
    db.session.add(tag)
    db.session.commit()

    response = jsonify(tag.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.read_tag', tag_id=tag.id)
    return response


"""
READ
"""


@bp.route('/tags/<int:tag_id>', methods=['GET'])
@check_if_token_required
def read_tag(tag_id):
    """ Gets a single tag given its ID. """

    tag = Tag.query.get(tag_id)
    if not tag:
        return error_response(404, 'Tag ID not found')

    return jsonify(tag.to_dict())


@bp.route('/tags', methods=['GET'])
@check_if_token_required
def read_tags():
    """ Gets a list of all the tags. """

    data = Tag.query.all()
    return jsonify([item.to_dict() for item in data])


"""
UPDATE
"""

update_schema = {
    'type': 'object',
    'properties': {
        'value': {'type': 'string', 'minLength': 1, 'maxLength': 255}
    },
    'required': ['value'],
    'additionalProperties': False
}


@bp.route('/tags/<int:tag_id>', methods=['PUT'])
@check_if_token_required
@validate_json
@validate_schema(update_schema)
def update_tag(tag_id):
    """ Updates an existing tag. """

    data = request.get_json()

    # Verify the ID exists.
    tag = Tag.query.get(tag_id)
    if not tag:
        return error_response(404, 'Tag ID not found')

    # Verify this value does not already exist.
    existing = Tag.query.filter_by(value=data['value']).first()
    if existing:
        return error_response(409, 'Tag already exists')

    # Set the new value.
    tag.value = data['value']
    db.session.commit()

    response = jsonify(tag.to_dict())
    return response


"""
DELETE
"""


@bp.route('/tags/<int:tag_id>', methods=['DELETE'])
@check_if_token_required
def delete_tag(tag_id):
    """ Deletes a tag. """

    tag = Tag.query.get(tag_id)
    if not tag:
        return error_response(404, 'Tag ID not found')

    try:
        db.session.delete(tag)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        return error_response(409, 'Unable to delete tag due to foreign key constraints')

    return '', 204
