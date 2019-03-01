import datetime
import time

from project.tests.helpers import *


"""
CREATE TESTS
"""


def test_create_schema(client):
    """ Ensure POST requests conform to the required JSON schema """

    # Invalid JSON
    data = {}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert response['msg'] == 'Request must include valid JSON'

    # Missing required name parameter
    data = {'username': 'asdf'}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert response['msg'] == "Request JSON does not match schema: 'name' is a required property"

    # Missing required username parameter
    data = {'name': 'asdf'}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert response['msg'] == "Request JSON does not match schema: 'username' is a required property"

    # Additional parameter
    data = {'name': 'asdf', 'username': 'asdf', 'asdf': 'asdf'}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'Additional properties are not allowed' in response['msg']

    # Invalid name parameter type
    data = {'name': 1, 'username': 'asdf'}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # Invalid username parameter type
    data = {'name': 'asdf', 'username': 1}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # name parameter too short
    data = {'name': '', 'username': 'asdf'}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # name parameter too long
    data = {'name': 'a' * 256, 'username': 'asdf'}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']

    # username parameter too short
    data = {'name': 'asdf', 'username': ''}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # username parameter too long
    data = {'name': 'asdf', 'username': 'a' * 256}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']

    # Invalid alerts parameter type
    data = {'name': 'asdf', 'username': 'asdf', 'alerts': 'asdf'}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "'asdf' is not of type 'array'" in response['msg']

    # Empty alerts parameter type
    data = {'name': 'asdf', 'username': 'asdf', 'alerts': []}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # Invalid alerts parameter type
    data = {'name': 'asdf', 'username': 'asdf', 'alerts': [1]}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'object'" in response['msg']

    # alerts type parameter too short
    data = {'name': 'asdf', 'username': 'asdf', 'alerts': [{'type': '', 'url': 'asdf'}]}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # alerts type parameter too long
    data = {'name': 'asdf', 'username': 'asdf', 'alerts': [{'type': 'a' * 256, 'url': 'asdf'}]}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']

    # alerts url parameter too short
    data = {'name': 'asdf', 'username': 'asdf', 'alerts': [{'type': 'asdf', 'url': ''}]}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # alerts url parameter too long
    data = {'name': 'asdf', 'username': 'asdf', 'alerts': [{'type': 'asdf', 'url': 'a' * 513}]}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']

    # Invalid description parameter type
    data = {'name': 'asdf', 'username': 'asdf', 'description': 1}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # Invalid attack_vectors parameter type
    data = {'name': 'asdf', 'username': 'asdf', 'attack_vectors': 'asdf'}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "'asdf' is not of type 'array'" in response['msg']

    # Invalid attack_vectors parameter type
    data = {'name': 'asdf', 'username': 'asdf', 'attack_vectors': [1]}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # Empty attack_vectors parameter type
    data = {'name': 'asdf', 'username': 'asdf', 'attack_vectors': []}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # attack_vectors parameter too short
    data = {'name': 'asdf', 'username': 'asdf', 'attack_vectors': ['']}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # attack_vectors parameter too long
    data = {'name': 'asdf', 'username': 'asdf', 'attack_vectors': ['a' * 256]}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']

    # Invalid malware parameter type
    data = {'name': 'asdf', 'username': 'asdf', 'malware': 'asdf'}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "'asdf' is not of type 'array'" in response['msg']

    # Empty malware parameter type
    data = {'name': 'asdf', 'username': 'asdf', 'malware': []}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # Invalid malware parameter type
    data = {'name': 'asdf', 'username': 'asdf', 'malware': [1]}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'object'" in response['msg']

    # malware name parameter too short
    data = {'name': 'asdf', 'username': 'asdf', 'malware': [{'name': ''}]}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # malware name parameter too long
    data = {'name': 'asdf', 'username': 'asdf', 'malware': [{'name': 'a' * 256}]}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']

    # Invalid malware types parameter type
    data = {'name': 'asdf', 'username': 'asdf', 'malware': [{'name': 'asdf', 'types': 'asdf'}]}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "'asdf' is not of type 'array'" in response['msg']

    # Empty malware types parameter
    data = {'name': 'asdf', 'username': 'asdf', 'malware': [{'name': 'asdf', 'types': []}]}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # Invalid malware types element parameter type
    data = {'name': 'asdf', 'username': 'asdf', 'malware': [{'name': 'asdf', 'types': [1]}]}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # malware types parameter too short
    data = {'name': 'asdf', 'username': 'asdf', 'malware': [{'name': 'asdf', 'types': ['']}]}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # malware types parameter too long
    data = {'name': 'asdf', 'username': 'asdf', 'malware': [{'name': 'asdf', 'types': ['a' * 256]}]}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']

    # Invalid prevention_tools parameter type
    data = {'name': 'asdf', 'username': 'asdf', 'prevention_tools': 'asdf'}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "'asdf' is not of type 'array'" in response['msg']

    # Empty prevention_tools parameter type
    data = {'name': 'asdf', 'username': 'asdf', 'prevention_tools': []}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # Invalid prevention_tools parameter type
    data = {'name': 'asdf', 'username': 'asdf', 'prevention_tools': [1]}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # prevention_tools parameter too short
    data = {'name': 'asdf', 'username': 'asdf', 'prevention_tools': ['']}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # prevention_tools parameter too long
    data = {'name': 'asdf', 'username': 'asdf', 'prevention_tools': ['a' * 256]}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']

    # Invalid references parameter type
    data = {'name': 'asdf', 'username': 'asdf', 'references': 'asdf'}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "'asdf' is not of type 'array'" in response['msg']

    # Empty references parameter type
    data = {'name': 'asdf', 'username': 'asdf', 'references': []}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # Invalid references parameter type
    data = {'name': 'asdf', 'username': 'asdf', 'references': [1]}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'object'" in response['msg']

    # references parameter too short
    data = {'name': 'asdf', 'username': 'asdf', 'references': [{'reference': '', 'source': 'asdf'}]}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # references parameter too long
    data = {'name': 'asdf', 'username': 'asdf', 'references': [{'reference': 'a' * 513, 'source': 'asdf'}]}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']

    # source parameter too short
    data = {'name': 'asdf', 'username': 'asdf', 'references': [{'reference': 'asdf', 'source': ''}]}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # source parameter too long
    data = {'name': 'asdf', 'username': 'asdf', 'references': [{'reference': 'asdf', 'source': 'a' * 256}]}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']

    # Invalid remediations parameter type
    data = {'name': 'asdf', 'username': 'asdf', 'remediations': 'asdf'}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "'asdf' is not of type 'array'" in response['msg']

    # Empty remediations parameter type
    data = {'name': 'asdf', 'username': 'asdf', 'remediations': []}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # Invalid remediations parameter type
    data = {'name': 'asdf', 'username': 'asdf', 'remediations': [1]}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # remediations parameter too short
    data = {'name': 'asdf', 'username': 'asdf', 'remediations': ['']}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # remediations parameter too long
    data = {'name': 'asdf', 'username': 'asdf', 'remediations': ['a' * 256]}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']

    # Invalid tags parameter type
    data = {'name': 'asdf', 'username': 'asdf', 'tags': 'asdf'}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "'asdf' is not of type 'array'" in response['msg']

    # Empty tags parameter type
    data = {'name': 'asdf', 'username': 'asdf', 'tags': []}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # Invalid tags parameter type
    data = {'name': 'asdf', 'username': 'asdf', 'tags': [1]}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # tags parameter too short
    data = {'name': 'asdf', 'username': 'asdf', 'tags': ['']}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # tags parameter too long
    data = {'name': 'asdf', 'username': 'asdf', 'tags': ['a' * 256]}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']

    # Invalid types parameter type
    data = {'name': 'asdf', 'username': 'asdf', 'types': 'asdf'}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "'asdf' is not of type 'array'" in response['msg']

    # Empty types parameter type
    data = {'name': 'asdf', 'username': 'asdf', 'types': []}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # Invalid types parameter type
    data = {'name': 'asdf', 'username': 'asdf', 'types': [1]}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # types parameter too short
    data = {'name': 'asdf', 'username': 'asdf', 'types': ['']}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # types parameter too long
    data = {'name': 'asdf', 'username': 'asdf', 'types': ['a' * 256]}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']

    # Invalid campaign parameter type
    data = {'name': 'asdf', 'username': 'asdf', 'campaign': 1}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # campaign parameter too short
    data = {'name': 'asdf', 'username': 'asdf', 'campaign': ''}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # campaign parameter too long
    data = {'name': 'asdf', 'username': 'asdf', 'campaign': 'a' * 256}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']

    # Invalid disposition parameter type
    data = {'name': 'asdf', 'username': 'asdf', 'disposition': 1}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # disposition parameter too short
    data = {'name': 'asdf', 'username': 'asdf', 'disposition': ''}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # disposition parameter too long
    data = {'name': 'asdf', 'username': 'asdf', 'disposition': 'a' * 256}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']

    # Invalid status parameter type
    data = {'name': 'asdf', 'username': 'asdf', 'status': 1}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # status parameter too short
    data = {'name': 'asdf', 'username': 'asdf', 'status': ''}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # status parameter too long
    data = {'name': 'asdf', 'username': 'asdf', 'status': 'a' * 256}
    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']


