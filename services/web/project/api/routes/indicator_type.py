from flask import jsonify, request, url_for

from project import db
from project.api import bp
from project.api.decorators import check_apikey
from project.api.errors import error_response
from project.models import IndicatorType

"""
CREATE
"""


@bp.route('/indicators/type', methods=['POST'])
@check_apikey
def create_indicator_type():
    """ Creates a new indicator type. """

    data = request.values or {}

    # Verify the required fields (value) are present.
    if 'value' not in data:
        return error_response(400, 'Request must include "value"')

    # Verify this value does not already exist.
    existing = IndicatorType.query.filter_by(value=data['value']).first()
    if existing:
        return error_response(409, 'Indicator type already exists')

    # Create and add the new value.
    indicator_type = IndicatorType(value=data['value'])
    db.session.add(indicator_type)
    db.session.commit()

    response = jsonify(indicator_type.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.read_indicator_type',
                                           indicator_type_id=indicator_type.id)
    return response


"""
READ
"""


@bp.route('/indicators/type/<int:indicator_type_id>', methods=['GET'])
@check_apikey
def read_indicator_type(indicator_type_id):
    """ Gets a single indicator type given its ID. """

    indicator_type = IndicatorType.query.get(indicator_type_id)
    if not indicator_type:
        return error_response(404, 'Indicator type ID not found')

    return jsonify(indicator_type.to_dict())


@bp.route('/indicators/type', methods=['GET'])
@check_apikey
def read_indicator_types():
    """ Gets a list of all the indicator types. """

    data = IndicatorType.query.all()
    return jsonify([item.to_dict() for item in data])


"""
UPDATE
"""


@bp.route('/indicators/type/<int:indicator_type_id>', methods=['PUT'])
@check_apikey
def update_indicator_type(indicator_type_id):
    """ Updates an existing indicator type. """

    data = request.values or {}

    # Verify the ID exists.
    indicator_type = IndicatorType.query.get(indicator_type_id)
    if not indicator_type:
        return error_response(404, 'Indicator type ID not found')

    # Verify the required fields (value) are present.
    if 'value' not in data:
        return error_response(400, 'Request must include "value"')

    # Verify this value does not already exist.
    existing = IndicatorType.query.filter_by(value=data['value']).first()
    if existing:
        return error_response(409, 'Indicator type already exists')

    # Set the new value.
    indicator_type.value = data['value']
    db.session.commit()

    response = jsonify(indicator_type.to_dict())
    return response


"""
DELETE
"""


@bp.route('/indicators/type/<int:indicator_type_id>', methods=['DELETE'])
@check_apikey
def delete_indicator_type(indicator_type_id):
    """ Deletes an indicator type. """

    indicator_type = IndicatorType.query.get(indicator_type_id)
    if not indicator_type:
        return error_response(404, 'Indicator type ID not found')

    db.session.delete(indicator_type)
    db.session.commit()

    return '', 204
