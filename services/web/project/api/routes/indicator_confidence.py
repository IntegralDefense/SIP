from flask import jsonify, request, url_for
from sqlalchemy import exc

from project import db
from project.api import bp
from project.api.decorators import check_if_token_required, validate_json, validate_schema
from project.api.errors import error_response
from project.models import IndicatorConfidence

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


@bp.route('/indicators/confidence', methods=['POST'])
@check_if_token_required
@validate_json
@validate_schema(create_schema)
def create_indicator_confidence():
    """ Creates a new indicator confidence. """

    data = request.get_json()

    # Verify this value does not already exist.
    existing = IndicatorConfidence.query.filter_by(value=data['value']).first()
    if existing:
        return error_response(409, 'Indicator confidence already exists')

    # Create and add the new value.
    indicator_confidence = IndicatorConfidence(value=data['value'])
    db.session.add(indicator_confidence)
    db.session.commit()

    response = jsonify(indicator_confidence.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.read_indicator_confidence',
                                           indicator_confidence_id=indicator_confidence.id)
    return response


"""
READ
"""


@bp.route('/indicators/confidence/<int:indicator_confidence_id>', methods=['GET'])
@check_if_token_required
def read_indicator_confidence(indicator_confidence_id):
    """ Gets a single indicator confidence given its ID. """

    indicator_confidence = IndicatorConfidence.query.get(indicator_confidence_id)
    if not indicator_confidence:
        return error_response(404, 'Indicator confidence ID not found')

    return jsonify(indicator_confidence.to_dict())


@bp.route('/indicators/confidence', methods=['GET'])
@check_if_token_required
def read_indicator_confidences():
    """ Gets a list of all the indicator confidences. """

    data = IndicatorConfidence.query.all()
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


@bp.route('/indicators/confidence/<int:indicator_confidence_id>', methods=['PUT'])
@check_if_token_required
@validate_json
@validate_schema(update_schema)
def update_indicator_confidence(indicator_confidence_id):
    """ Updates an existing indicator confidence. """

    data = request.get_json()

    # Verify the ID exists.
    indicator_confidence = IndicatorConfidence.query.get(indicator_confidence_id)
    if not indicator_confidence:
        return error_response(404, 'Indicator confidence ID not found')

    # Verify this value does not already exist.
    existing = IndicatorConfidence.query.filter_by(value=data['value']).first()
    if existing:
        return error_response(409, 'Indicator confidence already exists')

    # Set the new value.
    indicator_confidence.value = data['value']
    db.session.commit()

    response = jsonify(indicator_confidence.to_dict())
    return response


"""
DELETE
"""


@bp.route('/indicators/confidence/<int:indicator_confidence_id>', methods=['DELETE'])
@check_if_token_required
def delete_indicator_confidence(indicator_confidence_id):
    """ Deletes an indicator confidence. """

    indicator_confidence = IndicatorConfidence.query.get(indicator_confidence_id)
    if not indicator_confidence:
        return error_response(404, 'Indicator confidence ID not found')

    try:
        db.session.delete(indicator_confidence)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        return error_response(409, 'Unable to delete indicator confidence due to foreign key constraints')

    return '', 204
