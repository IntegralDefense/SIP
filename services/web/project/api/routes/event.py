import datetime

from dateutil.parser import parse
from flask import current_app, jsonify, request, url_for
from sqlalchemy import and_, exc

from project import db
from project.api import bp
from project.api.decorators import check_if_token_required, validate_json, validate_schema
from project.api.errors import error_response
from project.api.schemas import event_create, event_update
from project.models import Alert, AlertType, Campaign, Event, EventAttackVector, EventDisposition, EventPreventionTool, \
    EventRemediation, EventStatus, EventType, IntelReference, IntelSource, Malware, MalwareType, Tag, User

"""
CREATE
"""


@bp.route('/events', methods=['POST'])
@check_if_token_required
@validate_json
@validate_schema(event_create)
def create_event():
    """ Creates a new event.

    .. :quickref: Event; Creates a new event.

    **Example request**:

    .. sourcecode:: http

      POST /events HTTP/1.1
      Host: 127.0.0.1
      Content-Type: application/json

      {
        "alerts": [
          {
            "type": "SIEM",
            "url": "http://your-siem.com/alert1"
          }
        ],
        "attack_vectors": ["CORPORATE EMAIL"],
        "campaign": "LOLcats",
        "description": "Phish with a link to download a NanoCore .exe",
        "disposition": "DELIVERY",
        "malware": [
          {
            "name": "NanoCore",
            "types": ["RAT"]
          }
        ],
        "name": "20190228 - NanoCore phish",
        "prevention_tools": ["ANTIVIRUS"],
        "references": [
          {
            "source": "Your company",
            "reference": "http://yourwiki.com/page-for-the-event"
          }
        ],
        "remediations": ["REMOVED FROM MAILBOX"],
        "status": "OPEN",
        "tags": ["phish", "nanocore"],
        "types": ["phish"],
        "username": "your_SIP_username"
      }

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 201 Created
      Content-Type: application/json

      {
        "alerts": [
          {
            "event": "20190228 - NanoCore phish",
            "id": 1,
            "type": "SIEM",
            "url": "http://your-siem.com/alert1"
          }
        ],
        "attack_vectors": ["CORPORATE EMAIL"],
        "campaign": {
          "aliases": [],
          "created_time": "Thu, 28 Feb 2019 17:10:44 GMT",
          "id": 1,
          "modified_time": "Thu, 28 Feb 2019 17:10:44 GMT",
          "name": "LOLcats"
        },
        "created_time": "Thu, 28 Feb 2019 22:33:09 GMT",
        "description": "Phish with a link to download a NanoCore .exe",
        "disposition": "DELIVERY",
        "id": 1,
        "malware": [
          {
            "id": 1,
            "name": "NanoCore",
            "types": [
              "RAT"
            ]
          }
        ],
        "modified_time": "Thu, 28 Feb 2019 22:33:09 GMT",
        "name": "20190228 - NanoCore phish",
        "prevention_tools": ["ANTIVIRUS"],
        "references": [
          {
            "id": 1,
            "reference": "http://yourwiki.com/page-for-the-event",
            "source": "Your company",
            "user": "your_SIP_username"
          }
        ],
        "remediations": ["REMOVED FROM MAILBOX"],
        "status": "OPEN",
        "tags": ["nanocore", "phish"],
        "types": ["phish"],
        "user": "your_SIP_username"
      }

    :reqheader Authorization: Optional JWT Bearer token
    :resheader Content-Type: application/json
    :status 201: Event created
    :status 400: Disposition not given and no default to select
    :status 400: Status not given and no default to select
    :status 400: JSON does not match the schema
    :status 401: Invalid role to perform this action
    :status 401: Username is inactive
    :status 404: Alert not found
    :status 404: Attack vector not found
    :status 404: Campaign not found
    :status 404: Disposition not found
    :status 404: Malware not found
    :status 404: Prevention tool not found
    :status 404: Reference not found
    :status 404: Remediation not found
    :status 404: Status not found
    :status 404: Tag not found
    :status 404: Type not found
    :status 404: Username not found
    :status 409: Event name already exists
    """

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
        if not disposition:
            return error_response(400, 'No event disposition values exist to use as default')
    else:
        disposition = EventDisposition.query.filter_by(value=data['disposition']).first()
        if not disposition:
            if current_app.config['EVENT_AUTO_CREATE_EVENTDISPOSITION']:
                disposition = EventDisposition(value=data['disposition'])
                db.session.add(disposition)
            else:
                return error_response(404, 'Event disposition not found: {}'.format(data['disposition']))

    # Verify the status (has default).
    if 'status' not in data:
        status = EventStatus.query.order_by(EventStatus.id).limit(1).first()
        if not status:
            return error_response(400, 'No event status values exist to use as default')
    else:
        status = EventStatus.query.filter_by(value=data['status']).first()
        if not status:
            if current_app.config['EVENT_AUTO_CREATE_EVENTSTATUS']:
                status = EventStatus(value=data['status'])
                db.session.add(status)
            else:
                return error_response(404, 'Event status not found: {}'.format(data['status']))

    # Create the event object.
    event = Event(name=data['name'], disposition=disposition, status=status, user=user)

    # Verify any attack vectors that were specified.
    if 'attack_vectors' in data:
        for value in data['attack_vectors']:
            attack_vector = EventAttackVector.query.filter_by(value=value).first()
            if not attack_vector:
                if current_app.config['EVENT_AUTO_CREATE_EVENTATTACKVECTOR']:
                    attack_vector = EventAttackVector(value=value)
                    db.session.add(attack_vector)
                else:
                    return error_response(404, 'Event attack vector not found: {}'.format(value))

            event.attack_vectors.append(attack_vector)

    # Verify campaign if one was specified.
    if 'campaign' in data:
        campaign = Campaign.query.filter_by(name=data['campaign']).first()
        if not campaign:
            if current_app.config['EVENT_AUTO_CREATE_CAMPAIGN']:
                campaign = Campaign(name=data['campaign'])
                db.session.add(campaign)
            else:
                return error_response(404, 'Campaign not found: {}'.format(data['campaign']))

        event.campaign = campaign

    # Set the description if one was specified.
    if 'description' in data:
        event.description = data['description']

    # Verify any malware that was specified.
    if 'malware' in data:
        for item in data['malware']:
            malware = Malware.query.filter_by(name=item['name']).first()
            if not malware:
                if current_app.config['EVENT_AUTO_CREATE_MALWARE']:
                    malware = Malware(name=item['name'])
                    db.session.add(malware)

                    if 'types' in item:
                        for type_ in item['types']:
                            malware_type = MalwareType.query.filter_by(value=type_).first()
                            if not malware_type:
                                malware_type = MalwareType(value=type_)
                                db.session.add(malware_type)

                            if malware_type not in malware.types:
                                malware.types.append(malware_type)
                else:
                    return error_response(404, 'Malware not found: {}'.format(item['name']))

            event.malware.append(malware)

    # Verify any prevention tools that were specified.
    if 'prevention_tools' in data:
        for value in data['prevention_tools']:
            prevention_tool = EventPreventionTool.query.filter_by(value=value).first()
            if not prevention_tool:
                if current_app.config['EVENT_AUTO_CREATE_EVENTPREVENTIONTOOL']:
                    prevention_tool = EventPreventionTool(value=value)
                    db.session.add(prevention_tool)
                else:
                    return error_response(404, 'Event prevention tool not found: {}'.format(value))

            event.prevention_tools.append(prevention_tool)

    # Verify any references that were specified.
    if 'references' in data:
        for item in data['references']:
            reference = IntelReference.query.filter(and_(IntelReference.reference == item['reference'],
                                                         IntelReference.source.has(
                                                             IntelSource.value == item['source']))).first()
            if not reference:
                if current_app.config['EVENT_AUTO_CREATE_INTELREFERENCE']:
                    source = IntelSource.query.filter_by(value=item['source']).first()
                    if not source:
                        source = IntelSource(value=item['source'])
                        db.session.add(source)

                    reference = IntelReference(reference=item['reference'], source=source, user=user)
                    db.session.add(reference)
                else:
                    return error_response(404, 'Intel reference not found: {}'.format(item['reference']))

            event.references.append(reference)

    # Verify any remediations that were specified.
    if 'remediations' in data:
        for value in data['remediations']:
            remediation = EventRemediation.query.filter_by(value=value).first()
            if not remediation:
                if current_app.config['EVENT_AUTO_CREATE_EVENTREMEDIATION']:
                    remediation = EventRemediation(value=value)
                    db.session.add(remediation)
                else:
                    return error_response(404, 'Event remediation not found: {}'.format(value))

            event.remediations.append(remediation)

    # Verify any tags that were specified.
    if 'tags' in data:
        for value in data['tags']:
            tag = Tag.query.filter_by(value=value).first()
            if not tag:
                if current_app.config['EVENT_AUTO_CREATE_TAG']:
                    tag = Tag(value=value)
                    db.session.add(tag)
                else:
                    return error_response(404, 'Tag not found: {}'.format(value))

            event.tags.append(tag)

    # Verify any types that were specified.
    if 'types' in data:
        for value in data['types']:
            event_type = EventType.query.filter_by(value=value).first()
            if not event_type:
                if current_app.config['EVENT_AUTO_CREATE_EVENTTYPE']:
                    event_type = EventType(value=value)
                    db.session.add(event_type)
                else:
                    return error_response(404, 'Event type not found: {}'.format(value))

            event.types.append(event_type)

    # Verify any alerts that were specified. The alerts are added at the very end due
    # to how the relationships between Alert <> Event are configured. By adding an alert,
    # it will also add and commit the event. This is done last in case the auto-create
    # functionality is disabled and one of the other fields issues a 404, which will
    # correctly issue the 404 response and will not create the event.
    if 'alerts' in data:
        for value in data['alerts']:
            alert = Alert.query.filter_by(url=value['url']).first()
            if not alert:
                if current_app.config['EVENT_AUTO_CREATE_ALERT']:
                    alert_type = AlertType.query.filter_by(value=value['type']).first()
                    if not alert_type:
                        alert_type = AlertType(value=value['type'])
                        db.session.add(alert_type)
                    alert = Alert(type=alert_type, url=value['url'], event_id=event.id)
                    db.session.add(alert)
                else:
                    return error_response(404, 'Alert not found: {}'.format(value['url']))

            event.alerts.append(alert)

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
    """ Gets a single event given its ID.

    .. :quickref: Event; Gets a single event given its ID.

    **Example request**:

    .. sourcecode:: http

      GET /events/1 HTTP/1.1
      Host: 127.0.0.1
      Accept: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "alerts": [
          {
            "event": "20190228 - NanoCore phish",
            "id": 1,
            "type": "SIEM",
            "url": "http://your-siem.com/alert1"
          }
        ],
        "attack_vectors": ["CORPORATE EMAIL"],
        "campaign": {
          "aliases": [],
          "created_time": "Thu, 28 Feb 2019 17:10:44 GMT",
          "id": 1,
          "modified_time": "Thu, 28 Feb 2019 17:10:44 GMT",
          "name": "LOLcats"
        },
        "created_time": "Thu, 28 Feb 2019 22:33:09 GMT",
        "description": "Phish with a link to download a NanoCore .exe",
        "disposition": "DELIVERY",
        "id": 1,
        "malware": [
          {
            "id": 1,
            "name": "NanoCore",
            "types": [
              "RAT"
            ]
          }
        ],
        "modified_time": "Thu, 28 Feb 2019 22:33:09 GMT",
        "name": "20190228 - NanoCore phish",
        "prevention_tools": ["ANTIVIRUS"],
        "references": [
          {
            "id": 1,
            "reference": "http://yourwiki.com/page-for-the-event",
            "source": "Your company",
            "user": "your_SIP_username"
          }
        ],
        "remediations": ["REMOVED FROM MAILBOX"],
        "status": "OPEN",
        "tags": ["nanocore", "phish"],
        "types": ["phish"],
        "user": "your_SIP_username"
      }

    :reqheader Authorization: Optional JWT Bearer token
    :resheader Content-Type: application/json
    :status 200: Event found
    :status 401: Invalid role to perform this action
    :status 404: Event ID not found
    """

    event = Event.query.get(event_id)
    if not event:
        return error_response(404, 'Event ID not found')

    return jsonify(event.to_dict())


