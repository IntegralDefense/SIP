import json

from flask import current_app

from project.tests.base import BaseTestCase
from project.tests.base import TEST_ADMIN_APIKEY, TEST_ANALYST_APIKEY, TEST_INVALID_APIKEY


class TestRole(BaseTestCase):
    """ Tests for the Role API calls. Many functions require the admin role. """

    """
    CREATE TESTS
    """

    def test_create_missing_name(self):
        """ Ensure the 'name' parameter is given """

        with self.client:
            data = {'apikey': TEST_ADMIN_APIKEY}
            request = self.client.post('/api/roles', data=data)
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 400)
            self.assertEqual(response['message'], 'Request must include: name')

    def test_create_duplicate_name(self):
        """ Ensure duplicate name cannot be created """

        with self.client:
            data = {'apikey': TEST_ADMIN_APIKEY, 'name': 'asdf'}
            request = self.client.post('/api/roles', data=data)
            self.assertEqual(request.status_code, 201)

            data = {'apikey': TEST_ADMIN_APIKEY, 'name': 'asdf'}
            request = self.client.post('/api/roles', data=data)
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 409)
            self.assertEqual(response['message'], 'Role already exists')

    def test_create_missing_api_key(self):
        """ Ensure an API key is given if the config requires it """

        with self.client:
            data = {'name': 'asdf'}
            request = self.client.post('/api/roles', data=data)
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 401)
            self.assertEqual(response['message'], 'Bad or missing API key')

    def test_create_invalid_api_key(self):
        """ Ensure an API key not found in the database does not work """

        with self.client:
            data = {'apikey': TEST_INVALID_APIKEY, 'name': 'asdf'}
            request = self.client.post('/api/roles', data=data)
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 401)
            self.assertEqual(response['message'], 'API user does not exist')

    def test_create_invalid_role(self):
        """ Ensure the given API key has the proper role access """

        with self.client:
            current_app.config['POST'] = 'analyst'

            data = {'apikey': TEST_ANALYST_APIKEY, 'name': 'asdf'}
            request = self.client.post('/api/roles', data=data)
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 401)
            self.assertEqual(response['message'], 'Insufficient privileges')

    def test_create_description(self):
        """ Ensure a proper request with description actually works """

        with self.client:
            data = {'apikey': TEST_ADMIN_APIKEY, 'name': 'asdf', 'description': 'asdf asdf'}
            request = self.client.post('/api/roles', data=data)
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 201)
            self.assertEqual(response['name'], 'asdf')
            self.assertEqual(response['description'], 'asdf asdf')

    def test_create(self):
        """ Ensure a proper request actually works """

        with self.client:
            data = {'apikey': TEST_ADMIN_APIKEY, 'name': 'asdf'}
            request = self.client.post('/api/roles', data=data)
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 201)
            self.assertEqual(response['name'], 'asdf')
            self.assertEqual(response['description'], None)

    """
    READ TESTS
    """

    def test_read_nonexistent_id(self):
        """ Ensure a nonexistent ID does not work """

        with self.client:
            current_app.config['GET'] = None

            request = self.client.get('/api/roles/100')
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 404)
            self.assertEqual(response['message'], 'Role ID not found')

    def test_read_missing_api_key(self):
        """ Ensure an API key is given if the config requires it """

        with self.client:
            current_app.config['GET'] = 'analyst'

            request = self.client.get('/api/roles/1')
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 401)
            self.assertEqual(response['message'], 'Bad or missing API key')

    def test_read_invalid_api_key(self):
        """ Ensure an API key not found in the database does not work """

        with self.client:
            current_app.config['GET'] = 'analyst'

            request = self.client.get('/api/roles/1?apikey={}'.format(TEST_INVALID_APIKEY))
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 401)
            self.assertEqual(response['message'], 'API user does not exist')

    def test_read_invalid_role(self):
        """ Ensure the given API key has the proper role access """

        with self.client:
            current_app.config['GET'] = 'user_does_not_have_this_role'

            request = self.client.get('/api/roles/1?apikey={}'.format(TEST_ANALYST_APIKEY))
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 401)
            self.assertEqual(response['message'], 'Insufficient privileges')

    def test_read_all_values(self):
        """ Ensure all values properly return """

        with self.client:
            current_app.config['GET'] = None

            data = {'apikey': TEST_ADMIN_APIKEY, 'name': 'asdf'}
            request = self.client.post('/api/roles', data=data)
            self.assertEqual(request.status_code, 201)

            data = {'apikey': TEST_ADMIN_APIKEY, 'name': 'asdf2'}
            request = self.client.post('/api/roles', data=data)
            self.assertEqual(request.status_code, 201)

            data = {'apikey': TEST_ADMIN_APIKEY, 'name': 'asdf3'}
            request = self.client.post('/api/roles', data=data)
            self.assertEqual(request.status_code, 201)

            request = self.client.get('/api/roles')
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 200)
            self.assertGreaterEqual(len(response), 3)

    def test_read_by_id(self):
        """ Ensure names can be read by their ID """

        with self.client:
            current_app.config['GET'] = None

            request = self.client.get('/api/roles/1')
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 200)
            self.assertEqual(response['id'], 1)

    """
    UPDATE TESTS
    """

    def test_update_nonexistent_id(self):
        """ Ensure a nonexistent ID does not work """

        with self.client:
            data = {'apikey': TEST_ADMIN_APIKEY, 'name': 'asdf'}
            request = self.client.put('/api/roles/100', data=data)
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 404)
            self.assertEqual(response['message'], 'Role ID not found')

    def test_update_duplicate_value(self):
        """ Ensure duplicate names cannot be updated """

        with self.client:
            data = {'apikey': TEST_ADMIN_APIKEY, 'name': 'asdf'}
            request = self.client.post('/api/roles', data=data)
            self.assertEqual(request.status_code, 201)

            data = {'apikey': TEST_ADMIN_APIKEY, 'name': 'asdf'}
            request = self.client.put('/api/roles/1', data=data)
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 409)
            self.assertIn(response['message'], 'Role already exists')

    def test_update_missing_api_key(self):
        """ Ensure an API key is given if the config requires it """

        with self.client:
            data = {'name': 'asdf'}
            request = self.client.put('/api/roles/1', data=data)
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 401)
            self.assertEqual(response['message'], 'Bad or missing API key')

    def test_update_invalid_api_key(self):
        """ Ensure an API key not found in the database does not work """

        with self.client:
            data = {'apikey': TEST_INVALID_APIKEY, 'name': 'asdf'}
            request = self.client.put('/api/roles/1', data=data)
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 401)
            self.assertEqual(response['message'], 'API user does not exist')

    def test_update_invalid_role(self):
        """ Ensure the given API key has the proper role access """

        with self.client:
            data = {'apikey': TEST_ANALYST_APIKEY, 'name': 'asdf'}
            request = self.client.put('/api/roles/1', data=data)
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 401)
            self.assertEqual(response['message'], 'Insufficient privileges')

    def test_update_description(self):
        """ Ensure a proper request with a description actually works """

        with self.client:
            current_app.config['GET'] = None

            data = {'apikey': TEST_ADMIN_APIKEY, 'name': 'asdf'}
            request = self.client.post('/api/roles', data=data)
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 201)
            self.assertEqual(response['name'], 'asdf')
            self.assertEqual(response['description'], None)

            data = {'apikey': TEST_ADMIN_APIKEY, 'description': 'asdf asdf'}
            request = self.client.put('/api/roles/1', data=data)
            self.assertEqual(request.status_code, 200)

            request = self.client.get('/api/roles/1')
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 200)
            self.assertEqual(response['id'], 1)
            self.assertEqual(response['description'], 'asdf asdf')

    def test_update(self):
        """ Ensure a proper request actually works """

        with self.client:
            current_app.config['GET'] = None

            data = {'apikey': TEST_ADMIN_APIKEY, 'name': 'asdf'}
            request = self.client.post('/api/roles', data=data)
            self.assertEqual(request.status_code, 201)

            data = {'apikey': TEST_ADMIN_APIKEY, 'name': 'asdf2'}
            request = self.client.put('/api/roles/1', data=data)
            self.assertEqual(request.status_code, 200)

            request = self.client.get('/api/roles/1')
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 200)
            self.assertEqual(response['id'], 1)
            self.assertEqual(response['name'], 'asdf2')

    """
    DELETE TESTS
    """

    def test_delete_nonexistent_id(self):
        """ Ensure a nonexistent ID does not work """

        with self.client:
            data = {'apikey': TEST_ADMIN_APIKEY}
            request = self.client.delete('/api/roles/100', data=data)
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 404)
            self.assertEqual(response['message'], 'Role ID not found')

    def test_delete_missing_api_key(self):
        """ Ensure an API key is given if the config requires it """

        with self.client:
            request = self.client.delete('/api/roles/100')
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 401)
            self.assertEqual(response['message'], 'Bad or missing API key')

    def test_delete_invalid_api_key(self):
        """ Ensure an API key not found in the database does not work """

        with self.client:
            data = {'apikey': TEST_INVALID_APIKEY}
            request = self.client.delete('/api/roles/1', data=data)
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 401)
            self.assertEqual(response['message'], 'API user does not exist')

    def test_delete_invalid_role(self):
        """ Ensure the given API key has the proper role access """

        with self.client:
            data = {'apikey': TEST_ANALYST_APIKEY}
            request = self.client.delete('/api/roles/1', data=data)
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 401)
            self.assertEqual(response['message'], 'Insufficient privileges')

    def test_delete(self):
        """ Ensure a proper request actually works """

        with self.client:
            current_app.config['GET'] = None

            data = {'apikey': TEST_ADMIN_APIKEY, 'name': 'asdf'}
            request = self.client.post('/api/roles', data=data)
            self.assertEqual(request.status_code, 201)

            data = {'apikey': TEST_ADMIN_APIKEY}
            request = self.client.delete('/api/roles/1', data=data)
            self.assertEqual(request.status_code, 204)

            request = self.client.get('/api/roles/1')
            response = json.loads(request.data.decode())
            self.assertEqual(request.status_code, 404)
            self.assertEqual(response['message'], 'Role ID not found')
