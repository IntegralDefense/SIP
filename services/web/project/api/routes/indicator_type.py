from flask import jsonify, request, url_for
from sqlalchemy import exc

from project import db
from project.api import bp
from project.api.decorators import check_apikey, validate_json, validate_schema
from project.api.errors import error_response
from project.api.schemas import value_create, value_update
from project.models import IndicatorType

"""
CREATE
"""


@bp.route('/indicators/type', methods=['POST'])
@check_apikey
@validate_json
@validate_schema(value_create)
def create_indicator_type():
    """ Creates a new indicator type.
    
    .. :quickref: IndicatorType; Creates a new indicator type.

    **Example request**:

    .. sourcecode:: http

      POST /indicators/type HTTP/1.1
      Host: 127.0.0.1
      Content-Type: application/json

      {
        "value": "Email - Address"
      }

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 201 Created
      Content-Type: application/json

      {
        "id": 1,
        "value": "Email - Address"
      }

    :reqheader Authorization: Optional Apikey value
    :resheader Content-Type: application/json
    :status 201: Indicator type created
    :status 400: JSON does not match the schema
    :status 401: Invalid role to perform this action
    :status 409: Indicator type already exists
    """

    data = request.get_json()

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
    """ Gets a single indicator type given its ID.
    
    .. :quickref: IndicatorType; Gets a single indicator type given its ID.

    **Example request**:

    .. sourcecode:: http

      GET /indicators/type/1 HTTP/1.1
      Host: 127.0.0.1
      Accept: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "id": 1,
        "value": "Email - Address"
      }

    :reqheader Authorization: Optional Apikey value
    :resheader Content-Type: application/json
    :status 200: Indicator type found
    :status 401: Invalid role to perform this action
    :status 404: Indicator type ID not found
    """

    indicator_type = IndicatorType.query.get(indicator_type_id)
    if not indicator_type:
        return error_response(404, 'Indicator type ID not found')

    return jsonify(indicator_type.to_dict())


@bp.route('/indicators/type', methods=['GET'])
@check_apikey
def read_indicator_types():
    """ Gets a list of all the indicator types.
    
    .. :quickref: IndicatorType; Gets a list of all the indicator types.

    **Example request**:

    .. sourcecode:: http

      GET /indicators/type HTTP/1.1
      Host: 127.0.0.1
      Accept: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      [
        {
          "id": 1,
          "value": "Email - Address"
        },
        {
          "id": 2,
          "value": "URI - Domain Name"
        }
      ]

    :reqheader Authorization: Optional Apikey value
    :resheader Content-Type: application/json
    :status 200: Indicator types found
    :status 401: Invalid role to perform this action
    """

    data = IndicatorType.query.all()
    return jsonify([item.to_dict() for item in data])


"""
UPDATE
"""


@bp.route('/indicators/type/<int:indicator_type_id>', methods=['PUT'])
@check_apikey
@validate_json
@validate_schema(value_update)
def update_indicator_type(indicator_type_id):
    """ Updates an existing indicator type.
    
    .. :quickref: IndicatorType; Updates an existing indicator type.

    **Example request**:

    .. sourcecode:: http

      PUT /indicators/type/1 HTTP/1.1
      Host: 127.0.0.1
      Content-Type: application/json

      {
        "value": "URI - Domain Name",
      }

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "id": 1,
        "value": "URI - Domain Name"
      }

    :reqheader Authorization: Optional Apikey value
    :resheader Content-Type: application/json
    :status 200: Indicator type updated
    :status 400: JSON does not match the schema
    :status 401: Invalid role to perform this action
    :status 404: Indicator type ID not found
    :status 409: Indicator type already exists
    """

    data = request.get_json()

    # Verify the ID exists.
    indicator_type = IndicatorType.query.get(indicator_type_id)
    if not indicator_type:
        return error_response(404, 'Indicator type ID not found')

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
    """ Deletes an indicator type.
    
    .. :quickref: IndicatorType; Deletes an indicator type.

    **Example request**:

    .. sourcecode:: http

      DELETE /indicators/type/1 HTTP/1.1
      Host: 127.0.0.1

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 204 No Content

    :reqheader Authorization: Optional Apikey value
    :status 204: Indicator type deleted
    :status 401: Invalid role to perform this action
    :status 404: Indicator type ID not found
    :status 409: Unable to delete indicator type due to foreign key constraints
    """

    indicator_type = IndicatorType.query.get(indicator_type_id)
    if not indicator_type:
        return error_response(404, 'Indicator type ID not found')

    try:
        db.session.delete(indicator_type)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        return error_response(409, 'Unable to delete indicator type due to foreign key constraints')

    return '', 204
