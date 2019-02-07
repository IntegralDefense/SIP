import datetime

from dateutil.parser import parse
from flask import jsonify, request, url_for
from sqlalchemy import exc

from project import db
from project.api import bp
from project.api.decorators import check_if_token_required, validate_json, validate_schema
from project.api.errors import error_response
from project.models import Campaign, Event, EventAttackVector, EventDisposition, EventPreventionTool, \
    EventRemediation, EventStatus, EventType, IntelReference, IntelSource, Malware, Tag, User


"""
CREATE
"""

create_schema = {
    'type': 'object',
    'properties': {
        'attack_vectors': {
            'type': 'array',
            'items': {'type': 'string', 'minLength': 1, 'maxLength': 255},
            'minItems': 1
        },
        'campaign': {'type': 'string', 'minLength': 1, 'maxLength': 255},
        'disposition': {'type': 'string', 'minLength': 1, 'maxLength': 255},
        'malware': {
            'type': 'array',
            'items': {'type': 'string', 'minLength': 1, 'maxLength': 255},
            'minItems': 1
        },
        'name': {'type': 'string', 'minLength': 1, 'maxLength': 255},
        'prevention_tools': {
            'type': 'array',
            'items': {'type': 'string', 'minLength': 1, 'maxLength': 255},
            'minItems': 1
        },
        'references': {
            'type': 'array',
            'items': {'type': 'string', 'minLength': 1, 'maxLength': 512},
            'minItems': 1
        },
        'remediations': {
            'type': 'array',
            'items': {'type': 'string', 'minLength': 1, 'maxLength': 255},
            'minItems': 1
        },
        'status': {'type': 'string', 'minLength': 1, 'maxLength': 255},
        'tags': {
            'type': 'array',
            'items': {'type': 'string', 'minLength': 1, 'maxLength': 255},
            'minItems': 1
        },
        'types': {
            'type': 'array',
            'items': {'type': 'string', 'minLength': 1, 'maxLength': 255},
            'minItems': 1
        },
        'username': {'type': 'string', 'minLength': 1, 'maxLength': 255}
    },
    'required': ['name', 'username'],
    'additionalProperties': False
}


