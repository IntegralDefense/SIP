from project.tests.helpers import *


"""
CREATE TESTS
"""


def test_create_schema(client):
    """ Ensure POST requests conform to the required JSON schema """

    # Invalid JSON
    data = {}
    request = client.post('/api/indicators/impact', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert response['msg'] == 'Request must include valid JSON'

    # Missing required value parameter
    data = {'asdf': 'asdf'}
    request = client.post('/api/indicators/impact', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert response['msg'] == "Request JSON does not match schema: 'value' is a required property"

    # Additional parameter
    data = {'value': 'asdf', 'asdf': 'asdf'}
    request = client.post('/api/indicators/impact', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'Additional properties are not allowed' in response['msg']

    # Invalid value parameter type
    data = {'value': 1}
    request = client.post('/api/indicators/impact', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # value parameter too short
    data = {'value': ''}
    request = client.post('/api/indicators/impact', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # value parameter too long
    data = {'value': 'a' * 256}
    request = client.post('/api/indicators/impact', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']


def test_create_duplicate(client):
    """ Ensure a duplicate record cannot be created """

    data = {'value': 'asdf'}
    request = client.post('/api/indicators/impact', json=data)
    assert request.status_code == 201

    data = {'value': 'asdf'}
    request = client.post('/api/indicators/impact', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 409
    assert response['msg'] == 'Indicator impact already exists'


def test_create_missing_token(app, client):
    """ Ensure a token is given if the config requires it """

    app.config['POST'] = 'analyst'

    request = client.post('/api/indicators/impact')
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Missing Authorization Header'


def test_create_invalid_role(app, client):
    """ Ensure the given token has the proper role access """

    app.config['POST'] = 'user_does_not_have_this_role'

    access_token, refresh_token = obtain_token(client, 'analyst', 'analyst')
    headers = create_auth_header(access_token)
    request = client.post('/api/indicators/impact', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'user_does_not_have_this_role role required'


def test_create(client):
    """ Ensure a proper request actually works """

    data = {'value': 'asdf'}
    request = client.post('/api/indicators/impact', json=data)
    assert request.status_code == 201


"""
READ TESTS
"""


def test_read_nonexistent_id(client):
    """ Ensure a nonexistent ID does not work """

    request = client.get('/api/indicators/impact/100000')
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['msg'] == 'Indicator impact ID not found'


def test_read_missing_token(app, client):
    """ Ensure a token is given if the config requires it """

    app.config['GET'] = 'analyst'

    request = client.get('/api/indicators/impact/1')
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Missing Authorization Header'


def test_read_invalid_role(app, client):
    """ Ensure the given token has the proper role access """

    app.config['GET'] = 'user_does_not_have_this_role'

    access_token, refresh_token = obtain_token(client, 'analyst', 'analyst')
    headers = create_auth_header(access_token)
    request = client.get('/api/indicators/impact/1', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'user_does_not_have_this_role role required'


def test_read_all_values(client):
    """ Ensure all values properly return """

    data = {'value': 'asdf'}
    request = client.post('/api/indicators/impact', json=data)
    assert request.status_code == 201

    data = {'value': 'asdf2'}
    request = client.post('/api/indicators/impact', json=data)
    assert request.status_code == 201

    data = {'value': 'asdf3'}
    request = client.post('/api/indicators/impact', json=data)
    assert request.status_code == 201

    request = client.get('/api/indicators/impact')
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response) == 3


def test_read_by_id(client):
    """ Ensure names can be read by their ID """

    data = {'value': 'asdf'}
    request = client.post('/api/indicators/impact', json=data)
    response = json.loads(request.data.decode())
    _id = response['id']
    assert request.status_code == 201

    request = client.get('/api/indicators/impact/{}'.format(_id))
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert response['value'] == 'asdf'


"""
UPDATE TESTS
"""


def test_update_schema(client):
    """ Ensure PUT requests conform to the required JSON schema """

    # Invalid JSON
    data = {}
    request = client.put('/api/indicators/impact/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert response['msg'] == 'Request must include valid JSON'

    # Missing required value parameter
    data = {'asdf': 'asdf'}
    request = client.put('/api/indicators/impact/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert response['msg'] == "Request JSON does not match schema: 'value' is a required property"

    # Additional parameter
    data = {'value': 'asdf', 'asdf': 'asdf'}
    request = client.put('/api/indicators/impact/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'Additional properties are not allowed' in response['msg']

    # Invalid value parameter type
    data = {'value': 1}
    request = client.put('/api/indicators/impact/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # value parameter too short
    data = {'value': ''}
    request = client.put('/api/indicators/impact/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # value parameter too long
    data = {'value': 'a' * 256}
    request = client.put('/api/indicators/impact/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']


def test_update_nonexistent_id(client):
    """ Ensure a nonexistent ID does not work """

    data = {'value': 'asdf'}
    request = client.put('/api/indicators/impact/100000', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['msg'] == 'Indicator impact ID not found'


def test_update_duplicate(client):
    """ Ensure duplicate records cannot be updated """

    data = {'value': 'asdf'}
    request = client.post('/api/indicators/impact', json=data)
    response = json.loads(request.data.decode())
    _id = response['id']
    assert request.status_code == 201

    data = {'value': 'asdf'}
    request = client.put('/api/indicators/impact/{}'.format(_id), json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 409
    assert response['msg'] == 'Indicator impact already exists'


def test_update_missing_token(app, client):
    """ Ensure a token is given if the config requires it """

    app.config['PUT'] = 'analyst'

    request = client.put('/api/indicators/impact/1')
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Missing Authorization Header'


def test_update_invalid_role(app, client):
    """ Ensure the given token has the proper role access """

    app.config['PUT'] = 'user_does_not_have_this_role'

    access_token, refresh_token = obtain_token(client, 'analyst', 'analyst')
    headers = create_auth_header(access_token)
    request = client.put('/api/indicators/impact/1', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'user_does_not_have_this_role role required'


def test_update(client):
    """ Ensure a proper request actually works """

    data = {'value': 'asdf'}
    request = client.post('/api/indicators/impact', json=data)
    response = json.loads(request.data.decode())
    _id = response['id']
    assert request.status_code == 201

    data = {'value': 'asdf2'}
    request = client.put('/api/indicators/impact/{}'.format(_id), json=data)
    assert request.status_code == 200

    request = client.get('/api/indicators/impact/{}'.format(_id))
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert response['value'] == 'asdf2'


"""
DELETE TESTS
"""


def test_delete_nonexistent_id(client):
    """ Ensure a nonexistent ID does not work """

    request = client.delete('/api/indicators/impact/100000')
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['msg'] == 'Indicator impact ID not found'


def test_delete_missing_token(app, client):
    """ Ensure a token is given if the config requires it """

    app.config['DELETE'] = 'admin'

    request = client.delete('/api/indicators/impact/1')
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Missing Authorization Header'


def test_delete_invalid_role(app, client):
    """ Ensure the given token has the proper role access """

    app.config['DELETE'] = 'user_does_not_have_this_role'

    access_token, refresh_token = obtain_token(client, 'analyst', 'analyst')
    headers = create_auth_header(access_token)
    request = client.delete('/api/indicators/impact/1', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'user_does_not_have_this_role role required'
    
    
def test_delete_foreign_key(client):
    """ Ensure you cannot delete with foreign key constraints """

    impact_request, impact_response = create_indicator_impact(client, 'LOW')
    indicator_request, indicator_response = create_indicator(client, 'IP', '127.0.0.1', 'analyst', impact='LOW')
    assert impact_request.status_code == 201
    assert indicator_request.status_code == 201

    request = client.delete('/api/indicators/impact/{}'.format(impact_response['id']))
    response = json.loads(request.data.decode())
    assert request.status_code == 409
    assert response['msg'] == 'Unable to delete indicator impact due to foreign key constraints'


def test_delete(client):
    """ Ensure a proper request actually works """

    data = {'value': 'asdf'}
    request = client.post('/api/indicators/impact', json=data)
    response = json.loads(request.data.decode())
    _id = response['id']
    assert request.status_code == 201

    request = client.delete('/api/indicators/impact/{}'.format(_id))
    assert request.status_code == 204

    request = client.get('/api/indicators/impact/{}'.format(_id))
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['msg'] == 'Indicator impact ID not found'
