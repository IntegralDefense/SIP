from project.tests.helpers import *


"""
CREATE TESTS
"""


def test_create_schema(client):
    """ Ensure POST requests conform to the required JSON schema """

    data = {'asdf': 'asdf'}
    request = client.post('/api/indicators/1/2/equal', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "is not of type 'null'" in response['msg']


def test_create_nonexistent_id(client):
    """ Ensure a nonexistent ID does not work """

    indicator1_request, indicator1_response = create_indicator(client, 'asdf', 'asdf', 'analyst')
    assert indicator1_request.status_code == 201

    request = client.post('/api/indicators/{}/100000/equal'.format(indicator1_response['id']))
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert 'Indicator ID not found' in response['msg']

    request = client.post('/api/indicators/100000/{}/equal'.format(indicator1_response['id']))
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert 'Indicator ID not found' in response['msg']


def test_create_duplicate(client):
    """ Ensure a duplicate record cannot be created """

    indicator1_request, indicator1_response = create_indicator(client, 'asdf', 'asdf', 'analyst')
    indicator2_request, indicator2_response = create_indicator(client, 'asdf2', 'asdf2', 'analyst')
    assert indicator1_request.status_code == 201
    assert indicator2_request.status_code == 201

    request = client.post('/api/indicators/{}/{}/equal'.format(indicator1_response['id'], indicator2_response['id']))
    assert request.status_code == 204

    request = client.post('/api/indicators/{}/{}/equal'.format(indicator1_response['id'], indicator2_response['id']))
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert response['msg'] == 'The indicators are already equal'


def test_create_missing_token(app, client):
    """ Ensure a token is given if the config requires it """

    app.config['POST'] = 'analyst'

    request = client.post('/api/indicators/1/2/equal')
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Missing Authorization Header'


def test_create_invalid_role(app, client):
    """ Ensure the given token has the proper role access """

    app.config['POST'] = 'user_does_not_have_this_role'

    access_token, refresh_token = obtain_token(client, 'analyst', 'analyst')
    headers = create_auth_header(access_token)
    request = client.post('/api/indicators/1/2/equal', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'user_does_not_have_this_role role required'


def test_create(client):
    """ Ensure a proper request actually works """

    indicator1_request, indicator1_response = create_indicator(client, 'asdf', 'asdf', 'analyst')
    indicator2_request, indicator2_response = create_indicator(client, 'asdf2', 'asdf2', 'analyst')
    assert indicator1_request.status_code == 201
    assert indicator2_request.status_code == 201

    request = client.post('/api/indicators/{}/{}/equal'.format(indicator1_response['id'], indicator2_response['id']))
    assert request.status_code == 204


"""
DELETE TESTS
"""


def test_delete_nonexistent_id(client):
    """ Ensure a nonexistent ID does not work """

    indicator1_request, indicator1_response = create_indicator(client, 'asdf', 'asdf', 'analyst')
    assert indicator1_request.status_code == 201

    request = client.delete('/api/indicators/{}/100000/equal'.format(indicator1_response['id']))
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert 'Indicator ID not found' in response['msg']

    request = client.delete('/api/indicators/100000/{}/equal'.format(indicator1_response['id']))
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert 'Indicator ID not found' in response['msg']


def test_delete_missing_token(app, client):
    """ Ensure a token is given if the config requires it """

    app.config['DELETE'] = 'admin'

    request = client.delete('/api/indicators/1/2/equal')
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Missing Authorization Header'


def test_delete_invalid_role(app, client):
    """ Ensure the given token has the proper role access """

    app.config['DELETE'] = 'user_does_not_have_this_role'

    access_token, refresh_token = obtain_token(client, 'analyst', 'analyst')
    headers = create_auth_header(access_token)
    request = client.delete('/api/indicators/1/2/equal', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'user_does_not_have_this_role role required'


def test_delete(client):
    """ Ensure a proper request actually works """

    indicator1_request, indicator1_response = create_indicator(client, 'asdf', 'asdf', 'analyst')
    indicator2_request, indicator2_response = create_indicator(client, 'asdf2', 'asdf2', 'analyst')
    assert indicator1_request.status_code == 201
    assert indicator2_request.status_code == 201

    request = client.post('/api/indicators/{}/{}/equal'.format(indicator1_response['id'], indicator2_response['id']))
    assert request.status_code == 204

    request = client.delete('/api/indicators/{}/{}/equal'.format(indicator1_response['id'], indicator2_response['id']))
    assert request.status_code == 204

    request = client.delete('/api/indicators/{}/{}/equal'.format(indicator1_response['id'], indicator2_response['id']))
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert response['msg'] == 'Relationship does not exist or the indicators are not directly equal'
