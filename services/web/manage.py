import click
import configparser
import csv
import json
import jsonschema
import os
import random
import string
import time
import unittest

from dateutil.parser import parse
from flask import current_app
from flask.cli import FlaskGroup
from flask_security import SQLAlchemyUserDatastore
from flask_security.utils import hash_password

from lib.constants import HOME_DIR
from project import create_app, db, models

app = create_app()
cli = FlaskGroup(create_app=create_app)


@cli.command()
@click.option('--baseurl', type=str, required=True)
def import_ace_events(baseurl):
    """ Imports ACE events from the exported MySQL CSV """

    # Make sure the events.json file exists.
    if not os.path.exists('./import/ace_events.csv'):
        current_app.logger.error('Could not locate ace_events.csv for ACE import')
        return

    # Read the ace_events.csv file and build an events dictionary.
    start = time.time()
    events = dict()
    with open('./import/ace_events.csv') as f:
        rows = list(csv.DictReader(f, delimiter='\t'))
        for row in rows:
            event_name = '{} {}'.format(row['creation_date'].replace('-', ''), row['name'])
            if event_name not in events:
                events[event_name] = []
            events[event_name].append(row)
    current_app.logger.info('ACE IMPORT: Loaded ace_events.csv in {}'.format(time.time() - start))

    # Get the existing events from the database.
    start = time.time()
    existing_events = dict()
    for x in models.Event.query.all():
        existing_events[x.name] = x

    # Get the existing values from the database that events depend upon.
    existing_alerts = dict()
    for x in models.Alert.query.all():
        existing_alerts[x.url] = x

    existing_alert_type = dict()
    for x in models.AlertType.query.all():
        existing_alert_type[x.value] = x

    existing_campaigns = dict()
    for x in models.Campaign.query.all():
        existing_campaigns[x.name] = x

    existing_event_attack_vector = dict()
    for x in models.EventAttackVector.query.all():
        existing_event_attack_vector[x.value] = x

    existing_event_disposition = dict()
    for x in models.EventDisposition.query.all():
        existing_event_disposition[x.value] = x

    existing_event_prevention_tool = dict()
    for x in models.EventPreventionTool.query.all():
        existing_event_prevention_tool[x.value] = x

    existing_event_remediation = dict()
    for x in models.EventRemediation.query.all():
        existing_event_remediation[x.value] = x

    existing_event_status = dict()
    for x in models.EventStatus.query.all():
        existing_event_status[x.value] = x

    existing_event_type = dict()
    for x in models.EventType.query.all():
        existing_event_type[x.value] = x

    existing_malware = dict()
    for x in models.Malware.query.all():
        existing_malware[x.name] = x

    existing_malware_type = dict()
    for x in models.MalwareType.query.all():
        existing_malware_type[x.value] = x

    existing_users = dict()
    for x in models.User.query.all():
        existing_users[x.username] = x

    num_modified_events = 0
    for event_name in events.keys():

        event_modified = False

        # Check if the campaign must be created.
        this_campaign = events[event_name][0]['campaign_name']
        if this_campaign and this_campaign.lower() != 'unknown':
            if this_campaign in existing_campaigns:
                campaign = existing_campaigns[this_campaign]
            else:
                new_campaign = models.Campaign(name=this_campaign)
                existing_campaigns[new_campaign.name] = new_campaign
                campaign = new_campaign
                db.session.add(new_campaign)
        else:
            campaign = None

        # Check if the event attack_vector must be created.
        this_attack_vector = events[event_name][0]['vector']
        if this_attack_vector in existing_event_attack_vector:
            event_attack_vector = existing_event_attack_vector[this_attack_vector]
        else:
            new_event_attack_vector = models.EventAttackVector(value=this_attack_vector)
            existing_event_attack_vector[new_event_attack_vector.value] = new_event_attack_vector
            event_attack_vector = new_event_attack_vector
            db.session.add(new_event_attack_vector)

        # Check if the event disposition must be created.
        this_disposition = events[event_name][0]['disposition']
        if this_disposition in existing_event_disposition:
            event_disposition = existing_event_disposition[this_disposition]
        else:
            new_event_disposition = models.EventDisposition(value=this_disposition)
            existing_event_disposition[new_event_disposition.value] = new_event_disposition
            event_disposition = new_event_disposition
            db.session.add(new_event_disposition)

        # Check if the event prevention_tool must be created.
        this_prevention_tool = events[event_name][0]['prevention_tool']
        if this_prevention_tool in existing_event_prevention_tool:
            event_prevention_tool = existing_event_prevention_tool[this_prevention_tool]
        else:
            new_event_prevention_tool = models.EventPreventionTool(value=this_prevention_tool)
            existing_event_prevention_tool[new_event_prevention_tool.value] = new_event_prevention_tool
            event_prevention_tool = new_event_prevention_tool
            db.session.add(new_event_prevention_tool)

        # Check if the event remediation must be created.
        this_remediation = events[event_name][0]['remediation']
        if this_remediation in existing_event_remediation:
            event_remediation = existing_event_remediation[this_remediation]
        else:
            new_event_remediation = models.EventRemediation(value=this_remediation)
            existing_event_remediation[new_event_remediation.value] = new_event_remediation
            event_remediation = new_event_remediation
            db.session.add(new_event_remediation)

        # Check if the event status must be created.
        this_status = events[event_name][0]['status']
        if this_status in existing_event_status:
            event_status = existing_event_status[this_status]
        else:
            new_event_status = models.EventStatus(value=this_status)
            existing_event_status[new_event_status.value] = new_event_status
            event_status = new_event_status
            db.session.add(new_event_status)

        # Check if the event type must be created.
        this_type = events[event_name][0]['type']
        if this_type in existing_event_type:
            event_type = existing_event_type[this_type]
        else:
            new_event_type = models.EventType(value=this_type)
            existing_event_type[new_event_type.value] = new_event_type
            event_type = new_event_type
            db.session.add(new_event_type)

        # Check if the user must be created.
        this_username = events[event_name][0]['username']
        if this_username in existing_users:
            user = existing_users[this_username]
        else:
            password = ''.join(random.choice(string.ascii_letters + string.punctuation + string.digits) for x in range(20))
            new_user = models.User(active=False,
                                   email='{}@unknown'.format(this_username),
                                   first_name=this_username,
                                   last_name='Unknown',
                                   password=hash_password(password),
                                   roles=[],
                                   username=this_username)
            existing_users[this_username] = new_user
            user = new_user
            db.session.add(new_user)

        # Check if the event needs to be created.
        if event_name in existing_events:
            event = existing_events[event_name]
        elif event_name.replace(' ', '_') in existing_events:
            event = existing_events[event_name.replace(' ', '_')]
        else:
            event = models.Event(name=event_name,
                                 status=event_status,
                                 user=user)
            db.session.add(event)
            existing_events[event_name] = event
            event_modified = True

        # Check if the event needs to be updated.
        if event_attack_vector not in event.attack_vectors:
            event.attack_vectors.append(event_attack_vector)
            event_modified = True
        if event.campaign != campaign:
            event.campaign = campaign
            event_modified = True
        if event.disposition != event_disposition:
            event.disposition = event_disposition
            event_modified = True
        if event_prevention_tool not in event.prevention_tools:
            event.prevention_tools.append(event_prevention_tool)
            event_modified = True
        if event_remediation not in event.remediations:
            event.remediations.append(event_remediation)
            event_modified = True
        if event.status != event_status:
            event.status = event_status
        if event_type not in event.types:
            event.types.append(event_type)
            event_modified = True
        if event.user != user:
            event.user = user

        # Loop over each row contained in the event.
        earliest_disposition = None
        latest_disposition = None
        for row in events[event_name]:

            # Get the earliest and latest disposition times (for created and modified time).
            if not earliest_disposition:
                earliest_disposition = parse(row['disposition_time'])
            elif parse(row['disposition_time']) < earliest_disposition:
                earliest_disposition = parse(row['disposition_time'])

            if not latest_disposition:
                latest_disposition = parse(row['disposition_time'])
            elif latest_disposition < parse(row['disposition_time']):
                latest_disposition = parse(row['disposition_time'])

            event.created_time = earliest_disposition
            event.modified_time = latest_disposition

            # Check if the alert type must be created.
            if 'ACE' in existing_alert_type:
                alert_type = existing_alert_type['ACE']
            else:
                alert_type = models.AlertType(value='ACE')
                existing_alert_type['ACE'] = alert_type
                db.session.add(alert_type)
                event_modified = True

            # Check if the alert must be created. If the alert already exists,
            # it is already associated with an event, so there is no need to add it to the list.
            row_full_url = baseurl + row['uuid']
            if row_full_url not in existing_alerts:
                new_alert = models.Alert(event=event,
                                         type=alert_type,
                                         url=row_full_url)
                existing_alerts[row_full_url] = new_alert
                db.session.add(new_alert)
                event_modified = True

            # Check if the malware type must be created.
            if row['malware_type'] in existing_malware_type:
                malware_type = existing_malware_type[row['malware_type']]
            else:
                malware_type = models.MalwareType(value=row['malware_type'])
                existing_malware_type[malware_type.value] = malware_type
                db.session.add(malware_type)
                event_modified = True

            # Check if the malware must be created.
            if row['malware_name'] in existing_malware:
                malware = existing_malware[row['malware_name']]
            else:
                malware = models.Malware(name=row['malware_name'], types=[malware_type])
                existing_malware[malware.name] = malware
                db.session.add(malware)
                event_modified = True

            # Associate the malware with the event if it isn't already.
            if malware not in event.malware:
                event.malware.append(malware)
                event_modified = True

        if event_modified:
            num_modified_events += 1

    db.session.commit()

    current_app.logger.info('ACE IMPORT: Imported {}/{} events in {}'.format(num_modified_events, len(events.keys()), time.time() - start))


