from flask import jsonify, request, url_for
from sqlalchemy import exc

from project import db
from project.api import bp
from project.api.decorators import check_if_token_required, validate_json, validate_schema
from project.api.errors import error_response
from project.api.schemas import value_create, value_update
from project.models import EventAttackVector

"""
CREATE
"""


@bp.route('/events/attackvector', methods=['POST'])
@check_if_token_required
@validate_json
@validate_schema(value_create)
def create_event_attack_vector():
    """ Creates a new event attack vector.

    .. :quickref: EventAttackVector; Creates a new event attack vector.

    **Example request**:

    .. sourcecode:: http

      POST /events/attackvector HTTP/1.1
      Host: 127.0.0.1
      Content-Type: application/json

      {
        "value": "CORPORATE EMAIL"
      }

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 201 Created
      Content-Type: application/json

      {
        "id": 1,
        "value": "CORPORATE EMAIL"
      }

    :reqheader Authorization: Optional JWT Bearer token
    :resheader Content-Type: application/json
    :status 201: Event attack vector created
    :status 400: JSON does not match the schema
    :status 401: Invalid role to perform this action
    :status 409: Event attack vector already exists
    """

    data = request.get_json()

    # Verify this value does not already exist.
    existing = EventAttackVector.query.filter_by(value=data['value']).first()
    if existing:
        return error_response(409, 'Event attack vector already exists')

    # Create and add the new value.
    event_attack_vector = EventAttackVector(value=data['value'])
    db.session.add(event_attack_vector)
    db.session.commit()

    response = jsonify(event_attack_vector.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.read_event_attack_vector',
                                           event_attack_vector_id=event_attack_vector.id)
    return response


"""
READ
"""


@bp.route('/events/attackvector/<int:event_attack_vector_id>', methods=['GET'])
@check_if_token_required
def read_event_attack_vector(event_attack_vector_id):
    """ Gets a single event attack vector given its ID.

    .. :quickref: EventAttackVector; Gets a single event attack vector given its ID.

    **Example request**:

    .. sourcecode:: http

      GET /events/attackvector/1 HTTP/1.1
      Host: 127.0.0.1
      Accept: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "id": 1,
        "value": "CORPORATE EMAIL"
      }

    :reqheader Authorization: Optional JWT Bearer token
    :resheader Content-Type: application/json
    :status 200: Event attack vector found
    :status 401: Invalid role to perform this action
    :status 404: Event attack vector ID not found
    """

    event_attack_vector = EventAttackVector.query.get(event_attack_vector_id)
    if not event_attack_vector:
        return error_response(404, 'Event attack vector ID not found')

    return jsonify(event_attack_vector.to_dict())


@bp.route('/events/attackvector', methods=['GET'])
@check_if_token_required
def read_event_attack_vectors():
    """ Gets a list of all the event attack vectors.

    .. :quickref: EventAttackVector; Gets a list of all the event attack vectors.

    **Example request**:

    .. sourcecode:: http

      GET /events/attackvector HTTP/1.1
      Host: 127.0.0.1
      Accept: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      [
        {
          "id": 1,
          "value": "CORPORATE EMAIL"
        },
        {
          "id": 2,
          "value": "WEBMAIL"
        }
      ]

    :reqheader Authorization: Optional JWT Bearer token
    :resheader Content-Type: application/json
    :status 200: Event attack vectors found
    :status 401: Invalid role to perform this action
    """

    data = EventAttackVector.query.all()
    return jsonify([item.to_dict() for item in data])


"""
UPDATE
"""


@bp.route('/events/attackvector/<int:event_attack_vector_id>', methods=['PUT'])
@check_if_token_required
@validate_json
@validate_schema(value_update)
def update_event_attack_vector(event_attack_vector_id):
    """ Updates an existing event attack vector.

    .. :quickref: EventAttackVector; Updates an existing event attack vector.

    **Example request**:

    .. sourcecode:: http

      PUT /events/attackvector/1 HTTP/1.1
      Host: 127.0.0.1
      Content-Type: application/json

      {
        "value": "WEBMAIL",
      }

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "id": 1,
        "value": "WEBMAIL"
      }

    :reqheader Authorization: Optional JWT Bearer token
    :resheader Content-Type: application/json
    :status 200: Event attack vector updated
    :status 400: JSON does not match the schema
    :status 401: Invalid role to perform this action
    :status 404: Event attack vector ID not found
    :status 409: Event attack vector already exists
    """

    data = request.get_json()

    # Verify the ID exists.
    event_attack_vector = EventAttackVector.query.get(event_attack_vector_id)
    if not event_attack_vector:
        return error_response(404, 'Event attack vector ID not found')

    # Verify this value does not already exist.
    existing = EventAttackVector.query.filter_by(value=data['value']).first()
    if existing:
        return error_response(409, 'Event attack vector already exists')

    # Set the new value.
    event_attack_vector.value = data['value']
    db.session.commit()

    response = jsonify(event_attack_vector.to_dict())
    return response


"""
DELETE
"""


@bp.route('/events/attackvector/<int:event_attack_vector_id>', methods=['DELETE'])
@check_if_token_required
def delete_event_attack_vector(event_attack_vector_id):
    """ Deletes an event attack vector.

    .. :quickref: EventAttackVector; Deletes an event attack vector.

    **Example request**:

    .. sourcecode:: http

      DELETE /events/attackvector/1 HTTP/1.1
      Host: 127.0.0.1

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 204 No Content

    :reqheader Authorization: Optional JWT Bearer token
    :status 204: Event attack vector deleted
    :status 401: Invalid role to perform this action
    :status 404: Event attack vector ID not found
    :status 409: Unable to delete event attack vector due to foreign key constraints
    """

    event_attack_vector = EventAttackVector.query.get(event_attack_vector_id)
    if not event_attack_vector:
        return error_response(404, 'Event attack vector ID not found')

    try:
        db.session.delete(event_attack_vector)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        return error_response(409, 'Unable to delete event attack vector due to foreign key constraints')

    return '', 204
