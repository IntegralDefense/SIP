import uuid

from flask_security import SQLAlchemyUserDatastore
from flask_security.utils import hash_password
from flask_testing import TestCase

from project import create_app, db, models


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

        # Admin role
        if not models.Role.query.filter_by(name='admin').first():
            admin_role = models.Role(name='admin')
            db.session.add(admin_role)

        # Analyst role
        if not models.Role.query.filter_by(name='analyst').first():
            analyst_role = models.Role(name='analyst')
            db.session.add(analyst_role)

        # Test user
        if not models.User.query.filter_by(username='test').first():
            user_datastore = SQLAlchemyUserDatastore(db, models.User, models.Role)
            admin_role = models.Role.query.filter_by(name='admin').first()
            analyst_role = models.Role.query.filter_by(name='analyst').first()
            user_datastore.create_user(email='test@localhost', password=hash_password('test'), username='test',
                                       first_name='Test', last_name='Test', roles=[admin_role, analyst_role])
            test_user = models.User.query.filter_by(username='test').first()
            test_user.apikey = uuid.UUID(TEST_APIKEY)

        # Admin user
        if not models.User.query.filter_by(username='admin').first():
            user_datastore = SQLAlchemyUserDatastore(db, models.User, models.Role)
            admin_role = models.Role.query.filter_by(name='admin').first()
            user_datastore.create_user(email='admin@localhost', password=hash_password('admin'), username='admin',
                                       first_name='Admin', last_name='Admin', roles=[admin_role])
            admin_user = models.User.query.filter_by(username='admin').first()
            admin_user.apikey = uuid.UUID(TEST_ADMIN_APIKEY)

        # Analyst user
        if not models.User.query.filter_by(username='analyst').first():
            user_datastore = SQLAlchemyUserDatastore(db, models.User, models.Role)
            analyst_role = models.Role.query.filter_by(name='analyst').first()
            user_datastore.create_user(email='analyst@localhost', password=hash_password('analyst'), username='analyst',
                                       first_name='Analyst', last_name='Analyst', roles=[analyst_role])
            analyst_user = models.User.query.filter_by(username='analyst').first()
            analyst_user.apikey = uuid.UUID(TEST_ANALYST_APIKEY)

        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
