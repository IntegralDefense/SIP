import uuid

from flask import jsonify, request, url_for

from project import db
from project.api import bp
from project.api.decorators import check_apikey
from project.api.errors import error_response
from project.models import IntelReference, IntelSource, User


"""
CREATE
"""


@bp.route('/intel/reference', methods=['POST'])
@check_apikey
def create_intel_reference():
    """ Creates a new intel reference. """

    data = request.values or {}

    # Verify the required fields (apikey, reference, and source) are present.
    if 'apikey' not in data or 'reference' not in data or 'source' not in data:
        return error_response(400, 'Request must include: apikey, reference, source')

    # Verify the source already exists.
    source = IntelSource.query.filter_by(value=data['source']).first()
    if not source:
        return error_response(400, 'Intel source not found')

    # Verify this reference does not already exist.
    existing = IntelReference.query.filter_by(reference=data['reference'], source=source).first()
    if existing:
        return error_response(409, 'Intel reference already exists')

    # Get the API key if there is one.
    apikey = None
    if 'apikey' in request.values:
        try:
            apikey = uuid.UUID(data['apikey'])
        except ValueError:
            pass

    # If there is an API key, look it up and get the user.
    if apikey:
        user = db.session.query(User).filter_by(apikey=apikey).first()

        # If the user exists, create and add the new reference.
        if user:
            intel_reference = IntelReference(reference=data['reference'], source=source, user=user)
            db.session.add(intel_reference)
            db.session.commit()

            response = jsonify(intel_reference.to_dict())
            response.status_code = 201
            response.headers['Location'] = url_for('api.read_intel_reference', intel_reference_id=intel_reference.id)
            return response
        else:
            return error_response(401, 'API user does not exist')
    else:
        return error_response(401, 'Bad or missing API key')


"""
READ
"""


@bp.route('/intel/reference/<int:intel_reference_id>', methods=['GET'])
@check_apikey
def read_intel_reference(intel_reference_id):
    """ Gets a single intel reference given its ID. """

    intel_reference = IntelReference.query.get(intel_reference_id)
    if not intel_reference:
        return error_response(404, 'Intel reference ID not found')

    return jsonify(intel_reference.to_dict())


@bp.route('/intel/reference', methods=['GET'])
@check_apikey
def read_intel_references():
    """ Gets a list of all the intel references. """

    data = IntelReference.query.all()
    return jsonify([item.to_dict() for item in data])


"""
UPDATE
"""


@bp.route('/intel/reference/<int:intel_reference_id>', methods=['PUT'])
@check_apikey
def update_intel_reference(intel_reference_id):
    """ Updates an existing intel reference. """

    data = request.values or {}

    # Verify the ID exists.
    intel_reference = IntelReference.query.get(intel_reference_id)
    if not intel_reference:
        return error_response(404, 'Intel reference ID not found')

    # Ensure at least reference or source was specified.
    if 'reference' not in data and 'source' not in data:
        return error_response(400, 'Request must include at least reference or source')

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
@check_apikey
def delete_intel_reference(intel_reference_id):
    """ Deletes an intel reference. """

    intel_reference = IntelReference.query.get(intel_reference_id)
    if not intel_reference:
        return error_response(404, 'Intel reference ID not found')

    db.session.delete(intel_reference)
    db.session.commit()

    return '', 204
