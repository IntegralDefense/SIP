from flask import jsonify, request, url_for
from sqlalchemy import exc

from project import db
from project.api import bp
from project.api.decorators import check_if_token_required
from project.api.errors import error_response
from project.models import EventStatus

"""
CREATE
"""


@bp.route('/events/status', methods=['POST'])
@check_if_token_required
def create_event_status():
    """ Creates a new event status. """

    data = request.values or {}

    # Verify the required fields (value) are present.
    if 'value' not in data:
        return error_response(400, 'Request must include "value"')

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
    """ Gets a single event status given its ID. """

    event_status = EventStatus.query.get(event_status_id)
    if not event_status:
        return error_response(404, 'Event status ID not found')

    return jsonify(event_status.to_dict())


@bp.route('/events/status', methods=['GET'])
@check_if_token_required
def read_event_statuss():
    """ Gets a list of all the event statuss. """

    data = EventStatus.query.all()
    return jsonify([item.to_dict() for item in data])


"""
UPDATE
"""


@bp.route('/events/status/<int:event_status_id>', methods=['PUT'])
@check_if_token_required
def update_event_status(event_status_id):
    """ Updates an existing event status. """

    data = request.values or {}

    # Verify the ID exists.
    event_status = EventStatus.query.get(event_status_id)
    if not event_status:
        return error_response(404, 'Event status ID not found')

    # Verify the required fields (value) are present.
    if 'value' not in data:
        return error_response(400, 'Request must include "value"')

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
    """ Deletes an event status. """

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
