import json

from project.tests.conftest import TEST_ADMIN_APIKEY, TEST_ANALYST_APIKEY, TEST_INVALID_APIKEY

"""
CREATE TESTS
"""


def test_create_missing_parameter(client):
    """ Ensure the required parameters are given """

    # Missing email
    data = {'apikey': TEST_ADMIN_APIKEY, 'first_name': 'asdf', 'last_name': 'asdf', 'password': 'asdf',
            'roles': 'asdf', 'username': 'asdf'}
    request = client.post('/api/users', data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'Request must include:' in response['message']

    # Missing first_name
    data = {'apikey': TEST_ADMIN_APIKEY, 'email': 'asdf', 'last_name': 'asdf', 'password': 'asdf',
            'roles': 'asdf', 'username': 'asdf'}
    request = client.post('/api/users', data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'Request must include:' in response['message']

    # Missing last_name
    data = {'apikey': TEST_ADMIN_APIKEY, 'email': 'asdf', 'first_name': 'asdf', 'password': 'asdf',
            'roles': 'asdf', 'username': 'asdf'}
    request = client.post('/api/users', data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'Request must include:' in response['message']

    # Missing password
    data = {'apikey': TEST_ADMIN_APIKEY, 'email': 'asdf', 'first_name': 'asdf', 'last_name': 'asdf',
            'roles': 'asdf', 'username': 'asdf'}
    request = client.post('/api/users', data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'Request must include:' in response['message']

    # Missing roles
    data = {'apikey': TEST_ADMIN_APIKEY, 'email': 'asdf', 'first_name': 'asdf', 'last_name': 'asdf',
            'password': 'asdf', 'username': 'asdf'}
    request = client.post('/api/users', data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'Request must include:' in response['message']

    # Missing username
    data = {'apikey': TEST_ADMIN_APIKEY, 'email': 'asdf', 'first_name': 'asdf', 'last_name': 'asdf',
            'password': 'asdf', 'roles': 'asdf'}
    request = client.post('/api/users', data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'Request must include:' in response['message']


def test_create_duplicate(client):
    """ Ensure a duplicate record cannot be created """

    data = {'apikey': TEST_ADMIN_APIKEY, 'email': 'asdf', 'first_name': 'asdf', 'last_name': 'asdf',
            'password': 'asdf', 'roles': 'analyst', 'username': 'asdf'}
    request = client.post('/api/users', data=data)
    assert request.status_code == 201

    # Try making a duplicate email
    data = {'apikey': TEST_ADMIN_APIKEY, 'email': 'asdf', 'first_name': 'asdf', 'last_name': 'asdf',
            'password': 'asdf', 'roles': 'analyst', 'username': 'asdf2'}
    request = client.post('/api/users', data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 409
    assert response['message'] == 'User email already exists'

    # Try making a duplicate username
    data = {'apikey': TEST_ADMIN_APIKEY, 'email': 'asdf2', 'first_name': 'asdf', 'last_name': 'asdf',
            'password': 'asdf', 'roles': 'analyst', 'username': 'asdf'}
    request = client.post('/api/users', data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 409
    assert response['message'] == 'User username already exists'


def test_create_missing_api_key(client):
    """ Ensure an API key is given if the config requires it """

    data = {'email': 'asdf', 'first_name': 'asdf', 'last_name': 'asdf', 'password': 'asdf', 'roles': 'asdf',
            'username': 'asdf'}
    request = client.post('/api/users', data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['message'] == 'Bad or missing API key'


def test_create_invalid_api_key(client):
    """ Ensure an API key not found in the database does not work """

    data = {'apikey': TEST_INVALID_APIKEY, 'email': 'asdf', 'first_name': 'asdf', 'last_name': 'asdf',
            'password': 'asdf', 'roles': 'asdf', 'username': 'asdf'}
    request = client.post('/api/users', data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['message'] == 'API user does not exist'


def test_create_invalid_role(client):
    """ Ensure the given API key has the proper role access """

    data = {'apikey': TEST_ANALYST_APIKEY, 'email': 'asdf', 'first_name': 'asdf', 'last_name': 'asdf',
            'password': 'asdf', 'roles': 'asdf', 'username': 'asdf'}
    request = client.post('/api/users', data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['message'] == 'Insufficient privileges'


def test_create(client):
    """ Ensure a proper request actually works """

    # Try with a single roles string
    data = {'apikey': TEST_ADMIN_APIKEY, 'email': 'asdf', 'first_name': 'asdf', 'last_name': 'asdf',
            'password': 'asdf', 'roles': 'analyst', 'username': 'asdf'}
    request = client.post('/api/users', data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 201
    assert response['apikey']
    assert response['roles'] == ['analyst']
    assert response['username'] == 'asdf'

    # Try with a roles list
    data = {'apikey': TEST_ADMIN_APIKEY, 'email': 'asdf2', 'first_name': 'asdf', 'last_name': 'asdf',
            'password': 'asdf', 'roles': ['analyst', 'admin'], 'username': 'asdf2'}
    request = client.post('/api/users', data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 201
    assert response['apikey']
    assert response['roles'] == ['admin', 'analyst']
    assert response['username'] == 'asdf2'


"""
READ TESTS
"""


def test_read_nonexistent_id(client):
    """ Ensure a nonexistent ID does not work """

    request = client.get('/api/users/100000')
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['message'] == 'User ID not found'


def test_read_missing_api_key(app, client):
    """ Ensure an API key is given if the config requires it """

    app.config['GET'] = 'analyst'

    request = client.get('/api/users/1')
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['message'] == 'Bad or missing API key'


def test_read_invalid_api_key(app, client):
    """ Ensure an API key not found in the database does not work """

    app.config['GET'] = 'analyst'

    request = client.get('/api/users/1?apikey={}'.format(TEST_INVALID_APIKEY))
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['message'] == 'API user does not exist'


def test_read_invalid_role(app, client):
    """ Ensure the given API key has the proper role access """

    app.config['GET'] = 'user_does_not_have_this_role'

    request = client.get('/api/users/1?apikey={}'.format(TEST_ANALYST_APIKEY))
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['message'] == 'Insufficient privileges'


def test_read_all_values(client):
    """ Ensure all values properly return """

    request = client.get('/api/users')
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response) == 3


def test_read_by_id(client):
    """ Ensure names can be read by their ID """

    request = client.get('/api/users/1')
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == 1
    assert 'apikey' not in response


"""
UPDATE TESTS
"""


def test_update_nonexistent_id(client):
    """ Ensure a nonexistent ID does not work """

    data = {'apikey': TEST_ADMIN_APIKEY, 'email': 'asdf', 'first_name': 'asdf', 'last_name': 'asdf',
            'password': 'asdf', 'roles': ['analyst', 'admin'], 'username': 'asdf'}
    request = client.put('/api/users/100000', data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['message'] == 'User ID not found'


def test_update_missing_parameter(client):
    """ Ensure the required parameters are given """

    data = {'apikey': TEST_ADMIN_APIKEY}
    request = client.put('/api/users/1', data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'Request must include at least one of' in response['message']


def test_update_duplicate(client):
    """ Ensure duplicate records cannot be updated """

    data = {'apikey': TEST_ADMIN_APIKEY, 'email': 'asdf', 'first_name': 'asdf', 'last_name': 'asdf',
            'password': 'asdf', 'roles': 'analyst', 'username': 'asdf'}
    request = client.post('/api/users', data=data)
    response = json.loads(request.data.decode())
    _id = response['id']
    assert request.status_code == 201
    assert response['apikey']
    assert response['roles'] == ['analyst']
    assert response['username'] == 'asdf'

    # Try to update an existing email
    data = {'apikey': TEST_ADMIN_APIKEY, 'email': 'asdf'}
    request = client.put('/api/users/{}'.format(_id), data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 409
    assert response['message'] == 'User email already exists'

    # Try to update an existing username
    data = {'apikey': TEST_ADMIN_APIKEY, 'username': 'asdf'}
    request = client.put('/api/users/{}'.format(_id), data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 409
    assert response['message'] == 'User username already exists'


def test_update_missing_api_key(client):
    """ Ensure an API key is given if the config requires it """

    data = {'username': 'asdf'}
    request = client.put('/api/users/1', data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['message'] == 'Bad or missing API key'


def test_update_invalid_api_key(client):
    """ Ensure an API key not found in the database does not work """

    data = {'apikey': TEST_INVALID_APIKEY, 'username': 'asdf'}
    request = client.put('/api/users/1', data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['message'] == 'API user does not exist'


def test_update_invalid_role(client):
    """ Ensure the given API key has the proper role access """

    data = {'apikey': TEST_ANALYST_APIKEY, 'username': 'asdf'}
    request = client.put('/api/users/1', data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['message'] == 'Insufficient privileges'


def test_update(client):
    """ Ensure a proper request actually works """

    data = {'apikey': TEST_ADMIN_APIKEY, 'email': 'asdf', 'first_name': 'asdf', 'last_name': 'asdf',
            'password': 'asdf', 'roles': ['analyst', 'admin'], 'username': 'asdf'}
    request = client.post('/api/users', data=data)
    response = json.loads(request.data.decode())
    _id = response['id']
    orig_apikey = response['apikey']
    assert request.status_code == 201
    assert response['active'] is True
    assert response['roles'] == ['admin', 'analyst']

    # Update active
    data = {'apikey': TEST_ADMIN_APIKEY, 'active': False}
    request = client.put('/api/users/{}'.format(_id), data=data)
    assert request.status_code == 200

    request = client.get('/api/users/{}'.format(_id))
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert response['active'] is False

    # Update apikey
    data = {'apikey': TEST_ADMIN_APIKEY, 'apikey_refresh': True}
    request = client.put('/api/users/{}'.format(_id), data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['apikey']
    assert orig_apikey != response['apikey']

    # Update email
    data = {'apikey': TEST_ADMIN_APIKEY, 'email': 'asdf2'}
    request = client.put('/api/users/{}'.format(_id), data=data)
    assert request.status_code == 200

    request = client.get('/api/users/{}'.format(_id))
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert response['email'] == 'asdf2'

    # Update first_name
    data = {'apikey': TEST_ADMIN_APIKEY, 'first_name': 'asdf2'}
    request = client.put('/api/users/{}'.format(_id), data=data)
    assert request.status_code == 200

    request = client.get('/api/users/{}'.format(_id))
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert response['first_name'] == 'asdf2'

    # Update last_name
    data = {'apikey': TEST_ADMIN_APIKEY, 'last_name': 'asdf2'}
    request = client.put('/api/users/{}'.format(_id), data=data)
    assert request.status_code == 200

    request = client.get('/api/users/{}'.format(_id))
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert response['last_name'] == 'asdf2'

    # Password
    # TODO: Not sure how to effectively test changing password.

    # Update roles with a string
    data = {'apikey': TEST_ADMIN_APIKEY, 'roles': 'analyst'}
    request = client.put('/api/users/{}'.format(_id), data=data)
    assert request.status_code == 200

    request = client.get('/api/users/{}'.format(_id))
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert response['roles'] == ['analyst']

    # Update roles with a list
    data = {'apikey': TEST_ADMIN_APIKEY, 'roles': ['analyst', 'admin']}
    request = client.put('/api/users/{}'.format(_id), data=data)
    assert request.status_code == 200

    request = client.get('/api/users/{}'.format(_id))
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert response['roles'] == ['admin', 'analyst']


"""
DELETE TESTS
"""


def test_delete_nonexistent_id(client):
    """ Ensure a nonexistent ID does not work """

    data = {'apikey': TEST_ADMIN_APIKEY}
    request = client.delete('/api/users/100000', data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['message'] == 'User ID not found'


def test_delete_missing_api_key(client):
    """ Ensure an API key is given if the config requires it """

    request = client.delete('/api/users/1')
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['message'] == 'Bad or missing API key'


def test_delete_invalid_api_key(client):
    """ Ensure an API key not found in the database does not work """

    data = {'apikey': TEST_INVALID_APIKEY}
    request = client.delete('/api/users/1', data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['message'] == 'API user does not exist'


def test_delete_invalid_role(client):
    """ Ensure the given API key has the proper role access """

    data = {'apikey': TEST_ANALYST_APIKEY}
    request = client.delete('/api/users/1', data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['message'] == 'Insufficient privileges'


def test_delete(client):
    """ Ensure a proper request actually works """

    data = {'apikey': TEST_ADMIN_APIKEY, 'email': 'asdf', 'first_name': 'asdf', 'last_name': 'asdf',
            'password': 'asdf', 'roles': ['analyst', 'admin'], 'username': 'asdf'}
    request = client.post('/api/users', data=data)
    response = json.loads(request.data.decode())
    _id = response['id']
    assert request.status_code == 201

    data = {'apikey': TEST_ADMIN_APIKEY}
    request = client.delete('/api/users/{}'.format(_id), data=data)
    assert request.status_code == 204

    request = client.get('/api/users/{}'.format(_id))
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['message'] == 'User ID not found'