def test_create_duplicate(client):
    """ Ensure a duplicate record cannot be created """

    request, response = create_event(client, 'asdf', 'analyst')
    assert request.status_code == 201

    request, response = create_event(client, 'asdf', 'analyst')
    assert request.status_code == 409
    assert response['msg'] == 'Event name already exists'


def test_create_nonexistent_username(client):
    """ Ensure an event cannot be created with a nonexistent username """

    request, response = create_event(client, 'asdf', 'this_user_does_not_exist')
    assert request.status_code == 404
    assert 'User username not found:' in response['msg']


def test_create_inactive_username(client):
    """ Ensure an event cannot be created with an inactive username """

    request, response = create_event(client, 'asdf', 'inactive')
    assert request.status_code == 401
    assert response['msg'] == 'Cannot create an event with an inactive user'


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
    assert response['msg'] == 'user_does_not_have_this_role role required'


def test_create_autocreate_alert(app, client):
    """ Ensure the auto-create alert config actually works """

    app.config['EVENT_AUTO_CREATE_ALERT'] = False
    app.config['EVENT_AUTO_CREATE_CAMPAIGN'] = True
    app.config['EVENT_AUTO_CREATE_EVENTATTACKVECTOR'] = True
    app.config['EVENT_AUTO_CREATE_EVENTDISPOSITION'] = True
    app.config['EVENT_AUTO_CREATE_EVENTPREVENTIONTOOL'] = True
    app.config['EVENT_AUTO_CREATE_EVENTREMEDIATION'] = True
    app.config['EVENT_AUTO_CREATE_EVENTSTATUS'] = True
    app.config['EVENT_AUTO_CREATE_EVENTTYPE'] = True
    app.config['EVENT_AUTO_CREATE_INTELREFERENCE'] = True
    app.config['EVENT_AUTO_CREATE_MALWARE'] = True
    app.config['EVENT_AUTO_CREATE_TAG'] = True

    data = {'alerts': [{'type': 'ACE', 'url': 'http://ace/alert1'}],
            'attack_vectors': ['WEBMAIL'],
            'campaign': 'Derpsters',
            'disposition': 'DELIVERY',
            'malware': [{'name': 'Nanocore', 'types': ['RAT']}],
            'name': 'test event',
            'prevention_tools': ['IPS'],
            'references': [{'source': 'OSINT', 'reference': 'http://blahblah.com'}],
            'remediations': ['REIMAGED'],
            'status': 'CLOSED',
            'tags': ['phish', 'nanocore'],
            'types': ['phish'],
            'username': 'analyst'}

    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['msg'] == 'Alert not found: http://ace/alert1'

    app.config['EVENT_AUTO_CREATE_ALERT'] = True

    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 201
    assert response['alerts'][0]['url'] == 'http://ace/alert1'


