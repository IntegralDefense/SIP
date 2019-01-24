import json

from project.tests.conftest import TEST_ADMIN_APIKEY, TEST_ANALYST_APIKEY, TEST_INVALID_APIKEY


"""
CREATE TESTS
"""


def test_create_missing_parameter(client):
    """ Ensure the required parameters are given """

    data = {'apikey': TEST_ADMIN_APIKEY}
    request = client.post('/api/roles', data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert response['message'] == 'Request must include: name'


def test_create_duplicate(client):
    """ Ensure a duplicate record cannot be created """

    data = {'apikey': TEST_ADMIN_APIKEY, 'name': 'asdf'}
    request = client.post('/api/roles', data=data)
    assert request.status_code == 201

    data = {'apikey': TEST_ADMIN_APIKEY, 'name': 'asdf'}
    request = client.post('/api/roles', data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 409
    assert response['message'] == 'Role already exists'


def test_create_missing_api_key(app, client):
    """ Ensure an API key is given if the config requires it """

    app.config['POST'] = 'analyst'

    data = {'name': 'asdf'}
    request = client.post('/api/roles', data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['message'] == 'Bad or missing API key'


def test_create_invalid_api_key(app, client):
    """ Ensure an API key not found in the database does not work """

    app.config['POST'] = 'analyst'

    data = {'apikey': TEST_INVALID_APIKEY, 'name': 'asdf'}
    request = client.post('/api/roles', data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['message'] == 'API user does not exist'


def test_create_invalid_role(app, client):
    """ Ensure the given API key has the proper role access """

    app.config['POST'] = 'user_does_not_have_this_role'

    data = {'apikey': TEST_ANALYST_APIKEY, 'name': 'asdf'}
    request = client.post('/api/roles', data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['message'] == 'Insufficient privileges'


def test_create(client):
    """ Ensure a proper request actually works """

    data = {'apikey': TEST_ADMIN_APIKEY, 'name': 'asdf'}
    request = client.post('/api/roles', data=data)
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


def test_read_missing_api_key(app, client):
    """ Ensure an API key is given if the config requires it """

    app.config['GET'] = 'analyst'

    request = client.get('/api/roles/1')
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['message'] == 'Bad or missing API key'


def test_read_invalid_api_key(app, client):
    """ Ensure an API key not found in the database does not work """

    app.config['GET'] = 'analyst'

    request = client.get('/api/roles/1?apikey={}'.format(TEST_INVALID_APIKEY))
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['message'] == 'API user does not exist'


def test_read_invalid_role(app, client):
    """ Ensure the given API key has the proper role access """

    app.config['GET'] = 'user_does_not_have_this_role'

    request = client.get('/api/roles/1?apikey={}'.format(TEST_ANALYST_APIKEY))
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['message'] == 'Insufficient privileges'


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

    data = {'apikey': TEST_ADMIN_APIKEY, 'name': 'asdf'}
    request = client.put('/api/roles/100000', data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['message'] == 'Role ID not found'


def test_update_missing_parameter(client):
    """ Ensure the required parameters are given """

    data = {'apikey': TEST_ADMIN_APIKEY}
    request = client.put('/api/roles/1', data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert response['message'] == 'Request must include at least name or description'


def test_update_duplicate(client):
    """ Ensure duplicate records cannot be updated """

    data = {'apikey': TEST_ADMIN_APIKEY, 'name': 'asdf'}
    request = client.post('/api/roles', data=data)
    response = json.loads(request.data.decode())
    _id = response['id']
    assert request.status_code == 201

    data = {'apikey': TEST_ADMIN_APIKEY, 'name': 'asdf'}
    request = client.put('/api/roles/{}'.format(_id), data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 409
    assert response['message'] == 'Role already exists'


def test_update_missing_api_key(client):
    """ Ensure an API key is given if the config requires it """

    data = {'name': 'asdf'}
    request = client.put('/api/roles/1', data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['message'] == 'Bad or missing API key'


def test_update_invalid_api_key(client):
    """ Ensure an API key not found in the database does not work """

    data = {'apikey': TEST_INVALID_APIKEY, 'name': 'asdf'}
    request = client.put('/api/roles/1', data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['message'] == 'API user does not exist'


def test_update_invalid_role(client):
    """ Ensure the given API key has the proper role access """

    data = {'apikey': TEST_ANALYST_APIKEY, 'name': 'asdf'}
    request = client.put('/api/roles/1', data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['message'] == 'Insufficient privileges'


def test_update(client):
    """ Ensure a proper request actually works """

    data = {'apikey': TEST_ADMIN_APIKEY, 'name': 'asdf'}
    request = client.post('/api/roles', data=data)
    response = json.loads(request.data.decode())
    _id = response['id']
    assert request.status_code == 201

    data = {'apikey': TEST_ADMIN_APIKEY, 'name': 'asdf2'}
    request = client.put('/api/roles/{}'.format(_id), data=data)
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

    data = {'apikey': TEST_ADMIN_APIKEY}
    request = client.delete('/api/roles/100000', data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['message'] == 'Role ID not found'


def test_delete_missing_api_key(app, client):
    """ Ensure an API key is given if the config requires it """

    app.config['DELETE'] = 'admin'

    request = client.delete('/api/roles/1')
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['message'] == 'Bad or missing API key'


def test_delete_invalid_api_key(app, client):
    """ Ensure an API key not found in the database does not work """

    app.config['DELETE'] = 'admin'

    data = {'apikey': TEST_INVALID_APIKEY}
    request = client.delete('/api/roles/1', data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['message'] == 'API user does not exist'


def test_delete_invalid_role(app, client):
    """ Ensure the given API key has the proper role access """

    app.config['DELETE'] = 'user_does_not_have_this_role'

    data = {'apikey': TEST_ANALYST_APIKEY}
    request = client.delete('/api/roles/1', data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['message'] == 'Insufficient privileges'


def test_delete(client):
    """ Ensure a proper request actually works """

    data = {'apikey': TEST_ADMIN_APIKEY, 'name': 'asdf'}
    request = client.post('/api/roles', data=data)
    response = json.loads(request.data.decode())
    _id = response['id']
    assert request.status_code == 201

    data = {'apikey': TEST_ADMIN_APIKEY}
    request = client.delete('/api/roles/{}'.format(_id), data=data)
    assert request.status_code == 204

    request = client.get('/api/roles/{}'.format(_id))
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['message'] == 'Role ID not found'
