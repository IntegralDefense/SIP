from flask import jsonify, request, url_for
from sqlalchemy import exc

from project import db
from project.api import bp
from project.api.decorators import check_apikey, validate_json, validate_schema
from project.api.errors import error_response
from project.api.schemas import value_create, value_update
from project.models import IndicatorImpact

"""
CREATE
"""


@bp.route('/indicators/impact', methods=['POST'])
@check_apikey
@validate_json
@validate_schema(value_create)
def create_indicator_impact():
    """ Creates a new indicator impact.
    
    .. :quickref: IndicatorImpact; Creates a new indicator impact.

    **Example request**:

    .. sourcecode:: http

      POST /indicators/impact HTTP/1.1
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
    :status 201: Indicator impact created
    :status 400: JSON does not match the schema
    :status 401: Invalid role to perform this action
    :status 409: Indicator impact already exists
    """

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
@check_apikey
def read_indicator_impact(indicator_impact_id):
    """ Gets a single indicator impact given its ID.
    
    .. :quickref: IndicatorImpact; Gets a single indicator impact given its ID.

    **Example request**:

    .. sourcecode:: http

      GET /indicators/impact/1 HTTP/1.1
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
    :status 200: Indicator impact found
    :status 401: Invalid role to perform this action
    :status 404: Indicator impact ID not found
    """

    indicator_impact = IndicatorImpact.query.get(indicator_impact_id)
    if not indicator_impact:
        return error_response(404, 'Indicator impact ID not found')

    return jsonify(indicator_impact.to_dict())


@bp.route('/indicators/impact', methods=['GET'])
@check_apikey
def read_indicator_impacts():
    """ Gets a list of all the indicator impacts.
    
    .. :quickref: IndicatorImpact; Gets a list of all the indicator impacts.

    **Example request**:

    .. sourcecode:: http

      GET /indicators/impact HTTP/1.1
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
    :status 200: Indicator impacts found
    :status 401: Invalid role to perform this action
    """

    data = IndicatorImpact.query.all()
    return jsonify([item.to_dict() for item in data])


"""
UPDATE
"""


@bp.route('/indicators/impact/<int:indicator_impact_id>', methods=['PUT'])
@check_apikey
@validate_json
@validate_schema(value_update)
def update_indicator_impact(indicator_impact_id):
    """ Updates an existing indicator impact.
    
    .. :quickref: IndicatorImpact; Updates an existing indicator impact.

    **Example request**:

    .. sourcecode:: http

      PUT /indicators/impact/1 HTTP/1.1
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
    :status 200: Indicator impact updated
    :status 400: JSON does not match the schema
    :status 401: Invalid role to perform this action
    :status 404: Indicator impact ID not found
    :status 409: Indicator impact already exists
    """

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
@check_apikey
def delete_indicator_impact(indicator_impact_id):
    """ Deletes an indicator impact.
    
    .. :quickref: IndicatorImpact; Deletes an indicator impact.

    **Example request**:

    .. sourcecode:: http

      DELETE /indicators/impact/1 HTTP/1.1
      Host: 127.0.0.1

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 204 No Content

    :reqheader Authorization: Optional Apikey value
    :status 204: Indicator impact deleted
    :status 401: Invalid role to perform this action
    :status 404: Indicator impact ID not found
    :status 409: Unable to delete indicator impact due to foreign key constraints
    """

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