def test_create_autocreate_campaign(app, client):
    """ Ensure the auto-create campaign config actually works """

    app.config['EVENT_AUTO_CREATE_ALERT'] = True
    app.config['EVENT_AUTO_CREATE_CAMPAIGN'] = False
    app.config['EVENT_AUTO_CREATE_EVENTATTACKVECTOR'] = True
    app.config['EVENT_AUTO_CREATE_EVENTDISPOSITION'] = True
    app.config['EVENT_AUTO_CREATE_EVENTPREVENTIONTOOL'] = True
    app.config['EVENT_AUTO_CREATE_EVENTREMEDIATION'] = True
    app.config['EVENT_AUTO_CREATE_EVENTSTATUS'] = True
    app.config['EVENT_AUTO_CREATE_EVENTTYPE'] = True
    app.config['EVENT_AUTO_CREATE_INTELREFERENCE'] = True
    app.config['EVENT_AUTO_CREATE_MALWARE'] = True
    app.config['EVENT_AUTO_CREATE_TAG'] = True

    data = {'alerts': [{'type': 'ACE', 'url': 'http://ace/alert1'}],
            'attack_vectors': ['WEBMAIL'],
            'campaign': 'Derpsters',
            'disposition': 'DELIVERY',
            'malware': [{'name': 'Nanocore', 'types': ['RAT']}],
            'name': 'test event',
            'prevention_tools': ['IPS'],
            'references': [{'source': 'OSINT', 'reference': 'http://blahblah.com'}],
            'remediations': ['REIMAGED'],
            'status': 'CLOSED',
            'tags': ['phish', 'nanocore'],
            'types': ['phish'],
            'username': 'analyst'}

    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['msg'] == 'Campaign not found: Derpsters'

    app.config['EVENT_AUTO_CREATE_CAMPAIGN'] = True

    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 201
    assert response['campaign']['name'] == 'Derpsters'


def test_create_autocreate_event_attack_vector(app, client):
    """ Ensure the auto-create event attack vector config actually works """

    app.config['EVENT_AUTO_CREATE_ALERT'] = True
    app.config['EVENT_AUTO_CREATE_CAMPAIGN'] = True
    app.config['EVENT_AUTO_CREATE_EVENTATTACKVECTOR'] = False
    app.config['EVENT_AUTO_CREATE_EVENTDISPOSITION'] = True
    app.config['EVENT_AUTO_CREATE_EVENTPREVENTIONTOOL'] = True
    app.config['EVENT_AUTO_CREATE_EVENTREMEDIATION'] = True
    app.config['EVENT_AUTO_CREATE_EVENTSTATUS'] = True
    app.config['EVENT_AUTO_CREATE_EVENTTYPE'] = True
    app.config['EVENT_AUTO_CREATE_INTELREFERENCE'] = True
    app.config['EVENT_AUTO_CREATE_MALWARE'] = True
    app.config['EVENT_AUTO_CREATE_TAG'] = True

    data = {'alerts': [{'type': 'ACE', 'url': 'http://ace/alert1'}],
            'attack_vectors': ['WEBMAIL'],
            'campaign': 'Derpsters',
            'disposition': 'DELIVERY',
            'malware': [{'name': 'Nanocore', 'types': ['RAT']}],
            'name': 'test event',
            'prevention_tools': ['IPS'],
            'references': [{'source': 'OSINT', 'reference': 'http://blahblah.com'}],
            'remediations': ['REIMAGED'],
            'status': 'CLOSED',
            'tags': ['phish', 'nanocore'],
            'types': ['phish'],
            'username': 'analyst'}

    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['msg'] == 'Event attack vector not found: WEBMAIL'

    app.config['EVENT_AUTO_CREATE_EVENTATTACKVECTOR'] = True

    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 201
    assert response['attack_vectors'] == ['WEBMAIL']


def test_create_autocreate_event_disposition(app, client):
    """ Ensure the auto-create event disposition config actually works """

    app.config['EVENT_AUTO_CREATE_ALERT'] = True
    app.config['EVENT_AUTO_CREATE_CAMPAIGN'] = True
    app.config['EVENT_AUTO_CREATE_EVENTATTACKVECTOR'] = True
    app.config['EVENT_AUTO_CREATE_EVENTDISPOSITION'] = False
    app.config['EVENT_AUTO_CREATE_EVENTPREVENTIONTOOL'] = True
    app.config['EVENT_AUTO_CREATE_EVENTREMEDIATION'] = True
    app.config['EVENT_AUTO_CREATE_EVENTSTATUS'] = True
    app.config['EVENT_AUTO_CREATE_EVENTTYPE'] = True
    app.config['EVENT_AUTO_CREATE_INTELREFERENCE'] = True
    app.config['EVENT_AUTO_CREATE_MALWARE'] = True
    app.config['EVENT_AUTO_CREATE_TAG'] = True

    data = {'alerts': [{'type': 'ACE', 'url': 'http://ace/alert1'}],
            'attack_vectors': ['WEBMAIL'],
            'campaign': 'Derpsters',
            'disposition': 'DELIVERY',
            'malware': [{'name': 'Nanocore', 'types': ['RAT']}],
            'name': 'test event',
            'prevention_tools': ['IPS'],
            'references': [{'source': 'OSINT', 'reference': 'http://blahblah.com'}],
            'remediations': ['REIMAGED'],
            'status': 'CLOSED',
            'tags': ['phish', 'nanocore'],
            'types': ['phish'],
            'username': 'analyst'}

    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['msg'] == 'Event disposition not found: DELIVERY'

    app.config['EVENT_AUTO_CREATE_EVENTDISPOSITION'] = True

    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 201
    assert response['disposition'] == 'DELIVERY'


