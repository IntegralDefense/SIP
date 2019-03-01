from flask import jsonify, request, url_for
from sqlalchemy import exc

from project import db
from project.api import bp
from project.api.decorators import check_if_token_required, validate_json, validate_schema
from project.api.errors import error_response
from project.api.schemas import value_create, value_update
from project.models import AlertType

"""
CREATE
"""


@bp.route('/alerts/type', methods=['POST'])
@check_if_token_required
@validate_json
@validate_schema(value_create)
def create_alert_type():
    """ Creates a new alert type.

    .. :quickref: AlertType; Creates a new alert type.

    **Example request**:

    .. sourcecode:: http

      POST /api/alerts/type HTTP/1.1
      Host: 127.0.0.1
      Content-Type: application/json

      {
        "value": "SIEM"
      }

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 201 Created
      Content-Type: application/json

      {
        "id": 1,
        "value": "SIEM"
      }

    :reqheader Authorization: Optional JWT Bearer token
    :resheader Content-Type: application/json
    :status 201: Alert type created
    :status 400: JSON does not match the schema
    :status 401: Invalid role to perform this action
    :status 409: Alert type already exists
    """

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
    """ Gets a single alert type given its ID.

    .. :quickref: AlertType; Gets a single alert type given its ID.

    **Example request**:

    .. sourcecode:: http

      GET /api/alerts/type/1 HTTP/1.1
      Host: 127.0.0.1
      Accept: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "id": 1,
        "value": "SIEM"
      }

    :reqheader Authorization: Optional JWT Bearer token
    :resheader Content-Type: application/json
    :status 200: Alert type found
    :status 401: Invalid role to perform this action
    :status 404: Alert type ID not found
    """

    alert_type = AlertType.query.get(alert_type_id)
    if not alert_type:
        return error_response(404, 'Alert type ID not found')

    return jsonify(alert_type.to_dict())


@bp.route('/alerts/type', methods=['GET'])
@check_if_token_required
def read_alert_types():
    """ Gets a list of all the alert types.

    .. :quickref: AlertType; Gets a list of all the alert types.

    **Example request**:

    .. sourcecode:: http

      GET /api/alerts/type HTTP/1.1
      Host: 127.0.0.1
      Accept: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      [
        {
          "id": 1,
          "value": "SIEM"
        },
        {
          "id": 2,
          "value": "SIEM 2"
        }
      ]

    :reqheader Authorization: Optional JWT Bearer token
    :resheader Content-Type: application/json
    :status 200: Alert types found
    :status 401: Invalid role to perform this action
    """

    data = AlertType.query.all()
    return jsonify([item.to_dict() for item in data])


"""
UPDATE
"""


@bp.route('/alerts/type/<int:alert_type_id>', methods=['PUT'])
@check_if_token_required
@validate_json
@validate_schema(value_update)
def update_alert_type(alert_type_id):
    """ Updates an existing alert type.

    .. :quickref: AlertType; Updates an existing alert type.

    **Example request**:

    .. sourcecode:: http

      PUT /api/alerts/type/1 HTTP/1.1
      Host: 127.0.0.1
      Content-Type: application/json

      {
        "value": "SIEM 2",
      }

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "id": 1,
        "value": "SIEM 2"
      }

    :reqheader Authorization: Optional JWT Bearer token
    :resheader Content-Type: application/json
    :status 200: Alert type updated
    :status 400: JSON does not match the schema
    :status 401: Invalid role to perform this action
    :status 404: Alert type ID not found
    :status 409: Alert type already exists
    """

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
    """ Deletes an alert type.

    .. :quickref: AlertType; Deletes an alert type.

    **Example request**:

    .. sourcecode:: http

      DELETE /api/alerts/type/1 HTTP/1.1
      Host: 127.0.0.1

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 204 No Content

    :reqheader Authorization: Optional JWT Bearer token
    :status 204: Alert type deleted
    :status 401: Invalid role to perform this action
    :status 404: Alert type ID not found
    :status 409: Unable to delete alert type due to foreign key constraints
    """

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