@cli.command()
def import_crits_events():
    """ Imports CRITS events from the exported MongoDB JSON """

    # Make sure the events.json file exists.
    if not os.path.exists('./import/events.json'):
        current_app.logger.error('Could not locate events.json for CRITS import')
        return

    start = time.time()
    with open('./import/events.json') as f:
        events = json.load(f)
    current_app.logger.info('CRITS IMPORT: Loaded events.json in {}'.format(time.time() - start))

    # Validate the indicators JSON.
    crits_create_schema = {
        'type': 'array',
        'items': {
            'type': 'object',
            'properties': {
                'bucket_list': {
                    'type': 'array',
                    'items': {'type': 'string', 'maxLength': 255}
                },
                'campaign': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'date': {
                                'type': 'object',
                                'properties': {
                                    '$date': {'type': 'string', 'minLength': 24, 'maxLength': 24}
                                }
                            },
                            'name': {'type': 'string', 'maxLength': 255}
                        }
                    }
                },
                'created': {
                    'type': 'object',
                    'properties': {
                        '$date': {'type': 'string', 'minLength': 24, 'maxLength': 24}
                    }
                },
                'description': {'type': 'string'},
                'event_type': {'type': 'string', 'minLength': 1, 'maxLength': 255},
                'modified': {
                    'type': 'object',
                    'properties': {
                        '$date': {'type': 'string', 'minLength': 24, 'maxLength': 24}
                    }
                },
                'source': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'instances': {
                                'type': 'array',
                                'items': {
                                    'type': 'object',
                                    'properties': {
                                        'analyst': {'type': 'string', 'minLength': 1, 'maxLength': 255},
                                        'reference': {'type': 'string', 'minLength': 1, 'maxLength': 512}
                                    }
                                }
                            },
                            'name': {'type': 'string', 'minLength': 1, 'maxLength': 255}
                        }
                    }
                },
                'status': {'type': 'string', 'minLength': 1, 'maxLength': 255},
                'title': {'type': 'string', 'minLength': 1, 'maxLength': 255},
            },
            'required': ['created', 'event_type', 'modified', 'source', 'status', 'title']
        }
    }
    start = time.time()
    jsonschema.validate(events, crits_create_schema)
    current_app.logger.info('CRITS IMPORT: Validated events.json in {}'.format(time.time() - start))

    # Get the existing events from the database.
    start = time.time()
    existing_events = dict()
    for x in models.Event.query.all():
        existing_events[x.name] = x

    # Get the existing values from the database that events depend upon.
    existing_campaigns = dict()
    for x in models.Campaign.query.all():
        existing_campaigns[x.name] = x

    existing_event_status = dict()
    for x in models.EventStatus.query.all():
        existing_event_status[x.value] = x

    existing_event_type = dict()
    for x in models.EventType.query.all():
        existing_event_type[x.value] = x

    existing_intel_reference = dict()  # source: reference: object
    for x in models.IntelReference.query.all():
        if x.source.value not in existing_intel_reference:
            existing_intel_reference[x.source.value] = dict()
        existing_intel_reference[x.source.value][x.reference] = x

    existing_intel_source = dict()
    for x in models.IntelSource.query.all():
        existing_intel_source[x.value] = x

    existing_tags = dict()
    for x in models.Tag.query.all():
        existing_tags[x.value] = x

    existing_users = dict()
    for x in models.User.query.all():
        existing_users[x.username] = x

    num_modified_events = 0
    unique_events = []
    for event in events:

        event_modified = False

        # Make a list of potential event names to check for existing/duplicate events.
        potential_event_names = [event['title'], event['title'].replace('_', ' ')]

        # Skip this event if it is a duplicate.
        if any(event_name in unique_events for event_name in potential_event_names):
            current_app.logger.warning('CRITS IMPORT: Skipping duplicate event: {}'.format(event['title']))
            continue
        else:
            unique_events.append(event['title'])

        # Check if the event status must be created.
        if event['status'] in existing_event_status:
            event_status = existing_event_status[event['status']]
        else:
            new_event_status = models.EventStatus(value=event['status'])
            existing_event_status[new_event_status.value] = new_event_status
            event_status = new_event_status
            db.session.add(new_event_status)

        # Check if the event type must be created.
        if event['event_type'] in existing_event_type:
            event_types = [existing_event_type[event['event_type']]]
        else:
            new_event_type = models.EventType(value=event['event_type'])
            existing_event_type[new_event_type.value] = new_event_type
            event_types = [new_event_type]
            db.session.add(new_event_type)

        # Check if the user must be created.
        username = event['source'][0]['instances'][0]['analyst']
        if username in existing_users:
            user = existing_users[username]
        else:
            password = ''.join(random.choice(string.ascii_letters + string.punctuation + string.digits) for x in range(20))
            new_user = models.User(active=False,
                                   email='{}@unknown'.format(username),
                                   first_name=username,
                                   last_name='Unknown',
                                   password=hash_password(password),
                                   roles=[],
                                   username=username)
            existing_users[username] = new_user
            user = new_user
            db.session.add(new_user)

        # Pick the most recent campaign.
        if 'campaign' in event and event['campaign']:
            campaign = existing_campaigns[event['campaign'][-1]['name']]
        else:
            campaign = None

        # Create the intel references list.
        references = []
        for s in event['source']:

            # Check if the source must be created.
            if s['name'] in existing_intel_source:
                source = existing_intel_source[s['name']]
            else:
                source = models.IntelSource(value=s['name'])
                existing_intel_source[s['name']] = source
                db.session.add(source)

            # Make sure the source exists in the intel reference dictionary.
            if source.value not in existing_intel_reference:
                existing_intel_reference[source.value] = dict()

            for instance in s['instances']:

                # Check if the reference must be created.
                if 'reference' in instance and source.value in existing_intel_reference and instance['reference'] in existing_intel_reference[source.value]:
                    references.append(existing_intel_reference[source.value][instance['reference']])
                elif 'reference' in instance and instance['reference']:
                    new_reference = models.IntelReference(reference=instance['reference'],
                                                          source=source,
                                                          user=user)
                    existing_intel_reference[source.value][instance['reference']] = new_reference
                    references.append(new_reference)
                    db.session.add(new_reference)

        # Create the tags list.
        tags = []
        if 'bucket_list' in event and event['bucket_list']:
            for tag in event['bucket_list']:

                # Check if the tag must be created.
                if tag in existing_tags:
                    tags.append(existing_tags[tag])
                else:
                    new_tag = models.Tag(value=tag)
                    existing_tags[tag] = new_tag
                    tags.append(new_tag)
                    db.session.add(new_tag)

        # Check if the event needs to be created.
        this_event = None
        for event_name in potential_event_names:
            if event_name in existing_events:
                this_event = existing_events[event_name]
        if not this_event:
            this_event = models.Event(name=event['title'],
                                      status=event_status,
                                      user=user)
            db.session.add(this_event)
            existing_events[event['title']] = event
            event_modified = True

        # Check if the event needs to be updated.
        if this_event.campaign != campaign:
            this_event.campaign = campaign
            event_modified = True
            
        for event_type in event_types:
            if event_type not in this_event.types:
                this_event.types.append(event_type)
                event_modified = True
                
        crits_created = parse(event['created']['$date'], ignoretz=True)
        crits_modified = parse(event['modified']['$date'], ignoretz=True)
        if not this_event.created_time:
            this_event.created_time = crits_created
            event_modified = True
        elif crits_created < this_event.created_time:
            this_event.created_time = crits_created
            event_modified = True
            
        if not this_event.modified_time:
            this_event.modified_time = crits_modified
        elif this_event.modified_time < crits_modified:
            this_event.modified_time = crits_modified
            event_modified = True
            
        if not this_event.description == event['description']:
            this_event.description = event['description']
            event_modified = True
            
        for reference in references:
            if reference not in this_event.references:
                this_event.references.append(reference)
                event_modified = True
                
        for tag in tags:
            if tag not in this_event.tags:
                this_event.tags.append(tag)
                event_modified = True
                
        for event_type in event_types:
            if event_type not in this_event.types:
                this_event.types.append(event_type)

        if event_modified:
            num_modified_events += 1

    db.session.commit()

    current_app.logger.info('CRITS IMPORT: Imported {}/{} events in {}'.format(num_modified_events, len(events), time.time() - start))


