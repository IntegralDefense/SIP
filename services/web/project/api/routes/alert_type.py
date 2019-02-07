from flask import jsonify, request, url_for
from sqlalchemy import exc

from project import db
from project.api import bp
from project.api.decorators import check_if_token_required, validate_json, validate_schema
from project.api.errors import error_response
from project.models import AlertType

"""
CREATE
"""

create_schema = {
    'type': 'object',
    'properties': {
        'value': {'type': 'string', 'minLength': 1, 'maxLength': 255}
    },
    'required': ['value'],
    'additionalProperties': False
}


@bp.route('/alerts/type', methods=['POST'])
@check_if_token_required
@validate_json
@validate_schema(create_schema)
def create_alert_type():
    """ Creates a new alert type. """

    data = request.get_json()

    # Verify this value does not already exist.
    existing = AlertType.query.filter_by(value=data['value']).first()
    if existing:
        return error_response(409, 'Alert type already exists')

    # Create and add the new value.
    alert_type = AlertType(value=data['value'])
    db.session.add(alert_type)
    db.session.commit()

    response = jsonify(alert_type.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.read_alert_type',
                                           alert_type_id=alert_type.id)
    return response


"""
READ
"""


@bp.route('/alerts/type/<int:alert_type_id>', methods=['GET'])
@check_if_token_required
def read_alert_type(alert_type_id):
    """ Gets a single alert type given its ID. """

    alert_type = AlertType.query.get(alert_type_id)
    if not alert_type:
        return error_response(404, 'Alert type ID not found')

    return jsonify(alert_type.to_dict())


@bp.route('/alerts/type', methods=['GET'])
@check_if_token_required
def read_alert_types():
    """ Gets a list of all the alert types. """

    data = AlertType.query.all()
    return jsonify([item.to_dict() for item in data])


"""
UPDATE
"""

update_schema = {
    'type': 'object',
    'properties': {
        'value': {'type': 'string', 'minLength': 1, 'maxLength': 255}
    },
    'required': ['value'],
    'additionalProperties': False
}


@bp.route('/alerts/type/<int:alert_type_id>', methods=['PUT'])
@check_if_token_required
@validate_json
@validate_schema(update_schema)
def update_alert_type(alert_type_id):
    """ Updates an existing alert type. """

    data = request.get_json()

    # Verify the ID exists.
    alert_type = AlertType.query.get(alert_type_id)
    if not alert_type:
        return error_response(404, 'Alert type ID not found')

    # Verify this value does not already exist.
    existing = AlertType.query.filter_by(value=data['value']).first()
    if existing:
        return error_response(409, 'Alert type already exists')

    # Set the new value.
    alert_type.value = data['value']
    db.session.commit()

    response = jsonify(alert_type.to_dict())
    return response


"""
DELETE
"""


@bp.route('/alerts/type/<int:alert_type_id>', methods=['DELETE'])
@check_if_token_required
def delete_alert_type(alert_type_id):
    """ Deletes an alert type. """

    alert_type = AlertType.query.get(alert_type_id)
    if not alert_type:
        return error_response(404, 'Alert type ID not found')

    try:
        db.session.delete(alert_type)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        return error_response(409, 'Unable to delete alert type due to foreign key constraints')

    return '', 204
