from flask import jsonify, request, url_for
from sqlalchemy import exc

from project import db
from project.api import bp
from project.api.decorators import check_apikey
from project.api.errors import error_response
from project.api.helpers import parse_boolean
from project.models import Campaign, Indicator, IndicatorConfidence, IndicatorImpact, IndicatorStatus, IndicatorType, \
    IntelReference, Tag, User

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
        return error_response(404, 'User username not found: {}'.format(data['username']))

    # Verify the user is active.
    if not user.active:
        return error_response(401, 'Cannot create an indicator with an inactive user')

    # Verify this type+value does not already exist.
    existing = Indicator.query.filter_by(_type_id=_type.id, value=data['value']).first()
    if existing:
        return error_response(409, 'Indicator already exists')

    # Create the indicator object.
    indicator = Indicator(type=_type,
                          user=user,
                          value=data['value'])

    # Verify any campaign that was specified.
    for value in data.getlist('campaigns'):
        campaign = Campaign.query.filter_by(name=value).first()
        if not campaign:
            return error_response(404, 'Campaign not found: {}'.format(value))
        indicator.campaigns.append(campaign)

    # Verify the case-sensitive value (defaults to False).
    if 'case_sensitive' in data:
        case_sensitive = parse_boolean(data['case_sensitive'])
    else:
        case_sensitive = False
    indicator.case_sensitive = case_sensitive

    # Verify the confidence (has default).
    if 'confidence' not in data:
        confidence = IndicatorConfidence.query.order_by(IndicatorConfidence.id).limit(1).first()
    else:
        confidence = IndicatorConfidence.query.filter_by(value=data['confidence']).first()
        if not confidence:
            return error_response(404, 'Indicator confidence not found: {}'.format(data['confidence']))
    indicator.confidence = confidence

    # Verify the impact (has default).
    if 'impact' not in data:
        impact = IndicatorImpact.query.order_by(IndicatorImpact.id).limit(1).first()
    else:
        impact = IndicatorImpact.query.filter_by(value=data['impact']).first()
        if not impact:
            return error_response(404, 'Indicator impact not found: {}'.format(data['impact']))
    indicator.impact = impact

    # Verify any reference that was specified.
    for value in data.getlist('references'):
        reference = IntelReference.query.filter_by(reference=value).first()
        if not reference:
            return error_response(404, 'Reference not found: {}'.format(value))
        indicator.references.append(reference)

    # Verify the status (has default).
    if 'status' not in data:
        status = IndicatorStatus.query.order_by(IndicatorStatus.id).limit(1).first()
    else:
        status = IndicatorStatus.query.filter_by(value=data['status']).first()
        if not status:
            return error_response(404, 'Indicator status not found: {}'.format(data['status']))
    indicator.status = status

    # Verify the substring value (defaults to False).
    if 'substring' in data:
        substring = parse_boolean(data['substring'])
    else:
        substring = False
    indicator.substring = substring

    # Verify any tags that were specified.
    for value in data.getlist('tags'):
        tag = Tag.query.filter_by(value=value).first()
        if not tag:
            return error_response(404, 'Tag not found: {}'.format(value))
        indicator.tags.append(tag)

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
        return error_response(404, 'Indicator ID not found')

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
        return error_response(404, 'Indicator ID not found')

    # Verify at least one required field was specified.
    required = ['campaigns', 'case_sensitive', 'confidence', 'impact', 'references', 'status', 'substring', 'tags',
                'username']
    if not any(r in data for r in required):
        return error_response(400, 'Request must include at least one of: {}'.format(', '.join(sorted(required))))

    # Verify campaigns if it was specified.
    valid_campaigns = []
    for value in data.getlist('campaigns'):

        # Verify each campaign is actually valid.
        campaign = Campaign.query.filter_by(name=value).first()
        if not campaign:
            error_response(404, 'Campaign not found: {}'.format(value))
        valid_campaigns.append(campaign)
    if valid_campaigns:
        indicator.campaigns = valid_campaigns

    # Verify case_sensitive if it was specified
    if 'case_sensitive' in data:
        indicator.case_sensitive = parse_boolean(data['case_sensitive'], default=False)

    # Verify confidence if it was specified
    if 'confidence' in data:
        confidence = IndicatorConfidence.query.filter_by(value=data['confidence']).first()
        if not confidence:
            return error_response(404, 'Indicator confidence not found: {}'.format(data['confidence']))
        indicator.confidence = confidence

    # Verify impact if it was specified
    if 'impact' in data:
        impact = IndicatorImpact.query.filter_by(value=data['impact']).first()
        if not impact:
            return error_response(404, 'Indicator impact not found: {}'.format(data['impact']))
        indicator.impact = impact

    # Verify references if it was specified.
    valid_references = []
    for value in data.getlist('references'):

        # Verify each reference is actually valid.
        reference = IntelReference.query.filter_by(reference=value).first()
        if not reference:
            error_response(404, 'Intel reference not found: {}'.format(value))
        valid_references.append(reference)
    if valid_references:
        indicator.references = valid_references

    # Verify status if it was specified
    if 'status' in data:
        status = IndicatorStatus.query.filter_by(value=data['status']).first()
        if not status:
            return error_response(404, 'Indicator status not found: {}'.format(data['status']))
        indicator.status = status

    # Verify substring if it was specified
    if 'substring' in data:
        indicator.substring = parse_boolean(data['substring'], default=False)

    # Verify tags if it was specified.
    valid_tags = []
    for value in data.getlist('tags'):

        # Verify each tag is actually valid.
        tag = Tag.query.filter_by(value=value).first()
        if not tag:
            error_response(404, 'Tag not found: {}'.format(value))
        valid_tags.append(tag)
    if valid_tags:
        indicator.tags = valid_tags

    # Verify username if one was specified.
    if 'username' in data:
        user = User.query.filter_by(username=data['username']).first()
        if not user:
            return error_response(404, 'User username not found: {}'.format(data['username']))

        if not user.active:
            return error_response(401, 'Cannot update an indicator with an inactive user')

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
        return error_response(404, 'Indicator ID not found')

    try:
        db.session.delete(indicator)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        return error_response(409, 'Unable to delete indicator due to foreign key constraints')

    return '', 204