@cli.command()
def import_crits_indicators():
    """ Imports CRITS indicators from the exported MongoDB JSON """

    # Make sure the indicators.json file exists.
    if not os.path.exists('./import/indicators.json'):
        current_app.logger.error('Could not locate indicators.json for CRITS import')
        return

    start = time.time()
    with open('./import/indicators.json') as f:
        indicators = json.load(f)
    current_app.logger.info('CRITS IMPORT: Loaded indicators.json in {}'.format(time.time() - start))

    # Validate the indicators JSON.
    crits_create_schema = {
        'type': 'array',
        'items': {
            'type': 'object',
            'properties': {
                'bucket_list': {
                    'type': 'array',
                    'items': {'type': 'string', 'maxLength': 255}
                },
                'campaign': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'name': {'type': 'string', 'maxLength': 255}
                        }
                    }
                },
                'confidence': {
                    'type': 'object',
                    'properties': {
                        'rating': {'type': 'string', 'minLength': 1, 'maxLength': 255}
                    }
                },
                'created': {
                    'type': 'object',
                    'properties': {
                        '$date': {'type': 'string', 'minLength': 24, 'maxLength': 24}
                    }
                },
                'impact': {
                    'type': 'object',
                    'properties': {
                        'rating': {'type': 'string', 'minLength': 1, 'maxLength': 255}
                    }
                },
                'modified': {
                    'type': 'object',
                    'properties': {
                        '$date': {'type': 'string', 'minLength': 24, 'maxLength': 24}
                    }
                },
                'source': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'instances': {
                                'type': 'array',
                                'items': {
                                    'type': 'object',
                                    'properties': {
                                        'analyst': {'type': 'string', 'minLength': 1, 'maxLength': 255},
                                        'reference': {'type': 'string', 'maxLength': 512}
                                    }
                                }
                            },
                            'name': {'type': 'string', 'minLength': 1, 'maxLength': 255}
                        }
                    }
                },
                'status': {'type': 'string', 'minLength': 1, 'maxLength': 255},
                'type': {'type': 'string', 'minLength': 1, 'maxLength': 255},
                'value': {'type': 'string', 'minLength': 1}
            },
            'required': ['confidence', 'created', 'impact', 'modified', 'source', 'status', 'type', 'value']
        }
    }
    start = time.time()
    jsonschema.validate(indicators, crits_create_schema)
    current_app.logger.info('CRITS IMPORT: Validated indicators.json in {}'.format(time.time() - start))

    # Connect to the database engine to issue faster select statements.
    with db.engine.connect() as conn:

        # Get the existing indicators from the database.
        start = time.time()
        j = models.Indicator.__table__.join(models.IndicatorType,
                                            models.Indicator.type_id == models.IndicatorType.id)
        results = conn.execute(db.select([models.IndicatorType.value, models.Indicator.value]).select_from(j)).fetchall()
        existing_indicators = dict()  # type: value
        for result in results:
            if result[0] not in existing_indicators:
                existing_indicators[result[0]] = []
            existing_indicators[result[0]].append(result[1])

        # Get the existing values from the database that indicators depend upon.
        existing_campaigns = dict()
        for x in models.Campaign.query.all():
            existing_campaigns[x.name] = x

        existing_indicator_confidence = dict()
        for x in models.IndicatorConfidence.query.all():
            existing_indicator_confidence[x.value] = x

        existing_indicator_impact = dict()
        for x in models.IndicatorImpact.query.all():
            existing_indicator_impact[x.value] = x

        existing_indicator_status = dict()
        for x in models.IndicatorStatus.query.all():
            existing_indicator_status[x.value] = x

        existing_indicator_type = dict()
        for x in models.IndicatorType.query.all():
            existing_indicator_type[x.value] = x

        existing_intel_reference = dict()  # source: reference: object
        for x in models.IntelReference.query.all():
            if x.source.value not in existing_intel_reference:
                existing_intel_reference[x.source.value] = dict()
            existing_intel_reference[x.source.value][x.reference] = x

        existing_intel_source = dict()
        for x in models.IntelSource.query.all():
            existing_intel_source[x.value] = x

        existing_tags = dict()
        for x in models.Tag.query.all():
            existing_tags[x.value] = x

        existing_users = dict()
        for x in models.User.query.all():
            existing_users[x.username] = x

        num_new_indicators = 0
        unique_indicators = dict()  # type: value
        for indicator in indicators:

            # Skip this indicator if it is already in the database.
            if indicator['type'] in existing_indicators and indicator['value'] in existing_indicators[indicator['type']]:
                continue

            # Skip this indicator if it is a duplicate.
            if indicator['type'] not in unique_indicators:
                unique_indicators[indicator['type']] = []
            if indicator['value'] in unique_indicators[indicator['type']]:
                current_app.logger.warning('CRITS IMPORT: Skipping duplicate indicator: {}'.format(indicator['_id']['$oid']))
                continue
            else:
                unique_indicators[indicator['type']].append(indicator['value'])

            # Check if the indicator confidence must be created.
            if indicator['confidence']['rating'] in existing_indicator_confidence:
                indicator_confidence = existing_indicator_confidence[indicator['confidence']['rating']]
            else:
                new_indicator_confidence = models.IndicatorConfidence(value=indicator['confidence']['rating'])
                existing_indicator_confidence[new_indicator_confidence.value] = new_indicator_confidence
                indicator_confidence = new_indicator_confidence
                db.session.add(new_indicator_confidence)

            # Check if the indicator impact must be created.
            if indicator['impact']['rating'] in existing_indicator_impact:
                indicator_impact = existing_indicator_impact[indicator['impact']['rating']]
            else:
                new_indicator_impact = models.IndicatorImpact(value=indicator['impact']['rating'])
                existing_indicator_impact[new_indicator_impact.value] = new_indicator_impact
                indicator_impact = new_indicator_impact
                db.session.add(new_indicator_impact)

            # Check if the indicator status must be created.
            if indicator['status'] in existing_indicator_status:
                indicator_status = existing_indicator_status[indicator['status']]
            else:
                new_indicator_status = models.IndicatorStatus(value=indicator['status'])
                existing_indicator_status[new_indicator_status.value] = new_indicator_status
                indicator_status = new_indicator_status
                db.session.add(new_indicator_status)

            # Check if the indicator type must be created.
            if indicator['type'] in existing_indicator_type:
                indicator_type = existing_indicator_type[indicator['type']]
            else:
                new_indicator_type = models.IndicatorType(value=indicator['type'])
                existing_indicator_type[new_indicator_type.value] = new_indicator_type
                indicator_type = new_indicator_type
                db.session.add(new_indicator_type)

            # Check if the user must be created.
            username = indicator['source'][0]['instances'][0]['analyst']
            if username in existing_users:
                user = existing_users[username]
            else:
                password = ''.join(random.choice(string.ascii_letters + string.punctuation + string.digits) for x in range(20))
                new_user = models.User(active=False,
                                       email='{}@unknown'.format(username),
                                       first_name=username,
                                       last_name='Unknown',
                                       password=hash_password(password),
                                       roles=[],
                                       username=username)
                existing_users[username] = new_user
                user = new_user
                db.session.add(new_user)

            # Create the campaigns list.
            campaigns = []
            if 'campaign' in indicator and indicator['campaign']:
                for campaign in indicator['campaign']:
                    campaigns.append(existing_campaigns[campaign['name']])

            # Create the intel references list.
            references = []
            for s in indicator['source']:

                # Check if the source must be created.
                if s['name'] in existing_intel_source:
                    source = existing_intel_source[s['name']]
                else:
                    source = models.IntelSource(value=s['name'])
                    existing_intel_source[s['name']] = source
                    db.session.add(source)

                # Make sure the source exists in the intel reference dictionary.
                if source.value not in existing_intel_reference:
                    existing_intel_reference[source.value] = dict()

                for instance in s['instances']:

                    # Check if the reference must be created.
                    if 'reference' in instance and source.value in existing_intel_reference and instance['reference'] in existing_intel_reference[source.value]:
                        references.append(existing_intel_reference[source.value][instance['reference']])
                    elif 'reference' in instance and instance['reference']:
                        new_reference = models.IntelReference(reference=instance['reference'],
                                                              source=source,
                                                              user=user)
                        existing_intel_reference[source.value][instance['reference']] = new_reference
                        references.append(new_reference)
                        db.session.add(new_reference)

            # Create the tags list.
            tags = []
            if 'bucket_list' in indicator and indicator['bucket_list']:
                for tag in indicator['bucket_list']:

                    # Check if the tag must be created.
                    if tag in existing_tags:
                        tags.append(existing_tags[tag])
                    else:
                        new_tag = models.Tag(value=tag)
                        existing_tags[tag] = new_tag
                        tags.append(new_tag)
                        db.session.add(new_tag)

            # Create the new indicator.
            new_indicator = models.Indicator(campaigns=campaigns,
                                             case_sensitive=False,
                                             confidence=indicator_confidence,
                                             created_time=parse(indicator['created']['$date']),
                                             impact=indicator_impact,
                                             modified_time=parse(indicator['modified']['$date']),
                                             references=references,
                                             status=indicator_status,
                                             substring=False,
                                             tags=tags,
                                             type=indicator_type,
                                             user=user,
                                             value=indicator['value'])
            db.session.add(new_indicator)
            num_new_indicators += 1

    # Save any database changes.
    db.session.commit()

    current_app.logger.info('CRITS IMPORT: Imported {}/{} indicators in {}'.format(num_new_indicators, len(indicators), time.time() - start))


