from project.tests.helpers import *


"""
CREATE TESTS
"""


def test_create_missing_parameter(client):
    """ Ensure the required parameters are given """

    access_token, refresh_token = obtain_token(client, 'admin', 'admin')
    headers = create_auth_header(access_token)

    # Missing email
    data = {'first_name': 'asdf', 'last_name': 'asdf', 'password': 'asdf',
            'roles': 'asdf', 'username': 'asdf'}
    request = client.post('/api/users', data=data, headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'Request must include:' in response['message']

    # Missing first_name
    data = {'email': 'asdf', 'last_name': 'asdf', 'password': 'asdf',
            'roles': 'asdf', 'username': 'asdf'}
    request = client.post('/api/users', data=data, headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'Request must include:' in response['message']

    # Missing last_name
    data = {'email': 'asdf', 'first_name': 'asdf', 'password': 'asdf',
            'roles': 'asdf', 'username': 'asdf'}
    request = client.post('/api/users', data=data, headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'Request must include:' in response['message']

    # Missing password
    data = {'email': 'asdf', 'first_name': 'asdf', 'last_name': 'asdf',
            'roles': 'asdf', 'username': 'asdf'}
    request = client.post('/api/users', data=data, headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'Request must include:' in response['message']

    # Missing roles
    data = {'email': 'asdf', 'first_name': 'asdf', 'last_name': 'asdf',
            'password': 'asdf', 'username': 'asdf'}
    request = client.post('/api/users', data=data, headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'Request must include:' in response['message']

    # Missing username
    data = {'email': 'asdf', 'first_name': 'asdf', 'last_name': 'asdf',
            'password': 'asdf', 'roles': 'asdf'}
    request = client.post('/api/users', data=data, headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'Request must include:' in response['message']


def test_create_duplicate(client):
    """ Ensure a duplicate record cannot be created """

    access_token, refresh_token = obtain_token(client, 'admin', 'admin')
    headers = create_auth_header(access_token)
    
    data = {'email': 'asdf', 'first_name': 'asdf', 'last_name': 'asdf',
            'password': 'asdf', 'roles': 'analyst', 'username': 'asdf'}
    request = client.post('/api/users', data=data, headers=headers)
    assert request.status_code == 201

    # Try making a duplicate email
    data = {'email': 'asdf', 'first_name': 'asdf', 'last_name': 'asdf',
            'password': 'asdf', 'roles': 'analyst', 'username': 'asdf2'}
    request = client.post('/api/users', data=data, headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 409
    assert response['message'] == 'User email already exists'

    # Try making a duplicate username
    data = {'email': 'asdf2', 'first_name': 'asdf', 'last_name': 'asdf',
            'password': 'asdf', 'roles': 'analyst', 'username': 'asdf'}
    request = client.post('/api/users', data=data, headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 409
    assert response['message'] == 'User username already exists'


def test_create_missing_token(app, client):
    """ Ensure a token is given if the config requires it """

    app.config['POST'] = 'admin'

    request = client.post('/api/users')
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Missing Authorization Header'


def test_create_invalid_role(app, client):
    """ Ensure the given token has the proper role access """

    app.config['POST'] = 'admin'

    access_token, refresh_token = obtain_token(client, 'analyst', 'analyst')
    headers = create_auth_header(access_token)
    request = client.post('/api/users', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['message'] == 'admin role required'


def test_create(client):
    """ Ensure a proper request actually works """

    access_token, refresh_token = obtain_token(client, 'admin', 'admin')
    headers = create_auth_header(access_token)
    
    # Try with a single roles string
    data = {'email': 'asdf', 'first_name': 'asdf', 'last_name': 'asdf',
            'password': 'asdf', 'roles': 'analyst', 'username': 'asdf'}
    request = client.post('/api/users', data=data, headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 201
    assert response['roles'] == ['analyst']
    assert response['username'] == 'asdf'

    # Try with a roles list
    data = {'email': 'asdf2', 'first_name': 'asdf', 'last_name': 'asdf',
            'password': 'asdf', 'roles': ['analyst', 'admin'], 'username': 'asdf2'}
    request = client.post('/api/users', data=data, headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 201
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


def test_read_missing_token(app, client):
    """ Ensure a token is given if the config requires it """

    app.config['GET'] = 'admin'

    request = client.get('/api/users/1')
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Missing Authorization Header'


def test_read_invalid_role(app, client):
    """ Ensure the given token has the proper role access """

    app.config['GET'] = 'admin'

    access_token, refresh_token = obtain_token(client, 'analyst', 'analyst')
    headers = create_auth_header(access_token)
    request = client.get('/api/users/1', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['message'] == 'admin role required'


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

    access_token, refresh_token = obtain_token(client, 'admin', 'admin')
    headers = create_auth_header(access_token)
    
    data = {'email': 'asdf', 'first_name': 'asdf', 'last_name': 'asdf',
            'password': 'asdf', 'roles': ['analyst', 'admin'], 'username': 'asdf'}
    request = client.put('/api/users/100000', data=data, headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['message'] == 'User ID not found'


def test_update_missing_parameter(client):
    """ Ensure the required parameters are given """

    access_token, refresh_token = obtain_token(client, 'admin', 'admin')
    headers = create_auth_header(access_token)
    request = client.put('/api/users/1', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'Request must include at least one of' in response['message']


def test_update_duplicate(client):
    """ Ensure duplicate records cannot be updated """

    access_token, refresh_token = obtain_token(client, 'admin', 'admin')
    headers = create_auth_header(access_token)
    
    data = {'email': 'asdf', 'first_name': 'asdf', 'last_name': 'asdf',
            'password': 'asdf', 'roles': 'analyst', 'username': 'asdf'}
    request = client.post('/api/users', data=data, headers=headers)
    response = json.loads(request.data.decode())
    _id = response['id']
    assert request.status_code == 201
    assert response['roles'] == ['analyst']
    assert response['username'] == 'asdf'

    # Try to update an existing email
    data = {'email': 'asdf'}
    request = client.put('/api/users/{}'.format(_id), data=data, headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 409
    assert response['message'] == 'User email already exists'

    # Try to update an existing username
    data = {'username': 'asdf'}
    request = client.put('/api/users/{}'.format(_id), data=data, headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 409
    assert response['message'] == 'User username already exists'


def test_update_missing_token(app, client):
    """ Ensure a token is given if the config requires it """

    app.config['PUT'] = 'admin'

    request = client.put('/api/users/1')
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Missing Authorization Header'


def test_update_invalid_role(app, client):
    """ Ensure the given token has the proper role access """

    app.config['PUT'] = 'admin'

    access_token, refresh_token = obtain_token(client, 'analyst', 'analyst')
    headers = create_auth_header(access_token)
    request = client.put('/api/users/1', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['message'] == 'admin role required'


def test_update(client):
    """ Ensure a proper request actually works """

    access_token, refresh_token = obtain_token(client, 'admin', 'admin')
    headers = create_auth_header(access_token)
    data = {'email': 'asdf', 'first_name': 'asdf', 'last_name': 'asdf',
            'password': 'asdf', 'roles': ['analyst', 'admin'], 'username': 'asdf'}
    request = client.post('/api/users', data=data, headers=headers)
    response = json.loads(request.data.decode())
    _id = response['id']
    assert request.status_code == 201
    assert response['active'] is True
    assert response['roles'] == ['admin', 'analyst']

    # Update active
    data = {'active': False}
    request = client.put('/api/users/{}'.format(_id), data=data, headers=headers)
    assert request.status_code == 200

    request = client.get('/api/users/{}'.format(_id))
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert response['active'] is False

    # Update email
    data = {'email': 'asdf2'}
    request = client.put('/api/users/{}'.format(_id), data=data, headers=headers)
    assert request.status_code == 200

    request = client.get('/api/users/{}'.format(_id))
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert response['email'] == 'asdf2'

    # Update first_name
    data = {'first_name': 'asdf2'}
    request = client.put('/api/users/{}'.format(_id), data=data, headers=headers)
    assert request.status_code == 200

    request = client.get('/api/users/{}'.format(_id))
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert response['first_name'] == 'asdf2'

    # Update last_name
    data = {'last_name': 'asdf2'}
    request = client.put('/api/users/{}'.format(_id), data=data, headers=headers)
    assert request.status_code == 200

    request = client.get('/api/users/{}'.format(_id))
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert response['last_name'] == 'asdf2'

    # Password
    # TODO: Not sure how to effectively test changing password.

    # Update roles with a string
    data = {'roles': 'analyst'}
    request = client.put('/api/users/{}'.format(_id), data=data, headers=headers)
    assert request.status_code == 200

    request = client.get('/api/users/{}'.format(_id))
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert response['roles'] == ['analyst']

    # Update roles with a list
    data = {'roles': ['analyst', 'admin']}
    request = client.put('/api/users/{}'.format(_id), data=data, headers=headers)
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

    access_token, refresh_token = obtain_token(client, 'admin', 'admin')
    headers = create_auth_header(access_token)
    request = client.delete('/api/users/100000', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['message'] == 'User ID not found'


def test_delete_missing_token(app, client):
    """ Ensure a token is given if the config requires it """

    app.config['DELETE'] = 'admin'

    request = client.delete('/api/users/1')
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Missing Authorization Header'


def test_delete_invalid_role(app, client):
    """ Ensure the given token has the proper role access """

    app.config['DELETE'] = 'admin'

    access_token, refresh_token = obtain_token(client, 'analyst', 'analyst')
    headers = create_auth_header(access_token)
    request = client.delete('/api/users/1', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['message'] == 'admin role required'


def test_delete_foreign_key_event(client):
    """ Ensure you cannot delete with foreign key constraints """

    access_token, refresh_token = obtain_token(client, 'admin', 'admin')
    headers = create_auth_header(access_token)
    
    user_request, user_response = create_user(client, 'asdf@asdf.com', 'asdf', 'asdf', 'asdf', ['analyst'], 'some_guy')
    event_request, event_response = create_event(client, 'test_event', 'some_guy')
    assert user_request.status_code == 201
    assert event_request.status_code == 201

    request = client.delete('/api/users/{}'.format(user_response['id']), headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 409
    assert response['message'] == 'Unable to delete user due to foreign key constraints'


def test_delete_foreign_key_indicator(client):
    """ Ensure you cannot delete with foreign key constraints """

    access_token, refresh_token = obtain_token(client, 'admin', 'admin')
    headers = create_auth_header(access_token)
    
    user_request, user_response = create_user(client, 'asdf@asdf.com', 'asdf', 'asdf', 'asdf', ['analyst'], 'some_guy')
    indicator_request, indicator_response = create_indicator(client, 'IP', '127.0.0.1', 'some_guy')
    assert user_request.status_code == 201
    assert indicator_request.status_code == 201

    request = client.delete('/api/users/{}'.format(user_response['id']), headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 409
    assert response['message'] == 'Unable to delete user due to foreign key constraints'


def test_delete_foreign_key_reference(client):
    """ Ensure you cannot delete with foreign key constraints """

    access_token, refresh_token = obtain_token(client, 'admin', 'admin')
    headers = create_auth_header(access_token)
    
    user_request, user_response = create_user(client, 'asdf@asdf.com', 'asdf', 'asdf', 'asdf', ['analyst'], 'some_guy')
    reference_request, reference_response = create_intel_reference(client, 'some_guy', 'OSINT', 'http://blahblah.com')
    assert user_request.status_code == 201
    assert reference_request.status_code == 201

    request = client.delete('/api/users/{}'.format(user_response['id']), headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 409
    assert response['message'] == 'Unable to delete user due to foreign key constraints'


def test_delete(client):
    """ Ensure a proper request actually works """

    access_token, refresh_token = obtain_token(client, 'admin', 'admin')
    headers = create_auth_header(access_token)
    
    data = {'email': 'asdf', 'first_name': 'asdf', 'last_name': 'asdf',
            'password': 'asdf', 'roles': ['analyst', 'admin'], 'username': 'asdf'}
    request = client.post('/api/users', data=data, headers=headers)
    response = json.loads(request.data.decode())
    _id = response['id']
    assert request.status_code == 201

    request = client.delete('/api/users/{}'.format(_id), headers=headers)
    assert request.status_code == 204

    request = client.get('/api/users/{}'.format(_id))
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['message'] == 'User ID not found'
