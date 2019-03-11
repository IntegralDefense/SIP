from flask import jsonify, request, url_for
from sqlalchemy import exc

from project import db
from project.api import bp
from project.api.decorators import check_apikey, validate_json, validate_schema
from project.api.errors import error_response
from project.api.schemas import value_create, value_update
from project.models import IndicatorStatus

"""
CREATE
"""


@bp.route('/indicators/status', methods=['POST'])
@check_apikey
@validate_json
@validate_schema(value_create)
def create_indicator_status():
    """ Creates a new indicator status.
    
    .. :quickref: IndicatorStatus; Creates a new indicator status.

    **Example request**:

    .. sourcecode:: http

      POST /indicators/status HTTP/1.1
      Host: 127.0.0.1
      Content-Type: application/json

      {
        "value": "New"
      }

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 201 Created
      Content-Type: application/json

      {
        "id": 1,
        "value": "New"
      }

    :reqheader Authorization: Optional Apikey value
    :resheader Content-Type: application/json
    :status 201: Indicator status created
    :status 400: JSON does not match the schema
    :status 401: Invalid role to perform this action
    :status 409: Indicator status already exists
    """

    data = request.get_json()

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
    """ Gets a single indicator status given its ID.
    
    .. :quickref: IndicatorStatus; Gets a single indicator status given its ID.

    **Example request**:

    .. sourcecode:: http

      GET /indicators/status/1 HTTP/1.1
      Host: 127.0.0.1
      Accept: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "id": 1,
        "value": "New"
      }

    :reqheader Authorization: Optional Apikey value
    :resheader Content-Type: application/json
    :status 200: Indicator status found
    :status 401: Invalid role to perform this action
    :status 404: Indicator status ID not found
    """

    indicator_status = IndicatorStatus.query.get(indicator_status_id)
    if not indicator_status:
        return error_response(404, 'Indicator status ID not found')

    return jsonify(indicator_status.to_dict())


@bp.route('/indicators/status', methods=['GET'])
@check_apikey
def read_indicator_statuses():
    """ Gets a list of all the indicator statuses.
    
    .. :quickref: IndicatorStatus; Gets a list of all the indicator statuses.

    **Example request**:

    .. sourcecode:: http

      GET /indicators/status HTTP/1.1
      Host: 127.0.0.1
      Accept: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      [
        {
          "id": 1,
          "value": "New"
        },
        {
          "id": 2,
          "value": "Informational"
        }
      ]

    :reqheader Authorization: Optional Apikey value
    :resheader Content-Type: application/json
    :status 200: Indicator statuses found
    :status 401: Invalid role to perform this action
    """

    data = IndicatorStatus.query.all()
    return jsonify([item.to_dict() for item in data])


"""
UPDATE
"""


@bp.route('/indicators/status/<int:indicator_status_id>', methods=['PUT'])
@check_apikey
@validate_json
@validate_schema(value_update)
def update_indicator_status(indicator_status_id):
    """ Updates an existing indicator status.
    
    .. :quickref: IndicatorStatus; Updates an existing indicator status.

    **Example request**:

    .. sourcecode:: http

      PUT /indicators/status/1 HTTP/1.1
      Host: 127.0.0.1
      Content-Type: application/json

      {
        "value": "Informational",
      }

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "id": 1,
        "value": "Informational"
      }

    :reqheader Authorization: Optional Apikey value
    :resheader Content-Type: application/json
    :status 200: Indicator status updated
    :status 400: JSON does not match the schema
    :status 401: Invalid role to perform this action
    :status 404: Indicator status ID not found
    :status 409: Indicator status already exists
    """

    data = request.get_json()

    # Verify the ID exists.
    indicator_status = IndicatorStatus.query.get(indicator_status_id)
    if not indicator_status:
        return error_response(404, 'Indicator status ID not found')

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
    """ Deletes an indicator status.
    
    .. :quickref: IndicatorStatus; Deletes an indicator status.

    **Example request**:

    .. sourcecode:: http

      DELETE /indicators/status/1 HTTP/1.1
      Host: 127.0.0.1

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 204 No Content

    :reqheader Authorization: Optional Apikey value
    :status 204: Indicator status deleted
    :status 401: Invalid role to perform this action
    :status 404: Indicator status ID not found
    :status 409: Unable to delete indicator status due to foreign key constraints
    """

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
