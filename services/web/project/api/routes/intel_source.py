from flask import jsonify, request, url_for
from sqlalchemy import exc

from project import db
from project.api import bp
from project.api.decorators import check_apikey, validate_json, validate_schema
from project.api.errors import error_response
from project.api.schemas import value_create, value_update
from project.models import IntelSource

"""
CREATE
"""


@bp.route('/intel/source', methods=['POST'])
@check_apikey
@validate_json
@validate_schema(value_create)
def create_intel_source():
    """ Creates a new intel source.
    
    .. :quickref: IntelSource; Creates a new intel source.

    **Example request**:

    .. sourcecode:: http

      POST /intel/source HTTP/1.1
      Host: 127.0.0.1
      Content-Type: application/json

      {
        "value": "OSINT"
      }

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 201 Created
      Content-Type: application/json

      {
        "id": 1,
        "value": "OSINT"
      }

    :reqheader Authorization: Optional Apikey value
    :resheader Content-Type: application/json
    :status 201: Intel source created
    :status 400: JSON does not match the schema
    :status 401: Invalid role to perform this action
    :status 409: Intel source already exists
    """

    data = request.get_json()

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
    """ Gets a single intel source given its ID.
    
    .. :quickref: IntelSource; Gets a single intel source given its ID.

    **Example request**:

    .. sourcecode:: http

      GET /intel/source/1 HTTP/1.1
      Host: 127.0.0.1
      Accept: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "id": 1,
        "value": "OSINT"
      }

    :reqheader Authorization: Optional Apikey value
    :resheader Content-Type: application/json
    :status 200: Intel source found
    :status 401: Invalid role to perform this action
    :status 404: Intel source ID not found
    """

    intel_source = IntelSource.query.get(intel_source_id)
    if not intel_source:
        return error_response(404, 'Intel source ID not found')

    return jsonify(intel_source.to_dict())


@bp.route('/intel/source', methods=['GET'])
@check_apikey
def read_intel_sources():
    """ Gets a list of all the intel sources.
    
    .. :quickref: IntelSource; Gets a list of all the intel sources.

    **Example request**:

    .. sourcecode:: http

      GET /intel/source HTTP/1.1
      Host: 127.0.0.1
      Accept: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      [
        {
          "id": 1,
          "value": "OSINT"
        },
        {
          "id": 2,
          "value": "VirusTotal"
        }
      ]

    :reqheader Authorization: Optional Apikey value
    :resheader Content-Type: application/json
    :status 200: Intel sources found
    :status 401: Invalid role to perform this action
    """

    data = IntelSource.query.all()
    return jsonify([item.to_dict() for item in data])


"""
UPDATE
"""


@bp.route('/intel/source/<int:intel_source_id>', methods=['PUT'])
@check_apikey
@validate_json
@validate_schema(value_update)
def update_intel_source(intel_source_id):
    """ Updates an existing intel source.
    
    .. :quickref: IntelSource; Updates an existing intel source.

    **Example request**:

    .. sourcecode:: http

      PUT /intel/source/1 HTTP/1.1
      Host: 127.0.0.1
      Content-Type: application/json

      {
        "value": "VirusTotal",
      }

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "id": 1,
        "value": "VirusTotal"
      }

    :reqheader Authorization: Optional Apikey value
    :resheader Content-Type: application/json
    :status 200: Intel source updated
    :status 400: JSON does not match the schema
    :status 401: Invalid role to perform this action
    :status 404: Intel source ID not found
    :status 409: Intel source already exists
    """

    data = request.get_json()

    # Verify the ID exists.
    intel_source = IntelSource.query.get(intel_source_id)
    if not intel_source:
        return error_response(404, 'Intel source ID not found')

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
    """ Deletes an intel source.
    
    .. :quickref: IntelSource; Deletes an intel source.

    **Example request**:

    .. sourcecode:: http

      DELETE /intel/source/1 HTTP/1.1
      Host: 127.0.0.1

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 204 No Content

    :reqheader Authorization: Optional Apikey value
    :status 204: Intel source deleted
    :status 401: Invalid role to perform this action
    :status 404: Intel source ID not found
    :status 409: Unable to delete intel source due to foreign key constraints
    """

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
