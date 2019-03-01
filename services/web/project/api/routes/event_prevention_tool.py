from flask import jsonify, request, url_for
from sqlalchemy import exc

from project import db
from project.api import bp
from project.api.decorators import check_if_token_required, validate_json, validate_schema
from project.api.errors import error_response
from project.api.schemas import value_create, value_update
from project.models import EventPreventionTool

"""
CREATE
"""


@bp.route('/events/preventiontool', methods=['POST'])
@check_if_token_required
@validate_json
@validate_schema(value_create)
def create_event_prevention_tool():
    """ Creates a new event prevention tool.
    
    .. :quickref: EventPreventionTool; Creates a new event prevention tool.

    **Example request**:

    .. sourcecode:: http

      POST /events/preventiontool HTTP/1.1
      Host: 127.0.0.1
      Content-Type: application/json

      {
        "value": "IPS"
      }

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 201 Created
      Content-Type: application/json

      {
        "id": 1,
        "value": "IPS"
      }

    :reqheader Authorization: Optional JWT Bearer token
    :resheader Content-Type: application/json
    :status 201: Event prevention tool created
    :status 400: JSON does not match the schema
    :status 401: Invalid role to perform this action
    :status 409: Event prevention tool already exists
    """

    data = request.get_json()

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
@check_if_token_required
def read_event_prevention_tool(event_prevention_tool_id):
    """ Gets a single event prevention tool given its ID.
    
    .. :quickref: EventPreventionTool; Gets a single event prevention tool given its ID.

    **Example request**:

    .. sourcecode:: http

      GET /events/preventiontool/1 HTTP/1.1
      Host: 127.0.0.1
      Accept: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "id": 1,
        "value": "IPS"
      }

    :reqheader Authorization: Optional JWT Bearer token
    :resheader Content-Type: application/json
    :status 200: Event prevention tool found
    :status 401: Invalid role to perform this action
    :status 404: Event prevention tool ID not found
    """

    event_prevention_tool = EventPreventionTool.query.get(event_prevention_tool_id)
    if not event_prevention_tool:
        return error_response(404, 'Event prevention tool ID not found')

    return jsonify(event_prevention_tool.to_dict())


@bp.route('/events/preventiontool', methods=['GET'])
@check_if_token_required
def read_event_prevention_tools():
    """ Gets a list of all the event prevention tools.
    
    .. :quickref: EventPreventionTool; Gets a list of all the event prevention tools.

    **Example request**:

    .. sourcecode:: http

      GET /events/preventiontool HTTP/1.1
      Host: 127.0.0.1
      Accept: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      [
        {
          "id": 1,
          "value": "IPS"
        },
        {
          "id": 2,
          "value": "ANTIVIRUS"
        }
      ]

    :reqheader Authorization: Optional JWT Bearer token
    :resheader Content-Type: application/json
    :status 200: Event prevention tools found
    :status 401: Invalid role to perform this action
    """

    data = EventPreventionTool.query.all()
    return jsonify([item.to_dict() for item in data])


"""
UPDATE
"""


@bp.route('/events/preventiontool/<int:event_prevention_tool_id>', methods=['PUT'])
@check_if_token_required
@validate_json
@validate_schema(value_update)
def update_event_prevention_tool(event_prevention_tool_id):
    """ Updates an existing event prevention tool.
    
    .. :quickref: EventPreventionTool; Updates an existing event prevention tool.

    **Example request**:

    .. sourcecode:: http

      PUT /events/preventiontool/1 HTTP/1.1
      Host: 127.0.0.1
      Content-Type: application/json

      {
        "value": "ANTIVIRUS",
      }

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "id": 1,
        "value": "ANTIVIRUS"
      }

    :reqheader Authorization: Optional JWT Bearer token
    :resheader Content-Type: application/json
    :status 200: Event prevention tool updated
    :status 400: JSON does not match the schema
    :status 401: Invalid role to perform this action
    :status 404: Event prevention tool ID not found
    :status 409: Event prevention tool already exists
    """

    data = request.get_json()

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
@check_if_token_required
def delete_event_prevention_tool(event_prevention_tool_id):
    """ Deletes an event prevention tool.
    
    .. :quickref: EventPreventionTool; Deletes an event prevention tool.

    **Example request**:

    .. sourcecode:: http

      DELETE /events/preventiontool/1 HTTP/1.1
      Host: 127.0.0.1

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 204 No Content

    :reqheader Authorization: Optional JWT Bearer token
    :status 204: Event prevention tool deleted
    :status 401: Invalid role to perform this action
    :status 404: Event prevention tool ID not found
    :status 409: Unable to delete event prevention tool due to foreign key constraints
    """

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
