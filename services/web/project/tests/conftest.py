import pytest

from flask_security import SQLAlchemyUserDatastore
from flask_security.utils import hash_password

from project import create_app
from project import db as _db
from project.models import Role, User

TEST_INACTIVE_APIKEY = '11111111-1111-1111-1111-111111111111'
TEST_ADMIN_APIKEY = '22222222-2222-2222-2222-222222222222'
TEST_ANALYST_APIKEY = '33333333-3333-3333-3333-333333333333'
TEST_INVALID_APIKEY = '99999999-9999-9999-9999-999999999999'


@pytest.fixture(scope='session')
def app():

    _app = create_app()
    _app.config.from_object('project.config.TestingConfig')

    ctx = _app.app_context()
    ctx.push()

    yield _app

    ctx.pop()


@pytest.fixture(scope='session')
def client(app):
    return app.test_client()


@pytest.fixture(scope='session')
def db(app):
    _db.app = app
    _db.create_all()

    # Admin role
    if not Role.query.filter_by(name='admin').first():
        admin_role = Role(name='admin')
        _db.session.add(admin_role)

    # Analyst role
    if not Role.query.filter_by(name='analyst').first():
        analyst_role = Role(name='analyst')
        _db.session.add(analyst_role)

    # Inactive user
    if not User.query.filter_by(username='inactive').first():
        user_datastore = SQLAlchemyUserDatastore(_db, User, Role)
        analyst_role = Role.query.filter_by(name='analyst').first()
        user_datastore.create_user(email='inactive@localhost', password=hash_password('inactive'), username='inactive',
                                   first_name='Inactive', last_name='Inactive', roles=[analyst_role])
        inactive_user = User.query.filter_by(username='inactive').first()
        inactive_user.active = False
        inactive_user.apikey = TEST_INACTIVE_APIKEY

    # Admin user
    if not User.query.filter_by(username='admin').first():
        user_datastore = SQLAlchemyUserDatastore(_db, User, Role)
        admin_role = Role.query.filter_by(name='admin').first()
        user_datastore.create_user(email='admin@localhost', password=hash_password('admin'), username='admin',
                                   first_name='Admin', last_name='Admin', roles=[admin_role])
        admin_user = User.query.filter_by(username='admin').first()
        admin_user.apikey = TEST_ADMIN_APIKEY

    # Analyst user
    if not User.query.filter_by(username='analyst').first():
        user_datastore = SQLAlchemyUserDatastore(_db, User, Role)
        analyst_role = Role.query.filter_by(name='analyst').first()
        user_datastore.create_user(email='analyst@localhost', password=hash_password('analyst'), username='analyst',
                                   first_name='Analyst', last_name='Analyst', roles=[analyst_role])
        analyst_user = User.query.filter_by(username='analyst').first()
        analyst_user.apikey = TEST_ANALYST_APIKEY

    _db.session.commit()

    yield _db

    _db.drop_all()


@pytest.fixture(scope='function', autouse=True)
def session(app, db):
    app.config['POST'] = None
    app.config['GET'] = None
    app.config['PUT'] = None
    app.config['DELETE'] = None

    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    _session = db.create_scoped_session(options=options)

    db.session = _session

    yield _session

    transaction.rollback()
    connection.close()
    _session.remove()
