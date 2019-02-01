from flask import jsonify, request, url_for
from sqlalchemy import exc

from project import db
from project.api import bp
from project.api.decorators import check_apikey
from project.api.errors import error_response
from project.models import IntelSource

"""
CREATE
"""


@bp.route('/intel/source', methods=['POST'])
@check_apikey
def create_intel_source():
    """ Creates a new intel source. """

    data = request.values or {}

    # Verify the required fields (value) are present.
    if 'value' not in data:
        return error_response(400, 'Request must include "value"')

    # Verify this value does not already exist.
    existing = IntelSource.query.filter_by(value=data['value']).first()
    if existing:
        return error_response(409, 'Intel source already exists')

    # Create and add the new value.
    intel_source = IntelSource(value=data['value'])
    db.session.add(intel_source)
    db.session.commit()

    response = jsonify(intel_source.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.read_intel_source',
                                           intel_source_id=intel_source.id)
    return response


"""
READ
"""


@bp.route('/intel/source/<int:intel_source_id>', methods=['GET'])
@check_apikey
def read_intel_source(intel_source_id):
    """ Gets a single intel source given its ID. """

    intel_source = IntelSource.query.get(intel_source_id)
    if not intel_source:
        return error_response(404, 'Intel source ID not found')

    return jsonify(intel_source.to_dict())


@bp.route('/intel/source', methods=['GET'])
@check_apikey
def read_intel_sources():
    """ Gets a list of all the intel sources. """

    data = IntelSource.query.all()
    return jsonify([item.to_dict() for item in data])


"""
UPDATE
"""


@bp.route('/intel/source/<int:intel_source_id>', methods=['PUT'])
@check_apikey
def update_intel_source(intel_source_id):
    """ Updates an existing intel source. """

    data = request.values or {}

    # Verify the ID exists.
    intel_source = IntelSource.query.get(intel_source_id)
    if not intel_source:
        return error_response(404, 'Intel source ID not found')

    # Verify the required fields (value) are present.
    if 'value' not in data:
        return error_response(400, 'Request must include "value"')

    # Verify this value does not already exist.
    existing = IntelSource.query.filter_by(value=data['value']).first()
    if existing:
        return error_response(409, 'Intel source already exists')

    # Set the new value.
    intel_source.value = data['value']
    db.session.commit()

    response = jsonify(intel_source.to_dict())
    return response


"""
DELETE
"""


@bp.route('/intel/source/<int:intel_source_id>', methods=['DELETE'])
@check_apikey
def delete_intel_source(intel_source_id):
    """ Deletes an intel source. """

    intel_source = IntelSource.query.get(intel_source_id)
    if not intel_source:
        return error_response(404, 'Intel source ID not found')

    try:
        db.session.delete(intel_source)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        return error_response(409, 'Unable to delete intel source due to foreign key constraints')

    return '', 204
