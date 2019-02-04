import datetime
import time

from project.tests.helpers import *


"""
CREATE TESTS
"""


def test_create_missing_parameter(client):
    """ Ensure the required parameters are given """

    # Missing type
    data = {'username': 'analyst', 'value': 'asdf'}
    request = client.post('/api/indicators', data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert response['msg'] == 'Request must include: type, username, value'

    # Missing username
    data = {'type': 'asdf', 'value': 'asdf'}
    request = client.post('/api/indicators', data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert response['msg'] == 'Request must include: type, username, value'

    # Missing value
    data = {'type': 'asdf', 'username': 'analyst'}
    request = client.post('/api/indicators', data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert response['msg'] == 'Request must include: type, username, value'


def test_create_duplicate(client):
    """ Ensure a duplicate record cannot be created """

    request, response = create_indicator(client, 'asdf', 'asdf', 'analyst')
    assert request.status_code == 201

    request, response = create_indicator(client, 'asdf', 'asdf', 'analyst')
    assert request.status_code == 409
    assert response['msg'] == 'Indicator already exists'


def test_create_nonexistent_username(client):
    """ Ensure an indicator cannot be created with a nonexistent username """

    request, response = create_indicator(client, 'asdf', 'asdf', 'this_user_does_not_exist')
    assert request.status_code == 404
    assert 'User username not found:' in response['msg']


def test_create_inactive_username(client):
    """ Ensure an indicator cannot be created with an inactive username """

    request, response = create_indicator(client, 'asdf', 'asdf', 'inactive')
    assert request.status_code == 401
    assert response['msg'] == 'Cannot create an indicator with an inactive user'


def test_create_missing_token(app, client):
    """ Ensure a token is given if the config requires it """

    app.config['POST'] = 'analyst'

    request = client.post('/api/indicators')
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Missing Authorization Header'


def test_create_invalid_role(app, client):
    """ Ensure the given token has the proper role access """

    app.config['POST'] = 'user_does_not_have_this_role'

    access_token, refresh_token = obtain_token(client, 'analyst', 'analyst')
    headers = create_auth_header(access_token)
    request = client.post('/api/indicators', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'user_does_not_have_this_role role required'


def test_create(client):
    """ Ensure a proper request actually works """

    request, response = create_indicator(client, 'asdf', 'asdf', 'analyst', campaigns='LOLcats,Derpsters',
                                         case_sensitive=True, confidence='HIGH', impact='HIGH',
                                         intel_reference='http://blahblah.com', intel_source='OSINT',
                                         status='Analyzed', substring=True, tags='phish,nanocore')
    assert request.status_code == 201
    assert response['type'] == 'asdf'
    assert response['value'] == 'asdf'
    assert response['user'] == 'analyst'
    assert sorted([response['campaigns'][0]['name'], response['campaigns'][1]['name']]) == ['Derpsters', 'LOLcats']
    assert response['case_sensitive'] is True
    assert response['confidence'] == 'HIGH'
    assert response['impact'] == 'HIGH'
    assert response['references'][0]['reference'] == 'http://blahblah.com'
    assert response['status'] == 'Analyzed'
    assert response['substring'] is True
    assert sorted(response['tags']) == ['nanocore', 'phish']


"""
READ TESTS
"""


def test_read_nonexistent_id(client):
    """ Ensure a nonexistent ID does not work """

    request = client.get('/api/indicators/100000')
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['msg'] == 'Indicator ID not found'


def test_read_missing_token(app, client):
    """ Ensure a token is given if the config requires it """

    app.config['GET'] = 'analyst'

    request = client.get('/api/indicators/1')
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Missing Authorization Header'


def test_read_invalid_role(app, client):
    """ Ensure the given token has the proper role access """

    app.config['GET'] = 'user_does_not_have_this_role'

    access_token, refresh_token = obtain_token(client, 'analyst', 'analyst')
    headers = create_auth_header(access_token)
    request = client.get('/api/indicators/1', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'user_does_not_have_this_role role required'


def test_read_all_values(client):
    """ Ensure all values properly return """

    request, response = create_indicator(client, 'asdf', 'asdf', 'analyst')
    assert request.status_code == 201

    request, response = create_indicator(client, 'asdf', 'asdf2', 'analyst')
    assert request.status_code == 201

    request, response = create_indicator(client, 'asdf', 'asdf3', 'analyst')
    assert request.status_code == 201

    request = client.get('/api/indicators')
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 3


def test_read_by_id(client):
    """ Ensure indicators can be read by their ID """

    request, response = create_indicator(client, 'asdf', 'asdf', 'analyst')
    _id = response['id']
    assert request.status_code == 201

    request = client.get('/api/indicators/{}'.format(_id))
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert response['type'] == 'asdf'
    assert response['value'] == 'asdf'
    assert response['user'] == 'analyst'


def test_read_with_filters(client):
    """ Ensure indicators can be read using the various filters """

    indicator1_request, indicator1_response = create_indicator(client, 'IP', '1.1.1.1', 'analyst',
                                                               campaigns='Derpsters',
                                                               case_sensitive=True,
                                                               confidence='HIGH',
                                                               impact='HIGH',
                                                               intel_reference='http://blahblah.com',
                                                               intel_source='OSINT',
                                                               status='Analyzed',
                                                               substring=True,
                                                               tags='phish')
    assert indicator1_request.status_code == 201

    time.sleep(1)

    indicator2_request, indicator2_response = create_indicator(client, 'Email', 'asdf@asdf.com', 'admin',
                                                               campaigns='LOLcats',
                                                               case_sensitive=False,
                                                               confidence='LOW',
                                                               impact='LOW',
                                                               intel_reference='http://blahblah2.com',
                                                               intel_source='VirusTotal',
                                                               status='New',
                                                               substring=False,
                                                               tags='nanocore')
    assert indicator2_request.status_code == 201

    time.sleep(1)

    # Filter by case_sensitive
    request = client.get('/api/indicators?case_sensitive=true')
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 1
    assert response['items'][0]['case_sensitive'] is True

    # Filter by created_before
    request = client.get('/api/indicators?created_before={}'.format(datetime.datetime.now()))
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 2
    request = client.get('/api/indicators?created_before={}'.format(indicator2_response['created_time']))
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 1
    assert response['items'][0]['value'] == '1.1.1.1'

    # Filter by created_after
    request = client.get('/api/indicators?created_after={}'.format(datetime.datetime.min))
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 2
    request = client.get('/api/indicators?created_after={}'.format(indicator1_response['created_time']))
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 1
    assert response['items'][0]['value'] == 'asdf@asdf.com'

    # Filter by confidence
    request = client.get('/api/indicators?confidence=HIGH')
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 1
    assert response['items'][0]['value'] == '1.1.1.1'

    # Filter by impact
    request = client.get('/api/indicators?impact=HIGH')
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 1
    assert response['items'][0]['value'] == '1.1.1.1'

    # Filter by modified_before
    request = client.get('/api/indicators?modified_before={}'.format(datetime.datetime.now()))
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 2
    request = client.get('/api/indicators?modified_before={}'.format(indicator2_response['modified_time']))
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 1
    assert response['items'][0]['value'] == '1.1.1.1'

    # Filter by modified_after
    request = client.get('/api/indicators?modified_after={}'.format(datetime.datetime.min))
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 2
    request = client.get('/api/indicators?modified_after={}'.format(indicator1_response['modified_time']))
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 1
    assert response['items'][0]['value'] == 'asdf@asdf.com'

    # Filter by status
    request = client.get('/api/indicators?status=Analyzed')
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 1
    assert response['items'][0]['value'] == '1.1.1.1'

    # Filter by tag
    request = client.get('/api/indicators?tags=phish')
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 1
    assert response['items'][0]['value'] == '1.1.1.1'

    # Filter by type
    request = client.get('/api/indicators?type=IP')
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 1
    assert response['items'][0]['value'] == '1.1.1.1'

    # Filter by value
    request = client.get('/api/indicators?value=1.1')
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 1
    assert response['items'][0]['value'] == '1.1.1.1'

    # Filter by intel source
    request = client.get('/api/indicators?sources=OSINT')
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 1
    assert response['items'][0]['value'] == '1.1.1.1'

    # Filter by multiple
    request = client.get('/api/indicators?tags=phish&type=IP')
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 1
    assert response['items'][0]['value'] == '1.1.1.1'

    # Filter by multiple (conflicting)
    request = client.get('/api/indicators?tags=phish&type=Email')
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 0


"""
UPDATE TESTS
"""


def test_update_nonexistent_username(client):
    """ Ensure an indicator cannot be updated with a nonexistent username """

    request, response = create_indicator(client, 'asdf', 'asdf', 'analyst')
    _id = response['id']
    assert request.status_code == 201

    data = {'username': 'this_user_does_not_exist'}
    request = client.put('/api/indicators/{}'.format(_id), data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert 'User username not found:' in response['msg']


def test_update_inactive_username(client):
    """ Ensure an indicator cannot be updated with an inactive username """

    request, response = create_indicator(client, 'asdf', 'asdf', 'analyst')
    _id = response['id']
    assert request.status_code == 201

    data = {'username': 'inactive'}
    request = client.put('/api/indicators/{}'.format(_id), data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Cannot update an indicator with an inactive user'


def test_update_nonexistent_id(client):
    """ Ensure a nonexistent ID does not work """

    data = {'username': 'analyst'}
    request = client.put('/api/indicators/100000', data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['msg'] == 'Indicator ID not found'


def test_update_missing_parameter(client):
    """ Ensure the required parameters are given """

    request, response = create_indicator(client, 'asdf', 'asdf', 'analyst')
    _id = response['id']
    assert request.status_code == 201

    request = client.put('/api/indicators/{}'.format(_id))
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'Request must include at least one of:' in response['msg']


def test_update_missing_token(app, client):
    """ Ensure a token is given if the config requires it """

    app.config['PUT'] = 'analyst'

    request = client.put('/api/indicators/1')
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Missing Authorization Header'


def test_update_invalid_role(app, client):
    """ Ensure the given token has the proper role access """

    app.config['PUT'] = 'user_does_not_have_this_role'

    access_token, refresh_token = obtain_token(client, 'analyst', 'analyst')
    headers = create_auth_header(access_token)
    request = client.put('/api/indicators/1', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'user_does_not_have_this_role role required'


def test_update(client):
    """ Ensure a proper request actually works """

    indicator_request, indicator_response = create_indicator(client, 'asdf', 'asdf', 'analyst')
    _id = indicator_response['id']
    assert indicator_request.status_code == 201
    assert indicator_response['user'] == 'analyst'

    # campaigns string
    create_campaign(client, 'Derpsters')
    data = {'campaigns': 'Derpsters'}
    request = client.put('/api/indicators/{}'.format(_id), data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert response['campaigns'][0]['name'] == 'Derpsters'

    # campaigns list
    create_campaign(client, 'LOLcats')
    create_campaign(client, 'Beans')
    data = {'campaigns': ['LOLcats', 'Beans']}
    request = client.put('/api/indicators/{}'.format(_id), data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert len(response['campaigns']) == 2
    assert sorted([response['campaigns'][0]['name'], response['campaigns'][1]['name']]) == ['Beans', 'LOLcats']

    # case_sensitive
    data = {'case_sensitive': not indicator_response['case_sensitive']}
    request = client.put('/api/indicators/{}'.format(_id), data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert response['case_sensitive'] == data['case_sensitive']

    # confidence
    create_indicator_confidence(client, 'HIGH')
    data = {'confidence': 'HIGH'}
    request = client.put('/api/indicators/{}'.format(_id), data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert response['confidence'] == 'HIGH'

    # impact
    create_indicator_impact(client, 'HIGH')
    data = {'impact': 'HIGH'}
    request = client.put('/api/indicators/{}'.format(_id), data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert response['impact'] == 'HIGH'

    # references string
    create_intel_reference(client, 'analyst', 'OSINT', 'http://blahblah.com')
    data = {'references': 'http://blahblah.com'}
    request = client.put('/api/indicators/{}'.format(_id), data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert len(response['references']) == 1
    assert response['references'][0]['reference'] == 'http://blahblah.com'

    # references list
    create_intel_reference(client, 'analyst', 'OSINT', 'http://blahblah2.com')
    create_intel_reference(client, 'analyst', 'OSINT', 'http://blahblah3.com')
    data = {'references': ['http://blahblah2.com', 'http://blahblah3.com']}
    request = client.put('/api/indicators/{}'.format(_id), data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert len(response['references']) == 2
    assert sorted([response['references'][0]['reference'], response['references'][1]['reference']]) == [
        'http://blahblah2.com', 'http://blahblah3.com']

    # status
    create_indicator_status(client, 'Analyzed')
    data = {'status': 'Analyzed'}
    request = client.put('/api/indicators/{}'.format(_id), data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert response['status'] == 'Analyzed'

    # substring
    data = {'substring': not indicator_response['substring']}
    request = client.put('/api/indicators/{}'.format(_id), data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert response['substring'] == data['substring']

    # tags string
    create_tag(client, 'phish')
    data = {'tags': 'phish'}
    request = client.put('/api/indicators/{}'.format(_id), data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert len(response['tags']) == 1
    assert response['tags'][0] == 'phish'

    # tags list
    create_tag(client, 'nanocore')
    create_tag(client, 'remcos')
    data = {'tags': ['remcos', 'nanocore']}
    request = client.put('/api/indicators/{}'.format(_id), data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert len(response['tags']) == 2
    assert sorted(response['tags']) == ['nanocore', 'remcos']

    # username
    data = {'username': 'admin'}
    request = client.put('/api/indicators/{}'.format(_id), data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert response['user'] == 'admin'


"""
DELETE TESTS
"""


def test_delete_nonexistent_id(client):
    """ Ensure a nonexistent ID does not work """

    request = client.delete('/api/indicators/100000')
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['msg'] == 'Indicator ID not found'


def test_delete_missing_token(app, client):
    """ Ensure a token is given if the config requires it """

    app.config['DELETE'] = 'admin'

    request = client.delete('/api/indicators/1')
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Missing Authorization Header'


def test_delete_invalid_role(app, client):
    """ Ensure the given token has the proper role access """

    app.config['DELETE'] = 'user_does_not_have_this_role'

    access_token, refresh_token = obtain_token(client, 'analyst', 'analyst')
    headers = create_auth_header(access_token)
    request = client.delete('/api/indicators/1', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'user_does_not_have_this_role role required'


def test_delete(client):
    """ Ensure a proper request actually works """

    request, response = create_indicator(client, 'asdf', 'asdf', 'analyst')
    _id = response['id']
    assert request.status_code == 201

    request = client.delete('/api/indicators/{}'.format(_id))
    assert request.status_code == 204

    request = client.get('/api/indicators/{}'.format(_id))
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['msg'] == 'Indicator ID not found'