@bp.route('/events', methods=['GET'])
@check_if_token_required
def read_events():
    """ Gets a paginated list of events based on various filter criteria.

    .. :quickref: Event; Gets a paginated list of events based on various filter criteria.

    **Example request**:

    *NOTE*: Multiple query parameters can be used and will be applied with AND logic.

    .. sourcecode:: http

      GET /events?attack_vectors=WEBMAIL&created_after=2019-03-01 HTTP/1.1
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
          "self": "/api/events?page=1&per_page=10&attack_vectors=WEBMAIL"
        },
        "_meta": {
          "page": 1,
          "per_page": 10,
          "total_items": 1,
          "total_pages": 1
        },
        "items": [
          {
            "alerts": [
              {
                "event": "20190228 - Credential harvester phish",
                "id": 2,
                "type": "SIEM",
                "url": "http://your-siem.com/alert2"
              }
            ],
            "attack_vectors": ["WEBMAIL"],
            "campaign": null,
            "created_time": "Fri, 01 Mar 2019 15:50:32 GMT",
            "description": "Phish with a link to a credential harvester",
            "disposition": "DELIVERY",
            "id": 5,
            "malware": [],
            "modified_time": "Fri, 01 Mar 2019 15:50:32 GMT",
            "name": "20190228 - Credential harvester phish",
            "prevention_tools": ["PROXY"],
            "references": [
              {
                "id": 2,
                "reference": "http://yourwiki.com/event2",
                "source": "Your company",
                "user": "your_SIP_username"
              }
            ],
            "remediations": ["REMOVED FROM MAILBOX"],
            "status": "CLOSED",
            "tags": ["credential_harvesting", "phish"],
            "types": ["phish"],
            "user": "your_SIP_username"
          }
        ]
      }

    :reqheader Authorization: Optional JWT Bearer token
    :resheader Content-Type: application/json
    :query alert_types: Comma-separated list of alert types
    :query alert_url: String found in alert URLs (uses wildcard search)
    :query attack_vectors: Comma-separated list of attack vectors
    :query campaign: Campaign name
    :query created_after: Parsable date or datetime in GMT. Ex: YYYY-MM-DD or YYYY-MM-DD HH:MM:SS
    :query created_before: Parsable date or datetime in GMT. Ex: YYYY-MM-DD or YYYY-MM-DD HH:MM:SS
    :query description: String found in descriptions (uses wildcard search)
    :query disposition: Disposition value
    :query malware: Comma-separated list of malware names
    :query modified_after: Parsable date or datetime in GMT. Ex: YYYY-MM-DD or YYYY-MM-DD HH:MM:SS
    :query modified_before: Parsable date or datetime in GMT. Ex: YYYY-MM-DD or YYYY-MM-DD HH:MM:SS
    :query name: String found in event names (uses wildcard search)
    :query prevention_tools: Comma-separated list of prevention tools
    :query remediations: Comma-separated list of remediations
    :query sources: Comma-separated list of intel sources
    :query status: Status value
    :query tags: Comma-separated list of tags
    :query types: Comma-separated list of event types
    :query user: Username of person who created the event
    :status 200: Events found
    :status 401: Invalid role to perform this action
    """

    filters = set()

    # Alerts types filter
    if 'alert_types' in request.args:
        alert_types = request.args.get('alert_types').split(',')
        for alert_type in alert_types:
            filters.add(Event.alerts.any(Alert.type.has(AlertType.value == alert_type)))

    # Alerts URL filter
    if 'alert_url' in request.args:
        filters.add(Event.alerts.any(Alert.url.like('%{}%'.format(request.args.get('alert_url')))))

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

    # Description filter
    if 'description' in request.args:
        filters.add(Event.description.like('%{}%'.format(request.args.get('description'))))

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

    # User filter
    if 'user' in request.args:
        filters.add(Event.user.has(User.username == request.args.get('user')))

    data = Event.to_collection_dict(Event.query.filter(*filters), 'api.read_events', **request.args)
    return jsonify(data)


