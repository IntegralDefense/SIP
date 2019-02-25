import datetime

from dateutil.parser import parse
from flask import current_app, jsonify, request, url_for
from sqlalchemy import and_, exc

from project import db
from project.api import bp
from project.api.decorators import check_if_token_required, validate_json, validate_schema
from project.api.errors import error_response
from project.api.helpers import parse_boolean
from project.models import Campaign, Indicator, IndicatorConfidence, IndicatorImpact, IndicatorStatus, IndicatorType, \
    IntelReference, IntelSource, Tag, User

"""
CREATE
"""

create_schema = {
    'type': 'object',
    'properties': {
        'campaigns': {
            'type': 'array',
            'items': {'type': 'string', 'minLength': 1, 'maxLength': 255},
            'minItems': 1
        },
        'case_sensitive': {'type': 'boolean'},
        'confidence': {'type': 'string', 'minLength': 1, 'maxLength': 255},
        'impact': {'type': 'string', 'minLength': 1, 'maxLength': 255},
        'references': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'source': {'type': 'string', 'minLength': 1, 'maxLength': 255},
                    'reference': {'type': 'string', 'minLength': 1, 'maxLength': 512},
                },
                'required': ['source', 'reference'],
                'additionalProperties': False
            },
            'minItems': 1
        },
        'status': {'type': 'string', 'minLength': 1, 'maxLength': 255},
        'substring': {'type': 'boolean'},
        'tags': {
            'type': 'array',
            'items': {'type': 'string', 'minLength': 1, 'maxLength': 255},
            'minItems': 1
        },
        'type': {'type': 'string', 'minLength': 1, 'maxLength': 255},
        'username': {'type': 'string', 'minLength': 1, 'maxLength': 255},
        'value': {'type': 'string', 'minLength': 1, 'maxLength': 512}
    },
    'required': ['username', 'type', 'value'],
    'additionalProperties': False
}


@bp.route('/indicators', methods=['POST'])
@check_if_token_required
@validate_json
@validate_schema(create_schema)
def create_indicator():
    """ Creates a new indicator. """

    data = request.get_json()

    # Verify the username.
    user = User.query.filter_by(username=data['username']).first()
    if not user:
        return error_response(404, 'User username not found: {}'.format(data['username']))

    # Verify the user is active.
    if not user.active:
        return error_response(401, 'Cannot create an indicator with an inactive user')

    # Verify the indicator type.
    indicator_type = IndicatorType.query.filter_by(value=data['type']).first()
    if not indicator_type:
        if current_app.config['INDICATOR_AUTO_CREATE_INDICATORTYPE']:
            indicator_type = IndicatorType(value=data['type'])
            db.session.add(indicator_type)
        else:
            return error_response(404, 'Indicator type not found: {}'.format(data['type']))

    # Verify this type+value does not already exist.
    existing = Indicator.query.filter_by(type=indicator_type, value=data['value']).first()
    if existing:
        return error_response(409, 'Indicator already exists')

    # Verify the case-sensitive value (defaults to False).
    if 'case_sensitive' in data:
        case_sensitive = data['case_sensitive']
    else:
        case_sensitive = False

    # Verify the confidence (has default).
    if 'confidence' not in data:
        confidence = IndicatorConfidence.query.order_by(IndicatorConfidence.id).limit(1).first()
        if not confidence:
            return error_response(400, 'No indicator confidence values exist to use as default')
    else:
        confidence = IndicatorConfidence.query.filter_by(value=data['confidence']).first()
        if not confidence:
            if current_app.config['INDICATOR_AUTO_CREATE_INDICATORCONFIDENCE']:
                confidence = IndicatorConfidence(value=data['confidence'])
                db.session.add(confidence)
            else:
                return error_response(404, 'Indicator confidence not found: {}'.format(data['confidence']))

    # Verify the impact (has default).
    if 'impact' not in data:
        impact = IndicatorImpact.query.order_by(IndicatorImpact.id).limit(1).first()
        if not impact:
            return error_response(400, 'No indicator impact values exist to use as default')
    else:
        impact = IndicatorImpact.query.filter_by(value=data['impact']).first()
        if not impact:
            if current_app.config['INDICATOR_AUTO_CREATE_INDICATORIMPACT']:
                impact = IndicatorImpact(value=data['impact'])
                db.session.add(impact)
            else:
                return error_response(404, 'Indicator impact not found: {}'.format(data['impact']))

    # Verify the status (has default).
    if 'status' not in data:
        status = IndicatorStatus.query.order_by(IndicatorStatus.id).limit(1).first()
        if not status:
            return error_response(400, 'No indicator status values exist to use as default')
    else:
        status = IndicatorStatus.query.filter_by(value=data['status']).first()
        if not status:
            if current_app.config['INDICATOR_AUTO_CREATE_INDICATORSTATUS']:
                status = IndicatorStatus(value=data['status'])
                db.session.add(status)
            else:
                return error_response(404, 'Indicator status not found: {}'.format(data['status']))

    # Verify the substring value (defaults to False).
    if 'substring' in data:
        substring = data['substring']
    else:
        substring = False

    # Create the indicator object.
    indicator = Indicator(case_sensitive=case_sensitive,
                          confidence=confidence,
                          impact=impact,
                          status=status,
                          substring=substring,
                          type=indicator_type,
                          user=user,
                          value=data['value'])

    # Verify any campaign that was specified.
    if 'campaigns' in data:
        for value in data['campaigns']:
            campaign = Campaign.query.filter_by(name=value).first()
            if not campaign:
                if current_app.config['INDICATOR_AUTO_CREATE_CAMPAIGN']:
                    campaign = Campaign(name=value)
                    db.session.add(campaign)
                else:
                    return error_response(404, 'Campaign not found: {}'.format(value))

            indicator.campaigns.append(campaign)

    # Verify any references that were specified.
    if 'references' in data:
        for item in data['references']:
            reference = IntelReference.query.filter(and_(IntelReference.reference == item['reference'],
                                                         IntelReference.source.has(
                                                             IntelSource.value == item['source']))).first()
            if not reference:
                if current_app.config['INDICATOR_AUTO_CREATE_INTELREFERENCE']:
                    source = IntelSource.query.filter_by(value=item['source']).first()
                    if not source:
                        source = IntelSource(value=item['source'])
                        db.session.add(source)

                    reference = IntelReference(reference=item['reference'], source=source, user=user)
                    db.session.add(reference)
                else:
                    return error_response(404, 'Intel reference not found: {}'.format(item['reference']))

            indicator.references.append(reference)

    # Verify any tags that were specified.
    if 'tags' in data:
        for value in data['tags']:
            tag = Tag.query.filter_by(value=value).first()
            if not tag:
                if current_app.config['INDICATOR_AUTO_CREATE_TAG']:
                    tag = Tag(value=value)
                    db.session.add(tag)
                else:
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
@check_if_token_required
def read_indicator(indicator_id):
    """ Gets a single indicator given its ID. """

    indicator = Indicator.query.get(indicator_id)
    if not indicator:
        return error_response(404, 'Indicator ID not found')

    return jsonify(indicator.to_dict())


