import configparser
import os
import random
import string
import unittest

from flask.cli import FlaskGroup
from flask_security import SQLAlchemyUserDatastore
from flask_security.utils import hash_password

from lib.constants import HOME_DIR
from project import create_app, db, models

app = create_app()
cli = FlaskGroup(create_app=create_app)


@cli.command()
def nukedb():
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
def setup():
    """ Configures the database with the values in the setup.ini file """

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
        user_datastore.create_user(email='admin@localhost', password=hash_password(password), username='admin', first_name='Admin', last_name='Admin', roles=[admin_role])
        db.session.commit()
        admin = models.User.query.filter_by(username='admin').first()
        app.logger.info('SETUP: Created admin user with password: {}'.format(password))
        app.logger.info('SETUP: Created admin user with API key: {}'.format(admin.apikey))

if __name__ == '__main__':
    cli()
