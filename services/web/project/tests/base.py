import configparser
import os
import uuid

from flask_security import SQLAlchemyUserDatastore
from flask_security.utils import hash_password
from flask_testing import TestCase

from lib.constants import HOME_DIR
from project import create_app, db, models

# Load the setup.ini config file
config_path = os.path.join(HOME_DIR, 'etc', 'setup.ini')
if not os.path.exists(config_path):
    raise FileNotFoundError('Unable to locate setup.ini at: {}'.format(config_path))
config = configparser.ConfigParser(allow_no_value=True)
config.optionxform = str  # This preserves case-sensitivity for the values
config.read(config_path)

TEST_APIKEY = '11111111-1111-1111-1111-111111111111'
TEST_ADMIN_APIKEY = '22222222-2222-2222-2222-222222222222'
TEST_ANALYST_APIKEY = '33333333-3333-3333-3333-333333333333'
TEST_INVALID_APIKEY = '99999999-9999-9999-9999-999999999999'

app = create_app()


class BaseTestCase(TestCase):
    def create_app(self):
        app.config.from_object('project.config.TestingConfig')
        return app

    def setUp(self):
        """ Configures the database with the values in the setup.ini file """

        # Create the database schema
        db.create_all()
        db.session.commit()

        """
        # Load the setup.ini config file
        config_path = os.path.join(HOME_DIR, 'etc', 'setup.ini')
        if not os.path.exists(config_path):
            raise FileNotFoundError('Unable to locate setup.ini at: {}'.format(config_path))
        config = configparser.ConfigParser(allow_no_value=True)
        config.optionxform = str  # This preserves case-sensitivity for the values
        config.read(config_path)
        """

        # Admin role
        if not models.Role.query.filter_by(name='admin').first():
            admin_role = models.Role(name='admin')
            db.session.add(admin_role)
            db.session.commit()

        # Analyst role
        if not models.Role.query.filter_by(name='analyst').first():
            analyst_role = models.Role(name='analyst')
            db.session.add(analyst_role)
            db.session.commit()

        # Test user
        if not models.User.query.filter_by(username='test').first():
            user_datastore = SQLAlchemyUserDatastore(db, models.User, models.Role)
            password = 'test'
            admin_role = models.Role.query.filter_by(name='admin').first()
            analyst_role = models.Role.query.filter_by(name='analyst').first()
            user_datastore.create_user(email='test@localhost', password=hash_password(password), username='test',
                                       first_name='Test', last_name='Test', roles=[admin_role, analyst_role])
            db.session.commit()
            test_user = models.User.query.filter_by(username='test').first()
            test_user.apikey = uuid.UUID(TEST_APIKEY)
            db.session.commit()

        # Admin user
        if not models.User.query.filter_by(username='admin').first():
            user_datastore = SQLAlchemyUserDatastore(db, models.User, models.Role)
            password = 'admin'
            admin_role = models.Role.query.filter_by(name='admin').first()
            user_datastore.create_user(email='admin@localhost', password=hash_password(password), username='admin',
                                       first_name='Admin', last_name='Admin', roles=[admin_role])
            db.session.commit()
            admin_user = models.User.query.filter_by(username='admin').first()
            admin_user.apikey = uuid.UUID(TEST_ADMIN_APIKEY)
            db.session.commit()

        # Analyst user
        if not models.User.query.filter_by(username='analyst').first():
            user_datastore = SQLAlchemyUserDatastore(db, models.User, models.Role)
            password = 'analyst'
            analyst_role = models.Role.query.filter_by(name='analyst').first()
            user_datastore.create_user(email='analyst@localhost', password=hash_password(password), username='analyst',
                                       first_name='Analyst', last_name='Analyst', roles=[analyst_role])
            db.session.commit()
            analyst_user = models.User.query.filter_by(username='analyst').first()
            analyst_user.apikey = uuid.UUID(TEST_ANALYST_APIKEY)
            db.session.commit()

        """
        # Create the event attack vectors
        for value in config['event_attack_vector']:
            if not models.EventAttackVector.query.filter_by(value=value).first():
                db.session.add(models.EventAttackVector(value=value))
                db.session.commit()

        # Create the event dispositions
        for value in config['event_disposition']:
            if not models.EventDisposition.query.filter_by(value=value).first():
                db.session.add(models.EventDisposition(value=value))
                db.session.commit()

        # Create the event prevention tools
        for value in config['event_prevention_tool']:
            if not models.EventPreventionTool.query.filter_by(value=value).first():
                db.session.add(models.EventPreventionTool(value=value))
                db.session.commit()

        # Create the event remediations
        for value in config['event_remediation']:
            if not models.EventRemediation.query.filter_by(value=value).first():
                db.session.add(models.EventRemediation(value=value))
                db.session.commit()

        # Create the event statuses
        for value in config['event_status']:
            if not models.EventStatus.query.filter_by(value=value).first():
                db.session.add(models.EventStatus(value=value))
                db.session.commit()

        # Create the event types
        for value in config['event_type']:
            if not models.EventType.query.filter_by(value=value).first():
                db.session.add(models.EventType(value=value))
                db.session.commit()

        # Create the indicator confidences
        for value in config['indicator_confidence']:
            if not models.IndicatorConfidence.query.filter_by(value=value).first():
                db.session.add(models.IndicatorConfidence(value=value))
                db.session.commit()

        # Create the indicator impacts
        for value in config['indicator_impact']:
            if not models.IndicatorImpact.query.filter_by(value=value).first():
                db.session.add(models.IndicatorImpact(value=value))
                db.session.commit()

        # Create the indicator statuses
        for value in config['indicator_status']:
            if not models.IndicatorStatus.query.filter_by(value=value).first():
                db.session.add(models.IndicatorStatus(value=value))
                db.session.commit()

        # Create the indicator types
        for value in config['indicator_type']:
            if not models.IndicatorType.query.filter_by(value=value).first():
                db.session.add(models.IndicatorType(value=value))
                db.session.commit()

        # Create the intel sources
        for value in config['intel_source']:
            if not models.IntelSource.query.filter_by(value=value).first():
                db.session.add(models.IntelSource(value=value))
                db.session.commit()

        # Create the malware types
        for value in config['malware_type']:
            if not models.MalwareType.query.filter_by(value=value).first():
                db.session.add(models.MalwareType(value=value))
                db.session.commit()
        """

    def tearDown(self):
        db.session.remove()
        db.drop_all()