def test_create_autocreate_event_prevention_tool(app, client):
    """ Ensure the auto-create event prevention tool config actually works """

    app.config['EVENT_AUTO_CREATE_ALERT'] = True
    app.config['EVENT_AUTO_CREATE_CAMPAIGN'] = True
    app.config['EVENT_AUTO_CREATE_EVENTATTACKVECTOR'] = True
    app.config['EVENT_AUTO_CREATE_EVENTDISPOSITION'] = True
    app.config['EVENT_AUTO_CREATE_EVENTPREVENTIONTOOL'] = False
    app.config['EVENT_AUTO_CREATE_EVENTREMEDIATION'] = True
    app.config['EVENT_AUTO_CREATE_EVENTSTATUS'] = True
    app.config['EVENT_AUTO_CREATE_EVENTTYPE'] = True
    app.config['EVENT_AUTO_CREATE_INTELREFERENCE'] = True
    app.config['EVENT_AUTO_CREATE_MALWARE'] = True
    app.config['EVENT_AUTO_CREATE_TAG'] = True

    data = {'alerts': [{'type': 'ACE', 'url': 'http://ace/alert1'}],
            'attack_vectors': ['WEBMAIL'],
            'campaign': 'Derpsters',
            'disposition': 'DELIVERY',
            'malware': [{'name': 'Nanocore', 'types': ['RAT']}],
            'name': 'test event',
            'prevention_tools': ['IPS'],
            'references': [{'source': 'OSINT', 'reference': 'http://blahblah.com'}],
            'remediations': ['REIMAGED'],
            'status': 'CLOSED',
            'tags': ['phish', 'nanocore'],
            'types': ['phish'],
            'username': 'analyst'}

    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['msg'] == 'Event prevention tool not found: IPS'

    app.config['EVENT_AUTO_CREATE_EVENTPREVENTIONTOOL'] = True

    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 201
    assert response['prevention_tools'] == ['IPS']


def test_create_autocreate_event_remediation(app, client):
    """ Ensure the auto-create event remediation config actually works """

    app.config['EVENT_AUTO_CREATE_ALERT'] = True
    app.config['EVENT_AUTO_CREATE_CAMPAIGN'] = True
    app.config['EVENT_AUTO_CREATE_EVENTATTACKVECTOR'] = True
    app.config['EVENT_AUTO_CREATE_EVENTDISPOSITION'] = True
    app.config['EVENT_AUTO_CREATE_EVENTPREVENTIONTOOL'] = True
    app.config['EVENT_AUTO_CREATE_EVENTREMEDIATION'] = False
    app.config['EVENT_AUTO_CREATE_EVENTSTATUS'] = True
    app.config['EVENT_AUTO_CREATE_EVENTTYPE'] = True
    app.config['EVENT_AUTO_CREATE_INTELREFERENCE'] = True
    app.config['EVENT_AUTO_CREATE_MALWARE'] = True
    app.config['EVENT_AUTO_CREATE_TAG'] = True

    data = {'alerts': [{'type': 'ACE', 'url': 'http://ace/alert1'}],
            'attack_vectors': ['WEBMAIL'],
            'campaign': 'Derpsters',
            'disposition': 'DELIVERY',
            'malware': [{'name': 'Nanocore', 'types': ['RAT']}],
            'name': 'test event',
            'prevention_tools': ['IPS'],
            'references': [{'source': 'OSINT', 'reference': 'http://blahblah.com'}],
            'remediations': ['REIMAGED'],
            'status': 'CLOSED',
            'tags': ['phish', 'nanocore'],
            'types': ['phish'],
            'username': 'analyst'}

    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['msg'] == 'Event remediation not found: REIMAGED'

    app.config['EVENT_AUTO_CREATE_EVENTREMEDIATION'] = True

    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 201
    assert response['remediations'] == ['REIMAGED']


