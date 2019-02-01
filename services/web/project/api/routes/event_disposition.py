from flask import jsonify, request, url_for
from sqlalchemy import exc

from project import db
from project.api import bp
from project.api.decorators import check_apikey
from project.api.errors import error_response
from project.models import EventDisposition

"""
CREATE
"""


@bp.route('/events/disposition', methods=['POST'])
@check_apikey
def create_event_disposition():
    """ Creates a new event disposition. """

    data = request.values or {}

    # Verify the required fields (value) are present.
    if 'value' not in data:
        return error_response(400, 'Request must include "value"')

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
@check_apikey
def read_event_disposition(event_disposition_id):
    """ Gets a single event disposition given its ID. """

    event_disposition = EventDisposition.query.get(event_disposition_id)
    if not event_disposition:
        return error_response(404, 'Event disposition ID not found')

    return jsonify(event_disposition.to_dict())


@bp.route('/events/disposition', methods=['GET'])
@check_apikey
def read_event_dispositions():
    """ Gets a list of all the event dispositions. """

    data = EventDisposition.query.all()
    return jsonify([item.to_dict() for item in data])


"""
UPDATE
"""


@bp.route('/events/disposition/<int:event_disposition_id>', methods=['PUT'])
@check_apikey
def update_event_disposition(event_disposition_id):
    """ Updates an existing event disposition. """

    data = request.values or {}

    # Verify the ID exists.
    event_disposition = EventDisposition.query.get(event_disposition_id)
    if not event_disposition:
        return error_response(404, 'Event disposition ID not found')

    # Verify the required fields (value) are present.
    if 'value' not in data:
        return error_response(400, 'Request must include "value"')

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
@check_apikey
def delete_event_disposition(event_disposition_id):
    """ Deletes an event disposition. """

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
