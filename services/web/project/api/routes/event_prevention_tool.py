from flask import jsonify, request, url_for
from sqlalchemy import exc

from project import db
from project.api import bp
from project.api.decorators import check_apikey
from project.api.errors import error_response
from project.models import EventPreventionTool

"""
CREATE
"""


@bp.route('/events/preventiontool', methods=['POST'])
@check_apikey
def create_event_prevention_tool():
    """ Creates a new event prevention tool. """

    data = request.values or {}

    # Verify the required fields (value) are present.
    if 'value' not in data:
        return error_response(400, 'Request must include "value"')

    # Verify this value does not already exist.
    existing = EventPreventionTool.query.filter_by(value=data['value']).first()
    if existing:
        return error_response(409, 'Event prevention tool already exists')

    # Create and add the new value.
    event_prevention_tool = EventPreventionTool(value=data['value'])
    db.session.add(event_prevention_tool)
    db.session.commit()

    response = jsonify(event_prevention_tool.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.read_event_prevention_tool',
                                           event_prevention_tool_id=event_prevention_tool.id)
    return response


"""
READ
"""


@bp.route('/events/preventiontool/<int:event_prevention_tool_id>', methods=['GET'])
@check_apikey
def read_event_prevention_tool(event_prevention_tool_id):
    """ Gets a single event prevention tool given its ID. """

    event_prevention_tool = EventPreventionTool.query.get(event_prevention_tool_id)
    if not event_prevention_tool:
        return error_response(404, 'Event prevention tool ID not found')

    return jsonify(event_prevention_tool.to_dict())


@bp.route('/events/preventiontool', methods=['GET'])
@check_apikey
def read_event_prevention_tools():
    """ Gets a list of all the event prevention tools. """

    data = EventPreventionTool.query.all()
    return jsonify([item.to_dict() for item in data])


"""
UPDATE
"""


@bp.route('/events/preventiontool/<int:event_prevention_tool_id>', methods=['PUT'])
@check_apikey
def update_event_prevention_tool(event_prevention_tool_id):
    """ Updates an existing event prevention tool. """

    data = request.values or {}

    # Verify the ID exists.
    event_prevention_tool = EventPreventionTool.query.get(event_prevention_tool_id)
    if not event_prevention_tool:
        return error_response(404, 'Event prevention tool ID not found')

    # Verify the required fields (value) are present.
    if 'value' not in data:
        return error_response(400, 'Request must include "value"')

    # Verify this value does not already exist.
    existing = EventPreventionTool.query.filter_by(value=data['value']).first()
    if existing:
        return error_response(409, 'Event prevention tool already exists')

    # Set the new value.
    event_prevention_tool.value = data['value']
    db.session.commit()

    response = jsonify(event_prevention_tool.to_dict())
    return response


"""
DELETE
"""


@bp.route('/events/preventiontool/<int:event_prevention_tool_id>', methods=['DELETE'])
@check_apikey
def delete_event_prevention_tool(event_prevention_tool_id):
    """ Deletes an event prevention tool. """

    event_prevention_tool = EventPreventionTool.query.get(event_prevention_tool_id)
    if not event_prevention_tool:
        return error_response(404, 'Event prevention tool ID not found')

    try:
        db.session.delete(event_prevention_tool)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        return error_response(409, 'Unable to delete event prevention tool due to foreign key constraints')

    return '', 204
