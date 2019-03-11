from flask import jsonify, request, url_for
from sqlalchemy import exc

from project import db
from project.api import bp
from project.api.decorators import check_apikey, validate_json, validate_schema
from project.api.errors import error_response
from project.api.schemas import value_create, value_update
from project.models import IndicatorConfidence

"""
CREATE
"""


@bp.route('/indicators/confidence', methods=['POST'])
@check_apikey
@validate_json
@validate_schema(value_create)
def create_indicator_confidence():
    """ Creates a new indicator confidence.
    
    .. :quickref: IndicatorConfidence; Creates a new indicator confidence.

    **Example request**:

    .. sourcecode:: http

      POST /indicators/confidence HTTP/1.1
      Host: 127.0.0.1
      Content-Type: application/json

      {
        "value": "LOW"
      }

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 201 Created
      Content-Type: application/json

      {
        "id": 1,
        "value": "LOW"
      }

    :reqheader Authorization: Optional Apikey value
    :resheader Content-Type: application/json
    :status 201: Indicator confidence created
    :status 400: JSON does not match the schema
    :status 401: Invalid role to perform this action
    :status 409: Indicator confidence already exists
    """

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
@check_apikey
def read_indicator_confidence(indicator_confidence_id):
    """ Gets a single indicator confidence given its ID.
    
    .. :quickref: IndicatorConfidence; Gets a single indicator confidence given its ID.

    **Example request**:

    .. sourcecode:: http

      GET /indicators/confidence/1 HTTP/1.1
      Host: 127.0.0.1
      Accept: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "id": 1,
        "value": "LOW"
      }

    :reqheader Authorization: Optional Apikey value
    :resheader Content-Type: application/json
    :status 200: Indicator confidence found
    :status 401: Invalid role to perform this action
    :status 404: Indicator confidence ID not found
    """

    indicator_confidence = IndicatorConfidence.query.get(indicator_confidence_id)
    if not indicator_confidence:
        return error_response(404, 'Indicator confidence ID not found')

    return jsonify(indicator_confidence.to_dict())


@bp.route('/indicators/confidence', methods=['GET'])
@check_apikey
def read_indicator_confidences():
    """ Gets a list of all the indicator confidences.
    
    .. :quickref: IndicatorConfidence; Gets a list of all the indicator confidences.

    **Example request**:

    .. sourcecode:: http

      GET /indicators/confidence HTTP/1.1
      Host: 127.0.0.1
      Accept: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      [
        {
          "id": 1,
          "value": "LOW"
        },
        {
          "id": 2,
          "value": "HIGH"
        }
      ]

    :reqheader Authorization: Optional Apikey value
    :resheader Content-Type: application/json
    :status 200: Indicator confidences found
    :status 401: Invalid role to perform this action
    """

    data = IndicatorConfidence.query.all()
    return jsonify([item.to_dict() for item in data])


"""
UPDATE
"""


@bp.route('/indicators/confidence/<int:indicator_confidence_id>', methods=['PUT'])
@check_apikey
@validate_json
@validate_schema(value_update)
def update_indicator_confidence(indicator_confidence_id):
    """ Updates an existing indicator confidence.
    
    .. :quickref: IndicatorConfidence; Updates an existing indicator confidence.

    **Example request**:

    .. sourcecode:: http

      PUT /indicators/confidence/1 HTTP/1.1
      Host: 127.0.0.1
      Content-Type: application/json

      {
        "value": "HIGH",
      }

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "id": 1,
        "value": "HIGH"
      }

    :reqheader Authorization: Optional Apikey value
    :resheader Content-Type: application/json
    :status 200: Indicator confidence updated
    :status 400: JSON does not match the schema
    :status 401: Invalid role to perform this action
    :status 404: Indicator confidence ID not found
    :status 409: Indicator confidence already exists
    """

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
@check_apikey
def delete_indicator_confidence(indicator_confidence_id):
    """ Deletes an indicator confidence.
    
    .. :quickref: IndicatorConfidence; Deletes an indicator confidence.

    **Example request**:

    .. sourcecode:: http

      DELETE /indicators/confidence/1 HTTP/1.1
      Host: 127.0.0.1

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 204 No Content

    :reqheader Authorization: Optional Apikey value
    :status 204: Indicator confidence deleted
    :status 401: Invalid role to perform this action
    :status 404: Indicator confidence ID not found
    :status 409: Unable to delete indicator confidence due to foreign key constraints
    """

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
