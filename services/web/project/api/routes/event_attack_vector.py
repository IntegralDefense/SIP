from flask import jsonify, request, url_for
from sqlalchemy import exc

from project import db
from project.api import bp
from project.api.decorators import check_if_token_required, validate_json, validate_schema
from project.api.errors import error_response
from project.models import EventAttackVector

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


@bp.route('/events/attackvector', methods=['POST'])
@check_if_token_required
@validate_json
@validate_schema(create_schema)
def create_event_attack_vector():
    """ Creates a new event attack vector. """

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
    """ Gets a single event attack vector given its ID. """

    event_attack_vector = EventAttackVector.query.get(event_attack_vector_id)
    if not event_attack_vector:
        return error_response(404, 'Event attack vector ID not found')

    return jsonify(event_attack_vector.to_dict())


@bp.route('/events/attackvector', methods=['GET'])
@check_if_token_required
def read_event_attack_vectors():
    """ Gets a list of all the event attack vectors. """

    data = EventAttackVector.query.all()
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


@bp.route('/events/attackvector/<int:event_attack_vector_id>', methods=['PUT'])
@check_if_token_required
@validate_json
@validate_schema(update_schema)
def update_event_attack_vector(event_attack_vector_id):
    """ Updates an existing event attack vector. """

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
    """ Deletes an event attack vector. """

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
