from project.tests.conftest import TEST_ANALYST_APIKEY, TEST_INACTIVE_APIKEY, TEST_INVALID_APIKEY
from project.tests.helpers import *


"""
CREATE TESTS
"""


def test_create_schema(client):
    """ Ensure POST requests conform to the required JSON schema """

    # Invalid JSON
    data = {}
    request = client.post('/api/intel/reference', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert response['msg'] == 'Request must include valid JSON'

    # Missing required reference parameter
    data = {'source': 'asdf', 'username': 'asdf'}
    request = client.post('/api/intel/reference', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert response['msg'] == "Request JSON does not match schema: 'reference' is a required property"

    # Missing required source parameter
    data = {'reference': 'asdf', 'username': 'asdf'}
    request = client.post('/api/intel/reference', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert response['msg'] == "Request JSON does not match schema: 'source' is a required property"

    # Additional parameter
    data = {'reference': 'asdf', 'source': 'asdf', 'username': 'asdf', 'asdf': 'asdf'}
    request = client.post('/api/intel/reference', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'Additional properties are not allowed' in response['msg']

    # Invalid reference parameter type
    data = {'reference': 1, 'source': 'asdf', 'username': 'asdf'}
    request = client.post('/api/intel/reference', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # reference parameter too short
    data = {'reference': '', 'source': 'asdf', 'username': 'asdf'}
    request = client.post('/api/intel/reference', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # reference parameter too long
    data = {'reference': 'a' * 513, 'source': 'asdf', 'username': 'asdf'}
    request = client.post('/api/intel/reference', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']

    # Invalid source parameter type
    data = {'reference': 'asdf', 'source': 1, 'username': 'asdf'}
    request = client.post('/api/intel/reference', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # source parameter too short
    data = {'reference': 'asdf', 'source': '', 'username': 'asdf'}
    request = client.post('/api/intel/reference', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # source parameter too long
    data = {'reference': 'asdf', 'source': 'a' * 256, 'username': 'asdf'}
    request = client.post('/api/intel/reference', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']

    # Invalid username parameter type
    data = {'reference': 'asdf', 'source': 'asdf', 'username': 1}
    request = client.post('/api/intel/reference', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # username parameter too short
    data = {'reference': 'asdf', 'source': 'asdf', 'username': ''}
    request = client.post('/api/intel/reference', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # username parameter too long
    data = {'reference': 'asdf', 'source': 'asdf', 'username': 'a' * 256}
    request = client.post('/api/intel/reference', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']


def test_create_duplicate(client):
    """ Ensure a duplicate record cannot be created """

    data = {'value': 'asdf'}
    request = client.post('/api/intel/source', json=data)
    assert request.status_code == 201

    data = {'username': 'analyst', 'reference': 'asdf', 'source': 'asdf'}
    request = client.post('/api/intel/reference', json=data)
    assert request.status_code == 201

    data = {'username': 'analyst', 'reference': 'asdf', 'source': 'asdf'}
    request = client.post('/api/intel/reference', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 409
    assert response['msg'] == 'Intel reference already exists'


def test_create_nonexistent_source(app, client):
    """ Ensure a reference cannot be created with a nonexistent source """

    app.config['INTELREFERENCE_AUTO_CREATE_INTELSOURCE'] = False

    data = {'username': 'analyst', 'reference': 'asdf', 'source': 'asdf'}
    request = client.post('/api/intel/reference', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['msg'] == 'Intel source not found: asdf'


def test_create_missing_api_key(app, client):
    """ Ensure an API key is given if the config requires it """

    app.config['POST'] = 'analyst'

    request = client.post('/api/intel/reference')
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Bad or missing API key'


def test_create_invalid_api_key(app, client):
    """ Ensure an API key not found in the database does not work """

    app.config['POST'] = 'analyst'

    headers = {'Authorization': 'Apikey ' + TEST_INVALID_APIKEY}
    request = client.post('/api/intel/reference', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'API user does not exist'


def test_create_inactive_api_key(app, client):
    """ Ensure an inactive API key does not work """

    app.config['POST'] = 'analyst'

    headers = {'Authorization': 'Apikey ' + TEST_INACTIVE_APIKEY}
    request = client.post('/api/intel/reference', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'API user is not active'


def test_create_invalid_role(app, client):
    """ Ensure the given API key has the proper role access """

    app.config['POST'] = 'user_does_not_have_this_role'

    headers = {'Authorization': 'Apikey ' + TEST_ANALYST_APIKEY}
    request = client.post('/api/intel/reference', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Insufficient privileges'


def test_create_api_key_instead_of_username(app, client):
    """ Ensure that supplying an API key instead of username value works """

    app.config['INTELREFERENCE_AUTO_CREATE_INTELSOURCE'] = True

    # Try a missing API key.
    data = {'reference': 'http://blahblah.com',
            'source': 'OSINT'}
    request = client.post('/api/intel/reference', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'You must supply either username or API key'

    # Try an invalid API key.
    headers = {'Authorization': 'Apikey ' + 'this-api-key-does-not-exist'}
    data = {'reference': 'http://blahblah.com',
            'source': 'OSINT'}
    request = client.post('/api/intel/reference', headers=headers, json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['msg'] == 'User not found by API key'

    # Try an inactive API key.
    headers = {'Authorization': 'Apikey ' + TEST_INACTIVE_APIKEY}
    data = {'reference': 'http://blahblah.com',
            'source': 'OSINT'}
    request = client.post('/api/intel/reference', headers=headers, json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Cannot create an intel reference with an inactive user'

    # Try a valid API key.
    headers = {'Authorization': 'Apikey ' + TEST_ANALYST_APIKEY}
    data = {'reference': 'http://blahblah.com',
            'source': 'OSINT'}
    request = client.post('/api/intel/reference', headers=headers, json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 201
    assert response['user'] == 'analyst'


def test_create_autocreate_intel_source(app, client):
    """ Ensure the auto-create intel source config actually works """

    app.config['INTELREFERENCE_AUTO_CREATE_INTELSOURCE'] = False

    data = {'reference': 'http://blahblah.com',
            'source': 'OSINT',
            'username': 'analyst'}

    request = client.post('/api/intel/reference', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['msg'] == 'Intel source not found: OSINT'

    app.config['INTELREFERENCE_AUTO_CREATE_INTELSOURCE'] = True

    request = client.post('/api/intel/reference', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 201
    assert response['source'] == 'OSINT'


def test_create(client):
    """ Ensure a proper request actually works """

    data = {'value': 'asdf'}
    request = client.post('/api/intel/source', json=data)
    assert request.status_code == 201

    data = {'username': 'analyst', 'reference': 'asdf', 'source': 'asdf'}
    request = client.post('/api/intel/reference', json=data)
    assert request.status_code == 201


"""
READ TESTS
"""


def test_read_nonexistent_id(client):
    """ Ensure a nonexistent ID does not work """

    request = client.get('/api/intel/reference/100000')
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['msg'] == 'Intel reference ID not found'


def test_read_missing_api_key(app, client):
    """ Ensure an API key is given if the config requires it """

    app.config['GET'] = 'analyst'

    request = client.get('/api/intel/reference/1')
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Bad or missing API key'


def test_read_invalid_api_key(app, client):
    """ Ensure an API key not found in the database does not work """

    app.config['GET'] = 'analyst'

    headers = {'Authorization': 'Apikey ' + TEST_INVALID_APIKEY}
    request = client.get('/api/intel/reference/1', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'API user does not exist'


def test_read_inactive_api_key(app, client):
    """ Ensure an inactive API key does not work """

    app.config['GET'] = 'analyst'

    headers = {'Authorization': 'Apikey ' + TEST_INACTIVE_APIKEY}
    request = client.get('/api/intel/reference/1', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'API user is not active'


def test_read_invalid_role(app, client):
    """ Ensure the given API key has the proper role access """

    app.config['GET'] = 'user_does_not_have_this_role'

    headers = {'Authorization': 'Apikey ' + TEST_ANALYST_APIKEY}
    request = client.get('/api/intel/reference/1', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Insufficient privileges'


def test_read_all_values(client):
    """ Ensure all values properly return """

    data = {'value': 'asdf'}
    request = client.post('/api/intel/source', json=data)
    assert request.status_code == 201

    data = {'username': 'analyst', 'reference': 'asdf', 'source': 'asdf'}
    request = client.post('/api/intel/reference', json=data)
    assert request.status_code == 201

    data = {'username': 'analyst', 'reference': 'asdf2', 'source': 'asdf'}
    request = client.post('/api/intel/reference', json=data)
    assert request.status_code == 201

    data = {'username': 'analyst', 'reference': 'asdf3', 'source': 'asdf'}
    request = client.post('/api/intel/reference', json=data)
    assert request.status_code == 201

    request = client.get('/api/intel/reference')
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response) == 3


def test_read_by_id(client):
    """ Ensure names can be read by their ID """

    data = {'value': 'asdf'}
    request = client.post('/api/intel/source', json=data)
    assert request.status_code == 201

    data = {'username': 'analyst', 'reference': 'asdf', 'source': 'asdf'}
    request = client.post('/api/intel/reference', json=data)
    response = json.loads(request.data.decode())
    _id = response['id']
    assert request.status_code == 201

    request = client.get('/api/intel/reference/{}'.format(_id))
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert response['reference'] == 'asdf'


def test_read_indicators(client):
    """ Ensure indicators associated with this reference can be read """

    create_intel_source(client, 'OSINT')
    create_intel_source(client, 'VirusTotal')

    intel_reference1_request, intel_reference1_response = create_intel_reference(client, 'analyst', 'OSINT', 'http://blahblah.com')
    intel_reference2_request, intel_reference2_response = create_intel_reference(client, 'analyst', 'VirusTotal', 'http://virustotal.com')
    assert intel_reference1_request.status_code == 201
    assert intel_reference2_request.status_code == 201

    indicator1_request, indicator1_response = create_indicator(client, 'IP', '127.0.0.1', 'analyst', intel_reference='http://blahblah.com', intel_source='OSINT')
    indicator2_request, indicator2_response = create_indicator(client, 'Email', 'asdf@asdf.com', 'analyst', intel_reference='http://virustotal.com', intel_source='VirusTotal')
    assert indicator1_request.status_code == 201
    assert indicator2_request.status_code == 201

    request = client.get('/api/intel/reference/{}/indicators'.format(intel_reference1_response['id']))
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 1
    assert response['items'][0]['value'] == '127.0.0.1'


"""
UPDATE TESTS
"""


def test_update_schema(client):
    """ Ensure PUT requests conform to the required JSON schema """

    # Invalid JSON
    data = {}
    request = client.put('/api/intel/reference/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert response['msg'] == 'Request must include valid JSON'

    # Additional parameter
    data = {'reference': 'asdf', 'source': 'asdf', 'username': 'asdf', 'asdf': 'asdf'}
    request = client.put('/api/intel/reference/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'Additional properties are not allowed' in response['msg']

    # Invalid reference parameter type
    data = {'reference': 1, 'source': 'asdf', 'username': 'asdf'}
    request = client.put('/api/intel/reference/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # reference parameter too short
    data = {'reference': '', 'source': 'asdf', 'username': 'asdf'}
    request = client.put('/api/intel/reference/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # reference parameter too long
    data = {'reference': 'a' * 513, 'source': 'asdf', 'username': 'asdf'}
    request = client.put('/api/intel/reference/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']

    # Invalid source parameter type
    data = {'reference': 'asdf', 'source': 1, 'username': 'asdf'}
    request = client.put('/api/intel/reference/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # source parameter too short
    data = {'reference': 'asdf', 'source': '', 'username': 'asdf'}
    request = client.put('/api/intel/reference/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # source parameter too long
    data = {'reference': 'asdf', 'source': 'a' * 256, 'username': 'asdf'}
    request = client.put('/api/intel/reference/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']

    # Invalid username parameter type
    data = {'reference': 'asdf', 'source': 'asdf', 'username': 1}
    request = client.put('/api/intel/reference/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # username parameter too short
    data = {'reference': 'asdf', 'source': 'asdf', 'username': ''}
    request = client.put('/api/intel/reference/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # username parameter too long
    data = {'reference': 'asdf', 'source': 'asdf', 'username': 'a' * 256}
    request = client.put('/api/intel/reference/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']


def test_update_nonexistent_id(client):
    """ Ensure a nonexistent ID does not work """

    data = {'reference': 'asdf', 'source': 'asdf'}
    request = client.put('/api/intel/reference/100000', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['msg'] == 'Intel reference ID not found'


def test_update_duplicate(client):
    """ Ensure duplicate records cannot be updated """

    data = {'value': 'asdf'}
    request = client.post('/api/intel/source', json=data)
    assert request.status_code == 201

    data = {'username': 'analyst', 'reference': 'asdf', 'source': 'asdf'}
    request = client.post('/api/intel/reference', json=data)
    response = json.loads(request.data.decode())
    _id = response['id']
    assert request.status_code == 201

    data = {'username': 'analyst', 'reference': 'asdf', 'source': 'asdf'}
    request = client.put('/api/intel/reference/{}'.format(_id), json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 409
    assert response['msg'] == 'Intel reference already exists'


def test_update_nonexistent_source(client):
    """ Ensure a reference cannot be updated with a nonexistent source """

    data = {'value': 'asdf'}
    request = client.post('/api/intel/source', json=data)
    assert request.status_code == 201

    data = {'username': 'analyst', 'reference': 'asdf', 'source': 'asdf'}
    request = client.post('/api/intel/reference', json=data)
    response = json.loads(request.data.decode())
    _id = response['id']
    assert request.status_code == 201

    data = {'source': 'asdf2'}
    request = client.put('/api/intel/reference/{}'.format(_id), json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['msg'] == 'Intel source not found'


def test_update_missing_api_key(app, client):
    """ Ensure an API key is given if the config requires it """

    app.config['PUT'] = 'analyst'

    request = client.put('/api/intel/reference/1')
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Bad or missing API key'


def test_update_invalid_api_key(app, client):
    """ Ensure an API key not found in the database does not work """

    app.config['PUT'] = 'analyst'

    headers = {'Authorization': 'Apikey ' + TEST_INVALID_APIKEY}
    request = client.put('/api/intel/reference/1', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'API user does not exist'


def test_update_inactive_api_key(app, client):
    """ Ensure an inactive API key does not work """

    app.config['PUT'] = 'analyst'

    headers = {'Authorization': 'Apikey ' + TEST_INACTIVE_APIKEY}
    request = client.put('/api/intel/reference/1', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'API user is not active'


def test_update_invalid_role(app, client):
    """ Ensure the given API key has the proper role access """

    app.config['PUT'] = 'user_does_not_have_this_role'

    headers = {'Authorization': 'Apikey ' + TEST_ANALYST_APIKEY}
    request = client.put('/api/intel/reference/1', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Insufficient privileges'


def test_update(client):
    """ Ensure a proper request actually works """

    data = {'value': 'asdf'}
    request = client.post('/api/intel/source', json=data)
    assert request.status_code == 201

    data = {'username': 'analyst', 'reference': 'asdf', 'source': 'asdf'}
    request = client.post('/api/intel/reference', json=data)
    response = json.loads(request.data.decode())
    _id = response['id']
    assert request.status_code == 201

    data = {'reference': 'asdf2'}
    request = client.put('/api/intel/reference/{}'.format(_id), json=data)
    assert request.status_code == 200

    request = client.get('/api/intel/reference/{}'.format(_id))
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert response['reference'] == 'asdf2'


"""
DELETE TESTS
"""


def test_delete_nonexistent_id(client):
    """ Ensure a nonexistent ID does not work """

    request = client.delete('/api/intel/reference/100000')
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['msg'] == 'Intel reference ID not found'


def test_delete_missing_api_key(app, client):
    """ Ensure an API key is given if the config requires it """

    app.config['DELETE'] = 'admin'

    request = client.delete('/api/intel/reference/1')
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Bad or missing API key'


def test_delete_invalid_api_key(app, client):
    """ Ensure an API key not found in the database does not work """

    app.config['DELETE'] = 'admin'

    headers = {'Authorization': 'Apikey ' + TEST_INVALID_APIKEY}
    request = client.delete('/api/intel/reference/1', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'API user does not exist'


def test_delete_inactive_api_key(app, client):
    """ Ensure an inactive API key does not work """

    app.config['DELETE'] = 'admin'

    headers = {'Authorization': 'Apikey ' + TEST_INACTIVE_APIKEY}
    request = client.delete('/api/intel/reference/1', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'API user is not active'


def test_delete_invalid_role(app, client):
    """ Ensure the given API key has the proper role access """

    app.config['DELETE'] = 'user_does_not_have_this_role'

    headers = {'Authorization': 'Apikey ' + TEST_ANALYST_APIKEY}
    request = client.delete('/api/intel/reference/1', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Insufficient privileges'


def test_delete_foreign_key_indicator(client):
    """ Ensure you cannot delete with foreign key constraints """

    reference_request, reference_response = create_intel_reference(client, 'analyst', 'OSINT', 'http://blahblah.com')
    indicator_request, indicator_response = create_indicator(client, 'IP', '127.0.0.1', 'analyst', intel_reference='http://blahblah.com', intel_source='OSINT')
    assert reference_request.status_code == 201
    assert indicator_request.status_code == 201

    request = client.delete('/api/intel/reference/{}'.format(reference_response['id']))
    response = json.loads(request.data.decode())
    assert request.status_code == 409
    assert response['msg'] == 'Unable to delete intel reference due to foreign key constraints'


def test_delete(client):
    """ Ensure a proper request actually works """

    data = {'value': 'asdf'}
    request = client.post('/api/intel/source', json=data)
    assert request.status_code == 201

    data = {'username': 'analyst', 'reference': 'asdf', 'source': 'asdf'}
    request = client.post('/api/intel/reference', json=data)
    response = json.loads(request.data.decode())
    _id = response['id']
    assert request.status_code == 201

    request = client.delete('/api/intel/reference/{}'.format(_id))
    assert request.status_code == 204

    request = client.get('/api/intel/reference/{}'.format(_id))
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['msg'] == 'Intel reference ID not found'
