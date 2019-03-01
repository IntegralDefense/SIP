from flask import jsonify, request, url_for
from sqlalchemy import exc

from project import db
from project.api import bp
from project.api.decorators import check_if_token_required, validate_json, validate_schema
from project.api.errors import error_response
from project.api.schemas import value_create, value_update
from project.models import EventDisposition

"""
CREATE
"""


@bp.route('/events/disposition', methods=['POST'])
@check_if_token_required
@validate_json
@validate_schema(value_create)
def create_event_disposition():
    """ Creates a new event disposition.
    
    .. :quickref: EventDisposition; Creates a new event disposition.

    **Example request**:

    .. sourcecode:: http

      POST /events/disposition HTTP/1.1
      Host: 127.0.0.1
      Content-Type: application/json

      {
        "value": "DELIVERY"
      }

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 201 Created
      Content-Type: application/json

      {
        "id": 1,
        "value": "DELIVERY"
      }

    :reqheader Authorization: Optional JWT Bearer token
    :resheader Content-Type: application/json
    :status 201: Event disposition created
    :status 400: JSON does not match the schema
    :status 401: Invalid role to perform this action
    :status 409: Event disposition already exists
    """

    data = request.get_json()

    # Verify this value does not already exist.
    existing = EventDisposition.query.filter_by(value=data['value']).first()
    if existing:
        return error_response(409, 'Event disposition already exists')

    # Create and add the new value.
    event_disposition = EventDisposition(value=data['value'])
    db.session.add(event_disposition)
    db.session.commit()

    response = jsonify(event_disposition.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.read_event_disposition',
                                           event_disposition_id=event_disposition.id)
    return response


"""
READ
"""


@bp.route('/events/disposition/<int:event_disposition_id>', methods=['GET'])
@check_if_token_required
def read_event_disposition(event_disposition_id):
    """ Gets a single event disposition given its ID.
    
    .. :quickref: EventDisposition; Gets a single event disposition given its ID.

    **Example request**:

    .. sourcecode:: http

      GET /events/disposition/1 HTTP/1.1
      Host: 127.0.0.1
      Accept: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "id": 1,
        "value": "DELIVERY"
      }

    :reqheader Authorization: Optional JWT Bearer token
    :resheader Content-Type: application/json
    :status 200: Event disposition found
    :status 401: Invalid role to perform this action
    :status 404: Event disposition ID not found
    """

    event_disposition = EventDisposition.query.get(event_disposition_id)
    if not event_disposition:
        return error_response(404, 'Event disposition ID not found')

    return jsonify(event_disposition.to_dict())


@bp.route('/events/disposition', methods=['GET'])
@check_if_token_required
def read_event_dispositions():
    """ Gets a list of all the event dispositions.
    
    .. :quickref: EventDisposition; Gets a list of all the event dispositions.

    **Example request**:

    .. sourcecode:: http

      GET /events/disposition HTTP/1.1
      Host: 127.0.0.1
      Accept: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      [
        {
          "id": 1,
          "value": "DELIVERY"
        },
        {
          "id": 2,
          "value": "EXPLOITATION"
        }
      ]

    :reqheader Authorization: Optional JWT Bearer token
    :resheader Content-Type: application/json
    :status 200: Event dispositions found
    :status 401: Invalid role to perform this action
    """

    data = EventDisposition.query.all()
    return jsonify([item.to_dict() for item in data])


"""
UPDATE
"""


@bp.route('/events/disposition/<int:event_disposition_id>', methods=['PUT'])
@check_if_token_required
@validate_json
@validate_schema(value_update)
def update_event_disposition(event_disposition_id):
    """ Updates an existing event disposition.
    
    .. :quickref: EventDisposition; Updates an existing event disposition.

    **Example request**:

    .. sourcecode:: http

      PUT /events/disposition/1 HTTP/1.1
      Host: 127.0.0.1
      Content-Type: application/json

      {
        "value": "EXPLOITATION",
      }

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "id": 1,
        "value": "EXPLOITATION"
      }

    :reqheader Authorization: Optional JWT Bearer token
    :resheader Content-Type: application/json
    :status 200: Event disposition updated
    :status 400: JSON does not match the schema
    :status 401: Invalid role to perform this action
    :status 404: Event disposition ID not found
    :status 409: Event disposition already exists
    """

    data = request.get_json()

    # Verify the ID exists.
    event_disposition = EventDisposition.query.get(event_disposition_id)
    if not event_disposition:
        return error_response(404, 'Event disposition ID not found')

    # Verify this value does not already exist.
    existing = EventDisposition.query.filter_by(value=data['value']).first()
    if existing:
        return error_response(409, 'Event disposition already exists')

    # Set the new value.
    event_disposition.value = data['value']
    db.session.commit()

    response = jsonify(event_disposition.to_dict())
    return response


"""
DELETE
"""


@bp.route('/events/disposition/<int:event_disposition_id>', methods=['DELETE'])
@check_if_token_required
def delete_event_disposition(event_disposition_id):
    """ Deletes an event disposition.
    
    .. :quickref: EventDisposition; Deletes an event disposition.

    **Example request**:

    .. sourcecode:: http

      DELETE /events/disposition/1 HTTP/1.1
      Host: 127.0.0.1

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 204 No Content

    :reqheader Authorization: Optional JWT Bearer token
    :status 204: Event disposition deleted
    :status 401: Invalid role to perform this action
    :status 404: Event disposition ID not found
    :status 409: Unable to delete event disposition due to foreign key constraints
    """

    event_disposition = EventDisposition.query.get(event_disposition_id)
    if not event_disposition:
        return error_response(404, 'Event disposition ID not found')

    try:
        db.session.delete(event_disposition)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        return error_response(409, 'Unable to delete event disposition due to foreign key constraints')

    return '', 204
