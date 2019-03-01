from project.tests.helpers import *


"""
CREATE TESTS
"""


def test_create_schema(client):
    """ Ensure POST requests conform to the required JSON schema """

    # Invalid JSON
    data = {}
    request = client.post('/api/campaigns/alias', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert response['msg'] == 'Request must include valid JSON'

    # Missing required alias parameter
    data = {'campaign': 'asdf'}
    request = client.post('/api/campaigns/alias', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert response['msg'] == "Request JSON does not match schema: 'alias' is a required property"

    # Missing required campaign parameter
    data = {'alias': 'asdf'}
    request = client.post('/api/campaigns/alias', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert response['msg'] == "Request JSON does not match schema: 'campaign' is a required property"

    # Additional parameter
    data = {'alias': 'asdf', 'campaign': 'asdf', 'asdf': 'asdf'}
    request = client.post('/api/campaigns/alias', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'Additional properties are not allowed' in response['msg']

    # Invalid alias parameter type
    data = {'alias': 1, 'campaign': 'asdf'}
    request = client.post('/api/campaigns/alias', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # Invalid campaign parameter type
    data = {'alias': 'asdf', 'campaign': 1}
    request = client.post('/api/campaigns/alias', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # alias parameter too short
    data = {'alias': '', 'campaign': 'asdf'}
    request = client.post('/api/campaigns/alias', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # alias parameter too long
    data = {'alias': 'a' * 256, 'campaign': 'asdf'}
    request = client.post('/api/campaigns/alias', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']

    # campaign parameter too short
    data = {'alias': 'asdf', 'campaign': ''}
    request = client.post('/api/campaigns/alias', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # campaign parameter too long
    data = {'alias': 'asdf', 'campaign': 'a' * 256}
    request = client.post('/api/campaigns/alias', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']


def test_create_nonexistent_campaign(client):
    """ Ensure an alias cannot be created with a nonexistent campaign """

    data = {'alias': 'asdf', 'campaign': 'asdf'}
    request = client.post('/api/campaigns/alias', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['msg'] == 'Campaign does not exist'


def test_create_duplicate(client):
    """ Ensure a duplicate record cannot be created """

    data = {'name': 'asdf'}
    request = client.post('/api/campaigns', json=data)
    assert request.status_code == 201

    data = {'alias': 'asdf2', 'campaign': 'asdf'}
    request = client.post('/api/campaigns/alias', json=data)
    assert request.status_code == 201

    data = {'alias': 'asdf2', 'campaign': 'asdf'}
    request = client.post('/api/campaigns/alias', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 409
    assert response['msg'] == 'Campaign alias already exists'


def test_create_same_value(client):
    """ Ensure an alias cannot have the same value as the campaign name """

    data = {'name': 'asdf'}
    request = client.post('/api/campaigns', json=data)
    assert request.status_code == 201

    data = {'alias': 'asdf', 'campaign': 'asdf'}
    request = client.post('/api/campaigns/alias', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 409
    assert response['msg'] == 'Campaign alias cannot be the same as its name'


def test_create_missing_token(app, client):
    """ Ensure a token is given if the config requires it """

    app.config['POST'] = 'analyst'

    request = client.post('/api/campaigns/alias')
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Missing Authorization Header'


def test_create_invalid_role(app, client):
    """ Ensure the given token has the proper role access """

    app.config['POST'] = 'user_does_not_have_this_role'

    access_token, refresh_token = obtain_token(client, 'analyst', 'analyst')
    headers = create_auth_header(access_token)
    request = client.post('/api/campaigns/alias', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'user_does_not_have_this_role role required'


def test_create(client):
    """ Ensure a proper request actually works """

    data = {'name': 'asdf'}
    request = client.post('/api/campaigns', json=data)
    assert request.status_code == 201

    data = {'alias': 'asdf2', 'campaign': 'asdf'}
    request = client.post('/api/campaigns/alias', json=data)
    assert request.status_code == 201


"""
READ TESTS
"""


def test_read_nonexistent_id(client):
    """ Ensure a nonexistent ID does not work """

    request = client.get('/api/campaigns/alias/100000')
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['msg'] == 'Campaign alias ID not found'


def test_read_missing_token(app, client):
    """ Ensure a token is given if the config requires it """

    app.config['GET'] = 'analyst'

    request = client.get('/api/campaigns/alias/1')
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Missing Authorization Header'


def test_read_invalid_role(app, client):
    """ Ensure the given token has the proper role access """

    app.config['GET'] = 'user_does_not_have_this_role'

    access_token, refresh_token = obtain_token(client, 'analyst', 'analyst')
    headers = create_auth_header(access_token)
    request = client.get('/api/campaigns/alias/1', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'user_does_not_have_this_role role required'


def test_read_all_values(client):
    """ Ensure all values properly return """

    data = {'name': 'asdf'}
    request = client.post('/api/campaigns', json=data)
    assert request.status_code == 201

    data = {'alias': 'asdf2', 'campaign': 'asdf'}
    request = client.post('/api/campaigns/alias', json=data)
    assert request.status_code == 201

    data = {'alias': 'asdf3', 'campaign': 'asdf'}
    request = client.post('/api/campaigns/alias', json=data)
    assert request.status_code == 201

    data = {'alias': 'asdf4', 'campaign': 'asdf'}
    request = client.post('/api/campaigns/alias', json=data)
    assert request.status_code == 201

    request = client.get('/api/campaigns/alias')
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response) == 3


def test_read_by_id(client):
    """ Ensure names can be read by their ID """

    data = {'name': 'asdf'}
    request = client.post('/api/campaigns', json=data)
    assert request.status_code == 201

    data = {'alias': 'asdf2', 'campaign': 'asdf'}
    request = client.post('/api/campaigns/alias', json=data)
    response = json.loads(request.data.decode())
    _id = response['id']
    assert request.status_code == 201

    request = client.get('/api/campaigns/alias/{}'.format(_id))
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert response['alias'] == 'asdf2'


"""
UPDATE TESTS
"""


def test_update_schema(client):
    """ Ensure PUT requests conform to the required JSON schema """

    # Invalid JSON
    data = {}
    request = client.put('/api/campaigns/alias/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert response['msg'] == 'Request must include valid JSON'

    # Additional parameter
    data = {'asdf': 'asdf'}
    request = client.put('/api/campaigns/alias/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'Additional properties are not allowed' in response['msg']

    # Invalid alias parameter type
    data = {'alias': 1, 'campaign': 'asdf'}
    request = client.put('/api/campaigns/alias/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # Invalid campaign parameter type
    data = {'alias': 'asdf', 'campaign': 1}
    request = client.put('/api/campaigns/alias/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # alias parameter too short
    data = {'alias': '', 'campaign': 'asdf'}
    request = client.put('/api/campaigns/alias/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # alias parameter too long
    data = {'alias': 'a' * 256, 'campaign': 'asdf'}
    request = client.put('/api/campaigns/alias/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']

    # campaign parameter too short
    data = {'alias': 'asdf', 'campaign': ''}
    request = client.put('/api/campaigns/alias/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # campaign parameter too long
    data = {'alias': 'asdf', 'campaign': 'a' * 256}
    request = client.put('/api/campaigns/alias/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']


def test_update_nonexistent_id(client):
    """ Ensure a nonexistent ID does not work """

    data = {'alias': 'asdf2', 'campaign': 'asdf'}
    request = client.put('/api/campaigns/alias/100000', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['msg'] == 'Campaign alias ID not found'


def test_update_duplicate(client):
    """ Ensure duplicate records cannot be updated """

    data = {'name': 'asdf'}
    request = client.post('/api/campaigns', json=data)
    assert request.status_code == 201

    data = {'alias': 'asdf2', 'campaign': 'asdf'}
    request = client.post('/api/campaigns/alias', json=data)
    response = json.loads(request.data.decode())
    _id = response['id']
    assert request.status_code == 201

    data = {'alias': 'asdf2', 'campaign': 'asdf'}
    request = client.put('/api/campaigns/alias/{}'.format(_id), json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 409
    assert response['msg'] == 'Campaign alias already exists'


def test_update_same_value(client):
    """ Ensure an alias cannot have the same value as the campaign name """

    data = {'name': 'asdf'}
    request = client.post('/api/campaigns', json=data)
    assert request.status_code == 201

    data = {'alias': 'asdf2', 'campaign': 'asdf'}
    request = client.post('/api/campaigns/alias', json=data)
    assert request.status_code == 201

    data = {'alias': 'asdf', 'campaign': 'asdf'}
    request = client.post('/api/campaigns/alias', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 409
    assert response['msg'] == 'Campaign alias cannot be the same as its name'


def test_update_nonexistent_campaign(client):
    """ Ensure an alias cannot be updated with a nonexistent campaign """

    data = {'name': 'asdf'}
    request = client.post('/api/campaigns', json=data)
    assert request.status_code == 201

    data = {'alias': 'asdf2', 'campaign': 'asdf'}
    request = client.post('/api/campaigns/alias', json=data)
    response = json.loads(request.data.decode())
    _id = response['id']
    assert request.status_code == 201

    data = {'campaign': 'asdf2'}
    request = client.put('/api/campaigns/alias/{}'.format(_id), json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['msg'] == 'Campaign not found'


def test_update_missing_token(app, client):
    """ Ensure a token is given if the config requires it """

    app.config['PUT'] = 'analyst'

    request = client.put('/api/campaigns/alias/1')
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Missing Authorization Header'


def test_update_invalid_role(app, client):
    """ Ensure the given token has the proper role access """

    app.config['PUT'] = 'user_does_not_have_this_role'

    access_token, refresh_token = obtain_token(client, 'analyst', 'analyst')
    headers = create_auth_header(access_token)
    request = client.put('/api/campaigns/alias/1', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'user_does_not_have_this_role role required'


def test_update(client):
    """ Ensure a proper request actually works """

    data = {'name': 'asdf'}
    request = client.post('/api/campaigns', json=data)
    assert request.status_code == 201

    data = {'alias': 'asdf2', 'campaign': 'asdf'}
    request = client.post('/api/campaigns/alias', json=data)
    response = json.loads(request.data.decode())
    _id = response['id']
    assert request.status_code == 201

    data = {'alias': 'asdf3'}
    request = client.put('/api/campaigns/alias/{}'.format(_id), json=data)
    assert request.status_code == 200

    request = client.get('/api/campaigns/alias/{}'.format(_id))
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert response['alias'] == 'asdf3'


"""
DELETE TESTS
"""


def test_delete_nonexistent_id(client):
    """ Ensure a nonexistent ID does not work """

    request = client.delete('/api/campaigns/alias/100000')
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['msg'] == 'Campaign alias ID not found'


def test_delete_missing_token(app, client):
    """ Ensure a token is given if the config requires it """

    app.config['DELETE'] = 'admin'

    request = client.delete('/api/campaigns/alias/1')
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Missing Authorization Header'


def test_delete_invalid_role(app, client):
    """ Ensure the given token has the proper role access """

    app.config['DELETE'] = 'user_does_not_have_this_role'

    access_token, refresh_token = obtain_token(client, 'analyst', 'analyst')
    headers = create_auth_header(access_token)
    request = client.delete('/api/campaigns/alias/1', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'user_does_not_have_this_role role required'


def test_delete(client):
    """ Ensure a proper request actually works """

    data = {'name': 'asdf'}
    request = client.post('/api/campaigns', json=data)
    assert request.status_code == 201

    data = {'alias': 'asdf2', 'campaign': 'asdf'}
    request = client.post('/api/campaigns/alias', json=data)
    response = json.loads(request.data.decode())
    _id = response['id']
    assert request.status_code == 201

    request = client.delete('/api/campaigns/alias/{}'.format(_id))
    assert request.status_code == 204

    request = client.get('/api/campaigns/alias/{}'.format(_id))
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['msg'] == 'Campaign alias ID not found'
