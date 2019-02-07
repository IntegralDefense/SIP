from flask import jsonify, request, url_for
from sqlalchemy import exc

from project import db
from project.api import bp
from project.api.decorators import check_if_token_required, validate_json, validate_schema
from project.api.errors import error_response
from project.models import Alert, AlertType, Event

"""
CREATE
"""

create_schema = {
    'type': 'object',
    'properties': {
        'event': {'type': 'string', 'minLength': 1, 'maxLength': 255},
        'type': {'type': 'string', 'minLength': 1, 'maxLength': 255},
        'url': {'type': 'string', 'minLength': 1, 'maxLength': 512}
    },
    'required': ['event', 'type', 'url'],
    'additionalProperties': False
}


@bp.route('/alerts', methods=['POST'])
@check_if_token_required
@validate_json
@validate_schema(create_schema)
def create_alert():
    """ Creates a new alert. """

    data = request.get_json()

    # Verify this URL does not already exist.
    existing = Alert.query.filter_by(url=data['url']).first()
    if existing:
        return error_response(409, 'Alert URL already exists')

    # Verify the type exists.
    t = AlertType.query.filter_by(value=data['type']).first()
    if not t:
        return error_response(404, 'Event type not found: {}'.format(data['type']))

    # Verify the event exists.
    event = Event.query.filter_by(name=data['event']).first()
    if not event:
        return error_response(404, 'Event not found: {}'.format(data['event']))

    # Create and add the new name.
    alert = Alert(event_id=event.id, type_id=t.id, url=data['url'])

    db.session.add(alert)
    db.session.commit()

    response = jsonify(alert.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.read_alert', alert_id=alert.id)
    return response


"""
READ
"""


@bp.route('/alerts/<int:alert_id>', methods=['GET'])
@check_if_token_required
def read_alert(alert_id):
    """ Gets a single alert given its ID. """

    alert = Alert.query.get(alert_id)
    if not alert:
        return error_response(404, 'Alert ID not found')

    return jsonify(alert.to_dict())


@bp.route('/alerts', methods=['GET'])
@check_if_token_required
def read_alerts():
    """ Gets a list of all the alerts. """

    filters = set()

    # Event filter
    if 'event' in request.args:
        filters.add(Alert.event.has(Event.name.contains(request.args.get('event'))))

    # URL filter
    if 'url' in request.args:
        filters.add(Alert.url.like('%{}%'.format(request.args.get('url'))))

    # Type filter
    if 'type' in request.args:
        filters.add(Alert.type.has(AlertType.value == request.args.get('type')))

    data = Alert.to_collection_dict(Alert.query.filter(*filters), 'api.read_alerts', **request.args)
    return jsonify(data)


"""
UPDATE
"""

update_schema = {
    'type': 'object',
    'properties': {
        'event': {'type': 'string', 'minLength': 1, 'maxLength': 255},
        'type': {'type': 'string', 'minLength': 1, 'maxLength': 255},
        'url': {'type': 'string', 'minLength': 1, 'maxLength': 512}
    },
    'additionalProperties': False
}


@bp.route('/alerts/<int:alert_id>', methods=['PUT'])
@check_if_token_required
@validate_json
@validate_schema(update_schema)
def update_alert(alert_id):
    """ Updates an existing alert. """

    data = request.get_json()

    # Verify the ID exists.
    alert = Alert.query.get(alert_id)
    if not alert:
        return error_response(404, 'Alert ID not found')

    # Verify event if one was specified.
    if 'event' in data:

        # Verify the event actually exists.
        event = Event.query.filter_by(name=data['event']).first()
        if not event:
            return error_response(404, 'Event not found: {}'.format(data['event']))
        alert.event = event

    # Verify type if one was specified.
    if 'type' in data:

        # Verify the type actually exists.
        t = AlertType.query.filter_by(value=data['type']).first()
        if not t:
            return error_response(404, 'Event type not found: {}'.format(data['type']))
        alert.type = t

    # Verify URL if one was specified.
    if 'url' in data:

        # Verify the URL does not already exist
        existing = Alert.query.filter_by(url=data['url']).first()
        if existing:
            return error_response(409, 'Alert URL already exists')
        alert.url = data['url']

    # Save the changes.
    db.session.commit()

    response = jsonify(alert.to_dict())
    return response


"""
DELETE
"""


@bp.route('/alerts/<int:alert_id>', methods=['DELETE'])
@check_if_token_required
def delete_alert(alert_id):
    """ Deletes an alert. """

    alert = Alert.query.get(alert_id)
    if not alert:
        return error_response(404, 'Alert ID not found')

    try:
        db.session.delete(alert)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        return error_response(409, 'Unable to delete alert due to foreign key constraints')

    return '', 204
