from project.tests.conftest import TEST_ANALYST_APIKEY, TEST_INACTIVE_APIKEY, TEST_INVALID_APIKEY
from project.tests.helpers import *


"""
CREATE TESTS
"""


def test_create_schema(client):
    """ Ensure POST requests conform to the required JSON schema """

    # Invalid JSON
    data = {}
    request = client.post('/api/campaigns', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert response['msg'] == 'Request must include valid JSON'

    # Missing required name parameter
    data = {'asdf': 'asdf'}
    request = client.post('/api/campaigns', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert response['msg'] == "Request JSON does not match schema: 'name' is a required property"

    # Additional parameter
    data = {'name': 'asdf', 'asdf': 'asdf'}
    request = client.post('/api/campaigns', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'Additional properties are not allowed' in response['msg']

    # Invalid name parameter type
    data = {'name': 1}
    request = client.post('/api/campaigns', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # name parameter too short
    data = {'name': ''}
    request = client.post('/api/campaigns', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # name parameter too long
    data = {'name': 'a' * 256}
    request = client.post('/api/campaigns', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']

    # Invalid aliases parameter type
    data = {'name': 'asdf', 'aliases': 'asdf'}
    request = client.post('/api/campaigns', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "'asdf' is not of type 'array'" in response['msg']

    # Invalid aliases parameter type
    data = {'name': 'asdf', 'aliases': [1]}
    request = client.post('/api/campaigns', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # Empty aliases parameter type
    data = {'name': 'asdf', 'aliases': []}
    request = client.post('/api/campaigns', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # alias parameter too short
    data = {'name': 'asdf', 'aliases': ['']}
    request = client.post('/api/campaigns', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # alias parameter too long
    data = {'name': 'asdf', 'aliases': ['a' * 256]}
    request = client.post('/api/campaigns', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']


def test_create_missing_api_key(app, client):
    """ Ensure an API key is given if the config requires it """

    app.config['POST'] = 'analyst'

    request = client.post('/api/campaigns')
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Bad or missing API key'


def test_create_invalid_api_key(app, client):
    """ Ensure an API key not found in the database does not work """

    app.config['POST'] = 'analyst'

    headers = {'Authorization': 'Apikey ' + TEST_INVALID_APIKEY}
    request = client.post('/api/campaigns', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'API user does not exist'


def test_create_inactive_api_key(app, client):
    """ Ensure an inactive API key does not work """

    app.config['POST'] = 'analyst'

    headers = {'Authorization': 'Apikey ' + TEST_INACTIVE_APIKEY}
    request = client.post('/api/campaigns', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'API user is not active'


def test_create_invalid_role(app, client):
    """ Ensure the given API key has the proper role access """

    app.config['POST'] = 'user_does_not_have_this_role'

    headers = {'Authorization': 'Apikey ' + TEST_ANALYST_APIKEY}
    request = client.post('/api/campaigns', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Insufficient privileges'


def test_create_duplicate(client):
    """ Ensure a duplicate record cannot be created """

    data = {'name': 'asdf'}
    request = client.post('/api/campaigns', json=data)
    assert request.status_code == 201

    data = {'name': 'asdf'}
    request = client.post('/api/campaigns', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 409
    assert response['msg'] == 'Campaign already exists'


def test_create(client):
    """ Ensure a proper request actually works """

    data = {'name': 'asdf'}
    request = client.post('/api/campaigns', json=data)
    assert request.status_code == 201


"""
READ TESTS
"""


def test_read_nonexistent_id(client):
    """ Ensure a nonexistent ID does not work """

    request = client.get('/api/campaigns/100000')
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['msg'] == 'Campaign ID not found'


def test_read_missing_api_key(app, client):
    """ Ensure an API key is given if the config requires it """

    app.config['GET'] = 'analyst'

    request = client.get('/api/campaigns/1')
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Bad or missing API key'


def test_read_invalid_api_key(app, client):
    """ Ensure an API key not found in the database does not work """

    app.config['GET'] = 'analyst'

    headers = {'Authorization': 'Apikey ' + TEST_INVALID_APIKEY}
    request = client.get('/api/campaigns/1', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'API user does not exist'


def test_read_inactive_api_key(app, client):
    """ Ensure an inactive API key does not work """

    app.config['GET'] = 'analyst'

    headers = {'Authorization': 'Apikey ' + TEST_INACTIVE_APIKEY}
    request = client.get('/api/campaigns/1', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'API user is not active'


def test_read_invalid_role(app, client):
    """ Ensure the given API key has the proper role access """

    app.config['GET'] = 'user_does_not_have_this_role'

    headers = {'Authorization': 'Apikey ' + TEST_ANALYST_APIKEY}
    request = client.get('/api/campaigns/1', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Insufficient privileges'


def test_read_all_values(client):
    """ Ensure all values properly return """

    data = {'name': 'asdf'}
    request = client.post('/api/campaigns', json=data)
    assert request.status_code == 201

    data = {'name': 'asdf2'}
    request = client.post('/api/campaigns', json=data)
    assert request.status_code == 201

    data = {'name': 'asdf3'}
    request = client.post('/api/campaigns', json=data)
    assert request.status_code == 201

    request = client.get('/api/campaigns')
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response) == 3


def test_read_by_id(client):
    """ Ensure names can be read by their ID """

    data = {'name': 'asdf'}
    request = client.post('/api/campaigns', json=data)
    response = json.loads(request.data.decode())
    _id = response['id']
    assert request.status_code == 201

    request = client.get('/api/campaigns/{}'.format(_id))
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert response['name'] == 'asdf'


"""
UPDATE TESTS
"""


def test_update_schema(client):
    """ Ensure PUT requests conform to the required JSON schema """

    # Invalid JSON
    data = {}
    request = client.put('/api/campaigns/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert response['msg'] == 'Request must include valid JSON'

    # Missing required name parameter
    data = {'asdf': 'asdf'}
    request = client.put('/api/campaigns/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert response['msg'] == "Request JSON does not match schema: 'name' is a required property"

    # Additional parameter
    data = {'name': 'asdf', 'asdf': 'asdf'}
    request = client.put('/api/campaigns/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'Additional properties are not allowed' in response['msg']

    # Invalid name parameter type
    data = {'name': 1}
    request = client.put('/api/campaigns/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # name parameter too short
    data = {'name': ''}
    request = client.put('/api/campaigns/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # name parameter too long
    data = {'name': 'a' * 256}
    request = client.put('/api/campaigns/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']


def test_update_nonexistent_id(client):
    """ Ensure a nonexistent ID does not work """

    data = {'name': 'asdf'}
    request = client.put('/api/campaigns/100000', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['msg'] == 'Campaign ID not found'


def test_update_duplicate(client):
    """ Ensure duplicate records cannot be updated """

    data = {'name': 'asdf'}
    request = client.post('/api/campaigns', json=data)
    response = json.loads(request.data.decode())
    _id = response['id']
    assert request.status_code == 201

    data = {'name': 'asdf'}
    request = client.put('/api/campaigns/{}'.format(_id), json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 409
    assert response['msg'] == 'Campaign already exists'


def test_update_missing_api_key(app, client):
    """ Ensure an API key is given if the config requires it """

    app.config['PUT'] = 'analyst'

    request = client.put('/api/campaigns/1')
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Bad or missing API key'


def test_update_invalid_api_key(app, client):
    """ Ensure an API key not found in the database does not work """

    app.config['PUT'] = 'analyst'

    headers = {'Authorization': 'Apikey ' + TEST_INVALID_APIKEY}
    request = client.put('/api/campaigns/1', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'API user does not exist'


def test_update_inactive_api_key(app, client):
    """ Ensure an inactive API key does not work """

    app.config['PUT'] = 'analyst'

    headers = {'Authorization': 'Apikey ' + TEST_INACTIVE_APIKEY}
    request = client.put('/api/campaigns/1', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'API user is not active'


def test_update_invalid_role(app, client):
    """ Ensure the given API key has the proper role access """

    app.config['PUT'] = 'user_does_not_have_this_role'

    headers = {'Authorization': 'Apikey ' + TEST_ANALYST_APIKEY}
    request = client.put('/api/campaigns/1', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Insufficient privileges'


def test_update(client):
    """ Ensure a proper request actually works """

    data = {'name': 'asdf'}
    request = client.post('/api/campaigns', json=data)
    response = json.loads(request.data.decode())
    _id = response['id']
    assert request.status_code == 201

    data = {'name': 'asdf2'}
    request = client.put('/api/campaigns/{}'.format(_id), json=data)
    response = json.loads(request.data.decode())
    print(response)
    assert request.status_code == 200

    request = client.get('/api/campaigns/{}'.format(_id))
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert response['name'] == 'asdf2'


"""
DELETE TESTS
"""


def test_delete_nonexistent_id(client):
    """ Ensure a nonexistent ID does not work """

    request = client.delete('/api/campaigns/100000')
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['msg'] == 'Campaign ID not found'


def test_delete_missing_api_key(app, client):
    """ Ensure an API key is given if the config requires it """

    app.config['DELETE'] = 'admin'

    request = client.delete('/api/campaigns/1')
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Bad or missing API key'


def test_delete_invalid_api_key(app, client):
    """ Ensure an API key not found in the database does not work """

    app.config['DELETE'] = 'admin'

    headers = {'Authorization': 'Apikey ' + TEST_INVALID_APIKEY}
    request = client.delete('/api/campaigns/1', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'API user does not exist'


def test_delete_inactive_api_key(app, client):
    """ Ensure an inactive API key does not work """

    app.config['DELETE'] = 'admin'

    headers = {'Authorization': 'Apikey ' + TEST_INACTIVE_APIKEY}
    request = client.delete('/api/campaigns/1', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'API user is not active'


def test_delete_invalid_role(app, client):
    """ Ensure the given API key has the proper role access """

    app.config['DELETE'] = 'user_does_not_have_this_role'

    headers = {'Authorization': 'Apikey ' + TEST_ANALYST_APIKEY}
    request = client.delete('/api/campaigns/1', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Insufficient privileges'


def test_delete_foreign_key_indicator(client):
    """ Ensure you cannot delete with foreign key constraints """

    campaign_request, campaign_response = create_campaign(client, 'Derpsters')
    indicator_request, indicator_response = create_indicator(client, 'IP', '127.0.0.1', 'analyst', campaigns=['Derpsters'])
    assert campaign_request.status_code == 201
    assert indicator_request.status_code == 201

    request = client.delete('/api/campaigns/{}'.format(campaign_response['id']))
    response = json.loads(request.data.decode())
    assert request.status_code == 409
    assert response['msg'] == 'Unable to delete campaign due to foreign key constraints'


def test_delete_foreign_key_alias(client):
    """ Ensure that deleting a campaign also deletes its aliases """

    campaign_request, campaign_response = create_campaign(client, 'Derpsters')
    alias_request, alias_response = create_campaign_alias(client, 'asdf', 'Derpsters')
    assert campaign_request.status_code == 201
    assert alias_request.status_code == 201

    request = client.get('/api/campaigns/alias')
    response = json.loads(request.data.decode())
    assert len(response) == 1

    request = client.delete('/api/campaigns/{}'.format(campaign_response['id']))
    assert request.status_code == 204

    request = client.get('/api/campaigns/alias')
    response = json.loads(request.data.decode())
    assert len(response) == 0


def test_delete(client):
    """ Ensure a proper request actually works """

    data = {'name': 'asdf'}
    request = client.post('/api/campaigns', json=data)
    response = json.loads(request.data.decode())
    _id = response['id']
    assert request.status_code == 201

    request = client.delete('/api/campaigns/{}'.format(_id))
    assert request.status_code == 204

    request = client.get('/api/campaigns/{}'.format(_id))
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['msg'] == 'Campaign ID not found'
