from project.tests.helpers import *


"""
CREATE TESTS
"""


def test_create_missing_parameter(client):
    """ Ensure the required parameters are given """

    access_token, refresh_token = obtain_token(client, 'admin', 'admin')
    headers = create_auth_header(access_token)
    request = client.post('/api/roles', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert response['message'] == 'Request must include: name'


def test_create_duplicate(client):
    """ Ensure a duplicate record cannot be created """

    access_token, refresh_token = obtain_token(client, 'admin', 'admin')
    headers = create_auth_header(access_token)
    data = {'name': 'asdf'}
    request = client.post('/api/roles', data=data, headers=headers)
    assert request.status_code == 201

    data = {'name': 'asdf'}
    request = client.post('/api/roles', data=data, headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 409
    assert response['message'] == 'Role already exists'


def test_create_missing_token(app, client):
    """ Ensure a token is given if the config requires it """

    app.config['POST'] = 'admin'

    request = client.post('/api/roles')
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Missing Authorization Header'


def test_create_invalid_role(client):
    """ Ensure the given token has the proper role access """

    access_token, refresh_token = obtain_token(client, 'analyst', 'analyst')
    headers = create_auth_header(access_token)
    request = client.post('/api/roles', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['message'] == 'admin role required'


def test_create(client):
    """ Ensure a proper request actually works """

    access_token, refresh_token = obtain_token(client, 'admin', 'admin')
    headers = create_auth_header(access_token)
    data = {'name': 'asdf'}
    request = client.post('/api/roles', data=data, headers=headers)
    assert request.status_code == 201


"""
READ TESTS
"""


def test_read_nonexistent_id(client):
    """ Ensure a nonexistent ID does not work """

    request = client.get('/api/roles/100000')
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['message'] == 'Role ID not found'


def test_read_missing_token(app, client):
    """ Ensure a token is given if the config requires it """

    app.config['GET'] = 'admin'

    request = client.get('/api/roles/1')
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Missing Authorization Header'


def test_read_invalid_role(app, client):
    """ Ensure the given token has the proper role access """

    app.config['GET'] = 'admin'

    access_token, refresh_token = obtain_token(client, 'analyst', 'analyst')
    headers = create_auth_header(access_token)
    request = client.get('/api/roles/1', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['message'] == 'admin role required'


def test_read_all_values(client):
    """ Ensure all values properly return """

    request = client.get('/api/roles')
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response) == 2


def test_read_by_id(client):
    """ Ensure names can be read by their ID """

    request = client.get('/api/roles/1')
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == 1


"""
UPDATE TESTS
"""


def test_update_nonexistent_id(client):
    """ Ensure a nonexistent ID does not work """

    access_token, refresh_token = obtain_token(client, 'admin', 'admin')
    headers = create_auth_header(access_token)
    data = {'name': 'asdf'}
    request = client.put('/api/roles/100000', data=data, headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['message'] == 'Role ID not found'


def test_update_missing_parameter(client):
    """ Ensure the required parameters are given """

    access_token, refresh_token = obtain_token(client, 'admin', 'admin')
    headers = create_auth_header(access_token)
    request = client.put('/api/roles/1', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert response['message'] == 'Request must include at least name or description'


def test_update_duplicate(client):
    """ Ensure duplicate records cannot be updated """

    access_token, refresh_token = obtain_token(client, 'admin', 'admin')
    headers = create_auth_header(access_token)
    data = {'name': 'asdf'}
    request = client.post('/api/roles', data=data, headers=headers)
    response = json.loads(request.data.decode())
    _id = response['id']
    assert request.status_code == 201

    data = {'name': 'asdf'}
    request = client.put('/api/roles/{}'.format(_id), data=data, headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 409
    assert response['message'] == 'Role already exists'


def test_update_missing_token(app, client):
    """ Ensure a token is given if the config requires it """

    app.config['PUT'] = 'admin'

    request = client.put('/api/roles/1')
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Missing Authorization Header'


def test_update_invalid_role(client):
    """ Ensure the given token has the proper role access """

    access_token, refresh_token = obtain_token(client, 'analyst', 'analyst')
    headers = create_auth_header(access_token)
    request = client.put('/api/roles/1', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['message'] == 'admin role required'


def test_update(client):
    """ Ensure a proper request actually works """

    access_token, refresh_token = obtain_token(client, 'admin', 'admin')
    headers = create_auth_header(access_token)
    data = {'name': 'asdf'}
    request = client.post('/api/roles', data=data, headers=headers)
    response = json.loads(request.data.decode())
    _id = response['id']
    assert request.status_code == 201

    data = {'name': 'asdf2'}
    request = client.put('/api/roles/{}'.format(_id), data=data, headers=headers)
    assert request.status_code == 200

    request = client.get('/api/roles/{}'.format(_id))
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert response['name'] == 'asdf2'


"""
DELETE TESTS
"""


def test_delete_nonexistent_id(client):
    """ Ensure a nonexistent ID does not work """

    access_token, refresh_token = obtain_token(client, 'admin', 'admin')
    headers = create_auth_header(access_token)
    request = client.delete('/api/roles/100000', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['message'] == 'Role ID not found'


def test_delete_missing_token(app, client):
    """ Ensure a token is given if the config requires it """

    app.config['DELETE'] = 'admin'

    request = client.delete('/api/roles/1')
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Missing Authorization Header'


def test_delete_invalid_role(client):
    """ Ensure the given token has the proper role access """

    access_token, refresh_token = obtain_token(client, 'analyst', 'analyst')
    headers = create_auth_header(access_token)
    request = client.delete('/api/roles/1', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['message'] == 'admin role required'


def test_delete(client):
    """ Ensure a proper request actually works """

    access_token, refresh_token = obtain_token(client, 'admin', 'admin')
    headers = create_auth_header(access_token)
    data = {'name': 'asdf'}
    request = client.post('/api/roles', data=data, headers=headers)
    response = json.loads(request.data.decode())
    _id = response['id']
    assert request.status_code == 201

    request = client.delete('/api/roles/{}'.format(_id), headers=headers)
    assert request.status_code == 204

    request = client.get('/api/roles/{}'.format(_id))
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['message'] == 'Role ID not found'
