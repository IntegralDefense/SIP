import json

from flask import current_app

from project.tests.base import BaseTestCase
from project.tests.base import TEST_ADMIN_APIKEY, TEST_ANALYST_APIKEY, TEST_INVALID_APIKEY


class TestUser(BaseTestCase):
    """ Tests for the User API calls. Many functions require the admin role. """

    """
    CREATE TESTS
    """

    def test_create_missing_email(self):
        """ Ensure the required parameters are given """

        with self.client:
            # Missing email
            data = {'apikey': TEST_ADMIN_APIKEY, 'first_name': 'asdf', 'last_name': 'asdf', 'password': 'asdf',
                    'roles': 'asdf', 'username': 'asdf'}
            request = self.client.post('/api/users', data=data)
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 400)
            self.assertIn('Request must include:', response['message'])

            # Missing first_name
            data = {'apikey': TEST_ADMIN_APIKEY, 'email': 'asdf', 'last_name': 'asdf', 'password': 'asdf',
                    'roles': 'asdf', 'username': 'asdf'}
            request = self.client.post('/api/users', data=data)
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 400)
            self.assertIn('Request must include:', response['message'])

            # Missing last_name
            data = {'apikey': TEST_ADMIN_APIKEY, 'email': 'asdf', 'first_name': 'asdf', 'password': 'asdf',
                    'roles': 'asdf', 'username': 'asdf'}
            request = self.client.post('/api/users', data=data)
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 400)
            self.assertIn('Request must include:', response['message'])

            # Missing password
            data = {'apikey': TEST_ADMIN_APIKEY, 'email': 'asdf', 'first_name': 'asdf', 'last_name': 'asdf',
                    'roles': 'asdf', 'username': 'asdf'}
            request = self.client.post('/api/users', data=data)
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 400)
            self.assertIn('Request must include:', response['message'])

            # Missing roles
            data = {'apikey': TEST_ADMIN_APIKEY, 'email': 'asdf', 'first_name': 'asdf', 'last_name': 'asdf',
                    'password': 'asdf', 'username': 'asdf'}
            request = self.client.post('/api/users', data=data)
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 400)
            self.assertIn('Request must include:', response['message'])

            # Missing username
            data = {'apikey': TEST_ADMIN_APIKEY, 'email': 'asdf', 'first_name': 'asdf', 'last_name': 'asdf',
                    'password': 'asdf', 'roles': 'asdf'}
            request = self.client.post('/api/users', data=data)
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 400)
            self.assertIn('Request must include:', response['message'])

    def test_create_duplicate_email(self):
        """ Ensure duplicate email cannot be created """

        with self.client:
            data = {'apikey': TEST_ADMIN_APIKEY, 'email': 'asdf', 'first_name': 'asdf', 'last_name': 'asdf',
                    'password': 'asdf', 'roles': 'analyst', 'username': 'asdf'}
            request = self.client.post('/api/users', data=data)
            self.assertEqual(request.status_code, 201)

            data = {'apikey': TEST_ADMIN_APIKEY, 'email': 'asdf', 'first_name': 'asdf', 'last_name': 'asdf',
                    'password': 'asdf', 'roles': 'analyst', 'username': 'asdf2'}
            request = self.client.post('/api/users', data=data)
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 409)
            self.assertEqual(response['message'], 'User email already exists')

    def test_create_duplicate_username(self):
        """ Ensure duplicate username cannot be created """

        with self.client:
            data = {'apikey': TEST_ADMIN_APIKEY, 'email': 'asdf', 'first_name': 'asdf', 'last_name': 'asdf',
                    'password': 'asdf', 'roles': 'analyst', 'username': 'asdf'}
            request = self.client.post('/api/users', data=data)
            self.assertEqual(request.status_code, 201)

            data = {'apikey': TEST_ADMIN_APIKEY, 'email': 'asdf2', 'first_name': 'asdf', 'last_name': 'asdf',
                    'password': 'asdf', 'roles': 'analyst', 'username': 'asdf'}
            request = self.client.post('/api/users', data=data)
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 409)
            self.assertEqual(response['message'], 'User username already exists')

    def test_create_missing_api_key(self):
        """ Ensure an API key is given if the config requires it """

        with self.client:
            data = {'email': 'asdf', 'first_name': 'asdf', 'last_name': 'asdf', 'password': 'asdf', 'roles': 'asdf',
                    'username': 'asdf'}
            request = self.client.post('/api/users', data=data)
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 401)
            self.assertEqual(response['message'], 'Bad or missing API key')

    def test_create_invalid_api_key(self):
        """ Ensure an API key not found in the database does not work """

        with self.client:
            data = {'apikey': TEST_INVALID_APIKEY, 'email': 'asdf', 'first_name': 'asdf', 'last_name': 'asdf',
                    'password': 'asdf', 'roles': 'asdf', 'username': 'asdf'}
            request = self.client.post('/api/users', data=data)
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 401)
            self.assertEqual(response['message'], 'API user does not exist')

    def test_create_invalid_role(self):
        """ Ensure the given API key has the proper role access """

        with self.client:
            current_app.config['POST'] = 'analyst'

            data = {'apikey': TEST_ANALYST_APIKEY, 'email': 'asdf', 'first_name': 'asdf', 'last_name': 'asdf',
                    'password': 'asdf', 'roles': 'asdf', 'username': 'asdf'}
            request = self.client.post('/api/users', data=data)
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 401)
            self.assertEqual(response['message'], 'Insufficient privileges')

    def test_create_description(self):
        """ Ensure a proper request with roles string actually works """

        with self.client:
            data = {'apikey': TEST_ADMIN_APIKEY, 'email': 'asdf', 'first_name': 'asdf', 'last_name': 'asdf',
                    'password': 'asdf', 'roles': 'analyst', 'username': 'asdf'}
            request = self.client.post('/api/users', data=data)
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 201)
            self.assertTrue(response['apikey'])
            self.assertEqual(response['roles'], ['analyst'])
            self.assertEqual(response['username'], 'asdf')

    def test_create(self):
        """ Ensure a proper request with roles list actually works """

        with self.client:
            data = {'apikey': TEST_ADMIN_APIKEY, 'email': 'asdf', 'first_name': 'asdf', 'last_name': 'asdf',
                    'password': 'asdf', 'roles': ['analyst', 'admin'], 'username': 'asdf'}
            request = self.client.post('/api/users', data=data)
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 201)
            self.assertTrue(response['apikey'])
            self.assertEqual(response['roles'], ['admin', 'analyst'])
            self.assertEqual(response['username'], 'asdf')

    """
    READ TESTS
    """

    def test_read_nonexistent_id(self):
        """ Ensure a nonexistent ID does not work """

        with self.client:
            current_app.config['GET'] = None

            request = self.client.get('/api/users/100')
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 404)
            self.assertEqual(response['message'], 'User ID not found')

    def test_read_missing_api_key(self):
        """ Ensure an API key is given if the config requires it """

        with self.client:
            current_app.config['GET'] = 'analyst'

            request = self.client.get('/api/users/1')
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 401)
            self.assertEqual(response['message'], 'Bad or missing API key')

    def test_read_invalid_api_key(self):
        """ Ensure an API key not found in the database does not work """

        with self.client:
            current_app.config['GET'] = 'analyst'

            request = self.client.get('/api/users/1?apikey={}'.format(TEST_INVALID_APIKEY))
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 401)
            self.assertEqual(response['message'], 'API user does not exist')

    def test_read_invalid_role(self):
        """ Ensure the given API key has the proper role access """

        with self.client:
            current_app.config['GET'] = 'user_does_not_have_this_role'

            request = self.client.get('/api/users/1?apikey={}'.format(TEST_ANALYST_APIKEY))
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 401)
            self.assertEqual(response['message'], 'Insufficient privileges')

    def test_read_all_values(self):
        """ Ensure all users properly return """

        with self.client:
            current_app.config['GET'] = None

            request = self.client.get('/api/users')
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 200)
            self.assertEqual(len(response), 3)

    def test_read_by_id(self):
        """ Ensure users can be read by their ID """

        with self.client:
            current_app.config['GET'] = None

            request = self.client.get('/api/users/1')
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 200)
            self.assertEqual(response['id'], 1)

    """
    UPDATE TESTS
    """

    def test_update_nonexistent_id(self):
        """ Ensure a nonexistent ID does not work """

        with self.client:
            data = {'apikey': TEST_ADMIN_APIKEY, 'email': 'asdf', 'first_name': 'asdf', 'last_name': 'asdf',
                    'password': 'asdf', 'roles': ['analyst', 'admin'], 'username': 'asdf'}
            request = self.client.put('/api/users/100', data=data)
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 404)
            self.assertEqual(response['message'], 'User ID not found')

    def test_update_duplicate_values(self):
        """ Ensure duplicate emails or usernames cannot be updated """

        with self.client:
            data = {'apikey': TEST_ADMIN_APIKEY, 'email': 'asdf', 'first_name': 'asdf', 'last_name': 'asdf',
                    'password': 'asdf', 'roles': ['analyst', 'admin'], 'username': 'asdf'}
            request = self.client.post('/api/users', data=data)
            self.assertEqual(request.status_code, 201)

            data = {'apikey': TEST_ADMIN_APIKEY, 'email': 'asdf'}
            request = self.client.put('/api/users/1', data=data)
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 409)
            self.assertIn(response['message'], 'User email already exists')

            data = {'apikey': TEST_ADMIN_APIKEY, 'username': 'asdf'}
            request = self.client.put('/api/users/1', data=data)
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 409)
            self.assertIn(response['message'], 'User username already exists')

    def test_update_missing_api_key(self):
        """ Ensure an API key is given if the config requires it """

        with self.client:
            data = {'email': 'asdf', 'first_name': 'asdf', 'last_name': 'asdf', 'password': 'asdf',
                    'roles': ['analyst', 'admin'], 'username': 'asdf'}
            request = self.client.put('/api/users/1', data=data)
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 401)
            self.assertEqual(response['message'], 'Bad or missing API key')

    def test_update_invalid_api_key(self):
        """ Ensure an API key not found in the database does not work """

        with self.client:
            data = {'apikey': TEST_INVALID_APIKEY, 'email': 'asdf', 'first_name': 'asdf', 'last_name': 'asdf',
                    'password': 'asdf', 'roles': ['analyst', 'admin'], 'username': 'asdf'}
            request = self.client.put('/api/users/1', data=data)
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 401)
            self.assertEqual(response['message'], 'API user does not exist')

    def test_update_invalid_role(self):
        """ Ensure the given API key has the proper role access """

        with self.client:
            data = {'apikey': TEST_ANALYST_APIKEY, 'email': 'asdf', 'first_name': 'asdf', 'last_name': 'asdf',
                    'password': 'asdf', 'roles': ['analyst', 'admin'], 'username': 'asdf'}
            request = self.client.put('/api/users/1', data=data)
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 401)
            self.assertEqual(response['message'], 'Insufficient privileges')

    def test_update_nonexistent_role(self):
        """ Ensure a user cannot be updated with a nonexistent role """

        with self.client:
            data = {'apikey': TEST_ADMIN_APIKEY, 'roles': 'this_role_does_not_exist'}
            request = self.client.put('/api/users/1', data=data)
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 400)
            self.assertIn('Valid roles:', response['message'])

    def test_update(self):
        """ Ensure a proper request actually works """

        with self.client:
            current_app.config['GET'] = None

            data = {'apikey': TEST_ADMIN_APIKEY, 'email': 'asdf', 'first_name': 'asdf', 'last_name': 'asdf',
                    'password': 'asdf', 'roles': ['analyst', 'admin'], 'username': 'asdf'}
            request = self.client.post('/api/users', data=data)
            response = json.loads(request.data.decode())
            user_id = response['id']
            orig_apikey = response['apikey']
            self.assertEqual(request.status_code, 201)
            self.assertEqual(response['active'], True)
            self.assertEqual(response['roles'], ['admin', 'analyst'])

            # Active
            data = {'apikey': TEST_ADMIN_APIKEY, 'active': False}
            request = self.client.put('/api/users/{}'.format(user_id), data=data)
            self.assertEqual(request.status_code, 200)

            request = self.client.get('/api/users/{}'.format(user_id))
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 200)
            self.assertEqual(response['id'], user_id)
            self.assertEqual(response['active'], False)

            # API key
            data = {'apikey': TEST_ADMIN_APIKEY, 'apikey_refresh': True}
            request = self.client.put('/api/users/{}'.format(user_id), data=data)
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 200)
            self.assertNotEqual(orig_apikey, response['apikey'])

            # Email
            data = {'apikey': TEST_ADMIN_APIKEY, 'email': 'asdf2'}
            request = self.client.put('/api/users/{}'.format(user_id), data=data)
            self.assertEqual(request.status_code, 200)

            request = self.client.get('/api/users/{}'.format(user_id))
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 200)
            self.assertEqual(response['id'], user_id)
            self.assertEqual(response['email'], 'asdf2')

            # First Name
            data = {'apikey': TEST_ADMIN_APIKEY, 'first_name': 'asdf2'}
            request = self.client.put('/api/users/{}'.format(user_id), data=data)
            self.assertEqual(request.status_code, 200)

            request = self.client.get('/api/users/{}'.format(user_id))
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 200)
            self.assertEqual(response['id'], user_id)
            self.assertEqual(response['first_name'], 'asdf2')

            # Last Name
            data = {'apikey': TEST_ADMIN_APIKEY, 'last_name': 'asdf2'}
            request = self.client.put('/api/users/{}'.format(user_id), data=data)
            self.assertEqual(request.status_code, 200)

            request = self.client.get('/api/users/{}'.format(user_id))
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 200)
            self.assertEqual(response['id'], user_id)
            self.assertEqual(response['last_name'], 'asdf2')

            # Password
            # TODO: Not sure how to test changing password currently.

            # Roles (string)
            data = {'apikey': TEST_ADMIN_APIKEY, 'roles': 'analyst'}
            request = self.client.put('/api/users/{}'.format(user_id), data=data)
            self.assertEqual(request.status_code, 200)

            request = self.client.get('/api/users/{}'.format(user_id))
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 200)
            self.assertEqual(response['id'], user_id)
            self.assertEqual(response['roles'], ['analyst'])

            # Roles (list)
            data = {'apikey': TEST_ADMIN_APIKEY, 'roles': ['analyst', 'admin']}
            request = self.client.put('/api/users/{}'.format(user_id), data=data)
            self.assertEqual(request.status_code, 200)

            request = self.client.get('/api/users/{}'.format(user_id))
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 200)
            self.assertEqual(response['id'], user_id)
            self.assertEqual(response['roles'], ['admin', 'analyst'])

    """
    DELETE TESTS
    """

    def test_delete_nonexistent_id(self):
        """ Ensure a nonexistent ID does not work """

        with self.client:
            data = {'apikey': TEST_ADMIN_APIKEY}
            request = self.client.delete('/api/users/100', data=data)
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 404)
            self.assertEqual(response['message'], 'User ID not found')

    def test_delete_missing_api_key(self):
        """ Ensure an API key is given if the config requires it """

        with self.client:
            request = self.client.delete('/api/users/100')
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 401)
            self.assertEqual(response['message'], 'Bad or missing API key')

    def test_delete_invalid_api_key(self):
        """ Ensure an API key not found in the database does not work """

        with self.client:
            data = {'apikey': TEST_INVALID_APIKEY}
            request = self.client.delete('/api/users/1', data=data)
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 401)
            self.assertEqual(response['message'], 'API user does not exist')

    def test_delete_invalid_role(self):
        """ Ensure the given API key has the proper role access """

        with self.client:
            data = {'apikey': TEST_ANALYST_APIKEY}
            request = self.client.delete('/api/users/1', data=data)
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 401)
            self.assertEqual(response['message'], 'Insufficient privileges')

    def test_delete(self):
        """ Ensure a proper request actually works """

        with self.client:
            current_app.config['GET'] = None

            data = {'apikey': TEST_ADMIN_APIKEY}
            request = self.client.delete('/api/users/1', data=data)
            self.assertEqual(request.status_code, 204)

            request = self.client.get('/api/users/1')
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 404)
            self.assertEqual(response['message'], 'User ID not found')
