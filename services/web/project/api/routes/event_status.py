from flask import jsonify, request, url_for
from sqlalchemy import exc

from project import db
from project.api import bp
from project.api.decorators import check_if_token_required, validate_json, validate_schema
from project.api.errors import error_response
from project.api.schemas import value_create, value_update
from project.models import EventStatus

"""
CREATE
"""


@bp.route('/events/status', methods=['POST'])
@check_if_token_required
@validate_json
@validate_schema(value_create)
def create_event_status():
    """ Creates a new event status.
    
    .. :quickref: EventStatus; Creates a new event status.

    **Example request**:

    .. sourcecode:: http

      POST /events/status HTTP/1.1
      Host: 127.0.0.1
      Content-Type: application/json

      {
        "value": "OPEN"
      }

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 201 Created
      Content-Type: application/json

      {
        "id": 1,
        "value": "OPEN"
      }

    :reqheader Authorization: Optional JWT Bearer token
    :resheader Content-Type: application/json
    :status 201: Event status created
    :status 400: JSON does not match the schema
    :status 401: Invalid role to perform this action
    :status 409: Event status already exists
    """

    data = request.get_json()

    # Verify this value does not already exist.
    existing = EventStatus.query.filter_by(value=data['value']).first()
    if existing:
        return error_response(409, 'Event status already exists')

    # Create and add the new value.
    event_status = EventStatus(value=data['value'])
    db.session.add(event_status)
    db.session.commit()

    response = jsonify(event_status.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.read_event_status',
                                           event_status_id=event_status.id)
    return response


"""
READ
"""


@bp.route('/events/status/<int:event_status_id>', methods=['GET'])
@check_if_token_required
def read_event_status(event_status_id):
    """ Gets a single event status given its ID.
    
    .. :quickref: EventStatus; Gets a single event status given its ID.

    **Example request**:

    .. sourcecode:: http

      GET /events/status/1 HTTP/1.1
      Host: 127.0.0.1
      Accept: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "id": 1,
        "value": "OPEN"
      }

    :reqheader Authorization: Optional JWT Bearer token
    :resheader Content-Type: application/json
    :status 200: Event status found
    :status 401: Invalid role to perform this action
    :status 404: Event status ID not found
    """

    event_status = EventStatus.query.get(event_status_id)
    if not event_status:
        return error_response(404, 'Event status ID not found')

    return jsonify(event_status.to_dict())


@bp.route('/events/status', methods=['GET'])
@check_if_token_required
def read_event_statuses():
    """ Gets a list of all the event statuses.
    
    .. :quickref: EventStatus; Gets a list of all the event statuses.

    **Example request**:

    .. sourcecode:: http

      GET /events/status HTTP/1.1
      Host: 127.0.0.1
      Accept: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      [
        {
          "id": 1,
          "value": "OPEN"
        },
        {
          "id": 2,
          "value": "CLOSED"
        }
      ]

    :reqheader Authorization: Optional JWT Bearer token
    :resheader Content-Type: application/json
    :status 200: Event statuses found
    :status 401: Invalid role to perform this action
    """

    data = EventStatus.query.all()
    return jsonify([item.to_dict() for item in data])


"""
UPDATE
"""


@bp.route('/events/status/<int:event_status_id>', methods=['PUT'])
@check_if_token_required
@validate_json
@validate_schema(value_update)
def update_event_status(event_status_id):
    """ Updates an existing event status.
    
    .. :quickref: EventStatus; Updates an existing event status.

    **Example request**:

    .. sourcecode:: http

      PUT /events/status/1 HTTP/1.1
      Host: 127.0.0.1
      Content-Type: application/json

      {
        "value": "CLOSED",
      }

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "id": 1,
        "value": "CLOSED"
      }

    :reqheader Authorization: Optional JWT Bearer token
    :resheader Content-Type: application/json
    :status 200: Event status updated
    :status 400: JSON does not match the schema
    :status 401: Invalid role to perform this action
    :status 404: Event status ID not found
    :status 409: Event status already exists
    """

    data = request.get_json()

    # Verify the ID exists.
    event_status = EventStatus.query.get(event_status_id)
    if not event_status:
        return error_response(404, 'Event status ID not found')

    # Verify this value does not already exist.
    existing = EventStatus.query.filter_by(value=data['value']).first()
    if existing:
        return error_response(409, 'Event status already exists')

    # Set the new value.
    event_status.value = data['value']
    db.session.commit()

    response = jsonify(event_status.to_dict())
    return response


"""
DELETE
"""


@bp.route('/events/status/<int:event_status_id>', methods=['DELETE'])
@check_if_token_required
def delete_event_status(event_status_id):
    """ Deletes an event status.
    
    .. :quickref: EventStatus; Deletes an event status.

    **Example request**:

    .. sourcecode:: http

      DELETE /events/status/1 HTTP/1.1
      Host: 127.0.0.1

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 204 No Content

    :reqheader Authorization: Optional JWT Bearer token
    :status 204: Event status deleted
    :status 401: Invalid role to perform this action
    :status 404: Event status ID not found
    :status 409: Unable to delete event status due to foreign key constraints
    """

    event_status = EventStatus.query.get(event_status_id)
    if not event_status:
        return error_response(404, 'Event status ID not found')

    try:
        db.session.delete(event_status)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        return error_response(409, 'Unable to delete event status due to foreign key constraints')

    return '', 204
