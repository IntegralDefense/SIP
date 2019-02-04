import datetime
import time

from project.tests.helpers import *


"""
CREATE TESTS
"""


def test_create_missing_parameter(client):
    """ Ensure the required parameters are given """

    # Missing name
    data = {'username': 'analyst'}
    request = client.post('/api/events', data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert response['message'] == 'Request must include: name, username'

    # Missing username
    data = {'name': 'some event name'}
    request = client.post('/api/events', data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert response['message'] == 'Request must include: name, username'


def test_create_duplicate(client):
    """ Ensure a duplicate record cannot be created """

    request, response = create_event(client, 'asdf', 'analyst')
    assert request.status_code == 201

    request, response = create_event(client, 'asdf', 'analyst')
    assert request.status_code == 409
    assert response['message'] == 'Event name already exists'


def test_create_nonexistent_username(client):
    """ Ensure an event cannot be created with a nonexistent username """

    request, response = create_event(client, 'asdf', 'this_user_does_not_exist')
    assert request.status_code == 404
    assert 'User username not found:' in response['message']


def test_create_inactive_username(client):
    """ Ensure an event cannot be created with an inactive username """

    request, response = create_event(client, 'asdf', 'inactive')
    assert request.status_code == 401
    assert response['message'] == 'Cannot create an event with an inactive user'


def test_create_missing_token(app, client):
    """ Ensure a token is given if the config requires it """

    app.config['POST'] = 'analyst'

    request = client.post('/api/events')
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Missing Authorization Header'


def test_create_invalid_role(app, client):
    """ Ensure the given token has the proper role access """

    app.config['POST'] = 'user_does_not_have_this_role'

    access_token, refresh_token = obtain_token(client, 'analyst', 'analyst')
    headers = create_auth_header(access_token)
    request = client.post('/api/events', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['message'] == 'user_does_not_have_this_role role required'


def test_create(client):
    """ Ensure a proper request actually works """

    request, response = create_event(client, 'asdf', 'analyst', attack_vector='WEBMAIL', campaign='Derpsters',
                                     disposition='DELIVERY', malware='Remcos,Nanocore',
                                     prevention_tool='IPS', remediation='REIMAGED', status='CLOSED',
                                     tags='phish,nanocore', types='recon,phish', intel_reference='http://blahblah.com',
                                     intel_source='OSINT')
    assert request.status_code == 201
    assert response['name'] == 'asdf'
    assert response['user'] == 'analyst'
    assert response['attack_vectors'] == ['WEBMAIL']
    assert response['campaign']['name'] == 'Derpsters'
    assert response['disposition'] == 'DELIVERY'
    assert sorted([response['malware'][0]['name'], response['malware'][1]['name']]) == ['Nanocore', 'Remcos']
    assert response['prevention_tools'] == ['IPS']
    assert response['references'][0]['reference'] == 'http://blahblah.com'
    assert response['remediations'] == ['REIMAGED']
    assert response['status'] == 'CLOSED'
    assert sorted(response['tags']) == ['nanocore', 'phish']
    assert sorted(response['types']) == ['phish', 'recon']


"""
READ TESTS
"""


def test_read_nonexistent_id(client):
    """ Ensure a nonexistent ID does not work """

    request = client.get('/api/events/100000')
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['message'] == 'Event ID not found'


def test_read_missing_token(app, client):
    """ Ensure a token is given if the config requires it """

    app.config['GET'] = 'analyst'

    request = client.get('/api/events/1')
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Missing Authorization Header'


def test_read_invalid_role(app, client):
    """ Ensure the given token has the proper role access """

    app.config['GET'] = 'user_does_not_have_this_role'

    access_token, refresh_token = obtain_token(client, 'analyst', 'analyst')
    headers = create_auth_header(access_token)
    request = client.get('/api/events/1', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['message'] == 'user_does_not_have_this_role role required'


def test_read_all_values(client):
    """ Ensure all values properly return """

    request, response = create_event(client, 'asdf', 'analyst')
    assert request.status_code == 201

    request, response = create_event(client, 'asdf2', 'analyst')
    assert request.status_code == 201

    request, response = create_event(client, 'asdf3', 'analyst')
    assert request.status_code == 201

    request = client.get('/api/events')
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 3


def test_read_by_id(client):
    """ Ensure events can be read by their ID """

    request, response = create_event(client, 'asdf', 'analyst')
    _id = response['id']
    assert request.status_code == 201

    request = client.get('/api/events/{}'.format(_id))
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert response['name'] == 'asdf'
    assert response['user'] == 'analyst'


def test_read_with_filters(client):
    """ Ensure events can be read using the various filters """

    event1_request, event1_response = create_event(client, '20190125 Nanocore phish', 'analyst',
                                                   attack_vector='CORPORATE EMAIL',
                                                   disposition='EXPLOITATION',
                                                   prevention_tool='ANTIVIRUS',
                                                   remediation='REMOVED FROM INBOX',
                                                   status='OPEN',
                                                   types='PHISH',
                                                   campaign='Derpsters',
                                                   malware='Nanocore',
                                                   tags='phish',
                                                   intel_reference='https://wiki.local/20190125 Nanocore phish',
                                                   intel_source='OSINT')
    assert event1_request.status_code == 201

    time.sleep(1)

    event2_request, event2_response = create_event(client, '20190125 Remcos infection', 'analyst',
                                                   attack_vector='USB',
                                                   disposition='DELIVERY',
                                                   prevention_tool='PROXY',
                                                   remediation='REIMAGED',
                                                   status='CLOSED',
                                                   types='HOST COMPROMISE',
                                                   campaign='LOLcats',
                                                   malware='Remcos',
                                                   tags='remcos',
                                                   intel_reference='https://wiki.local/20190125 Remcos infection',
                                                   intel_source='VirusTotal')
    assert event2_request.status_code == 201

    time.sleep(1)

    # Filter by attack_vector
    request = client.get('/api/events?attack_vectors=CORPORATE EMAIL')
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 1
    assert response['items'][0]['attack_vectors'] == ['CORPORATE EMAIL']

    # Filter by disposition
    request = client.get('/api/events?disposition=EXPLOITATION')
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 1
    assert response['items'][0]['disposition'] == 'EXPLOITATION'

    # Filter by prevention_tool
    request = client.get('/api/events?prevention_tools=ANTIVIRUS')
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 1
    assert response['items'][0]['prevention_tools'] == ['ANTIVIRUS']

    # Filter by remediation
    request = client.get('/api/events?remediations=REMOVED FROM INBOX')
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 1
    assert response['items'][0]['remediations'] == ['REMOVED FROM INBOX']

    # Filter by status
    request = client.get('/api/events?status=OPEN')
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 1
    assert response['items'][0]['status'] == 'OPEN'

    # Filter by type
    request = client.get('/api/events?types=PHISH')
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 1
    assert response['items'][0]['types'] == ['PHISH']

    # Filter by campaign
    request = client.get('/api/events?campaign=Derpsters')
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 1
    assert response['items'][0]['campaign']['name'] == 'Derpsters'

    # Filter by malware
    request = client.get('/api/events?malware=Nanocore')
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 1
    assert response['items'][0]['malware'][0]['name'] == 'Nanocore'

    # Filter by tag
    request = client.get('/api/events?tags=phish')
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 1
    assert response['items'][0]['tags'] == ['phish']

    # Filter by created_before
    request = client.get('/api/events?created_before={}'.format(datetime.datetime.now()))
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 2
    request = client.get('/api/events?created_before={}'.format(event2_response['created_time']))
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 1
    assert response['items'][0]['name'] == '20190125 Nanocore phish'

    # Filter by created_after
    request = client.get('/api/events?created_after={}'.format(datetime.datetime.min))
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 2
    request = client.get('/api/events?created_after={}'.format(event1_response['created_time']))
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 1
    assert response['items'][0]['name'] == '20190125 Remcos infection'

    # Filter by modified_before
    request = client.get('/api/events?modified_before={}'.format(datetime.datetime.now()))
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 2
    request = client.get('/api/events?modified_before={}'.format(event2_response['modified_time']))
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 1
    assert response['items'][0]['name'] == '20190125 Nanocore phish'

    # Filter by modified_after
    request = client.get('/api/events?modified_after={}'.format(datetime.datetime.min))
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 2
    request = client.get('/api/events?modified_after={}'.format(event1_response['modified_time']))
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 1
    assert response['items'][0]['name'] == '20190125 Remcos infection'

    # Filter by intel source
    request = client.get('/api/events?sources=OSINT')
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 1
    assert response['items'][0]['references'][0]['source'] == 'OSINT'

    # Filter by multiple
    request = client.get('/api/events?tags=phish&disposition=EXPLOITATION')
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 1
    assert response['items'][0]['tags'] == ['phish']
    assert response['items'][0]['disposition'] == 'EXPLOITATION'

    # Filter by multiple (conflicting)
    request = client.get('/api/events?tags=phish&disposition=DELIVERY')
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 0


"""
UPDATE TESTS
"""


def test_update_nonexistent_username(client):
    """ Ensure an event cannot be updated with a nonexistent username """

    request, response = create_event(client, 'asdf', 'analyst')
    _id = response['id']
    assert request.status_code == 201

    data = {'username': 'this_user_does_not_exist'}
    request = client.put('/api/events/{}'.format(_id), data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert 'User username not found:' in response['message']


def test_update_inactive_username(client):
    """ Ensure an event cannot be updated with an inactive username """

    request, response = create_event(client, 'asdf', 'analyst')
    _id = response['id']
    assert request.status_code == 201

    data = {'username': 'inactive'}
    request = client.put('/api/events/{}'.format(_id), data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['message'] == 'Cannot update an event with an inactive user'


def test_update_nonexistent_id(client):
    """ Ensure a nonexistent ID does not work """

    data = {'username': 'analyst'}
    request = client.put('/api/events/100000', data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['message'] == 'Event ID not found'


def test_update_missing_parameter(client):
    """ Ensure the required parameters are given """

    request, response = create_event(client, 'asdf', 'analyst')
    _id = response['id']
    assert request.status_code == 201

    request = client.put('/api/events/{}'.format(_id))
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'Request must include at least one of:' in response['message']


def test_update_missing_token(app, client):
    """ Ensure a token is given if the config requires it """

    app.config['PUT'] = 'analyst'

    request = client.put('/api/events/1')
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Missing Authorization Header'


def test_update_invalid_role(app, client):
    """ Ensure the given token has the proper role access """

    app.config['PUT'] = 'user_does_not_have_this_role'

    access_token, refresh_token = obtain_token(client, 'analyst', 'analyst')
    headers = create_auth_header(access_token)
    request = client.put('/api/events/1', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['message'] == 'user_does_not_have_this_role role required'


def test_update(client):
    """ Ensure a proper request actually works """

    event_request, event_response = create_event(client, 'asdf', 'analyst')
    _id = event_response['id']
    assert event_request.status_code == 201
    assert event_response['user'] == 'analyst'

    # attack_vectors string
    create_event_attack_vector(client, 'USB')
    data = {'attack_vectors': 'USB'}
    request = client.put('/api/events/{}'.format(_id), data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert response['attack_vectors'] == ['USB']

    # attack_vectors list
    create_event_attack_vector(client, 'CORPORATE EMAIL')
    create_event_attack_vector(client, 'WEBMAIL')
    data = {'attack_vectors': ['CORPORATE EMAIL', 'WEBMAIL']}
    request = client.put('/api/events/{}'.format(_id), data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert response['attack_vectors'] == ['CORPORATE EMAIL', 'WEBMAIL']

    # campaign
    create_campaign(client, 'Derpsters')
    data = {'campaign': 'Derpsters'}
    request = client.put('/api/events/{}'.format(_id), data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert response['campaign']['name'] == 'Derpsters'

    # disposition
    create_event_disposition(client, 'DELIVERY')
    data = {'disposition': 'DELIVERY'}
    request = client.put('/api/events/{}'.format(_id), data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert response['disposition'] == 'DELIVERY'

    # malware string
    create_malware(client, 'Nanocore')
    data = {'malware': 'Nanocore'}
    request = client.put('/api/events/{}'.format(_id), data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert len(response['malware']) == 1
    assert response['malware'][0]['name'] == 'Nanocore'

    # malware list
    create_malware(client, 'Remcos')
    create_malware(client, 'Emotet')
    data = {'malware': ['Remcos', 'Emotet']}
    request = client.put('/api/events/{}'.format(_id), data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert len(response['malware']) == 2
    assert sorted([response['malware'][0]['name'], response['malware'][1]['name']]) == ['Emotet', 'Remcos']

    # prevention_tools string
    create_event_prevention_tool(client, 'ANTIVIRUS')
    data = {'prevention_tools': 'ANTIVIRUS'}
    request = client.put('/api/events/{}'.format(_id), data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert len(response['prevention_tools']) == 1
    assert response['prevention_tools'][0] == 'ANTIVIRUS'

    # prevention_tools list
    create_event_prevention_tool(client, 'PROXY')
    create_event_prevention_tool(client, 'IPS')
    data = {'prevention_tools': ['PROXY', 'IPS']}
    request = client.put('/api/events/{}'.format(_id), data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert len(response['malware']) == 2
    assert sorted(response['prevention_tools']) == ['IPS', 'PROXY']

    # references string
    create_intel_reference(client, 'analyst', 'OSINT', 'http://blahblah.com')
    data = {'references': 'http://blahblah.com'}
    request = client.put('/api/events/{}'.format(_id), data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert len(response['references']) == 1
    assert response['references'][0]['reference'] == 'http://blahblah.com'

    # references list
    create_intel_reference(client, 'analyst', 'OSINT', 'http://blahblah2.com')
    create_intel_reference(client, 'analyst', 'OSINT', 'http://blahblah3.com')
    data = {'references': ['http://blahblah2.com', 'http://blahblah3.com']}
    request = client.put('/api/events/{}'.format(_id), data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert len(response['references']) == 2
    assert sorted([response['references'][0]['reference'], response['references'][1]['reference']]) == [
        'http://blahblah2.com', 'http://blahblah3.com']

    # tags string
    create_tag(client, 'phish')
    data = {'tags': 'phish'}
    request = client.put('/api/events/{}'.format(_id), data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert len(response['tags']) == 1
    assert response['tags'][0] == 'phish'

    # tags list
    create_tag(client, 'nanocore')
    create_tag(client, 'remcos')
    data = {'tags': ['remcos', 'nanocore']}
    request = client.put('/api/events/{}'.format(_id), data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert len(response['tags']) == 2
    assert sorted(response['tags']) == ['nanocore', 'remcos']

    # types string
    create_event_type(client, 'phish')
    data = {'types': 'phish'}
    request = client.put('/api/events/{}'.format(_id), data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert len(response['types']) == 1
    assert response['types'][0] == 'phish'

    # types list
    create_event_type(client, 'host compromise')
    create_event_type(client, 'credential compromise')
    data = {'types': ['host compromise', 'credential compromise']}
    request = client.put('/api/events/{}'.format(_id), data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert len(response['types']) == 2
    assert sorted(response['types']) == ['credential compromise', 'host compromise']

    # username
    data = {'username': 'admin'}
    request = client.put('/api/events/{}'.format(_id), data=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert response['user'] == 'admin'


"""
DELETE TESTS
"""


def test_delete_nonexistent_id(client):
    """ Ensure a nonexistent ID does not work """

    request = client.delete('/api/events/100000')
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['message'] == 'Event ID not found'


def test_delete_missing_token(app, client):
    """ Ensure a token is given if the config requires it """

    app.config['DELETE'] = 'admin'

    request = client.delete('/api/events/1')
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Missing Authorization Header'


def test_delete_invalid_role(app, client):
    """ Ensure the given token has the proper role access """

    app.config['DELETE'] = 'user_does_not_have_this_role'

    access_token, refresh_token = obtain_token(client, 'analyst', 'analyst')
    headers = create_auth_header(access_token)
    request = client.delete('/api/events/1', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['message'] == 'user_does_not_have_this_role role required'


def test_delete(client):
    """ Ensure a proper request actually works """

    request, response = create_event(client, 'asdf', 'analyst')
    _id = response['id']
    assert request.status_code == 201

    request = client.delete('/api/events/{}'.format(_id))
    assert request.status_code == 204

    request = client.get('/api/events/{}'.format(_id))
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['message'] == 'Event ID not found'
