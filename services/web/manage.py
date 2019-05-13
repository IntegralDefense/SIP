import click
import configparser
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
def import_crits_indicators():
    """ Imports CRITS indicators from the exported MongoDB JSON """

    # Make sure the indicators.json file exists.
    if not os.path.exists('./import/indicators.json'):
        current_app.logger.error('Could not locate indicators.json for CRITS import')
        return

    # Validate the indicators JSON.
    crits_create_schema = {
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

    start = time.time()

    # Connect to the database engine to issue faster select statements.
    with db.engine.connect() as conn:

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

        line_count = 0

        with open('./import/indicators.json') as f:
            for line in f:
                indicator = json.loads(line)
                jsonschema.validate(indicator, crits_create_schema)

                line_count += 1

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
                    db.session.flush()

                # Check if the indicator impact must be created.
                if indicator['impact']['rating'] in existing_indicator_impact:
                    indicator_impact = existing_indicator_impact[indicator['impact']['rating']]
                else:
                    new_indicator_impact = models.IndicatorImpact(value=indicator['impact']['rating'])
                    existing_indicator_impact[new_indicator_impact.value] = new_indicator_impact
                    indicator_impact = new_indicator_impact
                    db.session.add(new_indicator_impact)
                    db.session.flush()

                # Check if the indicator status must be created.
                if indicator['status'] in existing_indicator_status:
                    indicator_status = existing_indicator_status[indicator['status']]
                else:
                    new_indicator_status = models.IndicatorStatus(value=indicator['status'])
                    existing_indicator_status[new_indicator_status.value] = new_indicator_status
                    indicator_status = new_indicator_status
                    db.session.add(new_indicator_status)
                    db.session.flush()

                # Check if the indicator type must be created.
                if indicator['type'] in existing_indicator_type:
                    indicator_type = existing_indicator_type[indicator['type']]
                else:
                    new_indicator_type = models.IndicatorType(value=indicator['type'])
                    existing_indicator_type[new_indicator_type.value] = new_indicator_type
                    indicator_type = new_indicator_type
                    db.session.add(new_indicator_type)
                    db.session.flush()

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
                    db.session.flush()

                # Create the campaigns list.
                campaigns = set()
                if 'campaign' in indicator and indicator['campaign']:
                    for campaign in indicator['campaign']:
                        campaigns.add(existing_campaigns[campaign['name']])

                # Create the intel references list.
                references = set()
                for s in indicator['source']:

                    # Check if the source must be created.
                    if s['name'] in existing_intel_source:
                        source = existing_intel_source[s['name']]
                    else:
                        source = models.IntelSource(value=s['name'])
                        existing_intel_source[s['name']] = source
                        db.session.add(source)
                        db.session.flush()

                    # Make sure the source exists in the intel reference dictionary.
                    if source.value not in existing_intel_reference:
                        existing_intel_reference[source.value] = dict()

                    for instance in s['instances']:

                        # Check if the reference must be created.
                        if 'reference' in instance and source.value in existing_intel_reference and instance['reference'] in existing_intel_reference[source.value]:
                            references.add(existing_intel_reference[source.value][instance['reference']])
                        elif 'reference' in instance and instance['reference']:
                            new_reference = models.IntelReference(reference=instance['reference'],
                                                                  source=source,
                                                                  user=user)
                            existing_intel_reference[source.value][instance['reference']] = new_reference
                            references.add(new_reference)
                            db.session.add(new_reference)
                            db.session.flush()

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
                            db.session.flush()

                # Create the new indicator.
                try:
                    new_indicator = models.Indicator(campaigns=list(campaigns),
                                                     case_sensitive=False,
                                                     confidence=indicator_confidence,
                                                     created_time=parse(indicator['created']['$date']),
                                                     impact=indicator_impact,
                                                     modified_time=parse(indicator['modified']['$date']),
                                                     references=list(references),
                                                     status=indicator_status,
                                                     substring=False,
                                                     tags=tags,
                                                     type=indicator_type,
                                                     user=user,
                                                     value=indicator['value'])
                    db.session.add(new_indicator)
                    num_new_indicators += 1
                except Exception as e:
                    current_app.logger.exception("CRITS IMPORT: unable to import indicator {}: {}".format(indicator, e))
                    #db.session.rollback()

    # Save any database changes.
    db.session.commit()
    current_app.logger.info('CRITS IMPORT: Imported {}/{} indicators in {}'.format(num_new_indicators, line_count, time.time() - start))

@cli.command()
def import_crits_campaigns():
    """ Imports CRITS campaigns from the exported MongoDB JSON """

    # Make sure the campaigns.json file exists.
    if not os.path.exists('./import/campaigns.json'):
        current_app.logger.error('Could not locate campaigns.json for CRITS import')
        return

    # Validate the campaigns JSON.
    crits_create_schema = {
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

    start = time.time()

    # Connect to the database engine to issue faster select statements.
    with db.engine.connect() as conn:

        # Get the existing campaigns and campaign aliases from the database.
        existing_campaigns = [x[0] for x in conn.execute(db.select([models.Campaign.name])).fetchall()]
        existing_campaign_aliases = [x[0] for x in conn.execute(db.select([models.CampaignAlias.alias])).fetchall()]

        num_new_campaigns = 0
        unique_campaigns = []
        unique_campaign_aliases = []
        line_count = 0

        with open('./import/campaigns.json') as f:
            for line in f:
                campaign = json.loads(line)
                jsonschema.validate(campaign, crits_create_schema)

                line_count += 1

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

    current_app.logger.info('CRITS IMPORT: Imported {}/{} campaigns in {}'.format(num_new_campaigns, line_count, time.time() - start))


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

    # Admin user
    if not models.User.query.filter_by(username='admin').first():
        user_datastore = SQLAlchemyUserDatastore(db, models.User, models.Role)
        password = ''.join(random.choice(string.ascii_letters + string.punctuation + string.digits) for x in range(20))
        admin_role = models.Role.query.filter_by(name='admin').first()
        user_datastore.create_user(email='admin@localhost', password=hash_password(password), username='admin', first_name='Admin', last_name='Admin', roles=[admin_role, analyst_role])
        db.session.commit()
        admin = models.User.query.filter_by(username='admin').first()
        app.logger.info('SETUP: Created admin user with password: {}'.format(password))
        app.logger.info('SETUP: Created admin user with API key: {}'.format(admin.apikey))


if __name__ == '__main__':
    cli()
