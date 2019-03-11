from project.tests.conftest import TEST_ANALYST_APIKEY, TEST_INACTIVE_APIKEY, TEST_INVALID_APIKEY
from project.tests.helpers import *


"""
CREATE TESTS
"""


def test_create_schema(client):
    """ Ensure POST requests conform to the required JSON schema """

    data = {'asdf': 'asdf'}
    request = client.post('/api/indicators/1/2/relationship', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "is not of type 'null'" in response['msg']


def test_create_nonexistent_id(client):
    """ Ensure a nonexistent ID does not work """

    indicator1_request, indicator1_response = create_indicator(client, 'asdf', 'asdf', 'analyst')
    assert indicator1_request.status_code == 201

    request = client.post('/api/indicators/{}/100000/relationship'.format(indicator1_response['id']))
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert 'Child indicator ID not found' in response['msg']

    request = client.post('/api/indicators/100000/{}/relationship'.format(indicator1_response['id']))
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert 'Parent indicator ID not found' in response['msg']


def test_create_duplicate(client):
    """ Ensure a duplicate record cannot be created """

    indicator1_request, indicator1_response = create_indicator(client, 'asdf', 'asdf', 'analyst')
    indicator2_request, indicator2_response = create_indicator(client, 'asdf2', 'asdf2', 'analyst')
    assert indicator1_request.status_code == 201
    assert indicator2_request.status_code == 201

    request = client.post('/api/indicators/{}/{}/relationship'.format(indicator1_response['id'], indicator2_response['id']))
    assert request.status_code == 204

    request = client.post('/api/indicators/{}/{}/relationship'.format(indicator1_response['id'], indicator2_response['id']))
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert response['msg'] == 'Child indicator already has a parent'


def test_create_missing_api_key(app, client):
    """ Ensure an API key is given if the config requires it """

    app.config['POST'] = 'analyst'

    request = client.post('/api/indicators/1/2/relationship')
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Bad or missing API key'


def test_create_invalid_api_key(app, client):
    """ Ensure an API key not found in the database does not work """

    app.config['POST'] = 'analyst'

    headers = {'Authorization': 'Apikey ' + TEST_INVALID_APIKEY}
    request = client.post('/api/indicators/1/2/relationship', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'API user does not exist'


def test_create_inactive_api_key(app, client):
    """ Ensure an inactive API key does not work """

    app.config['POST'] = 'analyst'

    headers = {'Authorization': 'Apikey ' + TEST_INACTIVE_APIKEY}
    request = client.post('/api/indicators/1/2/relationship', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'API user is not active'


def test_create_invalid_role(app, client):
    """ Ensure the given API key has the proper role access """

    app.config['POST'] = 'user_does_not_have_this_role'

    headers = {'Authorization': 'Apikey ' + TEST_ANALYST_APIKEY}
    request = client.post('/api/indicators/1/2/relationship', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Insufficient privileges'


def test_create(client):
    """ Ensure a proper request actually works """

    indicator1_request, indicator1_response = create_indicator(client, 'asdf', 'asdf', 'analyst')
    indicator2_request, indicator2_response = create_indicator(client, 'asdf2', 'asdf2', 'analyst')
    assert indicator1_request.status_code == 201
    assert indicator2_request.status_code == 201

    request = client.post('/api/indicators/{}/{}/relationship'.format(indicator1_response['id'], indicator2_response['id']))
    assert request.status_code == 204


"""
DELETE TESTS
"""


def test_delete_nonexistent_id(client):
    """ Ensure a nonexistent ID does not work """

    indicator1_request, indicator1_response = create_indicator(client, 'asdf', 'asdf', 'analyst')
    assert indicator1_request.status_code == 201

    request = client.delete('/api/indicators/{}/100000/relationship'.format(indicator1_response['id']))
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert 'Child indicator ID not found' in response['msg']

    request = client.delete('/api/indicators/100000/{}/relationship'.format(indicator1_response['id']))
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert 'Parent indicator ID not found' in response['msg']


def test_delete_missing_api_key(app, client):
    """ Ensure an API key is given if the config requires it """

    app.config['DELETE'] = 'admin'

    request = client.delete('/api/indicators/1/2/relationship')
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Bad or missing API key'


def test_delete_invalid_api_key(app, client):
    """ Ensure an API key not found in the database does not work """

    app.config['DELETE'] = 'admin'

    headers = {'Authorization': 'Apikey ' + TEST_INVALID_APIKEY}
    request = client.delete('/api/indicators/1/2/relationship', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'API user does not exist'


def test_delete_inactive_api_key(app, client):
    """ Ensure an inactive API key does not work """

    app.config['DELETE'] = 'admin'

    headers = {'Authorization': 'Apikey ' + TEST_INACTIVE_APIKEY}
    request = client.delete('/api/indicators/1/2/relationship', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'API user is not active'


def test_delete_invalid_role(app, client):
    """ Ensure the given API key has the proper role access """

    app.config['DELETE'] = 'user_does_not_have_this_role'

    headers = {'Authorization': 'Apikey ' + TEST_ANALYST_APIKEY}
    request = client.delete('/api/indicators/1/2/relationship', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Insufficient privileges'


def test_delete(client):
    """ Ensure a proper request actually works """

    indicator1_request, indicator1_response = create_indicator(client, 'asdf', 'asdf', 'analyst')
    indicator2_request, indicator2_response = create_indicator(client, 'asdf2', 'asdf2', 'analyst')
    assert indicator1_request.status_code == 201
    assert indicator2_request.status_code == 201

    request = client.post('/api/indicators/{}/{}/relationship'.format(indicator1_response['id'], indicator2_response['id']))
    assert request.status_code == 204

    request = client.delete('/api/indicators/{}/{}/relationship'.format(indicator1_response['id'], indicator2_response['id']))
    assert request.status_code == 204

    request = client.delete('/api/indicators/{}/{}/relationship'.format(indicator1_response['id'], indicator2_response['id']))
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['msg'] == 'Relationship does not exist'
