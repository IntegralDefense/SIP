from flask import current_app, jsonify, request, url_for
from sqlalchemy import and_, exc

from project import db
from project.api import bp
from project.api.decorators import check_apikey, validate_json, validate_schema
from project.api.errors import error_response
from project.api.helpers import get_apikey
from project.api.schemas import intel_reference_create, intel_reference_update
from project.models import IntelReference, IntelSource, User


"""
CREATE
"""


@bp.route('/intel/reference', methods=['POST'])
@check_apikey
@validate_json
@validate_schema(intel_reference_create)
def create_intel_reference():
    """ Creates a new intel reference.

    .. :quickref: IntelReference; Creates a new intel reference.

    **Example request**:

    .. sourcecode:: http

      POST /intel/reference HTTP/1.1
      Host: 127.0.0.1
      Content-Type: application/json

      {
        "reference": "http://yourwiki.com/page-for-the-event",
        "source": "Your company",
        "username": "your_SIP_username"
      }

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 201 Created
      Content-Type: application/json

      {
        "id": 1,
        "reference": "http://yourwiki.com/page-for-the-event",
        "source": "Your company",
        "username": "your_SIP_username"
      }

    :reqheader Authorization: Optional Apikey value
    :resheader Content-Type: application/json
    :status 201: Intel reference created
    :status 400: JSON does not match the schema
    :status 401: Invalid role to perform this action
    :status 401: Username is inactive
    :status 401: You must supply either username or API key
    :status 404: Source not found
    :status 404: User not found by API key
    :status 404: Username not found
    :status 409: Intel reference already exists
    """

    data = request.get_json()

    # Verify the user exists.
    user = None
    if 'username' in data:
        user = User.query.filter_by(username=data['username']).first()
        if not user:
            return error_response(404, 'User not found by username')
    else:
        apikey = get_apikey(request)
        if apikey:
            user = User.query.filter_by(apikey=apikey).first()
            if not user:
                return error_response(404, 'User not found by API key')
        else:
            return error_response(401, 'You must supply either username or API key')

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
@check_apikey
def read_intel_reference(intel_reference_id):
    """ Gets a single intel reference given its ID.

    .. :quickref: IntelReference; Gets a single intel reference given its ID.

    **Example request**:

    .. sourcecode:: http

      GET /intel/reference/1 HTTP/1.1
      Host: 127.0.0.1
      Accept: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "id": 1,
        "reference": "http://yourwiki.com/page-for-the-event",
        "source": "Your company",
        "username": "your_SIP_username"
      }

    :reqheader Authorization: Optional Apikey value
    :resheader Content-Type: application/json
    :status 200: Intel source found
    :status 401: Invalid role to perform this action
    :status 404: Intel source ID not found
    """

    intel_reference = IntelReference.query.get(intel_reference_id)
    if not intel_reference:
        return error_response(404, 'Intel reference ID not found')

    return jsonify(intel_reference.to_dict())


@bp.route('/intel/reference', methods=['GET'])
@check_apikey
def read_intel_references():
    """ Gets a paginated list of all the intel references.

    .. :quickref: IntelReference; Gets a paginated list of all the intel references.

    **Example request**:

    .. sourcecode:: http

      GET /intel/reference HTTP/1.1
      Host: 127.0.0.1
      Accept: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "_links": {
          "next": null,
          "prev": null,
          "self": "/api/intel/reference?page=1&per_page=10"
        },
        "_meta": {
          "page": 1,
          "per_page": 10,
          "total_items": 3,
          "total_pages": 1
        },
        "items": [
          {
            "id": 1,
            "reference": "http://yourwiki.com/page-for-the-event",
            "source": "Your company",
            "user": "your_SIP_username"
          },
          {
            "id": 2,
            "reference": "http://yourwiki.com/event2",
            "source": "Your company",
            "user": "your_SIP_username"
          },
          {
            "id": 3,
            "reference": "http://somehelpfulblog.com/malware-analysis",
            "source": "OSINT",
            "user": "your_SIP_username"
          }
        ]
      }

    :reqheader Authorization: Optional Apikey value
    :resheader Content-Type: application/json
    :status 200: Intel references found
    :status 401: Invalid role to perform this action
    """

    filters = set()
    data = IntelReference.to_collection_dict(IntelReference.query.filter(*filters), 'api.read_intel_references', **request.args)
    return jsonify(data)


