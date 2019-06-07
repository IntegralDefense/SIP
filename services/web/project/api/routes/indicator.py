import datetime
import gzip
import json

from dateutil.parser import parse
from flask import current_app, jsonify, request, Response, url_for
from sqlalchemy import and_, exc, func

from project import db
from project.api import bp
from project.api.decorators import check_apikey, validate_json, validate_schema
from project.api.errors import error_response
from project.api.helpers import get_apikey, parse_boolean
from project.api.schemas import indicator_create, indicator_update, indicator_bulk_create
from project.models import Campaign, Indicator, IndicatorConfidence, IndicatorImpact, IndicatorStatus, IndicatorType, \
    IntelReference, IntelSource, Tag, User

"""
CREATE
"""


@bp.route('/indicators', methods=['POST'])
@check_apikey
@validate_json
@validate_schema(indicator_create)
def create_indicator():
    """ Creates a new indicator.

    .. :quickref: Indicator; Creates a new indicator.

    **Example request**:

    .. sourcecode:: http

      POST /indicators HTTP/1.1
      Host: 127.0.0.1
      Content-Type: application/json

      {
        "campaigns": ["LOLcats", "Derpsters"],
        "case_sensitive": false,
        "confidence": "LOW",
        "impact": "LOW",
        "references": [
          {
            "source": "Your company",
            "reference": "http://yourwiki.com/page-for-the-event"
          },
          {
            "source": "OSINT",
            "reference": "http://somehelpfulblog.com/malware-analysis"
          }
        ],
        "status": "NEW",
        "substring": false,
        "tags": ["phish", "from_address"],
        "type": "Email - Address",
        "username": "your_SIP_username",
        "value": "badguy@evil.com"
      }

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 201 Created
      Content-Type: application/json

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
        "id": 1,
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

    :reqheader Authorization: Optional Apikey value
    :resheader Content-Type: application/json
    :status 201: Indicator created
    :status 400: Confidence not given and no default to select
    :status 400: Impact not given and no default to select
    :status 400: Status not given and no default to select
    :status 400: JSON does not match the schema
    :status 401: Invalid role to perform this action
    :status 401: Username is inactive
    :status 401: You must supply either username or API key
    :status 404: Campaign not found
    :status 404: Confidence not found
    :status 404: Impact not found
    :status 404: Reference not found
    :status 404: Status not found
    :status 404: Tag not found
    :status 404: Type not found
    :status 404: User not found by API key
    :status 404: Username not found
    :status 409: Indicator already exists
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
        return error_response(401, 'Cannot create an indicator with an inactive user')

    # Verify the indicator type.
    indicator_type = IndicatorType.query.filter_by(value=data['type']).first()
    if not indicator_type:
        if current_app.config['INDICATOR_AUTO_CREATE_INDICATORTYPE']:
            indicator_type = IndicatorType(value=data['type'])
            db.session.add(indicator_type)
        else:
            return error_response(404, 'Indicator type not found: {}'.format(data['type']))

    # Verify the case-sensitive value (defaults to False).
    if 'case_sensitive' in data:
        case_sensitive = data['case_sensitive']
    else:
        case_sensitive = False

    # Verify this type+value does not already exist based off of case_sensitive.
    if case_sensitive:
        existing = Indicator.query.filter(Indicator.type == indicator_type, func.binary(Indicator.value) == func.binary(data['value'])).first()
        if existing:
            return error_response(409, 'Case-sensitive indicator already exists')
    else:
        existing = Indicator.query.filter(Indicator.type == indicator_type, func.lower(Indicator.value) == func.lower(data['value'])).first()
        if existing:
            return error_response(409, 'Case-insensitive indicator already exists')

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


@bp.route('/indicators/bulk', methods=['POST'])
@check_apikey
@validate_json
@validate_schema(indicator_bulk_create)
def create_indicators():
    """ Creates a list of new indicators.

    .. :quickref: Indicator; Creates a list of new indicators.

    **Example request**:

    .. sourcecode:: http

      POST /indicators/bulk HTTP/1.1
      Host: 127.0.0.1
      Content-Type: application/json

      {
        "indicators": [
          {
            "campaigns": ["LOLcats", "Derpsters"],
            "case_sensitive": false,
            "confidence": "LOW",
            "impact": "LOW",
            "references": [
              {
                "source": "Your company",
                "reference": "http://yourwiki.com/page-for-the-event"
              },
              {
                "source": "OSINT",
                "reference": "http://somehelpfulblog.com/malware-analysis"
              }
            ],
            "status": "NEW",
            "substring": false,
            "tags": ["phish", "from_address"],
            "type": "Email - Address",
            "username": "your_SIP_username",
            "value": "badguy@evil.com"
          },
          {
            "campaigns": ["LOLcats", "Derpsters"],
            "case_sensitive": false,
            "confidence": "LOW",
            "impact": "LOW",
            "references": [
              {
                "source": "Your company",
                "reference": "http://yourwiki.com/page-for-the-event"
              },
              {
                "source": "OSINT",
                "reference": "http://somehelpfulblog.com/malware-analysis"
              }
            ],
            "status": "NEW",
            "substring": false,
            "tags": ["phish", "reply_to_address"],
            "type": "Email - Address",
            "username": "your_SIP_username",
            "value": "mastermind@evil.com"
          }
        ]
      }

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 204 No Content

    :reqheader Authorization: Optional Apikey value
    :resheader Content-Type: application/json
    :status 204: Indicators created
    :status 400: Confidence not given and no default to select
    :status 400: Impact not given and no default to select
    :status 400: Status not given and no default to select
    :status 400: JSON does not match the schema
    :status 401: Invalid role to perform this action
    :status 401: Username is inactive
    :status 401: You must supply either username or API key
    :status 404: Campaign not found
    :status 404: Confidence not found
    :status 404: Impact not found
    :status 404: Reference not found
    :status 404: Status not found
    :status 404: Tag not found
    :status 404: Type not found
    :status 404: User not found by API key
    :status 404: Username not found
    """

    # Set up cache to limit the number of required database queries.
    cache = {'usernames': {},
             'apikeys': {},
             'types': {},
             'confidences': {},
             'default_confidence': None,
             'impacts': {},
             'default_impact': None,
             'statuses': {},
             'default_status': None,
             'campaigns': {},
             'references': {},
             'sources': {},
             'tags': {}}

    for data in request.get_json()['indicators']:

        # Verify the user exists.
        user = None
        if 'username' in data:

            # Check the cache for this username.
            if data['username'] in cache['usernames']:
                user = cache['usernames'][data['username']]
            else:
                user = User.query.filter_by(username=data['username']).first()
                if not user:
                    return error_response(404, 'User not found by username')

                # Add the user to the cache.
                cache['usernames'][data['username']] = user
        else:
            apikey = get_apikey(request)
            if apikey:

                # Check the cache for this apikey.
                if apikey in cache['apikeys']:
                    user = cache['apikeys'][apikey]
                else:
                    user = User.query.filter_by(apikey=apikey).first()
                    if not user:
                        return error_response(404, 'User not found by API key')

                    # Add the user to the cache.
                    cache['apikeys'][apikey] = user
            else:
                return error_response(401, 'You must supply either username or API key')

        # Verify the user is active.
        if not user.active:
            return error_response(401, 'Cannot create an indicator with an inactive user')

        # Check the cache for this indicator type.
        if data['type'] in cache['types']:
            indicator_type = cache['types'][data['type']]
        else:
            # Verify the indicator type.
            indicator_type = IndicatorType.query.filter_by(value=data['type']).first()
            if not indicator_type:
                if current_app.config['INDICATOR_AUTO_CREATE_INDICATORTYPE']:
                    indicator_type = IndicatorType(value=data['type'])
                    db.session.add(indicator_type)
                else:
                    return error_response(404, 'Indicator type not found: {}'.format(data['type']))

            # Add the indicator type to the cache.
            cache['types'][data['type']] = indicator_type

        # Verify the case-sensitive value (defaults to False).
        if 'case_sensitive' in data:
            case_sensitive = data['case_sensitive']
        else:
            case_sensitive = False

        # Verify this type+value does not already exist based off of case_sensitive.
        if case_sensitive:
            existing = Indicator.query.filter(Indicator.type == indicator_type, func.binary(Indicator.value) == func.binary(data['value'])).first()
            if existing:
                continue
        else:
            existing = Indicator.query.filter(Indicator.type == indicator_type, func.lower(Indicator.value) == func.lower(data['value'])).first()
            if existing:
                continue

        # Verify the confidence (has default).
        if 'confidence' not in data:
            # Check the cache for the default indicator confidence.
            if cache['default_confidence']:
                confidence = cache['default_confidence']
            else:
                confidence = IndicatorConfidence.query.order_by(IndicatorConfidence.id).limit(1).first()
                if not confidence:
                    return error_response(400, 'No indicator confidence values exist to use as default')

                # Add the default confidence to the cache.
                cache['default_confidence'] = confidence
        else:
            # Check the cache for this indicator confidence.
            if data['confidence'] in cache['confidences']:
                confidence = cache['confidences'][data['confidence']]
            else:
                confidence = IndicatorConfidence.query.filter_by(value=data['confidence']).first()
                if not confidence:
                    if current_app.config['INDICATOR_AUTO_CREATE_INDICATORCONFIDENCE']:
                        confidence = IndicatorConfidence(value=data['confidence'])
                        db.session.add(confidence)
                    else:
                        return error_response(404, 'Indicator confidence not found: {}'.format(data['confidence']))

                # Add the indicator confidence to the cache.
                cache['confidences'][data['confidence']] = confidence

        # Verify the impact (has default).
        if 'impact' not in data:
            # Check the cache for the default indicator impact.
            if cache['default_impact']:
                impact = cache['default_impact']
            else:
                impact = IndicatorImpact.query.order_by(IndicatorImpact.id).limit(1).first()
                if not impact:
                    return error_response(400, 'No indicator impact values exist to use as default')

                # Add the default impact to the cache.
                cache['default_impact'] = impact
        else:
            # Check the cache for this indicator impact.
            if data['impact'] in cache['impacts']:
                impact = cache['impacts'][data['impact']]
            else:
                impact = IndicatorImpact.query.filter_by(value=data['impact']).first()
                if not impact:
                    if current_app.config['INDICATOR_AUTO_CREATE_INDICATORIMPACT']:
                        impact = IndicatorImpact(value=data['impact'])
                        db.session.add(impact)
                    else:
                        return error_response(404, 'Indicator impact not found: {}'.format(data['impact']))

                # Add the indicator impact to the cache.
                cache['impacts'][data['impact']] = impact

        # Verify the status (has default).
        if 'status' not in data:
            # Check the cache for the default indicator status.
            if cache['default_status']:
                status = cache['default_status']
            else:
                status = IndicatorStatus.query.order_by(IndicatorStatus.id).limit(1).first()
                if not status:
                    return error_response(400, 'No indicator status values exist to use as default')

                # Add the default status to the cache.
                cache['default_status'] = status
        else:
            # Check the cache for this indicator status.
            if data['status'] in cache['statuses']:
                status = cache['statuses'][data['status']]
            else:
                status = IndicatorStatus.query.filter_by(value=data['status']).first()
                if not status:
                    if current_app.config['INDICATOR_AUTO_CREATE_INDICATORSTATUS']:
                        status = IndicatorStatus(value=data['status'])
                        db.session.add(status)
                    else:
                        return error_response(404, 'Indicator status not found: {}'.format(data['status']))

                # Add the indicator status to the cache.
                cache['statuses'][data['status']] = status

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
                # Check the cache for this campaign.
                if value in cache['campaigns']:
                    campaign = cache['campaigns'][value]
                else:
                    campaign = Campaign.query.filter_by(name=value).first()
                    if not campaign:
                        if current_app.config['INDICATOR_AUTO_CREATE_CAMPAIGN']:
                            campaign = Campaign(name=value)
                            db.session.add(campaign)
                        else:
                            return error_response(404, 'Campaign not found: {}'.format(value))

                    # Add this campaign to the cache.
                    cache['campaigns'][value] = campaign

                indicator.campaigns.append(campaign)

        # Verify any references that were specified.
        if 'references' in data:
            for item in data['references']:

                # Check the cache for this source+reference pair.
                if '{}{}'.format(item['source'], item['reference']) in cache['references']:
                    reference = cache['references']['{}{}'.format(item['source'], item['reference'])]
                else:
                    reference = IntelReference.query.filter(and_(IntelReference.reference == item['reference'],
                                                                 IntelReference.source.has(
                                                                     IntelSource.value == item['source']))).first()
                    if not reference:
                        if current_app.config['INDICATOR_AUTO_CREATE_INTELREFERENCE']:

                            # Check the cache for this source.
                            if item['source'] in cache['sources']:
                                source = cache['sources'][item['source']]
                            else:
                                source = IntelSource.query.filter_by(value=item['source']).first()
                                if not source:
                                    source = IntelSource(value=item['source'])
                                    db.session.add(source)

                                # Add this source to the cache.
                                cache['sources'][item['source']] = source

                            reference = IntelReference(reference=item['reference'], source=source, user=user)
                            db.session.add(reference)
                        else:
                            return error_response(404, 'Intel reference not found: {}'.format(item['reference']))

                    # Add this reference to the cache.
                    cache['references']['{}{}'.format(item['source'], item['reference'])] = reference

                indicator.references.append(reference)

        # Verify any tags that were specified.
        if 'tags' in data:
            for value in data['tags']:

                # Check the cache for this tag.
                if value in cache['tags']:
                    tag = cache['tags'][value]
                else:
                    tag = Tag.query.filter_by(value=value).first()
                    if not tag:
                        if current_app.config['INDICATOR_AUTO_CREATE_TAG']:
                            tag = Tag(value=value)
                            db.session.add(tag)
                        else:
                            return error_response(404, 'Tag not found: {}'.format(value))

                    # Add this tag to the cache.
                    cache['tags'][value] = tag

                indicator.tags.append(tag)

        db.session.add(indicator)

    db.session.commit()

    return '', 204


"""
READ
"""


@bp.route('/indicators/<int:indicator_id>', methods=['GET'])
@check_apikey
def read_indicator(indicator_id):
    """ Gets a single indicator given its ID.

    .. :quickref: Indicator; Gets a single indicator given its ID.

    **Example request**:

    .. sourcecode:: http

      GET /indicators/1 HTTP/1.1
      Host: 127.0.0.1
      Accept: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

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
        "id": 1,
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

    :reqheader Authorization: Optional Apikey value
    :resheader Content-Type: application/json
    :status 200: Indicator found
    :status 401: Invalid role to perform this action
    :status 404: Indicator ID not found
    """

    indicator = Indicator.query.get(indicator_id)
    if not indicator:
        return error_response(404, 'Indicator ID not found')

    return jsonify(indicator.to_dict())


@bp.route('/indicators', methods=['GET'])
@check_apikey
def read_indicators():
    """ Gets a paginated list of indicators based on various filter criteria.

    .. :quickref: Indicator; Gets a paginated list of indicators based on various filter criteria.

    *NOTE*: Multiple query parameters can be used and will be applied with AND logic. The default logic for query
    parameters that accept a comma-separated list of values is also AND. However, there are some parameters listed
    below that support the use of OR logic instead. Simply include the string "[OR]" within the parameter's value.

    **Get indicators that have both intel sources A *AND* B**:

    .. sourcecode:: http

      GET /indicators?sources=A,B HTTP/1.1
      Host: 127.0.0.1
      Accept: application/json

    **Get indicators that have either intel source A *OR* B**:

    .. sourcecode:: http

      GET /indicators?sources=[OR]A,B HTTP/1.1
      Host: 127.0.0.1
      Accept: application/json

    **Example request**:

    .. sourcecode:: http

      GET /indicators?value=evil.com&status=NEW HTTP/1.1
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
          "self": "/api/indicators?page=1&per_page=10&value=evil.com&status=NEW"
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
            "id": 1,
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
    :query bulk: Flag to enable "bulk" mode and received a gzipped response of all indicators, but only id+type+value
    :query case_sensitive: True/False
    :query confidence: Confidence value
    :query count: Flag to return the number of results rather than the results themselves
    :query created_after: Parsable date or datetime in GMT. Ex: YYYY-MM-DD or YYYY-MM-DD HH:MM:SS
    :query created_before: Parsable date or datetime in GMT. Ex: YYYY-MM-DD or YYYY-MM-DD HH:MM:SS
    :query exact_value: Exact indicator value to find. Does not use a wildcard search.
    :query impact: Impact value
    :query modified_after: Parsable date or datetime in GMT. Ex: YYYY-MM-DD or YYYY-MM-DD HH:MM:SS
    :query modified_before: Parsable date or datetime in GMT. Ex: YYYY-MM-DD or YYYY-MM-DD HH:MM:SS
    :query no_campaigns: Flag to search for indicators withou any campaigns
    :query no_references: Flag to search for indicators without any references
    :query no_tags: Flag to search for indicators without any tags
    :query not_sources: Comma-separated list of intel sources to EXCLUDE
    :query not_tags: Comma-separated list of tags to EXCLUDE
    :query not_users: Comma-separated list of usernames to EXCLUDE
    :query reference: Intel reference value
    :query sources: Comma-separated list of intel sources. Supports [OR].
    :query status: Status value
    :query substring: True/False
    :query tags: Comma-separated list of tags. Supports [OR].
    :query type: Type value
    :query types: Comma-separated list of types. Only supports OR logic since indicators only have one type.
    :query user: Username of person who created the associated reference
    :query users: Comma-separated list of usernames of the associated references. Supports [OR].
    :query value: String found in value (uses wildcard search)
    :status 200: Indicators found
    :status 401: Invalid role to perform this action
    """

    filters = set()

    # Case-sensitive filter
    if 'case_sensitive' in request.args:
        arg = parse_boolean(request.args.get('case_sensitive'), default=None)
        filters.add(Indicator.case_sensitive.is_(arg))

    # Confidence filter
    if 'confidence' in request.args:
        filters.add(Indicator.confidence.has(IndicatorConfidence.value == request.args.get('confidence')))

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

    # Exact value filter
    if 'exact_value' in request.args:
        filters.add(Indicator.value == request.args.get('exact_value'))

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

    # NO campaigns filter
    if 'no_campaigns' in request.args:
        filters.add(~Indicator.campaigns.any())

    # NO Reference filter (IntelReference)
    if 'no_references' in request.args:
        filters.add(~Indicator.references.any())

    # NO tags filter
    if 'no_tags' in request.args:
        filters.add(~Indicator.tags.any())

    # NOT Source filter (IntelReference)
    if 'not_sources' in request.args:
        not_sources = request.args.get('not_sources').split(',')
        for ns in not_sources:
            filters.add(~Indicator.references.any(IntelReference.source.has(IntelSource.value == ns)))

    # NOT Tags filter
    if 'not_tags' in request.args:
        not_tags = request.args.get('not_tags').split(',')
        for nt in not_tags:
            filters.add(~Indicator.tags.any(value=nt))

    # NOT Username filter
    if 'not_users' in request.args:
        not_users = request.args.get('not_users').split(',')
        for nu in not_users:
            filters.add(~Indicator.references.any(IntelReference.user.has(User.username == nu)))

    # Reference filter (IntelReference)
    if 'reference' in request.args:
        reference = request.args.get('reference')
        filters.add(Indicator.references.any(IntelReference.reference == reference))

    # Source filter (IntelReference)
    if 'sources' in request.args:

        # Figure out AND or OR mode.
        list_mode = 'and'
        request_value = request.args.get('sources')
        if '[OR]' in request_value:
            list_mode = 'or'
            request_value = request_value.replace('[OR]', '')

        sources = request_value.split(',')
        if list_mode == 'and':
            for s in sources:
                filters.add(Indicator.references.any(IntelReference.source.has(IntelSource.value == s)))
        elif list_mode == 'or':
            filters.add(Indicator.references.any(IntelReference.source.has(IntelSource.value.in_(sources))))

    # Status filter
    if 'status' in request.args:
        filters.add(Indicator.status.has(IndicatorStatus.value == request.args.get('status')))

    # Substring filter
    if 'substring' in request.args:
        arg = parse_boolean(request.args.get('substring'), default=None)
        filters.add(Indicator.substring.is_(arg))

    # Tags filter
    if 'tags' in request.args:

        # Figure out AND or OR mode.
        list_mode = 'and'
        request_value = request.args.get('tags')
        if '[OR]' in request_value:
            list_mode = 'or'
            request_value = request_value.replace('[OR]', '')

        search_tags = request_value.split(',')
        if list_mode == 'and':
            for search_tag in search_tags:
                filters.add(Indicator.tags.any(value=search_tag))
        elif list_mode == 'or':
            filters.add(Indicator.tags.any(Tag.value.in_(search_tags)))

    # Type filter
    if 'type' in request.args:
        filters.add(Indicator.type.has(IndicatorType.value == request.args.get('type')))

    # Types filter
    if 'types' in request.args:
        types = request.args.get('types').split(',')
        filters.add(Indicator.type.has(IndicatorType.value.in_(types)))

    # User filter
    if 'user' in request.args:
        filters.add(Indicator.references.any(IntelReference.user.has(User.username == request.args.get('user'))))

    # Users filter
    if 'users' in request.args:

        # Figure out AND or OR mode.
        list_mode = 'and'
        request_value = request.args.get('users')
        if '[OR]' in request_value:
            list_mode = 'or'
            request_value = request_value.replace('[OR]', '')

        search_users = request_value.split(',')
        if list_mode == 'and':
            for search_user in search_users:
                filters.add(Indicator.references.any(IntelReference.user.has(User.username == search_user)))
        elif list_mode == 'or':
            filters.add(Indicator.references.any(IntelReference.user.has(User.username.in_(search_users))))

    # Value filter
    if 'value' in request.args:
        filters.add(Indicator.value.like('%{}%'.format(request.args.get('value'))))

    # If count is enabled, just return the number of results rather than the results themselves.
    if 'count' in request.args:
        count = Indicator.query.filter(*filters).count()
        data = {'count': count}
        return jsonify(data)

    # If bulk is enabled, get all of the results and compress them.
    if 'bulk' in request.args:
        data = [indicator.to_dict(bulk=True) for indicator in Indicator.query.filter(*filters)]
        data = json.dumps(data).encode('utf-8')

        response = Response(status=200, mimetype='application/json')
        response.data = gzip.compress(data)
        response.headers['Content-Encoding'] = 'gzip'
        response.headers['Content-Length'] = len(response.data)
        return response

    data = Indicator.to_collection_dict(Indicator.query.filter(*filters), 'api.read_indicators', **request.args)
    return jsonify(data)


"""
UPDATE
"""


@bp.route('/indicators/<indicator_id>', methods=['PUT'])
@check_apikey
@validate_json
@validate_schema(indicator_update)
def update_indicator(indicator_id):
    """ Updates an existing indicator.

    .. :quickref: Indicator; Updates an existing indicator.

    **Example request**:

    .. sourcecode:: http

      PUT /indicators/1 HTTP/1.1
      Host: 127.0.0.1
      Content-Type: application/json

      {
        "confidence": "HIGH",
        "status": "ENABLED"
      }

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

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
        "confidence": "HIGH",
        "created_time": "Fri, 01 Mar 2019 18:00:51 GMT",
        "equal": [],
        "id": 1,
        "impact": "LOW",
        "modified_time": "Fri, 01 Mar 2019 13:37:02 GMT",
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
        "status": "ENABLED",
        "substring": false,
        "tags": ["from_address", "phish"],
        "type": "Email - Address",
        "user": "your_SIP_username",
        "value": "badguy@evil.com"
      }

    :reqheader Authorization: Optional Apikey value
    :resheader Content-Type: application/json
    :status 200: Indicator updated
    :status 400: JSON does not match the schema
    :status 401: Invalid role to perform this action
    :status 401: Username is inactive
    :status 404: Campaign not found
    :status 404: Confidence not found
    :status 404: Impact not found
    :status 404: Indicator ID not found
    :status 404: Reference not found
    :status 404: Status not found
    :status 404: Tag not found
    :status 404: Username not found
    """

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
@check_apikey
def delete_indicator(indicator_id):
    """ Deletes an indicator.

    .. :quickref: Indicator; Deletes an indicator.

    **Example request**:

    .. sourcecode:: http

      DELETE /indicators/1 HTTP/1.1
      Host: 127.0.0.1

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 204 No Content

    :reqheader Authorization: Optional Apikey value
    :status 204: Indicator deleted
    :status 401: Invalid role to perform this action
    :status 404: Indicator ID not found
    :status 409: Unable to delete indicator due to foreign key constraints
    """

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