@bp.route('/events', methods=['POST'])
@check_if_token_required
@validate_json
@validate_schema(create_schema)
def create_event():
    """ Creates a new event. """

    data = request.get_json()

    # Verify this name does not already exist.
    existing = Event.query.filter_by(name=data['name']).first()
    if existing:
        return error_response(409, 'Event name already exists')

    # Verify the username exists.
    user = User.query.filter_by(username=data['username']).first()
    if not user:
        return error_response(404, 'User username not found: {}'.format(data['username']))

    # Verify the user is active.
    if not user.active:
        return error_response(401, 'Cannot create an event with an inactive user')

    # Verify the disposition (has default).
    if 'disposition' not in data:
        disposition = EventDisposition.query.order_by(EventDisposition.id).limit(1).first()
    else:
        disposition = EventDisposition.query.filter_by(value=data['disposition']).first()
        if not disposition:
            return error_response(404, 'Event disposition not found: {}'.format(data['disposition']))

    # Verify the status (has default).
    if 'status' not in data:
        status = EventStatus.query.order_by(EventStatus.id).limit(1).first()
    else:
        status = EventStatus.query.filter_by(value=data['status']).first()
        if not status:
            return error_response(404, 'Event status not found: {}'.format(data['status']))

    # Create the event object.
    event = Event(name=data['name'], disposition=disposition, status=status, user=user)

    # Verify any attack vectors that were specified.
    if 'attack_vectors' in data:
        for value in data['attack_vectors']:
            attack_vector = EventAttackVector.query.filter_by(value=value).first()
            if not attack_vector:
                error_response(404, 'Attack vector not found: {}'.format(value))
            event.attack_vectors.append(attack_vector)

    # Verify campaign if one was specified.
    if 'campaign' in data:
        campaign = Campaign.query.filter_by(name=data['campaign']).first()
        if not campaign:
            return error_response(404, 'Campaign not found: {}'.format(data['campaign']))
        event.campaign = campaign

    # Verify any malware that was specified.
    if 'malware' in data:
        for value in data['malware']:
            malware = Malware.query.filter_by(name=value).first()
            if not malware:
                return error_response(404, 'Malware not found: {}'.format(value))
            event.malware.append(malware)

    # Verify any prevention tools that were specified.
    if 'prevention_tools' in data:
        for value in data['prevention_tools']:
            prevention_tool = EventPreventionTool.query.filter_by(value=value).first()
            if not prevention_tool:
                return error_response(404, 'Prevention tool not found: {}'.format(value))
            event.prevention_tools.append(prevention_tool)

    # Verify any references that were specified.
    if 'references' in data:
        for value in data['references']:
            reference = IntelReference.query.filter_by(reference=value).first()
            if not reference:
                return error_response(404, 'Reference not found: {}'.format(value))
            event.references.append(reference)

    # Verify any remediations that were specified.
    if 'remediations' in data:
        for value in data['remediations']:
            remediation = EventRemediation.query.filter_by(value=value).first()
            if not remediation:
                return error_response(404, 'Remediation not found: {}'.format(value))
            event.remediations.append(remediation)

    # Verify any tags that were specified.
    if 'tags' in data:
        for value in data['tags']:
            tag = Tag.query.filter_by(value=value).first()
            if not tag:
                return error_response(404, 'Tag not found: {}'.format(value))
            event.tags.append(tag)

    # Verify any types that were specified.
    if 'types' in data:
        for value in data['types']:
            _type = EventType.query.filter_by(value=value).first()
            if not _type:
                return error_response(404, 'Type not found: {}'.format(value))
            event.types.append(_type)

    # Save the event.
    db.session.add(event)
    db.session.commit()

    response = jsonify(event.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.read_event', event_id=event.id)
    return response


"""
READ
"""


@bp.route('/events/<int:event_id>', methods=['GET'])
@check_if_token_required
def read_event(event_id):
    """ Gets a single event given its ID. """

    event = Event.query.get(event_id)
    if not event:
        return error_response(404, 'Event ID not found')

    return jsonify(event.to_dict())


@bp.route('/events', methods=['GET'])
@check_if_token_required
def read_events():
    """ Gets a paginated list of events based on various filter criteria. """

    filters = set()

    # Attack vector filter
    if 'attack_vectors' in request.args:
        attack_vectors = request.args.get('attack_vectors').split(',')
        for attack_vector in attack_vectors:
            filters.add(Event.attack_vectors.any(value=attack_vector))

    # Campaign filter
    if 'campaign' in request.args:
        filters.add(Event.campaign.has(Campaign.name == request.args.get('campaign')))

    # Created after filter
    if 'created_after' in request.args:
        try:
            created_after = parse(request.args.get('created_after'), ignoretz=True)
        except (ValueError, OverflowError):
            created_after = datetime.date.max
        filters.add(created_after < Event.created_time)

    # Created before filter
    if 'created_before' in request.args:
        try:
            created_before = parse(request.args.get('created_before'), ignoretz=True)
        except (ValueError, OverflowError):
            created_before = datetime.date.min
        filters.add(Event.created_time < created_before)

    # Disposition filter
    if 'disposition' in request.args:
        filters.add(Event.disposition.has(EventDisposition.value == request.args.get('disposition')))

    # Malware filter
    if 'malware' in request.args:
        malware = request.args.get('malware').split(',')
        for m in malware:
            filters.add(Event.malware.any(name=m))

    # Modified after filter
    if 'modified_after' in request.args:
        try:
            modified_after = parse(request.args.get('modified_after'))
        except (ValueError, OverflowError):
            modified_after = datetime.date.max
        filters.add(modified_after < Event.modified_time)

    # Modified before filter
    if 'modified_before' in request.args:
        try:
            modified_before = parse(request.args.get('modified_before'))
        except (ValueError, OverflowError):
            modified_before = datetime.date.min
        filters.add(Event.modified_time < modified_before)

    # Name filter
    if 'name' in request.args:
        filters.add(Event.name.like('%{}%'.format(request.args.get('name'))))

    # Prevention tool filter
    if 'prevention_tools' in request.args:
        prevention_tools = request.args.get('prevention_tools').split(',')
        for prevention_tool in prevention_tools:
            filters.add(Event.prevention_tools.any(value=prevention_tool))

    # Remediation filter
    if 'remediations' in request.args:
        remediations = request.args.get('remediations').split(',')
        for remediation in remediations:
            filters.add(Event.remediations.any(value=remediation))

    # Source filter (IntelReference)
    if 'sources' in request.args:
        sources = request.args.get('sources').split(',')
        for s in sources:
            filters.add(Event.references.any(IntelReference.source.has(IntelSource.value == s)))

    # Status filter
    if 'status' in request.args:
        filters.add(Event.status.has(EventStatus.value == request.args.get('status')))

    # Tags filter
    if 'tags' in request.args:
        tags = request.args.get('tags').split(',')
        for tag in tags:
            filters.add(Event.tags.any(value=tag))

    # Types filter
    if 'types' in request.args:
        types = request.args.get('types').split(',')
        for _type in types:
            filters.add(Event.types.any(value=_type))

    # Username filter (IntelReference)
    if 'username' in request.args:
        filters.add(Event.user.has(User.username == request.args.get('username')))

    data = Event.to_collection_dict(Event.query.filter(*filters), 'api.read_events', **request.args)
    return jsonify(data)


"""
UPDATE
"""

update_schema = {
    'type': 'object',
    'properties': {
        'attack_vectors': {
            'type': 'array',
            'items': {'type': 'string', 'minLength': 1, 'maxLength': 255},
            'minItems': 1
        },
        'campaign': {'type': 'string', 'minLength': 1, 'maxLength': 255},
        'disposition': {'type': 'string', 'minLength': 1, 'maxLength': 255},
        'malware': {
            'type': 'array',
            'items': {'type': 'string', 'minLength': 1, 'maxLength': 255},
            'minItems': 1
        },
        'prevention_tools': {
            'type': 'array',
            'items': {'type': 'string', 'minLength': 1, 'maxLength': 255},
            'minItems': 1
        },
        'references': {
            'type': 'array',
            'items': {'type': 'string', 'minLength': 1, 'maxLength': 512},
            'minItems': 1
        },
        'remediations': {
            'type': 'array',
            'items': {'type': 'string', 'minLength': 1, 'maxLength': 255},
            'minItems': 1
        },
        'status': {'type': 'string', 'minLength': 1, 'maxLength': 255},
        'tags': {
            'type': 'array',
            'items': {'type': 'string', 'minLength': 1, 'maxLength': 255},
            'minItems': 1
        },
        'types': {
            'type': 'array',
            'items': {'type': 'string', 'minLength': 1, 'maxLength': 255},
            'minItems': 1
        },
        'username': {'type': 'string', 'minLength': 1, 'maxLength': 255}
    },
    'additionalProperties': False
}


@bp.route('/events/<int:event_id>', methods=['PUT'])
@check_if_token_required
@validate_json
@validate_schema(update_schema)
def update_event(event_id):
    """ Updates an existing event. """

    data = request.get_json()

    # Verify the ID exists.
    event = Event.query.get(event_id)
    if not event:
        return error_response(404, 'Event ID not found')

    # Verify attack_vectors if it was specified.
    if 'attack_vectors' in data:
        valid_attack_vectors = []
        for value in data['attack_vectors']:

            # Verify each attack_vector is actually valid.
            attack_vector = EventAttackVector.query.filter_by(value=value).first()
            if not attack_vector:
                error_response(404, 'Event attack vector not found: {}'.format(value))
            valid_attack_vectors.append(attack_vector)
        if valid_attack_vectors:
            event.attack_vectors = valid_attack_vectors

    # Verify campaign if one was specified.
    if 'campaign' in data:
        campaign = Campaign.query.filter_by(name=data['campaign']).first()
        if not campaign:
            return error_response(404, 'Campaign not found: {}'.format(data['campaign']))
        event.campaign = campaign

    # Verify disposition if one was specified.
    if 'disposition' in data:
        disposition = EventDisposition.query.filter_by(value=data['disposition']).first()
        if not disposition:
            return error_response(404, 'Event disposition not found: {}'.format(data['disposition']))
        event.disposition = disposition

    # Verify malware if it was specified.
    if 'malware' in data:
        valid_malware = []
        for value in data['malware']:

            # Verify each malware is actually valid.
            malware = Malware.query.filter_by(name=value).first()
            if not malware:
                error_response(404, 'Malware not found: {}'.format(value))
            valid_malware.append(malware)
        if valid_malware:
            event.malware = valid_malware

    # Verify prevention_tools if it was specified.
    if 'prevention_tools' in data:
        valid_prevention_tools = []
        for value in data['prevention_tools']:

            # Verify each prevention_tool is actually valid.
            prevention_tool = EventPreventionTool.query.filter_by(value=value).first()
            if not prevention_tool:
                error_response(404, 'Event prevention tool not found: {}'.format(value))
            valid_prevention_tools.append(prevention_tool)
        if valid_prevention_tools:
            event.prevention_tools = valid_prevention_tools

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
            event.references = valid_references

    # Verify remediations if it was specified.
    if 'remediations' in data:
        valid_remediations = []
        for value in data['remediations']:

            # Verify each remediation is actually valid.
            remediation = EventRemediation.query.filter_by(value=value).first()
            if not remediation:
                error_response(404, 'Event remediation not found: {}'.format(value))
            valid_remediations.append(remediation)
        if valid_remediations:
            event.remediations = valid_remediations

    # Verify status if one was specified.
    if 'status' in data:
        status = EventStatus.query.filter_by(value=data['status']).first()
        if not status:
            return error_response(404, 'Event status not found: {}'.format(data['status']))
        event.status = status

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
            event.tags = valid_tags

    # Verify types if it was specified.
    if 'types' in data:
        valid_types = []
        for value in data['types']:

            # Verify each type is actually valid.
            _type = EventType.query.filter_by(value=value).first()
            if not _type:
                error_response(404, 'Event type not found: {}'.format(value))
            valid_types.append(_type)
        if valid_types:
            event.types = valid_types

    # Verify username if one was specified.
    if 'username' in data:
        user = User.query.filter_by(username=data['username']).first()
        if not user:
            return error_response(404, 'Username not found: {}'.format(data['username']))

        if not user.active:
            return error_response(401, 'Cannot update an event with an inactive user')

        event.user = user

    db.session.commit()

    response = jsonify(event.to_dict())
    return response


"""
DELETE
"""


@bp.route('/events/<int:event_id>', methods=['DELETE'])
@check_if_token_required
def delete_event(event_id):
    """ Deletes an event. """

    event = Event.query.get(event_id)
    if not event:
        return error_response(404, 'Event ID not found')

    try:
        db.session.delete(event)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        return error_response(409, 'Unable to delete event due to foreign key constraints')

    return '', 204
