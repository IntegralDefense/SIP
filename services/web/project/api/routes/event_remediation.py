from flask import jsonify, request, url_for

from project import db
from project.api import bp
from project.api.decorators import check_apikey
from project.api.errors import error_response
from project.models import EventRemediation

"""
CREATE
"""


@bp.route('/events/remediation', methods=['POST'])
@check_apikey
def create_event_remediation():
    """ Creates a new event remediation. """

    data = request.values or {}

    # Verify the required fields (value) are present.
    if 'value' not in data:
        return error_response(400, 'Request must include "value"')

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
@check_apikey
def read_event_remediation(event_remediation_id):
    """ Gets a single event remediation given its ID. """

    event_remediation = EventRemediation.query.get(event_remediation_id)
    if not event_remediation:
        return error_response(404, 'Event remediation ID not found')

    return jsonify(event_remediation.to_dict())


@bp.route('/events/remediation', methods=['GET'])
@check_apikey
def read_event_remediations():
    """ Gets a list of all the event remediations. """

    data = EventRemediation.query.all()
    return jsonify([item.to_dict() for item in data])


"""
UPDATE
"""


@bp.route('/events/remediation/<int:event_remediation_id>', methods=['PUT'])
@check_apikey
def update_event_remediation(event_remediation_id):
    """ Updates an existing event remediation. """

    data = request.values or {}

    # Verify the ID exists.
    event_remediation = EventRemediation.query.get(event_remediation_id)
    if not event_remediation:
        return error_response(404, 'Event remediation ID not found')

    # Verify the required fields (value) are present.
    if 'value' not in data:
        return error_response(400, 'Request must include "value"')

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
@check_apikey
def delete_event_remediation(event_remediation_id):
    """ Deletes an event remediation. """

    event_remediation = EventRemediation.query.get(event_remediation_id)
    if not event_remediation:
        return error_response(404, 'Event remediation ID not found')

    db.session.delete(event_remediation)
    db.session.commit()

    return '', 204