def test_create_autocreate_event_status(app, client):
    """ Ensure the auto-create event status config actually works """

    app.config['EVENT_AUTO_CREATE_ALERT'] = True
    app.config['EVENT_AUTO_CREATE_CAMPAIGN'] = True
    app.config['EVENT_AUTO_CREATE_EVENTATTACKVECTOR'] = True
    app.config['EVENT_AUTO_CREATE_EVENTDISPOSITION'] = True
    app.config['EVENT_AUTO_CREATE_EVENTPREVENTIONTOOL'] = True
    app.config['EVENT_AUTO_CREATE_EVENTREMEDIATION'] = True
    app.config['EVENT_AUTO_CREATE_EVENTSTATUS'] = False
    app.config['EVENT_AUTO_CREATE_EVENTTYPE'] = True
    app.config['EVENT_AUTO_CREATE_INTELREFERENCE'] = True
    app.config['EVENT_AUTO_CREATE_MALWARE'] = True
    app.config['EVENT_AUTO_CREATE_TAG'] = True

    data = {'alerts': [{'type': 'ACE', 'url': 'http://ace/alert1'}],
            'attack_vectors': ['WEBMAIL'],
            'campaign': 'Derpsters',
            'disposition': 'DELIVERY',
            'malware': [{'name': 'Nanocore', 'types': ['RAT']}],
            'name': 'test event',
            'prevention_tools': ['IPS'],
            'references': [{'source': 'OSINT', 'reference': 'http://blahblah.com'}],
            'remediations': ['REIMAGED'],
            'status': 'CLOSED',
            'tags': ['phish', 'nanocore'],
            'types': ['phish'],
            'username': 'analyst'}

    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['msg'] == 'Event status not found: CLOSED'

    app.config['EVENT_AUTO_CREATE_EVENTSTATUS'] = True

    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 201
    assert response['status'] == 'CLOSED'


def test_create_autocreate_event_type(app, client):
    """ Ensure the auto-create event type config actually works """

    app.config['EVENT_AUTO_CREATE_ALERT'] = True
    app.config['EVENT_AUTO_CREATE_CAMPAIGN'] = True
    app.config['EVENT_AUTO_CREATE_EVENTATTACKVECTOR'] = True
    app.config['EVENT_AUTO_CREATE_EVENTDISPOSITION'] = True
    app.config['EVENT_AUTO_CREATE_EVENTPREVENTIONTOOL'] = True
    app.config['EVENT_AUTO_CREATE_EVENTREMEDIATION'] = True
    app.config['EVENT_AUTO_CREATE_EVENTSTATUS'] = True
    app.config['EVENT_AUTO_CREATE_EVENTTYPE'] = False
    app.config['EVENT_AUTO_CREATE_INTELREFERENCE'] = True
    app.config['EVENT_AUTO_CREATE_MALWARE'] = True
    app.config['EVENT_AUTO_CREATE_TAG'] = True

    data = {'alerts': [{'type': 'ACE', 'url': 'http://ace/alert1'}],
            'attack_vectors': ['WEBMAIL'],
            'campaign': 'Derpsters',
            'disposition': 'DELIVERY',
            'malware': [{'name': 'Nanocore', 'types': ['RAT']}],
            'name': 'test event',
            'prevention_tools': ['IPS'],
            'references': [{'source': 'OSINT', 'reference': 'http://blahblah.com'}],
            'remediations': ['REIMAGED'],
            'status': 'CLOSED',
            'tags': ['phish', 'nanocore'],
            'types': ['phish'],
            'username': 'analyst'}

    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['msg'] == 'Event type not found: phish'

    app.config['EVENT_AUTO_CREATE_EVENTTYPE'] = True

    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 201
    assert response['types'] == ['phish']


def test_create_autocreate_intel_reference(app, client):
    """ Ensure the auto-create intel reference config actually works """

    app.config['EVENT_AUTO_CREATE_ALERT'] = True
    app.config['EVENT_AUTO_CREATE_CAMPAIGN'] = True
    app.config['EVENT_AUTO_CREATE_EVENTATTACKVECTOR'] = True
    app.config['EVENT_AUTO_CREATE_EVENTDISPOSITION'] = True
    app.config['EVENT_AUTO_CREATE_EVENTPREVENTIONTOOL'] = True
    app.config['EVENT_AUTO_CREATE_EVENTREMEDIATION'] = True
    app.config['EVENT_AUTO_CREATE_EVENTSTATUS'] = True
    app.config['EVENT_AUTO_CREATE_EVENTTYPE'] = True
    app.config['EVENT_AUTO_CREATE_INTELREFERENCE'] = False
    app.config['EVENT_AUTO_CREATE_MALWARE'] = True
    app.config['EVENT_AUTO_CREATE_TAG'] = True

    data = {'alerts': [{'type': 'ACE', 'url': 'http://ace/alert1'}],
            'attack_vectors': ['WEBMAIL'],
            'campaign': 'Derpsters',
            'disposition': 'DELIVERY',
            'malware': [{'name': 'Nanocore', 'types': ['RAT']}],
            'name': 'test event',
            'prevention_tools': ['IPS'],
            'references': [{'source': 'OSINT', 'reference': 'http://blahblah.com'}],
            'remediations': ['REIMAGED'],
            'status': 'CLOSED',
            'tags': ['phish', 'nanocore'],
            'types': ['phish'],
            'username': 'analyst'}

    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['msg'] == 'Intel reference not found: http://blahblah.com'

    app.config['EVENT_AUTO_CREATE_INTELREFERENCE'] = True

    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 201
    assert response['references'][0]['reference'] == 'http://blahblah.com'


