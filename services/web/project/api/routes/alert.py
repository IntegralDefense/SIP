from flask import current_app, jsonify, request, url_for
from sqlalchemy import exc

from project import db
from project.api import bp
from project.api.decorators import check_if_token_required, validate_json, validate_schema
from project.api.errors import error_response
from project.api.schemas import alert_create, alert_update
from project.models import Alert, AlertType, Event

"""
CREATE
"""


@bp.route('/alerts', methods=['POST'])
@check_if_token_required
@validate_json
@validate_schema(alert_create)
def create_alert():
    """ Creates a new alert.

    .. :quickref: Alert; Creates a new alert.

    **Example request**:

    .. sourcecode:: http

      POST /api/alerts HTTP/1.1
      Host: 127.0.0.1
      Content-Type: application/json

      {
        "event": "Your event name",
        "type": "SIEM",
        "url": "http://your-siem.com/alert1"
      }

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 201 Created
      Content-Type: application/json

      {
        "id": 1,
        "event": "Your event name",
        "type": "SIEM",
        "url": "http://your-siem.com/alert1"
      }

    :reqheader Authorization: Optional JWT Bearer token
    :resheader Content-Type: application/json
    :status 201: Alert created
    :status 400: JSON does not match the schema
    :status 401: Invalid role to perform this action
    :status 404: Alert type not found
    :status 404: Event name not found
    :status 409: Alert URL already exists
    """

    data = request.get_json()

    # Verify this URL does not already exist.
    existing = Alert.query.filter_by(url=data['url']).first()
    if existing:
        return error_response(409, 'Alert URL already exists')

    # Verify the event exists.
    event = Event.query.filter_by(name=data['event']).first()
    if not event:
        return error_response(404, 'Event not found: {}'.format(data['event']))

    # Verify the alert type.
    alert_type = AlertType.query.filter_by(value=data['type']).first()
    if not alert_type:
        if current_app.config['ALERT_AUTO_CREATE_ALERTTYPE']:
            alert_type = AlertType(value=data['type'])
            db.session.add(alert_type)
        else:
            return error_response(404, 'Alert type not found: {}'.format(data['type']))

    # Create and add the new name.
    alert = Alert(event_id=event.id, type=alert_type, url=data['url'])

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
    """ Gets a single alert given its ID.

    .. :quickref: Alert; Gets a single alert given its ID.

    **Example request**:

    .. sourcecode:: http

      GET /api/alerts/1 HTTP/1.1
      Host: 127.0.0.1
      Accept: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "id": 1,
        "event": "Your event name",
        "type": "SIEM",
        "url": "http://your-siem.com/alert1"
      }

    :reqheader Authorization: Optional JWT Bearer token
    :resheader Content-Type: application/json
    :status 200: Alert found
    :status 401: Invalid role to perform this action
    :status 404: Alert ID not found
    """

    alert = Alert.query.get(alert_id)
    if not alert:
        return error_response(404, 'Alert ID not found')

    return jsonify(alert.to_dict())


@bp.route('/alerts', methods=['GET'])
@check_if_token_required
def read_alerts():
    """ Gets a paginated list of all the alerts based on filters.

    .. :quickref: Alert; Gets a paginated list of all the alerts based on filters.

    **Example request**:

    .. sourcecode:: http

      GET /api/alerts?url=your-siem.com HTTP/1.1
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
          "self": "/api/alerts?page=1&per_page=10&url=your-siem.com"
        },
        "_meta": {
          "page": 1,
          "per_page": 10,
          "total_items": 2,
          "total_pages": 1
        },
        "items": [
          {
            "id": 1,
            "event": "Your event name",
            "type": "SIEM",
            "url": "http://your-siem.com/alert1"
          },
          {
            "id": 2,
            "event": "Your event name",
            "type": "SIEM",
            "url": "http://your-siem.com/alert2"
          }
        ]
      }

    :query event: Optional string found in event names
    :query url: Optional string found in alert URLs
    :query type: Optional alert type
    :reqheader Authorization: Optional JWT Bearer token
    :resheader Content-Type: application/json
    :status 200: Alerts found
    :status 401: Invalid role to perform this action
    """

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


@bp.route('/alerts/<int:alert_id>', methods=['PUT'])
@check_if_token_required
@validate_json
@validate_schema(alert_update)
def update_alert(alert_id):
    """ Updates an existing alert.

    .. :quickref: Alert; Updates an existing alert.

    **Example request**:

    .. sourcecode:: http

      PUT /api/alerts/1 HTTP/1.1
      Host: 127.0.0.1
      Content-Type: application/json

      {
        "event": "Your other name",
        "type": "SIEM 2",
        "url": "http://your-siem2.com/alert2"
      }

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "id": 1,
        "event": "Your other name",
        "type": "SIEM 2",
        "url": "http://your-siem2.com/alert2"
      }

    :reqheader Authorization: Optional JWT Bearer token
    :resheader Content-Type: application/json
    :status 200: Alert updated
    :status 400: JSON does not match the schema
    :status 401: Invalid role to perform this action
    :status 404: Alert ID not found
    :status 404: Alert type not found
    :status 404: Event name not found
    :status 409: Alert URL already exists
    """

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
    """ Deletes an alert.

    .. :quickref: Alert; Deletes an alert.

    **Example request**:

    .. sourcecode:: http

      DELETE /api/alerts/1 HTTP/1.1
      Host: 127.0.0.1

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 204 No Content

    :reqheader Authorization: Optional JWT Bearer token
    :status 204: Alert deleted
    :status 401: Invalid role to perform this action
    :status 404: Alert ID not found
    :status 409: Unable to delete alert due to foreign key constraints
    """

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