"""
UPDATE
"""


@bp.route('/events/<int:event_id>', methods=['PUT'])
@check_if_token_required
@validate_json
@validate_schema(event_update)
def update_event(event_id):
    """ Updates an existing event.

    .. :quickref: Event; Updates an existing event.

    **Example request**:

    .. sourcecode:: http

      PUT /events/1 HTTP/1.1
      Host: 127.0.0.1
      Content-Type: application/json

      {
        "description": "Phish with a link to download a Remcos .exe",
        "malware": ["Remcos"],
        "tags": ["remcos", "phish"]
      }

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "alerts": [
          {
            "event": "20190228 - NanoCore phish",
            "id": 1,
            "type": "SIEM",
            "url": "http://your-siem.com/alert1"
          }
        ],
        "attack_vectors": ["CORPORATE EMAIL"],
        "campaign": {
          "aliases": [],
          "created_time": "Thu, 28 Feb 2019 17:10:44 GMT",
          "id": 1,
          "modified_time": "Thu, 28 Feb 2019 19:04:45 GMT",
          "name": "LOLcats"
        },
        "created_time": "Thu, 28 Feb 2019 22:33:09 GMT",
        "description": "Phish with a link to download a Remcos .exe",
        "disposition": "DELIVERY",
        "id": 1,
        "malware": [
          {
            "id": 2,
            "name": "Remcos",
            "types": [
              "RAT"
            ]
          }
        ],
        "modified_time": "Thu, 28 Feb 2019 22:33:09 GMT",
        "name": "20190228 - NanoCore phish",
        "prevention_tools": ["ANTIVIRUS"],
        "references": [
          {
            "id": 1,
            "reference": "http://yourwiki.com/page-for-the-event",
            "source": "Your company",
            "user": "your_SIP_username"
          }
        ],
        "remediations": ["REMOVED FROM MAILBOX"],
        "status": "OPEN",
        "tags": ["phish", "remcos"],
        "types": ["phish"],
        "user": "your_SIP_username"
      }

    :reqheader Authorization: Optional JWT Bearer token
    :resheader Content-Type: application/json
    :status 200: Event updated
    :status 400: JSON does not match the schema
    :status 401: Invalid role to perform this action
    :status 401: Username is inactive
    :status 404: Alert URL not found
    :status 404: Attack vector not found
    :status 404: Campaign not found
    :status 404: Disposition not found
    :status 404: Event ID not found
    :status 404: Malware not found
    :status 404: Prevention tool not found
    :status 404: Reference not found
    :status 404: Remediation not found
    :status 404: Status not found
    :status 404: Tag not found
    :status 404: Type not found
    :status 404: Username not found
    """

    data = request.get_json()

    # Verify the ID exists.
    event = Event.query.get(event_id)
    if not event:
        return error_response(404, 'Event ID not found')

    # Verify alerts if it was specified.
    if 'alerts' in data:
        valid_alerts = []
        for url in data['alerts']:

            # Verify each alert is actually valid.
            alert = Alert.query.filter_by(url=url).first()
            if not alert:
                error_response(404, 'Alert not found: {}'.format(url))
            valid_alerts.append(alert)
        if valid_alerts:
            event.alerts = valid_alerts

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

    # Update the description if one was specified.
    if 'description' in data:
        event.description = data['description']

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
    """ Deletes an event.

    .. :quickref: Event; Deletes an event.

    **Example request**:

    .. sourcecode:: http

      DELETE /events/1 HTTP/1.1
      Host: 127.0.0.1

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 204 No Content

    :reqheader Authorization: Optional JWT Bearer token
    :status 204: Event deleted
    :status 401: Invalid role to perform this action
    :status 404: Event ID not found
    :status 409: Unable to delete event due to foreign key constraints
    """

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