def test_create_autocreate_malware(app, client):
    """ Ensure the auto-create malware config actually works """

    app.config['EVENT_AUTO_CREATE_ALERT'] = True
    app.config['EVENT_AUTO_CREATE_CAMPAIGN'] = True
    app.config['EVENT_AUTO_CREATE_EVENTATTACKVECTOR'] = True
    app.config['EVENT_AUTO_CREATE_EVENTDISPOSITION'] = True
    app.config['EVENT_AUTO_CREATE_EVENTPREVENTIONTOOL'] = True
    app.config['EVENT_AUTO_CREATE_EVENTREMEDIATION'] = True
    app.config['EVENT_AUTO_CREATE_EVENTSTATUS'] = True
    app.config['EVENT_AUTO_CREATE_EVENTTYPE'] = True
    app.config['EVENT_AUTO_CREATE_INTELREFERENCE'] = True
    app.config['EVENT_AUTO_CREATE_MALWARE'] = False
    app.config['EVENT_AUTO_CREATE_TAG'] = True

    data = {'alerts': [{'type': 'ACE', 'url': 'http://ace/alert1'}],
            'attack_vectors': ['WEBMAIL'],
            'campaign': 'Derpsters',
            'disposition': 'DELIVERY',
            'malware': [{'name': 'Nanocore', 'types': ['RAT']}],
            'name': 'test event',
            'prevention_tools': ['IPS'],
            'references': [{'source': 'OSINT', 'reference': 'http://blahblah.com'}],
            'remediations': ['REIMAGED'],
            'status': 'CLOSED',
            'tags': ['phish', 'nanocore'],
            'types': ['phish'],
            'username': 'analyst'}

    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['msg'] == 'Malware not found: Nanocore'

    app.config['EVENT_AUTO_CREATE_MALWARE'] = True

    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 201
    assert response['malware'][0]['name'] == 'Nanocore'
    assert response['malware'][0]['types'] == ['RAT']


def test_create_autocreate_tag(app, client):
    """ Ensure the auto-create tag config actually works """

    app.config['EVENT_AUTO_CREATE_ALERT'] = True
    app.config['EVENT_AUTO_CREATE_CAMPAIGN'] = True
    app.config['EVENT_AUTO_CREATE_EVENTATTACKVECTOR'] = True
    app.config['EVENT_AUTO_CREATE_EVENTDISPOSITION'] = True
    app.config['EVENT_AUTO_CREATE_EVENTPREVENTIONTOOL'] = True
    app.config['EVENT_AUTO_CREATE_EVENTREMEDIATION'] = True
    app.config['EVENT_AUTO_CREATE_EVENTSTATUS'] = True
    app.config['EVENT_AUTO_CREATE_EVENTTYPE'] = True
    app.config['EVENT_AUTO_CREATE_INTELREFERENCE'] = True
    app.config['EVENT_AUTO_CREATE_MALWARE'] = True
    app.config['EVENT_AUTO_CREATE_TAG'] = False

    data = {'alerts': [{'type': 'ACE', 'url': 'http://ace/alert1'}],
            'attack_vectors': ['WEBMAIL'],
            'campaign': 'Derpsters',
            'disposition': 'DELIVERY',
            'malware': [{'name': 'Nanocore', 'types': ['RAT']}],
            'name': 'test event',
            'prevention_tools': ['IPS'],
            'references': [{'source': 'OSINT', 'reference': 'http://blahblah.com'}],
            'remediations': ['REIMAGED'],
            'status': 'CLOSED',
            'tags': ['phish', 'nanocore'],
            'types': ['phish'],
            'username': 'analyst'}

    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['msg'] == 'Tag not found: phish'

    app.config['EVENT_AUTO_CREATE_TAG'] = True

    request = client.get('/api/events')
    response = json.loads(request.data.decode())
    print(response)

    request = client.post('/api/events', json=data)
    response = json.loads(request.data.decode())
    print(response)
    assert request.status_code == 201
    assert response['tags'] == ['nanocore', 'phish']


def test_create(client):
    """ Ensure a proper request actually works """

    request, response = create_event(client, 'asdf', 'analyst',
                                     attack_vectors=['WEBMAIL'],
                                     campaign='Derpsters',
                                     disposition='DELIVERY',
                                     malware=[{'name': 'Nanocore', 'types': ['RAT']},
                                              {'name': 'Remcos', 'types': ['RAT']}],
                                     prevention_tools=['IPS'],
                                     remediations=['REIMAGED'],
                                     status='CLOSED',
                                     tags=['phish', 'nanocore'],
                                     types=['recon', 'phish'],
                                     intel_reference='http://blahblah.com',
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
    assert response['msg'] == 'Event ID not found'


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
    assert response['msg'] == 'user_does_not_have_this_role role required'


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
                                                   alerts=[{'type': 'ACE', 'url': 'http://ace/alert1'}],
                                                   attack_vectors=['CORPORATE EMAIL'],
                                                   description='Phish with link to download Nanocore',
                                                   disposition='EXPLOITATION',
                                                   prevention_tools=['ANTIVIRUS'],
                                                   remediations=['REMOVED FROM INBOX'],
                                                   status='OPEN',
                                                   types=['PHISH'],
                                                   campaign='Derpsters',
                                                   malware=[{'name': 'Nanocore', 'types': ['RAT']}],
                                                   tags=['phish'],
                                                   intel_reference='https://wiki.local/20190125 Nanocore phish',
                                                   intel_source='OSINT')
    assert event1_request.status_code == 201

    time.sleep(1)

    event2_request, event2_response = create_event(client, '20190125 Remcos infection', 'admin',
                                                   alerts=[{'type': 'SIEM', 'url': 'http://siem/alert2'}],
                                                   attack_vectors=['USB'],
                                                   description='USB drive infected with Remcos',
                                                   disposition='DELIVERY',
                                                   prevention_tools=['PROXY'],
                                                   remediations=['REIMAGED'],
                                                   status='CLOSED',
                                                   types=['HOST COMPROMISE'],
                                                   campaign='LOLcats',
                                                   malware=[{'name': 'Remcos', 'types': ['RAT']}],
                                                   tags=['remcos'],
                                                   intel_reference='https://wiki.local/20190125 Remcos infection',
                                                   intel_source='VirusTotal')
    assert event2_request.status_code == 201

    time.sleep(1)

    # Filter by alert_types
    request = client.get('/api/events?alert_types=ACE')
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 1
    assert response['items'][0]['alerts'][0]['type'] == 'ACE'

    # Filter by alert_url
    request = client.get('/api/events?alert_url=siem')
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 1
    assert response['items'][0]['alerts'][0]['type'] == 'SIEM'

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

    # Filter by user
    request = client.get('/api/events?user=analyst')
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 1
    assert response['items'][0]['user'] == 'analyst'

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


