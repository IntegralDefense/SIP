from flask import jsonify, request, url_for
from sqlalchemy import exc

from project import db
from project.api import bp
from project.api.decorators import check_if_token_required, validate_json, validate_schema
from project.api.errors import error_response
from project.models import IndicatorImpact

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


@bp.route('/indicators/impact', methods=['POST'])
@check_if_token_required
@validate_json
@validate_schema(create_schema)
def create_indicator_impact():
    """ Creates a new indicator impact. """

    data = request.get_json()

    # Verify this value does not already exist.
    existing = IndicatorImpact.query.filter_by(value=data['value']).first()
    if existing:
        return error_response(409, 'Indicator impact already exists')

    # Create and add the new value.
    indicator_impact = IndicatorImpact(value=data['value'])
    db.session.add(indicator_impact)
    db.session.commit()

    response = jsonify(indicator_impact.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.read_indicator_impact',
                                           indicator_impact_id=indicator_impact.id)
    return response


"""
READ
"""


@bp.route('/indicators/impact/<int:indicator_impact_id>', methods=['GET'])
@check_if_token_required
def read_indicator_impact(indicator_impact_id):
    """ Gets a single indicator impact given its ID. """

    indicator_impact = IndicatorImpact.query.get(indicator_impact_id)
    if not indicator_impact:
        return error_response(404, 'Indicator impact ID not found')

    return jsonify(indicator_impact.to_dict())


@bp.route('/indicators/impact', methods=['GET'])
@check_if_token_required
def read_indicator_impacts():
    """ Gets a list of all the indicator impacts. """

    data = IndicatorImpact.query.all()
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


@bp.route('/indicators/impact/<int:indicator_impact_id>', methods=['PUT'])
@check_if_token_required
@validate_json
@validate_schema(update_schema)
def update_indicator_impact(indicator_impact_id):
    """ Updates an existing indicator impact. """

    data = request.get_json()

    # Verify the ID exists.
    indicator_impact = IndicatorImpact.query.get(indicator_impact_id)
    if not indicator_impact:
        return error_response(404, 'Indicator impact ID not found')

    # Verify this value does not already exist.
    existing = IndicatorImpact.query.filter_by(value=data['value']).first()
    if existing:
        return error_response(409, 'Indicator impact already exists')

    # Set the new value.
    indicator_impact.value = data['value']
    db.session.commit()

    response = jsonify(indicator_impact.to_dict())
    return response


"""
DELETE
"""


@bp.route('/indicators/impact/<int:indicator_impact_id>', methods=['DELETE'])
@check_if_token_required
def delete_indicator_impact(indicator_impact_id):
    """ Deletes an indicator impact. """

    indicator_impact = IndicatorImpact.query.get(indicator_impact_id)
    if not indicator_impact:
        return error_response(404, 'Indicator impact ID not found')

    try:
        db.session.delete(indicator_impact)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        return error_response(409, 'Unable to delete indicator impact due to foreign key constraints')

    return '', 204
