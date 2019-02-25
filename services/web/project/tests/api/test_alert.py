from project.tests.helpers import *


"""
CREATE TESTS
"""


def test_create_schema(client):
    """ Ensure POST requests conform to the required JSON schema """

    # Invalid JSON
    data = {}
    request = client.post('/api/alerts', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert response['msg'] == 'Request must include valid JSON'

    # Missing required event parameter
    data = {'type': 'asdf', 'url': 'asdf'}
    request = client.post('/api/alerts', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert response['msg'] == "Request JSON does not match schema: 'event' is a required property"

    # Missing required type parameter
    data = {'event': 'asdf', 'url': 'asdf'}
    request = client.post('/api/alerts', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert response['msg'] == "Request JSON does not match schema: 'type' is a required property"

    # Missing required url parameter
    data = {'type': 'asdf', 'event': 'asdf'}
    request = client.post('/api/alerts', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert response['msg'] == "Request JSON does not match schema: 'url' is a required property"

    # Additional parameter
    data = {'event': 'asdf', 'type': 'asdf', 'url': 'asdf', 'asdf': 'asdf'}
    request = client.post('/api/alerts', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'Additional properties are not allowed' in response['msg']

    # Invalid event parameter type
    data = {'event': 1, 'type': 'asdf', 'url': 'asdf'}
    request = client.post('/api/alerts', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # event parameter too short
    data = {'event': '', 'type': 'asdf', 'url': 'asdf'}
    request = client.post('/api/alerts', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # name parameter too long
    data = {'event': 'a' * 256, 'type': 'asdf', 'url': 'asdf'}
    request = client.post('/api/alerts', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']

    # Invalid type parameter type
    data = {'event': 'asdf', 'type': 1, 'url': 'asdf'}
    request = client.post('/api/alerts', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # type parameter too short
    data = {'event': 'asdf', 'type': '', 'url': 'asdf'}
    request = client.post('/api/alerts', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # type parameter too long
    data = {'event': 'asdf', 'type': 'a' * 256, 'url': 'asdf'}
    request = client.post('/api/alerts', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']

    # Invalid url parameter type
    data = {'event': 'asdf', 'type': 'asdf', 'url': 1}
    request = client.post('/api/alerts', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # url parameter too short
    data = {'event': 'asdf', 'type': 'asdf', 'url': ''}
    request = client.post('/api/alerts', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # url parameter too long
    data = {'event': 'asdf', 'type': 'asdf', 'url': 'a' * 513}
    request = client.post('/api/alerts', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']


def test_create_duplicate(client):
    """ Ensure a duplicate record cannot be created """

    create_event(client, 'test event', 'analyst')
    alert_request, alert_response = create_alert(client, 'test event', 'ACE', 'http://blahblah.com')
    assert alert_request.status_code == 201

    alert_request, alert_response = create_alert(client, 'test event', 'ACE', 'http://blahblah.com')
    assert alert_request.status_code == 409
    assert alert_response['msg'] == 'Alert URL already exists'


def test_create_missing_token(app, client):
    """ Ensure a token is given if the config requires it """

    app.config['POST'] = 'analyst'

    request = client.post('/api/alerts')
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Missing Authorization Header'


def test_create_invalid_role(app, client):
    """ Ensure the given token has the proper role access """

    app.config['POST'] = 'user_does_not_have_this_role'

    access_token, refresh_token = obtain_token(client, 'analyst', 'analyst')
    headers = create_auth_header(access_token)
    request = client.post('/api/alerts', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'user_does_not_have_this_role role required'


def test_create_autocreate_alert_type(app, client):
    """ Ensure the auto-create alert type config actually works """

    app.config['ALERT_AUTO_CREATE_ALERTTYPE'] = False

    create_event(client, 'test event', 'analyst')

    data = {'event': 'test event', 'type': 'ACE', 'url': 'http://blahblah.com'}

    request = client.post('/api/alerts', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['msg'] == 'Event type not found: ACE'

    app.config['ALERT_AUTO_CREATE_ALERTTYPE'] = True

    request = client.post('/api/alerts', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 201
    assert response['type'] == 'ACE'


def test_create(client):
    """ Ensure a proper request actually works """

    create_event(client, 'test event', 'analyst')
    alert_request, alert_response = create_alert(client, 'test event', 'ACE', 'http://blahblah.com')
    assert alert_request.status_code == 201


"""
READ TESTS
"""


def test_read_nonexistent_id(client):
    """ Ensure a nonexistent ID does not work """

    request = client.get('/api/alerts/100000')
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['msg'] == 'Alert ID not found'


def test_read_missing_token(app, client):
    """ Ensure a token is given if the config requires it """

    app.config['GET'] = 'analyst'

    request = client.get('/api/alerts/1')
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Missing Authorization Header'


def test_read_invalid_role(app, client):
    """ Ensure the given token has the proper role access """

    app.config['GET'] = 'user_does_not_have_this_role'

    access_token, refresh_token = obtain_token(client, 'analyst', 'analyst')
    headers = create_auth_header(access_token)
    request = client.get('/api/alerts/1', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'user_does_not_have_this_role role required'


def test_read_all_values(client):
    """ Ensure all values properly return """

    create_event(client, 'test event', 'analyst')

    alert_request, alert_response = create_alert(client, 'test event', 'ACE', 'http://blahblah.com/1')
    assert alert_request.status_code == 201

    alert_request, alert_response = create_alert(client, 'test event', 'ACE', 'http://blahblah.com/2')
    assert alert_request.status_code == 201

    alert_request, alert_response = create_alert(client, 'test event', 'ACE', 'http://blahblah.com/3')
    assert alert_request.status_code == 201

    request = client.get('/api/alerts')
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 3


def test_read_with_filters(client):
    """ Ensure indicators can be read using the various filters """

    create_event(client, 'test event 1', 'analyst')
    create_event(client, 'some other event 2', 'analyst')

    alert1_request, alert1_response = create_alert(client, 'test event 1', 'ACE', 'http://ace.com/1')
    alert2_request, alert2_response = create_alert(client, 'some other event 2', 'SIEM', 'http://siem.com/2')
    assert alert1_request.status_code == 201
    assert alert2_request.status_code == 201

    # Filter by event
    request = client.get('/api/alerts?event=test')
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 1

    # Filter by URL
    request = client.get('/api/alerts?url=ace.com')
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 1
    assert response['items'][0]['url'] == 'http://ace.com/1'

    # Filter by type
    request = client.get('/api/alerts?type=ACE')
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 1
    assert response['items'][0]['type'] == 'ACE'

    # Filter by multiple
    request = client.get('/api/alerts?event=other&url=siem.com')
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 1

    # Filter by multiple (conflicting)
    request = client.get('/api/alerts?event=test&type=SIEM')
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 0


def test_read_by_id(client):
    """ Ensure records can be read by their ID """

    create_event(client, 'test event', 'analyst')

    alert_request, alert_response = create_alert(client, 'test event', 'ACE', 'http://blahblah.com/1')
    _id = alert_response['id']
    assert alert_request.status_code == 201

    request = client.get('/api/alerts/{}'.format(_id))
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert response['url'] == 'http://blahblah.com/1'


"""
UPDATE TESTS
"""


def test_update_schema(client):
    """ Ensure PUT requests conform to the required JSON schema """

    # Invalid JSON
    data = {}
    request = client.put('/api/alerts/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert response['msg'] == 'Request must include valid JSON'

    # Additional parameter
    data = {'event': 'asdf', 'type': 'asdf', 'url': 'asdf', 'asdf': 'asdf'}
    request = client.put('/api/alerts/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'Additional properties are not allowed' in response['msg']

    # Invalid event parameter type
    data = {'event': 1, 'type': 'asdf', 'url': 'asdf'}
    request = client.put('/api/alerts/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # event parameter too short
    data = {'event': '', 'type': 'asdf', 'url': 'asdf'}
    request = client.put('/api/alerts/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # name parameter too long
    data = {'event': 'a' * 256, 'type': 'asdf', 'url': 'asdf'}
    request = client.put('/api/alerts/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']

    # Invalid type parameter type
    data = {'event': 'asdf', 'type': 1, 'url': 'asdf'}
    request = client.put('/api/alerts/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # type parameter too short
    data = {'event': 'asdf', 'type': '', 'url': 'asdf'}
    request = client.put('/api/alerts/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # type parameter too long
    data = {'event': 'asdf', 'type': 'a' * 256, 'url': 'asdf'}
    request = client.put('/api/alerts/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']

    # Invalid url parameter type
    data = {'event': 'asdf', 'type': 'asdf', 'url': 1}
    request = client.put('/api/alerts/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # url parameter too short
    data = {'event': 'asdf', 'type': 'asdf', 'url': ''}
    request = client.put('/api/alerts/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # url parameter too long
    data = {'event': 'asdf', 'type': 'asdf', 'url': 'a' * 513}
    request = client.put('/api/alerts/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']


def test_update_nonexistent_id(client):
    """ Ensure a nonexistent ID does not work """

    data = {'url': 'asdf'}
    request = client.put('/api/alerts/100000', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['msg'] == 'Alert ID not found'


def test_update_duplicate(client):
    """ Ensure duplicate records cannot be updated """

    create_event(client, 'test event', 'analyst')
    alert_request, alert_response = create_alert(client, 'test event', 'ACE', 'http://blahblah.com/1')
    _id = alert_response['id']
    assert alert_request.status_code == 201

    data = {'url': 'http://blahblah.com/1'}
    request = client.put('/api/alerts/{}'.format(_id), json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 409
    assert response['msg'] == 'Alert URL already exists'


def test_update_missing_token(app, client):
    """ Ensure a token is given if the config requires it """

    app.config['PUT'] = 'analyst'

    request = client.put('/api/alerts/1')
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Missing Authorization Header'


def test_update_invalid_role(app, client):
    """ Ensure the given token has the proper role access """

    app.config['PUT'] = 'user_does_not_have_this_role'

    access_token, refresh_token = obtain_token(client, 'analyst', 'analyst')
    headers = create_auth_header(access_token)
    request = client.put('/api/alerts/1', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'user_does_not_have_this_role role required'


def test_update(client):
    """ Ensure a proper request actually works """

    create_event(client, 'test event', 'analyst')
    alert_request, alert_response = create_alert(client, 'test event', 'ACE', 'http://blahblah.com/1')
    _id = alert_response['id']
    assert alert_request.status_code == 201

    data = {'url': 'http://blahblah.com/2'}
    request = client.put('/api/alerts/{}'.format(_id), json=data)
    assert request.status_code == 200

    request = client.get('/api/alerts/{}'.format(_id))
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert response['url'] == 'http://blahblah.com/2'


"""
DELETE TESTS
"""


def test_delete_nonexistent_id(client):
    """ Ensure a nonexistent ID does not work """

    request = client.delete('/api/alerts/100000')
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['msg'] == 'Alert ID not found'


def test_delete_missing_token(app, client):
    """ Ensure a token is given if the config requires it """

    app.config['DELETE'] = 'admin'

    request = client.delete('/api/alerts/1')
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Missing Authorization Header'


def test_delete_invalid_role(app, client):
    """ Ensure the given token has the proper role access """

    app.config['DELETE'] = 'user_does_not_have_this_role'

    access_token, refresh_token = obtain_token(client, 'analyst', 'analyst')
    headers = create_auth_header(access_token)
    request = client.delete('/api/alerts/1', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'user_does_not_have_this_role role required'


def test_delete(client):
    """ Ensure a proper request actually works """

    create_event(client, 'test event', 'analyst')
    alert_request, alert_response = create_alert(client, 'test event', 'ACE', 'http://blahblah.com/1')
    _id = alert_response['id']
    assert alert_request.status_code == 201

    request = client.delete('/api/alerts/{}'.format(_id))
    assert request.status_code == 204

    request = client.get('/api/alerts/{}'.format(_id))
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['msg'] == 'Alert ID not found'