@bp.route('/intel/reference/<int:intel_reference_id>/indicators', methods=['GET'])
@check_apikey
def read_intel_reference_indicators(intel_reference_id):
    """ Gets a paginated list of the indicators associated with the intel reference.

    .. :quickref: Indicator; Gets a paginated list of the indicators associated with the intel reference.

    **Example request**:

    .. sourcecode:: http

      GET /intel/reference/1/indicators HTTP/1.1
      Host: 127.0.0.1
      Accept: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "_links": {
          "next": null,
          "prev": null,
          "self": "/api/intel/reference/1/indicators?page=1&per_page=10"
        },
        "_meta": {
          "page": 1,
          "per_page": 10,
          "total_items": 1,
          "total_pages": 1
        },
        "items": [
          {
            "all_children": [],
            "all_equal": [],
            "campaigns": [
              {
                "aliases": [],
                "created_time": "Thu, 28 Feb 2019 17:10:44 GMT",
                "id": 1,
                "modified_time": "Thu, 28 Feb 2019 17:10:44 GMT",
                "name": "LOLcats"
              },
              {
                "aliases": [],
                "created_time": "Fri, 01 Mar 2019 17:58:45 GMT",
                "id": 2,
                "modified_time": "Fri, 01 Mar 2019 17:58:45 GMT",
                "name": "Derpsters"
              }
            ],
            "case_sensitive": false,
            "children": [],
            "confidence": "LOW",
            "created_time": "Fri, 01 Mar 2019 18:00:51 GMT",
            "equal": [],
            "id": 2,
            "impact": "LOW",
            "modified_time": "Fri, 01 Mar 2019 18:00:51 GMT",
            "parent": null,
            "references": [
              {
                "id": 1,
                "reference": "http://yourwiki.com/page-for-the-event",
                "source": "Your company",
                "user": "your_SIP_username"
              },
              {
                "id": 3,
                "reference": "http://somehelpfulblog.com/malware-analysis",
                "source": "OSINT",
                "user": "your_SIP_username"
              }
            ],
            "status": "NEW",
            "substring": false,
            "tags": ["from_address", "phish"],
            "type": "Email - Address",
            "user": "your_SIP_username",
            "value": "badguy@evil.com"
          }
        ]
      }

    :reqheader Authorization: Optional Apikey value
    :resheader Content-Type: application/json
    :status 200: Indicators found
    :status 401: Invalid role to perform this action
    """

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


@bp.route('/intel/reference/<int:intel_reference_id>', methods=['PUT'])
@check_apikey
@validate_json
@validate_schema(intel_reference_update)
def update_intel_reference(intel_reference_id):
    """ Updates an existing intel reference.

    .. :quickref: IntelReference; Updates an existing intel reference.

    **Example request**:

    .. sourcecode:: http

      PUT /intel/source/1 HTTP/1.1
      Host: 127.0.0.1
      Content-Type: application/json

      {
        "reference": "d41d8cd98f00b204e9800998ecf8427e"
      }

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "id": 1,
        "reference": "d41d8cd98f00b204e9800998ecf8427e",
        "source": "Your company",
        "username": "your_SIP_username"
      }

    :reqheader Authorization: Optional Apikey value
    :resheader Content-Type: application/json
    :status 200: Intel reference updated
    :status 400: JSON does not match the schema
    :status 401: Invalid role to perform this action
    :status 401: Username is inactive
    :status 404: Intel reference ID not found
    :status 404: Intel source not found
    :status 404: Username not found
    :status 409: Intel reference already exists
    """

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
@check_apikey
def delete_intel_reference(intel_reference_id):
    """ Deletes an intel reference.

    .. :quickref: IntelReference; Deletes an intel reference.

    **Example request**:

    .. sourcecode:: http

      DELETE /intel/reference/1 HTTP/1.1
      Host: 127.0.0.1

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 204 No Content

    :reqheader Authorization: Optional Apikey value
    :status 204: Intel reference deleted
    :status 401: Invalid role to perform this action
    :status 404: Intel reference ID not found
    :status 409: Unable to delete intel reference due to foreign key constraints
    """

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