@cli.command()
def import_crits_campaigns():
    """ Imports CRITS campaigns from the exported MongoDB JSON """

    # Make sure the campaigns.json file exists.
    if not os.path.exists('./import/campaigns.json'):
        current_app.logger.error('Could not locate campaigns.json for CRITS import')
        return

    start = time.time()
    with open('./import/campaigns.json') as f:
        campaigns = json.load(f)
    current_app.logger.info('CRITS IMPORT: Loaded campaigns.json in {}'.format(time.time() - start))

    # Validate the campaigns JSON.
    crits_create_schema = {
        'type': 'array',
        'items': {
            'type': 'object',
            'properties': {
                'aliases': {
                    'type': 'array',
                    'items': {'type': 'string', 'maxLength': 255}
                },
                'created': {
                    'type': 'object',
                    'properties': {
                        '$date': {'type': 'string', 'minLength': 24, 'maxLength': 24}
                    }
                },
                'modified': {
                    'type': 'object',
                    'properties': {
                        '$date': {'type': 'string', 'minLength': 24, 'maxLength': 24}
                    }
                },
                'name': {'type': 'string', 'minLength': 1, 'maxLength': 255}
            },
            'required': ['aliases', 'created', 'modified', 'name']
        }
    }
    start = time.time()
    jsonschema.validate(campaigns, crits_create_schema)
    current_app.logger.info('CRITS IMPORT: Validated campaigns.json in {}'.format(time.time() - start))

    # Connect to the database engine to issue faster select statements.
    with db.engine.connect() as conn:

        # Get the existing campaigns and campaign aliases from the database.
        start = time.time()
        existing_campaigns = [x[0] for x in conn.execute(db.select([models.Campaign.name])).fetchall()]
        existing_campaign_aliases = [x[0] for x in conn.execute(db.select([models.CampaignAlias.alias])).fetchall()]

        num_new_campaigns = 0
        unique_campaigns = []
        unique_campaign_aliases = []
        for campaign in campaigns:

            # Skip this campaign if it is already in the database.
            if campaign['name'] in existing_campaigns:
                continue

            # Skip this campaign if it is a duplicate.
            if campaign['name'] in unique_campaigns:
                current_app.logger.warning('CRITS IMPORT: Skipping duplicate campaign: {}'.format(campaign['name']))
                continue
            else:
                unique_campaigns.append(campaign['name'])

            # Create and add the new campaign.
            new_campaign = models.Campaign(name=campaign['name'],
                                           created_time=parse(campaign['created']['$date']),
                                           modified_time=parse(campaign['modified']['$date']))
            db.session.add(new_campaign)
            num_new_campaigns += 1

            if 'aliases' in campaign and campaign['aliases']:
                for alias in campaign['aliases']:

                    # Skip this campaign alias if it is already in the database.
                    if alias in existing_campaign_aliases:
                        continue

                    # Skip this campaign alias if it is a duplicate.
                    if alias in unique_campaign_aliases:
                        continue
                    else:
                        unique_campaign_aliases.append(alias)

                    # Create and add the new campaign alias.
                    new_campaign_alias = models.CampaignAlias(alias=alias, campaign=new_campaign)
                    db.session.add(new_campaign_alias)

    # Save any database changes.
    db.session.commit()

    current_app.logger.info('CRITS IMPORT: Imported {}/{} campaigns in {}'.format(num_new_campaigns, len(campaigns), time.time() - start))