def test_update_schema(client):
    """ Ensure POST requests conform to the required JSON schema """

    # Invalid JSON
    data = {}
    request = client.put('/api/events/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert response['msg'] == 'Request must include valid JSON'

    # Additional parameter
    data = {'asdf': 'asdf'}
    request = client.put('/api/events/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'Additional properties are not allowed' in response['msg']

    # Invalid username parameter type
    data = {'username': 1}
    request = client.put('/api/events/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # username parameter too short
    data = {'username': ''}
    request = client.put('/api/events/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400

    # username parameter too long
    data = {'username': 'a' * 256}
    request = client.put('/api/events/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']

    # Invalid alerts parameter type
    data = {'alerts': 'asdf'}
    request = client.put('/api/events/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "'asdf' is not of type 'array'" in response['msg']

    # Empty alerts parameter type
    data = {'alerts': []}
    request = client.put('/api/events/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # Invalid alerts parameter type
    data = {'alerts': [1]}
    request = client.put('/api/events/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # alerts parameter too short
    data = {'alerts': ['']}
    request = client.put('/api/events/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # alerts parameter too long
    data = {'alerts': ['a' * 513]}
    request = client.put('/api/events/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']

    # Invalid description parameter type
    data = {'description': 1}
    request = client.put('/api/events/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # Invalid attack_vectors parameter type
    data = {'attack_vectors': 'asdf'}
    request = client.put('/api/events/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "'asdf' is not of type 'array'" in response['msg']

    # Empty attack_vectors parameter type
    data = {'attack_vectors': []}
    request = client.put('/api/events/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # Invalid attack_vectors parameter type
    data = {'attack_vectors': [1]}
    request = client.put('/api/events/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # attack_vectors parameter too short
    data = {'attack_vectors': ['']}
    request = client.put('/api/events/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # attack_vectors parameter too long
    data = {'attack_vectors': ['a' * 256]}
    request = client.put('/api/events/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']

    # Invalid malware parameter type
    data = {'malware': 'asdf'}
    request = client.put('/api/events/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "'asdf' is not of type 'array'" in response['msg']

    # Empty malware parameter type
    data = {'malware': []}
    request = client.put('/api/events/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # Invalid malware parameter type
    data = {'malware': [1]}
    request = client.put('/api/events/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # malware parameter too short
    data = {'malware': ['']}
    request = client.put('/api/events/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # malware parameter too long
    data = {'malware': ['a' * 256]}
    request = client.put('/api/events/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']

    # Invalid prevention_tools parameter type
    data = {'prevention_tools': 'asdf'}
    request = client.put('/api/events/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "'asdf' is not of type 'array'" in response['msg']

    # Empty prevention_tools parameter type
    data = {'prevention_tools': []}
    request = client.put('/api/events/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # Invalid prevention_tools parameter type
    data = {'prevention_tools': [1]}
    request = client.put('/api/events/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # prevention_tools parameter too short
    data = {'prevention_tools': ['']}
    request = client.put('/api/events/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # prevention_tools parameter too long
    data = {'prevention_tools': ['a' * 256]}
    request = client.put('/api/events/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']

    # Invalid references parameter type
    data = {'references': 'asdf'}
    request = client.put('/api/events/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "'asdf' is not of type 'array'" in response['msg']

    # Empty references parameter type
    data = {'references': []}
    request = client.put('/api/events/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # Invalid references parameter type
    data = {'references': [1]}
    request = client.put('/api/events/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # references parameter too short
    data = {'references': ['']}
    request = client.put('/api/events/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # references parameter too long
    data = {'references': ['a' * 513]}
    request = client.put('/api/events/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']

    # Invalid remediations parameter type
    data = {'remediations': 'asdf'}
    request = client.put('/api/events/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "'asdf' is not of type 'array'" in response['msg']

    # Empty remediations parameter type
    data = {'remediations': []}
    request = client.put('/api/events/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # Invalid remediations parameter type
    data = {'remediations': [1]}
    request = client.put('/api/events/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # remediations parameter too short
    data = {'remediations': ['']}
    request = client.put('/api/events/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # remediations parameter too long
    data = {'remediations': ['a' * 256]}
    request = client.put('/api/events/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']

    # Invalid tags parameter type
    data = {'tags': 'asdf'}
    request = client.put('/api/events/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "'asdf' is not of type 'array'" in response['msg']

    # Empty tags parameter type
    data = {'tags': []}
    request = client.put('/api/events/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # Invalid tags parameter type
    data = {'tags': [1]}
    request = client.put('/api/events/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # tags parameter too short
    data = {'tags': ['']}
    request = client.put('/api/events/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # tags parameter too long
    data = {'tags': ['a' * 256]}
    request = client.put('/api/events/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']

    # Invalid types parameter type
    data = {'types': 'asdf'}
    request = client.put('/api/events/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "'asdf' is not of type 'array'" in response['msg']

    # Empty types parameter type
    data = {'types': []}
    request = client.put('/api/events/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # Invalid types parameter type
    data = {'types': [1]}
    request = client.put('/api/events/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # types parameter too short
    data = {'types': ['']}
    request = client.put('/api/events/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # types parameter too long
    data = {'types': ['a' * 256]}
    request = client.put('/api/events/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']

    # Invalid campaign parameter type
    data = {'campaign': 1}
    request = client.put('/api/events/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # campaign parameter too short
    data = {'campaign': ''}
    request = client.put('/api/events/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # campaign parameter too long
    data = {'campaign': 'a' * 256}
    request = client.put('/api/events/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']

    # Invalid disposition parameter type
    data = {'disposition': 1}
    request = client.put('/api/events/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # disposition parameter too short
    data = {'disposition': ''}
    request = client.put('/api/events/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # disposition parameter too long
    data = {'disposition': 'a' * 256}
    request = client.put('/api/events/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']

    # Invalid status parameter type
    data = {'status': 1}
    request = client.put('/api/events/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # status parameter too short
    data = {'status': ''}
    request = client.put('/api/events/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # status parameter too long
    data = {'status': 'a' * 256}
    request = client.put('/api/events/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']


def test_update_nonexistent_username(client):
    """ Ensure an event cannot be updated with a nonexistent username """

    request, response = create_event(client, 'asdf', 'analyst')
    _id = response['id']
    assert request.status_code == 201

    data = {'username': 'this_user_does_not_exist'}
    request = client.put('/api/events/{}'.format(_id), json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert 'Username not found:' in response['msg']


def test_update_inactive_username(client):
    """ Ensure an event cannot be updated with an inactive username """

    request, response = create_event(client, 'asdf', 'analyst')
    _id = response['id']
    assert request.status_code == 201

    data = {'username': 'inactive'}
    request = client.put('/api/events/{}'.format(_id), json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Cannot update an event with an inactive user'


def test_update_nonexistent_id(client):
    """ Ensure a nonexistent ID does not work """

    data = {'username': 'analyst'}
    request = client.put('/api/events/100000', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['msg'] == 'Event ID not found'


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
    assert response['msg'] == 'user_does_not_have_this_role role required'


def test_update(client):
    """ Ensure a proper request actually works """

    event_request, event_response = create_event(client, 'asdf', 'analyst')
    _id = event_response['id']
    assert event_request.status_code == 201
    assert event_response['user'] == 'analyst'

    # alerts
    create_alert(client, 'asdf', 'ACE', 'http://ace/alert1')
    data = {'alerts': ['http://ace/alert1']}
    request = client.put('/api/events/{}'.format(_id), json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert response['alerts'][0]['url'] == 'http://ace/alert1'

    # attack_vectors
    create_event_attack_vector(client, 'CORPORATE EMAIL')
    create_event_attack_vector(client, 'WEBMAIL')
    data = {'attack_vectors': ['CORPORATE EMAIL', 'WEBMAIL']}
    request = client.put('/api/events/{}'.format(_id), json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert response['attack_vectors'] == ['CORPORATE EMAIL', 'WEBMAIL']

    # campaign
    create_campaign(client, 'Derpsters')
    data = {'campaign': 'Derpsters'}
    request = client.put('/api/events/{}'.format(_id), json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert response['campaign']['name'] == 'Derpsters'

    # description
    data = {'description': 'This event did some stuff'}
    request = client.put('/api/events/{}'.format(_id), json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert response['description'] == 'This event did some stuff'

    # disposition
    create_event_disposition(client, 'DELIVERY')
    data = {'disposition': 'DELIVERY'}
    request = client.put('/api/events/{}'.format(_id), json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert response['disposition'] == 'DELIVERY'

    # malware
    create_malware(client, 'Remcos')
    create_malware(client, 'Emotet')
    data = {'malware': ['Remcos', 'Emotet']}
    request = client.put('/api/events/{}'.format(_id), json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert len(response['malware']) == 2
    assert sorted([response['malware'][0]['name'], response['malware'][1]['name']]) == ['Emotet', 'Remcos']

    # prevention_tools
    create_event_prevention_tool(client, 'PROXY')
    create_event_prevention_tool(client, 'IPS')
    data = {'prevention_tools': ['PROXY', 'IPS']}
    request = client.put('/api/events/{}'.format(_id), json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert len(response['malware']) == 2
    assert sorted(response['prevention_tools']) == ['IPS', 'PROXY']

    # references
    create_intel_reference(client, 'analyst', 'OSINT', 'http://blahblah2.com')
    create_intel_reference(client, 'analyst', 'OSINT', 'http://blahblah3.com')
    data = {'references': ['http://blahblah2.com', 'http://blahblah3.com']}
    request = client.put('/api/events/{}'.format(_id), json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert len(response['references']) == 2
    assert sorted([response['references'][0]['reference'], response['references'][1]['reference']]) == [
        'http://blahblah2.com', 'http://blahblah3.com']

    # status
    create_event_status(client, 'asdf')
    data = {'status': 'asdf'}
    request = client.put('/api/events/{}'.format(_id), json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert response['status'] == 'asdf'

    # tags
    create_tag(client, 'nanocore')
    create_tag(client, 'remcos')
    data = {'tags': ['remcos', 'nanocore']}
    request = client.put('/api/events/{}'.format(_id), json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert len(response['tags']) == 2
    assert sorted(response['tags']) == ['nanocore', 'remcos']

    # types
    create_event_type(client, 'host compromise')
    create_event_type(client, 'credential compromise')
    data = {'types': ['host compromise', 'credential compromise']}
    request = client.put('/api/events/{}'.format(_id), json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert len(response['types']) == 2
    assert sorted(response['types']) == ['credential compromise', 'host compromise']

    # username
    data = {'username': 'admin'}
    request = client.put('/api/events/{}'.format(_id), json=data)
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
    assert response['msg'] == 'Event ID not found'


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
    assert response['msg'] == 'user_does_not_have_this_role role required'


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
    assert response['msg'] == 'Event ID not found'
