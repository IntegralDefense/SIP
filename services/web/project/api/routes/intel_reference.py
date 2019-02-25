from flask import current_app, jsonify, request, url_for
from sqlalchemy import and_, exc

from project import db
from project.api import bp
from project.api.decorators import check_if_token_required, validate_json, validate_schema
from project.api.errors import error_response
from project.models import IntelReference, IntelSource, User


"""
CREATE
"""

create_schema = {
    'type': 'object',
    'properties': {
        'reference': {'type': 'string', 'minLength': 1, 'maxLength': 512},
        'source': {'type': 'string', 'minLength': 1, 'maxLength': 255},
        'username': {'type': 'string', 'minLength': 1, 'maxLength': 255}
    },
    'required': ['reference', 'source', 'username'],
    'additionalProperties': False
}


@bp.route('/intel/reference', methods=['POST'])
@check_if_token_required
@validate_json
@validate_schema(create_schema)
def create_intel_reference():
    """ Creates a new intel reference. """

    data = request.get_json()

    # Verify the username exists.
    user = User.query.filter_by(username=data['username']).first()
    if not user:
        return error_response(404, 'User username not found: {}'.format(data['username']))

    # Verify the user is active.
    if not user.active:
        return error_response(401, 'Cannot create an intel reference with an inactive user')

    # Verify the intel source.
    source = IntelSource.query.filter_by(value=data['source']).first()
    if not source:
        if current_app.config['INTELREFERENCE_AUTO_CREATE_INTELSOURCE']:
            source = IntelSource(value=data['source'])
            db.session.add(source)
        else:
            return error_response(404, 'Intel source not found: {}'.format(data['source']))

    # Verify this reference does not already exist.
    existing = IntelReference.query.filter(and_(IntelReference.reference == data['reference'],
                                                IntelReference.source.has(
                                                    IntelSource.value == source.value))).first()
    if existing:
        return error_response(409, 'Intel reference already exists')

    intel_reference = IntelReference(reference=data['reference'], source=source, user=user)
    db.session.add(intel_reference)
    db.session.commit()

    response = jsonify(intel_reference.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.read_intel_reference', intel_reference_id=intel_reference.id)
    return response


"""
READ
"""


@bp.route('/intel/reference/<int:intel_reference_id>', methods=['GET'])
@check_if_token_required
def read_intel_reference(intel_reference_id):
    """ Gets a single intel reference given its ID. """

    intel_reference = IntelReference.query.get(intel_reference_id)
    if not intel_reference:
        return error_response(404, 'Intel reference ID not found')

    return jsonify(intel_reference.to_dict())


@bp.route('/intel/reference', methods=['GET'])
@check_if_token_required
def read_intel_references():
    """ Gets a list of all the intel references. """

    data = IntelReference.query.all()
    return jsonify([item.to_dict() for item in data])


@bp.route('/intel/reference/<int:intel_reference_id>/indicators', methods=['GET'])
@check_if_token_required
def read_intel_reference_indicators(intel_reference_id):
    """ Gets a paginated list of the indicators associated with the intel reference """

    intel_reference = IntelReference.query.get(intel_reference_id)
    if not intel_reference:
        return error_response(404, 'Intel reference ID not found')

    # Inject the intel_reference_id parameter into the request arguments.
    # Also need to cast as a dict since request.args is a MultiDict, which causes issues in to_collection_dict.
    args = dict(request.args.copy())
    args['intel_reference_id'] = intel_reference.id

    data = IntelReference.to_collection_dict(intel_reference.indicators, 'api.read_intel_reference_indicators', **args)
    return jsonify(data)


"""
UPDATE
"""

update_schema = {
    'type': 'object',
    'properties': {
        'reference': {'type': 'string', 'minLength': 1, 'maxLength': 512},
        'source': {'type': 'string', 'minLength': 1, 'maxLength': 255},
        'username': {'type': 'string', 'minLength': 1, 'maxLength': 255}
    },
    'additionalProperties': False
}


@bp.route('/intel/reference/<int:intel_reference_id>', methods=['PUT'])
@check_if_token_required
@validate_json
@validate_schema(update_schema)
def update_intel_reference(intel_reference_id):
    """ Updates an existing intel reference. """

    data = request.get_json()

    # Verify the ID exists.
    intel_reference = IntelReference.query.get(intel_reference_id)
    if not intel_reference:
        return error_response(404, 'Intel reference ID not found')

    # Figure out if there was a reference specified.
    if 'reference' in data:
        reference = data['reference']
    else:
        reference = intel_reference.reference

    # Figure out if there was a source specified.
    if 'source' in data:
        source = IntelSource.query.filter_by(value=data['source']).first()
        if not source:
            return error_response(404, 'Intel source not found')
    else:
        source = intel_reference.source

    # Verify this reference+source does not already exist.
    existing = IntelReference.query.filter_by(reference=reference, source=source).first()
    if existing:
        return error_response(409, 'Intel reference already exists')

    # Verify username if one was specified.
    if 'username' in data:
        user = User.query.filter_by(username=data['username']).first()
        if not user:
            return error_response(404, 'Username not found: {}'.format(data['username']))

        if not user.active:
            return error_response(401, 'Cannot update an intel reference with an inactive user')

        intel_reference.user = user

    # Set the new values.
    intel_reference.reference = reference
    intel_reference.source = source
    db.session.commit()

    response = jsonify(intel_reference.to_dict())
    return response


"""
DELETE
"""


@bp.route('/intel/reference/<int:intel_reference_id>', methods=['DELETE'])
@check_if_token_required
def delete_intel_reference(intel_reference_id):
    """ Deletes an intel reference. """

    intel_reference = IntelReference.query.get(intel_reference_id)
    if not intel_reference:
        return error_response(404, 'Intel reference ID not found')

    try:
        db.session.delete(intel_reference)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        return error_response(409, 'Unable to delete intel reference due to foreign key constraints')

    return '', 204