@cli.command()
@click.option('--yes', is_flag=True, expose_value=False, prompt='Are you sure?')
def setupdb():
    """ Destroys and recreates the database. CAUTION! """

    db.drop_all()
    db.create_all()
    db.session.commit()


@cli.command()
def test():
    """ Runs the tests without code coverage"""

    tests = unittest.TestLoader().discover('project/tests', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1


@cli.command()
def seeddb():
    """ Seeds the database with the values in the setup.ini file """

    # Load the setup.ini config file
    config_path = os.path.join(HOME_DIR, 'etc', 'setup.ini')
    if not os.path.exists(config_path):
        raise FileNotFoundError('Unable to locate setup.ini at: {}'.format(config_path))
    config = configparser.ConfigParser(allow_no_value=True)
    config.optionxform = str  # This preserves case-sensitivity for the values
    config.read(config_path)

    # Admin role
    if not models.Role.query.filter_by(name='admin').first():
        admin_role = models.Role(name='admin')
        db.session.add(admin_role)
        db.session.commit()
        app.logger.info('SETUP: Created user role: admin')

    # Analyst role
    if not models.Role.query.filter_by(name='analyst').first():
        analyst_role = models.Role(name='analyst')
        db.session.add(analyst_role)
        db.session.commit()
        app.logger.info('SETUP: Created user role: analyst')

    # Create the event attack vectors
    for value in config['event_attack_vector']:
        if not models.EventAttackVector.query.filter_by(value=value).first():
            db.session.add(models.EventAttackVector(value=value))
            db.session.commit()
            app.logger.info('SETUP: Created event attack vector: {}'.format(value))

    # Create the event dispositions
    for value in config['event_disposition']:
        if not models.EventDisposition.query.filter_by(value=value).first():
            db.session.add(models.EventDisposition(value=value))
            db.session.commit()
            app.logger.info('SETUP: Created event disposition: {}'.format(value))

    # Create the event prevention tools
    for value in config['event_prevention_tool']:
        if not models.EventPreventionTool.query.filter_by(value=value).first():
            db.session.add(models.EventPreventionTool(value=value))
            db.session.commit()
            app.logger.info('SETUP: Created event prevention tool: {}'.format(value))

    # Create the event remediations
    for value in config['event_remediation']:
        if not models.EventRemediation.query.filter_by(value=value).first():
            db.session.add(models.EventRemediation(value=value))
            db.session.commit()
            app.logger.info('SETUP: Created event remediation: {}'.format(value))

    # Create the event statuses
    for value in config['event_status']:
        if not models.EventStatus.query.filter_by(value=value).first():
            db.session.add(models.EventStatus(value=value))
            db.session.commit()
            app.logger.info('SETUP: Created event status: {}'.format(value))

    # Create the event types
    for value in config['event_type']:
        if not models.EventType.query.filter_by(value=value).first():
            db.session.add(models.EventType(value=value))
            db.session.commit()
            app.logger.info('SETUP: Created event type: {}'.format(value))

    # Create the indicator confidences
    for value in config['indicator_confidence']:
        if not models.IndicatorConfidence.query.filter_by(value=value).first():
            db.session.add(models.IndicatorConfidence(value=value))
            db.session.commit()
            app.logger.info('SETUP: Created indicator confidence: {}'.format(value))

    # Create the indicator impacts
    for value in config['indicator_impact']:
        if not models.IndicatorImpact.query.filter_by(value=value).first():
            db.session.add(models.IndicatorImpact(value=value))
            db.session.commit()
            app.logger.info('SETUP: Created indicator impact: {}'.format(value))

    # Create the indicator statuses
    for value in config['indicator_status']:
        if not models.IndicatorStatus.query.filter_by(value=value).first():
            db.session.add(models.IndicatorStatus(value=value))
            db.session.commit()
            app.logger.info('SETUP: Created indicator status: {}'.format(value))

    # Create the indicator types
    for value in config['indicator_type']:
        if not models.IndicatorType.query.filter_by(value=value).first():
            db.session.add(models.IndicatorType(value=value))
            db.session.commit()
            app.logger.info('SETUP: Created indicator type: {}'.format(value))

    # Create the intel sources
    for value in config['intel_source']:
        if not models.IntelSource.query.filter_by(value=value).first():
            db.session.add(models.IntelSource(value=value))
            db.session.commit()
            app.logger.info('SETUP: Created intel source: {}'.format(value))

    # Create the malware types
    for value in config['malware_type']:
        if not models.MalwareType.query.filter_by(value=value).first():
            db.session.add(models.MalwareType(value=value))
            db.session.commit()
            app.logger.info('SETUP: Created malware type: {}'.format(value))

    # Admin user
    if not models.User.query.filter_by(username='admin').first():
        user_datastore = SQLAlchemyUserDatastore(db, models.User, models.Role)
        password = ''.join(random.choice(string.ascii_letters + string.punctuation + string.digits) for x in range(20))
        admin_role = models.Role.query.filter_by(name='admin').first()
        user_datastore.create_user(email='admin@localhost', password=hash_password(password), username='admin', first_name='Admin', last_name='Admin', roles=[admin_role, analyst_role])
        db.session.commit()
        app.logger.info('SETUP: Created admin user with password: {}'.format(password))


if __name__ == '__main__':
    cli()
