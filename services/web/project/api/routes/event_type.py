from flask import jsonify, request, url_for
from sqlalchemy import exc

from project import db
from project.api import bp
from project.api.decorators import check_if_token_required, validate_json, validate_schema
from project.api.errors import error_response
from project.api.schemas import value_create, value_update
from project.models import EventType

"""
CREATE
"""


@bp.route('/events/type', methods=['POST'])
@check_if_token_required
@validate_json
@validate_schema(value_create)
def create_event_type():
    """ Creates a new event type.
    
    .. :quickref: EventType; Creates a new event type.

    **Example request**:

    .. sourcecode:: http

      POST /events/type HTTP/1.1
      Host: 127.0.0.1
      Content-Type: application/json

      {
        "value": "PHISH"
      }

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 201 Created
      Content-Type: application/json

      {
        "id": 1,
        "value": "PHISH"
      }

    :reqheader Authorization: Optional JWT Bearer token
    :resheader Content-Type: application/json
    :status 201: Event type created
    :status 400: JSON does not match the schema
    :status 401: Invalid role to perform this action
    :status 409: Event type already exists
    """

    data = request.get_json()

    # Verify this value does not already exist.
    existing = EventType.query.filter_by(value=data['value']).first()
    if existing:
        return error_response(409, 'Event type already exists')

    # Create and add the new value.
    event_type = EventType(value=data['value'])
    db.session.add(event_type)
    db.session.commit()

    response = jsonify(event_type.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.read_event_type',
                                           event_type_id=event_type.id)
    return response


"""
READ
"""


@bp.route('/events/type/<int:event_type_id>', methods=['GET'])
@check_if_token_required
def read_event_type(event_type_id):
    """ Gets a single event type given its ID.
    
    .. :quickref: EventType; Gets a single event type given its ID.

    **Example request**:

    .. sourcecode:: http

      GET /events/type/1 HTTP/1.1
      Host: 127.0.0.1
      Accept: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "id": 1,
        "value": "PHISH"
      }

    :reqheader Authorization: Optional JWT Bearer token
    :resheader Content-Type: application/json
    :status 200: Event type found
    :status 401: Invalid role to perform this action
    :status 404: Event type ID not found
    """

    event_type = EventType.query.get(event_type_id)
    if not event_type:
        return error_response(404, 'Event type ID not found')

    return jsonify(event_type.to_dict())


@bp.route('/events/type', methods=['GET'])
@check_if_token_required
def read_event_types():
    """ Gets a list of all the event types.
    
    .. :quickref: EventType; Gets a list of all the event types.

    **Example request**:

    .. sourcecode:: http

      GET /events/type HTTP/1.1
      Host: 127.0.0.1
      Accept: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      [
        {
          "id": 1,
          "value": "PHISH"
        },
        {
          "id": 2,
          "value": "HOST COMPROMISE"
        }
      ]

    :reqheader Authorization: Optional JWT Bearer token
    :resheader Content-Type: application/json
    :status 200: Event types found
    :status 401: Invalid role to perform this action
    """

    data = EventType.query.all()
    return jsonify([item.to_dict() for item in data])


"""
UPDATE
"""


@bp.route('/events/type/<int:event_type_id>', methods=['PUT'])
@check_if_token_required
@validate_json
@validate_schema(value_update)
def update_event_type(event_type_id):
    """ Updates an existing event type.
    
    .. :quickref: EventType; Updates an existing event type.

    **Example request**:

    .. sourcecode:: http

      PUT /events/type/1 HTTP/1.1
      Host: 127.0.0.1
      Content-Type: application/json

      {
        "value": "HOST COMPROMISE",
      }

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "id": 1,
        "value": "HOST COMPROMISE"
      }

    :reqheader Authorization: Optional JWT Bearer token
    :resheader Content-Type: application/json
    :status 200: Event type updated
    :status 400: JSON does not match the schema
    :status 401: Invalid role to perform this action
    :status 404: Event type ID not found
    :status 409: Event type already exists
    """

    data = request.get_json()

    # Verify the ID exists.
    event_type = EventType.query.get(event_type_id)
    if not event_type:
        return error_response(404, 'Event type ID not found')

    # Verify this value does not already exist.
    existing = EventType.query.filter_by(value=data['value']).first()
    if existing:
        return error_response(409, 'Event type already exists')

    # Set the new value.
    event_type.value = data['value']
    db.session.commit()

    response = jsonify(event_type.to_dict())
    return response


"""
DELETE
"""


@bp.route('/events/type/<int:event_type_id>', methods=['DELETE'])
@check_if_token_required
def delete_event_type(event_type_id):
    """ Deletes an event type.
    
    .. :quickref: EventType; Deletes an event type.

    **Example request**:

    .. sourcecode:: http

      DELETE /events/type/1 HTTP/1.1
      Host: 127.0.0.1

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 204 No Content

    :reqheader Authorization: Optional JWT Bearer token
    :status 204: Event type deleted
    :status 401: Invalid role to perform this action
    :status 404: Event type ID not found
    :status 409: Unable to delete event type due to foreign key constraints
    """

    event_type = EventType.query.get(event_type_id)
    if not event_type:
        return error_response(404, 'Event type ID not found')

    try:
        db.session.delete(event_type)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        return error_response(409, 'Unable to delete event type due to foreign key constraints')

    return '', 204
