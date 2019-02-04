from flask_jwt_extended import verify_jwt_in_request, verify_fresh_jwt_in_request, get_jwt_claims

from project.tests.helpers import *


"""
AUTH TESTS
"""


def test_auth_missing_parameter(client):
    """ Ensure the required parameters are given """

    # Missing username
    request = client.post('/auth', data={'password': 'analyst'})
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert response['message'] == 'Request must include: username, password'

    # Missing password
    request = client.post('/auth', data={'password': 'analyst'})
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert response['message'] == 'Request must include: username, password'


def test_auth_nonexistent_username(client):
    """ Ensure a nonexistent username cannot receive a token """

    request = client.post('/auth', data={'username': 'this_user_does_not_exist', 'password': 'analyst'})
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['message'] == 'User does not exist'


def test_auth_inactive_user(client):
    """ Ensure an inactive user cannot receive a token """

    request = client.post('/auth', data={'username': 'inactive', 'password': 'inactive'})
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['message'] == 'User is inactive'


def test_auth_invalid_password(client):
    """ Ensure the wrong password cannot receive a token """

    request = client.post('/auth', data={'username': 'analyst', 'password': 'wrong_password'})
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['message'] == 'Invalid password'


def test_auth(client):
    """ Ensure a proper request actually works """

    request = client.post('/auth', data={'username': 'analyst', 'password': 'analyst'})
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['access_token']
    assert response['refresh_token']


"""
AUTH FRESH TESTS
"""


def test_auth_fresh_missing_parameter(client):
    """ Ensure the required parameters are given """

    # Missing username
    request = client.post('/auth-fresh', data={'password': 'analyst'})
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert response['message'] == 'Request must include: username, password'

    # Missing password
    request = client.post('/auth-fresh', data={'password': 'analyst'})
    response = json.loads(request.data.decode())
    assert request.status_code == 400
    assert response['message'] == 'Request must include: username, password'


def test_auth_fresh_nonexistent_username(client):
    """ Ensure a nonexistent username cannot receive a token """

    request = client.post('/auth-fresh', data={'username': 'this_user_does_not_exist', 'password': 'analyst'})
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['message'] == 'User does not exist'


def test_auth_fresh_inactive_user(client):
    """ Ensure an inactive user cannot receive a token """

    request = client.post('/auth-fresh', data={'username': 'inactive', 'password': 'inactive'})
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['message'] == 'User is inactive'


def test_auth_fresh_invalid_password(client):
    """ Ensure the wrong password cannot receive a token """

    request = client.post('/auth-fresh', data={'username': 'analyst', 'password': 'wrong_password'})
    response = json.loads(request.data.decode())
    assert request.status_code == 401
    assert response['message'] == 'Invalid password'


def test_auth_fresh(client):
    """ Ensure a proper request actually works """

    request = client.post('/auth-fresh', data={'username': 'analyst', 'password': 'analyst'})
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['access_token']
    assert 'refresh_token' not in response


"""
REFRESH TESTS
"""


def test_refresh_invalid_token(client):
    """ Ensure an invalid refresh token does not work """

    request = client.post('/auth', data={'username': 'analyst', 'password': 'analyst'})
    response = json.loads(request.data.decode())
    headers = {'Authorization': 'Bearer {}'.format(response['access_token'])}

    request = client.post('/refresh', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 422
    assert response['msg'] == 'Only refresh tokens are allowed'


def test_refresh(client):
    """ Ensure a proper request actually works """

    request = client.post('/auth', data={'username': 'analyst', 'password': 'analyst'})
    response = json.loads(request.data.decode())
    headers = {'Authorization': 'Bearer {}'.format(response['refresh_token'])}

    request = client.post('/refresh', headers=headers)
    response = json.loads(request.data.decode())
    assert request.status_code == 200
    assert response['access_token']
    assert 'refresh_token' not in response
