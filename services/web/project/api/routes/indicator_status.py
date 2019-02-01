from flask import jsonify, request, url_for
from sqlalchemy import exc

from project import db
from project.api import bp
from project.api.decorators import check_apikey
from project.api.errors import error_response
from project.models import IndicatorStatus

"""
CREATE
"""


@bp.route('/indicators/status', methods=['POST'])
@check_apikey
def create_indicator_status():
    """ Creates a new indicator status. """

    data = request.values or {}

    # Verify the required fields (value) are present.
    if 'value' not in data:
        return error_response(400, 'Request must include "value"')

    # Verify this value does not already exist.
    existing = IndicatorStatus.query.filter_by(value=data['value']).first()
    if existing:
        return error_response(409, 'Indicator status already exists')

    # Create and add the new value.
    indicator_status = IndicatorStatus(value=data['value'])
    db.session.add(indicator_status)
    db.session.commit()

    response = jsonify(indicator_status.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.read_indicator_status',
                                           indicator_status_id=indicator_status.id)
    return response


"""
READ
"""


@bp.route('/indicators/status/<int:indicator_status_id>', methods=['GET'])
@check_apikey
def read_indicator_status(indicator_status_id):
    """ Gets a single indicator status given its ID. """

    indicator_status = IndicatorStatus.query.get(indicator_status_id)
    if not indicator_status:
        return error_response(404, 'Indicator status ID not found')

    return jsonify(indicator_status.to_dict())


@bp.route('/indicators/status', methods=['GET'])
@check_apikey
def read_indicator_statuses():
    """ Gets a list of all the indicator statuses. """

    data = IndicatorStatus.query.all()
    return jsonify([item.to_dict() for item in data])


"""
UPDATE
"""


@bp.route('/indicators/status/<int:indicator_status_id>', methods=['PUT'])
@check_apikey
def update_indicator_status(indicator_status_id):
    """ Updates an existing indicator status. """

    data = request.values or {}

    # Verify the ID exists.
    indicator_status = IndicatorStatus.query.get(indicator_status_id)
    if not indicator_status:
        return error_response(404, 'Indicator status ID not found')

    # Verify the required fields (value) are present.
    if 'value' not in data:
        return error_response(400, 'Request must include "value"')

    # Verify this value does not already exist.
    existing = IndicatorStatus.query.filter_by(value=data['value']).first()
    if existing:
        return error_response(409, 'Indicator status already exists')

    # Set the new value.
    indicator_status.value = data['value']
    db.session.commit()

    response = jsonify(indicator_status.to_dict())
    return response


"""
DELETE
"""


@bp.route('/indicators/status/<int:indicator_status_id>', methods=['DELETE'])
@check_apikey
def delete_indicator_status(indicator_status_id):
    """ Deletes an indicator status. """

    indicator_status = IndicatorStatus.query.get(indicator_status_id)
    if not indicator_status:
        return error_response(404, 'Indicator status ID not found')

    try:
        db.session.delete(indicator_status)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        return error_response(409, 'Unable to delete indicator status due to foreign key constraints')

    return '', 204
