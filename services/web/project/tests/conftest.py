import pytest

from project import create_app, db


@pytest.fixture(scope='module')
def client():
    app = create_app()
    app.config.from_object('project.config.TestingConfig')
    app.config['POST'] = None
    app.config['GET'] = None
    app.config['PUT'] = None
    app.config['DELETE'] = None

    client = app.test_client()

    ctx = app.app_context()
    ctx.push()

    yield client

    ctx.pop()


@pytest.fixture(scope='module')
def db():
    db.drop_all()
    db.create_all()

    yield db

    db.drop_all()


@pytest.fixture(scope='function')
def session(db, request):
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)

    db.session = session

    def teardown():
        transaction.rollback()
        connection.close()
        session.remove()

    request.addfinalizer(teardown)
    return session
