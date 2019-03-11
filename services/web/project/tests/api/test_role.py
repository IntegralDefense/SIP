from project.tests.conftest import TEST_ADMIN_APIKEY, TEST_ANALYST_APIKEY, TEST_INACTIVE_APIKEY, TEST_INVALID_APIKEY
from project.tests.helpers import *


"""
CREATE TESTS
"""


def test_create_schema(client):
    """ Ensure POST requests conform to the required JSON schema """

    headers = create_auth_header(TEST_ADMIN_APIKEY)

    # Invalid JSON
    data = {}
    request = client.post('/api/roles', json=data, headers=headers)
    response = json.loads(request.data.decode())
    print('XXXXX: {}'.format(response))
    assert request.status_code == 400
    assert response['msg'] == 'Request must include valid JSON'

    # Missing required name parameter
    data = {'asdf': 'asdf'}
    request = client.post('/api/roles', json=data, headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert response['msg'] == "Request JSON does not match schema: 'name' is a required property"

    # Additional parameter
    data = {'name': 'asdf', 'asdf': 'asdf'}
    request = client.post('/api/roles', json=data, headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'Additional properties are not allowed' in response['msg']

    # Invalid name parameter type
    data = {'name': 1}
    request = client.post('/api/roles', json=data, headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # name parameter too short
    data = {'name': ''}
    request = client.post('/api/roles', json=data, headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # name parameter too long
    data = {'name': 'a' * 81}
    request = client.post('/api/roles', json=data, headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']

    # Invalid description parameter type
    data = {'name': 'asdf', 'description': 1}
    request = client.post('/api/roles', json=data, headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # description parameter too short
    data = {'name': 'asdf', 'description': ''}
    request = client.post('/api/roles', json=data, headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # description parameter too long
    data = {'name': 'asdf', 'description': 'a' * 256}
    request = client.post('/api/roles', json=data, headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']


def test_create_duplicate(client):
    """ Ensure a duplicate record cannot be created """

    headers = create_auth_header(TEST_ADMIN_APIKEY)
    data = {'name': 'asdf'}
    request = client.post('/api/roles', json=data, headers=headers)
    assert request.status_code == 201

    data = {'name': 'asdf'}
    request = client.post('/api/roles', json=data, headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 409
    assert response['msg'] == 'Role already exists'


def test_create_missing_api_key(app, client):
    """ Ensure an API key is given if the config requires it """

    app.config['POST'] = 'analyst'

    request = client.post('/api/roles')
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Bad or missing API key'


def test_create_invalid_api_key(app, client):
    """ Ensure an API key not found in the database does not work """

    app.config['POST'] = 'analyst'

    headers = {'Authorization': 'Apikey ' + TEST_INVALID_APIKEY}
    request = client.post('/api/roles', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'API user does not exist'


def test_create_inactive_api_key(app, client):
    """ Ensure an inactive API key does not work """

    app.config['POST'] = 'analyst'

    headers = {'Authorization': 'Apikey ' + TEST_INACTIVE_APIKEY}
    request = client.post('/api/roles', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'API user is not active'


def test_create_invalid_role(app, client):
    """ Ensure the given API key has the proper role access """

    app.config['POST'] = 'user_does_not_have_this_role'

    headers = {'Authorization': 'Apikey ' + TEST_ANALYST_APIKEY}
    request = client.post('/api/roles', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Insufficient privileges'


def test_create(client):
    """ Ensure a proper request actually works """

    headers = create_auth_header(TEST_ADMIN_APIKEY)
    data = {'name': 'asdf'}
    request = client.post('/api/roles', json=data, headers=headers)
    assert request.status_code == 201


"""
READ TESTS
"""


def test_read_nonexistent_id(client):
    """ Ensure a nonexistent ID does not work """

    request = client.get('/api/roles/100000')
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['msg'] == 'Role ID not found'


def test_read_missing_api_key(app, client):
    """ Ensure an API key is given if the config requires it """

    app.config['GET'] = 'analyst'

    request = client.get('/api/roles/1')
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Bad or missing API key'


def test_read_invalid_api_key(app, client):
    """ Ensure an API key not found in the database does not work """

    app.config['GET'] = 'analyst'

    headers = {'Authorization': 'Apikey ' + TEST_INVALID_APIKEY}
    request = client.get('/api/roles/1', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'API user does not exist'


def test_read_inactive_api_key(app, client):
    """ Ensure an inactive API key does not work """

    app.config['GET'] = 'analyst'

    headers = {'Authorization': 'Apikey ' + TEST_INACTIVE_APIKEY}
    request = client.get('/api/roles/1', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'API user is not active'


def test_read_invalid_role(app, client):
    """ Ensure the given API key has the proper role access """

    app.config['GET'] = 'user_does_not_have_this_role'

    headers = {'Authorization': 'Apikey ' + TEST_ANALYST_APIKEY}
    request = client.get('/api/roles/1', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Insufficient privileges'


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


def test_update_schema(client):
    """ Ensure PUT requests conform to the required JSON schema """

    headers = create_auth_header(TEST_ADMIN_APIKEY)

    # Invalid JSON
    data = {}
    request = client.put('/api/roles/1', json=data, headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert response['msg'] == 'Request must include valid JSON'

    # Additional parameter
    data = {'name': 'asdf', 'asdf': 'asdf'}
    request = client.put('/api/roles/1', json=data, headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'Additional properties are not allowed' in response['msg']

    # Invalid name parameter type
    data = {'name': 1}
    request = client.put('/api/roles/1', json=data, headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # name parameter too short
    data = {'name': ''}
    request = client.put('/api/roles/1', json=data, headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # name parameter too long
    data = {'name': 'a' * 81}
    request = client.put('/api/roles/1', json=data, headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']

    # Invalid description parameter type
    data = {'name': 'asdf', 'description': 1}
    request = client.put('/api/roles/1', json=data, headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # description parameter too short
    data = {'name': 'asdf', 'description': ''}
    request = client.put('/api/roles/1', json=data, headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # description parameter too long
    data = {'name': 'asdf', 'description': 'a' * 256}
    request = client.put('/api/roles/1', json=data, headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']


def test_update_nonexistent_id(client):
    """ Ensure a nonexistent ID does not work """

    headers = create_auth_header(TEST_ADMIN_APIKEY)
    data = {'name': 'asdf'}
    request = client.put('/api/roles/100000', json=data, headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['msg'] == 'Role ID not found'


def test_update_duplicate(client):
    """ Ensure duplicate records cannot be updated """

    headers = create_auth_header(TEST_ADMIN_APIKEY)
    data = {'name': 'asdf'}
    request = client.post('/api/roles', json=data, headers=headers)
    response = json.loads(request.data.decode())
    _id = response['id']
    assert request.status_code == 201

    data = {'name': 'asdf'}
    request = client.put('/api/roles/{}'.format(_id), json=data, headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 409
    assert response['msg'] == 'Role already exists'


def test_update_missing_api_key(app, client):
    """ Ensure an API key is given if the config requires it """

    app.config['PUT'] = 'analyst'

    request = client.put('/api/roles/1')
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Bad or missing API key'


def test_update_invalid_api_key(app, client):
    """ Ensure an API key not found in the database does not work """

    app.config['PUT'] = 'analyst'

    headers = {'Authorization': 'Apikey ' + TEST_INVALID_APIKEY}
    request = client.put('/api/roles/1', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'API user does not exist'


def test_update_inactive_api_key(app, client):
    """ Ensure an inactive API key does not work """

    app.config['PUT'] = 'analyst'

    headers = {'Authorization': 'Apikey ' + TEST_INACTIVE_APIKEY}
    request = client.put('/api/roles/1', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'API user is not active'


def test_update_invalid_role(app, client):
    """ Ensure the given API key has the proper role access """

    app.config['PUT'] = 'user_does_not_have_this_role'

    headers = {'Authorization': 'Apikey ' + TEST_ANALYST_APIKEY}
    request = client.put('/api/roles/1', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Insufficient privileges'


def test_update(client):
    """ Ensure a proper request actually works """

    headers = create_auth_header(TEST_ADMIN_APIKEY)
    data = {'name': 'asdf'}
    request = client.post('/api/roles', json=data, headers=headers)
    response = json.loads(request.data.decode())
    _id = response['id']
    assert request.status_code == 201

    data = {'name': 'asdf2'}
    request = client.put('/api/roles/{}'.format(_id), json=data, headers=headers)
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

    headers = create_auth_header(TEST_ADMIN_APIKEY)
    request = client.delete('/api/roles/100000', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['msg'] == 'Role ID not found'


def test_delete_missing_api_key(app, client):
    """ Ensure an API key is given if the config requires it """

    app.config['DELETE'] = 'admin'

    request = client.delete('/api/roles/1')
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Bad or missing API key'


def test_delete_invalid_api_key(app, client):
    """ Ensure an API key not found in the database does not work """

    app.config['DELETE'] = 'admin'

    headers = {'Authorization': 'Apikey ' + TEST_INVALID_APIKEY}
    request = client.delete('/api/roles/1', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'API user does not exist'


def test_delete_inactive_api_key(app, client):
    """ Ensure an inactive API key does not work """

    app.config['DELETE'] = 'admin'

    headers = {'Authorization': 'Apikey ' + TEST_INACTIVE_APIKEY}
    request = client.delete('/api/roles/1', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'API user is not active'


def test_delete_invalid_role(app, client):
    """ Ensure the given API key has the proper role access """

    app.config['DELETE'] = 'user_does_not_have_this_role'

    headers = {'Authorization': 'Apikey ' + TEST_ANALYST_APIKEY}
    request = client.delete('/api/roles/1', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Insufficient privileges'


def test_delete(client):
    """ Ensure a proper request actually works """

    headers = create_auth_header(TEST_ADMIN_APIKEY)
    data = {'name': 'asdf'}
    request = client.post('/api/roles', json=data, headers=headers)
    response = json.loads(request.data.decode())
    _id = response['id']
    assert request.status_code == 201

    request = client.delete('/api/roles/{}'.format(_id), headers=headers)
    assert request.status_code == 204

    request = client.get('/api/roles/{}'.format(_id))
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['msg'] == 'Role ID not found'
