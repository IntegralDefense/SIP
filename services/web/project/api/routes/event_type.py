from flask import jsonify, request, url_for
from sqlalchemy import exc

from project import db
from project.api import bp
from project.api.decorators import check_apikey
from project.api.errors import error_response
from project.models import EventType

"""
CREATE
"""


@bp.route('/events/type', methods=['POST'])
@check_apikey
def create_event_type():
    """ Creates a new event type. """

    data = request.values or {}

    # Verify the required fields (value) are present.
    if 'value' not in data:
        return error_response(400, 'Request must include "value"')

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
@check_apikey
def read_event_type(event_type_id):
    """ Gets a single event type given its ID. """

    event_type = EventType.query.get(event_type_id)
    if not event_type:
        return error_response(404, 'Event type ID not found')

    return jsonify(event_type.to_dict())


@bp.route('/events/type', methods=['GET'])
@check_apikey
def read_event_types():
    """ Gets a list of all the event types. """

    data = EventType.query.all()
    return jsonify([item.to_dict() for item in data])


"""
UPDATE
"""


@bp.route('/events/type/<int:event_type_id>', methods=['PUT'])
@check_apikey
def update_event_type(event_type_id):
    """ Updates an existing event type. """

    data = request.values or {}

    # Verify the ID exists.
    event_type = EventType.query.get(event_type_id)
    if not event_type:
        return error_response(404, 'Event type ID not found')

    # Verify the required fields (value) are present.
    if 'value' not in data:
        return error_response(400, 'Request must include "value"')

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
@check_apikey
def delete_event_type(event_type_id):
    """ Deletes an event type. """

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
