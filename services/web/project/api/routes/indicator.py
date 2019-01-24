from flask import jsonify, request, url_for

from project import db
from project.api import bp
from project.api.decorators import check_apikey
from project.api.errors import error_response
from project.api.helpers import parse_boolean
from project.models import Indicator, IndicatorConfidence, IndicatorImpact, IndicatorStatus, IndicatorType, User


"""
CREATE
"""


@bp.route('/indicators', methods=['POST'])
@check_apikey
def create_indicator():
    """ Creates a new indicator. """

    data = request.values or {}

    # Verify the required fields (type, username, value) are present.
    if 'type' not in data or 'username' not in data or 'value' not in data:
        return error_response(400, 'Request must include: type, username, value')

    # Verify the type.
    _type = IndicatorType.query.filter_by(value=data['type']).first()
    if not _type:
        return error_response(404, 'Indicator type not found')

    # Verify the username.
    user = User.query.filter_by(username=data['username']).first()
    if not user:
        return error_response(404, 'User username not found')

    # Verify this type+value does not already exist.
    existing = Indicator.query.filter_by(_type_id=_type.id, value=data['value']).first()
    if existing:
        return error_response(409, 'Indicator already exists: {}'.format(existing.id),
                              url_for('api.read_indicator', indicator_id=existing.id))

    # Verify the case-sensitive value (defaults to False).
    if 'case_sensitive' in data:
        case_sensitive = parse_boolean(data['case_sensitive'])
    else:
        case_sensitive = False

    # Verify the confidence (has default).
    if 'confidence' not in data:
        confidence = IndicatorConfidence.query.order_by(IndicatorConfidence.id).limit(1).first()
    else:
        confidence = IndicatorConfidence.query.filter_by(value=data['confidence']).first()
        if not confidence:
            results = IndicatorConfidence.query.all()
            acceptable = sorted([r.value for r in results])
            return error_response(400, 'confidence must be one of: {}'.format(', '.join(acceptable)))

    # Verify the impact (has default).
    if 'impact' not in data:
        impact = IndicatorImpact.query.order_by(IndicatorImpact.id).limit(1).first()
    else:
        impact = IndicatorImpact.query.filter_by(value=data['impact']).first()
        if not impact:
            results = IndicatorImpact.query.all()
            acceptable = sorted([r.value for r in results])
            return error_response(400, 'impact must be one of: {}'.format(', '.join(acceptable)))

    # Verify the status (has default).
    if 'status' not in data:
        status = IndicatorStatus.query.order_by(IndicatorStatus.id).limit(1).first()
    else:
        status = IndicatorStatus.query.filter_by(value=data['status']).first()
        if not status:
            results = IndicatorStatus.query.all()
            acceptable = sorted([r.value for r in results])
            return error_response(400, 'status must be one of: {}'.format(', '.join(acceptable)))

    # Verify the substring value (defaults to False).
    if 'substring' in data:
        substring = parse_boolean(data['substring'])
    else:
        substring = False

    indicator = Indicator(case_sensitive=case_sensitive,
                          confidence=confidence,
                          impact=impact,
                          status=status,
                          substring=substring,
                          type=_type,
                          user=user,
                          value=data['value'])

    db.session.add(indicator)
    db.session.commit()

    response = jsonify(indicator.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.read_indicator', indicator_id=indicator.id)
    return response


"""
READ
"""


@bp.route('/indicators/<int:indicator_id>', methods=['GET'])
@check_apikey
def read_indicator(indicator_id):
    """ Gets a single indicator given its ID. """

    indicator = Indicator.query.get(indicator_id)
    if not indicator:
        return error_response(404, 'Indicator ID not found: {}'.format(indicator_id))

    return jsonify(indicator.to_dict())


@bp.route('/indicators', methods=['GET'])
@check_apikey
def read_indicators():
    """ Gets a paginated list of indicators based on various filter criteria. """

    filters = set()

    # Case-sensitive filter
    if 'case_sensitive' in request.args:
        arg = parse_boolean(request.args.get('case_sensitive'), default=None)
        filters.add(Indicator.case_sensitive.is_(arg))

    # Confidence filter
    if 'confidence' in request.args:
        confidence = IndicatorConfidence.query.filter_by(value=request.args.get('confidence')).first()
        if confidence:
            confidence_id = confidence.id
        else:
            confidence_id = -1
        filters.add(Indicator.confidence.id == confidence_id)

    # Impact filter
    if 'impact' in request.args:
        impact = IndicatorImpact.query.filter_by(value=request.args.get('impact')).first()
        if impact:
            impact_id = impact.id
        else:
            impact_id = -1
        filters.add(Indicator.impact.id == impact_id)

    # Status filter
    if 'status' in request.args:
        status = IndicatorStatus.query.filter_by(value=request.args.get('status')).first()
        if status:
            status_id = status.id
        else:
            status_id = -1
        filters.add(Indicator.status.id == status_id)

    # Substring filter
    if 'substring' in request.args:
        arg = parse_boolean(request.args.get('substring'), default=None)
        filters.add(Indicator.substring.is_(arg))

    # Tags filter
    if 'tags' in request.args:
        search_tags = request.args.get('tags').split(',')
        for search_tag in search_tags:
            filters.add(Indicator.tags.any(value=search_tag))

    # Type filter
    if 'type' in request.args:
        _type = IndicatorType.query.filter_by(value=request.args.get('type')).first()
        if _type:
            type_id = _type.id
        else:
            type_id = -1
        filters.add(Indicator.type.id == type_id)

    # Value filter
    if 'value' in request.args:
        filters.add(Indicator.value.like('%{}%'.format(request.args.get('value'))))

    data = Indicator.to_collection_dict(Indicator.query.filter(*filters), 'api.read_indicators', **request.args)
    return jsonify(data)


"""
UPDATE
"""


@bp.route('/indicators/<indicator_id>', methods=['PUT'])
@check_apikey
def update_indicator(indicator_id):
    """ Updates an existing indicator. """

    data = request.values or {}

    # Verify the ID exists.
    indicator = Indicator.query.get(indicator_id)
    if not indicator:
        return error_response(404, 'Indicator ID not found: {}'.format(indicator_id))

    # Verify at least one required field was specified.
    required = ['confidence', 'impact', 'status', 'username']
    if not any(r in data for r in required):
        return error_response(400, 'Request must include at least one of: {}'.format(', '.join(sorted(required))))

    # Verify the confidence.
    if 'confidence' in data:
        confidence = IndicatorConfidence.query.filter_by(value=data['confidence']).first()
        if not confidence:
            results = IndicatorConfidence.query.all()
            acceptable = sorted([r.value for r in results])
            return error_response(400, 'confidence must be one of: {}'.format(', '.join(acceptable)))
        indicator.confidence = confidence

    # Verify the impact.
    if 'impact' in data:
        impact = IndicatorImpact.query.filter_by(value=data['impact']).first()
        if not impact:
            results = IndicatorImpact.query.all()
            acceptable = sorted([r.value for r in results])
            return error_response(400, 'impact must be one of: {}'.format(', '.join(acceptable)))
        indicator.impact = impact

    # Verify the status.
    if 'status' in data:
        status = IndicatorStatus.query.filter_by(value=data['status']).first()
        if not status:
            results = IndicatorStatus.query.all()
            acceptable = sorted([r.value for r in results])
            return error_response(400, 'status must be one of: {}'.format(', '.join(acceptable)))
        indicator.status = status

    # Verify username if one was specified.
    if 'username' in data:
        user = User.query.filter_by(username=data['username'])
        if not user:
            return error_response(404, 'User username not found: {}'.format(data['username']))
        indicator.user = user

    db.session.commit()

    response = jsonify(indicator.to_dict())
    return response


"""
DELETE
"""


@bp.route('/indicators/<indicator_id>', methods=['DELETE'])
@check_apikey
def delete_indicator(indicator_id):
    """ Deletes an indicator """

    indicator = Indicator.query.get(indicator_id)
    if not indicator:
        return error_response(404, 'Indicator ID not found: {}'.format(indicator_id))

    db.session.delete(indicator)
    db.session.commit()

    return '', 204
