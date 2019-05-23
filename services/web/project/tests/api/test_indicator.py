import datetime
import gzip
import time
import urllib.parse

from project.tests.conftest import TEST_ANALYST_APIKEY, TEST_INACTIVE_APIKEY, TEST_INVALID_APIKEY
from project.tests.helpers import *


"""
CREATE TESTS
"""


def test_create_schema(client):
    """ Ensure POST requests conform to the required JSON schema """

    # Invalid JSON
    data = {}
    request = client.post('/api/indicators', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert response['msg'] == 'Request must include valid JSON'

    # Missing required type parameter
    data = {'username': 'asdf', 'value': 'asdf'}
    request = client.post('/api/indicators', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert response['msg'] == "Request JSON does not match schema: 'type' is a required property"

    # Missing required value parameter
    data = {'type': 'asdf', 'username': 'asdf'}
    request = client.post('/api/indicators', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert response['msg'] == "Request JSON does not match schema: 'value' is a required property"

    # Additional parameter
    data = {'type': 'asdf', 'username': 'asdf', 'value': 'asdf', 'asdf': 'asdf'}
    request = client.post('/api/indicators', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'Additional properties are not allowed' in response['msg']

    # Invalid type parameter type
    data = {'type': 1, 'username': 'asdf', 'value': 'asdf'}
    request = client.post('/api/indicators', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # Invalid username parameter type
    data = {'type': 'asdf', 'username': 1, 'value': 'asdf'}
    request = client.post('/api/indicators', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # Invalid value parameter type
    data = {'type': 'asdf', 'username': 'asdf', 'value': 1}
    request = client.post('/api/indicators', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # type parameter too short
    data = {'type': '', 'username': 'asdf', 'value': 'asdf'}
    request = client.post('/api/indicators', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # type parameter too long
    data = {'type': 'a' * 256, 'username': 'asdf', 'value': 'asdf'}
    request = client.post('/api/indicators', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']

    # username parameter too short
    data = {'type': 'asdf', 'username': '', 'value': 'asdf'}
    request = client.post('/api/indicators', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # username parameter too long
    data = {'type': 'asdf', 'username': 'a' * 256, 'value': 'asdf'}
    request = client.post('/api/indicators', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']

    # value parameter too short
    data = {'type': 'asdf', 'username': 'asdf', 'value': ''}
    request = client.post('/api/indicators', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # value parameter too long
    data = {'type': 'asdf', 'username': 'asdf', 'value': 'a' * 513}
    request = client.post('/api/indicators', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']

    # Invalid campaigns parameter type
    data = {'type': 'asdf', 'username': 'asdf', 'value': 'asdf', 'campaigns': 'asdf'}
    request = client.post('/api/indicators', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "'asdf' is not of type 'array'" in response['msg']

    # Empty campaigns parameter type
    data = {'type': 'asdf', 'username': 'asdf', 'value': 'asdf', 'campaigns': []}
    request = client.post('/api/indicators', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # Invalid campaigns parameter type
    data = {'type': 'asdf', 'username': 'asdf', 'value': 'asdf', 'campaigns': [1]}
    request = client.post('/api/indicators', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # campaigns parameter too short
    data = {'type': 'asdf', 'username': 'asdf', 'value': 'asdf', 'campaigns': ['']}
    request = client.post('/api/indicators', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # campaigns parameter too long
    data = {'type': 'asdf', 'username': 'asdf', 'value': 'asdf', 'campaigns': ['a' * 256]}
    request = client.post('/api/indicators', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']

    # Invalid references parameter type
    data = {'type': 'asdf', 'username': 'asdf', 'value': 'asdf', 'references': 'asdf'}
    request = client.post('/api/indicators', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "'asdf' is not of type 'array'" in response['msg']

    # Empty references parameter type
    data = {'type': 'asdf', 'username': 'analyst', 'value': 'asdf', 'references': []}
    request = client.post('/api/indicators', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # Invalid references parameter type
    data = {'type': 'asdf', 'username': 'asdf', 'value': 'asdf', 'references': [1]}
    request = client.post('/api/indicators', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'object'" in response['msg']

    # reference parameter too short
    data = {'type': 'asdf', 'username': 'asdf', 'value': 'asdf', 'references': [{'reference': '', 'source': 'asdf'}]}
    request = client.post('/api/indicators', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # reference parameter too long
    data = {'type': 'asdf', 'username': 'asdf', 'value': 'asdf', 'references': [{'reference': 'a' * 513, 'source': 'asdf'}]}
    request = client.post('/api/indicators', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']

    # source parameter too short
    data = {'type': 'asdf', 'username': 'asdf', 'value': 'asdf', 'references': [{'reference': 'asdf', 'source': ''}]}
    request = client.post('/api/indicators', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # source parameter too long
    data = {'type': 'asdf', 'username': 'asdf', 'value': 'asdf', 'references': [{'reference': 'asdf', 'source': 'a' * 256}]}
    request = client.post('/api/indicators', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']

    # Invalid tags parameter type
    data = {'type': 'asdf', 'username': 'asdf', 'value': 'asdf', 'tags': 'asdf'}
    request = client.post('/api/indicators', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "'asdf' is not of type 'array'" in response['msg']

    # Empty tags parameter type
    data = {'type': 'asdf', 'username': 'asdf', 'value': 'asdf', 'tags': []}
    request = client.post('/api/indicators', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # Invalid tags parameter type
    data = {'type': 'asdf', 'username': 'asdf', 'value': 'asdf', 'tags': [1]}
    request = client.post('/api/indicators', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # tags parameter too short
    data = {'type': 'asdf', 'username': 'asdf', 'value': 'asdf', 'tags': ['']}
    request = client.post('/api/indicators', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # tags parameter too long
    data = {'type': 'asdf', 'username': 'asdf', 'value': 'asdf', 'tags': ['a' * 256]}
    request = client.post('/api/indicators', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']

    # Invalid case_sensitive parameter type
    data = {'type': 'asdf', 'username': 'asdf', 'value': 'asdf', 'case_sensitive': 1}
    request = client.post('/api/indicators', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'boolean'" in response['msg']

    # Invalid substring parameter type
    data = {'type': 'asdf', 'username': 'asdf', 'value': 'asdf', 'substring': 1}
    request = client.post('/api/indicators', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'boolean'" in response['msg']

    # Invalid confidence parameter type
    data = {'type': 'asdf', 'username': 'asdf', 'value': 'asdf', 'confidence': 1}
    request = client.post('/api/indicators', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # confidence parameter too short
    data = {'type': 'asdf', 'username': 'asdf', 'value': 'asdf', 'confidence': ''}
    request = client.post('/api/indicators', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # confidence parameter too long
    data = {'type': 'asdf', 'username': 'asdf', 'value': 'asdf', 'confidence': 'a' * 256}
    request = client.post('/api/indicators', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']

    # Invalid impact parameter type
    data = {'type': 'asdf', 'username': 'asdf', 'value': 'asdf', 'impact': 1}
    request = client.post('/api/indicators', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # impact parameter too short
    data = {'type': 'asdf', 'username': 'asdf', 'value': 'asdf', 'impact': ''}
    request = client.post('/api/indicators', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # impact parameter too long
    data = {'type': 'asdf', 'username': 'asdf', 'value': 'asdf', 'impact': 'a' * 256}
    request = client.post('/api/indicators', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']

    # Invalid status parameter type
    data = {'type': 'asdf', 'username': 'asdf', 'value': 'asdf', 'status': 1}
    request = client.post('/api/indicators', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # status parameter too short
    data = {'type': 'asdf', 'username': 'asdf', 'value': 'asdf', 'status': ''}
    request = client.post('/api/indicators', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # status parameter too long
    data = {'type': 'asdf', 'username': 'asdf', 'value': 'asdf', 'status': 'a' * 256}
    request = client.post('/api/indicators', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']


def test_create_duplicate(client):
    """ Ensure a duplicate record cannot be created """

    request, response = create_indicator(client, 'asdf', 'asdf', 'analyst')
    assert request.status_code == 201

    request, response = create_indicator(client, 'asdf', 'asdf', 'analyst')
    assert request.status_code == 409
    assert response['msg'] == 'Case-insensitive indicator already exists'

    request, response = create_indicator(client, 'asdf', 'ASDF', 'analyst')
    assert request.status_code == 409
    assert response['msg'] == 'Case-insensitive indicator already exists'


def test_create_nonexistent_username(client):
    """ Ensure an indicator cannot be created with a nonexistent username """

    request, response = create_indicator(client, 'asdf', 'asdf', 'this_user_does_not_exist')
    assert request.status_code == 404
    assert response['msg'] == 'User not found by username'


def test_create_inactive_username(client):
    """ Ensure an indicator cannot be created with an inactive username """

    request, response = create_indicator(client, 'asdf', 'asdf', 'inactive')
    assert request.status_code == 401
    assert response['msg'] == 'Cannot create an indicator with an inactive user'


def test_create_missing_api_key(app, client):
    """ Ensure an API key is given if the config requires it """

    app.config['POST'] = 'analyst'

    request = client.post('/api/indicators')
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Bad or missing API key'


def test_create_invalid_api_key(app, client):
    """ Ensure an API key not found in the database does not work """

    app.config['POST'] = 'analyst'

    headers = {'Authorization': 'Apikey ' + TEST_INVALID_APIKEY}
    request = client.post('/api/indicators', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'API user does not exist'


def test_create_inactive_api_key(app, client):
    """ Ensure an inactive API key does not work """

    app.config['POST'] = 'analyst'

    headers = {'Authorization': 'Apikey ' + TEST_INACTIVE_APIKEY}
    request = client.post('/api/indicators', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'API user is not active'


def test_create_invalid_role(app, client):
    """ Ensure the given API key has the proper role access """

    app.config['POST'] = 'user_does_not_have_this_role'

    headers = {'Authorization': 'Apikey ' + TEST_ANALYST_APIKEY}
    request = client.post('/api/indicators', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Insufficient privileges'


def test_create_api_key_instead_of_username(app, client):
    """ Ensure that supplying an API key instead of username value works """

    app.config['INDICATOR_AUTO_CREATE_INDICATORCONFIDENCE'] = True
    app.config['INDICATOR_AUTO_CREATE_INDICATORIMPACT'] = True
    app.config['INDICATOR_AUTO_CREATE_INDICATORSTATUS'] = True
    app.config['INDICATOR_AUTO_CREATE_INDICATORTYPE'] = True

    # Try a missing API key.
    data = {'confidence': 'LOW',
            'impact': 'LOW',
            'status': 'New',
            'substring': False,
            'type': 'Email - Address',
            'value': 'badguy@evil.com'}
    request = client.post('/api/indicators', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'You must supply either username or API key'

    # Try an invalid API key.
    headers = {'Authorization': 'Apikey ' + 'this-api-key-does-not-exist'}
    data = {'confidence': 'LOW',
            'impact': 'LOW',
            'status': 'New',
            'substring': False,
            'type': 'Email - Address',
            'value': 'badguy@evil.com'}
    request = client.post('/api/indicators', headers=headers, json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['msg'] == 'User not found by API key'

    # Try an inactive API key.
    headers = {'Authorization': 'Apikey ' + TEST_INACTIVE_APIKEY}
    data = {'confidence': 'LOW',
            'impact': 'LOW',
            'status': 'New',
            'substring': False,
            'type': 'Email - Address',
            'value': 'badguy@evil.com'}
    request = client.post('/api/indicators', headers=headers, json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Cannot create an indicator with an inactive user'

    # Try a valid API key.
    headers = {'Authorization': 'Apikey ' + TEST_ANALYST_APIKEY}
    data = {'confidence': 'LOW',
            'impact': 'LOW',
            'status': 'New',
            'substring': False,
            'type': 'Email - Address',
            'value': 'badguy@evil.com'}
    request = client.post('/api/indicators', headers=headers, json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 201
    assert response['user'] == 'analyst'


def test_create_autocreate_campaign(app, client):
    """ Ensure the auto-create campaign config actually works """

    app.config['INDICATOR_AUTO_CREATE_CAMPAIGN'] = False
    app.config['INDICATOR_AUTO_CREATE_INDICATORCONFIDENCE'] = True
    app.config['INDICATOR_AUTO_CREATE_INDICATORIMPACT'] = True
    app.config['INDICATOR_AUTO_CREATE_INDICATORSTATUS'] = True
    app.config['INDICATOR_AUTO_CREATE_INDICATORTYPE'] = True
    app.config['INDICATOR_AUTO_CREATE_INTELREFERENCE'] = True
    app.config['INDICATOR_AUTO_CREATE_TAG'] = True

    data = {'campaigns': ['Derpsters'],
            'case_sensitive': False,
            'confidence': 'LOW',
            'impact': 'LOW',
            'references': [{'source': 'OSINT', 'reference': 'http://blahblah.com'}],
            'status': 'New',
            'substring': False,
            'tags': ['phish', 'from_address'],
            'type': 'Email - Address',
            'username': 'analyst',
            'value': 'badguy@evil.com'}

    request = client.post('/api/indicators', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['msg'] == 'Campaign not found: Derpsters'

    app.config['INDICATOR_AUTO_CREATE_CAMPAIGN'] = True

    request = client.post('/api/indicators', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 201
    assert response['campaigns'][0]['name'] == 'Derpsters'


def test_create_autocreate_indicator_confidence(app, client):
    """ Ensure the auto-create indicator confidence config actually works """

    app.config['INDICATOR_AUTO_CREATE_CAMPAIGN'] = True
    app.config['INDICATOR_AUTO_CREATE_INDICATORCONFIDENCE'] = False
    app.config['INDICATOR_AUTO_CREATE_INDICATORIMPACT'] = True
    app.config['INDICATOR_AUTO_CREATE_INDICATORSTATUS'] = True
    app.config['INDICATOR_AUTO_CREATE_INDICATORTYPE'] = True
    app.config['INDICATOR_AUTO_CREATE_INTELREFERENCE'] = True
    app.config['INDICATOR_AUTO_CREATE_TAG'] = True

    data = {'campaigns': ['Derpsters'],
            'case_sensitive': False,
            'confidence': 'LOW',
            'impact': 'LOW',
            'references': [{'source': 'OSINT', 'reference': 'http://blahblah.com'}],
            'status': 'New',
            'substring': False,
            'tags': ['phish', 'from_address'],
            'type': 'Email - Address',
            'username': 'analyst',
            'value': 'badguy@evil.com'}

    request = client.post('/api/indicators', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['msg'] == 'Indicator confidence not found: LOW'

    app.config['INDICATOR_AUTO_CREATE_INDICATORCONFIDENCE'] = True

    request = client.post('/api/indicators', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 201
    assert response['confidence'] == 'LOW'


def test_create_autocreate_indicator_impact(app, client):
    """ Ensure the auto-create indicator impact config actually works """

    app.config['INDICATOR_AUTO_CREATE_CAMPAIGN'] = True
    app.config['INDICATOR_AUTO_CREATE_INDICATORCONFIDENCE'] = True
    app.config['INDICATOR_AUTO_CREATE_INDICATORIMPACT'] = False
    app.config['INDICATOR_AUTO_CREATE_INDICATORSTATUS'] = True
    app.config['INDICATOR_AUTO_CREATE_INDICATORTYPE'] = True
    app.config['INDICATOR_AUTO_CREATE_INTELREFERENCE'] = True
    app.config['INDICATOR_AUTO_CREATE_TAG'] = True

    data = {'campaigns': ['Derpsters'],
            'case_sensitive': False,
            'confidence': 'LOW',
            'impact': 'LOW',
            'references': [{'source': 'OSINT', 'reference': 'http://blahblah.com'}],
            'status': 'New',
            'substring': False,
            'tags': ['phish', 'from_address'],
            'type': 'Email - Address',
            'username': 'analyst',
            'value': 'badguy@evil.com'}

    request = client.post('/api/indicators', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['msg'] == 'Indicator impact not found: LOW'

    app.config['INDICATOR_AUTO_CREATE_INDICATORIMPACT'] = True

    request = client.post('/api/indicators', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 201
    assert response['impact'] == 'LOW'


def test_create_autocreate_indicator_status(app, client):
    """ Ensure the auto-create indicator status config actually works """

    app.config['INDICATOR_AUTO_CREATE_CAMPAIGN'] = True
    app.config['INDICATOR_AUTO_CREATE_INDICATORCONFIDENCE'] = True
    app.config['INDICATOR_AUTO_CREATE_INDICATORIMPACT'] = True
    app.config['INDICATOR_AUTO_CREATE_INDICATORSTATUS'] = False
    app.config['INDICATOR_AUTO_CREATE_INDICATORTYPE'] = True
    app.config['INDICATOR_AUTO_CREATE_INTELREFERENCE'] = True
    app.config['INDICATOR_AUTO_CREATE_TAG'] = True

    data = {'campaigns': ['Derpsters'],
            'case_sensitive': False,
            'confidence': 'LOW',
            'impact': 'LOW',
            'references': [{'source': 'OSINT', 'reference': 'http://blahblah.com'}],
            'status': 'New',
            'substring': False,
            'tags': ['phish', 'from_address'],
            'type': 'Email - Address',
            'username': 'analyst',
            'value': 'badguy@evil.com'}

    request = client.post('/api/indicators', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['msg'] == 'Indicator status not found: New'

    app.config['INDICATOR_AUTO_CREATE_INDICATORSTATUS'] = True

    request = client.post('/api/indicators', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 201
    assert response['status'] == 'New'


def test_create_autocreate_indicator_type(app, client):
    """ Ensure the auto-create indicator type config actually works """

    app.config['INDICATOR_AUTO_CREATE_CAMPAIGN'] = True
    app.config['INDICATOR_AUTO_CREATE_INDICATORCONFIDENCE'] = True
    app.config['INDICATOR_AUTO_CREATE_INDICATORIMPACT'] = True
    app.config['INDICATOR_AUTO_CREATE_INDICATORSTATUS'] = True
    app.config['INDICATOR_AUTO_CREATE_INDICATORTYPE'] = False
    app.config['INDICATOR_AUTO_CREATE_INTELREFERENCE'] = True
    app.config['INDICATOR_AUTO_CREATE_TAG'] = True

    data = {'campaigns': ['Derpsters'],
            'case_sensitive': False,
            'confidence': 'LOW',
            'impact': 'LOW',
            'references': [{'source': 'OSINT', 'reference': 'http://blahblah.com'}],
            'status': 'New',
            'substring': False,
            'tags': ['phish', 'from_address'],
            'type': 'Email - Address',
            'username': 'analyst',
            'value': 'badguy@evil.com'}

    request = client.post('/api/indicators', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['msg'] == 'Indicator type not found: Email - Address'

    app.config['INDICATOR_AUTO_CREATE_INDICATORTYPE'] = True

    request = client.post('/api/indicators', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 201
    assert response['type'] == 'Email - Address'


def test_create_autocreate_intel_reference(app, client):
    """ Ensure the auto-create intel reference config actually works """

    app.config['INDICATOR_AUTO_CREATE_CAMPAIGN'] = True
    app.config['INDICATOR_AUTO_CREATE_INDICATORCONFIDENCE'] = True
    app.config['INDICATOR_AUTO_CREATE_INDICATORIMPACT'] = True
    app.config['INDICATOR_AUTO_CREATE_INDICATORSTATUS'] = True
    app.config['INDICATOR_AUTO_CREATE_INDICATORTYPE'] = True
    app.config['INDICATOR_AUTO_CREATE_INTELREFERENCE'] = False
    app.config['INDICATOR_AUTO_CREATE_TAG'] = True

    data = {'campaigns': ['Derpsters'],
            'case_sensitive': False,
            'confidence': 'LOW',
            'impact': 'LOW',
            'references': [{'source': 'OSINT', 'reference': 'http://blahblah.com'}],
            'status': 'New',
            'substring': False,
            'tags': ['phish', 'from_address'],
            'type': 'Email - Address',
            'username': 'analyst',
            'value': 'badguy@evil.com'}

    request = client.post('/api/indicators', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['msg'] == 'Intel reference not found: http://blahblah.com'

    app.config['INDICATOR_AUTO_CREATE_INTELREFERENCE'] = True

    request = client.post('/api/indicators', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 201
    assert response['references'][0]['reference'] == 'http://blahblah.com'


def test_create_autocreate_tag(app, client):
    """ Ensure the auto-create tag config actually works """

    app.config['INDICATOR_AUTO_CREATE_CAMPAIGN'] = True
    app.config['INDICATOR_AUTO_CREATE_INDICATORCONFIDENCE'] = True
    app.config['INDICATOR_AUTO_CREATE_INDICATORIMPACT'] = True
    app.config['INDICATOR_AUTO_CREATE_INDICATORSTATUS'] = True
    app.config['INDICATOR_AUTO_CREATE_INDICATORTYPE'] = True
    app.config['INDICATOR_AUTO_CREATE_INTELREFERENCE'] = True
    app.config['INDICATOR_AUTO_CREATE_TAG'] = False

    data = {'campaigns': ['Derpsters'],
            'case_sensitive': False,
            'confidence': 'LOW',
            'impact': 'LOW',
            'references': [{'source': 'OSINT', 'reference': 'http://blahblah.com'}],
            'status': 'New',
            'substring': False,
            'tags': ['phish', 'from_address'],
            'type': 'Email - Address',
            'username': 'analyst',
            'value': 'badguy@evil.com'}

    request = client.post('/api/indicators', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['msg'] == 'Tag not found: phish'

    app.config['INDICATOR_AUTO_CREATE_TAG'] = True

    request = client.post('/api/indicators', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 201
    assert response['tags'] == ['from_address', 'phish']


def test_create_case_sensitivity(client):
    """ Ensure the database case-sensitivity is working """

    request, response = create_indicator(client, 'asdf', 'asdf', 'analyst',
                                         campaigns=['LOLcats', 'Derpsters'],
                                         case_sensitive=False,
                                         confidence='HIGH',
                                         impact='HIGH',
                                         intel_reference='http://blahblah.com',
                                         intel_source='OSINT',
                                         status='Analyzed',
                                         substring=False,
                                         tags=['phish', 'nanocore'])
    assert request.status_code == 201
    assert response['type'] == 'asdf'
    assert response['value'] == 'asdf'

    request, response = create_indicator(client, 'asdf', 'ASDF', 'analyst',
                                         campaigns=['LOLcats', 'Derpsters'],
                                         case_sensitive=False,
                                         confidence='HIGH',
                                         impact='HIGH',
                                         intel_reference='http://blahblah.com',
                                         intel_source='OSINT',
                                         status='Analyzed',
                                         substring=False,
                                         tags=['phish', 'nanocore'])
    assert request.status_code == 409
    assert response['msg'] == 'Case-insensitive indicator already exists'

    request, response = create_indicator(client, 'asdf', 'ASDF', 'analyst',
                                         campaigns=['LOLcats', 'Derpsters'],
                                         case_sensitive=True,
                                         confidence='HIGH',
                                         impact='HIGH',
                                         intel_reference='http://blahblah.com',
                                         intel_source='OSINT',
                                         status='Analyzed',
                                         substring=False,
                                         tags=['phish', 'nanocore'])
    assert request.status_code == 201
    assert response['type'] == 'asdf'
    assert response['value'] == 'ASDF'


def test_create(client):
    """ Ensure a proper request actually works """

    request, response = create_indicator(client, 'asdf', 'asdf', 'analyst',
                                         campaigns=['LOLcats', 'Derpsters'],
                                         case_sensitive=True,
                                         confidence='HIGH',
                                         impact='HIGH',
                                         intel_reference='http://blahblah.com',
                                         intel_source='OSINT',
                                         status='Analyzed',
                                         substring=True,
                                         tags=['phish', 'nanocore'])
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


def test_read_missing_api_key(app, client):
    """ Ensure an API key is given if the config requires it """

    app.config['GET'] = 'analyst'

    request = client.get('/api/indicators/1')
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Bad or missing API key'


def test_read_invalid_api_key(app, client):
    """ Ensure an API key not found in the database does not work """

    app.config['GET'] = 'analyst'

    headers = {'Authorization': 'Apikey ' + TEST_INVALID_APIKEY}
    request = client.get('/api/indicators/1', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'API user does not exist'


def test_read_inactive_api_key(app, client):
    """ Ensure an inactive API key does not work """

    app.config['GET'] = 'analyst'

    headers = {'Authorization': 'Apikey ' + TEST_INACTIVE_APIKEY}
    request = client.get('/api/indicators/1', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'API user is not active'


def test_read_invalid_role(app, client):
    """ Ensure the given API key has the proper role access """

    app.config['GET'] = 'user_does_not_have_this_role'

    headers = {'Authorization': 'Apikey ' + TEST_ANALYST_APIKEY}
    request = client.get('/api/indicators/1', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Insufficient privileges'


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
                                                               campaigns=['Derpsters'],
                                                               case_sensitive=True,
                                                               confidence='HIGH',
                                                               impact='HIGH',
                                                               intel_reference='http://blahblah.com',
                                                               intel_source='OSINT',
                                                               status='Analyzed',
                                                               substring=True,
                                                               tags=['phish'])
    assert indicator1_request.status_code == 201

    time.sleep(1)

    indicator2_request, indicator2_response = create_indicator(client, 'Email', 'asdf@asdf.com', 'admin',
                                                               campaigns=['LOLcats'],
                                                               case_sensitive=False,
                                                               confidence='LOW',
                                                               impact='LOW',
                                                               intel_reference='http://blahblah2.com',
                                                               intel_source='VirusTotal',
                                                               status='New',
                                                               substring=False,
                                                               tags=['nanocore'])
    assert indicator2_request.status_code == 201

    time.sleep(1)

    indicator3_request, indicator3_response = create_indicator(client, 'Email', 'abcd@abcd.com', 'admin',
                                                               campaigns=['LOLcats'],
                                                               case_sensitive=False,
                                                               confidence='LOW',
                                                               impact='LOW',
                                                               intel_reference='http://blahblah2.com',
                                                               intel_source='VirusTotal',
                                                               status='New',
                                                               substring=False,
                                                               tags=['nanocore'])
    assert indicator3_request.status_code == 201

    time.sleep(1)

    indicator4_request, indicator4_response = create_indicator(client, 'Email', 'abcd2@abcd.com', 'admin',
                                                               campaigns=[],
                                                               case_sensitive=False,
                                                               confidence='LOW',
                                                               impact='LOW',
                                                               intel_reference='https://your.wiki/display/events/20190501+somebadsite.local+-+Bad+Guy',
                                                               intel_source='VirusTotal',
                                                               status='New',
                                                               substring=False,
                                                               tags=['nanocore'])
    assert indicator4_request.status_code == 201

    time.sleep(1)

    # Filter with bulk mode enabled.
    request = client.get('/api/indicators?bulk=true')
    response = gzip.decompress(request.data)
    response = json.loads(response.decode('utf-8'))
    assert request.status_code == 200
    assert len(response) == 4

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
    assert len(response['items']) == 4
    request = client.get('/api/indicators?created_before={}'.format(indicator2_response['created_time']))
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 1
    assert response['items'][0]['value'] == '1.1.1.1'

    # Filter by created_after
    request = client.get('/api/indicators?created_after={}'.format(datetime.datetime.min))
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 4
    request = client.get('/api/indicators?created_after={}'.format(indicator1_response['created_time']))
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 3
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
    assert len(response['items']) == 4
    request = client.get('/api/indicators?modified_before={}'.format(indicator2_response['modified_time']))
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 1
    assert response['items'][0]['value'] == '1.1.1.1'

    # Filter by modified_after
    request = client.get('/api/indicators?modified_after={}'.format(datetime.datetime.min))
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 4
    request = client.get('/api/indicators?modified_after={}'.format(indicator1_response['modified_time']))
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 3
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

    # Filter by NOT tag
    request = client.get('/api/indicators?not_tags=nanocore')
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 1
    assert response['items'][0]['value'] == '1.1.1.1'
    request = client.get('/api/indicators?not_tags=nanocore,phish')
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 0

    # Filter by type
    request = client.get('/api/indicators?type=IP')
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 1
    assert response['items'][0]['value'] == '1.1.1.1'

    # Filter by user
    request = client.get('/api/indicators?user=analyst')
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 1
    assert response['items'][0]['user'] == 'analyst'

    # Filter by value
    request = client.get('/api/indicators?value=abcd')
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 2

    # Filter by exact value (success)
    request = client.get('/api/indicators?exact_value=abcd@abcd.com')
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 1
    assert response['items'][0]['value'] == 'abcd@abcd.com'

    # Filter by exact value (failure)
    request = client.get('/api/indicators?exact_value=abcd')
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 0

    # Filter by intel reference
    request = client.get('/api/indicators?reference={}'.format(urllib.parse.quote('https://your.wiki/display/events/20190501+somebadsite.local+-+Bad+Guy')))
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 1
    assert response['items'][0]['value'] == 'abcd2@abcd.com'

    # Filter by intel source
    request = client.get('/api/indicators?sources=OSINT')
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 1
    assert response['items'][0]['value'] == '1.1.1.1'

    # Filter by NOT intel source
    request = client.get('/api/indicators?not_sources=OSINT')
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert len(response['items']) == 3
    assert response['items'][0]['value'] == 'asdf@asdf.com'
    assert response['items'][1]['value'] == 'abcd@abcd.com'

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


def test_update_schema(client):
    """ Ensure PUT requests conform to the required JSON schema """

    # Invalid JSON
    data = {}
    request = client.put('/api/indicators/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert response['msg'] == 'Request must include valid JSON'

    # Additional parameter
    data = {'type': 'asdf', 'username': 'asdf', 'value': 'asdf', 'asdf': 'asdf'}
    request = client.put('/api/indicators/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'Additional properties are not allowed' in response['msg']

    # Invalid username parameter type
    data = {'type': 'asdf', 'username': 1, 'value': 'asdf'}
    request = client.put('/api/indicators/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # username parameter too short
    data = {'type': 'asdf', 'username': '', 'value': 'asdf'}
    request = client.put('/api/indicators/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # username parameter too long
    data = {'type': 'asdf', 'username': 'a' * 256, 'value': 'asdf'}
    request = client.put('/api/indicators/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']

    # Invalid campaigns parameter type
    data = {'type': 'asdf', 'username': 'asdf', 'value': 'asdf', 'campaigns': 'asdf'}
    request = client.put('/api/indicators/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "'asdf' is not of type 'array'" in response['msg']

    # Empty campaigns parameter type
    data = {'type': 'asdf', 'username': 'asdf', 'value': 'asdf', 'campaigns': []}
    request = client.put('/api/indicators/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # Invalid campaigns parameter type
    data = {'type': 'asdf', 'username': 'asdf', 'value': 'asdf', 'campaigns': [1]}
    request = client.put('/api/indicators/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # campaigns parameter too short
    data = {'type': 'asdf', 'username': 'asdf', 'value': 'asdf', 'campaigns': ['']}
    request = client.put('/api/indicators/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # campaigns parameter too long
    data = {'type': 'asdf', 'username': 'asdf', 'value': 'asdf', 'campaigns': ['a' * 256]}
    request = client.put('/api/indicators/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']

    # Invalid references parameter type
    data = {'type': 'asdf', 'username': 'asdf', 'value': 'asdf', 'references': 'asdf'}
    request = client.put('/api/indicators/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "'asdf' is not of type 'array'" in response['msg']

    # Empty references parameter type
    data = {'type': 'asdf', 'username': 'asdf', 'value': 'asdf', 'references': []}
    request = client.put('/api/indicators/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # Invalid references parameter type
    data = {'type': 'asdf', 'username': 'asdf', 'value': 'asdf', 'references': [1]}
    request = client.put('/api/indicators/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # references parameter too short
    data = {'type': 'asdf', 'username': 'asdf', 'value': 'asdf', 'references': ['']}
    request = client.put('/api/indicators/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # references parameter too long
    data = {'type': 'asdf', 'username': 'asdf', 'value': 'asdf', 'references': ['a' * 513]}
    request = client.put('/api/indicators/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']

    # Invalid tags parameter type
    data = {'type': 'asdf', 'username': 'asdf', 'value': 'asdf', 'tags': 'asdf'}
    request = client.put('/api/indicators/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "'asdf' is not of type 'array'" in response['msg']

    # Empty tags parameter type
    data = {'type': 'asdf', 'username': 'asdf', 'value': 'asdf', 'tags': []}
    request = client.put('/api/indicators/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # Invalid tags parameter type
    data = {'type': 'asdf', 'username': 'asdf', 'value': 'asdf', 'tags': [1]}
    request = client.put('/api/indicators/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # tags parameter too short
    data = {'type': 'asdf', 'username': 'asdf', 'value': 'asdf', 'tags': ['']}
    request = client.put('/api/indicators/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # tags parameter too long
    data = {'type': 'asdf', 'username': 'asdf', 'value': 'asdf', 'tags': ['a' * 256]}
    request = client.put('/api/indicators/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']

    # Invalid case_sensitive parameter type
    data = {'type': 'asdf', 'username': 'asdf', 'value': 'asdf', 'case_sensitive': 1}
    request = client.put('/api/indicators/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'boolean'" in response['msg']

    # Invalid substring parameter type
    data = {'type': 'asdf', 'username': 'asdf', 'value': 'asdf', 'substring': 1}
    request = client.put('/api/indicators/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'boolean'" in response['msg']

    # Invalid confidence parameter type
    data = {'type': 'asdf', 'username': 'asdf', 'value': 'asdf', 'confidence': 1}
    request = client.put('/api/indicators/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # confidence parameter too short
    data = {'type': 'asdf', 'username': 'asdf', 'value': 'asdf', 'confidence': ''}
    request = client.put('/api/indicators/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # confidence parameter too long
    data = {'type': 'asdf', 'username': 'asdf', 'value': 'asdf', 'confidence': 'a' * 256}
    request = client.put('/api/indicators/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']

    # Invalid impact parameter type
    data = {'type': 'asdf', 'username': 'asdf', 'value': 'asdf', 'impact': 1}
    request = client.put('/api/indicators/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # impact parameter too short
    data = {'type': 'asdf', 'username': 'asdf', 'value': 'asdf', 'impact': ''}
    request = client.put('/api/indicators/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # impact parameter too long
    data = {'type': 'asdf', 'username': 'asdf', 'value': 'asdf', 'impact': 'a' * 256}
    request = client.put('/api/indicators/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']

    # Invalid status parameter type
    data = {'type': 'asdf', 'username': 'asdf', 'value': 'asdf', 'status': 1}
    request = client.put('/api/indicators/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert "1 is not of type 'string'" in response['msg']

    # status parameter too short
    data = {'type': 'asdf', 'username': 'asdf', 'value': 'asdf', 'status': ''}
    request = client.put('/api/indicators/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too short' in response['msg']

    # status parameter too long
    data = {'type': 'asdf', 'username': 'asdf', 'value': 'asdf', 'status': 'a' * 256}
    request = client.put('/api/indicators/1', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert 'too long' in response['msg']


def test_update_nonexistent_username(client):
    """ Ensure an indicator cannot be updated with a nonexistent username """

    request, response = create_indicator(client, 'asdf', 'asdf', 'analyst')
    _id = response['id']
    assert request.status_code == 201

    data = {'username': 'this_user_does_not_exist'}
    request = client.put('/api/indicators/{}'.format(_id), json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert 'User username not found:' in response['msg']


def test_update_inactive_username(client):
    """ Ensure an indicator cannot be updated with an inactive username """

    request, response = create_indicator(client, 'asdf', 'asdf', 'analyst')
    _id = response['id']
    assert request.status_code == 201

    data = {'username': 'inactive'}
    request = client.put('/api/indicators/{}'.format(_id), json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Cannot update an indicator with an inactive user'


def test_update_nonexistent_id(client):
    """ Ensure a nonexistent ID does not work """

    data = {'username': 'analyst'}
    request = client.put('/api/indicators/100000', json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 404
    assert response['msg'] == 'Indicator ID not found'


def test_update_missing_api_key(app, client):
    """ Ensure an API key is given if the config requires it """

    app.config['PUT'] = 'analyst'

    request = client.put('/api/indicators/1')
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Bad or missing API key'


def test_update_invalid_api_key(app, client):
    """ Ensure an API key not found in the database does not work """

    app.config['PUT'] = 'analyst'

    headers = {'Authorization': 'Apikey ' + TEST_INVALID_APIKEY}
    request = client.put('/api/indicators/1', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'API user does not exist'


def test_update_inactive_api_key(app, client):
    """ Ensure an inactive API key does not work """

    app.config['PUT'] = 'analyst'

    headers = {'Authorization': 'Apikey ' + TEST_INACTIVE_APIKEY}
    request = client.put('/api/indicators/1', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'API user is not active'


def test_update_invalid_role(app, client):
    """ Ensure the given API key has the proper role access """

    app.config['PUT'] = 'user_does_not_have_this_role'

    headers = {'Authorization': 'Apikey ' + TEST_ANALYST_APIKEY}
    request = client.put('/api/indicators/1', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Insufficient privileges'


def test_update(client):
    """ Ensure a proper request actually works """

    indicator_request, indicator_response = create_indicator(client, 'asdf', 'asdf', 'analyst')
    _id = indicator_response['id']
    assert indicator_request.status_code == 201
    assert indicator_response['user'] == 'analyst'

    # campaigns list
    create_campaign(client, 'LOLcats')
    create_campaign(client, 'Beans')
    data = {'campaigns': ['LOLcats', 'Beans']}
    request = client.put('/api/indicators/{}'.format(_id), json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert len(response['campaigns']) == 2
    assert sorted([response['campaigns'][0]['name'], response['campaigns'][1]['name']]) == ['Beans', 'LOLcats']

    # case_sensitive
    data = {'case_sensitive': not indicator_response['case_sensitive']}
    request = client.put('/api/indicators/{}'.format(_id), json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert response['case_sensitive'] == data['case_sensitive']

    # confidence
    create_indicator_confidence(client, 'HIGH')
    data = {'confidence': 'HIGH'}
    request = client.put('/api/indicators/{}'.format(_id), json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert response['confidence'] == 'HIGH'

    # impact
    create_indicator_impact(client, 'HIGH')
    data = {'impact': 'HIGH'}
    request = client.put('/api/indicators/{}'.format(_id), json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert response['impact'] == 'HIGH'

    # references list
    create_intel_reference(client, 'analyst', 'OSINT', 'http://blahblah2.com')
    create_intel_reference(client, 'analyst', 'OSINT', 'http://blahblah3.com')
    data = {'references': ['http://blahblah2.com', 'http://blahblah3.com']}
    request = client.put('/api/indicators/{}'.format(_id), json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert len(response['references']) == 2
    assert sorted([response['references'][0]['reference'], response['references'][1]['reference']]) == [
        'http://blahblah2.com', 'http://blahblah3.com']

    # status
    create_indicator_status(client, 'Analyzed')
    data = {'status': 'Analyzed'}
    request = client.put('/api/indicators/{}'.format(_id), json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert response['status'] == 'Analyzed'

    # substring
    data = {'substring': not indicator_response['substring']}
    request = client.put('/api/indicators/{}'.format(_id), json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert response['substring'] == data['substring']

    # tags list
    create_tag(client, 'nanocore')
    create_tag(client, 'remcos')
    data = {'tags': ['remcos', 'nanocore']}
    request = client.put('/api/indicators/{}'.format(_id), json=data)
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['id'] == _id
    assert len(response['tags']) == 2
    assert sorted(response['tags']) == ['nanocore', 'remcos']

    # username
    data = {'username': 'admin'}
    request = client.put('/api/indicators/{}'.format(_id), json=data)
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


def test_delete_missing_api_key(app, client):
    """ Ensure an API key is given if the config requires it """

    app.config['DELETE'] = 'admin'

    request = client.delete('/api/indicators/1')
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Bad or missing API key'


def test_delete_invalid_api_key(app, client):
    """ Ensure an API key not found in the database does not work """

    app.config['DELETE'] = 'admin'

    headers = {'Authorization': 'Apikey ' + TEST_INVALID_APIKEY}
    request = client.delete('/api/indicators/1', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'API user does not exist'


def test_delete_inactive_api_key(app, client):
    """ Ensure an inactive API key does not work """

    app.config['DELETE'] = 'admin'

    headers = {'Authorization': 'Apikey ' + TEST_INACTIVE_APIKEY}
    request = client.delete('/api/indicators/1', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'API user is not active'


def test_delete_invalid_role(app, client):
    """ Ensure the given API key has the proper role access """

    app.config['DELETE'] = 'user_does_not_have_this_role'

    headers = {'Authorization': 'Apikey ' + TEST_ANALYST_APIKEY}
    request = client.delete('/api/indicators/1', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['msg'] == 'Insufficient privileges'


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