@bp.route('/indicators', methods=['GET'])
@check_if_token_required
def read_indicators():
    """ Gets a paginated list of indicators based on various filter criteria. """

    filters = set()

    # Case-sensitive filter
    if 'case_sensitive' in request.args:
        arg = parse_boolean(request.args.get('case_sensitive'), default=None)
        filters.add(Indicator.case_sensitive.is_(arg))

    # Created after filter
    if 'created_after' in request.args:
        try:
            created_after = parse(request.args.get('created_after'), ignoretz=True)
        except (ValueError, OverflowError):
            created_after = datetime.date.max
        filters.add(created_after < Indicator.created_time)

    # Created before filter
    if 'created_before' in request.args:
        try:
            created_before = parse(request.args.get('created_before'), ignoretz=True)
        except (ValueError, OverflowError):
            created_before = datetime.date.min
        filters.add(Indicator.created_time < created_before)

    # Confidence filter
    if 'confidence' in request.args:
        filters.add(Indicator.confidence.has(IndicatorConfidence.value == request.args.get('confidence')))

    # Impact filter
    if 'impact' in request.args:
        filters.add(Indicator.impact.has(IndicatorImpact.value == request.args.get('impact')))

    # Modified after filter
    if 'modified_after' in request.args:
        try:
            modified_after = parse(request.args.get('modified_after'))
        except (ValueError, OverflowError):
            modified_after = datetime.date.max
        filters.add(modified_after < Indicator.modified_time)

    # Modified before filter
    if 'modified_before' in request.args:
        try:
            modified_before = parse(request.args.get('modified_before'))
        except (ValueError, OverflowError):
            modified_before = datetime.date.min
        filters.add(Indicator.modified_time < modified_before)

    # Source filter (IntelReference)
    if 'sources' in request.args:
        sources = request.args.get('sources').split(',')
        for s in sources:
            filters.add(Indicator.references.any(IntelReference.source.has(IntelSource.value == s)))

    # Status filter
    if 'status' in request.args:
        filters.add(Indicator.status.has(IndicatorStatus.value == request.args.get('status')))

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
        filters.add(Indicator.type.has(IndicatorType.value == request.args.get('type')))

    # Value filter
    if 'value' in request.args:
        filters.add(Indicator.value.like('%{}%'.format(request.args.get('value'))))

    data = Indicator.to_collection_dict(Indicator.query.filter(*filters), 'api.read_indicators', **request.args)
    return jsonify(data)


"""
UPDATE
"""

update_schema = {
    'type': 'object',
    'properties': {
        'campaigns': {
            'type': 'array',
            'items': {'type': 'string', 'minLength': 1, 'maxLength': 255},
            'minItems': 1
        },
        'case_sensitive': {'type': 'boolean'},
        'confidence': {'type': 'string', 'minLength': 1, 'maxLength': 255},
        'impact': {'type': 'string', 'minLength': 1, 'maxLength': 255},
        'references': {
            'type': 'array',
            'items': {'type': 'string', 'minLength': 1, 'maxLength': 512},
            'minItems': 1
        },
        'status': {'type': 'string', 'minLength': 1, 'maxLength': 255},
        'substring': {'type': 'boolean'},
        'tags': {
            'type': 'array',
            'items': {'type': 'string', 'minLength': 1, 'maxLength': 255},
            'minItems': 1
        },
        'username': {'type': 'string', 'minLength': 1, 'maxLength': 255}
    },
    'additionalProperties': False
}


@bp.route('/indicators/<indicator_id>', methods=['PUT'])
@check_if_token_required
@validate_json
@validate_schema(update_schema)
def update_indicator(indicator_id):
    """ Updates an existing indicator. """

    data = request.get_json()

    # Verify the ID exists.
    indicator = Indicator.query.get(indicator_id)
    if not indicator:
        return error_response(404, 'Indicator ID not found')

    # Verify campaigns if it was specified.
    if 'campaigns' in data:
        valid_campaigns = []
        for value in data['campaigns']:

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
    if 'references' in data:
        valid_references = []
        for value in data['references']:

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
    if 'tags' in data:
        valid_tags = []
        for value in data['tags']:

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
@check_if_token_required
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
