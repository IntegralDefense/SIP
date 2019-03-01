from flask import jsonify, request, url_for
from sqlalchemy import exc

from project import db
from project.api import bp
from project.api.decorators import check_if_token_required, validate_json, validate_schema
from project.api.errors import error_response
from project.api.schemas import value_create, value_update
from project.models import EventRemediation

"""
CREATE
"""


@bp.route('/events/remediation', methods=['POST'])
@check_if_token_required
@validate_json
@validate_schema(value_create)
def create_event_remediation():
    """ Creates a new event remediation.
    
    .. :quickref: EventRemediation; Creates a new event remediation.

    **Example request**:

    .. sourcecode:: http

      POST /events/remediation HTTP/1.1
      Host: 127.0.0.1
      Content-Type: application/json

      {
        "value": "REMOVED FROM MAILBOX"
      }

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 201 Created
      Content-Type: application/json

      {
        "id": 1,
        "value": "REMOVED FROM MAILBOX"
      }

    :reqheader Authorization: Optional JWT Bearer token
    :resheader Content-Type: application/json
    :status 201: Event remediation created
    :status 400: JSON does not match the schema
    :status 401: Invalid role to perform this action
    :status 409: Event remediation already exists
    """

    data = request.get_json()

    # Verify this value does not already exist.
    existing = EventRemediation.query.filter_by(value=data['value']).first()
    if existing:
        return error_response(409, 'Event remediation already exists')

    # Create and add the new value.
    event_remediation = EventRemediation(value=data['value'])
    db.session.add(event_remediation)
    db.session.commit()

    response = jsonify(event_remediation.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.read_event_remediation',
                                           event_remediation_id=event_remediation.id)
    return response


"""
READ
"""


@bp.route('/events/remediation/<int:event_remediation_id>', methods=['GET'])
@check_if_token_required
def read_event_remediation(event_remediation_id):
    """ Gets a single event remediation given its ID.
    
    .. :quickref: EventRemediation; Gets a single event remediation given its ID.

    **Example request**:

    .. sourcecode:: http

      GET /events/remediation/1 HTTP/1.1
      Host: 127.0.0.1
      Accept: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "id": 1,
        "value": "REMOVED FROM MAILBOX"
      }

    :reqheader Authorization: Optional JWT Bearer token
    :resheader Content-Type: application/json
    :status 200: Event remediation found
    :status 401: Invalid role to perform this action
    :status 404: Event remediation ID not found
    """

    event_remediation = EventRemediation.query.get(event_remediation_id)
    if not event_remediation:
        return error_response(404, 'Event remediation ID not found')

    return jsonify(event_remediation.to_dict())


@bp.route('/events/remediation', methods=['GET'])
@check_if_token_required
def read_event_remediations():
    """ Gets a list of all the event remediations.
    
    .. :quickref: EventRemediation; Gets a list of all the event remediations.

    **Example request**:

    .. sourcecode:: http

      GET /events/remediation HTTP/1.1
      Host: 127.0.0.1
      Accept: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      [
        {
          "id": 1,
          "value": "REMOVED FROM MAILBOX"
        },
        {
          "id": 2,
          "value": "REIMAGED"
        }
      ]

    :reqheader Authorization: Optional JWT Bearer token
    :resheader Content-Type: application/json
    :status 200: Event remediations found
    :status 401: Invalid role to perform this action
    """

    data = EventRemediation.query.all()
    return jsonify([item.to_dict() for item in data])


"""
UPDATE
"""


@bp.route('/events/remediation/<int:event_remediation_id>', methods=['PUT'])
@check_if_token_required
@validate_json
@validate_schema(value_update)
def update_event_remediation(event_remediation_id):
    """ Updates an existing event remediation.
    
    .. :quickref: EventRemediation; Updates an existing event remediation.

    **Example request**:

    .. sourcecode:: http

      PUT /events/remediation/1 HTTP/1.1
      Host: 127.0.0.1
      Content-Type: application/json

      {
        "value": "REIMAGED",
      }

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "id": 1,
        "value": "REIMAGED"
      }

    :reqheader Authorization: Optional JWT Bearer token
    :resheader Content-Type: application/json
    :status 200: Event remediation updated
    :status 400: JSON does not match the schema
    :status 401: Invalid role to perform this action
    :status 404: Event remediation ID not found
    :status 409: Event remediation already exists
    """

    data = request.get_json()

    # Verify the ID exists.
    event_remediation = EventRemediation.query.get(event_remediation_id)
    if not event_remediation:
        return error_response(404, 'Event remediation ID not found')

    # Verify this value does not already exist.
    existing = EventRemediation.query.filter_by(value=data['value']).first()
    if existing:
        return error_response(409, 'Event remediation already exists')

    # Set the new value.
    event_remediation.value = data['value']
    db.session.commit()

    response = jsonify(event_remediation.to_dict())
    return response


"""
DELETE
"""


@bp.route('/events/remediation/<int:event_remediation_id>', methods=['DELETE'])
@check_if_token_required
def delete_event_remediation(event_remediation_id):
    """ Deletes an event remediation.
    
    .. :quickref: EventRemediation; Deletes an event remediation.

    **Example request**:

    .. sourcecode:: http

      DELETE /events/remediation/1 HTTP/1.1
      Host: 127.0.0.1

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 204 No Content

    :reqheader Authorization: Optional JWT Bearer token
    :status 204: Event remediation deleted
    :status 401: Invalid role to perform this action
    :status 404: Event remediation ID not found
    :status 409: Unable to delete event remediation due to foreign key constraints
    """

    event_remediation = EventRemediation.query.get(event_remediation_id)
    if not event_remediation:
        return error_response(404, 'Event remediation ID not found')

    try:
        db.session.delete(event_remediation)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        return error_response(409, 'Unable to delete event remediation due to foreign key constraints')

    return '', 204
