from flask import jsonify, request, url_for
from sqlalchemy import exc

from project import db
from project.api import bp
from project.api.decorators import check_apikey, validate_json, validate_schema
from project.api.errors import error_response
from project.api.schemas import value_create, value_update
from project.models import Tag

"""
CREATE
"""


@bp.route('/tags', methods=['POST'])
@check_apikey
@validate_json
@validate_schema(value_create)
def create_tag():
    """ Creates a new tag.
    
    .. :quickref: Tag; Creates a new tag.

    **Example request**:

    .. sourcecode:: http

      POST /tags HTTP/1.1
      Host: 127.0.0.1
      Content-Type: application/json

      {
        "value": "phish"
      }

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 201 Created
      Content-Type: application/json

      {
        "id": 1,
        "value": "phish"
      }

    :reqheader Authorization: Optional Apikey value
    :resheader Content-Type: application/json
    :status 201: Tag created
    :status 400: JSON does not match the schema
    :status 401: Invalid role to perform this action
    :status 409: Tag already exists
    """

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
@check_apikey
def read_tag(tag_id):
    """ Gets a single tag given its ID.
    
    .. :quickref: Tag; Gets a single tag given its ID.

    **Example request**:

    .. sourcecode:: http

      GET /tags/1 HTTP/1.1
      Host: 127.0.0.1
      Accept: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "id": 1,
        "value": "phish"
      }

    :reqheader Authorization: Optional Apikey value
    :resheader Content-Type: application/json
    :status 200: Tag found
    :status 401: Invalid role to perform this action
    :status 404: Tag ID not found
    """

    tag = Tag.query.get(tag_id)
    if not tag:
        return error_response(404, 'Tag ID not found')

    return jsonify(tag.to_dict())


@bp.route('/tags', methods=['GET'])
@check_apikey
def read_tags():
    """ Gets a list of all the tags.
    
    .. :quickref: Tag; Gets a list of all the tags.

    **Example request**:

    .. sourcecode:: http

      GET /tags HTTP/1.1
      Host: 127.0.0.1
      Accept: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      [
        {
          "id": 1,
          "value": "phish"
        },
        {
          "id": 2,
          "value": "from_address"
        }
      ]

    :reqheader Authorization: Optional Apikey value
    :resheader Content-Type: application/json
    :status 200: Tags found
    :status 401: Invalid role to perform this action
    """

    data = Tag.query.all()
    return jsonify([item.to_dict() for item in data])


"""
UPDATE
"""


@bp.route('/tags/<int:tag_id>', methods=['PUT'])
@check_apikey
@validate_json
@validate_schema(value_update)
def update_tag(tag_id):
    """ Updates an existing tag.
    
    .. :quickref: Tag; Updates an existing tag.

    **Example request**:

    .. sourcecode:: http

      PUT /tags/1 HTTP/1.1
      Host: 127.0.0.1
      Content-Type: application/json

      {
        "value": "from_address",
      }

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "id": 1,
        "value": "from_address"
      }

    :reqheader Authorization: Optional Apikey value
    :resheader Content-Type: application/json
    :status 200: Tag updated
    :status 400: JSON does not match the schema
    :status 401: Invalid role to perform this action
    :status 404: Tag ID not found
    :status 409: Tag already exists
    """

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
@check_apikey
def delete_tag(tag_id):
    """ Deletes a tag.
    
    .. :quickref: Tag; Deletes a tag.

    **Example request**:

    .. sourcecode:: http

      DELETE /tags/1 HTTP/1.1
      Host: 127.0.0.1

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 204 No Content

    :reqheader Authorization: Optional Apikey value
    :status 204: Tag deleted
    :status 401: Invalid role to perform this action
    :status 404: Tag ID not found
    :status 409: Unable to delete tag due to foreign key constraints
    """

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
